"""Resolve the same authored resources in a checkout or an installed wheel."""
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
