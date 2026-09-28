"""Meaningful checks for exact public-row selection and missing-value display."""

import csv
import hashlib
import json
from pathlib import Path

import pytest

from scripts.site_charts import FIELDS, METRICS, render_charts


def _write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as output:
        writer = csv.DictWriter(output, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def _stage(tmp_path: Path, *, gap: bool = False) -> Path:
    exports = tmp_path / "research" / "exports"
    exports.mkdir(parents=True)
    rows = []
    links = []
    periods = [f"{year}-Q{quarter}" for year, quarter in
               ((2024, 3), (2024, 4), (2025, 1), (2025, 2), (2025, 3), (2025, 4), (2026, 1), (2026, 2))]
    for metric, _, unit in METRICS:
        for field, name, _ in FIELDS:
            for index, period in enumerate(periods):
                record_id = f"trend-{metric}-{field}-{period}"
                missing = gap and metric == "employment_rate" and field == "033100" and index == 3
                value = 75.86 if metric == "employment_rate" and field == "033100" and index == 7 else (18000 + index * 100 if unit == "MXN/mes" else 65 + index)
                rows.append({"record_id": record_id, "population_id": "completed_professional_known_age",
                             "field_of_study_id": field, "field_label": name, "geography_id": "mx",
                             "geography_label": "México", "period_id": period, "metric_id": metric,
                             "value": "" if missing else str(value),
                             "ci90_lower": "" if missing else str(value-2),
                             "ci90_upper": "" if missing else str(value+2), "status": "REVIEW"})
                links.append({"figure_id": "figure:eight-quarter-trends", "record_id": record_id})
    for code in range(1, 33):
        record_id = f"state-{code:02d}"
        rows.append({"record_id": record_id, "population_id": "completed_professional_known_age",
                     "field_of_study_id": "033100", "field_label": "Derecho", "geography_id": f"{code:02d}",
                     "geography_label": f"Estado {code:02d}", "period_id": "2026-Q2", "metric_id": "employment_rate",
                     "value": "" if gap and code == 12 else "75.86", "ci90_lower": "" if gap and code == 12 else "74",
                     "ci90_upper": "" if gap and code == 12 else "77.6", "status": "REVIEW"})
        links.append({"figure_id": "figure:state-availability", "record_id": record_id})
    rows.append({"record_id": "unlinked", "population_id": "other", "field_of_study_id": "other",
                 "field_label": "Other", "geography_id": "mx", "geography_label": "México",
                 "period_id": "2026-Q2", "metric_id": "employment_rate", "value": "99999",
                 "ci90_lower": "99998", "ci90_upper": "99999", "status": "REVIEW"})
    for row in rows:
        row["recorded_sex_id"] = "all"
    _write_csv(exports / "public-records.csv", rows)
    _write_csv(exports / "figure-record-links.csv", links)
    return tmp_path


def test_exact_linked_rows_and_original_values(tmp_path):
    stage = _stage(tmp_path)
    result = render_charts(stage)
    trace = json.loads((stage / "charts/chart-data.json").read_text(encoding="utf-8"))
    assert len(trace["figures"]["figure:eight-quarter-trends"]) == 72
    assert len(trace["figures"]["figure:state-availability"]) == 32
    assert "unlinked" not in json.dumps(trace)
    assert trace["figures"]["figure:eight-quarter-trends"][0]["value"] == "65"
    assert trace["source_sha256"]["public-records.csv"] == hashlib.sha256(
        (stage / "research/exports/public-records.csv").read_bytes()).hexdigest()
    assert len(list((stage / "charts").glob("trend-*.svg"))) == 9
    assert len(list((stage / "charts").glob("territory-*.svg"))) == 2
    assert "75.86 %" in result["hero_markup"]
    assert "Ver los 32 registros" in result["territory_markup"]
    assert '<th scope="col">Entidad</th>' in result["territory_markup"]
    assert "<td>Estado 32</td>" in result["territory_markup"]


def test_null_gap_does_not_draw_false_zero_or_connect_across_gap(tmp_path):
    stage = _stage(tmp_path, gap=True)
    result = render_charts(stage)
    svg = (stage / "charts/trend-employment_rate-033100.svg").read_text(encoding="utf-8")
    # There are six connections between the seven visible points, split by the gap.
    assert svg.count('fill="none" stroke="#3659d9" stroke-width="2.5"') == 5
    assert "No disponible" in result["territory_markup"]
    trace = json.loads((stage / "charts/chart-data.json").read_text(encoding="utf-8"))
    missing = next(r for r in trace["figures"]["figure:eight-quarter-trends"] if r["record_id"] == "trend-employment_rate-033100-2025-Q2")
    assert missing["value"] == "" and missing["ci90_lower"] == ""


def test_duplicate_figure_link_fails(tmp_path):
    stage = _stage(tmp_path)
    links = stage / "research/exports/figure-record-links.csv"
    with links.open("a", encoding="utf-8") as output:
        output.write("figure:eight-quarter-trends,trend-employment_rate-033100-2026-Q2\n")
    with pytest.raises(ValueError, match="duplicados"):
        render_charts(stage)


def test_missing_public_record_fails(tmp_path):
    stage = _stage(tmp_path)
    path = stage / "research/exports/figure-record-links.csv"
    text = path.read_text(encoding="utf-8").replace(
        "trend-employment_rate-033100-2026-Q2", "not-published")
    path.write_text(text, encoding="utf-8")
    with pytest.raises(ValueError, match="no publicado"):
        render_charts(stage)
