import math

import numpy as np
import pytest

from brujula.survey import SurveyDesign, Z90


def test_analytic_stratified_total():
    design = SurveyDesign([1] * 4, [1, 1, 2, 2], [1, 2, 3, 4])
    result = design.total([10, 30, 20, 40])
    assert result["estimate"] == 100
    assert result["standard_error"] == pytest.approx(math.sqrt(800))
    assert result["ci_lower"] == pytest.approx(100 - Z90 * math.sqrt(800))
    assert result["design_df"] == 2
    assert result["value"] is None
    assert result["sample_size"] == 4


def test_singleton_policy_defaults_to_fail():
    with pytest.raises(ValueError, match="singleton stratum"):
        SurveyDesign([1, 1, 1], [1, 2, 2], [1, 2, 3])


def test_singleton_policy_rejects_unknown_value():
    with pytest.raises(ValueError, match="singleton_policy must be fail or adjust"):
        SurveyDesign([1, 1], [1, 1], [1, 2], singleton_policy="collapse")


def test_singleton_adjust_uses_full_frame_grandmean_and_factor_one():
    # PSU totals are 10 (singleton), 30 and 50. The grand mean is 30.
    design = SurveyDesign([1, 1, 1], [1, 2, 2], [1, 2, 3],
                          singleton_policy="adjust")
    result = design.total([10, 30, 50])

    # Singleton: (10 - 30)^2 * 1; stratum 2: ((30 - 40)^2 +
    # (50 - 40)^2) * 2/(2-1).
    assert result["standard_error"] == pytest.approx(math.sqrt(800))
    assert result["singleton_policy"] == "adjust"
    assert result["singleton_strata_count"] == 1
    assert result["variance_method"].endswith("_singleton_adjust")


def test_singleton_adjust_marks_review_and_exposes_precision_note():
    weights = [1.0] * 30
    strata = ["singleton"] * 10 + ["paired"] * 20
    psu = ["p1"] * 10 + ["p2"] * 10 + ["p3"] * 10
    values = [1.0] * 10 + [3.0] * 10 + [5.0] * 10

    result = SurveyDesign(weights, strata, psu,
                          singleton_policy="adjust").total(values)

    assert result["sample_size"] == 30
    assert result["n_psu_domain"] == 3
    assert result["status"] == "REVIEW"
    assert result["value"] is None
    assert "Project variance approximation" in result["precision_note"]


def test_domain_variance_keeps_zero_contributor_psus_in_full_frame():
    design = SurveyDesign([1] * 4, [1, 1, 2, 2], [1, 2, 3, 4])
    result = design.total([10, math.nan, 30, math.nan],
                          domain=[True, False, True, False])

    # Domain PSU totals are [10, 0] and [30, 0]; both zero PSUs remain in
    # their strata for variance estimation.
    assert result["estimate"] == 40
    assert result["weighted_denominator"] == 2
    assert result["n_psu_domain"] == 2
    assert result["standard_error"] == pytest.approx(math.sqrt(1000))


def test_total_is_invariant_to_row_permutation():
    weights = np.array([1, 2, 1, 3, 2, 1], dtype=float)
    strata = np.array(["a", "a", "b", "b", "b", "b"], dtype=object)
    psu = np.array(["a1", "a2", "b1", "b1", "b2", "b2"], dtype=object)
    values = np.array([4, 8, 3, 7, 2, 6], dtype=float)
    order = np.array([5, 2, 0, 4, 1, 3])

    first = SurveyDesign(weights, strata, psu).total(values)
    second = SurveyDesign(weights[order], strata[order], psu[order]).total(values[order])

    for key in ("estimate", "standard_error", "weighted_denominator"):
        assert second[key] == pytest.approx(first[key])


def test_analytic_ratio_and_actual_denominator():
    design = SurveyDesign([1, 1], [1, 1], [1, 2])
    result = design.ratio([2, 4], [1, 1])
    assert result["estimate"] == 3
    assert result["standard_error"] == 1
    assert result["weighted_denominator"] == 2
    other = design.ratio([4, 8], [2, 2])
    assert other["estimate"] == 3
    assert other["standard_error"] == 1
    assert other["weighted_denominator"] == 4


