"""Resolve authored resources shipped in the installed package."""

import hashlib
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
    "catalog/enoe-snapshots.json": snapshot_catalog_path,
    "catalog/enoe-metrics.json": metric_catalog_path,
    "fixtures/enoe-aggregate-golden.json": aggregate_golden_path,
    "fixtures/enoe-analysis-reference.json": analysis_reference_path,
    "fixtures/enoe-analysis-coverage-pins.json": coverage_pins_path,
    "oracle/enoe_survey_oracle.R": oracle_script_path,
}

_SCHEMA_NAMES = (
    "analysis-v2.schema.json",
    "research-v2.schema.json",
    "research-v2-public.schema.json",
)


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
    return digests
