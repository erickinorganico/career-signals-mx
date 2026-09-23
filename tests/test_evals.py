import json
from pathlib import Path

import pytest

from evals.run import run_evals


ROOT = Path(__file__).parents[1]
CASES = ROOT / "evals" / "cases.json"


def test_fixed_eval_suite_has_zero_critical_violations():
    result = run_evals(CASES)
    assert result["receipt"] == {
        "suite_id": "brujula_claim_authority_v1",
        "eval_version": "1.0",
        "status": "PASS",
        "case_count": 12,
        "passed_count": 12,
        "critical_violations": [],
    }


def test_eval_suite_covers_required_failure_modes():
    payload = json.loads(CASES.read_text(encoding="utf-8"))
    mutations = {case["mutation"] for case in payload["cases"]}
    assert {
        "false_zero", "invented_numeric", "concept_confusion", "vacancy_claim", "evidence_orphan",
        "evidence_incongruent", "method_mismatch", "comparison_claim_v1", "causal_claim",
        "instruction_like_input", "no_match",
    } <= mutations


def test_eval_result_is_deterministic():
    assert run_evals(CASES) == run_evals(CASES)


def test_unknown_eval_mutation_fails_closed(tmp_path):
    payload = json.loads(CASES.read_text(encoding="utf-8"))
    payload["cases"][0]["mutation"] = "call_a_model"
    target = tmp_path / "cases.json"
    target.write_text(json.dumps(payload), encoding="utf-8")
    with pytest.raises(ValueError, match="unknown eval mutation"):
        run_evals(target)
