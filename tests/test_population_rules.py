"""Small synthetic rows test ENOE population boundaries without person data."""

import pytest

from brujula.populations import (
    COMPLETED_PROFESSIONAL_KNOWN_AGE,
    NATIONAL_15_PLUS_CONTEXT,
    POPULATION_DEFINITIONS,
    classify_eligibility,
    classify_income_state,
    normalize_cmpe_key,
    summarize_denominators,
    summarize_measure_denominator,
)


BASE = {"r_def": "00", "c_res": "1", "eda": "30", "cs_p13_1": "07",
        "cs_p16": "1", "cs_p14_c": "33100", "fac_tri": "2"}


def row(**changes):
    return {**BASE, **changes}


@pytest.mark.parametrize("code,expected", [("0", True), ("00", True), ("15", False), ("", False), ("  ", False), ("０", False), (0, False)])
def test_response_normalization_is_ascii_and_bounded(code, expected):
    assert classify_eligibility(row(r_def=code), NATIONAL_15_PLUS_CONTEXT)["eligible"] is expected


@pytest.mark.parametrize("code,expected", [("1", True), ("3", True), ("2", False), ("", False), ("4", False), ("１", False)])
def test_residency_codes(code, expected):
    assert classify_eligibility(row(c_res=code), NATIONAL_15_PLUS_CONTEXT)["eligible"] is expected


@pytest.mark.parametrize("age,national,cohort,unknown", [
    ("14", False, False, False), ("15", True, True, False),
    ("97", True, True, False), ("98", True, False, True),
    ("99", False, False, True), ("  ", False, False, True),
    ("abc", False, False, False),
])
def test_age_boundaries_and_operational_unknown(age, national, cohort, unknown):
    context = classify_eligibility(row(eda=age), NATIONAL_15_PLUS_CONTEXT)
    professional = classify_eligibility(row(eda=age), COMPLETED_PROFESSIONAL_KNOWN_AGE)
    assert (context["eligible"], professional["eligible"], context["age_unknown"]) == (national, cohort, unknown)
    assert professional["age_unknown"] is unknown


@pytest.mark.parametrize("education,completion,reason", [
    ("06", "1", "technical_education"), ("08", "1", "postgraduate_education"),
    ("09", "1", "postgraduate_education"), ("07", "2", "incomplete_education"),
    ("07", "9", "unknown_completion"), ("07", " ", "unknown_completion"),
    ("  ", "1", "unknown_education"), ("99", "1", "unknown_education"),
    ("-1", "1", "unknown_education"), ("00", "1", "other_education"),
    ("07", "x", "invalid_completion"),
])
def test_professional_exclusions_are_distinct(education, completion, reason):
    result = classify_eligibility(row(cs_p13_1=education, cs_p16=completion), COMPLETED_PROFESSIONAL_KNOWN_AGE)
    assert result["eligible"] is False and reason in result["exclusion_reasons"]


@pytest.mark.parametrize("age", ["-1", -1, "99", " "])
def test_missing_age_is_unknown_not_under_15(age):
    result = classify_eligibility(row(eda=age), COMPLETED_PROFESSIONAL_KNOWN_AGE)
    assert result["eligible"] is False
    assert "age_unknown" in result["exclusion_reasons"]
    assert "age_below_15" not in result["exclusion_reasons"]


@pytest.mark.parametrize("field", ["999999", " 999999", "", "  ", None, "３１３００"])
def test_unknown_field_is_visible_without_inventing_named_field(field):
    result = classify_eligibility(row(cs_p14_c=field), COMPLETED_PROFESSIONAL_KNOWN_AGE)
    assert result["eligible"] is True
    assert result["field_unknown"] is True
    assert result["exclusion_reasons"] == []


