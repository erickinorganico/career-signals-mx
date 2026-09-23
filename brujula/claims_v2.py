"""Deterministic Spanish claims from sanitized ENOE public records."""

from __future__ import annotations

import hashlib
import json
import math
from decimal import Decimal, ROUND_HALF_UP


KINDS = {"observation": None, "qoq": "adjacent_quarter",
         "yoy": "like_quarter_annual", "sex": "recorded_sex_slice",
         "entity": "entity_slice"}
UNITS = {"people": "personas", "percent": "%", "MXN/month": "MXN mensuales nominales",
         "hours/week": "horas semanales"}
METRIC_LABELS = {
    "population_total": "población estimada", "occupied_total": "personas ocupadas estimadas",
    "pea_total": "población económicamente activa estimada",
    "unemployed_total": "personas desocupadas estimadas",
    "employment_rate": "tasa de ocupación", "participation_rate": "tasa de participación",
    "unemployment_rate": "tasa de desocupación",
    "positive_income_mean": "ingreso mensual medio positivo conocido",
    "positive_income_coverage": "cobertura de ingreso positivo conocido entre personas ocupadas",
    "no_income_count": "personas ocupadas sin ingreso registrado",
    "no_income_share": "proporción de personas ocupadas sin ingreso registrado",
    "unspecified_income_count": "personas ocupadas con ingreso no especificado",
    "unspecified_income_share": "proporción de personas ocupadas con ingreso no especificado",
    "main_job_informality_rate": "informalidad del empleo principal",
    "women_occupied_share": "proporción de mujeres entre personas ocupadas",
    "position_1_share": "proporción en posición ocupacional 1",
    "position_2_share": "proporción en posición ocupacional 2",
    "position_3_share": "proporción en posición ocupacional 3",
    "position_4_share": "proporción en posición ocupacional 4",
    "suboccupied_count": "personas subocupadas estimadas",
    "suboccupied_rate": "tasa de subocupación entre personas ocupadas",
    "known_hours_mean": "horas semanales medias conocidas",
    "known_hours_coverage": "cobertura de horas semanales conocidas entre personas ocupadas",
}
POPULATION_LABELS = {
    "national_15_plus_context": "personas residentes en el contexto nacional operativo de 15 años o más (código 98: edad operativamente desconocida)",
    "completed_professional_known_age": "personas residentes con estudios profesionales terminados y edad conocida de 15 años o más (código 97: 97 años o más; edad no especificada excluida; excluye estudios técnicos, de posgrado e incompletos)",
}


def _digest(value: object) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=False,
                                     separators=(",", ":"), allow_nan=False).encode("utf-8")).hexdigest()


