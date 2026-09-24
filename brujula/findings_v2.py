"""Sealed analytical handoff built from accepted public ENOE aggregates only."""

from __future__ import annotations

from collections import Counter
from collections.abc import Mapping
from copy import deepcopy
import json
import math

from jsonschema import Draft202012Validator

from .analysis_v2 import _digest, build_profiles, index_public_estimates
from .claims_v2 import (METRIC_LABELS, POPULATION_LABELS, make_claim,
                        select_opening_claims, validate_claim)
from .comparisons_v2 import build_comparison_ledger, load_definition_registry
from .estimates import FOCAL_FIELDS
from .research_contract import GRAIN
from .resources import analysis_reference_path, contract_path, require_installed_package_path
from .source_inventory import PERIODS


CLAIM_METRICS = ("positive_income_coverage", "employment_rate", "positive_income_mean",
                 "main_job_informality_rate")
COMPARISON_METRICS = ("employment_rate", "positive_income_mean", "main_job_informality_rate")
SECTIONS = ("national", "latest_fields", "latest_states", "latest_recorded_sexes")
SNAPSHOTS = tuple("enoe_" + period.lower().replace("-", "_") for period in PERIODS)
VALID_LIMITATIONS = {
    "precision": "La precisión de este proyecto no constituye certificación oficial del INEGI.",
    "overlap": "Las muestras trimestrales pueden solaparse; los cambios no tienen prueba de significancia.",
    "income": "Los ingresos medios positivos conocidos son condicionales y nominales; no se ajustan por inflación.",
    "sparse": "Las celdas sin soporte permanecen nulas con su motivo visible.",
    "redaction": "Algunos totales se ocultaron para impedir reconstruir una celda suprimida.",
    "edition": "La fecha exacta de edición de alguna fuente no está disponible.",
    "empty": "No hay un hallazgo inicial con soporte suficiente en las medidas predefinidas.",
}


def _load_reference() -> dict:
    return json.loads(require_installed_package_path(analysis_reference_path()).read_text(encoding="utf-8"))


def _reference_from_packet(packet: dict) -> dict:
    """Hash-only promotion reference; never includes public or hidden numeric rows."""
    return {"schema_version": "1.0", "source_manifest_sha256": _digest(packet["source_manifest"]),
            "record_index_sha256": _digest(packet["record_index"]),
            "profiles_sha256": _digest(packet["profiles"]),
            "coverage_sha256": _digest(packet["coverage"]),
            "accepted_numeric_digest": packet["source_manifest"]["acceptance"]["numeric_content_digest"],
            "snapshot_ids": list(SNAPSHOTS)}


def _source_manifest(index: dict, acceptance: Mapping[str, object]) -> dict:
    # The raw payload digest is verified by index_public_estimates but includes
    # the acquisition clock. Analytical identity binds canonical content.
    fields = ("public_content_sha256", "numeric_digest", "requested_count")
    snapshots = {sid: {key: acceptance["snapshots"][sid][key] for key in fields} for sid in SNAPSHOTS}
    sources = {}
    for sid in SNAPSHOTS:
        catalog = index["catalogs"][sid]
        source, method = catalog["sources"][0], catalog["methods"][0]
        sources[sid] = {"period_id": source["period_id"], "sha256": source["sha256"],
                        "url": source["url"], "method_version": method["version"]}
    return {"acceptance": {"status": acceptance["status"],
                            "numeric_content_digest": acceptance["numeric_content_digest"],
                            "metric_manifest_sha256": acceptance["metric_manifest_sha256"],
                            "code_sha256": dict(sorted(acceptance["code_sha256"].items())),
                            "snapshots": snapshots}, "sources": sources}


def _display_items(profiles: dict, catalogs: dict, registry: dict) -> dict:
    enriched = deepcopy(profiles["record_index"])
    for rid, item in enriched.items():
        item["grain"] = list(item["grain"])
        row = item["record"]
        sid = row["source_snapshot_id"]
        if sid not in catalogs or item["record_id"] != rid:
            raise ValueError("record source catalog is absent")
        fields = {x["id"]: x["label"] for x in catalogs[sid]["fields_of_study"]}
        if row["field_of_study_id"] not in fields:
            raise ValueError("field code is absent from accepted source catalog")
        geo = row["geography_id"]
        if geo == "mx":
            geography = "México"
        else:
            state = registry["states"].get(geo)
            if state is None:
                raise ValueError("entity code is absent from reviewed state catalog")
            geography = state["name"]
        sex = {"all": "todos los sexos registrados", "1": "hombres registrados",
               "2": "mujeres registradas"}.get(row["recorded_sex_id"])
        if sex is None or row["metric_id"] not in METRIC_LABELS:
            raise ValueError("sex or metric code lacks a reviewed display label")
        item["display"] = {"field": fields[row["field_of_study_id"]],
                           "population": POPULATION_LABELS[row["population_id"]],
                           "metric": METRIC_LABELS[row["metric_id"]],
                           "geography": geography, "recorded_sex": sex,
                           "period": row["period_id"]}
    return dict(sorted(enriched.items()))


