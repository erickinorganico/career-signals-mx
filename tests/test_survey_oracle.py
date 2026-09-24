"""Fast aggregate-only checks; the real R gate is run by acceptance."""

import pytest

from scripts.accept_enoe_estimates import compare_oracle_cases


def test_oracle_signed_errors_and_order():
    expected = [{"id": "a", "estimate": 100.0, "standard_error": 5.0},
                {"id": "b", "estimate": 20.0, "standard_error": 2.0}]
    actual = list(reversed(expected))
    result = compare_oracle_cases(expected, actual)
    assert result["status"] == "PASS"
    assert list(result["cases"]) == ["a", "b"]
    assert result["cases"]["a"]["point_signed_difference"] == 0


@pytest.mark.parametrize("actual", [[], [{"id": "a", "estimate": 100, "standard_error": 5}] * 2,
                                      [{"id": "a", "estimate": float("nan"), "standard_error": 5}]])
def test_oracle_missing_duplicate_nonfinite_fails(actual):
    expected = [{"id": "a", "estimate": 100, "standard_error": 5}]
    assert compare_oracle_cases(expected, actual)["status"] == "BLOCKED"


def test_oracle_tolerance_neighbor_and_signed_precision():
    expected = [{"id": "a", "estimate": 100, "standard_error": 5}]
    accepted = [{"id": "a", "estimate": 100 + 0.9e-8, "standard_error": 5 - 0.9e-8}]
    rejected = [{"id": "a", "estimate": 100 + 2.1e-8, "standard_error": 5 - 2.1e-8}]
    assert compare_oracle_cases(expected, accepted)["status"] == "PASS"
    result = compare_oracle_cases(expected, rejected)
    assert result["status"] == "BLOCKED"
    assert result["cases"]["a"]["point_signed_difference"] > 0
    assert result["cases"]["a"]["se_signed_difference"] < 0


def test_oracle_relative_tolerance_and_duplicate_expected():
    expected = [{"id": "large", "estimate": 1_000_000_000.0, "standard_error": 1_000_000.0}]
    inside = [{"id": "large", "estimate": 1_000_000_000.09, "standard_error": 1_000_000.00009}]
    outside = [{"id": "large", "estimate": 1_000_000_000.11, "standard_error": 1_000_000.00011}]
    assert compare_oracle_cases(expected, inside)["status"] == "PASS"
    assert compare_oracle_cases(expected, outside)["status"] == "BLOCKED"
    assert compare_oracle_cases(expected * 2, inside)["status"] == "BLOCKED"
