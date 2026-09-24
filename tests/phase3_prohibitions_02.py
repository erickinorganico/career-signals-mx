"""Content-dependent comparison prohibition checks over real public APIs."""

import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from brujula.comparisons_v2 import (build_comparison_ledger, compare_public_records,
                                    load_definition_registry)


def _item(period: str, metric: str, value: float, registry: dict) -> dict:
    snapshot = "enoe_" + period.lower().replace("-", "_")
    definition = registry["metrics"][metric]
    row = {"source_snapshot_id": snapshot,
           "population_id": "completed_professional_known_age",
           "field_of_study_id": "031300", "occupation_id": "all", "industry_id": "all",
           "geography_id": "mx", "recorded_sex_id": "all", "period_id": period,
           "metric_id": metric, "method_id": "enoe_taylor_project_adjust",
           "method_version": registry["method_version"], "design_id": registry["design_id"],
           "unit": definition["unit"], "price_basis": definition["price_basis"],
           "status": "REVIEW", "value": value, "reason": "synthetic_fixture",
           "precision": {"method": registry["precision_method"],
                         "ci_method": "normal_wald_90", "singleton_policy": "adjust",
                         "official_precision": False},
           "evidence_refs": [snapshot + "_custody"], "synthetic": True}
    grain = tuple(row[key] for key in registry["grain"])
    record_id = "v2r:" + hashlib.sha256(json.dumps(list(grain), sort_keys=True,
                        ensure_ascii=False, separators=(",", ":")).encode()).hexdigest()
    return {"record_id": record_id, "grain": grain, "record": row,
            "snapshot_sha256": registry["snapshots"][snapshot]["raw_sha256"],
            "method_version": row["method_version"]}


def _computed_subject() -> tuple[dict, list[dict]]:
    registry = load_definition_registry()
    records = [_item(period, metric, (10000 + i * 100) if metric == "positive_income_mean" else (50 + i), registry)
               for metric in ("positive_income_mean", "employment_rate")
               for i, period in enumerate(registry["periods"])]
    profiles = {"periods": list(reversed(registry["periods"])),
                "metric_ids": ["positive_income_mean", "employment_rate"],
                "national": [{"record_id": item["record_id"], **item["record"]} for item in records],
                "latest_states": [], "latest_recorded_sexes": [],
                "record_index": {item["record_id"]: item for item in records},
                "synthetic": True}
    ledger = build_comparison_ledger(profiles, registry=registry)
    pair = [item for item in records if item["record"]["metric_id"] == "positive_income_mean"
            and item["record"]["period_id"] in ("2025-Q2", "2025-Q3")]
    income = compare_public_records(pair[0], pair[1], registry=registry)
    assert income["comparable"] and income["absolute_change"] == 100
    assert len(ledger) == 22 and all(entry["comparable"] for entry in ledger)
    return income, ledger


def _check_income(income: dict, ledger: list[dict]) -> None:
    assert income["display_unit"] == "nominal MXN/month"
    assert income["absolute_change"] == 100
    income_entries = [entry for entry in ledger if entry["display_unit"] == "nominal MXN/month"]
    assert len(income_entries) == 11
    assert all(entry["display_unit"] == "nominal MXN/month" for entry in income_entries)
    assert not any(entry["comparable"] and "minimum_wage_band" in json.dumps(entry)
                   for entry in ledger)
    assert "purchasing-power" not in json.dumps((income, ledger)).lower()


def _check_overlap(ledger: list[dict]) -> None:
    assert len(ledger) == 22
    assert {entry["comparison_type"] for entry in ledger} == {"adjacent_quarter", "like_quarter_annual"}
    forbidden = {"combined_sample_size", "distinct_person_sum", "change_standard_error",
                 "delta_standard_error", "change_ci90", "delta_confidence_interval",
                 "p_value", "significant", "statistical_significance"}
    assert all(not forbidden.intersection(entry) for entry in ledger)
    assert all("quarterly_samples_may_overlap" in entry["limitations"] for entry in ledger)
    assert all("seasonality_qoq" in entry["limitations"] for entry in ledger
               if entry["comparison_type"] == "adjacent_quarter")


def main(case: str, subject_path: str) -> None:
    subject = json.loads((ROOT / subject_path).read_text(encoding="utf-8"))
    assert subject["synthetic"] is True and subject["case"] in ("clean", "p3", "p4")
    income, ledger = _computed_subject()
    if subject["case"] == case == "p3":
        assert subject["mutation"] == "purchasing_power_label"
        income["display_unit"] = "purchasing-power MXN/month"
    if subject["case"] == case == "p4":
        assert subject["mutation"] == "delta_standard_error"
        ledger[0]["change_standard_error"] = 1.25
    {"p3": lambda: _check_income(income, ledger),
     "p4": lambda: _check_overlap(ledger)}[case]()
    print("checked computed Phase 3 comparison ledger (synthetic fixture)")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
