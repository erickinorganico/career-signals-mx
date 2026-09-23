"""Portable guards for installed numerical acceptance and read-only replay."""

import json
import os
import subprocess
from pathlib import Path

import pytest

from brujula import enoe_acceptance as service
from brujula.analysis_v2 import _check_codes, _required_code_files, _approved_public_pins
from brujula.resources import oracle_script_path


def test_new_package_inventory_is_exact_and_rejects_old_scripts():
    actual = service._code_hashes()
    assert len(actual) == 11
    assert set(actual) == _required_code_files()
    _check_codes({"code_sha256": actual})
    old = {name.replace("brujula/enoe_acceptance.py", "scripts/accept_enoe_estimates.py"):
           value for name, value in actual.items()}
    with pytest.raises(ValueError, match="inventory"):
        _check_codes({"code_sha256": old})
    changed = dict(actual)
    changed["brujula/enoe_acceptance.py"] = "0" * 64
    with pytest.raises(ValueError, match="code changed"):
        _check_codes({"code_sha256": changed})


def test_package_golden_has_independent_content_hash():
    pins = _approved_public_pins()
    assert len(pins) == 8
    assert all(len(digest) == 64 for digest in pins.values())
    assert "fixtures/enoe-analysis-reference.json" not in service.NUMERIC_RESOURCES
    assert "fixtures/enoe-aggregate-golden.json" in service.NUMERIC_RESOURCES


def test_altered_golden_and_outside_package_resource_fail(monkeypatch, tmp_path):
    from brujula import analysis_v2, resources

    bad = tmp_path / "enoe-aggregate-golden.json"
    bad.write_text('{"tampered":true}', encoding="utf-8")
    monkeypatch.setattr(analysis_v2, "aggregate_golden_path", lambda: bad)
    with pytest.raises(ValueError, match="independent package golden"):
        analysis_v2._approved_public_pins()
    monkeypatch.setattr(resources, "CHECKOUT_ROOT", None)
    with pytest.raises(FileNotFoundError, match="escaped package"):
        resources.require_installed_package_path(bad)


def test_missing_r_or_sources_leave_distinct_failed_receipts(tmp_path):
    source = tmp_path / "source"
    output = tmp_path / "output"
    audit = tmp_path / "audit"
    first = service.accept(
        output, audit, source_root=source, workbook=tmp_path / "missing.xlsx",
        pdf=tmp_path / "missing.pdf", rscript=tmp_path / "missing-rscript",
        r_lib=tmp_path / "missing-lib")
    assert first["status"] == "BLOCKED"
    assert "missing.xlsx" in first["reason"]
    second = service.accept(
        output, audit, source_root=source, workbook=tmp_path / "missing.xlsx",
        pdf=tmp_path / "missing.pdf", rscript=Path(__file__), r_lib=tmp_path / "missing-lib")
    assert second["status"] == "BLOCKED"
    assert first["attempt_id"] != second["attempt_id"]
    receipts = sorted((audit / "attempts").glob("*.json"))
    assert len(receipts) == 2
    assert json.loads((audit / "current.json").read_text())["status"] == "BLOCKED"
    with pytest.raises(FileNotFoundError, match="Rscript executable unavailable"):
        service._r_runtime(tmp_path / "missing-rscript", None, tmp_path / "missing-lib")


def test_golden_generation_is_rejected_before_any_source_read(tmp_path):
    result = service.accept(tmp_path / "out", tmp_path / "audit", source_root=tmp_path / "source",
                            workbook=tmp_path / "workbook", pdf=tmp_path / "pdf",
                            generate_golden=True)
    assert result["status"] == "BLOCKED" and "cannot generate golden" in result["reason"]


def test_nested_roots_are_rejected_before_output_creation(tmp_path):
    source = tmp_path / "source"
    nested_output = source / "output"
    with pytest.raises(ValueError, match="must not overlap"):
        service.accept(nested_output, tmp_path / "audit", source_root=source,
                       workbook=tmp_path / "workbook", pdf=tmp_path / "pdf")
    assert not nested_output.exists()


