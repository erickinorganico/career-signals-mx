"""Synthetic metric semantics and sentinel controls."""

import numpy as np
import pytest
import brujula.metrics as metrics_module

from brujula.enoe_adapter import load_snapshot_frame
from brujula.metrics import load_metric_manifest, metric_vectors
from brujula.populations import NATIONAL_15_PLUS_CONTEXT, COMPLETED_PROFESSIONAL_KNOWN_AGE
from test_enoe_adapter import fixture, ROWS


def vectors(tmp_path, metric, rows=ROWS, population=NATIONAL_15_PLUS_CONTEXT, domain=None):
    sid, root, registry = fixture(tmp_path, rows=rows)
    frame, _ = load_snapshot_frame(sid, root, registry)
    return metric_vectors(frame, population, domain or {}, metric)


def test_manifest_hash_and_all_metrics():
    manifest = load_metric_manifest()
    assert len(manifest["metrics"]) >= 18
    assert len(manifest["content_sha256"]) == 64
    for entry in manifest["metrics"]:
        assert {"id", "operation", "numerator", "denominator", "unit", "price_basis", "sentinels", "dictionary_refs"} <= set(entry)


def test_manifest_return_mutation_cannot_change_later_method(tmp_path):
    original = load_metric_manifest()
    expected = original["method_version"]
    original["method_version"] = "tampered"
    original["metrics"][0]["id"] = "tampered"
    original["dictionary_refs"]["2025-Q2"] = "0" * 64
    fresh = load_metric_manifest()
    assert fresh["method_version"] == expected
    assert fresh["metrics"][0]["id"] == "population_total"
    assert fresh["dictionary_refs"]["2025-Q2"] != "0" * 64
    result = vectors(tmp_path, "population_total")
    assert result["method_version"] != "tampered"
    assert result["synthetic"] is True
    assert result["dictionary_binding"] == "synthetic_fixture"


def test_real_frame_dictionary_mismatch_fails_before_metric(tmp_path):
    sid, root, registry = fixture(tmp_path)
    frame, _ = load_snapshot_frame(sid, root, registry)
    object.__setattr__(frame, "synthetic", False)
    frame.inventory["dictionary_member"]["sha256"] = "0" * 64
    with pytest.raises(ValueError, match="dictionary"):
        metric_vectors(frame, NATIONAL_15_PLUS_CONTEXT, {}, "occupied_total")


def test_occupied_pea_and_suboccupation_are_distinct(tmp_path):
    occupied = vectors(tmp_path / "occupied", "occupied_total")
    pea = vectors(tmp_path / "pea", "pea_total")
    sub = vectors(tmp_path / "sub", "suboccupied_rate")
    assert occupied["numerator"].tolist() == [1., 0., 1.]
    assert pea["numerator"].tolist() == [1., 1., 1.]
    assert sub["numerator"].tolist() == [1., 0., 0.]
    assert sub["denominator"].tolist() == [1., 0., 1.]
    assert all(x.shape == (3,) for x in (sub["numerator"], sub["denominator"], sub["domain"]))


def test_income_and_hours_states(tmp_path):
    income = vectors(tmp_path / "income", "positive_income_mean")
    hours = vectors(tmp_path / "hours", "known_hours_mean")
    assert income["numerator"].tolist() == [100., 0., 0.]
    assert income["denominator"].tolist() == [1., 0., 0.]
    assert hours["numerator"].tolist() == [40., 0., 0.]
    assert hours["denominator"].tolist() == [1., 0., 1.]
    assert hours["coverage"]["eligible_n"] == 2
    assert income["coverage"]["eligible_n"] == 1
    assert income["exclusions"]["no_income"] == 1


def test_unknown_age_field_and_empty_denominators(tmp_path):
    focal = vectors(tmp_path / "focal", "population_total", population=COMPLETED_PROFESSIONAL_KNOWN_AGE,
                    domain={"field_of_study": "033100"})
    assert focal["domain"].tolist() == [True, False, False]
    empty = vectors(tmp_path / "empty", "positive_income_mean", domain={"field_of_study": "032100"})
    assert empty["coverage"]["eligible_n"] == 0
    assert empty["coverage"]["weighted_denominator"] is None
    assert not np.any(empty["numerator"])


@pytest.mark.parametrize("snapshot_id", ["enoe_2025_q2", "enoe_2025_q3"])
@pytest.mark.parametrize("selector", [2, "02"])
def test_entity_selectors_match_canonical_loaded_geography(tmp_path, snapshot_id, selector):
    sid, root, registry = fixture(tmp_path / snapshot_id / str(selector), snapshot_id=snapshot_id)
    frame, _ = load_snapshot_frame(sid, root, registry)
    result = metric_vectors(frame, NATIONAL_15_PLUS_CONTEXT, {"entity": selector}, "occupied_total")
    assert result["domain"].tolist() == [True, True, False]
    assert result["numerator"].tolist() == [1.0, 0.0, 0.0]
    assert float(result["numerator"].sum()) == 1.0


def test_missing_entity_does_not_enter_valid_entity_domain(tmp_path):
    missing = ROWS[0].removesuffix(",02") + ","
    sid, root, registry = fixture(tmp_path, rows=[missing, ROWS[1], ROWS[2]])
    frame, _ = load_snapshot_frame(sid, root, registry)
    result = metric_vectors(frame, NATIONAL_15_PLUS_CONTEXT, {"entity": "02"}, "occupied_total")
    assert result["domain"].tolist() == [False, True, False]
    assert float(result["numerator"].sum()) == 0.0


