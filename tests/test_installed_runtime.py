"""Installed package resource and PDF capability controls."""

import hashlib
import importlib
import sys
import tomllib
from types import SimpleNamespace

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

AUDITED_FONTS = {
    "DejaVuSans.ttf": "3fdf69cabf06049ea70a00b5919340e2ce1e6d02b0cc3c4b44fb6801bd1e0d22",
    "DejaVuSans-Bold.ttf": "b184b89e3c1075f22f6b71575b6fc20d4972b3cfd3b23322ca6fd596dcaef167",
    "DejaVuSerif.ttf": "107244956e9962b9e96faccdc551825e0ae0898ae13737133e1b921a2fd35ffa",
    "DejaVuSerif-Bold.ttf": "c3753f2ed6bc673f15846dc45addbeb3b9c872f32fb18fd53a21f1bef1ed7676",
    "LICENSE_DEJAVU": "d75938dec098f06f0ac3c00853065d94f020be1c3c62ef1dc2975ba15b4d9b0e",
}


def test_authored_resource_paths_and_digests():
    digests = resources.authored_resource_digests()
    for name, accessor in RESOURCE_ACCESSORS.items():
        path = accessor()
        assert path.is_file(), name
        assert digests[name] == hashlib.sha256(path.read_bytes()).hexdigest()
    assert len(digests) == 22


def test_packaged_oracle_is_byte_identical_to_authored_script():
    from pathlib import Path

    script = Path(__file__).resolve().parents[1] / "scripts/enoe_survey_oracle.R"
    assert resources.oracle_script_path().read_bytes() == script.read_bytes()


def test_missing_resource_fails_closed(monkeypatch, tmp_path):
    monkeypatch.setattr(resources, "files", lambda _package: tmp_path)
    monkeypatch.setattr(resources, "CHECKOUT_ROOT", None)
    with pytest.raises(FileNotFoundError, match="enoe-snapshots.json"):
        resources.snapshot_catalog_path()


@pytest.mark.parametrize("name", sorted(AUDITED_FONTS))
def test_audited_font_inventory(name):
    path = resources.font_path(name)
    assert path.is_file()
    assert resources.authored_resource_digests()[f"assets/fonts/{name}"] == hashlib.sha256(path.read_bytes()).hexdigest()
    assert hashlib.sha256(path.read_bytes()).hexdigest() == AUDITED_FONTS[name]


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


def test_missing_native_pdf_loader_fails_explicitly(monkeypatch):
    def broken_html(**_kwargs):
        return SimpleNamespace(write_pdf=lambda: (_ for _ in ()).throw(OSError("Pango unavailable")))

    monkeypatch.setitem(sys.modules, "weasyprint", SimpleNamespace(__version__="70.0", HTML=broken_html))
    with pytest.raises(RuntimeError, match="Pango/Fontconfig render failed"):
        resources.require_pdf_capability()