def test_audit_overlap_never_writes_into_source_or_sealed_output(tmp_path):
    source = tmp_path / "source"
    source.mkdir()
    with pytest.raises(ValueError, match="must not overlap"):
        service.accept(tmp_path / "output", source / "audit", source_root=source,
                       workbook=tmp_path / "workbook", pdf=tmp_path / "pdf")
    assert list(source.iterdir()) == []
    historical = tmp_path / "historical"
    historical.mkdir()
    attempts = tmp_path / "old-audit" / "attempts"
    attempts.mkdir(parents=True)
    seal = attempts / "prior.json"
    seal.write_text(json.dumps({"output_root": str(historical)}), encoding="utf-8")
    with pytest.raises(ValueError, match="overlaps sealed accepted output"):
        service.replay(source, seal, historical / "audit")
    assert list(historical.iterdir()) == []
    with pytest.raises(ValueError, match="overlaps sealed acceptance audit"):
        service.replay(source, seal, attempts.parent / "nested-audit")


def test_benchmark_hashes_reject_mid_run_replacement(monkeypatch, tmp_path):
    from brujula import official_reconciliation as official

    workbook = tmp_path / "workbook.xlsx"
    pdf = tmp_path / "report.pdf"
    workbook.write_bytes(b"reviewed workbook")
    pdf.write_bytes(b"reviewed PDF")
    monkeypatch.setattr(official, "WORKBOOK_SHA256", service.hashlib.sha256(workbook.read_bytes()).hexdigest())
    monkeypatch.setattr(official, "PDF_2026_Q2_SHA256", service.hashlib.sha256(pdf.read_bytes()).hexdigest())
    pinned = service._benchmark_digests(workbook, pdf)
    pdf.write_bytes(b"replaced PDF")
    with pytest.raises(ValueError, match="SHA-256"):
        service._benchmark_digests(workbook, pdf)
    assert pinned["pdf_sha256"] != service.hashlib.sha256(pdf.read_bytes()).hexdigest()


def test_existing_acceptance_artifacts_are_immutable(tmp_path):
    output = tmp_path / "output"
    output.mkdir()
    historical = output / "enoe_2024_q3-public-v2.json"
    historical.write_text("historical", encoding="utf-8")
    result = service.accept(output, tmp_path / "audit", source_root=tmp_path / "source",
                            workbook=tmp_path / "workbook", pdf=tmp_path / "pdf")
    assert result["status"] == "BLOCKED" and "historical artifacts" in result["reason"]
    assert historical.read_text(encoding="utf-8") == "historical"


def test_explicit_r_library_cannot_fall_back_to_system_packages(tmp_path):
    rscript = Path(__file__).resolve().parents[1] / ".cache/R-4.6.1/bin/Rscript.exe"
    r_home = rscript.parents[1]
    if not rscript.is_file():
        pytest.skip("optional reviewed local R runtime unavailable")
    with pytest.raises(ValueError, match="explicit R library"):
        service._r_runtime(rscript, r_home, tmp_path)


def test_oracle_loads_packages_only_from_explicit_library(tmp_path):
    repo = Path(__file__).resolve().parents[1]
    rscript = repo / ".cache/R-4.6.1/bin/Rscript.exe"
    library = repo / ".cache/R-library"
    if not rscript.is_file() or not library.is_dir():
        pytest.skip("optional reviewed local R runtime unavailable")
    empty = tmp_path / "empty-library"
    empty.mkdir()
    env = {**os.environ, "R_HOME": str(rscript.parents[1]),
           "R_LIBS_SITE": str(library), "BRUJULA_R_LIB": str(empty)}
    command = [str(rscript), str(oracle_script_path()), "--frame", str(tmp_path / "missing.csv"),
               "--cases", str(tmp_path / "missing.json"), "--output", str(tmp_path / "out.json")]
    result = subprocess.run(command, capture_output=True, text=True, env=env, timeout=30)
    assert result.returncode != 0
    assert "survey" in result.stderr.lower() and "package" in result.stderr.lower()
