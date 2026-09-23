"""Strict, separate v2 research validation and public projection."""

from __future__ import annotations

import json
import math
from collections.abc import Mapping
from datetime import date
from functools import lru_cache

from jsonschema import Draft202012Validator, FormatChecker

from .populations import POPULATION_DEFINITIONS
from .resources import contract_path


GRAIN = (
    "source_snapshot_id", "population_id", "field_of_study_id", "occupation_id",
    "industry_id", "geography_id", "recorded_sex_id", "period_id", "metric_id", "method_id",
)
CATALOG_REFS = {
    "source_snapshot_id": "sources", "population_id": "populations",
    "field_of_study_id": "fields_of_study", "occupation_id": "occupations",
    "industry_id": "industries", "geography_id": "geographies",
    "recorded_sex_id": "recorded_sexes", "period_id": "periods",
    "metric_id": "metrics", "method_id": "methods",
}


@lru_cache(maxsize=2)
def _validator(public: bool) -> Draft202012Validator:
    name = "research-v2-public.schema.json" if public else "research-v2.schema.json"
    schema = json.loads(contract_path(name).read_text(encoding="utf-8"))
    Draft202012Validator.check_schema(schema)
    return Draft202012Validator(schema, format_checker=FormatChecker())


def _fail(check_id: str, message: str) -> dict:
    return {"id": check_id, "message": message}


def _schema_checks(payload: Mapping[str, object], public: bool) -> list[dict]:
    errors = _validator(public).iter_errors(payload)
    checks = [_fail("schema", f"{'.'.join(map(str, error.absolute_path)) or '$'}: {error.message}") for error in errors]
    return sorted(checks, key=lambda x: (x["id"], x["message"]))


def _nonfinite_paths(value: object, path: str = "$", seen: set[int] | None = None) -> list[str]:
    seen = seen if seen is not None else set()
    if isinstance(value, float) and not math.isfinite(value):
        return [path]
    if isinstance(value, (Mapping, list)):
        identity = id(value)
        if identity in seen:
            return [path + " (cycle)"]
        seen.add(identity)
        if isinstance(value, Mapping):
            result = [child for key, part in value.items() for child in _nonfinite_paths(part, f"{path}.{key}", seen)]
        else:
            result = [child for index, part in enumerate(value) for child in _nonfinite_paths(part, f"{path}[{index}]", seen)]
        seen.remove(identity)
        return result
    return []


