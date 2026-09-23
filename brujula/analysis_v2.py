"""Evidence-bound profiles built solely from accepted public ENOE aggregates.

No survey person rows or internal diagnostic estimates enter this module.
"""

from __future__ import annotations

import hashlib
import json
from collections.abc import Mapping
from copy import deepcopy
from pathlib import Path

from .estimates import FOCAL_FIELDS, METHOD_ID
from .metrics import load_metric_manifest
from .populations import (COMPLETED_PROFESSIONAL_KNOWN_AGE,
                          NATIONAL_15_PLUS_CONTEXT, POPULATION_DEFINITIONS)
from .research_contract import GRAIN, _public_reason, validate_public_research_v2
from .source_inventory import PERIODS
from .source_inventory import _registry


ROOT = Path(__file__).resolve().parents[1]
STATE_CODES = tuple(f"{i:02d}" for i in range(1, 33))
SEX_CODES = ("1", "2")
SUPPRESSED_NUMERIC = ("weighted_denominator",)
SUPPRESSED_PRECISION = ("standard_error", "coefficient_variation", "ci90_lower", "ci90_upper")
COMPUTED_REASONS = frozenset({"sample_size_below_30", "cv_at_least_30",
    "fewer_than_two_domain_psus", "proportion_boundary", "zero_variance",
    "degenerate_interval", "zero_denominator", "zero_design_df",
    "nonpositive_denominator", "missing_standard_error", "invalid_cv",
    "empty_denominator"})
EXPECTED_CODE_FILES = frozenset({
    "scripts/accept_enoe_estimates.py", "scripts/enoe_survey_oracle.R",
    "scripts/official_reconciliation.py", "brujula/acquisition.py",
    "brujula/source_inventory.py", "brujula/enoe_adapter.py",
    "brujula/populations.py", "brujula/metrics.py", "brujula/survey.py",
    "brujula/estimates.py", "brujula/research_contract.py",
})


def _digest(value: object) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"),
                                     ensure_ascii=False, allow_nan=False).encode("utf-8")).hexdigest()


def _content_digest(public: dict) -> str:
    """Use the Phase 2 numeric-content convention, excluding operational clocks."""
    content = deepcopy(public)
    for row in content["records"]:
        row.pop("method_version", None)
    for method in content["methods"]:
        method.pop("version", None)
    for source in content["sources"]:
        source.pop("acquired_at", None)
    content["records"].sort(key=lambda row: tuple(row[key] for key in GRAIN))
    for catalog in ("sources", "populations", "fields_of_study", "occupations",
                    "industries", "geographies", "recorded_sexes", "periods", "metrics",
                    "methods", "evidence"):
        content[catalog].sort(key=lambda row: row["id"])
    return _digest(content)


def _snapshot(period: str) -> str:
    return "enoe_" + period.lower().replace("-", "_")


def _grain(row: Mapping[str, object]) -> tuple[str, ...]:
    return tuple(row[key] for key in GRAIN)


def _ledger_key(grain: tuple[str, ...]) -> str:
    if any("|" in part for part in grain):
        raise ValueError("grain component contains ledger separator")
    return "|".join(grain)


def _check_codes(manifest: dict) -> None:
    hashes = manifest.get("code_sha256")
    if not isinstance(hashes, dict) or set(hashes) != _required_code_files():
        raise ValueError("accepted Phase 2 code hash inventory is incomplete")
    for name, expected in hashes.items():
        if not isinstance(name, str) or not isinstance(expected, str) or len(expected) != 64:
            raise ValueError("malformed accepted code hash")
        path = (ROOT / name).resolve()
        if not path.is_relative_to(ROOT) or not path.is_file():
            raise ValueError("accepted code path is unavailable")
        actual = hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n")).hexdigest()
        if actual != expected:
            raise ValueError(f"accepted Phase 2 code changed: {name}")


def _required_code_files() -> frozenset[str]:
    return EXPECTED_CODE_FILES


