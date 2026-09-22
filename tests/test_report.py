import json
from copy import deepcopy
from pathlib import Path

import pytest

from brujula.report import render_report


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
    render_report(payload, tmp_path)
    html = (tmp_path / "report.html").read_text(encoding="utf-8")
    assert "<script>" not in html and "&lt;script&gt;" in html
