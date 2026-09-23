"""Executable Phase 1 must-NOT controls over current APIs and synthetic inputs.

Each subject selects one mutation of a freshly computed API result. The bad
subjects demonstrate that the assertions detect the prohibited output; they
are never fed to a production path or mistaken for official observations.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from tempfile import TemporaryDirectory

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(Path(__file__).parent))

from brujula.populations import (
    COMPLETED_PROFESSIONAL_KNOWN_AGE, NATIONAL_15_PLUS_CONTEXT,
    POPULATION_DEFINITIONS, classify_eligibility, classify_income_state,
    normalize_cmpe_key, summarize_denominators, summarize_measure_denominator,
)
from brujula.research_contract import (
    public_research_projection, validate_research_v2, validate_public_research_v2,
)
from brujula.source_inventory import inventory_all

from test_research_contract import research_fixture  # synthetic fixture only
from test_source_inventory import _cache  # tiny synthetic ZIPs only


def _ids(payload):
    return {item["id"] for item in validate_research_v2(payload)}


def p1(mutation):
    with TemporaryDirectory() as directory:
        root, registry = _cache(Path(directory))
        items = inventory_all(root, registry)
        receipt = json.loads((root / "acquisitions" / items[0]["snapshot_id"] / "current.json").read_text())
    if mutation == "publish_receipt":
        items[0]["microdata_publication_approved"] = True
        receipt["numerical_findings_approved"] = True
    assert len(items) == 8 and receipt["status"] == "SUCCEEDED"
    assert all(item["microdata_publication_approved"] is False for item in items)
    assert not receipt.get("numerical_findings_approved", False)
    assert all("observations" not in item and "numerical_findings" not in item for item in items)


def p2(mutation):
    with TemporaryDirectory() as directory:
        root, registry = _cache(Path(directory))
        items = inventory_all(root, registry)
    if mutation == "erase_corrections_and_approve_alias":
        items[0]["revisions"]["count"] = 0
        items[4]["concept_equivalence_review"] = "APPROVED"
    assert [item["revisions"]["count"] for item in items[:2]] == [4, 9]
    assert [item["geography_header"] for item in items] == ["ENT"] * 4 + ["CVE_ENT"] * 4
    assert all(item["concept_equivalence_review"] == "REVIEW" for item in items)


def _person(**overrides):
    row = {"r_def": "00", "c_res": "1", "eda": "30", "cs_p13_1": "07",
           "cs_p16": "1", "cs_p14_c": "033100", "fac_tri": "2",
           "clase2": "1", "ing7c": "1", "ingocup": "100"}
    row.update(overrides)
    return row


def p3(mutation):
    cohort = COMPLETED_PROFESSIONAL_KNOWN_AGE
    findings = {
        "completed": classify_eligibility(_person(), cohort),
        "postgraduate": classify_eligibility(_person(cs_p13_1="08"), cohort),
        "unknown": classify_eligibility(_person(cs_p13_1=""), cohort),
        "incomplete": classify_eligibility(_person(cs_p16="2"), cohort),
    }
    label = POPULATION_DEFINITIONS[cohort]["label"]
    if mutation == "fold_other_education":
        findings["postgraduate"]["eligible"] = True
        findings["unknown"]["eligible"] = True
        label = "Everyone who ever attended licenciatura"
    assert findings["completed"]["eligible"]
    assert not findings["postgraduate"]["eligible"] and "postgraduate_education" in findings["postgraduate"]["exclusion_reasons"]
    assert not findings["unknown"]["eligible"] and "unknown_education" in findings["unknown"]["exclusion_reasons"]
    assert not findings["incomplete"]["eligible"]
    assert "completed" in label.lower() and "ever attended" not in label.lower()


def p4(mutation):
    cohort = COMPLETED_PROFESSIONAL_KNOWN_AGE
    missing_age = classify_eligibility(_person(eda=""), cohort)
    missing_field = classify_eligibility(_person(cs_p14_c=""), cohort)
    denominator = summarize_denominators([_person(cs_p14_c="")], cohort)
    income = classify_income_state(_person(ing7c="7", ingocup="999999"))
    measure = summarize_measure_denominator([_person(ing7c="7", ingocup="999999")], "positive_known_income")
    field_key = normalize_cmpe_key("", {"33100"})
    if mutation == "impute_missing_zero":
        missing_age["eligible"] = True
        missing_field["field_unknown"] = False
        denominator["unknown_field_eligible_n"] = 0
        income["positive_known"] = True
        measure["observed_valid_n"] = 1
        field_key = "033100"
    assert not missing_age["eligible"] and "age_unknown" in missing_age["exclusion_reasons"]
    assert missing_field["eligible"] and missing_field["field_unknown"]
    assert denominator["unknown_field_eligible_n"] == 1
    assert income["state"] == "unspecified" and not income["positive_known"]
    assert measure["observed_valid_n"] == 0 and measure["weighted_denominator"] is None
    assert field_key is None


def p5(mutation):
    payload = research_fixture()
    record = payload["records"][0]
    record.update(status="REVIEW", reason="Project singleton adjustment")
    record["precision"].update(singleton_policy="adjust", official_precision=False)
    assert validate_research_v2(payload) == []
    projected = public_research_projection(payload)["records"][0]
    record["precision"]["official_precision"] = True
    official_errors = _ids(payload)
    record["precision"]["official_precision"] = False
    record["sample_size"] = 1
    diagnostic_errors = _ids(payload)
    if mutation == "declare_singleton_official_and_activate_diagnostic":
        official_errors.discard("singleton_precision")
        diagnostic_errors.discard("precision_gate")
        projected["precision"]["official_precision"] = True
    assert "singleton_precision" in official_errors
    assert "precision_gate" in diagnostic_errors
    assert projected["status"] == "REVIEW" and projected["precision"]["official_precision"] is False


def p6(mutation):
    synthetic = research_fixture()
    synthetic_public = public_research_projection(synthetic)["records"][0]
    synthetic["records"][0].update(status="MEASURED", reason=None)
    synthetic_errors = _ids(synthetic)
    suppressed = research_fixture()
    suppressed["records"][0].update(status="UNKNOWN", reason="unknown", value=None)
    assert validate_research_v2(suppressed) == []
    public = public_research_projection(suppressed)
    null_record = public["records"][0]
    if mutation == "promote_and_leak_suppressed":
        synthetic_errors.discard("synthetic_status")
        synthetic_errors.discard("schema")
        synthetic_public["status"] = "MEASURED"
        null_record["status"] = "MEASURED"
        null_record["value"] = 120.0
        null_record["precision"]["standard_error"] = 3.0
    assert synthetic_errors & {"schema", "synthetic_status"}
    assert synthetic_public["status"] == "REVIEW" and synthetic_public["synthetic"]
    assert null_record["status"] == "UNKNOWN" and null_record["value"] is None
    assert null_record["precision"]["standard_error"] is None
    assert validate_public_research_v2(public) == []


CASES = {f"p{number}": globals()[f"p{number}"] for number in range(1, 7)}


def main():
    case, subject_path = sys.argv[1:]
    subject = json.loads(Path(subject_path).read_text(encoding="utf-8"))
    assert subject["case"] == case
    CASES[case](subject["mutation"])
    print(f"checked actual Phase 1 API: {case}")


if __name__ == "__main__":
    main()
