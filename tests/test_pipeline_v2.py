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


def test_current_pointer_rejects_unlisted_authority_fields(monkeypatch, tmp_path):
    source, out = tmp_path / "source", tmp_path / "out"
    out.mkdir()
    pointer = {"schema_version": "2.0", "run_id": "20260923T120000-aaaaaaaaaaaa",
               "status": "REVIEW", "build_status": "SUCCEEDED",
               "manifest_sha256": "a" * 64, "forged_success": True}
    p.atomic_json(out / "current.json", pointer)
    monkeypatch.setattr(p, "_verify_sealed", lambda *_args: {
        "sources": [], "artifact_hashes": {}, "manifest": {}, "receipt": {}})
    with pytest.raises(ValueError, match="current publication"):
        p.resolve_publication_current(out, source)


def test_current_resolution_rechecks_source_and_artifact_identity(monkeypatch, tmp_path):
    source, out = tmp_path / "source", tmp_path / "out"
    out.mkdir()
    p.atomic_json(out / "current.json", {
        "schema_version": "2.0", "run_id": "20260923T120000-aaaaaaaaaaaa",
        "status": "REVIEW", "build_status": "SUCCEEDED", "manifest_sha256": "a" * 64})
    count = 0

    def verify(*_args):
        nonlocal count
        count += 1
        return {"sources": [{"attempt": count}], "artifact_hashes": {},
                "manifest": {}, "receipt": {}}

    monkeypatch.setattr(p, "_verify_sealed", verify)
    with pytest.raises(ValueError, match="changed during resolution"):
        p.resolve_publication_current(out, source)
    assert count == 2


def test_safe_artifact_paths_reject_traversal_and_backslashes(tmp_path):
    root = tmp_path / "run"
    root.mkdir()
    for value in ("../escape", "C:/absolute", "sub\\evil", "/absolute"):
        with pytest.raises(ValueError, match="unsafe|escaped"):
            p._safe_file(root, value)


@pytest.mark.parametrize("stage", ("render", "receipt", "manifest", "pointer", "final_index"))
def test_fault_boundaries_leave_blocked_current_and_preserve_history(monkeypatch, tmp_path, stage):
    source, out, audit, analysis, _names = _stub_build(monkeypatch, tmp_path)
    good = p.build_publication(source, out, audit, analysis)
    sealed = (good["run"] / "manifest.json").read_bytes()
    armed = True
    if stage == "render":
        monkeypatch.setattr(p, "_render", lambda *_args: (_ for _ in ()).throw(RuntimeError("private path")))
    elif stage == "receipt":
        original = p.immutable_bytes

        def fail_receipt(path, content):
            nonlocal armed
            if path.name == "receipt.json" and armed:
                armed = False
                raise OSError("receipt I/O fault")
            return original(path, content)

        monkeypatch.setattr(p, "immutable_bytes", fail_receipt)
    elif stage == "manifest":
        monkeypatch.setattr(p, "_validate_manifest", lambda _item: (_ for _ in ()).throw(ValueError("manifest fault")))
    else:
        original = p.atomic_json

        def fail_atomic(path, value):
            nonlocal armed
            if armed and ((stage == "pointer" and path.name == "current.json"
                           and value.get("status") == "REVIEW")
                          or (stage == "final_index" and path.name == "journal.json"
                              and value.get("build_status") == "SUCCEEDED")):
                armed = False
                raise OSError("promotion fault")
            return original(path, value)

        monkeypatch.setattr(p, "atomic_json", fail_atomic)
    with pytest.raises((OSError, ValueError, RuntimeError)):
        p.build_publication(source, out, audit, analysis)
    current = json.loads((out / "current.json").read_text(encoding="utf-8"))
    assert current["status"] == "BLOCKED"
    assert "private" not in json.dumps(current)
    assert (good["run"] / "manifest.json").read_bytes() == sealed
    failed = out / "runs" / current["run_id"]
    assert (failed / "receipt.json").exists()


