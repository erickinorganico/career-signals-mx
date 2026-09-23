"""Sealed v2 publication boundary checks."""

from pathlib import Path
import hashlib
import json

import pytest

from brujula import pipeline_v2 as p


def test_v2_publication_service_exists():
    from brujula import pipeline_v2

    assert callable(pipeline_v2.build_publication)
    assert callable(pipeline_v2.resolve_publication_current)
    assert callable(pipeline_v2.analyze_acceptance)
    assert callable(pipeline_v2.replay_publication)


def test_unsafe_roots_rejected_before_writes(tmp_path: Path):
    from brujula.pipeline_v2 import build_publication

    root = tmp_path / "source"
    with pytest.raises(ValueError, match="overlap"):
        build_publication(root, root / "publication", tmp_path / "audit", tmp_path / "analysis.json")
    assert not root.exists()


def _stub_build(monkeypatch, tmp_path):
    source, out, audit = (tmp_path / name for name in ("source", "out", "audit"))
    analysis = tmp_path / "input.json"
    analysis.write_text(json.dumps({"content_digest": "a" * 64}), encoding="utf-8")
    packet = {"content_digest": "a" * 64}
    model = {"content_digest": "b" * 64}
    sources = [{"snapshot_id": sid, "acquisition_attempt_id": "attempt",
                "source_url": "https://www.inegi.org.mx/example.zip",
                "source_sha256": "2" * 64, "period_id": period,
                "receipt_sha256": "3" * 64}
               for sid, period in zip(p.SNAPSHOTS, p.PERIODS)]
    acceptance = {"attempt_id": "sample", "numeric_content_digest": "c" * 64}
    names = {"analysis.json", "report.html", "report.md", "report.pdf"}
    names.update({f"assets/fonts/{name}" for name in p.FONT_NAMES})
    names.update({f"exports/f{i:02d}.csv" for i in range(46)})
    names.update({f"figures/f{i:02d}.svg" for i in range(18)})
    assert len(names) == 73
    monkeypatch.setattr(p, "_sources", lambda _root: sources)
    monkeypatch.setattr(p, "_accepted", lambda _audit, selected=None: (acceptance, "d" * 64))
    monkeypatch.setattr(p, "validate_analysis_packet", lambda _packet: [])
    monkeypatch.setattr(p, "build_publication_model", lambda _packet: model)
    monkeypatch.setattr(p, "validate_publication_model", lambda _model: [])
    monkeypatch.setattr(p, "_summary", lambda *_args: {
        "attempt_id": "sample", "receipt_sha256": "d" * 64,
        "numeric_content_digest": "c" * 64, "metric_manifest_sha256": "e" * 64,
        "code_sha256": {f"c{i}": "f" * 64 for i in range(11)},
        "resource_sha256": {f"r{i}": "1" * 64 for i in range(7)},
        "source_manifest": {}})
    monkeypatch.setattr(p, "_expected", lambda _model: names)

    def rendered(_model, run):
        for name in names - {"analysis.json"}:
            path = run / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(name.encode("utf-8"))
        return p._inventory(run, names)

    monkeypatch.setattr(p, "_render", rendered)
    return source, out, audit, analysis, names


def test_build_seals_before_current_and_preserves_history_on_failure(monkeypatch, tmp_path):
    source, out, audit, analysis, names = _stub_build(monkeypatch, tmp_path)
    built = p.build_publication(source, out, audit, analysis)
    run = built["run"]
    assert set(built["manifest"]["artifact_hashes"]) == names
    assert (run / "receipt.json").is_file() and (run / "manifest.json").is_file()
    current = json.loads((out / "current.json").read_text(encoding="utf-8"))
    assert current["manifest_sha256"] == hashlib.sha256((run / "manifest.json").read_bytes()).hexdigest()
    assert "audit_dir" not in json.dumps(built["manifest"]) + json.dumps(built["receipt"])

    def fail_render(_model, _run):
        raise RuntimeError("secret C:/private/path")

    monkeypatch.setattr(p, "_render", fail_render)
    with pytest.raises(RuntimeError):
        p.build_publication(source, out, audit, analysis)
    blocked = json.loads((out / "current.json").read_text(encoding="utf-8"))
    assert blocked["status"] == "BLOCKED"
    assert "private" not in json.dumps(blocked)
    assert (run / "manifest.json").read_bytes() == p.json_bytes(built["manifest"])
    assert (out / "runs" / blocked["run_id"] / "receipt.json").is_file()


def test_colliding_run_id_never_reuses_sealed_history(monkeypatch, tmp_path):
    source, out, audit, analysis, _names = _stub_build(monkeypatch, tmp_path)
    monkeypatch.setattr(p, "_attempt_id", lambda: "20260923T120000-aaaaaaaaaaaa")
    p.build_publication(source, out, audit, analysis)
    prior = (out / "runs/20260923T120000-aaaaaaaaaaaa/manifest.json").read_bytes()
    with pytest.raises(FileExistsError):
        p.build_publication(source, out, audit, analysis)
    assert (out / "runs/20260923T120000-aaaaaaaaaaaa/manifest.json").read_bytes() == prior


def test_inventory_rejects_extra_missing_and_symlink(tmp_path):
    root = tmp_path / "run"
    root.mkdir()
    (root / "analysis.json").write_bytes(b"approved")
    assert set(p._inventory(root, {"analysis.json"})) == {"analysis.json"}
    (root / "extra.txt").write_bytes(b"extra")
    with pytest.raises(ValueError, match="inventory"):
        p._inventory(root, {"analysis.json"})
    (root / "extra.txt").unlink()
    (root / "analysis.json").unlink()
    with pytest.raises(ValueError, match="inventory"):
        p._inventory(root, {"analysis.json"})
