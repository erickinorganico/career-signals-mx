from __future__ import annotations

from datetime import date
import math
import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator, FormatChecker

from .data import SCHEMA_PATH


def _check(checks: list[dict[str, str]], ident: str, status: str, message: str) -> None:
    checks.append({"id": ident, "status": status, "message": message})


def validate_dataset(dataset: dict[str, Any], as_of: date | None = None) -> dict[str, Any]:
    checks: list[dict[str, str]] = []
    row_statuses: dict[str, str] = {}
    try:
        schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
        errors = sorted(Draft202012Validator(schema, format_checker=FormatChecker()).iter_errors(dataset), key=lambda e: list(e.path))
    except Exception as exc:
        errors = [exc]
    if errors:
        message = "; ".join(getattr(error, "message", str(error)) for error in errors[:5])
        _check(checks, "schema", "FAIL", message)
        return {"status": "BLOCKED", "publishable": False, "checks": checks, "row_statuses": row_statuses, "freshness": {"status": "BLOCKED", "as_of": (as_of or date.today()).isoformat(), "latest_period_end": None, "age_days": None, "threshold_days": 180, "message": "Schema inválido"}}
    _check(checks, "schema", "PASS", "Dataset conforms to schema")
    dims = dataset["dimensions"]
    sources = {item["id"]: item for item in dataset["sources"]}
    evidence = {item["id"]: item for item in dataset["evidence"]}
    geographies = {item["id"] for item in dims["geographies"]}
    periods = {item["id"]: item for item in dims["periods"]}
    metrics = {item["id"]: item for item in dataset["metrics"]}
    fields = {item["id"] for item in dims["fields"]}
    occupations = {item["id"] for item in dims["occupations"]}
    industries = {item["id"] for item in dims["industries"]}
    valid = True

    def fail(ident: str, message: str) -> None:
        nonlocal valid
        valid = False
        _check(checks, ident, "FAIL", message)

    if len(sources) != len(dataset["sources"]): fail("source_ids", "Duplicate source IDs")
    if len({item["id"] for item in dataset["evidence"]}) != len(dataset["evidence"]): fail("evidence_ids", "Duplicate evidence IDs")
    if len({item["id"] for item in dataset["metrics"]}) != len(dataset["metrics"]): fail("metric_ids", "Duplicate metric IDs")
    if len({item["id"] for item in dims["geographies"]}) != len(dims["geographies"]): fail("geography_ids", "Duplicate geography IDs")
    if len({item["id"] for item in dims["fields"]}) != len(dims["fields"]): fail("field_ids", "Duplicate field IDs")
    if len({item["id"] for item in dims["occupations"]}) != len(dims["occupations"]): fail("occupation_ids", "Duplicate occupation IDs")
    if len({item["id"] for item in dims["industries"]}) != len(dims["industries"]): fail("industry_ids", "Duplicate industry IDs")
    if len({item["id"] for item in dims["bridges"]}) != len(dims["bridges"]): fail("bridge_ids", "Duplicate bridge IDs")
    for item in dataset["evidence"]:
        if item["source_id"] not in sources: fail("evidence_source", f"Evidence references unknown source: {item['id']}")
    if len(periods) != len(dims["periods"]): fail("period_ids", "Duplicate period IDs")
    for period in dims["periods"]:
        try:
            if date.fromisoformat(period["start"]) > date.fromisoformat(period["end"]): fail("period_ranges", f"Invalid range: {period['id']}")
            if date.fromisoformat(period["end"]) > (as_of or date.today()): fail("future_period", f"Period ends in the future: {period['id']}")
        except ValueError: fail("period_dates", f"Invalid period date: {period['id']}")
    for source in dataset["sources"]:
        if source["checked_at"]:
            try:
                if date.fromisoformat(source["checked_at"]) > (as_of or date.today()): fail("future_source", f"Source checked_at is in the future: {source['id']}")
            except ValueError: fail("source_dates", f"Invalid source checked_at: {source['id']}")
    for bridge in dims["bridges"]:
        if bridge["confidence"] is not None and not math.isfinite(bridge["confidence"]): fail("finite_confidence", f"Non-finite bridge confidence: {bridge['id']}")
    grains: set[tuple[str, str, str, str]] = set()
    metric_units = {item["id"]: (item["unit"], item["price_basis"]) for item in dataset["metrics"]}
    observation_ids: set[str] = set()
    for row in dataset["observations"]:
        if row["id"] in observation_ids: fail("observation_ids", f"Duplicate observation ID: {row['id']}")
        observation_ids.add(row["id"])
        row_statuses[row["id"]] = row["status"]
        grain = (row["concept_type"], row["concept_id"], row["geography_id"], row["period_id"] + "|" + row["metric_id"])
        if grain in grains: fail("duplicate_grain", f"Duplicate observation grain: {grain}")
        grains.add(grain)
        concept_ids = fields if row["concept_type"] == "field_of_study" else occupations
        if row["concept_id"] not in concept_ids: fail("concept_refs", f"Unknown concept: {row['concept_id']}")
        if row["geography_id"] not in geographies: fail("geography_refs", f"Unknown geography: {row['geography_id']}")
        if row["period_id"] not in periods: fail("period_refs", f"Unknown period: {row['period_id']}")
        if row["metric_id"] not in metrics: fail("metric_refs", f"Unknown metric: {row['metric_id']}")
        if row["source_id"] not in sources: fail("source_refs", f"Unknown source: {row['source_id']}")
        if not row["evidence_refs"]: fail("evidence_required", f"Observation lacks evidence: {row['id']}")
        for evidence_id in row["evidence_refs"]:
            if evidence_id not in evidence: fail("evidence_refs", f"Unknown evidence: {evidence_id}")
            elif evidence[evidence_id]["source_id"] != row["source_id"]: fail("evidence_source", f"Evidence/source mismatch: {row['id']}")
        if row["source_id"] in sources and not sources[row["source_id"]]["approved"]: fail("approved_source", f"Unapproved source: {row['source_id']}")
        expected_unit, expected_basis = metric_units.get(row["metric_id"], (None, None))
        if expected_unit and (row["unit"], row["price_basis"]) != (expected_unit, expected_basis): fail("metric_coherence", f"Unit/basis mismatch: {row['id']}")
        if row["value"] is not None:
            if not math.isfinite(row["value"]): fail("finite_values", f"Non-finite value: {row['id']}")
            if row["value"] < 0: fail("ranges", f"Negative value: {row['id']}")
            if row["unit"] == "percent" and row["value"] > 100: fail("ranges", f"Percent over 100: {row['id']}")
        if row["synthetic"] and row["value"] is not None and row["status"] != "REVIEW": fail("synthetic_status", f"Synthetic value must be REVIEW: {row['id']}")
        if row["value"] is None and row["status"] not in {"UNKNOWN", "BLOCKED"}: fail("null_status", f"Null value must be UNKNOWN or BLOCKED: {row['id']}")
        if row["value"] is not None and row["status"] in {"UNKNOWN", "BLOCKED"}: fail("value_status", f"Available value cannot be {row['status']}: {row['id']}")
        if row["status"] == "MEASURED" and row["synthetic"]: fail("synthetic_measured", f"Synthetic row cannot be MEASURED: {row['id']}")
        if row["value"] is not None and not row.get("precision_note"): fail("precision", f"Available value lacks precision note: {row['id']}")
        if row["coefficient_variation"] is not None and not math.isfinite(row["coefficient_variation"]): fail("finite_precision", f"Non-finite coefficient variation: {row['id']}")
        if row["status"] == "MEASURED" and (row.get("sample_size") is None or row["sample_size"] <= 0): fail("precision", f"Measured value lacks positive sample size: {row['id']}")
        if row["status"] == "MEASURED" and row.get("coefficient_variation") is None: fail("precision", f"Measured value lacks coefficient variation: {row['id']}")
        if row["status"] == "BLOCKED": valid = False
        if dataset["mode"] == "illustrative" and not row["synthetic"]: fail("synthetic_mode", f"Illustrative row must be synthetic: {row['id']}")
        if dataset["mode"] == "official_snapshot" and row["synthetic"]: fail("synthetic_mode", f"Official row cannot be synthetic: {row['id']}")
    if dataset["mode"] == "illustrative":
        if dataset.get("id") == "demo_pilot_2025" and (len(dims["fields"]) != 3 or len(dims["geographies"]) != 2 or len(dims["periods"]) != 3 or len(dataset["metrics"]) != 3):
            fail("pilot_dimensions", "demo_pilot_2025 requires 3 fields, 2 geographies, 3 periods and 3 metrics")
        expected = {(field["id"], geography["id"], period["id"], metric["id"])
                    for field in dims["fields"] for geography in dims["geographies"]
                    for period in dims["periods"] for metric in dataset["metrics"]}
        actual = {(row["concept_id"], row["geography_id"], row["period_id"], row["metric_id"])
                  for row in dataset["observations"] if row["concept_type"] == "field_of_study"}
        if actual != expected:
            fail("coverage", f"Illustrative field coverage mismatch: expected {len(expected)}, got {len(actual)}")
    for bridge in dims["bridges"]:
        known = {"field_of_study": fields, "occupation": occupations, "industry": industries}
        if bridge["from_id"] not in known.get(bridge["from_type"], set()) or bridge["to_id"] not in known.get(bridge["to_type"], set()): fail("bridge_refs", f"Unknown bridge endpoint: {bridge['id']}")
        if bridge["status"] != "REVIEW": fail("bridge_status", f"Bridge must remain REVIEW: {bridge['id']}")
        for ref in bridge["evidence_refs"]:
            if ref not in evidence: fail("bridge_evidence", f"Unknown bridge evidence: {ref}")
            elif evidence[ref]["source_id"] not in sources: fail("evidence_source", f"Evidence references unknown source: {ref}")
    _check(checks, "relations", "PASS" if valid else "FAIL", "References, grain, ranges and source coherence checked")
    today = as_of or date.today()
    referenced_period_ids = {row["period_id"] for row in dataset["observations"] if row["period_id"] in periods}
    latest = max((date.fromisoformat(periods[period_id]["end"]) for period_id in referenced_period_ids), default=None)
    age = (today - latest).days if latest else None
    freshness_status = "REVIEW" if dataset["mode"] == "illustrative" else ("MEASURED" if age is not None and age <= 180 else "REVIEW")
    if dataset["mode"] == "official_snapshot":
        fail("source_activation", "official_snapshot requires an activated approved source")
    freshness = {"status": freshness_status, "as_of": today.isoformat(), "latest_period_end": latest.isoformat() if latest else None, "age_days": age, "threshold_days": 180, "message": "Synthetic fixture freshness is illustrative" if dataset["mode"] == "illustrative" else "Period age warning"}
    values = [row for row in dataset["observations"] if row["value"] is not None]
    row_states = set(row_statuses.values())
    if not valid or "BLOCKED" in row_states:
        quality_status, publishable = "BLOCKED", False
    elif not dataset["observations"] or not values or row_states <= {"UNKNOWN"}:
        quality_status, publishable = "UNKNOWN", False
    elif dataset["mode"] == "illustrative" or "REVIEW" in row_states or freshness_status == "REVIEW":
        quality_status, publishable = "REVIEW", True
    else:
        quality_status, publishable = "MEASURED", True
    return {"status": quality_status, "publishable": publishable, "checks": checks, "row_statuses": row_statuses, "freshness": freshness}


