"""Resolve authored resources shipped in the installed package."""

import hashlib
import importlib
from importlib.resources import files
from pathlib import Path

PACKAGE_ROOT = Path(__file__).resolve().parent
_candidate = PACKAGE_ROOT.parent
CHECKOUT_ROOT = _candidate if (_candidate / "pyproject.toml").is_file() and (_candidate / "tests").is_dir() else None


def _resource(package_directory: str, checkout_directory: str, filename: str) -> Path:
    path = PACKAGE_ROOT / package_directory / filename
    if path.is_file():
        return path
    if CHECKOUT_ROOT is not None:
        path = CHECKOUT_ROOT / checkout_directory / filename
        if path.is_file():
            return path
    raise FileNotFoundError(f"Missing bundled resource: {filename}")


def contract_path(name: str) -> Path:
    return _resource("contracts", "contracts", name)


def fixture_path() -> Path:
    return _resource("fixtures", "data/fixtures", "pilot.json")


def catalog_path() -> Path:
    return _resource("catalog", "data/catalog", "sources.json")


def _bundled(directory: str, filename: str) -> Path:
    """Use the package file, with an authored-tree fallback in a checkout."""
    resource = files("brujula").joinpath(directory, filename)
    if not resource.is_file():
        checkout_directory = {"catalog": "data/catalog", "fixtures": "data/fixtures", "contracts": "contracts"}.get(directory)
        if CHECKOUT_ROOT is not None and checkout_directory is not None:
            fallback = CHECKOUT_ROOT / checkout_directory / filename
            if fallback.is_file():
                return fallback
        raise FileNotFoundError(f"Missing bundled resource: {directory}/{filename}")
    # Wheel installation unpacks resources to a filesystem path. External tools
    # such as R require that stable path rather than a temporary context path.
    if not isinstance(resource, Path):
        raise RuntimeError(f"Resource requires an unpacked wheel: {directory}/{filename}")
    return resource


def require_installed_package_path(path: Path) -> Path:
    """For installed evidence, reject a resource resolved outside this package."""
    resolved = Path(path).resolve()
    if CHECKOUT_ROOT is None and not resolved.is_relative_to(PACKAGE_ROOT):
        raise FileNotFoundError(f"Installed resource escaped package: {path}")
    return resolved


def snapshot_catalog_path() -> Path:
    return _bundled("catalog", "enoe-snapshots.json")


def metric_catalog_path() -> Path:
    return _bundled("catalog", "enoe-metrics.json")


def aggregate_golden_path() -> Path:
    return _bundled("fixtures", "enoe-aggregate-golden.json")


def analysis_reference_path() -> Path:
    return _bundled("fixtures", "enoe-analysis-reference.json")


def coverage_pins_path() -> Path:
    return _bundled("fixtures", "enoe-analysis-coverage-pins.json")


def oracle_script_path() -> Path:
    return _bundled("oracle", "enoe_survey_oracle.R")


_AUTHORED_RESOURCES = {
    "catalog/sources.json": catalog_path,
    "catalog/enoe-snapshots.json": snapshot_catalog_path,
    "catalog/enoe-metrics.json": metric_catalog_path,
    "catalog/enoe-geography-equivalence.json": lambda: _bundled("catalog", "enoe-geography-equivalence.json"),
    "fixtures/pilot.json": fixture_path,
    "fixtures/analysis-v2-golden.json": lambda: _bundled("fixtures", "analysis-v2-golden.json"),
    "fixtures/enoe-aggregate-golden.json": aggregate_golden_path,
    "fixtures/enoe-analysis-reference.json": analysis_reference_path,
    "fixtures/enoe-analysis-coverage-pins.json": coverage_pins_path,
    "oracle/enoe_survey_oracle.R": oracle_script_path,
}

_SCHEMA_NAMES = (
    "agent-run.schema.json",
    "analysis-v2.schema.json",
    "dataset.schema.json",
    "insight.schema.json",
    "publication-v2.schema.json",
    "publication-manifest-v2.schema.json",
    "research-v2.schema.json",
    "research-v2-public.schema.json",
    "run.schema.json",
)

_FONT_NAMES = frozenset({
    "DejaVuSans.ttf", "DejaVuSans-Bold.ttf",
    "DejaVuSerif.ttf", "DejaVuSerif-Bold.ttf", "LICENSE_DEJAVU",
})


def font_path(name: str) -> Path:
    if name not in _FONT_NAMES:
        raise ValueError(f"Unapproved font resource: {name}")
    return _bundled("assets/fonts", name)


def require_pdf_capability() -> str:
    """Render a small PDF to prove both optional Python and native libraries work."""
    try:
        weasyprint = importlib.import_module("weasyprint")
    except (ImportError, OSError) as exc:
        raise RuntimeError(
            "PDF requires weasyprint==70.0 plus Pango/Fontconfig; on Windows set "
            "WEASYPRINT_DLL_DIRECTORIES to reviewed local DLLs, or install "
            "Pango on Ubuntu."
        ) from exc
    if getattr(weasyprint, "__version__", None) != "70.0":
        raise RuntimeError("PDF requires weasyprint==70.0")
    try:
        rendered = weasyprint.HTML(string="<html><body>Prueba áéíóú ñ</body></html>").write_pdf()
    except Exception as exc:
        raise RuntimeError(
            "PDF native Pango/Fontconfig render failed; check "
            "WEASYPRINT_DLL_DIRECTORIES on Windows or Pango on Ubuntu."
        ) from exc
    if not rendered.startswith(b"%PDF-"):
        raise RuntimeError("PDF native render did not produce a PDF")
    return weasyprint.__version__


def authored_resource_digests() -> dict[str, str]:
    """Hash the exact bytes consumed from each mandatory authored resource."""
    digests = {
        name: hashlib.sha256(accessor().read_bytes()).hexdigest()
        for name, accessor in _AUTHORED_RESOURCES.items()
    }
    for name in _SCHEMA_NAMES:
        digests[f"contracts/{name}"] = hashlib.sha256(
            _bundled("contracts", name).read_bytes()
        ).hexdigest()
    for name in sorted(_FONT_NAMES):
        digests[f"assets/fonts/{name}"] = hashlib.sha256(font_path(name).read_bytes()).hexdigest()
    return digests
