"""Typed Spanish claims over sanitized public aggregate records."""

from copy import deepcopy
import hashlib
import json

import pytest

from brujula.claims_v2 import (METRIC_LABELS, POPULATION_LABELS, make_claim,
                               select_opening_claims, validate_claim)


def _item(field="031300", unit="percent", value=48.25):
    row = {"source_snapshot_id": "enoe_2026_q2", "population_id": "completed_professional_known_age",
           "field_of_study_id": field, "occupation_id": "all", "industry_id": "all",
           "geography_id": "mx", "recorded_sex_id": "all", "period_id": "2026-Q2",
           "metric_id": "employment_rate", "method_id": "enoe_taylor_project_adjust",
           "method_version": "method:v1", "unit": unit, "price_basis": "not_applicable",
           "value": value, "status": "REVIEW", "reason": "project_singleton_adjustment",
           "sample_size": 40, "evidence_refs": ["enoe_2026_q2_custody"], "synthetic": True,
           "precision": {"coefficient_variation": 12.0, "official_precision": False,
                         "ci90_lower": 40.0, "ci90_upper": 55.0}}
    grain = tuple(row[k] for k in ("source_snapshot_id", "population_id", "field_of_study_id",
              "occupation_id", "industry_id", "geography_id", "recorded_sex_id", "period_id",
              "metric_id", "method_id"))
    rid = "v2r:" + hashlib.sha256(json.dumps(list(grain), ensure_ascii=False, sort_keys=True,
                                              separators=(",", ":")).encode()).hexdigest()
    return {"record_id": rid, "grain": grain, "record": row,
            "snapshot_sha256": "a" * 64, "method_version": "method:v1",
            "display": {"field": "Ciencias políticas" if field == "031300" else "Comunicación y periodismo",
                        "population": POPULATION_LABELS["completed_professional_known_age"],
                        "metric": METRIC_LABELS["employment_rate"], "geography": "México",
                        "recorded_sex": "todos los sexos registrados", "period": "2026-Q2"}}


def _changed(item, **updates):
    changed = deepcopy(item)
    changed["record"].update(updates)
    grain_keys = ("source_snapshot_id", "population_id", "field_of_study_id", "occupation_id",
                  "industry_id", "geography_id", "recorded_sex_id", "period_id", "metric_id", "method_id")
    grain = tuple(changed["record"][key] for key in grain_keys)
    changed["grain"] = grain
    changed["record_id"] = "v2r:" + hashlib.sha256(json.dumps(list(grain), sort_keys=True,
                                      ensure_ascii=False, separators=(",", ":")).encode()).hexdigest()
    changed["display"]["period"] = changed["record"]["period_id"]
    if changed["record"]["geography_id"] == "02":
        changed["display"]["geography"] = "Baja California"
    elif changed["record"]["geography_id"] == "01":
        changed["display"]["geography"] = "Aguascalientes"
    changed["display"]["recorded_sex"] = {"all": "todos los sexos registrados",
                                              "1": "hombres registrados", "2": "mujeres registradas"}[
                                                  changed["record"]["recorded_sex_id"]]
    return changed


def test_observation_has_exact_evidence_and_canonical_spanish():
    item = _item()
    index = {item["record_id"]: item}
    claim = make_claim("observation", item["record_id"], public_index=index, comparison_ledger={})
    assert validate_claim(claim, public_index=index, comparison_ledger={}) == []
    assert "Ciencias políticas" in claim["observation"] and "48,25" in claim["observation"]
    assert claim["record_ids"] == [item["record_id"]]
    assert claim["source_snapshot_ids"] == ["enoe_2026_q2"]
    assert claim["source_sha256s"] == ["a" * 64]
    for field, replacement in (("observation", "causa 7 empleos"),
                               ("title", "ocupación en la profesión de Ciencias políticas"),
                               ("limitation", "estadísticamente significativo")):
        altered = deepcopy(claim)
        altered[field] = replacement
        assert validate_claim(altered, public_index=index, comparison_ledger={})


def test_equal_values_from_different_fields_are_not_interchangeable():
    first, second = _item(), _item("032100")
    index = {x["record_id"]: x for x in (first, second)}
    claim = make_claim("observation", first["record_id"], public_index=index, comparison_ledger={})
    altered = deepcopy(claim)
    altered["record_ids"] = [second["record_id"]]
    assert validate_claim(altered, public_index=index, comparison_ledger={})
    altered = deepcopy(claim)
    altered["title"] = altered["title"].replace("Ciencias", "Cienciаs")  # Cyrillic lookalike
    assert validate_claim(altered, public_index=index, comparison_ledger={})


def test_suppressed_record_and_boundary_selection():
    item = _item()
    item["record"]["value"] = None
    with pytest.raises(ValueError):
        make_claim("observation", item["record_id"], public_index={item["record_id"]: item}, comparison_ledger={})
    assert select_opening_claims([]) == []
    candidates = [{"claim_id": f"v2k:{i}", "kind": "observation",
                   "metric_id": ["employment_rate", "positive_income_coverage", "positive_income_mean", "main_job_informality_rate"][i],
                   "record_ids": [str(i)], "coverage_n": 40} for i in range(4)]
    assert len(select_opening_claims(candidates[:3])) == 3
    with pytest.raises(ValueError):
        select_opening_claims(candidates, limit=4)


