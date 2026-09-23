"""Computed Phase 3 sparse-profile and professional-label controls."""

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tests"))

from brujula.analysis_v2 import STATE_CODES, SEX_CODES, build_profiles, index_public_estimates
from brujula.estimates import FOCAL_FIELDS
from brujula.populations import (COMPLETED_PROFESSIONAL_KNOWN_AGE,
                                  NATIONAL_15_PLUS_CONTEXT, POPULATION_DEFINITIONS)
from brujula.source_inventory import PERIODS
from test_analysis_v2 import synthetic_inputs


class _Patch:
    @staticmethod
    def setattr(obj, name, value):
        setattr(obj, name, value)


def check_sparse(packet):
    states, sexes = packet["latest_states"], packet["latest_recorded_sexes"]
    fields = ("all", *FOCAL_FIELDS)
    assert len(states) == len(fields) * len(STATE_CODES)
    assert len(sexes) == len(fields) * len(SEX_CODES)
    for field in fields:
        selected_states = [row for row in states if row["field_of_study_id"] == field]
        selected_sexes = [row for row in sexes if row["field_of_study_id"] == field]
        assert [row["geography_id"] for row in selected_states] == list(STATE_CODES)
        assert [row["recorded_sex_id"] for row in selected_sexes] == list(SEX_CODES)
    for row in states + sexes + packet["latest_fields"]:
        assert row["value"] is None and row["reason"] == "unknown"
        assert row["weighted_denominator_estimate"] is None
        assert row["support"]["weighted_support_total"] is None
        assert all(row["precision"][name] is None for name in
                   ("standard_error", "coefficient_variation", "ci90_lower", "ci90_upper"))


def check_cohort(packet):
    labels = packet["population_labels"]
    assert labels[COMPLETED_PROFESSIONAL_KNOWN_AGE] == POPULATION_DEFINITIONS[
        COMPLETED_PROFESSIONAL_KNOWN_AGE]["label"]
    assert labels[NATIONAL_15_PLUS_CONTEXT] == POPULATION_DEFINITIONS[
        NATIONAL_15_PLUS_CONTEXT]["label"]
    assert labels[COMPLETED_PROFESSIONAL_KNOWN_AGE] != labels[NATIONAL_15_PLUS_CONTEXT]
    assert len(packet["national"]) == len(PERIODS) * 5
    assert {row["population_id"] for row in packet["national"]} == {
        COMPLETED_PROFESSIONAL_KNOWN_AGE, NATIONAL_15_PLUS_CONTEXT}


def main(case: str, subject_path: str) -> None:
    subject = json.loads((ROOT / subject_path).read_text(encoding="utf-8"))
    assert subject["synthetic"] is True
    assert subject["case"] in ("clean", "p1", "p2")
    public, acceptance = synthetic_inputs(_Patch())
    index = index_public_estimates(public, acceptance)
    packet = build_profiles(index, acceptance["audits"], latest_period_id=PERIODS[-1])
    assert packet["synthetic"] is True
    # Mutate only after the actual APIs produced the packet. Clean subject is
    # byte-for-byte untouched; an env variable alone cannot make a test red.
    if subject["case"] == case == "p1":
        if subject["mutation"] == "delete_sparse_state":
            packet["latest_states"].pop(0)
        elif subject["mutation"] == "zero_sparse_state":
            packet["latest_states"][0]["value"] = 0
        else:
            raise ValueError("unknown sparse mutation")
    if subject["case"] == case == "p2":
        if subject["mutation"] != "all_graduates_label":
            raise ValueError("unknown cohort mutation")
        packet["population_labels"][COMPLETED_PROFESSIONAL_KNOWN_AGE] = "All graduates"
    {"p1": check_sparse, "p2": check_cohort}[case](packet)
    print("checked computed Phase 3 profiles and population definitions")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
