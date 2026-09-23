"""Installed package resource and PDF capability controls."""

import hashlib
import importlib
import tomllib

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
    monkeypatch.setattr(resources, "files", lambda _package: tmp_path)
    monkeypatch.setattr(resources, "CHECKOUT_ROOT", None)
    with pytest.raises(FileNotFoundError, match="enoe-snapshots.json"):
        resources.snapshot_catalog_path()


@pytest.mark.parametrize("name", [
    "DejaVuSans.ttf", "DejaVuSans-Bold.ttf",
    "DejaVuSerif.ttf", "DejaVuSerif-Bold.ttf", "LICENSE_DEJAVU",
])
def test_audited_font_inventory(name):
    path = resources.font_path(name)
    assert path.is_file()
    assert resources.authored_resource_digests()[f"assets/fonts/{name}"] == hashlib.sha256(path.read_bytes()).hexdigest()


def test_font_allowlist_rejects_other_paths():
    with pytest.raises(ValueError):
        resources.font_path("../../private.txt")


def test_pdf_extra_is_exactly_reviewed_version():
    from pathlib import Path

    project = tomllib.loads((Path(__file__).resolve().parents[1] / "pyproject.toml").read_text(encoding="utf-8"))
    assert project["project"]["optional-dependencies"]["pdf"] == ["weasyprint==70.0"]


def test_missing_pdf_dependency_fails_explicitly(monkeypatch):
    actual_import = importlib.import_module

    def missing(name):
        if name == "weasyprint":
            raise ImportError("simulated absent optional dependency")
        return actual_import(name)

    monkeypatch.setattr(importlib, "import_module", missing)
    with pytest.raises(RuntimeError, match="weasyprint==70.0"):
        resources.require_pdf_capability()
