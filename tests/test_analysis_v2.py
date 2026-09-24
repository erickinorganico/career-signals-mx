"""Synthetic aggregate controls and an offline accepted-public integration gate."""

from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest

from brujula import analysis_v2
from brujula.estimates import FOCAL_FIELDS, METHOD_ID
from brujula.populations import COMPLETED_PROFESSIONAL_KNOWN_AGE, NATIONAL_15_PLUS_CONTEXT
from brujula.research_contract import GRAIN, validate_public_research_v2
from brujula.source_inventory import PERIODS


ROOT = Path(__file__).resolve().parents[1]
GOLDEN = json.loads((ROOT / "data/fixtures/analysis-v2-golden.json").read_text(encoding="utf-8"))


def synthetic_inputs(monkeypatch, *, complementary=False):
    """Generate small but complete Phase 3 synthetic public roots and audits."""
    monkeypatch.setattr(analysis_v2, "load_metric_manifest", lambda: {
        "content_sha256": GOLDEN["metric_manifest_sha256"],
        "metrics": [{"id": GOLDEN["metric_id"]}],
    })
    monkeypatch.setattr(analysis_v2, "_required_code_files",
                        lambda: frozenset({"brujula/research_contract.py"}))
    fields = GOLDEN["named_fields"]
    source_hash = GOLDEN["source_sha256"]
    manifest = {"status": "PASS", "numeric_content_digest": None,
                "metric_manifest_sha256": GOLDEN["metric_manifest_sha256"],
                "code_sha256": {"brujula/research_contract.py": analysis_v2.hashlib.sha256(
                    (ROOT / "brujula/research_contract.py").read_bytes().replace(b"\r\n", b"\n")).hexdigest()},
                "snapshots": {}}
    publics, audits, approved_pins = {}, {}, {}
    for period in PERIODS:
        snapshot = analysis_v2._snapshot(period)
        year, quarter = period.split("-Q")
        first_month = (int(quarter) - 1) * 3 + 1
        final_month = first_month + 2
        import calendar
        period_row = {"id": period, "label": period,
                      "start": f"{year}-{first_month:02d}-01",
                      "end": f"{year}-{final_month:02d}-{calendar.monthrange(int(year), final_month)[1]:02d}"}
        domains = {(NATIONAL_15_PLUS_CONTEXT, "all", "mx", "all"),
                   (COMPLETED_PROFESSIONAL_KNOWN_AGE, "all", "mx", "all")}
        domains.update((COMPLETED_PROFESSIONAL_KNOWN_AGE, field, "mx", "all") for field in FOCAL_FIELDS)
        if period == PERIODS[-1]:
            domains.update((COMPLETED_PROFESSIONAL_KNOWN_AGE, field, state, "all")
                           for field in ("all", *FOCAL_FIELDS) for state in analysis_v2.STATE_CODES)
            domains.update((COMPLETED_PROFESSIONAL_KNOWN_AGE, field, "mx", sex)
                           for field in ("all", *FOCAL_FIELDS) for sex in analysis_v2.SEX_CODES)
        source = {"id": snapshot, "period_id": period, "url": "https://www.inegi.org.mx/synthetic.zip",
                  "sha256": source_hash, "terms_url": "https://www.inegi.org.mx/inegi/terminos.html",
                  "authority": "INEGI", "acquired_at": "2026-09-23T00:00:00Z"}
        method_version = "synthetic-method:" + GOLDEN["metric_manifest_sha256"]
        records, requested, evaluated, population_coverage = [], {}, {}, {}
        for population, field, geography, sex in sorted(domains):
            key = "|".join((population, field, geography, sex))
            population_coverage[key] = {"counts_nonexclusive": True,
                                        "responding_resident_n": 100, "population_eligible_n": 30,
                                        "observed_category_counts": {"unknown_field": 3},
                                        "exclusions": {"age_unknown": 2, "unknown_field": 3,
                                                       "technical_education": 4,
                                                       "postgraduate_education": 5,
                                                       "incomplete_education": 6}}
            row = {"source_snapshot_id": snapshot, "population_id": population,
                   "field_of_study_id": field, "occupation_id": "all", "industry_id": "all",
                   "geography_id": geography, "recorded_sex_id": sex,
                   "period_id": period, "metric_id": GOLDEN["metric_id"], "method_id": METHOD_ID,
                   "unit": "people", "price_basis": "not_applicable", "method_version": method_version,
                   "design_id": "synthetic_design", "sample_size": 0, "weighted_denominator": None,
                   "support": {"n_psu_design": 4, "n_strata_design": 2, "n_psu_domain": 0,
                               "n_strata_domain": 0, "design_df": 2, "weighted_support_total": None},
                   "precision": {"standard_error": None, "coefficient_variation": None,
                                 "ci90_lower": None, "ci90_upper": None,
                                 "method": "synthetic_taylor", "ci_method": "normal_wald_90", "level": 0.9,
                                 "singleton_policy": "fail", "official_precision": False},
                   "status": "UNKNOWN", "reason": "unknown", "value": None,
                   "evidence_refs": [snapshot + "_custody"], "synthetic": True}
            if (complementary and period == PERIODS[-1]
                    and population == COMPLETED_PROFESSIONAL_KNOWN_AGE
                    and field == "033100" and sex == "all"
                    and geography in {"mx", *analysis_v2.STATE_CODES[1:]}):
                value = 3100.0 if geography == "mx" else 100.0
                row.update(status="REVIEW", reason="synthetic_fixture", value=value,
                           sample_size=40, weighted_denominator=value)
                row["support"].update(n_psu_domain=4, n_strata_domain=2,
                                      weighted_support_total=value)
                row["precision"].update(standard_error=value * 0.05,
                                        coefficient_variation=5.0,
                                        ci90_lower=value * 0.9, ci90_upper=value * 1.1)
            records.append(row)
            grain = analysis_v2._ledger_key(tuple(row[key] for key in GRAIN))
            requested[grain] = True
            visible = row["value"] is not None
            evaluated[grain] = {"status": row["status"], "has_estimate": visible,
                                "reason": "Synthetic fixture" if visible else "sample_size_below_30",
                                "coverage": {"domain_n": row["sample_size"],
                                             "eligible_n": row["sample_size"],
                                             "reason": None if visible else "empty"},
                                "exclusions": {"income_amount_unknown": 0},
                                "method_version": method_version,
                                "metric_version": "synthetic:" + GOLDEN["metric_manifest_sha256"],
                                "dictionary_binding": "synthetic", "synthetic": True}
        public = {"schema_version": "2.0", "sources": [source],
                  "populations": [{"id": NATIONAL_15_PLUS_CONTEXT},
                                  {"id": COMPLETED_PROFESSIONAL_KNOWN_AGE}],
                  "fields_of_study": [{"id": "all", "label": "Todos los campos"}]
                                     + [{"id": code, "label": label} for code, label in sorted(fields.items())],
                  "occupations": [{"id": "all", "label": "Todas"}],
                  "industries": [{"id": "all", "label": "Todas"}],
                  "geographies": [{"id": "mx", "label": "México"}]
                                 + [{"id": code, "label": code} for code in analysis_v2.STATE_CODES],
                  "recorded_sexes": [{"id": code, "label": code} for code in ("all", *analysis_v2.SEX_CODES)],
                  "periods": [period_row],
                  "metrics": [{"id": GOLDEN["metric_id"], "label": "Población total",
                               "unit": "people", "price_basis": "not_applicable"}],
                  "methods": [{"id": METHOD_ID, "design_id": "synthetic_design",
                               "version": method_version, "source_snapshot_ids": [snapshot]}],
                  "evidence": [{"id": snapshot + "_custody", "source_snapshot_id": snapshot,
                                "label": "Recibo sintético", "url": source["url"], "kind": "source_receipt"}],
                  "records": records}
        assert validate_public_research_v2(public) == []
        audit = {"snapshot_id": snapshot, "period": period, "source_sha256": source_hash,
                 "method_version": method_version, "requested_cells": requested,
                 "evaluated_cells": evaluated, "population_coverage": population_coverage,
                 "request_comparison": {"status": "PASS"},
                 "numeric_digest": analysis_v2._digest(records),
                 "public_records": copy.deepcopy(records),
                 "public_content_sha256": analysis_v2._content_digest(public)}
        manifest["snapshots"][snapshot] = {"public_v2_digest": analysis_v2._digest(public),
                                            "public_content_sha256": audit["public_content_sha256"],
                                            "numeric_digest": audit["numeric_digest"],
                                            "requested_count": len(records)}
        publics[snapshot] = public
        audits[snapshot] = audit
        approved_pins[snapshot] = audit["public_content_sha256"]
    manifest["numeric_content_digest"] = analysis_v2._digest({
        snapshot: audit["numeric_digest"] for snapshot, audit in audits.items()})
    monkeypatch.setattr(analysis_v2, "_approved_sources", lambda: {
        snapshot: {"sha256": source_hash, "url": public["sources"][0]["url"]}
        for snapshot, public in publics.items()})
    monkeypatch.setattr(analysis_v2, "_approved_public_pins", lambda: approved_pins)
    approved_coverage = {snapshot: analysis_v2._coverage_digest(audit)
                         for snapshot, audit in audits.items()}
    monkeypatch.setattr(analysis_v2, "_approved_coverage_pins", lambda: approved_coverage)
    return publics, {"manifest": manifest, "audits": audits}


