"""Deterministic, read-only agent replay for evidence-aware local builds."""
from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator
from referencing import Registry, Resource

from .insights import generate_insights, validate_insights
from .resources import contract_path

AGENT_SCHEMA = contract_path("agent-run.schema.json")
INSIGHT_SCHEMA = contract_path("insight.schema.json")

ROLE_LABELS = (
    ("source_scout", "Source Scout"),
    ("schema_mapper", "Schema Mapper"),
    ("data_quality_guardian", "Data Quality Guardian"),
    ("insight_analyst", "Insight Analyst"),
    ("visualization_planner", "Visualization Planner"),
    ("publisher", "Publisher"),
)
PUBLIC_STATES = {"MEASURED", "REVIEW", "UNKNOWN", "BLOCKED"}
_SAFE_ID = re.compile(r"^[a-z0-9][a-z0-9_.:-]{0,127}$")
_INSTRUCTION_MARKERS = (
    "ignore previous", "ignore all", "system prompt", "developer message",
    "run command", "tool call", "activate source", "activa la fuente",
    "instrucciones anteriores", "ejecuta el comando",
)


def _instruction_like(value: str) -> bool:
    normalized = value.casefold().replace("_", " ").replace("-", " ")
    return any(marker in normalized for marker in _INSTRUCTION_MARKERS)


def _safe_catalog_id(item: dict[str, Any], position: int) -> str:
    candidate = str(item.get("source_id") or item.get("id") or "")
    return candidate if _SAFE_ID.fullmatch(candidate) and not _instruction_like(candidate) else f"untrusted_catalog_item_{position}"


def _role(
    role_id: str,
    label: str,
    status: str,
    summary: str,
    proposals: list[dict[str, str]],
    evidence_refs: list[str],
) -> dict[str, Any]:
    return {
        "id": role_id,
        "label": label,
        "status": status,
        "read_only": True,
        "summary": summary,
        "proposals": proposals,
        "evidence_refs": evidence_refs,
    }


def run_agents(
    dataset: dict[str, Any],
    quality: dict[str, Any],
    comparisons: list[dict[str, Any]],
    catalog: list[dict[str, Any]],
) -> dict[str, Any]:
    """Replay six bounded roles without tools, writes, network, or inference."""
    del comparisons  # Agents consume comparison results but never calculate them.
    evidence_ids = sorted(item["id"] for item in dataset.get("evidence", []))
    insights = generate_insights(dataset)
    blocked_rows = [row["id"] for row in dataset.get("observations", []) if row.get("status") == "BLOCKED"]
    source_proposals = [
        {
            "action": "review_source",
            "target_id": _safe_catalog_id(item, position),
            "status": "REVIEW",
            "rationale": "Candidate remains inactive pending human review of authority, terms and method.",
        }
        for position, item in enumerate(catalog, start=1)
    ]
    bridge_proposals = [
        {
            "action": "review_bridge",
            "target_id": item["id"],
            "status": "REVIEW",
            "rationale": "Editorial bridge remains a proposal and does not equate distinct concepts.",
        }
        for item in dataset.get("dimensions", {}).get("bridges", [])
    ]
    quality_ok = quality.get("status") in {"MEASURED", "REVIEW"} and bool(quality.get("publishable"))
    allowed = quality_ok and not blocked_rows and bool(insights)
    roles = [
        _role("source_scout", "Source Scout", "REVIEW", f"Inspected {len(catalog)} catalog candidates without activation.", source_proposals, []),
        _role("schema_mapper", "Schema Mapper", "REVIEW", f"Kept {len(bridge_proposals)} editorial bridges in review.", bridge_proposals, evidence_ids),
        _role(
            "data_quality_guardian", "Data Quality Guardian", "REVIEW" if quality_ok else "BLOCKED",
            "Accepted the supplied quality gate." if quality_ok else "Quality gate denies publication.", [], evidence_ids,
        ),
        _role("insight_analyst", "Insight Analyst", "REVIEW" if insights else "UNKNOWN", f"Built {len(insights)} evidence-bound insight packets.", [], evidence_ids),
        _role(
            "visualization_planner", "Visualization Planner", "REVIEW" if insights else "UNKNOWN",
            "Proposed descriptive rendering with synthetic and precision labels." if insights else "No descriptive rendering proposed because no claim matched.", [], evidence_ids,
        ),
        _role(
            "publisher", "Publisher", "REVIEW" if allowed else "BLOCKED",
            "Local artifact gate passed." if allowed else "Local artifact gate retained the build.", [], evidence_ids,
        ),
    ]
    return {"mode": "deterministic_replay", "publication_allowed": allowed, "roles": roles, "insights": insights}