def test_descriptive_comparison_requires_supported_pair():
    a, b = _item(), _item("032100")
    index = {x["record_id"]: x for x in (a, b)}
    comparison = {"comparison_id": "v2c:pair", "comparison_type": "entity_slice",
                  "previous_record_id": a["record_id"], "current_record_id": b["record_id"],
                  "comparable": False, "status": "BLOCKED", "absolute_change": None,
                  "relative_change_pct": None, "reasons": ["field_of_study_id"],
                  "limitations": ["descriptive_change_only"], "evidence_refs": a["record"]["evidence_refs"],
                  "source_snapshot_ids": ["enoe_2026_q2", "enoe_2026_q2"],
                  "source_sha256s": ["a" * 64, "a" * 64], "display_unit": "percentage points"}
    with pytest.raises(ValueError):
        make_claim("entity", "v2c:pair", public_index=index,
                   comparison_ledger={"v2c:pair": comparison})


@pytest.mark.parametrize("kind,comparison_type,left_changes,right_changes", [
    ("qoq", "adjacent_quarter", {"period_id": "2026-Q1", "source_snapshot_id": "enoe_2026_q1"}, {}),
    ("yoy", "like_quarter_annual", {"period_id": "2025-Q2", "source_snapshot_id": "enoe_2025_q2"}, {}),
    ("sex", "recorded_sex_slice", {"recorded_sex_id": "1"}, {"recorded_sex_id": "2"}),
    ("entity", "entity_slice", {"geography_id": "02"}, {"geography_id": "01"}),
])
def test_supported_descriptive_templates_and_exact_metadata(kind, comparison_type, left_changes, right_changes):
    base = _item()
    left = _changed(base, value=40.0, **left_changes)
    right = _changed(base, value=48.25, **right_changes)
    index = {x["record_id"]: x for x in (left, right)}
    comparison = {"comparison_id": "v2c:pair", "comparison_type": comparison_type,
                  "previous_record_id": left["record_id"], "current_record_id": right["record_id"],
                  "comparable": True, "status": "REVIEW", "absolute_change": 8.25,
                  "relative_change_pct": 20.625, "reasons": [],
                  "limitations": (["descriptive_change_only", "quarterly_samples_may_overlap",
                                   "seasonality_qoq" if kind == "qoq" else "like_quarter_yoy"]
                                  if kind in ("qoq", "yoy") else
                                  ["descriptive_difference_only", "same_period_descriptive_slice"]),
                  "evidence_refs": sorted(set(left["record"]["evidence_refs"] + right["record"]["evidence_refs"])),
                  "source_snapshot_ids": [left["record"]["source_snapshot_id"], right["record"]["source_snapshot_id"]],
                  "source_sha256s": [left["snapshot_sha256"], right["snapshot_sha256"]],
                  "display_unit": "percentage points"}
    ledger = {"v2c:pair": comparison}
    claim = make_claim(kind, "v2c:pair", public_index=index, comparison_ledger=ledger)
    assert validate_claim(claim, public_index=index, comparison_ledger=ledger) == []
    assert ("el cambio" in claim["interpretation"]) == (kind in ("qoq", "yoy"))
    assert ("el contraste" in claim["interpretation"]) == (kind in ("sex", "entity"))
    assert ("muestras trimestrales pueden solaparse" in claim["limitation"]) == (kind in ("qoq", "yoy"))
    assert ("diferencia entre grupos" in claim["limitation"]) == (kind in ("sex", "entity"))
    assert "no establece efecto causal" in claim["interpretation"]
    assert "código 97: 97 años o más" in claim["observation"]
    for field in ("source_snapshot_ids", "source_sha256s", "method_versions", "evidence_refs", "quantities"):
        changed = deepcopy(claim)
        changed[field] = [] if field != "quantities" else {"absolute_change": 999}
        assert validate_claim(changed, public_index=index, comparison_ledger=ledger)


def test_opening_selection_is_stable_under_reorder_and_uses_distinct_themes():
    candidates = [{"claim_id": f"v2k:{i}", "kind": "observation", "subject_id": f"v2r:{i}",
                   "metric_id": metric, "record_ids": [f"v2r:{i}"], "sample_sizes": [40]}
                  for i, metric in enumerate(("employment_rate", "positive_income_coverage",
                                              "positive_income_mean", "main_job_informality_rate"))]
    chosen = select_opening_claims(candidates)
    assert [x["claim_id"] for x in chosen] == [x["claim_id"] for x in select_opening_claims(list(reversed(candidates)))]
    assert [x["metric_id"] for x in chosen] == ["positive_income_coverage", "employment_rate", "positive_income_mean"]


def test_income_and_plural_metric_use_neutral_grammar_and_nominal_caveat():
    income = _changed(_item(), metric_id="positive_income_mean", unit="MXN/month",
                      price_basis="nominal", value=12450.5)
    income["display"]["metric"] = METRIC_LABELS["positive_income_mean"]
    claim = make_claim("observation", income["record_id"],
                       public_index={income["record_id"]: income}, comparison_ledger={})
    assert "el valor de «ingreso mensual medio positivo conocido» fue" in claim["observation"]
    assert "MXN mensuales nominales" in claim["observation"]
    assert "condicionado a ocupación e ingreso positivo" in claim["limitation"]
    assert validate_claim(claim, public_index={income["record_id"]: income}, comparison_ledger={}) == []
    people = _changed(_item(), metric_id="occupied_total", unit="people", value=12450.5)
    people["display"]["metric"] = METRIC_LABELS["occupied_total"]
    claim = make_claim("observation", people["record_id"],
                       public_index={people["record_id"]: people}, comparison_ledger={})
    assert "el valor de «personas ocupadas estimadas» fue" in claim["observation"]
    assert "código 98: edad operativamente desconocida" in POPULATION_LABELS["national_15_plus_context"]