def test_domain_preserves_zero_contribution_psus():
    design = SurveyDesign([1, 1], [1, 1], [1, 2])
    result = design.total([1, np.nan], domain=[True, False])
    assert result["estimate"] == 1
    assert result["standard_error"] == 1
    assert result["n_psu_domain"] == 1
    assert result["design_df"] == 1
    with pytest.raises(ValueError, match="singleton"):
        SurveyDesign([1], [1], [1])


def test_weight_scale_metamorphism():
    a = SurveyDesign([2, 3, 4, 5], [1, 1, 2, 2], [1, 2, 3, 4])
    b = SurveyDesign([20, 30, 40, 50], [1, 1, 2, 2], [1, 2, 3, 4])
    for method, args in [("total", ([1, 2, 3, 4],)),
                         ("ratio", ([1, 2, 3, 4], [1] * 4))]:
        first, second = getattr(a, method)(*args), getattr(b, method)(*args)
        factor = 10 if method == "total" else 1
        for key in ("estimate", "standard_error"):
            assert second[key] == pytest.approx(first[key] * factor)
        assert second["coefficient_variation"] == pytest.approx(first["coefficient_variation"])


def test_nested_psu_ids_and_row_permutation():
    weights, strata, psu = [1] * 4, [1, 1, 2, 2], [1, 2, 1, 2]
    a = SurveyDesign(weights, strata, psu).total([10, 30, 20, 40])
    b = SurveyDesign(weights, strata[::-1], psu[::-1]).total([40, 20, 30, 10])
    assert a == b
    assert a["standard_error"] == pytest.approx(math.sqrt(800))


def test_publication_precision_thresholds_and_logit_interval():
    # Two equally sized PSUs make mean SE = half their difference exactly.
    design = SurveyDesign(np.ones(40), np.ones(40, dtype=int), np.repeat([1, 2], 20))
    for cv, status, visible in [(10, "MEASURED", True), (15, "REVIEW", True),
                                (29, "REVIEW", True), (30, "REVIEW", False)]:
        result = design.ratio(np.repeat([100-cv, 100+cv], 20), np.ones(40))
        assert result["coefficient_variation"] == pytest.approx(cv)
        assert result["status"] == status
        assert (result["value"] is not None) == visible
    result = design.ratio(np.repeat([0.4, 0.6], 20), np.ones(40), percent=True)
    assert result["estimate"] == pytest.approx(50)
    assert result["standard_error"] == pytest.approx(10)
    assert 0 < result["ci_lower"] < 50 < result["ci_upper"] < 100
    expected = 100 / (1 + math.exp(Z90 * 0.1 / 0.25))
    assert result["ci_lower"] == pytest.approx(expected)
    assert result["ci_method"] == "logit_delta_normal_90"


@pytest.mark.parametrize("n,visible", [(29, False), (30, True)])
def test_sample_size_threshold(n, visible):
    design = SurveyDesign(np.ones(n), np.ones(n, dtype=int), np.arange(n))
    result = design.ratio(np.linspace(9, 11, n), np.ones(n))
    assert (result["value"] is not None) == visible
    assert result["sample_size"] == n


@pytest.mark.parametrize("proportion", [0, 1])
def test_boundary_proportion_is_not_exact_certainty(proportion):
    design = SurveyDesign(np.ones(40), np.ones(40, dtype=int), np.arange(40))
    result = design.ratio(np.repeat(proportion, 40), np.ones(40), percent=True)
    assert result["estimate"] == proportion * 100
    assert result["value"] is None
    assert result["ci_lower"] is None and result["ci_upper"] is None
    assert "proportion_boundary" in result["suppression_reason"]
    assert result["status"] == "REVIEW"


def test_empty_domain_and_zero_denominator_are_unknown():
    design = SurveyDesign([1, 1], [1, 1], [1, 2])
    total = design.total([0, 0])
    assert total["estimate"] == 0 and total["value"] is None
    assert total["coefficient_variation"] is None
    ratio = design.ratio([0, 0], [0, 0])
    assert ratio["estimate"] is None and ratio["standard_error"] is None
    assert ratio["status"] == "UNKNOWN"


def test_missing_income_excluded_only_through_explicit_domain():
    design = SurveyDesign([1, 1, 1], [1, 1, 1], [1, 2, 3])
    result = design.ratio([2, 4, np.nan], [1, 1, np.nan], [True, True, False])
    assert result["estimate"] == 3
    assert result["sample_size"] == 2
    assert result["weighted_denominator"] == 2
    with pytest.raises(ValueError, match="finite inside"):
        design.ratio([2, 4, np.nan], [1, 1, 1])


