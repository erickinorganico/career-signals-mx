"""Adversarial public-aggregate edge checks for the Phase 3 validation map."""

from __future__ import annotations

from copy import deepcopy

import pytest

from brujula import analysis_v2
from brujula.claims_v2 import select_opening_claims
from brujula.estimates import FOCAL_FIELDS
from brujula.source_inventory import PERIODS
from tests.test_analysis_v2 import synthetic_inputs


def _repin_catalog_only(monkeypatch, publics, accepted, snapshot):
    """Approve a changed test catalog while retaining the independent test pin."""
    original = analysis_v2._approved_public_pins()
    public = publics[snapshot]
    content = analysis_v2._content_digest(public)
    accepted["manifest"]["snapshots"][snapshot]["public_v2_digest"] = analysis_v2._digest(public)
    accepted["manifest"]["snapshots"][snapshot]["public_content_sha256"] = content
    accepted["audits"][snapshot]["public_content_sha256"] = content
    monkeypatch.setattr(analysis_v2, "_approved_public_pins", lambda: {**original, snapshot: content})


def _profiles(publics, accepted):
    index = analysis_v2.index_public_estimates(publics, accepted)
    return analysis_v2.build_profiles(index, accepted["audits"], latest_period_id=PERIODS[-1])


def test_same_catalog_code_keeps_field_occupation_and_industry_separate(monkeypatch):
    publics, accepted = synthetic_inputs(monkeypatch)
    snapshot = analysis_v2._snapshot(PERIODS[-1])
    public = publics[snapshot]
    code = FOCAL_FIELDS[0]
    public["occupations"].append({"id": code, "label": "Ocupación homónima"})
    public["industries"].append({"id": code, "label": "Industria homónima"})
    reference = next(row for row in public["records"] if row["field_of_study_id"] == "all"
                     and row["geography_id"] == "mx" and row["recorded_sex_id"] == "all")
    audit = accepted["audits"][snapshot]
    for dimension in ("occupation_id", "industry_id"):
        row = deepcopy(reference)
        row[dimension] = code
        public["records"].append(row)
        grain = tuple(row[key] for key in analysis_v2.GRAIN)
        key = analysis_v2._ledger_key(grain)
        audit["requested_cells"][key] = True
        original_key = analysis_v2._ledger_key(tuple(reference[key] for key in analysis_v2.GRAIN))
        audit["evaluated_cells"][key] = deepcopy(audit["evaluated_cells"][original_key])
    audit["public_records"] = deepcopy(public["records"])
    pin = accepted["manifest"]["snapshots"][snapshot]
    audit["numeric_digest"] = pin["numeric_digest"] = analysis_v2._digest(public["records"])
    pin["requested_count"] = len(public["records"])
    accepted["manifest"]["numeric_content_digest"] = analysis_v2._digest({
        name: item["numeric_digest"] for name, item in accepted["audits"].items()
    })
    coverage_pins = analysis_v2._approved_coverage_pins()
    coverage_pin = analysis_v2._coverage_digest(audit)
    monkeypatch.setattr(analysis_v2, "_approved_coverage_pins",
                        lambda: {**coverage_pins, snapshot: coverage_pin})
    _repin_catalog_only(monkeypatch, publics, accepted, snapshot)

    profiles = _profiles(publics, accepted)
    field_cells = [cell for cell in profiles["latest_fields"] if cell["field_of_study_id"] == code]
    assert field_cells
    assert all(cell["occupation_id"] == "all" and cell["industry_id"] == "all" for cell in field_cells)
    assert {cell["record_id"] for cell in field_cells} == {
        cell["record_id"] for cell in profiles["national"]
        if cell["period_id"] == PERIODS[-1] and cell["field_of_study_id"] == code
    }
    assert not {cell["record_id"] for cell in field_cells}.intersection({
        item["record_id"] for item in profiles["record_index"].values()
        if item["record"]["occupation_id"] == code or item["record"]["industry_id"] == code
    })


@pytest.mark.parametrize("unknown_code", ["", "999999"])
def test_unknown_cmpe_key_cannot_become_a_named_field(monkeypatch, unknown_code):
    publics, accepted = synthetic_inputs(monkeypatch)
    snapshot = analysis_v2._snapshot(PERIODS[-1])
    publics[snapshot]["fields_of_study"].append({"id": unknown_code, "label": "Campo inventado"})
    _repin_catalog_only(monkeypatch, publics, accepted, snapshot)

    with pytest.raises(ValueError):
        _profiles(publics, accepted)