def test_analysis_failure_receipt_is_separate_and_bounded(monkeypatch, tmp_path):
    source = tmp_path / "sources"
    audit = tmp_path / "analysis-audit"
    numerical = tmp_path / "numerical-audit"
    receipt = numerical / "attempts" / ("a" * 36 + ".json")
    output = tmp_path / "new-analysis.json"
    monkeypatch.setattr(p, "_accepted", lambda *_args: (
        {"output_root": str(tmp_path / "accepted-output"), "attempt_id": "a" * 36}, "b" * 64))
    monkeypatch.setattr(p, "_sources", lambda *_args: [{"snapshot_id": sid} for sid in p.SNAPSHOTS])
    monkeypatch.setattr(p, "_accepted_payloads", lambda *_args: ({}, {}))
    monkeypatch.setattr(p, "build_analysis_packet",
                        lambda *_args: (_ for _ in ()).throw(ValueError("C:/private/secret")))
    with pytest.raises(ValueError):
        p.analyze_acceptance(source, receipt, output, audit)
    current = json.loads((audit / "current.json").read_text(encoding="utf-8"))
    assert current["status"] == "BLOCKED"
    assert "private" not in json.dumps(current)
    assert (audit / "attempts" / (current["attempt_id"] + ".json")).exists()
    assert not numerical.exists() and not output.exists()


def test_missing_accepted_receipt_seals_analysis_failure(tmp_path):
    receipt = tmp_path / "numerical" / "attempts" / ("a" * 36 + ".json")
    audit = tmp_path / "analysis-audit"
    with pytest.raises(FileNotFoundError):
        p.analyze_acceptance(tmp_path / "source", receipt, tmp_path / "fresh.json", audit)
    current = json.loads((audit / "current.json").read_text(encoding="utf-8"))
    assert current["status"] == "BLOCKED"
    assert (audit / "attempts" / (current["attempt_id"] + ".json")).is_file()


def test_symlinked_authority_paths_fail_before_read(monkeypatch, tmp_path):
    audit = tmp_path / "numerical"
    audit.mkdir()
    current = audit / "current.json"
    current.write_text("{}", encoding="utf-8")
    original = Path.is_symlink
    monkeypatch.setattr(Path, "is_symlink", lambda path: path == current or original(path))
    with pytest.raises(ValueError, match="symlink"):
        p._accepted(audit)
    monkeypatch.setattr(Path, "is_symlink", original)
    run = tmp_path / "publication" / "runs" / "20260923T120000-aaaaaaaaaaaa"
    run.mkdir(parents=True)
    monkeypatch.setattr(Path, "is_symlink", lambda path: path == run.parent or original(path))
    with pytest.raises(ValueError, match="symlink"):
        p._verify_sealed(run, tmp_path / "source")


def test_junction_runs_parent_rejected_before_any_publication_write(monkeypatch, tmp_path):
    source, out, audit, analysis, _names = _stub_build(monkeypatch, tmp_path)
    (out / "runs").mkdir(parents=True)
    original = Path.is_junction
    monkeypatch.setattr(Path, "is_junction", lambda path: path == out / "runs" or original(path))
    with pytest.raises(ValueError, match="junction|reparse|escaped"):
        p.build_publication(source, out, audit, analysis)
    assert not (out / "current.json").exists()
    assert not (out / "runs" / "20260923T120000-aaaaaaaaaaaa").exists()


def test_analysis_output_junction_parent_rejected_before_receipt(monkeypatch, tmp_path):
    source = tmp_path / "source"
    audit = tmp_path / "operation-audit"
    acceptance = tmp_path / "numerical" / "attempts" / ("a" * 36 + ".json")
    escaped_parent = tmp_path / "alias"
    escaped_parent.mkdir()
    original = Path.is_junction
    monkeypatch.setattr(Path, "is_junction", lambda path: path == escaped_parent or original(path))
    with pytest.raises(ValueError, match="junction"):
        p.analyze_acceptance(source, acceptance, escaped_parent / "analysis.json", audit)
    assert not (escaped_parent / "analysis.json").exists()
    assert not audit.exists()


