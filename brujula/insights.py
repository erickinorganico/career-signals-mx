"""Deterministic, evidence-bound insight packets.

This module deliberately does not call models, tools, or the network. It turns
validated observations into descriptive packets and validates that every claim
still points to the exact supplied evidence.
"""
from __future__ import annotations

import re
import unicodedata
from collections.abc import Iterable
from typing import Any


_NUMBER = re.compile(r"(?<![\w])[-+]?\d[\d,]*(?:\.\d+)?%?")
_FORBIDDEN_CLAIMS = (
    "caus", "provoc", "ocasion", "debido a", "demuestra que", "genera un",
    "leads to", "resulted in", "because of", "statistically significant",
    "estadisticamente signific", "vacan", "oferta de empleo", "job opening",
    "equivale a una ocupacion", "es una ocupacion", "field equals occupation",
)
_INSTRUCTION_LIKE = (
    "ignore previous", "ignore all", "system prompt", "developer message",
    "instrucciones anteriores", "ejecuta el comando", "run this command",
    "tool call", "llama a la herramienta", "activa la fuente",
)


def _plain(text: str) -> str:
    normalized = unicodedata.normalize("NFKD", text.casefold())
    return "".join(char for char in normalized if not unicodedata.combining(char))


def _maps(dataset: dict[str, Any]) -> tuple[dict[tuple[str, str], str], dict[str, str], dict[str, str], dict[str, str]]:
    dimensions = dataset["dimensions"]
    concepts = {
        (concept_type, item["id"]): item["label"]
        for concept_type, key in (("field_of_study", "fields"), ("occupation", "occupations"))
        for item in dimensions[key]
    }
    geographies = {item["id"]: item["label"] for item in dimensions["geographies"]}
    periods = {item["id"]: item["label"] for item in dimensions["periods"]}
    metrics = {item["id"]: item["label"] for item in dataset["metrics"]}
    return concepts, geographies, periods, metrics


def _display_value(row: dict[str, Any]) -> str:
    if row["value"] is None:
        return "sin valor disponible"
    return f"{row['value']:,.12g} {row['unit']}"


def observation_claim(row: dict[str, Any], dataset: dict[str, Any]) -> str:
    """Return the only accepted descriptive claim for an observation row."""
    concepts, geographies, periods, metrics = _maps(dataset)
    subject = "fixture sintético" if row["synthetic"] else "dataset validado"
    return (
        f"El {subject} registra {metrics[row['metric_id']]} de {_display_value(row)} "
        f"para {concepts[(row['concept_type'], row['concept_id'])]} en {geographies[row['geography_id']]}, "
        f"{periods[row['period_id']]}, con población {row['population']} y método "
        f"{row['methodology_id']}, según la fuente {row['source_id']}."
    )


def _title(row: dict[str, Any], concepts: dict[tuple[str, str], str]) -> str:
    label = concepts[(row["concept_type"], row["concept_id"])]
    return f"Señal ilustrativa: {label}" if row["synthetic"] else f"Señal observada: {label}"


def _interpretation(row: dict[str, Any]) -> str:
    return (
        "Describe únicamente el fixture, la población y el periodo indicados."
        if row["synthetic"]
        else "Describe únicamente la población y el periodo indicados."
    )


def _recommendation() -> str:
    return "Revise fuente, población, unidad, método y precisión antes de usar la señal."


def _unknowns(row: dict[str, Any]) -> list[str]:
    values = ["El fixture no es una estimación oficial." if row["synthetic"] else "La observación no identifica causas."]
    if row.get("coefficient_variation") is None:
        values.append("La precisión muestral no está cuantificada.")
    return values


def generate_insights(dataset: dict[str, Any]) -> list[dict[str, Any]]:
    """Generate one latest, available packet per field of study."""
    concepts, _, _, _ = _maps(dataset)
    ends = {item["id"]: item["end"] for item in dataset["dimensions"]["periods"]}
    selected: dict[str, dict[str, Any]] = {}
    for row in dataset.get("observations", []):
        if row.get("concept_type") != "field_of_study" or row.get("value") is None or row.get("status") in {"UNKNOWN", "BLOCKED"}:
            continue
        current = selected.get(row["concept_id"])
        candidate_key = (ends[row["period_id"]], row["metric_id"], row["id"])
        current_key = None if current is None else (ends[current["period_id"]], current["metric_id"], current["id"])
        if current_key is None or candidate_key > current_key:
            selected[row["concept_id"]] = row

    packets: list[dict[str, Any]] = []
    for concept_id in sorted(selected):
        row = selected[concept_id]
        synthetic = bool(row["synthetic"])
        packets.append({
            "id": f"insight_{row['id']}",
            "status": "REVIEW" if synthetic else row["status"],
            "title": _title(row, concepts),
            "observation": observation_claim(row, dataset),
            "interpretation": _interpretation(row),
            "recommendation": _recommendation(),
            "evidence_refs": sorted(set(row["evidence_refs"])),
            "unknowns": _unknowns(row),
            "synthetic": synthetic,
        })
    return packets


