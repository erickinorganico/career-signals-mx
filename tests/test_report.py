import json
from copy import deepcopy
from pathlib import Path

import pytest
from matplotlib.axes import Axes

from brujula.report import _period_x_positions, _trend_points, _trend_segments, render_report


@pytest.fixture
def payload():
    dataset = json.loads((Path(__file__).parents[1] / "data/fixtures/pilot.json").read_text(encoding="utf-8"))
    return {"schema_version":"1.0","status":"REVIEW","publishable":True,"generated_at":"2026-01-01T00:00:00Z","dataset":dataset,"quality":{"freshness":{"status":"illustrative","latest_period_end":"2025-12-31"}},"comparisons":[],"insights":[],"receipt":{},"catalog":[]}


def test_static_report_has_metadata_charts_and_synthetic_warning(tmp_path, payload):
    result = render_report(payload, tmp_path)
    report = (tmp_path / result["markdown"]).read_text(encoding="utf-8")
    assert result["charts"] and (tmp_path / result["charts"][0]).exists()
    assert "DATOS SINTÉTICOS" in report and "Frescura por periodo de negocio" in report
    assert "Campo y ocupación" in report and "No disponible" in report


def test_blocked_payload_never_renders_figures_or_numeric_values(tmp_path, payload):
    blocked = deepcopy(payload); blocked.update(status="BLOCKED", publishable=False, dataset=None, error="gate")
    result = render_report(blocked, tmp_path)
    assert result["charts"] == []
    assert "No se publican cifras" in (tmp_path / "report.md").read_text(encoding="utf-8")


def test_html_escapes_payload_text(tmp_path, payload):
    payload["dataset"]["label"] = "<script>alert(1)</script>"
    payload["dataset"]["sources"][0]["url"] = "![remote](https://example.invalid/image.png)"
    render_report(payload, tmp_path)
    html = (tmp_path / "report.html").read_text(encoding="utf-8")
    markdown = (tmp_path / "report.md").read_text(encoding="utf-8")
    assert "<script>" not in html and "&lt;script&gt;" in html
    assert "![remote]" not in markdown
    assert "https://example.invalid" not in markdown


def test_missing_and_non_comparable_values_are_gaps_not_zero(tmp_path, payload):
    dataset = payload["dataset"]
    # Extend the local fixture in-memory with a second income period. Its declared
    # comparison is blocked, so the trend cannot join it to the previous point.
    prior = deepcopy(dataset["observations"][0])
    current = deepcopy(prior)
    current.update(id="synthetic_income_q3", period_id="demo_2025_q3", value=19000)
    dataset["observations"].append(current)
    payload["comparisons"] = [{"previous_id": prior["id"], "current_id": current["id"], "comparable": False,
                               "absolute_change": None, "relative_change_pct": None}]
    result = render_report(payload, tmp_path)
    report = (tmp_path / result["markdown"]).read_text(encoding="utf-8")
    assert "No disponible" in report
    assert "Punto aislado; no hay par comparable declarado" in report
    assert "0 MXN/month" not in report
    assert [row["id"] for row in _trend_points([prior, current])] == [prior["id"], current["id"]]
    assert _trend_segments([prior, current], set()) == []
    assert _trend_segments([prior, current], {(prior["id"], current["id"])}) == [(prior, current)]


def test_report_is_deterministic_for_same_payload(tmp_path, payload):
    first = render_report(payload, tmp_path / "one")
    second = render_report(payload, tmp_path / "two")
    for name in ("report.md", "report.html"):
        assert (tmp_path / "one" / name).read_bytes() == (tmp_path / "two" / name).read_bytes()
    assert first["charts"] == second["charts"]
    for relative in first["charts"]:
        assert (tmp_path / "one" / relative).read_bytes() == (tmp_path / "two" / relative).read_bytes()
    svg = next(tmp_path.glob("one/charts/*.svg")).read_text(encoding="utf-8")
    assert "Fuente:" in svg and "precio:" in svg and "precision:" in svg


def test_untrusted_metric_id_and_label_cannot_escape_report_paths(tmp_path, payload):
    metric = payload["dataset"]["metrics"][0]
    metric.update(id="../../outside", label="![remote](https://example.invalid/image.png)")
    for row in payload["dataset"]["observations"]:
        if row["metric_id"] == "mean_monthly_income":
            row["metric_id"] = "../../outside"
    result = render_report(payload, tmp_path)
    assert all(".." not in path and "\\" not in path for path in result["charts"])
    markdown = (tmp_path / "report.md").read_text(encoding="utf-8")
    assert "![remote]" not in markdown


def test_unavailable_status_hides_malicious_numeric_value(tmp_path, payload):
    row = payload["dataset"]["observations"][2]
    row.update(status="UNKNOWN", value=987654321)
    render_report(payload, tmp_path)
    report = (tmp_path / "report.md").read_text(encoding="utf-8")
    assert "987,654,321" not in report


def test_concept_type_namespace_prevents_occupation_label_collision(tmp_path, payload):
    dataset = payload["dataset"]
    dataset["dimensions"]["occupations"].append({"id": "demo_field_derecho", "label": "WRONG OCCUPATION LABEL", "description": "Valid separate namespace."})
    occupation = deepcopy(dataset["observations"][0])
    occupation.update(id="occupation_same_id", concept_type="occupation", concept_id="demo_field_derecho")
    dataset["observations"].append(occupation)
    render_report(payload, tmp_path)
    report = (tmp_path / "report.md").read_text(encoding="utf-8")
    assert "Derecho" in report
    assert "WRONG OCCUPATION LABEL" in report


def test_global_period_axis_order_survives_leading_null_series(payload):
    periods = {period["id"]: period for period in payload["dataset"]["dimensions"]["periods"]}
    ordered, positions = _period_x_positions(periods)
    leading_null = deepcopy(payload["dataset"]["observations"][0])
    leading_null.update(id="leading-null", period_id="demo_2025_q2", value=None, status="UNKNOWN")
    later = deepcopy(leading_null)
    later.update(id="later-valid", period_id="demo_2025_q3", value=19000, status="REVIEW")
    assert [period["id"] for period in ordered] == ["demo_2025_q2", "demo_2025_q3", "demo_2025_q4"]
    assert positions[leading_null["period_id"]] == 0
    assert positions[later["period_id"]] == 1
    assert [row["id"] for row in _trend_points([leading_null, later])] == ["later-valid"]


def test_latest_national_chart_keeps_missing_fields_as_holes(tmp_path, payload, monkeypatch):
    rows = [row for row in payload["dataset"]["observations"] if row["metric_id"] == "female_share" and row["geography_id"] == "demo_mx" and row["period_id"] == "demo_2025_q4"]
    assert len(rows) == 3
    rows[0].update(value=57.0, status="REVIEW")
    for row in rows[1:]:
        row.update(value=None, status="UNKNOWN")
    heights: list[list[float]] = []
    original_bar = Axes.bar

    def capture_bar(self, x, height, *args, **kwargs):
        heights.append(list(height) if hasattr(height, "__iter__") else [height])
        return original_bar(self, x, height, *args, **kwargs)

    monkeypatch.setattr(Axes, "bar", capture_bar)
    render_report(payload, tmp_path)
    svg = "\n".join(path.read_text(encoding="utf-8") for path in (tmp_path / "charts").glob("*.svg"))
    assert "Derecho" in svg and "Comunicación y periodismo" in svg and "Ciencias políticas" in svg
    assert "Sin dato" in svg
    assert [57.0] in heights
    assert all(0.0 not in captured for captured in heights)