def test_definition_and_summary_keep_counts_and_weights_separate():
    assert set(POPULATION_DEFINITIONS) == {NATIONAL_15_PLUS_CONTEXT, COMPLETED_PROFESSIONAL_KNOWN_AGE}
    sample = [row(fac_tri="2"), row(eda="98", fac_tri="3"), row(cs_p13_1="08"), row(cs_p16="9"), row(r_def="15")]
    summary = summarize_denominators(sample, COMPLETED_PROFESSIONAL_KNOWN_AGE)
    assert summary["observed_rows_n"] == 5
    assert summary["valid_response_n"] == 4
    assert summary["observed_eligible_n"] == 1
    assert summary["weighted_eligible_denominator"] == 2
    assert summary["exclusion_counts"]["age_unknown"] == 1
    assert summary["exclusion_counts"]["postgraduate_education"] == 1
    assert summary["exclusion_counts"]["unknown_completion"] == 1
    assert summary["exclusion_counts"]["nonresponse"] == 1
    assert summarize_denominators([], NATIONAL_15_PLUS_CONTEXT)["weighted_eligible_denominator"] is None


def test_unknown_population_rejected():
    with pytest.raises(ValueError):
        classify_eligibility(BASE, "not_a_population")


CATALOG = ("31300", "32100", "33100")


@pytest.mark.parametrize("raw,expected", [
    ("31300", "031300"), (" 32100 ", "032100"), ("33100", "033100"),
    ("999999", None), (None, None), (" ", None), ("99999", None),
    ("３１３００", None), ("31300.0", None), (31300, None),
])
def test_cmpe_requires_supplied_period_catalog_and_ascii_digits(raw, expected):
    assert normalize_cmpe_key(raw, CATALOG) == expected


@pytest.mark.parametrize("keys", [(), ("31300", "031300"), ("31300", "abc"), ("999999",), (" 31300",)])
def test_bad_catalog_rejected(keys):
    with pytest.raises(ValueError):
        normalize_cmpe_key("31300", keys)


@pytest.mark.parametrize("ing7c,amount,state", [
    ("2", "1000", "positive_known"), ("6", "0", "no_income"),
    ("7", "0", "unspecified"), ("7", "", "unspecified"),
    ("2", "0", "amount_unknown"), ("2", "999999", "amount_unknown"),
    ("6", "1000", "conflicting"), ("7", "1000", "conflicting"),
    ("0", "0", "not_applicable"), ("", "0", "unknown_income_state"),
])
def test_income_sentinels_do_not_invent_zero_wage(ing7c, amount, state):
    result = classify_income_state(row(ing7c=ing7c, ingocup=amount))
    assert result["state"] == state
    assert result["positive_known"] is (state == "positive_known")
    assert result.get("income_amount") is None or state == "positive_known"


def test_measure_denominators_keep_employment_and_positive_income_distinct():
    rows = [
        row(clase2="1", ing7c="2", ingocup="100", fac_tri="2"),
        row(clase2="1", ing7c="6", ingocup="0", fac_tri="3"),
        row(clase2="1", ing7c="7", ingocup="0", fac_tri="4"),
        row(clase2="2", ing7c="0", ingocup="0", fac_tri="5"),
        row(clase2="4", ing7c="0", ingocup="0", fac_tri="6"),
    ]
    employment = summarize_measure_denominator(rows, "employment")
    income = summarize_measure_denominator(rows, "positive_known_income")
    assert employment["observed_valid_n"] == 5
    assert employment["observed_occupied_n"] == 3
    assert employment["weighted_denominator"] == 20
    assert income["observed_valid_n"] == 1
    assert income["weighted_denominator"] == 2
    assert income["excluded_counts"]["no_income"] == 1
    assert income["excluded_counts"]["unspecified"] == 1
    assert income["excluded_counts"]["not_occupied"] == 2
    assert summarize_measure_denominator([], "positive_known_income")["weighted_denominator"] is None
    assert summarize_measure_denominator([row(clase2="1", ing7c="7", ingocup="0")], "positive_known_income")["weighted_denominator"] is None


def test_weight_validation_and_finite_accumulation():
    assert summarize_measure_denominator([row(clase2="1", fac_tri="0.1"), row(clase2="1", fac_tri="0.2")], "employment")["weighted_denominator"] == pytest.approx(0.3)
    for invalid in (float("nan"), float("inf"), -1, True, "1e2", "１２", 0):
        with pytest.raises(ValueError):
            summarize_measure_denominator([row(clase2="1", fac_tri=invalid)], "employment")
    with pytest.raises(ValueError, match="overflow"):
        summarize_measure_denominator([row(clase2="1", fac_tri=1e308), row(clase2="1", fac_tri=1e308)], "employment")
