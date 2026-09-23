"""Synthetic-only integration tests for the strict estimate boundary."""

import json

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
    return Frame("enoe_2025_q2", "2025-Q2", "inegi_enoe", inventory,
                 frozenset({"033100"}), columns)


def test_inventory_includes_distinct_latest_slices():
    from brujula.estimates import required_estimation_domains
    domains = required_estimation_domains("enoe_2025_q2", latest_snapshot_id="enoe_2025_q2",
                                          field_ids=["033100"])
    assert any(d["population_id"] == "national_15_plus_context" for d in domains)
    assert any(d["field_of_study_id"] == "033100" and d["geography_id"] == "mx" for d in domains)
    assert any(d["field_of_study_id"] == "033100" and d["geography_id"] == "01" for d in domains)
    assert any(d["field_of_study_id"] == "033100" and d["recorded_sex_id"] == "2" for d in domains)
    assert len(domains) == len({tuple(sorted(d.items())) for d in domains})


def test_snapshot_evaluates_each_metric_and_strict_public_projection(monkeypatch, tmp_path):
    from brujula import estimates
    frame = synthetic_frame()
    monkeypatch.setattr(estimates, "load_snapshot_frame", lambda *a, **k: (frame, {"synthetic": True}))
    domain = {"population_id": "completed_professional_known_age", "field_of_study_id": "033100",
              "geography_id": "mx", "recorded_sex_id": "all"}
    result = estimates.estimate_snapshot(frame.snapshot_id, tmp_path, domains=[domain])
    records = result["internal"]["records"]
    assert len(records) == len(load_metric_manifest()["metrics"]) == 23
    assert result["audit"]["requested_cells"] == result["audit"]["evaluated_cells"]
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
    monkeypatch.setattr(estimates, "load_snapshot_frame", lambda *a, **k: (synthetic_frame(), {}))
    with pytest.raises(ValueError, match="verified|catalog"):
        estimates.estimate_snapshot("enoe_2025_q2", tmp_path,
                                    domains=[{"population_id": "completed_professional_known_age",
                                              "field_of_study_id": "999999", "geography_id": "mx",
                                              "recorded_sex_id": "all"}])