def _approved_sources() -> dict[str, dict]:
    """Read the independently approved Phase 1 source catalog, without ZIP access."""
    _, sources = _registry(None)
    return {name: {"sha256": item["expected_sha256"], "url": item["url"]}
            for name, item in sources.items()}


def _approved_public_pins() -> dict[str, str]:
    """Phase 2 golden public content is independent of the caller's manifest."""
    golden = json.loads((ROOT / "data/fixtures/enoe-aggregate-golden.json").read_text(encoding="utf-8"))
    return golden["public_content_sha256_by_snapshot"]


def _required_grains(snapshot: str, period: str, metrics: tuple[str, ...],
                     fields: tuple[str, ...], latest: str) -> set[tuple[str, ...]]:
    domains = {(NATIONAL_15_PLUS_CONTEXT, "all", "mx", "all"),
               (COMPLETED_PROFESSIONAL_KNOWN_AGE, "all", "mx", "all")}
    domains.update((COMPLETED_PROFESSIONAL_KNOWN_AGE, field, "mx", "all")
                   for field in FOCAL_FIELDS)
    if period == latest:
        domains.update((COMPLETED_PROFESSIONAL_KNOWN_AGE, field, "mx", "all")
                       for field in fields)
        for field in ("all", *FOCAL_FIELDS):
            domains.update((COMPLETED_PROFESSIONAL_KNOWN_AGE, field, state, "all")
                           for state in STATE_CODES)
            domains.update((COMPLETED_PROFESSIONAL_KNOWN_AGE, field, "mx", sex)
                           for sex in SEX_CODES)
    return {(snapshot, population, field, "all", "all", geography, sex, period, metric, METHOD_ID)
            for population, field, geography, sex in domains for metric in metrics}