def compare_observations(previous: dict[str, Any], current: dict[str, Any], periods_by_id: dict[str, Any] | None = None) -> dict[str, Any]:
    reasons: list[str] = []
    required = ("concept_type", "concept_id", "geography_id", "period_id", "metric_id", "value", "source_id", "population", "methodology_id", "unit", "price_basis", "status", "evidence_refs", "synthetic")
    for label, row in (("previous", previous), ("current", current)):
        for field in required:
            if field not in row: reasons.append(f"missing_{label}_{field}")
        if row.get("concept_type") not in {"field_of_study", "occupation"} or not row.get("concept_id"): reasons.append(f"invalid_{label}_concept")
        if row.get("status") not in {"MEASURED", "REVIEW", "UNKNOWN", "BLOCKED"}: reasons.append(f"invalid_{label}_status")
        if not row.get("evidence_refs"): reasons.append(f"missing_{label}_evidence")
        if row.get("value") is not None and (isinstance(row.get("value"), bool) or not isinstance(row.get("value"), (int, float))): reasons.append(f"invalid_{label}_value")
        if row.get("value") is not None and isinstance(row.get("value"), (int, float)) and not math.isfinite(row["value"]): reasons.append(f"nonfinite_{label}_value")
    fields = ("concept_type", "concept_id", "geography_id", "metric_id", "unit", "population", "methodology_id", "price_basis", "source_id", "synthetic")
    for field in fields:
        if previous.get(field) != current.get(field): reasons.append(f"different_{field}")
    if previous.get("value") is None or current.get("value") is None: reasons.append("null_value")
    if previous.get("status") in {"BLOCKED", "UNKNOWN"} or current.get("status") in {"BLOCKED", "UNKNOWN"}: reasons.append("unavailable_status")
    if previous.get("period_id") == current.get("period_id"): reasons.append("same_period")
    if periods_by_id is None:
        reasons.append("period_context_required")
    else:
        previous_period = periods_by_id.get(previous.get("period_id"))
        current_period = periods_by_id.get(current.get("period_id"))
        if previous_period is None or current_period is None:
            reasons.append("unknown_period")
        else:
            try:
                previous_start = date.fromisoformat(previous_period["start"])
                previous_end = date.fromisoformat(previous_period["end"])
                current_start = date.fromisoformat(current_period["start"])
                current_end = date.fromisoformat(current_period["end"])
                if previous_start > previous_end or current_start > current_end:
                    reasons.append("invalid_period_range")
                if current_start <= previous_end:
                    reasons.append("non_chronological_periods")
            except (KeyError, TypeError, ValueError):
                reasons.append("invalid_period_context")
    if not reasons:
        absolute = current["value"] - previous["value"]
        relative = None if previous["value"] == 0 else absolute / previous["value"] * 100
        if math.isfinite(absolute) and (relative is None or math.isfinite(relative)):
            return {"status": "REVIEW" if previous.get("status") == "REVIEW" or current.get("status") == "REVIEW" else "MEASURED", "comparable": True, "absolute_change": absolute, "relative_change_pct": relative, "reasons": [], "evidence_refs": sorted(set(previous.get("evidence_refs", [])) | set(current.get("evidence_refs", [])))}
        reasons.append("nonfinite_change")
    return {"status": "BLOCKED", "comparable": False, "absolute_change": None, "relative_change_pct": None, "reasons": reasons, "evidence_refs": sorted(set(previous.get("evidence_refs", [])) | set(current.get("evidence_refs", [])))}