def _coverage(profiles: dict) -> dict:
    cells = [cell for name in SECTIONS for cell in profiles[name]]
    reasons = Counter(cell["reason"] or "unknown" for cell in cells if cell["value"] is None)
    return {"expected_cells": {name: len(profiles[name]) for name in SECTIONS},
            "missing_reasons": dict(sorted(reasons.items())),
            "suppressed_cells": sum(cell["value"] is None for cell in cells)}


def _claims(index: dict, comparisons: list[dict]) -> tuple[list[dict], list[str]]:
    ledger = {row["comparison_id"]: row for row in comparisons}
    if len(ledger) != len(comparisons):
        raise ValueError("duplicate comparison ID")
    candidates = []
    for rid, item in index.items():
        row = item["record"]
        if (row["period_id"] == PERIODS[-1] and row["field_of_study_id"] in FOCAL_FIELDS
                and row["geography_id"] == "mx" and row["recorded_sex_id"] == "all"
                and row["metric_id"] in CLAIM_METRICS and row["value"] is not None
                and not item.get("redaction_reason") and row["sample_size"] >= 30):
            candidates.append(make_claim("observation", rid, public_index=index,
                                         comparison_ledger=ledger))
    types = {"adjacent_quarter": "qoq", "like_quarter_annual": "yoy",
             "recorded_sex_slice": "sex", "entity_slice": "entity"}
    for entry in comparisons:
        if not entry["comparable"] or entry["comparison_type"] not in types:
            continue
        current = index[entry["current_record_id"]]["record"]
        if (current["period_id"] != PERIODS[-1] or current["field_of_study_id"] not in FOCAL_FIELDS
                or current["metric_id"] not in COMPARISON_METRICS):
            continue
        if (entry["comparison_type"] == "entity_slice"
                and current["geography_id"] != "01"):
            continue  # Predeclared 01 versus reviewed reference 02; no outcome ranking.
        candidates.append(make_claim(types[entry["comparison_type"]], entry["comparison_id"],
                                     public_index=index, comparison_ledger=ledger))
    candidates.sort(key=lambda claim: claim["claim_id"])
    if len({claim["claim_id"] for claim in candidates}) != len(candidates):
        raise ValueError("duplicate canonical claim ID")
    opening = select_opening_claims(candidates)
    return candidates, [claim["claim_id"] for claim in opening]


def _limitations(profiles: dict, comparisons: list[dict], opening: list[str]) -> list[str]:
    limits = [VALID_LIMITATIONS["precision"], VALID_LIMITATIONS["overlap"],
              VALID_LIMITATIONS["income"]]
    if any(cell["value"] is None for section in SECTIONS for cell in profiles[section]):
        limits.append(VALID_LIMITATIONS["sparse"])
    if any(item.get("redaction_reason") for item in profiles["record_index"].values()):
        limits.append(VALID_LIMITATIONS["redaction"])
    if any("unknown_edition_date" in item["limitations"] for item in comparisons):
        limits.append(VALID_LIMITATIONS["edition"])
    if not opening:
        limits.append(VALID_LIMITATIONS["empty"])
    return limits


def _assemble(public_by_snapshot: Mapping[str, dict], acceptance: Mapping[str, object],
              coverage_audits: Mapping[str, dict], definition_registry: dict) -> dict:
    """Compute candidate content; production entrypoint also enforces frozen pins."""
    index = index_public_estimates(public_by_snapshot,
                                   {"manifest": acceptance, "audits": coverage_audits})
    if tuple(index["periods"]) != tuple(PERIODS):
        raise ValueError("accepted periods differ from Phase 3 scope")
    profiles = build_profiles(index, coverage_audits, latest_period_id=PERIODS[-1])
    if (definition_registry.get("entity_reference_code") != "02"
            or definition_registry.get("metric_manifest_sha256") != acceptance["metric_manifest_sha256"]):
        raise ValueError("reviewed definition registry differs from acceptance")
    comparisons = build_comparison_ledger(profiles, registry=definition_registry)
    enriched = _display_items(profiles, index["catalogs"], definition_registry)
    public_profiles = {key: deepcopy(value) for key, value in profiles.items() if key != "record_index"}
    for section in SECTIONS:
        for cell in public_profiles[section]:
            cell["grain"] = list(cell["grain"])
    coverage = _coverage(public_profiles)
    claims, opening = _claims(enriched, comparisons)
    packet = {"schema_version": "2.0", "source_manifest": _source_manifest(index, acceptance),
              "record_index": enriched, "profiles": public_profiles, "coverage": coverage,
              "comparisons": comparisons, "claims": claims, "opening_claim_ids": opening,
              "limitations": _limitations(profiles, comparisons, opening)}
    packet["content_digest"] = _digest(packet)
    return packet