def _packet_text(packet: dict[str, Any]) -> str:
    fields = [str(packet.get(key, "")) for key in ("title", "observation", "interpretation", "recommendation")]
    fields.extend(str(value) for value in packet.get("unknowns", []))
    return " ".join(fields)


def validate_insights(packets: list[dict[str, Any]], dataset: dict[str, Any], comparisons: Iterable[dict[str, Any]] = ()) -> list[str]:
    """Validate semantic claim/evidence binding after structural validation."""
    del comparisons  # v1 emits observation packets only; comparison prose fails closed.
    concepts, _, _, _ = _maps(dataset)
    observation_anchors = {
        observation_claim(row, dataset): {
            "evidence_refs": set(row.get("evidence_refs", [])),
            "id": f"insight_{row['id']}",
            "synthetic": bool(row["synthetic"]),
            "status": "REVIEW" if row["synthetic"] else row["status"],
            "title": _title(row, concepts),
            "interpretation": _interpretation(row),
            "recommendation": _recommendation(),
            "unknowns": _unknowns(row),
            "source_id": row["source_id"],
        }
        for row in dataset.get("observations", [])
    }
    anchors = observation_anchors
    evidence_by_id = {item["id"]: item for item in dataset.get("evidence", [])}
    errors: list[str] = []
    for packet in packets:
        packet_id = str(packet.get("id", "<missing>"))
        claim = packet.get("observation")
        anchor = anchors.get(claim)
        if anchor is None:
            errors.append(f"insight:{packet_id}:claim is not an exact supplied v1 observation")
            anchor = {"evidence_refs": set(), "id": None, "synthetic": None, "status": None, "title": None, "interpretation": None, "recommendation": None, "unknowns": None, "source_id": None}
        actual_refs = set(packet.get("evidence_refs", []))
        unknown_refs = actual_refs - set(evidence_by_id)
        if unknown_refs:
            errors.append(f"insight:{packet_id}:unknown evidence {sorted(unknown_refs)}")
        if claim in anchors and actual_refs != anchor["evidence_refs"]:
            errors.append(f"insight:{packet_id}:evidence is incongruent with the supplied claim")
        for ref in actual_refs & set(evidence_by_id):
            if anchor["source_id"] and evidence_by_id[ref]["source_id"] != anchor["source_id"]:
                errors.append(f"insight:{packet_id}:evidence source is incongruent with the observation")
        if claim in anchors:
            for field in ("id", "synthetic", "status"):
                if anchor[field] is not None and packet.get(field) != anchor[field]:
                    errors.append(f"insight:{packet_id}:{field} is incongruent with the supplied claim")
            if anchor["title"] is not None and packet.get("title") != anchor["title"]:
                errors.append(f"insight:{packet_id}:title is incongruent with the supplied concept")
            for field in ("interpretation", "recommendation", "unknowns"):
                if anchor[field] is not None and packet.get(field) != anchor[field]:
                    errors.append(f"insight:{packet_id}:{field} is not the sanctioned deterministic text")
        for field in ("interpretation", "recommendation"):
            if _NUMBER.search(str(packet.get(field, ""))):
                errors.append(f"insight:{packet_id}:{field} introduces an unbound numeric claim")
        if any(_NUMBER.search(str(value)) for value in packet.get("unknowns", [])):
            errors.append(f"insight:{packet_id}:unknowns introduce an unbound numeric claim")
        normalized = _plain(_packet_text(packet))
        if any(term in normalized for term in _FORBIDDEN_CLAIMS):
            errors.append(f"insight:{packet_id}:causal, significance, vacancy or concept-identity claim is forbidden")
        if any(term in normalized for term in _INSTRUCTION_LIKE):
            errors.append(f"insight:{packet_id}:instruction-like content is forbidden")
    return errors