def index_public_estimates(public_by_snapshot: Mapping[str, dict],
                           acceptance: Mapping[str, object]) -> dict:
    """Validate accepted eight-quarter payloads and return stable public IDs.

    ``acceptance`` contains the sealed Phase 2 ``manifest`` and aggregate-only
    ``audits`` keyed by snapshot. All requested, evaluated and public grains must
    agree; computed suppression remains a record, while absent work blocks.
    """
    if not isinstance(public_by_snapshot, Mapping) or not isinstance(acceptance, Mapping):
        raise ValueError("public payloads and acceptance must be mappings")
    manifest, audits = acceptance.get("manifest"), acceptance.get("audits")
    snapshots = tuple(_snapshot(period) for period in PERIODS)
    if not isinstance(manifest, dict) or manifest.get("status") != "PASS":
        raise ValueError("Phase 2 acceptance is absent or failed")
    if manifest.get("numeric_content_digest") is None or not isinstance(audits, Mapping):
        raise ValueError("accepted numeric digest or aggregate ledgers are absent")
    if set(public_by_snapshot) != set(audits) or set(audits) != set(snapshots) or set(manifest.get("snapshots", {})) != set(snapshots):
        raise ValueError("Phase 2 must contain exactly the eight approved snapshots")
    if manifest.get("metric_manifest_sha256") != load_metric_manifest()["content_sha256"]:
        raise ValueError("metric manifest differs from accepted definitions")
    _check_codes(manifest)
    metrics = tuple(sorted(row["id"] for row in load_metric_manifest()["metrics"]))
    approved_sources, approved_pins = _approved_sources(), _approved_public_pins()
    if set(approved_sources) != set(snapshots) or set(approved_pins) != set(snapshots):
        raise ValueError("approved source or public-pin inventory is incomplete")
    entries, by_grain, catalogs, evaluations, coverage = [], {}, {}, {}, {}
    quarter_numeric_digests = {}
    ids = set()
    latest = PERIODS[-1]
    for period in PERIODS:
        snapshot = _snapshot(period)
        public, audit, pin = public_by_snapshot[snapshot], audits[snapshot], manifest["snapshots"][snapshot]
        if validate_public_research_v2(public):
            raise ValueError(f"invalid public v2 payload: {snapshot}")
        if (len(public["sources"]) != 1 or public["sources"][0]["id"] != snapshot
                or len(public["periods"]) != 1 or public["periods"][0]["id"] != period):
            raise ValueError("mixed source or period in public root")
        if (_digest(public) != pin.get("public_v2_digest")
                or _content_digest(public) != pin.get("public_content_sha256")):
            raise ValueError(f"public payload differs from accepted hash: {snapshot}")
        if pin["public_content_sha256"] != approved_pins[snapshot]:
            raise ValueError("public content differs from independent Phase 2 golden pin")
        if (public["sources"][0]["sha256"] != approved_sources[snapshot]["sha256"]
                or public["sources"][0]["url"] != approved_sources[snapshot]["url"]):
            raise ValueError("source differs from approved pinned snapshot catalog")
        quarter_digest = _digest(public["records"])
        if quarter_digest != pin.get("numeric_digest") or quarter_digest != audit.get("numeric_digest"):
            raise ValueError("numeric record digest differs from accepted ledger")
        if _digest(audit.get("public_records")) != quarter_digest:
            raise ValueError("aggregate public records differ from accepted public payload")
        quarter_numeric_digests[snapshot] = quarter_digest
        if (audit.get("snapshot_id") != snapshot or audit.get("period") != period
                or audit.get("source_sha256") != public["sources"][0]["sha256"]
                or audit.get("numeric_digest") != pin.get("numeric_digest")
                or audit.get("public_content_sha256") != pin.get("public_content_sha256")
                or audit.get("method_version") != public["methods"][0]["version"]):
            raise ValueError("aggregate ledger identity differs from accepted public source")
        if (len(public["methods"]) != 1 or public["methods"][0]["id"] != METHOD_ID
                or public["methods"][0]["source_snapshot_ids"] != [snapshot]):
            raise ValueError("method catalog has mixed snapshot references")
        if tuple(sorted(row["id"] for row in public["metrics"])) != metrics:
            raise ValueError("public metric set differs from accepted manifest")
        fields = tuple(sorted(row["id"] for row in public["fields_of_study"] if row["id"] != "all"))
        if (not set(FOCAL_FIELDS) <= set(fields)
                or any(len(code) != 6 or not code.isascii() or not code.isdigit() or code == "999999" for code in fields)):
            raise ValueError("named fields are not verified six-digit CMPE codes")
        rows = public["records"]
        row_grains = [_grain(row) for row in rows]
        row_keys = [_ledger_key(grain) for grain in row_grains]
        requested, evaluated = audit.get("requested_cells"), audit.get("evaluated_cells")
        if (not isinstance(requested, dict) or not isinstance(evaluated, dict)
                or any(value is not True for value in requested.values())
                or len(row_keys) != len(set(row_keys))
                or set(row_keys) != set(requested) or set(requested) != set(evaluated)
                or len(row_keys) != pin.get("requested_count")
                or audit.get("request_comparison", {}).get("status") != "PASS"):
            raise ValueError("requested, evaluated and public record grains differ")
        required = _required_grains(snapshot, period, metrics, fields, latest)
        if not {_ledger_key(grain) for grain in required} <= set(requested):
            raise ValueError("required Phase 3 computation was not requested")
        for row, grain, key in zip(rows, row_grains, row_keys):
            evaluation = evaluated[key]
            raw_reason = evaluation.get("reason")
            if raw_reason == "Project singleton adjustment":
                reason_ok = row["value"] is not None
            elif raw_reason == "Synthetic fixture":
                reason_ok = row["synthetic"] is True and row["value"] is not None
            else:
                reason_ok = (isinstance(raw_reason, str) and bool(raw_reason)
                             and set(raw_reason.split(";")) <= COMPUTED_REASONS)
            if (not reason_ok or _public_reason(raw_reason, row["status"]) != row["reason"]):
                raise ValueError("evaluated cell disagrees with public reason")
            if (row["source_snapshot_id"] != snapshot or row["period_id"] != period
                    or row["method_version"] != audit["method_version"]
                    or evaluation.get("method_version") != row["method_version"]
                    or evaluation.get("status") != row["status"]
                    or evaluation.get("synthetic") != row["synthetic"]
                    or evaluation.get("coverage", {}).get("eligible_n") != row["sample_size"]
                    or not isinstance(evaluation.get("metric_version"), str)
                    or not evaluation["metric_version"].endswith(manifest["metric_manifest_sha256"])):
                raise ValueError("evaluated cell disagrees with public record")
            if row["value"] is None:
                if (evaluation.get("has_estimate") is not True):
                    # Empty domains legitimately have no estimate, but were still evaluated.
                    if evaluation.get("coverage", {}).get("eligible_n") != 0 or evaluation.get("has_estimate") is not False:
                        raise ValueError("suppressed cell lacks an actual evaluated reason")
            elif evaluation.get("has_estimate") is not True:
                raise ValueError("visible value lacks a computed estimate")
            if row["value"] is None and any(row[name] is not None for name in SUPPRESSED_NUMERIC):
                raise ValueError("suppressed public denominator leaked")
            record_id = "v2r:" + _digest(list(grain))
            if record_id in ids or grain in by_grain:
                raise ValueError("canonical record ID collision or duplicate grain")
            ids.add(record_id)
            item = {"record_id": record_id, "grain": grain, "record": deepcopy(row),
                    "snapshot_sha256": public["sources"][0]["sha256"],
                    "method_version": row["method_version"]}
            entries.append(item)
            by_grain[grain] = item
            evaluations[grain] = deepcopy(evaluation)
        catalogs[snapshot] = {name: deepcopy(public[name]) for name in
                              ("sources", "populations", "fields_of_study", "occupations", "industries",
                               "geographies", "recorded_sexes", "periods", "metrics", "methods", "evidence")}
        coverage[snapshot] = deepcopy(audit.get("population_coverage"))
    if _digest(quarter_numeric_digests) != manifest["numeric_content_digest"]:
        raise ValueError("combined numeric content digest differs from accepted Phase 2 result")
    entries.sort(key=lambda item: item["grain"])
    return {"records": entries, "by_grain": by_grain, "evaluations": evaluations,
            "catalogs": catalogs, "coverage": coverage, "periods": tuple(PERIODS),
            "metric_ids": metrics, "accepted_numeric_digest": manifest["numeric_content_digest"]}