def _schema_errors(value: Any, path: Path) -> list[str]:
    schema = json.loads(path.read_text(encoding="utf-8"))
    insight_schema = json.loads(INSIGHT_SCHEMA.read_text(encoding="utf-8"))
    registry = Registry().with_resource(insight_schema["$id"], Resource.from_contents(insight_schema))
    validator = Draft202012Validator(schema, registry=registry)
    errors = sorted(validator.iter_errors(value), key=lambda error: list(error.absolute_path))
    return [f"schema:{'/'.join(map(str, error.absolute_path)) or '$'}:{error.message}" for error in errors]


def validate_agent_run(
    result: dict[str, Any],
    dataset: dict[str, Any],
    quality: dict[str, Any],
    comparisons: list[dict[str, Any]] | None = None,
) -> list[str]:
    """Return all structural, evidence, claim, and authority violations."""
    errors = _schema_errors(result, AGENT_SCHEMA)
    if errors:
        return errors
    errors.extend(validate_insights(result["insights"], dataset, comparisons or []))
    evidence = {item["id"] for item in dataset.get("evidence", [])}
    bridges = {item["id"] for item in dataset.get("dimensions", {}).get("bridges", [])}
    expected_roles = dict(ROLE_LABELS)
    actual_ids = [role["id"] for role in result["roles"]]
    if actual_ids != list(expected_roles):
        errors.append("roles:expected the six contracted roles in canonical order")
    for role in result["roles"]:
        if role["label"] != expected_roles.get(role["id"]):
            errors.append(f"role:{role['id']}:label does not match the contract")
        if not role["read_only"]:
            errors.append(f"role:{role['id']}:must be read-only")
        if _instruction_like(role["summary"]):
            errors.append(f"role:{role['id']}:instruction-like summary is forbidden")
        unknown_refs = set(role["evidence_refs"]) - evidence
        if unknown_refs:
            errors.append(f"role:{role['id']}:unknown evidence {sorted(unknown_refs)}")
        for proposal in role["proposals"]:
            if proposal["status"] != "REVIEW":
                errors.append(f"role:{role['id']}:proposal attempted promotion")
            if not _SAFE_ID.fullmatch(proposal["target_id"]):
                errors.append(f"role:{role['id']}:unsafe or instruction-like target id")
            if _instruction_like(proposal["target_id"]) or _instruction_like(proposal["rationale"]):
                errors.append(f"role:{role['id']}:instruction-like proposal content is forbidden")
            if proposal["action"] == "review_bridge" and proposal["target_id"] not in bridges:
                errors.append(f"role:{role['id']}:proposal references an unknown bridge")

    quality_status = quality.get("status")
    if quality_status not in PUBLIC_STATES:
        errors.append("quality:status must use one of the four uppercase public states")
    blocked = any(row.get("status") == "BLOCKED" for row in dataset.get("observations", []))
    should_allow = quality_status in {"MEASURED", "REVIEW"} and bool(quality.get("publishable")) and not blocked and bool(result["insights"])
    if result["publication_allowed"] != should_allow:
        errors.append("publication_allowed:inconsistent with quality, blocked rows or matched insights")
    return errors
