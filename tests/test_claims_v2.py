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