def test_synthetic_complete_grid_and_canonical_ids(monkeypatch):
    publics, acceptance = synthetic_inputs(monkeypatch)
    index = analysis_v2.index_public_estimates(publics, acceptance)
    packet = analysis_v2.build_profiles(index, acceptance["audits"], latest_period_id=PERIODS[-1])
    assert packet["synthetic"] is True
    assert len(packet["national"]) == len(PERIODS) * 5
    assert len(packet["latest_fields"]) == len(GOLDEN["named_fields"])
    assert len(packet["latest_states"]) == 4 * 32
    assert len(packet["latest_recorded_sexes"]) == 4 * 2
    assert {cell["geography_id"] for cell in packet["latest_states"]} == set(analysis_v2.STATE_CODES)
    assert {cell["recorded_sex_id"] for cell in packet["latest_recorded_sexes"]} == {"1", "2"}
    assert all(cell["value"] is None and cell["reason"] == "unknown" for cell in packet["latest_states"])
    assert all(cell["coverage"]["counts_nonexclusive"] is True for cell in packet["national"])
    assert packet["national"][0]["coverage"]["metric_exclusions"] == {"income_amount_unknown": 0}
    assert packet["national"][0]["coverage"]["denominator_keys"]["metric_eligible_n"] == "eligible_n"
    reordered = copy.deepcopy(publics)
    for root in reordered.values():
        root["records"].reverse()
        root["fields_of_study"].reverse()
    for snapshot, root in reordered.items():
        acceptance["manifest"]["snapshots"][snapshot]["public_v2_digest"] = analysis_v2._digest(root)
        acceptance["manifest"]["snapshots"][snapshot]["numeric_digest"] = analysis_v2._digest(root["records"])
        acceptance["audits"][snapshot]["numeric_digest"] = analysis_v2._digest(root["records"])
        acceptance["audits"][snapshot]["public_records"] = copy.deepcopy(root["records"])
    acceptance["manifest"]["numeric_content_digest"] = analysis_v2._digest({
        snapshot: audit["numeric_digest"] for snapshot, audit in acceptance["audits"].items()})
    again = analysis_v2.index_public_estimates(reordered, acceptance)
    assert [entry["record_id"] for entry in index["records"]] == [entry["record_id"] for entry in again["records"]]


