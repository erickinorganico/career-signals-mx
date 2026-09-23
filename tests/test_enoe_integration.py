"""Synthetic inventory and failure-state acceptance controls."""

import json
from copy import deepcopy
from unittest.mock import patch

import pytest

from brujula import estimates
from brujula.metrics import load_metric_manifest
from scripts.accept_enoe_estimates import (
    _canonical_research_content, _digest, compare_inventory, compare_pinned_numeric_content,
    expected_acceptance_domains, initialize_internal_golden, verify_acceptance_domains,
    write_attempt, run_attempt, _verify_result,
)
from test_estimates import synthetic_frame


def test_missing_or_duplicate_evaluation_blocks():
    assert compare_inventory(["a", "b"], ["a"], ["a", "b"])["status"] == "BLOCKED"
    assert compare_inventory(["a"], ["a", "a"], ["a"])["status"] == "BLOCKED"


@pytest.mark.parametrize("missing", [
    ("completed_professional_known_age", "033100", "32", "all"),
    ("completed_professional_known_age", "033100", "mx", "2"),
    ("completed_professional_known_age", "031300", "mx", "all"),
])
def test_complete_acceptance_inventory_rejects_omitted_domain(missing):
    catalog = {"033100", "031300", "032100"}
    required = expected_acceptance_domains("enoe_2026_q2", sorted(catalog), catalog)
    assert len(required) == 5 + 4 * 34 + 1
    actual = [domain for domain in required if tuple(domain[key] for key in
              ("population_id", "field_of_study_id", "geography_id", "recorded_sex_id")) != missing]
    with pytest.raises(ValueError, match="complete acceptance domain inventory mismatch"):
        verify_acceptance_domains(actual, required)


def test_explicit_baja_california_context_domains_are_required():
    catalog = {"033100", "031300", "032100"}
    for snapshot in ("enoe_2025_q2", "enoe_2026_q2"):
        required = expected_acceptance_domains(snapshot, sorted(catalog), catalog)
        assert {tuple(d.values()) for d in required} >= {
            ("national_15_plus_context", "all", "02", "all")}
        with pytest.raises(ValueError, match="complete acceptance domain inventory mismatch"):
            verify_acceptance_domains([d for d in required if not (
                d["population_id"] == "national_15_plus_context" and d["geography_id"] == "02")], required)


def _numeric_pin_fixture():
    snapshot = "enoe_2024_q3"  # outside the latest R and official cases
    public = {
        "schema_version": "2.0", "sources": [{"id": snapshot}],
        "fields_of_study": [{"id": "all"}], "geographies": [{"id": "mx"}],
        "metrics": [{"id": "known_hours_mean"}],
        "methods": [{"id": "enoe_taylor_project_adjust", "version": "adapter:old"}],
        "records": [{"source_snapshot_id": snapshot, "metric_id": "known_hours_mean",
                     "method_version": "adapter:old", "value": 42.5, "sample_size": 100,
                     "weighted_denominator": 1000.0, "support": {"weighted_support_total": 1000.0},
                     "precision": {"standard_error": 0.5}, "status": "REVIEW",
                     "reason": "project_singleton_adjustment"}],
    }
    internal = deepcopy(public)
    internal["records"][0]["estimate"] = 42.5
    golden = {"metric_manifest_sha256": "metric-digest",
              "public_content_sha256_by_snapshot": {snapshot: _digest(_canonical_research_content(public))},
              "internal_content_sha256_by_snapshot": {snapshot: _digest(_canonical_research_content(internal))}}
    return snapshot, public, internal, golden


def test_non_oracle_older_quarter_metric_change_blocks_public_pin():
    snapshot, public, internal, golden = _numeric_pin_fixture()
    assert compare_pinned_numeric_content(public, internal, golden, snapshot, "metric-digest")
    changed = deepcopy(public)
    changed["records"][0]["value"] = 43.5
    with pytest.raises(ValueError, match="pinned public numeric content"):
        compare_pinned_numeric_content(changed, internal, golden, snapshot, "metric-digest")


def test_suppressed_internal_only_diagnostic_change_blocks_hash_pin():
    snapshot, public, internal, golden = _numeric_pin_fixture()
    public["records"][0]["value"] = None
    public["records"][0]["weighted_denominator"] = None
    public["records"][0]["precision"]["standard_error"] = None
    internal["records"][0]["value"] = None
    internal["records"][0]["estimate"] = 42.5
    golden["public_content_sha256_by_snapshot"][snapshot] = _digest(_canonical_research_content(public))
    golden["internal_content_sha256_by_snapshot"][snapshot] = _digest(_canonical_research_content(internal))
    changed = deepcopy(internal)
    changed["records"][0]["estimate"] = 43.5
    with pytest.raises(ValueError, match="pinned internal numeric diagnostics"):
        compare_pinned_numeric_content(public, changed, golden, snapshot, "metric-digest")


