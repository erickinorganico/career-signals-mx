"""Fast official cell comparison controls, independent of the local workbook."""

from scripts.official_reconciliation import compare_official_cells


def test_six_exact_counts_and_rounding_boundary():
    official = {f"{geo}|{metric}": {"estimate": float(value), "standard_error": 10.0, "kind": "count"}
                for geo, values in {"mx": [102615200, 61065005, 1624245],
                                    "02": [3014248, 1790619, 41435]}.items()
                for metric, value in zip(("population_total", "pea_total", "unemployed_total"), values)}
    computed = {key: {"estimate": row["estimate"], "standard_error": 9.9} for key, row in official.items()}
    official["mx|unemployment_rate"] = {"estimate": 2.6599, "standard_error": 0.1, "kind": "rate"}
    computed["mx|unemployment_rate"] = {"estimate": 2.65995, "standard_error": 0.09}
    assert compare_official_cells(official, computed)["status"] == "PASS"
    computed["mx|unemployment_rate"]["estimate"] = 2.65995001
    assert compare_official_cells(official, computed)["status"] == "BLOCKED"
    assert compare_official_cells(official, {"mx|population_total": computed["mx|population_total"]})["status"] == "BLOCKED"