def test_manifest_accepts_exact_sparse_figure_inventory(monkeypatch, tmp_path):
    # Six non-opening figures remain; 0–3 supported opening claims add 0–6 files.
    for group_count in range(4):
        case = tmp_path / str(group_count)
        case.mkdir()
        source, out, audit, analysis, names = _stub_build(monkeypatch, case)
        names.difference_update({name for name in names
                                 if name.startswith("figures/f") and int(name[9:11]) >= 12})
        names.update({f"figures/g{i}.{extension}" for i in range(group_count)
                      for extension in ("svg", "png")})
        assert len(names) == 67 + 2 * group_count
        sealed = p.build_publication(source, out, audit, analysis)
        assert set(sealed["manifest"]["artifact_hashes"]) == names
        p._validate_manifest(sealed["manifest"])


def test_replay_logical_exports_checks_csv_and_parquet_independently(tmp_path):
    import duckdb

    left, right = tmp_path / "left", tmp_path / "right"
    for root in (left, right):
        root.mkdir()
        db = duckdb.connect(str(root / "public.duckdb"))
        db.execute("CREATE TABLE public_records(value DOUBLE)")
        db.execute("INSERT INTO public_records VALUES (1.0)")
        db.execute(f"COPY public_records TO '{(root / 'public-records.parquet').as_posix()}' (FORMAT PARQUET)")
        db.close()
        (root / "public-records.csv").write_text("value\n1.0\n", encoding="utf-8")
    assert p._logical_exports(left, right, {"public_records"})
    (right / "public-records.csv").write_text("value\n999.0\n", encoding="utf-8")
    assert not p._logical_exports(left, right, {"public_records"})


def test_replay_logical_exports_ignores_tied_container_row_order(tmp_path):
    import duckdb

    left, right = tmp_path / "left", tmp_path / "right"
    for root, values in ((left, [(1, 10), (1, 20)]),
                         (right, [(1, 20), (1, 10)])):
        root.mkdir()
        db = duckdb.connect(str(root / "public.duckdb"))
        db.execute("CREATE TABLE public_records(k INTEGER, v INTEGER)")
        db.executemany("INSERT INTO public_records VALUES (?, ?)", values)
        db.execute(f"COPY public_records TO '{(root / 'public-records.parquet').as_posix()}' (FORMAT PARQUET)")
        db.close()
        (root / "public-records.csv").write_text("k,v\n1,10\n1,20\n", encoding="utf-8")
    assert p._logical_exports(left, right, {"public_records"})
    (right / "public-records.csv").write_text("value\n1.0\n", encoding="utf-8")
    (right / "public-records.parquet").unlink()
    db = duckdb.connect()
    db.execute(f"COPY (SELECT 999.0 AS value) TO '{(right / 'public-records.parquet').as_posix()}' (FORMAT PARQUET)")
    db.close()
    assert not p._logical_exports(left, right, {"public_records"})


def test_replay_reconstructs_and_keeps_baseline_immutable(monkeypatch, tmp_path):
    source, audit = tmp_path / "sources", tmp_path / "replay-audit"
    sealed = tmp_path / "publication" / "runs" / "20260923T120000-aaaaaaaaaaaa"
    sealed.mkdir(parents=True)
    (sealed / "manifest.json").write_bytes(b"baseline")
    packet = {"content_digest": "a" * 64}
    model = {"content_digest": "b" * 64, "records": {"v2r:one": {}},
             "comparisons": [], "claims": [], "figure_links": []}
    calls = []
    baseline = {"manifest": {"numerical_acceptance": {"numeric_content_digest": "c" * 64}},
                "manifest_sha256": "d" * 64, "packet": packet, "model": model,
                "sources": [], "artifact_hashes": {"report.html": "e" * 64}}
    monkeypatch.setattr(p, "_verify_sealed", lambda *_args: baseline)
    monkeypatch.setattr(p, "build_publication_model", lambda _packet: model)
    monkeypatch.setattr(p, "_render", lambda _model, directory: (
        calls.append(directory), {"report.html": "f" * 64})[1])
    monkeypatch.setattr(p, "_table_data", lambda _model: {"public_records": ({}, [])})
    monkeypatch.setattr(p, "_logical_exports", lambda *_args: True)
    result = p.replay_publication(source, sealed, audit)
    assert result["status"] == "PASS" and len(calls) == 1
    assert calls[0].is_relative_to(audit / "replay-runs")
    assert (sealed / "manifest.json").read_bytes() == b"baseline"
    assert (audit / "attempts" / (result["attempt_id"] + ".json")).exists()