def _semantic_checks(payload: Mapping[str, object], public: bool) -> list[dict]:
    checks: list[dict] = []
    tables: dict[str, dict[str, dict]] = {}
    for table in ("sources", "populations", "fields_of_study", "occupations", "industries", "geographies", "recorded_sexes", "periods", "metrics", "methods", "evidence"):
        ids: dict[str, dict] = {}
        for item in payload[table]:
            if item["id"] in ids:
                checks.append(_fail("duplicate_id", f"{table}:{item['id']}"))
            ids[item["id"]] = item
        tables[table] = ids
    for name in sorted(tables["populations"]):
        if name not in POPULATION_DEFINITIONS:
            checks.append(_fail("population_id", f"unrecognized population:{name}"))
    for source in payload["sources"]:
        if source["period_id"] not in tables["periods"]:
            checks.append(_fail("source_period", f"{source['id']} has unknown period:{source['period_id']}"))
    for method in payload["methods"]:
        for source_id in method["source_snapshot_ids"]:
            if source_id not in tables["sources"]:
                checks.append(_fail("method_source", f"{method['id']} has unknown source:{source_id}"))
    for metric in payload["metrics"]:
        basis = "nominal" if metric["unit"] == "MXN/month" else "not_applicable"
        if metric["price_basis"] != basis:
            checks.append(_fail("unit_price_basis", f"{metric['id']} has incompatible price basis"))
    for evidence in payload["evidence"]:
        if evidence["source_snapshot_id"] not in tables["sources"]:
            checks.append(_fail("evidence_source", f"{evidence['id']} has unknown source:{evidence['source_snapshot_id']}"))
    ordered = sorted(payload["periods"], key=lambda period: (period["start"], period["id"]))
    previous_end: date | None = None
    for period in ordered:
        start = date.fromisoformat(period["start"])
        end = date.fromisoformat(period["end"])
        if start > end:
            checks.append(_fail("period_range", f"{period['id']} starts after end"))
        if previous_end is not None and start <= previous_end:
            checks.append(_fail("period_overlap", f"{period['id']} overlaps previous period"))
        previous_end = max(previous_end, end) if previous_end is not None else end
    seen_grains: set[tuple] = set()
    for index, record in enumerate(payload["records"]):
        grain = tuple(record[key] for key in GRAIN)
        if grain in seen_grains:
            checks.append(_fail("duplicate_grain", f"records[{index}] duplicates a prior grain"))
        seen_grains.add(grain)
        for field, table in CATALOG_REFS.items():
            if record[field] not in tables[table]:
                checks.append(_fail("orphan_ref", f"records[{index}].{field}:{record[field]}"))
        source = tables["sources"].get(record["source_snapshot_id"])
        method = tables["methods"].get(record["method_id"])
        metric = tables["metrics"].get(record["metric_id"])
        if source and source["period_id"] != record["period_id"]:
            checks.append(_fail("source_period", f"records[{index}] period differs from source"))
        if method and (record["source_snapshot_id"] not in method["source_snapshot_ids"]
                       or record["method_version"] != method["version"] or record["design_id"] != method["design_id"]):
            checks.append(_fail("method_compatibility", f"records[{index}] method/design/source mismatch"))
        if metric and (record["unit"] != metric["unit"] or record["price_basis"] != metric["price_basis"]):
            checks.append(_fail("metric_compatibility", f"records[{index}] unit or price basis mismatch"))
        if record["value"] is not None and (record["value"] < 0 or record["unit"] == "percent" and record["value"] > 100):
            checks.append(_fail("value_range", f"records[{index}] value outside metric range"))
        for ref in record["evidence_refs"]:
            item = tables["evidence"].get(ref)
            if item is None or item["source_snapshot_id"] != record["source_snapshot_id"]:
                checks.append(_fail("evidence_ref", f"records[{index}] orphan or wrong-source evidence:{ref}"))
        support = record["support"]
        if (support["n_psu_domain"] > support["n_psu_design"] or
                support["n_strata_domain"] > support["n_strata_design"] or
                support["n_strata_domain"] > support["n_psu_domain"] or
                support["design_df"] != support["n_psu_design"] - support["n_strata_design"]):
            checks.append(_fail("support", f"records[{index}] impossible design/domain support"))
        precision = record["precision"]
        if precision["singleton_policy"] == "adjust" and (precision["official_precision"] or record["status"] == "MEASURED"):
            checks.append(_fail("singleton_precision", f"records[{index}] project singleton adjustment cannot assert official precision"))
        if record["synthetic"] and (record["status"] == "MEASURED" or precision["official_precision"]):
            checks.append(_fail("synthetic_status", f"records[{index}] synthetic cannot assert official measurement"))
        if record["reason"] is not None and not record["reason"].strip():
            checks.append(_fail("reason", f"records[{index}] reason is blank"))
        if record["status"] == "REVIEW" and not record["reason"]:
            checks.append(_fail("review_reason", f"records[{index}] REVIEW requires a reason"))
        if record["value"] is not None and record["weighted_denominator"] is None:
            checks.append(_fail("denominator", f"records[{index}] visible value lacks weighted denominator"))
        lower, upper = precision["ci90_lower"], precision["ci90_upper"]
        if lower is not None and upper is not None and (lower > upper or record["value"] is not None and not lower <= record["value"] <= upper):
            checks.append(_fail("precision_interval", f"records[{index}] invalid interval ordering"))
        if record["value"] is not None:
            cv = precision["coefficient_variation"]
            se = precision["standard_error"]
            if (record["sample_size"] < 30 or support["n_psu_domain"] < 2 or support["design_df"] < 1 or
                    record["weighted_denominator"] is None or record["weighted_denominator"] <= 0 or
                    se is None or se <= 0 or cv is None or cv >= 30 or
                    lower is None or upper is None or lower == upper or record["value"] == 0 or
                    record["unit"] == "percent" and record["value"] == 100):
                checks.append(_fail("precision_gate", f"records[{index}] unsupported value must be null"))
            elif record["status"] == "MEASURED" and cv >= 15:
                checks.append(_fail("precision_grade", f"records[{index}] CV requires REVIEW"))
        if public:
            if record["value"] is None and (record["weighted_denominator"] is not None or support["weighted_support_total"] is not None or
                                               any(precision[name] is not None for name in ("standard_error", "coefficient_variation", "ci90_lower", "ci90_upper"))):
                checks.append(_fail("suppression", f"records[{index}] suppressed diagnostics leaked"))
        else:
            estimate = record["estimate"]
            value = record["value"]
            if value is not None and (estimate is None or value != estimate):
                checks.append(_fail("value_estimate", f"records[{index}] public value must match exact gated estimate"))
            if value is None and lower is not None and upper is not None and (lower > upper or estimate is not None and not lower <= estimate <= upper):
                checks.append(_fail("precision_interval", f"records[{index}] invalid interval ordering"))
    return sorted(checks, key=lambda x: (x["id"], x["message"]))


