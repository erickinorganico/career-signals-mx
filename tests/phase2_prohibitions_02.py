"""Computed Phase 2 precision and public suppression negative controls."""

import json
import sys
from dataclasses import replace
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(Path(__file__).parent))

from brujula import estimates
from brujula.enoe_adapter import Frame
from brujula.research_contract import validate_public_research_v2, validate_research_v2
from brujula.survey import SurveyDesign
from test_estimates import synthetic_frame


def _computed(*, singleton=False, sex="all"):
    frame = synthetic_frame()
    if singleton:
        columns = dict(frame.columns)
        columns["est_d_tri"] = columns["est_d_tri"].copy()
        columns["est_d_tri"][1:] = "2"
        columns["est_d_tri"].flags.writeable = False
        frame = replace(frame, columns=columns)
    domain = {"population_id": "completed_professional_known_age", "field_of_study_id": "033100",
              "geography_id": "mx", "recorded_sex_id": sex}
    with TemporaryDirectory() as tmp, patch.object(estimates, "load_snapshot_frame",
                                                  return_value=(frame, {"synthetic": True, "provenance": frame.provenance})):
        return estimates.estimate_snapshot(frame.snapshot_id, Path(tmp), domains=[domain])


def p3(mutation):
    # The engine is also checked directly so an assembler mutation cannot
    # mask its policy. The cell is a genuinely supported computed estimate.
    design = SurveyDesign([1] * 40, [1] + [2] * 39, list(range(40)), singleton_policy="adjust")
    result = design.ratio([0, 1] * 20, [1] * 40, percent=True)
    assert result["value"] is not None and result["status"] == "REVIEW"
    assert result["official_precision"] is False
    output = _computed(singleton=True)
    row = next(row for row in output["internal"]["records"] if row["metric_id"] == "employment_rate")
    assert row["value"] is not None and row["status"] == "REVIEW"
    assert row["precision"]["singleton_policy"] == "adjust"
    if mutation == "promote_official":
        row["status"] = "MEASURED"
        row["precision"]["official_precision"] = True
        assert {failure["id"] for failure in validate_research_v2(output["internal"])} & {
            "singleton_precision", "synthetic_status"
        }
    assert row["status"] == "REVIEW" and row["precision"]["official_precision"] is False
    assert validate_research_v2(output["internal"]) == []


def p4(mutation):
    output = _computed(sex="1")
    internal = next(row for row in output["internal"]["records"] if row["metric_id"] == "population_total")
    public = next(row for row in output["public"]["records"] if row["metric_id"] == "population_total")
    assert internal["value"] is None and internal["estimate"] == 20
    assert internal["weighted_denominator"] == internal["estimate"]
    assert internal["support"]["weighted_support_total"] == internal["estimate"]
    assert internal["precision"]["ci90_lower"] != internal["estimate"]
    if mutation == "leak_support":
        public["support"]["weighted_support_total"] = internal["estimate"]
    elif mutation == "leak_interval":
        public["precision"]["ci90_lower"] = internal["precision"]["ci90_lower"]
    if mutation is not None:
        assert "suppression" in {failure["id"] for failure in validate_public_research_v2(output["public"])}
    serialized = json.loads(json.dumps(output["public"], allow_nan=False))
    for row in serialized["records"]:
        if row["value"] is None:
            assert row["weighted_denominator"] is None
            assert row["support"]["weighted_support_total"] is None
            assert all(row["precision"][name] is None for name in
                       ("standard_error", "coefficient_variation", "ci90_lower", "ci90_upper"))
    assert validate_public_research_v2(serialized) == []


if __name__ == "__main__":
    case = sys.argv[1]
    subject = json.loads((ROOT / sys.argv[2]).read_text(encoding="utf-8"))
    assert subject["case"] in ("clean", "p3", "p4")
    assert subject["mutation"] in (None, "promote_official", "leak_support", "leak_interval")
    {"p3": p3, "p4": p4}[case](subject["mutation"] if subject["case"] == case else None)
    print("checked computed Phase 2 precision and public projection")
