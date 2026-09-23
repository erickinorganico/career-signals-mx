"""Small synthetic rows test ENOE population boundaries without person data."""

import pytest

from brujula.populations import (
    COMPLETED_PROFESSIONAL_KNOWN_AGE,
    NATIONAL_15_PLUS_CONTEXT,
    POPULATION_DEFINITIONS,
    classify_eligibility,
    summarize_denominators,
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
    ("  ", "1", "unknown_education"), ("07", "x", "invalid_completion"),
])
def test_professional_exclusions_are_distinct(education, completion, reason):
    result = classify_eligibility(row(cs_p13_1=education, cs_p16=completion), COMPLETED_PROFESSIONAL_KNOWN_AGE)
    assert result["eligible"] is False and reason in result["exclusion_reasons"]


def test_unknown_field_is_visible_without_inventing_named_field():
    result = classify_eligibility(row(cs_p14_c="999999"), COMPLETED_PROFESSIONAL_KNOWN_AGE)
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