def _coverage(index: dict, audits: Mapping[str, dict], grain: tuple[str, ...]) -> dict:
    snapshot, population, field, _, _, geography, sex, _, metric, _ = grain
    audit = audits[snapshot]
    key = "|".join((population, field, geography, sex))
    source = audit["population_coverage"].get(key)
    evaluation = index["evaluations"][grain]
    if not isinstance(source, dict) or source != index["coverage"][snapshot].get(key):
        raise ValueError("accepted aggregate coverage is missing or changed")
    if source.get("counts_nonexclusive") is not True:
        raise ValueError("exclusion counts must declare nonexclusive semantics")
    result = {"observed_n": evaluation["coverage"]["domain_n"],
            "metric_eligible_n": evaluation["coverage"]["eligible_n"],
            "metric_exclusions": dict(sorted(evaluation["exclusions"].items())),
            "responding_resident_n": source["responding_resident_n"],
            "population_eligible_n": source["population_eligible_n"],
            "exclusions": dict(sorted(source["exclusions"].items())),
            "observed_category_counts": dict(sorted(source["observed_category_counts"].items())),
            "counts_nonexclusive": True,
            "denominator_keys": {"observed_n": "domain_n", "metric_eligible_n": "eligible_n",
                                 "population_eligible_n": "responding_resident_n"},
            "metric_id": metric}
    if {"positive_income_mean", "positive_income_coverage"} <= set(index["metric_ids"]):
        mean_grain = grain[:8] + ("positive_income_mean", grain[9])
        coverage_grain = grain[:8] + ("positive_income_coverage", grain[9])
        mean = index["by_grain"].get(mean_grain)
        coverage = index["by_grain"].get(coverage_grain)
        if mean is None or coverage is None:
            raise ValueError("exact-income response computation is absent")
        result["exact_income_response"] = _observed_response(
            mean["record"]["sample_size"], coverage["record"]["sample_size"])
    return result