def test_method_source_hash_change_does_not_change_numeric_pin():
    snapshot, public, internal, golden = _numeric_pin_fixture()
    for document in (public, internal):
        document["methods"][0]["version"] = "adapter:new"
        document["records"][0]["method_version"] = "adapter:new"
    assert compare_pinned_numeric_content(public, internal, golden, snapshot, "metric-digest")
    with pytest.raises(ValueError, match="metric manifest"):
        compare_pinned_numeric_content(public, internal, golden, snapshot, "wrong-metric-digest")


def test_internal_initialization_cannot_rewrite_public_baseline():
    snapshot, _, _, golden = _numeric_pin_fixture()
    prior = {key: value for key, value in golden.items() if key != "internal_content_sha256_by_snapshot"}
    assert initialize_internal_golden(prior, golden) == golden
    changed = deepcopy(golden)
    changed["public_content_sha256_by_snapshot"][snapshot] = "replacement"
    with pytest.raises(ValueError, match="would change approved public"):
        initialize_internal_golden(prior, changed)


def test_failure_invalidates_previous_success(tmp_path):
    write_attempt(tmp_path, {"status": "PASS", "digest": "old"})
    write_attempt(tmp_path, {"status": "BLOCKED", "reason": "numerical_failure"})
    assert json.loads((tmp_path / "current.json").read_text())["status"] == "BLOCKED"
    assert not (tmp_path / "current.json").read_text().count("old")


def test_actual_synthetic_result_grains_and_suppression_are_checked(tmp_path):
    frame = synthetic_frame()
    domain = {"population_id": "completed_professional_known_age", "field_of_study_id": "033100",
              "geography_id": "mx", "recorded_sex_id": "all"}
    with patch.object(estimates, "load_snapshot_frame", return_value=(
            frame, {"synthetic": True, "provenance": frame.provenance})):
        output = estimates.estimate_snapshot(frame.snapshot_id, tmp_path, domains=[domain])
    # The real-source provenance check intentionally blocks a synthetic run;
    # the record inventory check still verifies the computed 23-metric grain.
    expected = list(output["audit"]["requested_cells"])
    assert len(expected) == len(load_metric_manifest()["metrics"]) == 23
    assert compare_inventory(expected, list(output["audit"]["requested_cells"]),
                             list(output["audit"]["evaluated_cells"]))["status"] == "PASS"
    with pytest.raises(ValueError, match="real source provenance"):
        _verify_result(output, [domain], sorted(x["id"] for x in load_metric_manifest()["metrics"]),
                       frame.snapshot_id, frame.period)
    output["audit"]["requested_cells"][expected[0]] = False
    with pytest.raises(ValueError, match="declared true"):
        _verify_result(output, [domain], sorted(x["id"] for x in load_metric_manifest()["metrics"]),
                       frame.snapshot_id, frame.period)
    output["audit"]["requested_cells"][expected[0]] = True
    output["audit"]["evaluated_cells"][expected[0]]["status"] = "BLOCKED"
    with pytest.raises(ValueError, match="metadata differs"):
        _verify_result(output, [domain], sorted(x["id"] for x in load_metric_manifest()["metrics"]),
                       frame.snapshot_id, frame.period)
    output["audit"]["evaluated_cells"][expected[0]]["status"] = output["internal"]["records"][0]["status"]
    output["audit"]["evaluated_cells"].pop(expected[0])
    with pytest.raises(ValueError, match="grain mismatch"):
        _verify_result(output, [domain], sorted(x["id"] for x in load_metric_manifest()["metrics"]),
                       frame.snapshot_id, frame.period)


def test_run_attempt_uses_failing_operation(tmp_path):
    run_attempt(tmp_path, lambda: {"status": "PASS", "numeric_content_digest": "old"})
    def fail():
        raise ValueError("synthetic numerical mismatch")
    result = run_attempt(tmp_path, fail)
    assert result["status"] == "BLOCKED"
    assert "synthetic numerical mismatch" in result["reason"]
    assert "old" not in (tmp_path / "current.json").read_text(encoding="utf-8")