@pytest.mark.parametrize("weights", [[1, -1], [1, np.nan], [1, np.inf], [0, 1]])
def test_invalid_or_unaudited_weights_fail(weights):
    with pytest.raises(ValueError):
        SurveyDesign(weights, [1, 1], [1, 2])


def test_audited_zero_weights_do_not_inflate_sample_support():
    design = SurveyDesign([1, 0, 1], [1, 1, 1], [1, 1, 2], allow_zero_weights=True)
    result = design.ratio([2, 200, 4], [1, 1, 1])
    assert result["estimate"] == 3 and result["sample_size"] == 2
    assert result["zero_weight_count"] == 1
    with pytest.raises(ValueError, match="positive weight support"):
        SurveyDesign([1, 0], [1, 1], [1, 2], allow_zero_weights=True)


@pytest.mark.parametrize("strata,psu", [([1, None], [1, 2]), ([1, 1], [1, ""]),
                                         ([1], [1, 2]), ([1, np.nan], [1, 2])])
def test_invalid_design_identifiers_fail(strata, psu):
    with pytest.raises(ValueError):
        SurveyDesign([1, 1], strata, psu)


def test_invalid_domain_shape_and_ratio_bounds_fail():
    design = SurveyDesign([1, 1], [1, 1], [1, 2])
    for bad_domain in ([1, 0], [True], [True, None]):
        with pytest.raises(ValueError, match="boolean mask"):
            design.total([1, 1], bad_domain)
    with pytest.raises(ValueError, match="nonnegative"):
        design.ratio([1, 1], [-1, 1])
    with pytest.raises(ValueError, match="zero requires"):
        design.ratio([1, 1], [0, 1])
    with pytest.raises(ValueError, match="proportions require"):
        design.ratio([2, 1], [1, 1], percent=True)
    with pytest.raises(ValueError, match="full design"):
        design.total([1])


def test_caller_weight_mutation_cannot_change_design():
    weights = np.array([1.0, 1.0])
    design = SurveyDesign(weights, [1, 1], [1, 2])
    weights[:] = 100
    assert design.total([2, 4])["estimate"] == 6


def test_zero_mean_with_positive_variance_has_no_false_precision_grade():
    design = SurveyDesign(np.ones(40), np.ones(40, dtype=int), np.arange(40))
    result = design.ratio(np.tile([-1, 1], 20), np.ones(40))
    assert result["estimate"] == 0
    assert result["standard_error"] > 0
    assert result["coefficient_variation"] is None
    assert result["value"] is None
    assert result["status"] == "REVIEW"
    assert "undefined_cv_at_zero" in result["suppression_reason"]


def test_design_and_domain_support_are_distinct():
    design = SurveyDesign([1] * 40, [1] * 20 + [2] * 20, list(range(40)))
    denominator = [1] * 20 + [0] * 20
    result = design.ratio([2] * 20 + [0] * 20, denominator)
    assert result["n_psu_design"] == 40
    assert result["n_strata_design"] == 2
    assert result["design_df"] == 38
    assert result["n_psu_domain"] == 20
    assert result["n_strata_domain"] == 1


def test_two_domain_psus_count_even_when_numerator_zero():
    design = SurveyDesign([1] * 40, [1] * 40, [1] * 20 + [2] * 20)
    result = design.ratio([1] * 20 + [0] * 20, [1] * 40, percent=True)
    assert result["sample_size"] == 40
    assert result["n_psu_domain"] == 2
    assert result["n_strata_domain"] == 1
    assert result["value"] is None
    assert "cv_at_least_30" in result["suppression_reason"]


def test_support_failures_have_stable_order():
    design = SurveyDesign([1] * 40, [1] * 40, [1] * 20 + [2] * 20)
    result = design.ratio([0] * 40, [0] * 40)
    assert result["suppression_reason"] == (
        "zero_denominator;sample_size_below_30;fewer_than_two_domain_psus"
    )


def test_adjust_is_never_official_precision():
    design = SurveyDesign([1] * 40, [1] * 39 + [2], list(range(40)), singleton_policy="adjust")
    result = design.ratio([9, 11] * 20, [1] * 40)
    assert result["singleton_policy"] == "adjust"
    assert result["official_precision"] is False
    assert result["status"] == "REVIEW"