def _json_safe(value: object, seen: set[int] | None = None, depth: int = 0) -> bool:
    if depth > 100:
        return False
    if value is None or type(value) in (bool, str):
        return True
    if type(value) is int:
        return abs(value) <= 2**53 - 1
    if type(value) is float:
        return math.isfinite(value)
    if type(value) in (list, tuple, dict):
        seen = seen if seen is not None else set()
        identity = id(value)
        if identity in seen:
            return False
        seen.add(identity)
        try:
            if type(value) is dict:
                return all(type(key) is str and _json_safe(item, seen, depth + 1)
                           for key, item in value.items())
            return all(_json_safe(item, seen, depth + 1) for item in value)
        finally:
            seen.remove(identity)
    return False


def validate_analysis_packet(packet: dict) -> list[dict]:
    """Validate shape, independent accepted pins and all derived public claims."""
    errors: list[dict] = []
    if not isinstance(packet, dict) or not _json_safe(packet):
        return [{"id": "json_scalars", "message": "packet contains unsafe JSON values"}]
    try:
        schema = json.loads(contract_path("analysis-v2.schema.json").read_text(encoding="utf-8"))
        for err in Draft202012Validator(schema).iter_errors(packet):
            errors.append({"id": "schema", "message": f"{'/'.join(map(str, err.path))}: {err.message}"})
            if len(errors) >= 20:
                return errors
        if errors:
            return errors
        if _digest({key: value for key, value in packet.items() if key != "content_digest"}) != packet["content_digest"]:
            errors.append({"id": "content_digest", "message": "packet content digest differs"})
        trusted = _load_reference()
        observed = _reference_from_packet(packet)
        if observed != trusted:
            errors.append({"id": "trusted_reference", "message": "sanitized inputs or source manifest differ from independent accepted pins"})
        index, profiles = packet["record_index"], packet["profiles"]
        if (len(profiles["periods"]) != 8 or profiles["periods"] != list(PERIODS)
                or set(packet["source_manifest"]["sources"]) != set(SNAPSHOTS)):
            errors.append({"id": "scope", "message": "period or source inventory differs"})
        if any(key != item["record_id"] or item["record"]["source_snapshot_id"] not in SNAPSHOTS
               or item["snapshot_sha256"] != packet["source_manifest"]["sources"][item["record"]["source_snapshot_id"]]["sha256"]
               or tuple(item["grain"]) != tuple(item["record"][name] for name in GRAIN)
               or key != "v2r:" + _digest(list(item["grain"]))
               for key, item in index.items()):
            errors.append({"id": "record_identity", "message": "record ID, grain or source differs"})
        for section in SECTIONS:
            for cell in profiles[section]:
                item = index.get(cell["record_id"])
                if item is None or cell["value"] != item["record"]["value"]:
                    errors.append({"id": "profile_reference", "message": "profile cell differs from sanitized record"})
                    break
                if cell["reason"] == "complementary_suppression" and item.get("redaction_reason") != "complementary_suppression":
                    errors.append({"id": "profile_redaction", "message": "redacted profile lacks sanitized source"})
                    break
        if _coverage(profiles) != packet["coverage"]:
            errors.append({"id": "coverage", "message": "coverage does not equal profile cells"})
        registry = load_definition_registry(entity_reference_code="02")
        regenerated = build_comparison_ledger({**profiles, "record_index": index}, registry=registry)
        if regenerated != packet["comparisons"]:
            errors.append({"id": "comparisons", "message": "ledger differs from recomputed public pairs"})
        claims, opening = _claims(index, regenerated)
        if claims != packet["claims"] or any(validate_claim(claim, public_index=index,
                          comparison_ledger={row["comparison_id"]: row for row in regenerated}) for claim in packet["claims"]):
            errors.append({"id": "claims", "message": "claims differ from canonical public evidence"})
        if opening != packet["opening_claim_ids"]:
            errors.append({"id": "opening", "message": "opening IDs differ from supported selection"})
        if _limitations({**profiles, "record_index": index}, regenerated, opening) != packet["limitations"]:
            errors.append({"id": "limitations", "message": "publication limitations differ from source outcomes"})
    except (ValueError, KeyError, TypeError, FileNotFoundError, OverflowError) as exc:
        errors.append({"id": "semantic", "message": str(exc)})
    return errors


def build_analysis_packet(public_by_snapshot: Mapping[str, dict], acceptance: Mapping[str, object],
                          coverage_audits: Mapping[str, dict], definition_registry: dict) -> dict:
    """Assemble then fail closed unless trusted reference and semantics agree."""
    packet = _assemble(public_by_snapshot, acceptance, coverage_audits, definition_registry)
    errors = validate_analysis_packet(packet)
    if errors:
        raise ValueError(f"analytical packet failed validation: {errors[:3]}")
    return packet