def _validate(payload: Mapping[str, object], public: bool) -> list[dict]:
    finite = [_fail("nonfinite", path) for path in _nonfinite_paths(payload)]
    if finite:
        return sorted(finite, key=lambda x: x["message"])
    schema = _schema_checks(payload, public)
    if schema:
        return schema
    return _semantic_checks(payload, public)


def validate_research_v2(payload: Mapping[str, object]) -> list[dict]:
    """Return deterministic schema/semantic failures; an empty list is valid."""
    return _validate(payload, public=False)


def validate_public_research_v2(payload: Mapping[str, object]) -> list[dict]:
    """Validate a public v2 bundle against its separate strict contract."""
    return _validate(payload, public=True)


def public_research_projection(payload: Mapping[str, object]) -> dict:
    """Project only validated records through a public allowlist, then validate."""
    failures = validate_research_v2(payload)
    if failures:
        raise ValueError(f"invalid internal research v2: {failures}")
    catalog_fields = {
        "sources": ("id", "period_id", "url", "sha256", "terms_url", "authority", "acquired_at"),
        "populations": ("id",),
        "fields_of_study": ("id", "label"),
        "occupations": ("id", "label"),
        "industries": ("id", "label"),
        "geographies": ("id", "label"),
        "recorded_sexes": ("id", "label"),
        "periods": ("id", "label", "start", "end"),
        "metrics": ("id", "label", "unit", "price_basis"),
        "methods": ("id", "design_id", "version", "source_snapshot_ids"),
        "evidence": ("id", "source_snapshot_id", "label", "url", "kind"),
    }
    result: dict = {"schema_version": "2.0"}
    for table, fields in catalog_fields.items():
        result[table] = [{key: list(item[key]) if key == "source_snapshot_ids" else item[key] for key in fields}
                         for item in payload[table]]
    record_fields = (*GRAIN, "unit", "price_basis", "method_version", "design_id", "sample_size",
                     "status", "reason", "value", "evidence_refs", "synthetic")
    support_fields = ("n_psu_design", "n_strata_design", "n_psu_domain", "n_strata_domain", "design_df")
    precision_fields = ("method", "ci_method", "level", "singleton_policy", "official_precision")
    result["records"] = []
    for row in payload["records"]:
        suppressed = row["value"] is None
        projected = {key: list(row[key]) if key == "evidence_refs" else row[key] for key in record_fields}
        projected["weighted_denominator"] = None if suppressed else row["weighted_denominator"]
        projected["support"] = {key: row["support"][key] for key in support_fields}
        projected["support"]["weighted_support_total"] = None if suppressed else row["support"]["weighted_support_total"]
        projected["precision"] = {key: row["precision"][key] for key in precision_fields}
        for key in ("standard_error", "coefficient_variation", "ci90_lower", "ci90_upper"):
            projected["precision"][key] = None if suppressed else row["precision"][key]
        result["records"].append(projected)
    failures = validate_public_research_v2(result)
    if failures:
        raise ValueError(f"invalid public research v2: {failures}")
    return result
