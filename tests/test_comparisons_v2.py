"""Fail-closed comparison contracts over sanitized public profile records."""

from copy import deepcopy
import hashlib
import json
from pathlib import Path

import pytest

from brujula.comparisons_v2 import (
    build_comparison_ledger, compare_public_records, compare_public_slices,
    comparison_signature, load_definition_registry,
)


ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture
def registry():
    return load_definition_registry()


@pytest.fixture
def pair(registry):
    snapshots = registry["snapshots"]
    def item(period, *, geography="mx", sex="all", value=40.0, metric="employment_rate"):
        snapshot = "enoe_" + period.lower().replace("-", "_")
        row = {"source_snapshot_id": snapshot, "population_id": "completed_professional_known_age",
               "field_of_study_id": "031300", "occupation_id": "all", "industry_id": "all",
               "geography_id": geography, "recorded_sex_id": sex, "period_id": period,
               "metric_id": metric, "method_id": "enoe_taylor_project_adjust",
               "method_version": registry["method_version"],
               "design_id": registry["design_id"], "unit": "percent", "price_basis": "not_applicable",
               "status": "MEASURED", "value": value, "reason": None,
               "precision": {"method": registry["precision_method"],
                             "ci_method": "logit_delta_normal_90", "singleton_policy": "adjust",
                             "official_precision": False}, "evidence_refs": [snapshot + "_custody"]}
        grain = tuple(row[k] for k in registry["grain"])
        record_id = "v2r:" + hashlib.sha256(json.dumps(list(grain), sort_keys=True,
                            ensure_ascii=False, separators=(",", ":")).encode()).hexdigest()
        return {"record_id": record_id, "grain": grain, "record": row,
                "snapshot_sha256": snapshots[snapshot]["raw_sha256"],
                "method_version": row["method_version"]}
    return item


def test_approved_signatures_and_cross_boundary(pair, registry):
    earlier = pair("2025-Q2", geography="02")
    later = pair("2025-Q3", geography="02", value=42)
    sig = comparison_signature(earlier["record"], earlier, registry)
    assert sig["geography_key"] == "02"
    assert sig["native_geography_field"] == "ENT"
    result = compare_public_records(earlier, later, registry=registry)
    assert result["comparable"] and result["absolute_change"] == 2
    assert result["display_unit"] == "percentage points"
    assert "unknown_edition_date" in result["limitations"]
    assert result["source_sha256s"] == [earlier["snapshot_sha256"], later["snapshot_sha256"]]


@pytest.mark.parametrize("mutation,reason", [
    (lambda x: x["record"].update(population_id="national_15_plus_context"), "population_id"),
    (lambda x: x["record"].update(recorded_sex_id="1"), "recorded_sex_id"),
    (lambda x: x["record"].update(occupation_id="031300"), "occupation_id"),
    (lambda x: x["record"].update(metric_id="unemployment_rate"), "metric_id"),
    (lambda x: x["record"].update(unit="people"), "unit"),
    (lambda x: x["record"].update(price_basis="nominal"), "price_basis"),
    (lambda x: x["record"].update(method_version="changed"), "method_version"),
    (lambda x: x.update(snapshot_sha256="0" * 64), "unapproved_snapshot"),
])
def test_signature_mismatch_blocks(pair, registry, mutation, reason):
    earlier, later = pair("2025-Q2"), pair("2025-Q3")
    mutation(later)
    result = compare_public_records(earlier, later, registry=registry)
    assert not result["comparable"] and result["absolute_change"] is None
    assert result["relative_change_pct"] is None and reason in result["reasons"]


def test_suppression_and_missing_policy_block(pair, registry):
    a, b = pair("2025-Q2"), pair("2025-Q3")
    b["record"]["value"] = None
    b["record"]["status"] = "REVIEW"
    b["redaction_reason"] = "complementary_suppression"
    result = compare_public_records(a, b, registry=registry)
    assert not result["comparable"] and "complementary_suppression" in result["reasons"]
    altered = deepcopy(registry)
    del altered["population_versions"]["completed_professional_known_age"]
    assert "population_version" in compare_public_records(a, pair("2025-Q3"), registry=altered)["reasons"]


def test_one_axis_slices_require_same_snapshot_and_reference(pair, registry):
    male, female = pair("2026-Q2", sex="1"), pair("2026-Q2", sex="2", value=43)
    assert compare_public_slices(male, female, axis="sex", registry=registry)["comparable"]
    female["record"]["geography_id"] = "02"
    assert not compare_public_slices(male, female, axis="sex", registry=registry)["comparable"]
    left, right = pair("2026-Q2", geography="01"), pair("2026-Q2", geography="02")
    altered = deepcopy(registry)
    altered["entity_reference_code"] = "01"
    assert compare_public_slices(left, right, axis="entity", registry=altered)["comparable"]
    del altered["entity_reference_code"]
    assert "entity_reference_code" in compare_public_slices(left, right, axis="entity", registry=altered)["reasons"]
    right["snapshot_sha256"] = "f" * 64
    assert not compare_public_slices(left, right, axis="entity", registry=registry)["comparable"]


def test_ledger_has_all_slots_in_stable_order(pair, registry):
    records = [pair(p, value=10 + i) for i, p in enumerate(registry["periods"])]
    profiles = {"periods": list(reversed(registry["periods"])), "metric_ids": ["employment_rate"],
                "national": [{"record_id": x["record_id"], **x["record"]} for x in reversed(records)],
                "latest_states": [], "latest_recorded_sexes": [],
                "record_index": {x["record_id"]: x for x in reversed(records)}}
    ledger = build_comparison_ledger(profiles, registry=registry)
    assert len(ledger) == 11
    assert [x["comparison_type"] for x in ledger].count("adjacent_quarter") == 7
    assert [x["comparison_type"] for x in ledger].count("like_quarter_annual") == 4
    assert all("standard_error" not in x and "p_value" not in x for x in ledger)
    records[3]["record"]["value"] = None
    blocked = build_comparison_ledger(profiles, registry=registry)
    assert len(blocked) == 11
    assert any(not x["comparable"] and x["absolute_change"] is None for x in blocked)


def test_ledger_rejects_record_index_identity_tamper(pair, registry):
    records = [pair(p) for p in registry["periods"]]
    profiles = {"periods": list(registry["periods"]), "metric_ids": ["employment_rate"],
                "national": [{"record_id": x["record_id"], **x["record"]} for x in records],
                "latest_states": [], "latest_recorded_sexes": [],
                "record_index": {x["record_id"]: x for x in records}}
    records[3]["record"]["population_id"] = "national_15_plus_context"
    with pytest.raises(ValueError, match="grain"):
        build_comparison_ledger(profiles, registry=registry)
