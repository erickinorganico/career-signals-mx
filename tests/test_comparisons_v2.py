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


@pytest.mark.parametrize("period, native, catalog_hash", [
    ("2025-Q2", "CVE_ENT", "f297f6856885a3da13f754749000e0a35d8c1745e7f2cf474a1e2adc01e07ddf"),
    ("2025-Q3", "ENT", "ea2e8198df208d0b662c00766739eb39c5a6b9a198821903d1a9416cdf9c7c1a"),
])
def test_coherent_native_alias_and_catalog_tamper_is_blocked(pair, registry, period, native, catalog_hash):
    earlier, later = pair("2025-Q2", geography="02"), pair("2025-Q3", geography="02", value=42)
    altered = deepcopy(registry)
    altered["snapshots"]["enoe_" + period.lower().replace("-", "_")].update(
        native_geography_field=native, state_catalog_sha256=catalog_hash)
    result = compare_public_records(earlier, later, registry=altered)
    assert not result["comparable"]
    assert result["absolute_change"] is None and result["relative_change_pct"] is None
    assert "geography_snapshot_identity" in result["reasons"]


def test_coherent_native_alias_and_catalog_tamper_is_blocked_for_national_metadata(pair, registry):
    earlier, later = pair("2025-Q2"), pair("2025-Q3", value=42)
    altered = deepcopy(registry)
    altered["snapshots"]["enoe_2025_q2"].update(
        native_geography_field="CVE_ENT",
        state_catalog_sha256="f297f6856885a3da13f754749000e0a35d8c1745e7f2cf474a1e2adc01e07ddf")
    result = compare_public_records(earlier, later, registry=altered)
    assert not result["comparable"]
    assert result["absolute_change"] is None and result["relative_change_pct"] is None
    assert "geography_snapshot_identity" in result["reasons"]


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
    altered["entity_reference_code"] = "02"
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
    next(cell for cell in profiles["national"] if cell["record_id"] == records[3]["record_id"])["value"] = None
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


def test_zero_prior_has_no_relative_percent_and_income_is_nominal(pair, registry):
    earlier, later = pair("2025-Q2", value=0), pair("2025-Q3", value=5)
    result = compare_public_records(earlier, later, registry=registry)
    assert result["comparable"] and result["absolute_change"] == 5
    assert result["relative_change_pct"] is None
    for item, amount in ((earlier, 10000), (later, 10500)):
        item["record"].update(metric_id="positive_income_mean", unit="MXN/month",
                              price_basis="nominal", value=amount)
        item["grain"] = tuple(item["record"][key] for key in registry["grain"])
        item["record_id"] = "v2r:" + hashlib.sha256(json.dumps(list(item["grain"]),
                            sort_keys=True, ensure_ascii=False, separators=(",", ":")).encode()).hexdigest()
    income = compare_public_records(earlier, later, registry=registry)
    assert income["comparable"] and income["absolute_change"] == 500
    assert income["display_unit"] == "nominal MXN/month"
    assert "purchasing" not in json.dumps(income).lower()


def test_missing_version_and_wrong_native_alias_are_blocked(pair, registry):
    earlier, later = pair("2025-Q2", geography="02"), pair("2025-Q3", geography="02")
    altered = deepcopy(registry)
    altered["snapshots"]["enoe_2025_q2"]["native_geography_field"] = "CVE_ENT"
    assert "geography_alias_code_name" in compare_public_records(earlier, later, registry=altered)["reasons"] or \
           "edition_revision" in compare_public_records(earlier, later, registry=altered)["reasons"]
    altered = deepcopy(registry)
    del altered["suppression_policy_version"]
    assert "precision_policy" in compare_public_records(earlier, later, registry=altered)["reasons"]
    altered = deepcopy(registry)
    altered["suppression_policy_version"] = "changed-nonempty"
    assert "precision_policy" in compare_public_records(earlier, later, registry=altered)["reasons"]
    altered = deepcopy(registry)
    altered["precision_policy_version"] = "changed-nonempty"
    assert "precision_policy" in compare_public_records(earlier, later, registry=altered)["reasons"]
    altered = deepcopy(registry)
    altered["states"]["02"]["name"] = "Changed official name"
    assert "geography_catalog" in compare_public_records(earlier, later, registry=altered)["reasons"]
    with pytest.raises(ValueError, match="fixed"):
        load_definition_registry(entity_reference_code="01")


def test_reason_and_id_order_are_stable(pair, registry):
    earlier, later = pair("2025-Q2"), pair("2025-Q3")
    later["record"]["population_id"] = "national_15_plus_context"
    later["record"]["unit"] = "people"
    first = compare_public_records(earlier, later, registry=registry)
    later["record"] = dict(reversed(list(later["record"].items())))
    second = compare_public_records(earlier, later, registry=registry)
    assert first["comparison_id"] == second["comparison_id"]
    assert first["reasons"] == second["reasons"] == sorted(set(first["reasons"]))


