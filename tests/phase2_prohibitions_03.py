"""Executable Phase 2 numerical prohibitions with content-dependent bad subjects."""

import json
import sys
import hashlib
from dataclasses import replace
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scripts.accept_enoe_estimates import compare_oracle_cases, quarter_claim_guard, run_attempt
from scripts.official_reconciliation import compare_official_cells
from brujula import estimates
from test_estimates import synthetic_frame


def p5(mutation):
    golden = json.loads((ROOT / "data/fixtures/enoe-aggregate-golden.json").read_text(encoding="utf-8"))
    prior = golden["official_cells"]
    official = {key: {"estimate": cell["official_estimate"],
                      "standard_error": cell["official_standard_error"], "kind": cell["kind"]}
                for key, cell in prior.items()}
    computed = {key: {"estimate": cell["project_estimate"],
                      "standard_error": cell["project_standard_error"]}
                for key, cell in prior.items()}
    ledger = compare_official_cells(official, computed)
    assert ledger["status"] == "PASS" and ledger["cells"] == prior
    py_r = compare_oracle_cases([{"id": "control", "estimate": 100, "standard_error": 5}],
                                [{"id": "control", "estimate": 100, "standard_error": 5}])
    assert py_r["status"] == "PASS"
    if mutation == "erase_official_discrepancy":
        ledger["cells"]["mx|population_total"]["se_signed_difference"] = 0
    if mutation == "promote_official_precision":
        ledger["cells"]["mx|population_total"]["official_precision"] = True
    assert ledger["cells"]["mx|population_total"]["se_signed_difference"] != 0
    assert all(cell["official_precision"] is False for cell in ledger["cells"].values())
    assert golden["national_population_se_relative_difference"] != 0


def p6(mutation):
    # Compute two disposable synthetic quarter payloads through the estimator.
    quarters = []
    for snapshot, period in (("enoe_2025_q1", "2025-Q1"), ("enoe_2025_q2", "2025-Q2")):
        frame = replace(synthetic_frame(), snapshot_id=snapshot, period=period)
        domain = [{"population_id": "completed_professional_known_age", "field_of_study_id": "033100",
                   "geography_id": "mx", "recorded_sex_id": "all"}]
        with TemporaryDirectory() as temporary, patch.object(estimates, "load_snapshot_frame",
                 return_value=(frame, {"synthetic": True, "provenance": frame.provenance})):
            output = estimates.estimate_snapshot(snapshot, Path(temporary), domains=domain)
        encoded = json.dumps(output["public"], sort_keys=True, allow_nan=False).encode("utf-8")
        quarters.append({"snapshot_id": snapshot, "numeric_digest": hashlib.sha256(encoded).hexdigest()})
    ledger = quarter_claim_guard(quarters)
    if mutation == "sum_as_distinct_people":
        ledger["distinct_people_8q"] = 210
    elif mutation == "independent_significance":
        ledger["independent_quarter_significance"] = True
    assert ledger["no_distinct_person_sum"] and ledger["no_independent_quarter_significance"]
    assert "distinct_people_8q" not in ledger
    assert "independent_quarter_significance" not in ledger


def p7(mutation):
    with TemporaryDirectory() as temporary:
        root = Path(temporary)
        assert run_attempt(root, lambda: {"status": "PASS", "numeric_content_digest": "old"})["status"] == "PASS"
        def numerical_failure():
            raise ValueError("injected numerical failure")
        assert run_attempt(root, numerical_failure)["status"] == "BLOCKED"
        current = json.loads((root / "current.json").read_text(encoding="utf-8"))
        if mutation == "reuse_old_success":
            current = {"status": "PASS", "numeric_content_digest": "old"}
        assert current["status"] == "BLOCKED"
        assert current.get("numeric_content_digest") is None


if __name__ == "__main__":
    case = sys.argv[1]
    subject = json.loads((ROOT / sys.argv[2]).read_text(encoding="utf-8"))
    if case not in {"p5", "p6", "p7"} or subject["case"] not in {"clean", "p5", "p6", "p7"}:
        raise ValueError("invalid numerical prohibition subject")
    {"p5": p5, "p6": p6, "p7": p7}[case](subject["mutation"] if subject["case"] == case else None)
    print("checked computed numerical acceptance and failure state")
