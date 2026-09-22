import copy
from datetime import date
from pathlib import Path

from brujula.data import load_dataset
from brujula.quality import compare_observations, validate_dataset

FIXTURE = Path(__file__).parents[1] / "data" / "fixtures" / "pilot.json"


def test_fixture_is_publishable_with_illustrative_freshness():
    result = validate_dataset(load_dataset(FIXTURE), as_of=date(2026, 1, 15))
    assert result["publishable"] is True
    assert result["status"] == "valid"
    assert result["freshness"]["status"] == "illustrative"
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


def test_compare_preserves_null_and_zero_denominator():
    previous = {"concept_type":"field_of_study","concept_id":"demo_field_derecho","geography_id":"demo_mx","metric_id":"employed_people","unit":"people","population":"Employed people","methodology_id":"m","price_basis":"not_applicable","source_id":"demo_fixture_source","synthetic":True,"period_id":"demo_2025_q2","value":0,"status":"REVIEW","evidence_refs":["e"]}
    current = dict(previous, period_id="demo_2025_q3", value=3)
    result = compare_observations(previous, current)
    assert result["comparable"] is True
    assert result["absolute_change"] == 3
    assert result["relative_change_pct"] is None
    current["value"] = None
    assert compare_observations(previous, current)["comparable"] is False