def test_missing_computation_blocks_instead_of_becoming_sparse(monkeypatch):
    publics, acceptance = synthetic_inputs(monkeypatch)
    snap = analysis_v2._snapshot(PERIODS[-1])
    key = next(iter(acceptance["audits"][snap]["evaluated_cells"]))
    del acceptance["audits"][snap]["evaluated_cells"][key]
    with pytest.raises(ValueError, match="requested, evaluated"):
        analysis_v2.index_public_estimates(publics, acceptance)


def test_changed_public_hash_blocks(monkeypatch):
    publics, acceptance = synthetic_inputs(monkeypatch)
    snap = analysis_v2._snapshot(PERIODS[-1])
    publics[snap]["fields_of_study"][0]["label"] = "Altered"
    with pytest.raises(ValueError, match="accepted hash"):
        analysis_v2.index_public_estimates(publics, acceptance)


def test_evaluated_reason_cannot_disagree_with_suppressed_public_row(monkeypatch):
    publics, acceptance = synthetic_inputs(monkeypatch)
    snap = analysis_v2._snapshot(PERIODS[-1])
    key = next(iter(acceptance["audits"][snap]["evaluated_cells"]))
    acceptance["audits"][snap]["evaluated_cells"][key]["reason"] = "different computed reason"
    with pytest.raises(ValueError, match="evaluated cell disagrees"):
        analysis_v2.index_public_estimates(publics, acceptance)