def _observed_response(responding_n: int, denominator_n: int) -> dict:
    """Describe observed exact-income availability, never a weighted estimate."""
    if (type(responding_n) is not int or type(denominator_n) is not int
            or responding_n < 0 or denominator_n < 0 or responding_n > denominator_n):
        raise ValueError("response count exceeds or invalidates occupied denominator")
    return {"responding_n": responding_n, "denominator_n": denominator_n,
            "observed_percent": 100.0 * responding_n / denominator_n if denominator_n else None,
            "reason": None if denominator_n else "empty_denominator",
            "denominator_key": "occupied_eligible_n"}


def _cell(index: dict, audits: Mapping[str, dict], grain: tuple[str, ...]) -> dict:
    item = index["by_grain"].get(grain)
    if item is None:
        raise ValueError("expected cell has no computed public record")
    row = item["record"]
    cell = {"record_id": item["record_id"], "grain": grain, "value": row["value"],
            "status": row["status"], "reason": row["reason"], "sample_size": row["sample_size"],
            "support": deepcopy(row["support"]), "precision": deepcopy(row["precision"]),
            "weighted_denominator_estimate": row["weighted_denominator"],
            "source_sha256": item["snapshot_sha256"], "method_version": item["method_version"],
            "evidence_refs": list(row["evidence_refs"]), "synthetic": row["synthetic"],
            **{key: row[key] for key in GRAIN}}
    if row["value"] is None:
        if (cell["weighted_denominator_estimate"] is not None
                or cell["support"]["weighted_support_total"] is not None
                or any(cell["precision"][name] is not None for name in SUPPRESSED_PRECISION)):
            raise ValueError("suppressed numeric diagnostic leaked to profile")
    cell["coverage"] = _coverage(index, audits, grain)
    return cell


def _redact_parent_if_complementary(parent: dict, parts: list[dict]) -> bool:
    """Hide an otherwise visible parent when it isolates one suppressed part."""
    if parent["value"] is None or sum(part["value"] is None for part in parts) != 1:
        return False
    parent["value"] = None
    parent["status"] = "REVIEW"
    parent["reason"] = "complementary_suppression"
    parent["weighted_denominator_estimate"] = None
    parent["support"]["weighted_support_total"] = None
    for name in SUPPRESSED_PRECISION:
        parent["precision"][name] = None
    return True


