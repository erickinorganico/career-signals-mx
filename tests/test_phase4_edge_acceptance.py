"""Exact Phase 4 edge acceptance over emitted public artifacts."""

from tests.phase4_prohibitions import run_prohibition_case


def test_public_suppression_control_computes_bad_then_clean():
    outcome = run_prohibition_case("suppressed")
    assert outcome["bad_rejected"] is True
    assert outcome["clean_accepted"] is True
