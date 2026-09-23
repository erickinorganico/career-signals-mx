"""Synthetic v2 records exercise strict references and public suppression."""

import copy
import json

import pytest

from brujula.research_contract import validate_research_v2, validate_public_research_v2, public_research_projection


def research_fixture():
    """Complete synthetic fixture; its values are never official findings."""
    return {
        "schema_version": "2.0",
        "sources": [{"id": "enoe_2025_q2", "period_id": "2025-Q2", "url": "https://www.inegi.org.mx/synthetic.zip",
                     "sha256": "a" * 64, "terms_url": "https://www.inegi.org.mx/inegi/terminos.html",
                     "authority": "INEGI", "acquired_at": "2026-09-22T00:00:00Z"}],
        "populations": [{"id": "completed_professional_known_age"}],
        "fields_of_study": [{"id": "033100", "label": "Derecho"}, {"id": "all", "label": "Todos"}, {"id": "unknown", "label": "Desconocido"}],
        "occupations": [{"id": "all", "label": "Todas"}, {"id": "unknown", "label": "Desconocida"}],
        "industries": [{"id": "all", "label": "Todas"}, {"id": "unknown", "label": "Desconocida"}],
        "geographies": [{"id": "mx", "label": "México"}, {"id": "unknown", "label": "Desconocida"}],
        "recorded_sexes": [{"id": "all", "label": "Todas"}, {"id": "unknown", "label": "Desconocido"}],
        "periods": [{"id": "2025-Q2", "label": "2025 segundo trimestre", "start": "2025-04-01", "end": "2025-06-30"},
                    {"id": "2025-Q3", "label": "2025 tercer trimestre", "start": "2025-07-01", "end": "2025-09-30"}],
        "metrics": [{"id": "occupied_people", "label": "Personas ocupadas", "unit": "people", "price_basis": "not_applicable"}],
        "methods": [{"id": "taylor_v1", "design_id": "enoe_strata_upm", "version": "1.0",
                     "source_snapshot_ids": ["enoe_2025_q2"]}],
        "evidence": [{"id": "source_receipt", "source_snapshot_id": "enoe_2025_q2", "label": "Recibo sintético",
                      "url": "https://www.inegi.org.mx/synthetic.zip", "kind": "receipt"}],
        "records": [{"source_snapshot_id": "enoe_2025_q2", "population_id": "completed_professional_known_age",
                     "field_of_study_id": "033100", "occupation_id": "all", "industry_id": "all", "geography_id": "mx",
                     "recorded_sex_id": "all", "period_id": "2025-Q2", "metric_id": "occupied_people", "method_id": "taylor_v1",
                     "unit": "people", "price_basis": "not_applicable", "method_version": "1.0", "design_id": "enoe_strata_upm",
                     "sample_size": 40, "weighted_denominator": 120.0,
                     "support": {"n_psu_design": 16, "n_strata_design": 8, "n_psu_domain": 10, "n_strata_domain": 6,
                                 "design_df": 8, "weighted_support_total": 120.0},
                     "precision": {"standard_error": 3.0, "coefficient_variation": 2.5, "ci90_lower": 115.0,
                                   "ci90_upper": 125.0, "method": "taylor_linearized", "level": 0.90,
                                   "singleton_policy": "fail", "official_precision": False},
                     "status": "REVIEW", "reason": "Synthetic fixture", "estimate": 120.0, "value": 120.0,
                     "evidence_refs": ["source_receipt"], "synthetic": True}],
    }


def failures(payload):
    return {item["id"] for item in validate_research_v2(payload)}


def test_complete_v2_fixture_and_input_order_independence():
    fixture = research_fixture()
    assert validate_research_v2(fixture) == []
    reordered = copy.deepcopy(fixture)
    reordered["fields_of_study"].reverse()
    reordered["periods"].reverse()
    assert validate_research_v2(reordered) == []


@pytest.mark.parametrize("change", [
    lambda p: p["records"][0].update(rogue=True),
    lambda p: p["records"][0].pop("estimate"),
    lambda p: p["records"][0].update(estimate=float("nan")),
    lambda p: p["records"][0].update(sample_size=-1),
    lambda p: p["records"][0].update(value=None, reason=None),
    lambda p: p["records"][0].update(field_of_study_id="missing"),
    lambda p: p["records"][0].update(evidence_refs=[]),
    lambda p: p["records"].append(copy.deepcopy(p["records"][0])),
    lambda p: p["populations"].append({"id": "unsupported_population"}),
    lambda p: p["evidence"].append(copy.deepcopy(p["evidence"][0])),
    lambda p: p["records"][0].update(method_version="other"),
    lambda p: p["records"][0].update(period_id="2025-Q3"),
])
def test_internal_rejects_invalid_or_orphan_records(change):
    fixture = research_fixture()
    change(fixture)
    assert failures(fixture)


def test_adjacent_periods_are_valid_but_overlapping_periods_are_not():
    fixture = research_fixture()
    assert validate_research_v2(fixture) == []
    fixture["periods"][1]["start"] = "2025-06-30"
    assert "period_overlap" in failures(fixture)


def test_empty_catalog_and_blank_ids_fail():
    fixture = research_fixture()
    fixture["metrics"] = []
    assert failures(fixture)
    fixture = research_fixture()
    fixture["sources"][0]["id"] = " "
    assert failures(fixture)


def test_suppressed_projection_never_leaks_value_equivalent_sentinels():
    fixture = research_fixture()
    record = fixture["records"][0]
    record.update(status="BLOCKED", reason="precision", value=None, estimate=123456.789,
                  weighted_denominator=123456.789)
    record["support"]["weighted_support_total"] = 123456.789
    record["precision"].update(standard_error=987654.321, ci90_lower=987654.321,
                               ci90_upper=987654.321, coefficient_variation=987654.321)
    public = public_research_projection(fixture)
    assert validate_public_research_v2(public) == []
    serial = json.dumps(public, sort_keys=True)
    assert "123456.789" not in serial and "987654.321" not in serial
    projected = public["records"][0]
    assert "estimate" not in projected and projected["value"] is None
    assert projected["weighted_denominator"] is None
    assert projected["support"]["n_psu_domain"] == 10
    assert projected["support"]["n_strata_domain"] == 6
    assert projected["sample_size"] == 40
    assert projected["precision"]["level"] == 0.90


def test_supported_review_and_measured_value_remain_visible():
    fixture = research_fixture()
    review = public_research_projection(fixture)["records"][0]
    assert review["status"] == "REVIEW" and review["value"] == 120.0
    assert "estimate" not in review
    record = fixture["records"][0]
    record.update(status="MEASURED", reason=None, synthetic=False)
    assert public_research_projection(fixture)["records"][0]["value"] == 120.0


def test_public_rejects_diagnostic_and_suppression_leaks():
    public = public_research_projection(research_fixture())
    leaked = copy.deepcopy(public)
    leaked["records"][0]["estimate"] = 120
    assert validate_public_research_v2(leaked)
    leaked = copy.deepcopy(public)
    leaked["records"][0].update(status="BLOCKED", reason="precision", value=None, weighted_denominator=120)
    assert validate_public_research_v2(leaked)
    leaked = copy.deepcopy(public)
    leaked["records"][0]["field_of_study_id"] = "missing"
    assert validate_public_research_v2(leaked)
