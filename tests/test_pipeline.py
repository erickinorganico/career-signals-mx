"""Analytical E2E: input -> contracts -> warehouse -> agents -> reports -> receipt."""
import csv
import hashlib
import io
import json
import subprocess
import sys
import shutil
from copy import deepcopy
from datetime import date
from pathlib import Path

import duckdb
import pytest

from brujula.pipeline import ROOT, build, export_csv, immutable_bytes, resolve_current


@pytest.fixture(scope="module")
def successful_run(tmp_path_factory):
    output = tmp_path_factory.mktemp("full-pipeline")
    payload = build(output=output, as_of=date(2026, 9, 22))
    assert payload["publishable"], payload["receipt"]
    return output, payload


def test_full_analytical_pipeline(successful_run):
    output, payload = successful_run
    receipt = payload["receipt"]
    assert receipt["build_status"] == "SUCCEEDED"
    assert payload["status"] == "REVIEW"  # synthetic data are never real measurements
    assert len(payload["dataset"]["observations"]) == 54
    assert payload["agent_run"]["publication_allowed"] is True
    run = output / "runs" / receipt["run_id"]
    raw = output / "raw" / (receipt["input_sha256"] + ".json")
    assert hashlib.sha256(raw.read_bytes()).hexdigest() == receipt["input_sha256"]
    with duckdb.connect(str(run / "warehouse.duckdb"), read_only=True) as connection:
        assert connection.execute("SELECT count(*) FROM observation").fetchone()[0] == 54
        assert connection.execute("SELECT count(*) FROM observation WHERE value IS NULL").fetchone()[0] >= 2
        parquet = str(run / "observations.parquet").replace("'", "''")
        assert connection.execute(f"SELECT count(*) FROM read_parquet('{parquet}')").fetchone()[0] == 54
        assert connection.execute("SELECT count(*) FROM observation WHERE concept_type = 'occupation'").fetchone()[0] == 0
    manifest = json.loads((run / "manifest.json").read_text(encoding="utf-8"))
    for relative, digest in manifest.items():
        assert hashlib.sha256((run / relative).read_bytes()).hexdigest() == digest
    report = (run / "report/report.md").read_text(encoding="utf-8")
    assert "SINTÉTICOS" in report
    assert "No disponible" in report
    html = (run / "report/report.html").read_text(encoding="utf-8")
    assert "<img" in html and "<table" in html
    assert "<script" not in html
    assert "http-server" not in html


def test_failed_refresh_replaces_current_without_destroying_history(successful_run, tmp_path):
    original, good = successful_run
    output = tmp_path / "isolated"
    shutil.copytree(original, output)
    bad = deepcopy(good["dataset"])
    bad["observations"][0]["evidence_refs"] = ["invented-reference"]
    input_path = tmp_path / "invalid.json"
    input_path.write_text(json.dumps(bad), encoding="utf-8")
    good_receipt = output / "runs" / good["run_id"] / "receipt.json"
    preserved = good_receipt.read_bytes()
    failure = build(input_path, output, as_of=date(2026, 9, 22))
    assert not failure["publishable"]
    assert failure["dataset"] is None and failure["insights"] == []
    current = json.loads((output / "current.json").read_text(encoding="utf-8"))
    assert current["status"] == "BLOCKED" and current["build_status"] == "FAILED"
    assert current["report"] is None
    assert current["run_id"] != good["run_id"]
    assert good_receipt.read_bytes() == preserved
    assert "Abrir el reporte verificado" not in (output / "report.md").read_text(encoding="utf-8")
    failed_run = output / "runs" / current["run_id"]
    assert not (failed_run / "observations.csv").exists()
    assert not (failed_run / "warehouse.duckdb").exists()


def test_missing_input_records_failure_receipt(tmp_path):
    failure = build(tmp_path / "missing.json", tmp_path / "out")
    assert failure["status"] == "BLOCKED"
    assert failure["receipt"]["input_sha256"] is None
    assert failure["receipt"]["error"]["type"] == "FileNotFoundError"
    assert (tmp_path / "out/runs" / failure["run_id"] / "receipt.json").exists()


def test_immutable_raw_rejects_replacement(tmp_path):
    path = tmp_path / "raw.json"
    immutable_bytes(path, b"first")
    immutable_bytes(path, b"first")
    with pytest.raises(ValueError, match="collision"):
        immutable_bytes(path, b"changed")
    assert path.read_bytes() == b"first"


def test_csv_preserves_absence_metadata_and_neutralizes_formulas(successful_run):
    data = deepcopy(successful_run[1]["dataset"])
    data["observations"][0]["precision_note"] = '=HYPERLINK("bad")'
    records = list(csv.DictReader(io.StringIO(export_csv(data))))
    assert records[0]["precision_note"].startswith("'=")
    assert any(r["value"] == "" and r["status"] == "UNKNOWN" for r in records)
    assert all(r["synthetic"] == "True" and r["unit"] and r["period_id"] and r["source_id"] for r in records)