def test_reordering_public_records_and_catalog_preserves_entire_profile_grid(monkeypatch):
    publics, accepted = synthetic_inputs(monkeypatch)
    baseline = _profiles(publics, accepted)
    reordered = deepcopy(publics)
    for snapshot, public in reordered.items():
        public["records"].reverse()
        public["fields_of_study"].reverse()
        audit = accepted["audits"][snapshot]
        pin = accepted["manifest"]["snapshots"][snapshot]
        audit["public_records"] = deepcopy(public["records"])
        audit["numeric_digest"] = pin["numeric_digest"] = analysis_v2._digest(public["records"])
        pin["public_v2_digest"] = analysis_v2._digest(public)
    accepted["manifest"]["numeric_content_digest"] = analysis_v2._digest({
        snapshot: audit["numeric_digest"] for snapshot, audit in accepted["audits"].items()
    })

    actual = _profiles(reordered, accepted)
    for section in ("national", "latest_fields", "latest_states", "latest_recorded_sexes"):
        assert actual[section] == baseline[section]
    assert actual["record_index"] == baseline["record_index"]


def test_overlapping_exclusions_survive_audit_permutation_without_additive_total(monkeypatch):
    publics, accepted = synthetic_inputs(monkeypatch)
    snapshot = analysis_v2._snapshot(PERIODS[-1])
    audit = accepted["audits"][snapshot]
    key = next(key for key in audit["population_coverage"] if FOCAL_FIELDS[0] in key and "|mx|all" in key)
    source = audit["population_coverage"][key]
    source["responding_resident_n"] = 10
    source["population_eligible_n"] = 8
    source["exclusions"]["age_unknown"] = 8
    source["exclusions"]["unknown_field"] = 7
    source["observed_category_counts"]["unknown_field"] = 7
    original = analysis_v2._approved_coverage_pins()
    pinned = analysis_v2._coverage_digest(audit)
    monkeypatch.setattr(analysis_v2, "_approved_coverage_pins", lambda: {**original, snapshot: pinned})
    index = analysis_v2.index_public_estimates(publics, accepted)
    baseline = analysis_v2.build_profiles(index, accepted["audits"], latest_period_id=PERIODS[-1])
    baseline_cell = next(cell for cell in baseline["latest_fields"] if cell["field_of_study_id"] == FOCAL_FIELDS[0])
    coverage = baseline_cell["coverage"]
    assert coverage["counts_nonexclusive"] is True
    assert coverage["responding_resident_n"] == 10
    assert coverage["exclusions"]["age_unknown"] == 8
    assert coverage["exclusions"]["unknown_field"] == 7
    assert sum(coverage["exclusions"].values()) > coverage["responding_resident_n"]
    assert "exclusive_exclusion_total" not in coverage

    permuted = deepcopy(accepted["audits"])
    affected = permuted[snapshot]["population_coverage"]
    permuted[snapshot]["population_coverage"] = dict(reversed(list(affected.items())))
    permuted[snapshot]["population_coverage"][key]["exclusions"] = dict(reversed(
        list(permuted[snapshot]["population_coverage"][key]["exclusions"].items())
    ))
    actual = analysis_v2.build_profiles(index, permuted, latest_period_id=PERIODS[-1])
    assert actual["latest_fields"] == baseline["latest_fields"]


def test_observed_support_is_not_replaced_by_a_weighted_population_estimate(monkeypatch):
    publics, accepted = synthetic_inputs(monkeypatch, complementary=True)
    profiles = _profiles(publics, accepted)
    cell = next(row for row in profiles["latest_states"]
                if row["field_of_study_id"] == "033100" and row["geography_id"] == "02")
    assert cell["sample_size"] == cell["coverage"]["observed_n"] == 40
    assert cell["weighted_denominator_estimate"] == 100.0
    assert cell["weighted_denominator_estimate"] != cell["sample_size"]
    assert "effective_sample_size" not in cell and "effective_sample_size" not in cell["coverage"]


@pytest.mark.parametrize("count", [1, 2])
def test_one_or_two_supported_opening_claims_are_retained(count):
    candidates = [
        {"claim_id": f"v2k:{i}", "kind": "observation", "subject_id": f"v2r:{i}",
         "metric_id": metric, "record_ids": [f"v2r:{i}"], "sample_sizes": [40]}
        for i, metric in enumerate(("positive_income_coverage", "employment_rate"))
    ]
    actual = select_opening_claims(candidates[:count])
    assert [claim["claim_id"] for claim in actual] == [claim["claim_id"] for claim in candidates[:count]]
