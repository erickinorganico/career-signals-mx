"""Synthetic v2 records exercise strict references and public suppression."""

import copy
import json

import pytest

from brujula.research_contract import validate_research_v2, validate_public_research_v2, public_research_projection
from brujula.resources import contract_path


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
                                   "ci90_upper": 125.0, "method": "taylor_linearized", "ci_method": "normal_wald_90", "level": 0.90,
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


def test_rounding_unit_and_singleton_claims_fail_closed():
    fixture = research_fixture()
    fixture["records"][0]["value"] = 119.9
    assert "value_estimate" in failures(fixture)
    fixture = research_fixture()
    fixture["metrics"][0]["price_basis"] = "nominal"
    fixture["records"][0]["price_basis"] = "nominal"
    assert "unit_price_basis" in failures(fixture)
    fixture = research_fixture()
    fixture["records"][0]["precision"].update(singleton_policy="adjust", official_precision=True)
    assert "singleton_precision" in failures(fixture)
    fixture = research_fixture()
    fixture["metrics"][0]["unit"] = "percent"
    fixture["records"][0].update(unit="percent", value=120.0)
    assert "value_range" in failures(fixture)


@pytest.mark.parametrize("change", [
    lambda r: r.update(sample_size=29),
    lambda r: r["support"].update(n_psu_domain=1, n_strata_domain=1),
    lambda r: r.update(weighted_denominator=0),
    lambda r: r["precision"].update(standard_error=0),
    lambda r: r["precision"].update(coefficient_variation=30),
    lambda r: r["precision"].update(ci90_upper=None),
])
def test_unsupported_visible_values_fail_precision_gate(change):
    fixture = research_fixture()
    change(fixture["records"][0])
    assert "precision_gate" in failures(fixture)


def test_review_value_allows_cv_20_or_project_singleton_but_measured_does_not():
    fixture = research_fixture()
    record = fixture["records"][0]
    record["precision"]["coefficient_variation"] = 20
    assert validate_research_v2(fixture) == []
    record.update(status="MEASURED", reason=None, synthetic=False)
    assert "precision_grade" in failures(fixture)
    record.update(status="REVIEW", reason="Project singleton adjustment")
    record["precision"].update(singleton_policy="adjust", official_precision=False)
    assert validate_research_v2(fixture) == []


def test_suppressed_projection_never_leaks_value_equivalent_sentinels():
    fixture = research_fixture()
    record = fixture["records"][0]
    record.update(status="BLOCKED", reason="precision", value=None, estimate=123456.789,
                  weighted_denominator=123456.789)
    record["support"]["weighted_support_total"] = 123456.789
    record["precision"].update(standard_error=987654.321, ci90_lower=100000.0,
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


def test_distinct_packaged_public_schema_and_hours_unit():
    internal = json.loads(contract_path("research-v2.schema.json").read_text(encoding="utf-8"))
    public_schema = json.loads(contract_path("research-v2-public.schema.json").read_text(encoding="utf-8"))
    assert internal["$id"] != public_schema["$id"]
    assert "estimate" in internal["$defs"]["record"]["required"]
    assert "estimate" not in public_schema["$defs"]["record"]["properties"]
    fixture = research_fixture()
    fixture["metrics"][0].update(unit="hours/week", price_basis="not_applicable")
    fixture["records"][0].update(unit="hours/week", price_basis="not_applicable")
    assert validate_research_v2(fixture) == []
    assert validate_public_research_v2(public_research_projection(fixture)) == []


def test_suppressed_public_schema_rejects_nested_interval_and_weighted_total():
    fixture = research_fixture()
    fixture["records"][0].update(status="UNKNOWN", reason="unsupported", value=None)
    public = public_research_projection(fixture)
    leaked = copy.deepcopy(public)
    leaked["records"][0]["support"]["weighted_support_total"] = 120.0
    assert validate_public_research_v2(leaked)
    leaked = copy.deepcopy(public)
    leaked["records"][0]["precision"]["ci90_upper"] = 125.0
    assert validate_public_research_v2(leaked)
    leaked = copy.deepcopy(public)
    leaked["records"][0]["precision"]["standard_error"] = float("inf")
    assert validate_public_research_v2(leaked)
