"""Deterministic, read-only agent replay for evidence-aware local builds."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
AGENT_SCHEMA = ROOT / "contracts" / "agent-run.schema.json"
INSIGHT_SCHEMA = ROOT / "contracts" / "insight.schema.json"

ROLE_LABELS = (
    ("source_scout", "Source Scout"),
    ("schema_mapper", "Schema Mapper"),
    ("data_quality_guardian", "Data Quality Guardian"),
    ("insight_analyst", "Insight Analyst"),
    ("visualization_planner", "Visualization Planner"),
    ("publisher", "Publisher"),
)


def _catalog_id(item: dict[str, Any]) -> str:
    return str(item.get("source_id") or item.get("id") or "unknown_source")


def _maps(dataset: dict[str, Any]) -> tuple[dict[str, str], dict[str, str], dict[str, str]]:
    dims = dataset["dimensions"]
    concepts = {item["id"]: item["label"] for key in ("fields", "occupations") for item in dims[key]}
    geographies = {item["id"]: item["label"] for item in dims["geographies"]}
    periods = {item["id"]: item["label"] for item in dims["periods"]}
    return concepts, geographies, periods


def _display_value(row: dict[str, Any]) -> str:
    value = row["value"]
    if value is None:
        return "sin valor disponible"
    rendered = f"{value:,.2f}".rstrip("0").rstrip(".")
    return f"{rendered} {row['unit']}"


def _observation_text(row: dict[str, Any], dataset: dict[str, Any]) -> str:
    concepts, geographies, periods = _maps(dataset)
    prefix = "El fixture registra" if row["synthetic"] else "La observación registra"
    return (
        f"{prefix} {_display_value(row)} para {concepts[row['concept_id']]} en "
        f"{geographies[row['geography_id']]}, {periods[row['period_id']]}."
    )


def _make_insights(dataset: dict[str, Any]) -> list[dict[str, Any]]:
    concepts, _, _ = _maps(dataset)
    selected: dict[str, dict[str, Any]] = {}
    for row in dataset["observations"]:
        if row["concept_type"] != "field_of_study" or row["value"] is None or row["status"] == "BLOCKED":
            continue
        current = selected.get(row["concept_id"])
        if current is None or row["period_id"] > current["period_id"]:
            selected[row["concept_id"]] = row
    insights = []
    for concept_id in sorted(selected):
        row = selected[concept_id]
        synthetic = bool(row["synthetic"])
        unknowns = ["No es una estimación oficial." if synthetic else "No establece causalidad."]
        if row.get("coefficient_variation") is None:
            unknowns.append("La precisión muestral no está cuantificada.")
        insights.append({
            "id": f"insight_{row['id']}",
            "status": "REVIEW" if synthetic or row["status"] == "REVIEW" else row["status"],
            "title": f"Señal ilustrativa: {concepts[concept_id]}" if synthetic else f"Señal observada: {concepts[concept_id]}",
            "observation": _observation_text(row, dataset),
            "interpretation": "Sirve para probar el flujo de comparación y evidencia; no describe el mercado laboral real." if synthetic else "Describe la población y el periodo indicados, sin identificar una causa.",
            "recommendation": "Consulte fuente, población, unidad y precisión antes de usar esta señal en una decisión.",
            "evidence_refs": sorted(set(row["evidence_refs"])),
            "unknowns": unknowns,
            "synthetic": synthetic,
        })
    return insights


def _role(role_id: str, label: str, status: str, summary: str,
          proposals: list[dict[str, str]], evidence_refs: list[str]) -> dict[str, Any]:
    return {"id": role_id, "label": label, "status": status, "read_only": True,
            "summary": summary, "proposals": proposals, "evidence_refs": evidence_refs}


def run_agents(dataset: dict[str, Any], quality: dict[str, Any],
               comparisons: list[dict[str, Any]], catalog: list[dict[str, Any]]) -> dict[str, Any]:
    """Run a deterministic replay. Catalog text is treated only as untrusted data."""
    evidence_ids = sorted(item["id"] for item in dataset.get("evidence", []))
    insights = _make_insights(dataset)
    blocked_rows = [row["id"] for row in dataset.get("observations", []) if row["status"] == "BLOCKED"]
    source_proposals = [
        {"action": "review_source", "target_id": _catalog_id(item), "status": "REVIEW",
         "rationale": "Candidate remains inactive until a human verifies authority, terms and method."}
        for item in catalog
    ]
    bridge_proposals = [
        {"action": "review_bridge", "target_id": item["id"], "status": "REVIEW",
         "rationale": "Editorial bridge cannot equate a field of study with an occupation."}
        for item in dataset.get("dimensions", {}).get("bridges", [])
    ]
    allowed = bool(quality.get("publishable")) and not blocked_rows and bool(insights)
    roles = [
        _role("source_scout", "Source Scout", "REVIEW" if source_proposals else "PASS",
              f"Inspected {len(catalog)} catalog candidates without activating any source.", source_proposals, []),
        _role("schema_mapper", "Schema Mapper", "REVIEW" if bridge_proposals else "PASS",
              f"Kept {len(bridge_proposals)} editorial bridges in REVIEW.", bridge_proposals, evidence_ids),
        _role("data_quality_guardian", "Data Quality Guardian", "PASS" if quality.get("publishable") else "BLOCKED",
              "Accepted the supplied quality gate." if quality.get("publishable") else "Quality gate denies publication.", [], evidence_ids),
        _role("insight_analyst", "Insight Analyst", "PASS" if insights else "BLOCKED",
              f"Built {len(insights)} evidence-bound insight packets.", [], evidence_ids),
        _role("visualization_planner", "Visualization Planner", "PASS" if insights else "BLOCKED",
              "Proposed descriptive rendering with synthetic and precision labels.", [], evidence_ids),
        _role("publisher", "Publisher", "PASS" if allowed else "BLOCKED",
              "Publication gate passed." if allowed else "Publication gate retained the build.", [], evidence_ids),
    ]
    return {"mode": "deterministic_replay", "publication_allowed": allowed,
            "roles": roles, "insights": insights}


def _schema_errors(value: Any, path: Path) -> list[str]:
    schema = json.loads(path.read_text(encoding="utf-8"))
    errors = sorted(Draft202012Validator(schema).iter_errors(value), key=lambda error: list(error.path))
    return [f"schema:{'/'.join(map(str, error.path)) or '$'}:{error.message}" for error in errors]


def validate_agent_run(result: dict[str, Any], dataset: dict[str, Any],
                       quality: dict[str, Any]) -> list[str]:
    """Return contract errors; an empty list means the replay is safe to publish."""
    errors = _schema_errors(result, AGENT_SCHEMA)
    for insight in result.get("insights", []):
        errors.extend(_schema_errors(insight, INSIGHT_SCHEMA))
    if errors:
        return errors
    evidence = {item["id"] for item in dataset["evidence"]}
    allowed_observations = {_observation_text(row, dataset) for row in dataset["observations"]}
    for insight in result["insights"]:
        unknown_refs = set(insight["evidence_refs"]) - evidence
        if unknown_refs:
            errors.append(f"insight:{insight['id']}:unknown evidence {sorted(unknown_refs)}")
        if insight["observation"] not in allowed_observations:
            errors.append(f"insight:{insight['id']}:observation or numeric claim is not dataset-derived")
        if not insight["evidence_refs"]:
            errors.append(f"insight:{insight['id']}:evidence is required")
    expected_roles = {role_id for role_id, _ in ROLE_LABELS}
    actual_roles = {role["id"] for role in result["roles"]}
    if actual_roles != expected_roles:
        errors.append("roles:expected the six contracted roles exactly")
    for role in result["roles"]:
        if not role["read_only"]:
            errors.append(f"role:{role['id']}:must be read-only")
        for proposal in role["proposals"]:
            if proposal["status"] != "REVIEW":
                errors.append(f"role:{role['id']}:proposal attempted promotion")
    blocked = any(row["status"] == "BLOCKED" for row in dataset["observations"])
    should_allow = bool(quality.get("publishable")) and not blocked and bool(result["insights"])
    if result["publication_allowed"] != should_allow:
        errors.append("publication_allowed:inconsistent with quality, blocked rows or insight availability")
    return errors
