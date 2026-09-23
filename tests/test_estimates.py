"""Synthetic-only integration tests for the strict estimate boundary."""

import json
from dataclasses import replace

import numpy as np
import pytest

from brujula.enoe_adapter import Frame
from brujula.metrics import load_metric_manifest
from brujula.research_contract import validate_public_research_v2, validate_research_v2


def synthetic_frame(n=40):
    columns = {
        "fac_tri": np.ones(n), "est_d_tri": np.array(["1"] * n),
        "upm": np.arange(n), "eda": np.full(n, 30), "cs_p13_1": np.full(n, 7),
        "cs_p16": np.ones(n, dtype=int), "cs_p14_c": np.array(["033100"] * n),
        "sex": np.tile([1, 2], n // 2), "ent": np.ones(n, dtype=int),
        "clase1": np.ones(n, dtype=int), "clase2": np.tile([1, 2], n // 2),
        "ing7c": np.full(n, 1), "ingocup": np.tile([100, 200], n // 2),
        "emp_ppal": np.tile([1, 2], n // 2), "pos_ocu": np.tile([1, 2], n // 2),
        "sub_o": np.tile([1, 0], n // 2), "dur9c": np.full(n, 2),
        "hrsocup": np.tile([30, 40], n // 2),
    }
    for array in columns.values():
        array.flags.writeable = False
    inventory = {
        "geography_header": "ENT", "raw_sha256": "a" * 64,
        "source_url": "https://www.inegi.org.mx/synthetic.zip",
        "terms_url": "https://www.inegi.org.mx/inegi/terminos.html",
        "authority": "INEGI", "acquired_at": "2026-09-22T00:00:00Z",
        "receipt_run_id": "synthetic", "dictionary_member": {"sha256": "b" * 64},
    }
    return Frame(snapshot_id="enoe_2025_q2", period="2025-Q2", source_id="inegi_enoe",
                 synthetic=True, provenance="declared_synthetic_fixture", inventory=inventory,
                 cmpe_catalog_keys=frozenset({"033100"}), cmpe_catalog_labels={"033100": "Derecho"},
                 columns=columns)


def test_inventory_includes_distinct_latest_slices():
    from brujula.estimates import required_estimation_domains
    domains = required_estimation_domains("enoe_2025_q2", latest_snapshot_id="enoe_2025_q2",
                                          field_ids=["033100"])
    assert any(d["population_id"] == "national_15_plus_context" for d in domains)
    assert any(d["field_of_study_id"] == "033100" and d["geography_id"] == "mx" for d in domains)
    assert any(d["field_of_study_id"] == "033100" and d["geography_id"] == "01" for d in domains)
    assert any(d["field_of_study_id"] == "033100" and d["recorded_sex_id"] == "2" for d in domains)
    assert len(domains) == len({tuple(sorted(d.items())) for d in domains})
    assert len(domains) == 5 + 4 * (32 + 2)
    assert all(d["geography_id"] == "mx" or d["recorded_sex_id"] == "all" for d in domains)
    historical = required_estimation_domains("enoe_2025_q1", latest_snapshot_id="enoe_2025_q2",
                                              field_ids=["033100"])
    assert len(historical) == 5


def test_snapshot_evaluates_each_metric_and_strict_public_projection(monkeypatch, tmp_path):
    from brujula import estimates
    frame = synthetic_frame()
    monkeypatch.setattr(estimates, "load_snapshot_frame", lambda *a, **k: (frame, {"synthetic": True, "provenance": frame.provenance}))
    domain = {"population_id": "completed_professional_known_age", "field_of_study_id": "033100",
              "geography_id": "mx", "recorded_sex_id": "all"}
    result = estimates.estimate_snapshot(frame.snapshot_id, tmp_path, domains=[domain])
    records = result["internal"]["records"]
    assert len(records) == len(load_metric_manifest()["metrics"]) == 23
    assert result["audit"]["requested_cells"].keys() == result["audit"]["evaluated_cells"].keys()
    assert validate_research_v2(result["internal"]) == []
    assert validate_public_research_v2(result["public"]) == []
    assert all(r["status"] != "MEASURED" for r in records)
    assert all("id" not in r for r in records)
    for internal, public in zip(records, result["public"]["records"]):
        if internal["value"] is None:
            assert public["weighted_denominator"] is None
            assert public["support"]["weighted_support_total"] is None
            assert all(public["precision"][key] is None for key in
                       ("standard_error", "coefficient_variation", "ci90_lower", "ci90_upper"))
    assert "cs_p14_c" not in json.dumps(result["audit"])


def test_unverified_field_rejected(monkeypatch, tmp_path):
    from brujula import estimates
    frame = synthetic_frame()
    monkeypatch.setattr(estimates, "load_snapshot_frame", lambda *a, **k: (frame, {"synthetic": True, "provenance": frame.provenance}))
    with pytest.raises(ValueError, match="verified|catalog"):
        estimates.estimate_snapshot("enoe_2025_q2", tmp_path,
                                    domains=[{"population_id": "completed_professional_known_age",
                                              "field_of_study_id": "999999", "geography_id": "mx",
                                              "recorded_sex_id": "all"}])


def test_ratio_support_includes_known_zero_outcomes(monkeypatch, tmp_path):
    from brujula import estimates
    frame = synthetic_frame()
    monkeypatch.setattr(estimates, "load_snapshot_frame", lambda *a, **k: (frame, {"synthetic": True, "provenance": frame.provenance}))
    domain = {"population_id": "completed_professional_known_age", "field_of_study_id": "033100",
              "geography_id": "mx", "recorded_sex_id": "all"}
    rows = estimates.estimate_snapshot(frame.snapshot_id, tmp_path, domains=[domain])["internal"]["records"]
    rate = next(row for row in rows if row["metric_id"] == "employment_rate")
    assert rate["sample_size"] == 40
    assert rate["support"]["weighted_support_total"] == 40
    assert rate["weighted_denominator"] == 40


def test_method_version_normalizes_platform_line_endings(monkeypatch, tmp_path):
    from brujula import estimates
    source = tmp_path / "adapter.py"
    manifest = load_metric_manifest()
    monkeypatch.setattr(estimates.enoe_adapter, "__file__", str(source))
    source.write_bytes(b"a = 1\n")
    unix = estimates._method_version(manifest)
    source.write_bytes(b"a = 1\r\n")
    assert estimates._method_version(manifest) == unix


def test_catalogued_field_with_zero_observed_rows_is_evaluated(monkeypatch, tmp_path):
    from brujula import estimates
    frame = synthetic_frame()
    frame = replace(frame, cmpe_catalog_keys=frozenset({"033100", "031300"}),
                    cmpe_catalog_labels={"033100": "Derecho", "031300": "Ciencias políticas"})
    monkeypatch.setattr(estimates, "load_snapshot_frame", lambda *a, **k: (frame, {"synthetic": True, "provenance": frame.provenance}))
    domain = {"population_id": "completed_professional_known_age", "field_of_study_id": "031300",
              "geography_id": "mx", "recorded_sex_id": "all"}
    result = estimates.estimate_snapshot(frame.snapshot_id, tmp_path, domains=[domain])
    assert result["audit"]["requested_count"] == result["audit"]["evaluated_count"] == 23
    assert all(row["sample_size"] == 0 and row["value"] is None and row["reason"]
               for row in result["internal"]["records"])


def test_missing_synthetic_provenance_fails_closed(monkeypatch, tmp_path):
    from brujula import estimates
    monkeypatch.setattr(estimates, "load_snapshot_frame", lambda *a, **k: (synthetic_frame(), {}))
    domain = {"population_id": "completed_professional_known_age", "field_of_study_id": "033100",
              "geography_id": "mx", "recorded_sex_id": "all"}
    with pytest.raises(ValueError, match="synthetic provenance"):
        estimates.estimate_snapshot("enoe_2025_q2", tmp_path, domains=[domain])


def test_aggregate_audit_keeps_distinct_exclusions_without_weighted_leaks(monkeypatch, tmp_path):
    from brujula import estimates
    frame = synthetic_frame()
    columns = dict(frame.columns)
    for name in ("eda", "cs_p13_1", "cs_p16", "cs_p14_c", "ingocup"):
        columns[name] = columns[name].copy()
    columns["cs_p14_c"] = columns["cs_p14_c"].astype(object)
    columns["eda"][0] = 98
    columns["cs_p13_1"][1] = 6
    columns["cs_p13_1"][2] = 8
    columns["cs_p16"][3] = 2
    columns["cs_p14_c"][4] = None
    columns["ingocup"][6] = 0
    frame = replace(frame, columns=columns)
    source_audit = {"synthetic": True, "provenance": frame.provenance,
                    "lexemes": {"eda": {"digits": 40}}}
    monkeypatch.setattr(estimates, "load_snapshot_frame", lambda *a, **k: (frame, source_audit))
    domain = {"population_id": "completed_professional_known_age", "field_of_study_id": "all",
              "geography_id": "mx", "recorded_sex_id": "all"}
    output = estimates.estimate_snapshot(frame.snapshot_id, tmp_path, domains=[domain])
    audit = output["audit"]
    assert audit["source_frame_audit"]["lexemes"]["eda"]["digits"] == 40
    population = audit["population_coverage"]["completed_professional_known_age|all|mx|all"]
    assert population["responding_resident_n"] == 40
    assert population["counts_nonexclusive"] is True
    assert all(population["exclusions"][key] == 1 for key in
               ("age_unknown", "technical_education", "postgraduate_education",
                "incomplete_education"))
    assert population["observed_category_counts"]["unknown_field_eligible_professional"] == 1
    income_key = next(key for key in audit["evaluated_cells"] if "|positive_income_mean|" in key)
    assert audit["evaluated_cells"][income_key]["exclusions"]["income_amount_unknown"] >= 1
    assert audit["evaluated_cells"][income_key]["coverage"]["eligible_n"] > 0
    assert "weighted_denominator" not in json.dumps(audit)


def test_population_coverage_matches_age_and_education_sentinels():
    from brujula import estimates

    frame = synthetic_frame()
    columns = dict(frame.columns)
    for name in ("eda", "cs_p13_1"):
        columns[name] = columns[name].copy()
    columns["eda"][:4] = [98, -1, 99, 14]
    columns["cs_p13_1"][:4] = [0, -1, 99, 6]
    frame = replace(frame, columns=columns)

    national = estimates._population_coverage(frame, {
        "population_id": "national_15_plus_context", "field_of_study_id": "all",
        "geography_id": "mx", "recorded_sex_id": "all",
    })
    professional = estimates._population_coverage(frame, {
        "population_id": "completed_professional_known_age", "field_of_study_id": "all",
        "geography_id": "mx", "recorded_sex_id": "all",
    })

    # National EDA 98 is included operationally; missing/99 age is unknown,
    # and -1 must never leak into the under-15 count.
    assert national["population_eligible_n"] == 37
    assert national["exclusions"]["age_unknown"] == 2
    assert national["exclusions"]["age_below_15"] == 1
    assert national["exclusions"]["technical_education"] == 0
    assert national["exclusions"]["other_education"] == 0
    assert national["observed_category_counts"]["age_unknown_operational_included_n"] == 1

    # The known-age professional cohort excludes 98 and applies education
    # exclusions; catalog value 0 is known other education.
    assert professional["population_eligible_n"] == 36
    assert professional["exclusions"]["age_unknown"] == 3
    assert professional["exclusions"]["age_below_15"] == 1
    assert professional["exclusions"]["other_education"] == 1
    assert professional["exclusions"]["unknown_education"] == 2
    assert professional["exclusions"]["technical_education"] == 1


def test_population_coverage_counts_all_known_nonprofessional_education_codes():
    from brujula import estimates

    frame = synthetic_frame()
    columns = dict(frame.columns)
    columns["cs_p13_1"] = columns["cs_p13_1"].copy()
    columns["cs_p13_1"][:6] = [0, 1, 2, 3, 4, 5]
    frame = replace(frame, columns=columns)
    coverage = estimates._population_coverage(frame, {
        "population_id": "completed_professional_known_age", "field_of_study_id": "all",
        "geography_id": "mx", "recorded_sex_id": "all",
    })
    assert coverage["exclusions"]["other_education"] == 6
