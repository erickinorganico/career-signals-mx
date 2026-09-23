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


def synthetic_inputs(monkeypatch):
    """Generate small but complete Phase 3 synthetic public roots and audits."""
    monkeypatch.setattr(analysis_v2, "load_metric_manifest", lambda: {
        "content_sha256": GOLDEN["metric_manifest_sha256"],
        "metrics": [{"id": GOLDEN["metric_id"]}],
    })
    fields = GOLDEN["named_fields"]
    source_hash = GOLDEN["source_sha256"]
    manifest = {"status": "PASS", "numeric_content_digest": "synthetic-eight-quarter-digest",
                "metric_manifest_sha256": GOLDEN["metric_manifest_sha256"],
                "code_sha256": {"brujula/research_contract.py": analysis_v2.hashlib.sha256(
                    (ROOT / "brujula/research_contract.py").read_bytes().replace(b"\r\n", b"\n")).hexdigest()},
                "snapshots": {}}
    publics, audits = {}, {}
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
            records.append(row)
            grain = analysis_v2._ledger_key(tuple(row[key] for key in GRAIN))
            requested[grain] = True
            evaluated[grain] = {"status": "UNKNOWN", "has_estimate": False, "reason": "sample_size_below_30",
                                "coverage": {"domain_n": 0, "eligible_n": 0, "reason": "empty"},
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
                 "numeric_digest": "synthetic:" + snapshot,
                 "public_content_sha256": analysis_v2._content_digest(public)}
        manifest["snapshots"][snapshot] = {"public_v2_digest": analysis_v2._digest(public),
                                            "public_content_sha256": audit["public_content_sha256"],
                                            "numeric_digest": audit["numeric_digest"],
                                            "requested_count": len(records)}
        publics[snapshot] = public
        audits[snapshot] = audit
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
