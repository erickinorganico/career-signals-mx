"""Installed package resource and PDF capability controls."""

import hashlib

import pytest

from brujula import resources


RESOURCE_ACCESSORS = {
    "catalog/enoe-snapshots.json": resources.snapshot_catalog_path,
    "catalog/enoe-metrics.json": resources.metric_catalog_path,
    "fixtures/enoe-aggregate-golden.json": resources.aggregate_golden_path,
    "fixtures/enoe-analysis-reference.json": resources.analysis_reference_path,
    "fixtures/enoe-analysis-coverage-pins.json": resources.coverage_pins_path,
    "oracle/enoe_survey_oracle.R": resources.oracle_script_path,
}


def test_authored_resource_paths_and_digests():
    digests = resources.authored_resource_digests()
    for name, accessor in RESOURCE_ACCESSORS.items():
        path = accessor()
        assert path.is_file(), name
        assert digests[name] == hashlib.sha256(path.read_bytes()).hexdigest()


def test_packaged_oracle_is_byte_identical_to_authored_script():
    from pathlib import Path

    script = Path(__file__).resolve().parents[1] / "scripts/enoe_survey_oracle.R"
    assert resources.oracle_script_path().read_bytes() == script.read_bytes()


def test_missing_resource_fails_closed(monkeypatch, tmp_path):
    monkeypatch.setattr(resources, "PACKAGE_ROOT", tmp_path)
    with pytest.raises(FileNotFoundError, match="enoe-snapshots.json"):
        resources.snapshot_catalog_path()
