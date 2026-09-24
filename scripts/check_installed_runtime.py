"""Audit one freshly installed wheel from a working directory outside checkout.

The receipt contains package/resource hashes and PDF capability facts only;
it does not copy a source snapshot, person row, fixture payload or local path.
"""

from __future__ import annotations

import argparse
from email.parser import BytesParser
import hashlib
from importlib import metadata
import json
import os
from pathlib import Path
import platform
import subprocess
import sys
from tempfile import TemporaryDirectory
import zipfile


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _font_embedded(reader) -> bool:
    for page in reader.pages:
        resources = page.get("/Resources", {}).get_object()
        for entry in resources.get("/Font", {}).values():
            font = entry.get_object()
            descendants = [value.get_object() for value in font.get("/DescendantFonts", [])]
            for candidate in (font, *descendants):
                descriptor = candidate.get("/FontDescriptor")
                if descriptor is not None and "/FontFile2" in descriptor.get_object():
                    return True
    return False


def _native_versions() -> dict[str, str]:
    if platform.system() == "Windows":
        observed = os.environ.get("BRUJULA_NATIVE_SOURCE_SHA256", "").lower()
        if observed != "ab1151f210b4e6bb7aa7a79e91a67e8ddb760094c107bfda55241b6aaefe7d53":
            raise RuntimeError("reviewed Windows native source receipt is absent or changed")
        return {"weasyprint_onedir_sha256": observed}
    names = ("libpango-1.0-0", "libharfbuzz0b", "libpangoft2-1.0-0", "libharfbuzz-subset0")
    result = subprocess.run(["dpkg-query", "-W", "-f=${binary:Package}=${Version}\\n", *names],
                            capture_output=True, text=True, check=True)
    versions = {name.split(":", 1)[0]: version for line in result.stdout.splitlines()
                if "=" in line for name, version in [line.split("=", 1)]}
    if set(versions) != set(names):
        raise RuntimeError("required native package receipt is incomplete")
    return versions


