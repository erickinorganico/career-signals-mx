import copy
from datetime import date
from pathlib import Path

import pytest

from brujula.data import load_dataset
from brujula.quality import compare_observations, validate_dataset

FIXTURE = Path(__file__).parents[1] / "data" / "fixtures" / "pilot.json"


def test_fixture_is_publishable_with_illustrative_freshness():
    result = validate_dataset(load_dataset(FIXTURE), as_of=date(2026, 1, 15))
    assert result["publishable"] is True
    assert result["status"] == "REVIEW"
    assert result["freshness"]["status"] == "REVIEW"
    assert any(row_status == "UNKNOWN" for row_status in result["row_statuses"].values())


def test_quality_fails_duplicate_grain_and_unapproved_source():
    dataset = load_dataset(FIXTURE)
    dataset["observations"].append(copy.deepcopy(dataset["observations"][0]))
    dataset["sources"][0]["approved"] = False
    result = validate_dataset(dataset)
    assert result["publishable"] is False
    ids = {check["id"] for check in result["checks"] if check["status"] == "FAIL"}
    assert {"duplicate_grain", "approved_source"} <= ids


def test_quality_fails_blocked_and_mismatched_evidence():
    dataset = load_dataset(FIXTURE)
    row = dataset["observations"][0]
    row["status"] = "BLOCKED"
    row["evidence_refs"] = []
    result = validate_dataset(dataset)
    assert result["publishable"] is False
    assert any(check["id"] == "evidence_required" for check in result["checks"])


@pytest.mark.parametrize("mutator,check_id", [
    (lambda d: d["observations"].append(copy.deepcopy(d["observations"][0])), "observation_ids"),
    (lambda d: d["observations"][0].update(source_id="missing"), "source_refs"),
    (lambda d: d["evidence"].append(copy.deepcopy(d["evidence"][0])), "evidence_ids"),
    (lambda d: d["dimensions"]["industries"].append(copy.deepcopy(d["dimensions"]["industries"][0])), "industry_ids"),
])
def test_quality_rejects_entity_duplicates_and_orphans(mutator, check_id):
    dataset = load_dataset(FIXTURE)
    mutator(dataset)
    result = validate_dataset(dataset)
    assert any(check["id"] == check_id for check in result["checks"] if check["status"] == "FAIL")


def test_quality_rejects_future_source_and_mixed_mode():
    dataset = load_dataset(FIXTURE)
    dataset["sources"][0]["checked_at"] = "2999-01-01"
    dataset["observations"][0]["synthetic"] = False
    result = validate_dataset(dataset)
    ids = {check["id"] for check in result["checks"] if check["status"] == "FAIL"}
    assert {"future_source", "synthetic_mode"} <= ids


def test_quality_uses_referenced_periods_for_freshness_and_blocks_official_snapshot():
    dataset = load_dataset(FIXTURE)
    dataset["observations"] = [row for row in dataset["observations"] if row["period_id"] == "demo_2025_q2"]
    result = validate_dataset(dataset, as_of=date(2026, 1, 15))
    assert result["freshness"]["latest_period_end"] == "2025-06-30"
    dataset["mode"] = "official_snapshot"
    result = validate_dataset(dataset, as_of=date(2026, 1, 15))
    assert any(check["id"] == "source_activation" for check in result["checks"])


def test_compare_preserves_null_and_zero_denominator():
    previous = {"concept_type":"field_of_study","concept_id":"demo_field_derecho","geography_id":"demo_mx","metric_id":"employed_people","unit":"people","population":"Employed people","methodology_id":"m","price_basis":"not_applicable","source_id":"demo_fixture_source","synthetic":True,"period_id":"demo_2025_q2","value":0,"status":"REVIEW","evidence_refs":["e"]}
    current = dict(previous, period_id="demo_2025_q3", value=3)
    periods = {
        "demo_2025_q2": {"start": "2025-04-01", "end": "2025-06-30"},
        "demo_2025_q3": {"start": "2025-07-01", "end": "2025-09-30"},
    }
    result = compare_observations(previous, current, periods)
    assert result["comparable"] is True
    assert result["absolute_change"] == 3
    assert result["relative_change_pct"] is None
    current["value"] = None
    assert compare_observations(previous, current, periods)["comparable"] is False


def test_compare_rejects_invalid_period_and_missing_evidence():
    previous = {"concept_type": "field_of_study", "concept_id": "x", "geography_id": "g", "metric_id": "m", "unit": "people", "population": "p", "methodology_id": "m", "price_basis": "not_applicable", "source_id": "s", "synthetic": True, "period_id": "p1", "value": 1, "status": "REVIEW", "evidence_refs": []}
    current = dict(previous, period_id="p2", value=2, evidence_refs=["e"])
    periods = {"p1": {"start": "2025-04-01", "end": "2025-06-30"}, "p2": {"start": "2025-06-01", "end": "2025-05-31"}}
    result = compare_observations(previous, current, periods)
    assert result["comparable"] is False
    assert {"missing_previous_evidence", "invalid_period_range"} <= set(result["reasons"])