def _number(value: int | float) -> str:
    if type(value) not in (int, float) or not math.isfinite(value):
        raise ValueError("claim quantity must be a finite public number")
    decimal = Decimal(str(value)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    return format(decimal, ",.2f").replace(",", "_").replace(".", ",").replace("_", " ")


def _record(item: dict) -> dict:
    if not isinstance(item, dict) or item.get("redaction_reason"):
        raise ValueError("redacted public record cannot support a claim")
    row = item.get("record")
    if not isinstance(row, dict) or row.get("status") not in ("REVIEW", "MEASURED"):
        raise ValueError("unsupported public record status")
    if row.get("value") is None or type(row["value"]) not in (int, float) or not math.isfinite(row["value"]):
        raise ValueError("suppressed or invalid public value")
    if not item.get("record_id", "").startswith("v2r:") or not item.get("snapshot_sha256"):
        raise ValueError("record provenance is absent")
    if not isinstance(row.get("evidence_refs"), list) or not row["evidence_refs"]:
        raise ValueError("record evidence is absent")
    display = item.get("display")
    if not isinstance(display, dict) or set(display) != {"field", "population", "metric", "geography", "recorded_sex", "period"}:
        raise ValueError("safe display metadata is absent")
    if (display["metric"] != METRIC_LABELS.get(row.get("metric_id"))
            or display["population"] != POPULATION_LABELS.get(row.get("population_id"))
            or display["period"] != row.get("period_id")
            or any(not isinstance(v, str) or not v for v in display.values())):
        raise ValueError("display metadata disagrees with accepted definitions")
    if row.get("unit") not in UNITS:
        raise ValueError("unsupported metric unit")
    if (row["unit"] == "MXN/month") != (row.get("price_basis") == "nominal"):
        raise ValueError("unit and price basis disagree")
    return row


def _precision_limit(rows: list[dict]) -> str:
    if any(row.get("synthetic") is True for row in rows):
        return "Ejemplo sintético; no es una medición oficial."
    if any(row["status"] == "REVIEW" or not row.get("precision", {}).get("official_precision") for row in rows):
        return "Estimación de revisión del proyecto; la precisión no está certificada oficialmente."
    return "Estimación descriptiva; el intervalo marginal no prueba diferencias entre grupos."


def _scope(row: dict, item: dict) -> str:
    d = item["display"]
    return (f"{d['field']} · {d['geography']} · {d['recorded_sex']} · {d['period']} · "
            f"{d['population']}")


def _extra_limit(rows: list[dict], comparison: dict | None) -> str:
    metric = rows[-1]["metric_id"]
    parts = [_precision_limit(rows)]
    if metric == "positive_income_mean":
        parts.append("Ingreso condicionado a ocupación e ingreso positivo de monto exacto conocido; pesos nominales, sin ajuste por inflación.")
    elif metric == "positive_income_coverage":
        parts.append("Cobertura entre personas ocupadas; los ingresos sin monto exacto permanecen fuera del numerador.")
    if comparison:
        if comparison["comparison_type"] in ("adjacent_quarter", "like_quarter_annual"):
            parts.append("Cambio descriptivo; las muestras trimestrales pueden solaparse y no se calculó precisión del cambio.")
        else:
            parts.append("Contraste descriptivo del mismo trimestre; no se calculó precisión de la diferencia entre grupos.")
        if "seasonality_qoq" in comparison.get("limitations", []):
            parts.append("Trimestres adyacentes: la estacionalidad puede influir.")
        if "unknown_edition_date" in comparison.get("limitations", []):
            parts.append("Fecha de edición exacta no disponible.")
    return " ".join(parts)


def make_claim(kind: str, subject_id: str, *, public_index: dict, comparison_ledger: dict) -> dict:
    """Build one claim from a supported record or passing descriptive comparison."""
    if kind not in KINDS:
        raise ValueError("unsupported claim kind")
    if kind == "observation":
        item = public_index.get(subject_id)
        row = _record(item)
        items, rows, comparison = [item], [row], None
    else:
        comparison = comparison_ledger.get(subject_id)
        if (not comparison or comparison.get("comparison_type") != KINDS[kind]
                or comparison.get("comparable") is not True or comparison.get("status") != "REVIEW"
                or comparison.get("reasons") or comparison.get("absolute_change") is None):
            raise ValueError("comparison cannot support a claim")
        ids = [comparison.get("previous_record_id"), comparison.get("current_record_id")]
        items = [public_index.get(record_id) for record_id in ids]
        rows = [_record(item) for item in items]
        if (comparison.get("source_snapshot_ids") != [r["source_snapshot_id"] for r in rows]
                or comparison.get("source_sha256s") != [i["snapshot_sha256"] for i in items]
                or comparison.get("evidence_refs") != sorted(set(sum((r["evidence_refs"] for r in rows), [])))
                or not math.isclose(comparison["absolute_change"], rows[1]["value"] - rows[0]["value"], rel_tol=1e-12, abs_tol=1e-12)):
            raise ValueError("comparison provenance or change disagrees with public endpoints")
    last, last_item = rows[-1], items[-1]
    scope = _scope(last, last_item)
    unit = UNITS[last["unit"]]
    title = f"{last_item['display']['metric']} · {last_item['display']['field']}"
    if comparison is None:
        observation = (f"En {scope}, el valor de «{last_item['display']['metric']}» fue "
                       f"{_number(last['value'])} {unit}.")
        interpretation = "Estimación descriptiva de la población y medida indicadas; el campo de estudio no identifica la ocupación ejercida."
        quantities = {"value": last["value"], "unit": last["unit"]}
    else:
        first, first_item = rows[0], items[0]
        delta_unit = "puntos porcentuales" if last["unit"] == "percent" else unit
        qualifier = {"qoq": "entre trimestres adyacentes", "yoy": "entre trimestres equivalentes de años consecutivos",
                     "sex": "entre sexos registrados del mismo trimestre", "entity": "entre entidades del mismo trimestre"}[kind]
        observation = (f"En {scope}, el valor de «{last_item['display']['metric']}» fue {_number(last['value'])} {unit}; "
                       f"el contraste descriptivo {qualifier} frente a {_scope(first, first_item)} fue "
                       f"{_number(comparison['absolute_change'])} {delta_unit}.")
        noun = "cambio" if kind in ("qoq", "yoy") else "contraste"
        interpretation = ("Los extremos usan la misma definición revisada; el " + noun
                          + " no establece efecto causal ni significancia estadística.")
        quantities = {"previous_value": first["value"], "current_value": last["value"],
                      "absolute_change": comparison["absolute_change"], "unit": last["unit"],
                      "display_unit": comparison["display_unit"]}
    return {"claim_id": "v2k:" + _digest([kind, subject_id]), "kind": kind,
            "subject_id": subject_id, "comparison_id": subject_id if comparison else None,
            "record_ids": [item["record_id"] for item in items], "grain": [list(item["grain"]) for item in items],
            "source_snapshot_ids": [row["source_snapshot_id"] for row in rows],
            "source_sha256s": [item["snapshot_sha256"] for item in items],
            "evidence_refs": sorted(set(sum((row["evidence_refs"] for row in rows), []))),
            "method_ids": [row["method_id"] for row in rows],
            "method_versions": [row["method_version"] for row in rows],
            "population_id": last["population_id"], "metric_id": last["metric_id"],
            "precision_statuses": [row["status"] for row in rows],
            "sample_sizes": [row.get("sample_size") for row in rows],
            "quantities": quantities, "title": title, "observation": observation,
            "interpretation": interpretation, "limitation": _extra_limit(rows, comparison),
            "synthetic": any(row.get("synthetic") is True for row in rows)}


def validate_claim(claim: dict, *, public_index: dict, comparison_ledger: dict) -> list[dict]:
    """Regenerate every field; exact equality rejects altered prose and quantities."""
    try:
        if not isinstance(claim, dict):
            raise ValueError("claim must be an object")
        expected = make_claim(claim.get("kind"), claim.get("subject_id"),
                              public_index=public_index, comparison_ledger=comparison_ledger)
        if claim != expected:
            raise ValueError("claim differs from canonical public evidence")
    except (ValueError, TypeError, KeyError, AttributeError) as exc:
        return [{"id": "canonical_claim", "message": str(exc)}]
    return []


def select_opening_claims(candidates: list[dict], *, limit: int = 3) -> list[dict]:
    """Pick at most three distinct supported themes without ranking outcome values."""
    if type(limit) is not int or not 0 <= limit <= 3:
        raise ValueError("opening claim limit must be 0..3")
    if not isinstance(candidates, list):
        raise ValueError("candidate claims must be a list")
    priorities = {"positive_income_coverage": 0, "employment_rate": 1,
                  "positive_income_mean": 2, "main_job_informality_rate": 3}
    ordered = sorted(candidates, key=lambda claim: (priorities.get(claim.get("metric_id"), 9),
                                                    0 if claim.get("kind") == "observation" else 1,
                                                    claim.get("subject_id", str(claim.get("record_ids", []))),
                                                    claim.get("claim_id", "")))
    chosen, themes = [], set()
    for claim in ordered:
        if not isinstance(claim, dict) or not claim.get("claim_id") or not claim.get("record_ids"):
            continue
        theme = claim.get("metric_id")
        if theme in themes or claim.get("coverage_n", min((x for x in claim.get("sample_sizes", [])
                                                          if type(x) is int), default=0)) < 30:
            continue
        chosen.append(claim)
        themes.add(theme)
        if len(chosen) == limit:
            break
    return chosen[:limit]