def test_fully_missing_pair_ids_remain_unique_across_series_and_slots(pair, registry):
    records = [pair("2024-Q3", metric="employment_rate"),
               pair("2024-Q3", metric="unemployment_rate")]
    for item in records:
        item["record"]["metric_id"] = item["grain"][8]
    profiles = {"periods": list(registry["periods"]),
                "metric_ids": ["employment_rate", "unemployment_rate"],
                "national": [{"record_id": x["record_id"], **x["record"]} for x in records],
                "latest_states": [], "latest_recorded_sexes": [],
                "record_index": {x["record_id"]: x for x in records}}
    ledger = build_comparison_ledger(profiles, registry=registry)
    assert len(ledger) == 22 and len({x["comparison_id"] for x in ledger}) == 22
    assert all(not x["comparable"] and x["absolute_change"] is None for x in ledger)
    assert sum(x["previous_record_id"] is None and x["current_record_id"] is None for x in ledger) > 0


def test_missing_reference_emits_blocked_entity_slots(pair, registry):
    left, right = pair("2026-Q2", geography="02"), pair("2026-Q2", geography="03")
    profiles = {"periods": list(registry["periods"]), "metric_ids": ["employment_rate"],
                "national": [], "latest_recorded_sexes": [],
                "latest_states": [{"record_id": x["record_id"], **x["record"]} for x in (left, right)],
                "record_index": {x["record_id"]: x for x in (left, right)}}
    ledger = build_comparison_ledger(profiles, registry=registry)
    entities = [x for x in ledger if x["comparison_type"] == "entity_slice"]
    assert entities and all(not x["comparable"] and "entity_reference_code" in x["reasons"] for x in entities)


@pytest.mark.parametrize("axis", ["sex", "entity"])
def test_same_period_slice_has_difference_limits_without_time_change(pair, registry, axis):
    registry["entity_reference_code"] = "02"
    if axis == "sex":
        left, right = pair("2026-Q2", sex="1"), pair("2026-Q2", sex="2", value=43)
    else:
        left, right = pair("2026-Q2", geography="02"), pair("2026-Q2", geography="01", value=43)
    result = compare_public_slices(left, right, axis=axis, registry=registry)
    assert result["comparable"] and result["absolute_change"] == 3
    assert "descriptive_difference_only" in result["limitations"]
    assert "same_period_descriptive_slice" in result["limitations"]
    assert not {"descriptive_change_only", "quarterly_samples_may_overlap", "seasonality_qoq", "like_quarter_yoy"}.intersection(result["limitations"])


def test_temporal_pairs_keep_specific_seasonality_and_overlap_limits(pair, registry):
    qoq = compare_public_records(pair("2025-Q2"), pair("2025-Q3"), registry=registry)
    yoy = compare_public_records(pair("2025-Q2"), pair("2026-Q2"), registry=registry)
    for result in (qoq, yoy):
        assert result["comparable"]
        assert {"descriptive_change_only", "quarterly_samples_may_overlap"}.issubset(result["limitations"])
        assert "same_period_descriptive_slice" not in result["limitations"]
    assert "seasonality_qoq" in qoq["limitations"] and "like_quarter_yoy" not in qoq["limitations"]
    assert "like_quarter_yoy" in yoy["limitations"] and "seasonality_qoq" not in yoy["limitations"]


@pytest.mark.parametrize("kind", ["reversed", "missing", "duplicate"])
def test_mutated_period_registry_cannot_authorize_a_different_window(pair, registry, kind):
    altered = deepcopy(registry)
    if kind == "reversed":
        altered["periods"] = tuple(reversed(registry["periods"]))
    elif kind == "missing":
        altered["periods"] = registry["periods"][1:]
    else:
        altered["periods"] = registry["periods"][:-1] + (registry["periods"][-2],)
    result = compare_public_records(pair("2025-Q3"), pair("2025-Q2"), registry=altered)
    assert not result["comparable"] and result["absolute_change"] is None
    assert "period_registry" in result["reasons"]
    profiles = {"periods": list(registry["periods"]), "record_index": {}, "national": [],
                "latest_states": [], "latest_recorded_sexes": []}
    with pytest.raises(ValueError, match="period registry"):
        build_comparison_ledger(profiles, registry=altered)



def test_geography_concept_cannot_be_coherently_replaced(pair, registry):
    altered = deepcopy(registry)
    altered["geography_concept"] = "arbitrary different state concept"
    result = compare_public_records(pair("2025-Q2", geography="02"),
                                    pair("2025-Q3", geography="02"), registry=altered)
    assert not result["comparable"] and result["absolute_change"] is None
    assert "geography_concept_review" in result["reasons"]