def test_observed_exact_income_response_has_explicit_denominator_and_empty_state():
    assert analysis_v2._observed_response(0, 0) == {
        "responding_n": 0, "denominator_n": 0, "observed_percent": None,
        "reason": "empty_denominator", "denominator_key": "occupied_eligible_n",
    }
    assert analysis_v2._observed_response(5, 10)["observed_percent"] == 50.0
    assert analysis_v2._observed_response(10, 10)["observed_percent"] == 100.0
    with pytest.raises(ValueError, match="response count"):
        analysis_v2._observed_response(11, 10)


def test_complementary_parent_cannot_reveal_one_suppressed_state():
    parent = {"value": 900.0, "status": "REVIEW", "reason": "project_singleton_adjustment",
              "weighted_denominator_estimate": 900.0,
              "support": {"weighted_support_total": 900.0},
              "precision": {"standard_error": 9.0, "coefficient_variation": 1.0,
                            "ci90_lower": 880.0, "ci90_upper": 920.0}}
    parts = [{"value": float(i)} for i in range(31)] + [{"value": None}]
    analysis_v2._redact_parent_if_complementary(parent, parts)
    assert parent["value"] is None
    assert parent["reason"] == "complementary_suppression"
    assert parent["weighted_denominator_estimate"] is None
    assert parent["support"]["weighted_support_total"] is None
    assert all(parent["precision"][key] is None for key in analysis_v2.SUPPRESSED_PRECISION)


def test_profile_redaction_flows_to_downstream_record_index(monkeypatch):
    publics, acceptance = synthetic_inputs(monkeypatch, complementary=True)
    source_index = analysis_v2.index_public_estimates(publics, acceptance)
    packet = analysis_v2.build_profiles(source_index, acceptance["audits"], latest_period_id=PERIODS[-1])
    parent = next(row for row in packet["national"] if row["period_id"] == PERIODS[-1]
                  and row["field_of_study_id"] == "033100")
    assert parent["value"] is None and parent["reason"] == "complementary_suppression"
    downstream = packet["record_index"][parent["record_id"]]
    released = downstream["record"]
    assert downstream["redaction_reason"] == "complementary_suppression"
    assert released["value"] is None and released["reason"] == "review_required"
    assert released["weighted_denominator"] is None
    assert released["support"]["weighted_support_total"] is None
    assert all(released["precision"][key] is None for key in analysis_v2.SUPPRESSED_PRECISION)
    assert source_index["by_grain"][parent["grain"]]["record"]["value"] == 3100.0
    sanitized_root = copy.deepcopy(publics[analysis_v2._snapshot(PERIODS[-1])])
    sanitized_root["records"] = [packet["record_index"]["v2r:" + analysis_v2._digest(
        list(analysis_v2._grain(row)))]["record"]
                                 for row in sanitized_root["records"]]
    assert validate_public_research_v2(sanitized_root) == []


def test_combined_digest_cannot_be_replaced(monkeypatch):
    publics, acceptance = synthetic_inputs(monkeypatch)
    acceptance["manifest"]["numeric_content_digest"] = "0" * 64
    with pytest.raises(ValueError, match="combined numeric content digest"):
        analysis_v2.index_public_estimates(publics, acceptance)


def test_jointly_replaced_audit_and_manifest_record_digest_blocks(monkeypatch):
    publics, acceptance = synthetic_inputs(monkeypatch)
    snapshot = analysis_v2._snapshot(PERIODS[-1])
    acceptance["audits"][snapshot]["numeric_digest"] = "0" * 64
    acceptance["manifest"]["snapshots"][snapshot]["numeric_digest"] = "0" * 64
    with pytest.raises(ValueError, match="numeric record digest"):
        analysis_v2.index_public_estimates(publics, acceptance)


