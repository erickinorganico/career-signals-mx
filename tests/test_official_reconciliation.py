"""Fast official cell comparison controls, independent of the local workbook."""

import hashlib

import pytest

from brujula.official_reconciliation import (
    compare_official_cells, workbook_cells, reconcile, check_2026_pdf_benchmark,
)


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
    computed["mx|unemployment_rate"]["estimate"] = 2.65985
    assert compare_official_cells(official, computed)["status"] == "PASS"
    computed["mx|unemployment_rate"]["estimate"] = 2.65984999
    assert compare_official_cells(official, computed)["status"] == "BLOCKED"
    assert compare_official_cells(official, {"mx|population_total": computed["mx|population_total"]})["status"] == "BLOCKED"


def test_official_order_exact_count_and_nonfinite():
    official = {"mx|population_total": {"estimate": 10, "standard_error": 1, "kind": "count"},
                "02|population_total": {"estimate": 20, "standard_error": 2, "kind": "count"}}
    computed = {"02|population_total": {"estimate": 20, "standard_error": 1.9},
                "mx|population_total": {"estimate": 10, "standard_error": 0.9}}
    result = compare_official_cells(official, computed)
    assert result["status"] == "PASS"
    assert list(result["cells"]) == sorted(official)
    assert all(item["se_signed_difference"] < 0 for item in result["cells"].values())
    computed["mx|population_total"]["estimate"] = 10.000001
    assert compare_official_cells(official, computed)["status"] == "BLOCKED"
    computed["mx|population_total"]["estimate"] = float("inf")
    assert compare_official_cells(official, computed)["status"] == "BLOCKED"


def test_official_workbook_missing_or_bad_hash(tmp_path):
    with pytest.raises((ValueError, OSError)):
        workbook_cells(tmp_path / "missing.xlsx")
    fake = tmp_path / "wrong.xlsx"
    fake.write_bytes(b"wrong edition")
    with pytest.raises(ValueError, match="SHA-256"):
        workbook_cells(fake)


def test_official_source_hash_and_pdf_hash_fail_closed(monkeypatch, tmp_path):
    from brujula import official_reconciliation as official

    source = tmp_path / "source.zip"
    source.write_bytes(b"synthetic source")
    monkeypatch.setattr(official, "resolve_snapshot", lambda *args: (source, {"sha256": "bad"}))
    monkeypatch.setattr(official, "inventory_snapshot", lambda *args: {"raw_sha256": "bad"})
    with pytest.raises(ValueError, match="source SHA-256"):
        reconcile(tmp_path, tmp_path / "workbook.xlsx", [])
    pdf = tmp_path / "wrong.pdf"
    pdf.write_bytes(b"wrong edition")
    with pytest.raises(ValueError, match="PDF SHA-256"):
        check_2026_pdf_benchmark(pdf, [])


@pytest.mark.parametrize("mutation", ["period_id", "occupation_id", "industry_id", "method_id"])
def test_official_wrong_period_universe_or_method_fails(monkeypatch, tmp_path, mutation):
    from brujula import official_reconciliation as official

    source = tmp_path / "source.zip"
    source.write_bytes(b"synthetic source")
    monkeypatch.setattr(official, "resolve_snapshot", lambda *args: (source, {"sha256": official.SOURCE_SHA256}))
    monkeypatch.setattr(official, "inventory_snapshot", lambda *args: {"raw_sha256": official.SOURCE_SHA256})
    monkeypatch.setattr(official, "workbook_cells", lambda *args: {})
    row = {"source_snapshot_id": official.SNAPSHOT, "population_id": "national_15_plus_context",
           "field_of_study_id": "all", "recorded_sex_id": "all", "geography_id": "mx",
           "period_id": "2025-Q2", "occupation_id": "all", "industry_id": "all",
           "method_id": official.METHOD_ID, "metric_id": "population_total", "estimate": 1,
           "precision": {"standard_error": 1}}
    row[mutation] = "wrong"
    with pytest.raises(ValueError, match="period, universe or method"):
        reconcile(tmp_path, tmp_path / "workbook.xlsx", [row])


def test_pdf_duplicate_metric_fails(monkeypatch, tmp_path):
    from brujula import official_reconciliation as official

    pdf = tmp_path / "synthetic.pdf"
    pdf.write_bytes(b"disposable synthetic PDF bytes")
    monkeypatch.setattr(official, "PDF_2026_Q2_SHA256", hashlib.sha256(pdf.read_bytes()).hexdigest())
    row = {"source_snapshot_id": "enoe_2026_q2", "population_id": "national_15_plus_context",
           "field_of_study_id": "all", "recorded_sex_id": "all", "geography_id": "mx",
           "period_id": "2026-Q2", "occupation_id": "all", "industry_id": "all",
           "method_id": official.METHOD_ID, "metric_id": "population_total", "estimate": 1}
    with pytest.raises(ValueError, match="duplicate"):
        check_2026_pdf_benchmark(pdf, [row, row])
