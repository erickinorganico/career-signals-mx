"""Portable guards for installed numerical acceptance and read-only replay."""

import json
from pathlib import Path

import pytest

from brujula import enoe_acceptance as service
from brujula.analysis_v2 import _check_codes, _required_code_files, _approved_public_pins


def test_new_package_inventory_is_exact_and_rejects_old_scripts():
    actual = service._code_hashes()
    assert len(actual) == 11
    assert set(actual) == _required_code_files()
    _check_codes({"code_sha256": actual})
    old = {name.replace("brujula/enoe_acceptance.py", "scripts/accept_enoe_estimates.py"):
           value for name, value in actual.items()}
    with pytest.raises(ValueError, match="inventory"):
        _check_codes({"code_sha256": old})


def test_package_golden_has_independent_content_hash():
    pins = _approved_public_pins()
    assert len(pins) == 8
    assert all(len(digest) == 64 for digest in pins.values())


def test_missing_r_or_sources_leave_distinct_failed_receipts(tmp_path):
    source = tmp_path / "source"
    output = tmp_path / "output"
    audit = tmp_path / "audit"
    first = service.run_attempt(audit, lambda: service.accept(
        output, audit, source_root=source, workbook=tmp_path / "missing.xlsx",
        pdf=tmp_path / "missing.pdf", rscript=tmp_path / "missing-rscript",
        r_lib=tmp_path / "missing-lib"))
    assert first["status"] == "BLOCKED"
    assert "missing.xlsx" in first["reason"]
    second = service.run_attempt(audit, lambda: service.accept(
        output, audit, source_root=source, workbook=tmp_path / "missing.xlsx",
        pdf=tmp_path / "missing.pdf", rscript=Path(__file__), r_lib=tmp_path / "missing-lib"))
    assert second["status"] == "BLOCKED"
    assert first["attempt_id"] != second["attempt_id"]
    receipts = sorted((audit / "attempts").glob("*.json"))
    assert len(receipts) == 2
    assert json.loads((audit / "current.json").read_text())["status"] == "BLOCKED"
    with pytest.raises(FileNotFoundError, match="Rscript executable unavailable"):
        service._r_runtime(tmp_path / "missing-rscript", None, tmp_path / "missing-lib")


def test_golden_generation_is_rejected_before_any_source_read(tmp_path):
    with pytest.raises(ValueError, match="cannot generate golden"):
        service.accept(tmp_path / "out", tmp_path / "audit", source_root=tmp_path / "source",
                       workbook=tmp_path / "workbook", pdf=tmp_path / "pdf",
                       generate_golden=True)