def test_cli_failure_exit_is_nonzero_and_persists_block(tmp_path):
    run = subprocess.run([sys.executable, "-m", "brujula", "build", "--input", str(tmp_path / "absent.json"), "--output", str(tmp_path / "out")], cwd=ROOT, capture_output=True, text=True)
    assert run.returncode == 1
    assert json.loads((tmp_path / "out/current.json").read_text(encoding="utf-8"))["status"] == "BLOCKED"


def test_build_lock_prevents_overlapping_writers(tmp_path):
    (tmp_path / ".build.lock").write_text("test-owner", encoding="utf-8")
    with pytest.raises(RuntimeError, match="build is running"):
        build(output=tmp_path)
    assert (tmp_path / ".build.lock").read_text(encoding="utf-8") == "test-owner"


def test_resolver_ignores_stale_human_index_and_rejects_changed_artifact(successful_run, tmp_path):
    original, good = successful_run
    output = tmp_path / "copy"
    shutil.copytree(original, output)
    (output / "report.md").write_text("outdated index", encoding="utf-8")
    resolved = resolve_current(output)
    assert resolved["bundle"]["run_id"] == good["run_id"]
    resolved["html"].write_text("modified artifact", encoding="utf-8")
    with pytest.raises(ValueError, match="integrity"):
        resolve_current(output)


def test_resolver_detects_corrupted_raw_provenance(successful_run, tmp_path):
    original, good = successful_run
    output = tmp_path / "copy"
    shutil.copytree(original, output)
    raw = output / "raw" / (good["receipt"]["input_sha256"] + ".json")
    raw.write_text("modified input", encoding="utf-8")
    with pytest.raises(ValueError, match="Raw input integrity"):
        resolve_current(output)


def fast_renderer(payload, path):
    path.mkdir(parents=True)
    for name in ("report.md", "report.html"):
        (path / name).write_text("SYNTHETIC test artifact", encoding="utf-8")
    return {"markdown": "report.md", "html": "report.html", "charts": []}


def test_renderer_failure_retains_staging_only(monkeypatch, tmp_path):
    def broken_renderer(*args):
        raise ValueError("renderer failed")
    monkeypatch.setattr("brujula.report.render_report", broken_renderer)
    payload = build(output=tmp_path)
    run = tmp_path / "runs" / payload["run_id"]
    assert (run / "observations.parquet").exists()  # diagnostic staging only
    assert payload["status"] == "BLOCKED" and payload["dataset"] is None
    with pytest.raises(ValueError, match="BLOCKED"):
        resolve_current(tmp_path)


def test_crash_before_receipt_recovers_as_failure(monkeypatch, tmp_path):
    def crashed(*args):
        raise KeyboardInterrupt()
    monkeypatch.setattr("brujula.report.render_report", crashed)
    with pytest.raises(KeyboardInterrupt):
        build(output=tmp_path)
    current = json.loads((tmp_path / "current.json").read_text())
    assert current["build_status"] == "RUNNING" and not current["publishable"]
    digest = hashlib.sha256((ROOT / "data/fixtures/pilot.json").read_bytes()).hexdigest()
    assert current["input_sha256"] == digest
    abandoned = tmp_path / "runs" / current["run_id"]
    assert not (abandoned / "receipt.json").exists()
    monkeypatch.setattr("brujula.report.render_report", fast_renderer)
    assert build(output=tmp_path)["publishable"]
    assert json.loads((abandoned / "receipt.json").read_text())["build_status"] == "FAILED"
    assert json.loads((abandoned / "receipt.json").read_text())["input_sha256"] == digest


@pytest.mark.parametrize("exception", [OSError, KeyboardInterrupt])
def test_failure_between_sealing_and_commit_never_rewrites_receipt(monkeypatch, tmp_path, exception):
    import brujula.pipeline as pipeline
    original_write = pipeline.atomic_json
    rejected = []
    def fail_once(path, value):
        if path.name == "current.json" and value.get("publishable") and not rejected:
            rejected.append(value["run_id"])
            raise exception("commit interruption")
        original_write(path, value)
    monkeypatch.setattr("brujula.report.render_report", fast_renderer)
    monkeypatch.setattr(pipeline, "atomic_json", fail_once)
    if exception is KeyboardInterrupt:
        with pytest.raises(KeyboardInterrupt):
            build(output=tmp_path)
    else:
        assert not build(output=tmp_path)["publishable"]
    with pytest.raises(ValueError, match="BLOCKED"):
        resolve_current(tmp_path)
    old_run = tmp_path / "runs" / rejected[0]
    sealed = (old_run / "receipt.json").read_bytes()
    assert json.loads(sealed)["build_status"] == "SUCCEEDED"
    assert build(output=tmp_path)["publishable"]
    assert (old_run / "receipt.json").read_bytes() == sealed
    assert json.loads((old_run / "publication-failure.json").read_text())["build_status"] == "FAILED"


def test_index_failure_after_commit_keeps_verified_current(monkeypatch, tmp_path):
    monkeypatch.setattr("brujula.report.render_report", fast_renderer)
    def fail_index(*args):
        raise OSError("index unavailable")
    monkeypatch.setattr("brujula.pipeline.current_report", fail_index)
    payload = build(output=tmp_path)
    assert payload["publishable"]
    assert resolve_current(tmp_path)["bundle"]["run_id"] == payload["run_id"]