def test_incomplete_accepted_code_inventory_blocks(monkeypatch):
    publics, acceptance = synthetic_inputs(monkeypatch)
    acceptance["manifest"]["code_sha256"].clear()
    with pytest.raises(ValueError, match="code hash inventory"):
        analysis_v2.index_public_estimates(publics, acceptance)


def test_repinned_unapproved_source_hash_blocks(monkeypatch):
    publics, acceptance = synthetic_inputs(monkeypatch)
    snapshot = analysis_v2._snapshot(PERIODS[-1])
    publics[snapshot]["sources"][0]["sha256"] = "b" * 64
    acceptance["audits"][snapshot]["source_sha256"] = "b" * 64
    new_content = analysis_v2._content_digest(publics[snapshot])
    acceptance["manifest"]["snapshots"][snapshot]["public_v2_digest"] = analysis_v2._digest(publics[snapshot])
    acceptance["manifest"]["snapshots"][snapshot]["public_content_sha256"] = new_content
    monkeypatch.setattr(analysis_v2, "_approved_public_pins", lambda: {
        snap: (new_content if snap == snapshot else pin["public_content_sha256"])
        for snap, pin in acceptance["manifest"]["snapshots"].items()})
    with pytest.raises(ValueError, match="approved pinned snapshot catalog"):
        analysis_v2.index_public_estimates(publics, acceptance)


def test_repinning_a_numeric_value_cannot_override_independent_golden(monkeypatch):
    publics, acceptance = synthetic_inputs(monkeypatch, complementary=True)
    snapshot = analysis_v2._snapshot(PERIODS[-1])
    public = publics[snapshot]
    row = next(item for item in public["records"] if item["field_of_study_id"] == "033100"
               and item["geography_id"] == "mx" and item["recorded_sex_id"] == "all")
    row["value"] = 3200.0
    row["weighted_denominator"] = 3200.0
    row["support"]["weighted_support_total"] = 3200.0
    row["precision"].update(standard_error=160.0, coefficient_variation=5.0,
                            ci90_lower=3000.0, ci90_upper=3400.0)
    assert validate_public_research_v2(public) == []
    audit = acceptance["audits"][snapshot]
    pin = acceptance["manifest"]["snapshots"][snapshot]
    audit["public_records"] = copy.deepcopy(public["records"])
    audit["numeric_digest"] = pin["numeric_digest"] = analysis_v2._digest(public["records"])
    audit["public_content_sha256"] = pin["public_content_sha256"] = analysis_v2._content_digest(public)
    pin["public_v2_digest"] = analysis_v2._digest(public)
    acceptance["manifest"]["numeric_content_digest"] = analysis_v2._digest({
        snap: item["numeric_digest"] for snap, item in acceptance["audits"].items()})
    with pytest.raises(ValueError, match="independent Phase 2 golden"):
        analysis_v2.index_public_estimates(publics, acceptance)


@pytest.mark.parametrize("target,value", [
    ("responding_resident_n", 999999999),
    ("population_eligible_n", 999999999),
    ("domain_n", 999999999),
    ("population_exclusion", -1),
    ("metric_exclusion", "1"),
    ("responding_resident_n", float("nan")),
    ("responding_resident_n", True),
])
def test_coverage_cannot_change_independently_of_accepted_inputs(monkeypatch, target, value):
    publics, acceptance = synthetic_inputs(monkeypatch)
    snapshot = analysis_v2._snapshot(PERIODS[0])
    audit = acceptance["audits"][snapshot]
    population = next(iter(audit["population_coverage"].values()))
    evaluated = next(iter(audit["evaluated_cells"].values()))
    if target in ("responding_resident_n", "population_eligible_n"):
        population[target] = value
    elif target == "domain_n":
        evaluated["coverage"][target] = value
    elif target == "population_exclusion":
        population["exclusions"]["unknown_field"] = value
    else:
        evaluated["exclusions"]["income_amount_unknown"] = value
    # A caller-controlled extra hash does not approve different coverage.
    try:
        claimed_digest = analysis_v2._coverage_digest(audit)
    except ValueError:
        claimed_digest = "0" * 64
    acceptance["manifest"]["snapshots"][snapshot]["coverage_sha256"] = claimed_digest
    with pytest.raises(ValueError, match="coverage"):
        analysis_v2.index_public_estimates(publics, acceptance)