@pytest.mark.parametrize("entity,geography", [(2, 3), ("02", "03"), (2, "03")])
def test_conflicting_geography_aliases_fail_before_vectors(tmp_path, entity, geography):
    sid, root, registry = fixture(tmp_path)
    frame, _ = load_snapshot_frame(sid, root, registry)
    with pytest.raises(ValueError, match="conflict"):
        metric_vectors(frame, NATIONAL_15_PLUS_CONTEXT,
                       {"entity": entity, "geography": geography}, "occupied_total")
    assert frame.metric_cache.get("domain_state") is None


@pytest.mark.parametrize("entity,geography", [(2, "02"), ("02", 2)])
def test_equivalent_geography_aliases_share_one_domain(tmp_path, entity, geography):
    sid, root, registry = fixture(tmp_path)
    frame, _ = load_snapshot_frame(sid, root, registry)
    result = metric_vectors(frame, NATIONAL_15_PLUS_CONTEXT,
                            {"entity": entity, "geography": geography}, "occupied_total")
    assert result["domain"].tolist() == [True, True, False]


def test_unknown_labor_status_does_not_become_rate_zero(tmp_path):
    row = ROWS[0].replace(",2,1,1,1,100,", ",2,1,9,1,100,")
    employment = vectors(tmp_path / "employment", "employment_rate", rows=[row, ROWS[1], ROWS[2]])
    unemployment = vectors(tmp_path / "unemployment", "unemployment_rate", rows=[row, ROWS[1], ROWS[2]])
    assert employment["denominator"].tolist() == [0., 1., 1.]
    assert unemployment["denominator"].tolist() == [0., 1., 1.]
    assert employment["exclusions"]["unknown_clase2"] == 1
    assert unemployment["exclusions"]["unknown_clase2"] == 1
    unknown_pea = ROWS[0].replace(",2,1,1,1,100,", ",2,9,1,1,100,")
    participation = vectors(tmp_path / "participation", "participation_rate", rows=[unknown_pea, ROWS[1], ROWS[2]])
    assert participation["denominator"].tolist() == [0., 1., 1.]
    assert participation["exclusions"]["unknown_clase1"] == 1


def test_income_state_shares_keep_known_band_with_unknown_amount(tmp_path):
    positive_amount_unknown = ROWS[0].replace(",1,100,1,", ",1,999999,1,")
    unspecified = ROWS[1].replace(",1,2,7,999999,", ",1,1,7,999999,")
    rows = [positive_amount_unknown, unspecified, ROWS[2]]
    no_income = vectors(tmp_path / "no_income", "no_income_share", rows=rows)
    unspecified_share = vectors(tmp_path / "unspecified", "unspecified_income_share", rows=rows)
    positive_mean = vectors(tmp_path / "positive", "positive_income_mean", rows=rows)
    assert no_income["denominator"].tolist() == [1., 1., 1.]
    assert unspecified_share["denominator"].tolist() == [1., 1., 1.]
    assert no_income["numerator"].tolist() == [0., 0., 1.]
    assert unspecified_share["numerator"].tolist() == [0., 1., 0.]
    assert positive_mean["coverage"]["weighted_denominator"] is None


def test_frame_reuses_masks_for_metrics_in_same_domain(tmp_path, monkeypatch):
    sid, root, registry = fixture(tmp_path)
    frame, _ = load_snapshot_frame(sid, root, registry)
    counts = {"domain": 0, "states": 0}
    original_domain, original_states = metrics_module._domain, metrics_module._states

    def domain_once(*args):
        counts["domain"] += 1
        return original_domain(*args)

    def states_once(*args):
        counts["states"] += 1
        return original_states(*args)

    monkeypatch.setattr(metrics_module, "_domain", domain_once)
    monkeypatch.setattr(metrics_module, "_states", states_once)
    for metric in ("occupied_total", "positive_income_mean", "known_hours_mean"):
        metric_vectors(frame, NATIONAL_15_PLUS_CONTEXT, {}, metric)
    assert counts == {"domain": 1, "states": 1}
    metric_vectors(frame, NATIONAL_15_PLUS_CONTEXT, {"entity": 2}, "occupied_total")
    assert counts == {"domain": 2, "states": 2}
    assert set(frame.metric_cache) == {"base", "domain_state"}


def test_unknown_suboccupation_excluded_from_rate_denominator(tmp_path):
    unknown_sub = ROWS[0].replace(",1,1,1,2,40,", ",1,1,9,2,40,")
    result = vectors(tmp_path, "suboccupied_rate", rows=[unknown_sub, ROWS[1], ROWS[2]])
    assert result["numerator"].tolist() == [0., 0., 0.]
    assert result["denominator"].tolist() == [0., 0., 1.]
    assert result["exclusions"]["unknown_sub_o"] == 1


@pytest.mark.parametrize("metric", ["positive_income_mean", "known_hours_mean", "suboccupied_rate", "unemployment_rate"])
def test_row_order_preserves_aggregate_vectors(tmp_path, metric):
    a = vectors(tmp_path / "a", metric)
    b = vectors(tmp_path / "b", metric, rows=list(reversed(ROWS)))
    assert sorted(a["numerator"].tolist()) == sorted(b["numerator"].tolist())
    assert sorted(a["denominator"].tolist()) == sorted(b["denominator"].tolist())
    assert a["coverage"] == b["coverage"]