def build_profiles(index: dict, coverage_audits: Mapping[str, dict], *, latest_period_id: str) -> dict:
    """Materialize all requested slots without inventing sparse cells or zeros."""
    if latest_period_id != index["periods"][-1] or set(coverage_audits) != set(index["catalogs"]):
        raise ValueError("latest period or aggregate coverage inventory differs from acceptance")
    metrics = index["metric_ids"]
    fields = tuple(sorted(row["id"] for row in index["catalogs"][_snapshot(latest_period_id)]["fields_of_study"]
                          if row["id"] != "all"))
    national, named_fields, states, sexes = [], [], [], []
    for period in index["periods"]:
        snapshot = _snapshot(period)
        for population, field in ((NATIONAL_15_PLUS_CONTEXT, "all"),
                                  (COMPLETED_PROFESSIONAL_KNOWN_AGE, "all"),
                                  *((COMPLETED_PROFESSIONAL_KNOWN_AGE, focal) for focal in FOCAL_FIELDS)):
            for metric in metrics:
                national.append(_cell(index, coverage_audits,
                                      (snapshot, population, field, "all", "all", "mx", "all", period, metric, METHOD_ID)))
    latest_snapshot = _snapshot(latest_period_id)
    labels = {row["id"]: row["label"] for row in index["catalogs"][latest_snapshot]["fields_of_study"]}
    for field in fields:
        for metric in metrics:
            cell = _cell(index, coverage_audits, (latest_snapshot, COMPLETED_PROFESSIONAL_KNOWN_AGE,
                         field, "all", "all", "mx", "all", latest_period_id, metric, METHOD_ID))
            cell["field_label"] = labels[field]
            named_fields.append(cell)
    for field in ("all", *FOCAL_FIELDS):
        for state in STATE_CODES:
            for metric in metrics:
                states.append(_cell(index, coverage_audits, (latest_snapshot, COMPLETED_PROFESSIONAL_KNOWN_AGE,
                              field, "all", "all", state, "all", latest_period_id, metric, METHOD_ID)))
        for sex in SEX_CODES:
            for metric in metrics:
                sexes.append(_cell(index, coverage_audits, (latest_snapshot, COMPLETED_PROFESSIONAL_KNOWN_AGE,
                             field, "all", "all", "mx", sex, latest_period_id, metric, METHOD_ID)))
    # A visible all-sex or all-state parent and all but one visible part can
    # reconstruct a hidden part. Keep both copies of a focal national cell in
    # sync; the index remains an internal accepted-public input, not output.
    parents = {(cell["field_of_study_id"], cell["metric_id"]): cell for cell in national
               if cell["period_id"] == latest_period_id
               and cell["population_id"] == COMPLETED_PROFESSIONAL_KNOWN_AGE}
    field_copies = {(cell["field_of_study_id"], cell["metric_id"]): cell for cell in named_fields}
    for field in ("all", *FOCAL_FIELDS):
        for metric in metrics:
            parent = parents[(field, metric)]
            state_parts = [cell for cell in states if cell["field_of_study_id"] == field
                           and cell["metric_id"] == metric]
            sex_parts = [cell for cell in sexes if cell["field_of_study_id"] == field
                         and cell["metric_id"] == metric]
            if len(state_parts) != 32 or len(sex_parts) != 2:
                raise ValueError("partition is incomplete for complementary suppression")
            if (_redact_parent_if_complementary(parent, state_parts)
                    or _redact_parent_if_complementary(parent, sex_parts)):
                duplicate = field_copies.get((field, metric))
                if duplicate is not None:
                    _redact_parent_if_complementary(duplicate, state_parts if sum(
                        part["value"] is None for part in state_parts) == 1 else sex_parts)
    # This is the common downstream record source for comparison, claims and
    # publication. The accepted input index is deliberately left private and
    # unchanged; consumers must use this sanitized copy, keyed by stable ID.
    record_index = {item["record_id"]: deepcopy(item) for item in index["records"]}
    for cell in (*national, *named_fields):
        if cell["reason"] != "complementary_suppression":
            continue
        item = record_index[cell["record_id"]]
        row = item["record"]
        row["value"] = None
        row["status"] = "REVIEW"
        row["reason"] = "review_required"  # valid public-v2 controlled reason
        row["weighted_denominator"] = None
        row["support"]["weighted_support_total"] = None
        for name in SUPPRESSED_PRECISION:
            row["precision"][name] = None
        item["redaction_reason"] = "complementary_suppression"
    return {"accepted_numeric_digest": index["accepted_numeric_digest"],
            "population_labels": {name: POPULATION_DEFINITIONS[name]["label"] for name in
                                  (NATIONAL_15_PLUS_CONTEXT, COMPLETED_PROFESSIONAL_KNOWN_AGE)},
            "periods": list(index["periods"]), "metric_ids": list(metrics),
            "national": national, "latest_fields": named_fields,
            "latest_states": states, "latest_recorded_sexes": sexes,
            "record_index": record_index,
            "latest_named_field_count": len(fields), "synthetic": all(item["record"]["synthetic"] for item in index["records"])}
