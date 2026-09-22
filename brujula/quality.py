from __future__ import annotations

from datetime import date
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
        return {"status": "blocked", "publishable": False, "checks": checks, "row_statuses": row_statuses, "freshness": {"status": "unknown", "as_of": (as_of or date.today()).isoformat(), "latest_period_end": None, "age_days": None, "threshold_days": 180, "message": "Schema inválido"}}
    _check(checks, "schema", "PASS", "Dataset conforms to schema")
    dims = dataset["dimensions"]
    sources = {item["id"]: item for item in dataset["sources"]}
    evidence = {item["id"]: item for item in dataset["evidence"]}
    geographies = {item["id"] for item in dims["geographies"]}
    periods = {item["id"]: item for item in dims["periods"]}
    metrics = {item["id"]: item for item in dataset["metrics"]}
    fields = {item["id"] for item in dims["fields"]}
    occupations = {item["id"] for item in dims["occupations"]}
    valid = True

    def fail(ident: str, message: str) -> None:
        nonlocal valid
        valid = False
        _check(checks, ident, "FAIL", message)

    if len(sources) != len(dataset["sources"]): fail("source_ids", "Duplicate source IDs")
    if len(periods) != len(dims["periods"]): fail("period_ids", "Duplicate period IDs")
    for period in dims["periods"]:
        try:
            if date.fromisoformat(period["start"]) > date.fromisoformat(period["end"]): fail("period_ranges", f"Invalid range: {period['id']}")
        except ValueError: fail("period_dates", f"Invalid period date: {period['id']}")
    grains: set[tuple[str, str, str, str]] = set()
    metric_units = {item["id"]: (item["unit"], item["price_basis"]) for item in dataset["metrics"]}
    for row in dataset["observations"]:
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
            if row["value"] < 0: fail("ranges", f"Negative value: {row['id']}")
            if row["unit"] == "percent" and row["value"] > 100: fail("ranges", f"Percent over 100: {row['id']}")
        if row["synthetic"] and row["value"] is not None and row["status"] != "REVIEW": fail("synthetic_status", f"Synthetic value must be REVIEW: {row['id']}")
        if row["status"] == "BLOCKED": valid = False
    for bridge in dims["bridges"]:
        known = {"field_of_study": fields, "occupation": occupations, "industry": {x["id"] for x in dims["industries"]}}
        if bridge["from_id"] not in known.get(bridge["from_type"], set()) or bridge["to_id"] not in known.get(bridge["to_type"], set()): fail("bridge_refs", f"Unknown bridge endpoint: {bridge['id']}")
        if bridge["status"] != "REVIEW": fail("bridge_status", f"Bridge must remain REVIEW: {bridge['id']}")
        for ref in bridge["evidence_refs"]:
            if ref not in evidence: fail("bridge_evidence", f"Unknown bridge evidence: {ref}")
    _check(checks, "relations", "PASS" if valid else "FAIL", "References, grain, ranges and source coherence checked")
    today = as_of or date.today()
    latest = max((date.fromisoformat(period["end"]) for period in periods.values()), default=None)
    age = (today - latest).days if latest else None
    freshness_status = "illustrative" if dataset["mode"] == "illustrative" else ("fresh" if age is not None and age <= 180 else "warning")
    freshness = {"status": freshness_status, "as_of": today.isoformat(), "latest_period_end": latest.isoformat() if latest else None, "age_days": age, "threshold_days": 180, "message": "Synthetic fixture freshness is illustrative" if dataset["mode"] == "illustrative" else "Period age warning"}
    return {"status": "valid" if valid else "blocked", "publishable": valid, "checks": checks, "row_statuses": row_statuses, "freshness": freshness}


def compare_observations(previous: dict[str, Any], current: dict[str, Any]) -> dict[str, Any]:
    reasons: list[str] = []
    fields = ("concept_type", "concept_id", "geography_id", "metric_id", "unit", "population", "methodology_id", "price_basis", "source_id", "synthetic")
    for field in fields:
        if previous.get(field) != current.get(field): reasons.append(f"different_{field}")
    if previous.get("value") is None or current.get("value") is None: reasons.append("null_value")
    if previous.get("status") in {"BLOCKED", "UNKNOWN"} or current.get("status") in {"BLOCKED", "UNKNOWN"}: reasons.append("unavailable_status")
    if previous.get("period_id") == current.get("period_id"): reasons.append("same_period")
    if not reasons:
        absolute = current["value"] - previous["value"]
        relative = None if previous["value"] == 0 else absolute / previous["value"] * 100
        return {"status": "descriptive" if previous.get("status") == "REVIEW" or current.get("status") == "REVIEW" else "comparable", "comparable": True, "absolute_change": absolute, "relative_change_pct": relative, "reasons": [], "evidence_refs": sorted(set(previous.get("evidence_refs", [])) | set(current.get("evidence_refs", [])))}
    return {"status": "blocked", "comparable": False, "absolute_change": None, "relative_change_pct": None, "reasons": reasons, "evidence_refs": sorted(set(previous.get("evidence_refs", [])) | set(current.get("evidence_refs", [])))}