def check_installed(checkout: Path, wheel: Path) -> dict:
    checkout = checkout.resolve(strict=True)
    wheel = wheel.resolve(strict=True)
    if Path.cwd().resolve().is_relative_to(checkout):
        raise RuntimeError("installed check must run outside checkout")
    import brujula
    from brujula import resources
    from brujula.pdf_v2 import LocalOnlyFetcher, render_pdf
    from brujula.report_v2 import FONT_NAMES, FONT_SHA256, stage_report_fonts
    from pypdf import PdfReader
    import weasyprint

    module = Path(brujula.__file__).resolve(strict=True)
    package = module.parent
    if module.is_relative_to(checkout) or resources.CHECKOUT_ROOT is not None:
        raise RuntimeError("checkout package imported instead of installed wheel")
    installed_version = metadata.version("career-signals-mx")
    digests = resources.authored_resource_digests()
    if not digests:
        raise RuntimeError("authored resource inventory is empty")
    if not all((package / name).is_file() for name in digests):
        raise RuntimeError("authored resource escaped installed package")
    for name, digest in digests.items():
        if _sha(package / name) != digest:
            raise RuntimeError("installed authored resource hash differs")
    try:
        resources.contract_path("missing-phase4.schema.json")
    except FileNotFoundError:
        missing_resource_blocked = True
    else:
        raise RuntimeError("missing resource did not fail closed")
    if resources.require_pdf_capability() != "70.0" or weasyprint.__version__ != "70.0":
        raise RuntimeError("reviewed PDF capability unavailable")
    with zipfile.ZipFile(wheel) as archive:
        members = archive.namelist()
        if len(members) != len(set(members)) or not all(name and not name.startswith("/") for name in members):
            raise RuntimeError("unsafe wheel member inventory")
        if any(name.startswith(("raw/", "private/", ".cache/")) or
               name.endswith((".zip", ".env", ".pem", ".key")) or
               "/__pycache__/" in name for name in members):
            raise RuntimeError("wheel contains forbidden data or credential path")
        if not all("brujula/" + name in members for name in digests):
            raise RuntimeError("wheel omits an authored resource")
        wheel_code = {name for name in members if name.startswith("brujula/") and name.endswith(".py")}
        installed_code = {"brujula/" + path.relative_to(package).as_posix()
                          for path in package.rglob("*.py")}
        if not wheel_code or installed_code != wheel_code:
            raise RuntimeError("installed Python module inventory differs from wheel")
        identity_members = wheel_code | {"brujula/" + name for name in digests}
        installed_hashes = {}
        for name in sorted(identity_members):
            path = package / name.removeprefix("brujula/")
            if not path.is_file():
                raise RuntimeError("installed wheel member is missing")
            expected_hash = hashlib.sha256(archive.read(name)).hexdigest()
            observed_hash = _sha(path)
            if observed_hash != expected_hash:
                raise RuntimeError("installed wheel member differs from current wheel")
            installed_hashes[name] = observed_hash
        identity_digest = hashlib.sha256(json.dumps(installed_hashes, sort_keys=True,
                                                   separators=(",", ":")).encode()).hexdigest()
        metadata_members = [name for name in members if name.endswith(".dist-info/METADATA")]
        if len(metadata_members) != 1:
            raise RuntimeError("wheel metadata inventory differs")
        wheel_metadata = BytesParser().parsebytes(archive.read(metadata_members[0]))
        wheel_name = wheel_metadata.get("Name", "").lower().replace("_", "-")
        if wheel_name != "career-signals-mx" or wheel_metadata.get("Version") != installed_version:
            raise RuntimeError("installed version differs from current wheel metadata")
    with TemporaryDirectory(prefix="brujula-installed-pdf-") as dirname:
        root = Path(dirname)
        html = root / "report.html"
        html.write_text('<!doctype html><html lang="es"><head><meta charset="utf-8">'
                        '<style>@font-face{font-family:LocalSans;src:url("assets/fonts/DejaVuSans.ttf")}'
                        'body{font-family:LocalSans}</style></head>'
                        '<body><h1>Árbol, profesión y México</h1><p>Investigación laboral sin red.</p></body></html>',
                        encoding="utf-8")
        staged = stage_report_fonts(root)
        if set(staged) != {f"assets/fonts/{name}" for name in FONT_NAMES}:
            raise RuntimeError("staged font inventory differs")
        allowed = {name: _sha(root / name) for name in ("report.html", *staged)}
        if any(allowed[f"assets/fonts/{name}"] != FONT_SHA256[name] for name in FONT_NAMES):
            raise RuntimeError("staged font identity differs")
        fetcher = LocalOnlyFetcher(root, allowed)
        denied = 0
        for url in ("https://example.org/escape", "data:text/plain,bad", "../escape.png",
                    (root / "missing.png").as_uri()):
            try:
                fetcher(url)
            except (ValueError, FileNotFoundError):
                denied += 1
        if denied != 4:
            raise RuntimeError("local-only PDF fetch guard differs")
        damaged = root / staged[0]
        saved = damaged.read_bytes()
        damaged.write_bytes(b"changed")
        try:
            try:
                render_pdf(html, root, root / "invalid.pdf", allowed_assets=allowed)
            except (ValueError, FileNotFoundError):
                changed_font_blocked = True
            else:
                raise RuntimeError("altered staged font was accepted")
        finally:
            damaged.write_bytes(saved)
        if (root / "invalid.pdf").exists():
            raise RuntimeError("invalid PDF was written")
        pdf = render_pdf(html, root, root / "report.pdf", allowed_assets=allowed)
        reader = PdfReader(pdf)
        text = "\n".join(page.extract_text() for page in reader.pages)
        if "Árbol, profesión y México" not in text or not _font_embedded(reader):
            raise RuntimeError("Spanish text or embedded font missing from installed PDF")
        pdf_facts = {"sha256": _sha(pdf), "pages": len(reader.pages),
                     "searchable_spanish": True, "embedded_dejavu": True,
                     "local_url_rejections": denied, "altered_font_blocked": changed_font_blocked}
    return {"schema_version": "1.0", "status": "PASS", "host_os": platform.system(),
            "python_version": platform.python_version(), "package_version": installed_version,
            "installed_outside_checkout": True, "module_within_installed_package": module.is_relative_to(package),
            "wheel_sha256": _sha(wheel), "wheel_member_count": len(members),
            "installed_code_count": len(wheel_code),
            "installed_code_and_resource_sha256": identity_digest,
            "authored_resource_count": len(digests), "authored_resource_sha256": dict(sorted(digests.items())),
            "missing_resource_blocked": missing_resource_blocked,
            "weasyprint_version": weasyprint.__version__, "pdf": pdf_facts,
            "native_versions": _native_versions()}


def main() -> int:
    parser = argparse.ArgumentParser(description="Audit an outside-checkout installed Brújula wheel")
    parser.add_argument("--checkout-root", type=Path, required=True)
    parser.add_argument("--wheel", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = check_installed(args.checkout_root, args.wheel)
    target = args.output.resolve()
    target.parent.mkdir(parents=True, exist_ok=True)
    temporary = target.with_name(target.name + ".tmp")
    temporary.write_text(json.dumps(result, sort_keys=True, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    os.replace(temporary, target)
    print(json.dumps({"status": result["status"], "wheel_sha256": result["wheel_sha256"],
                      "resource_count": result["authored_resource_count"], "pdf_pages": result["pdf"]["pages"]}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
