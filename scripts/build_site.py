"""Build the static Pages directory from the approved v1.0.0 research archive."""

from __future__ import annotations

import argparse
import hashlib
from html.parser import HTMLParser
import json
import os
from pathlib import Path, PurePosixPath
import re
import shutil
import stat
import sys
import tempfile
from urllib.parse import unquote, urlsplit
from urllib.request import urlopen
import zipfile


ROOT = Path(__file__).resolve().parents[1]
INVENTORY = ROOT / "docs/evidence/phase-05-release-inventory.json"
ARCHIVE_URL = "https://github.com/erickinorganico/career-signals-mx/releases/download/v1.0.0/brujula-laboral-mx-investigacion.zip"
DEFAULT_OUTPUT = ROOT / ".cache/pages"
MARKER = ".pages-build.json"
CSS_URL = re.compile(r"url\(\s*(['\"]?)(.*?)\1\s*\)", re.I)
CSS_IMPORT = re.compile(r"@import\s+(['\"])(.*?)\1", re.I)


class BuildError(ValueError):
    pass


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _safe_name(name: str) -> str:
    if not name or "\\" in name or "\x00" in name or name.startswith("/"):
        raise BuildError(f"unsafe ZIP path: {name!r}")
    parts = name.split("/")
    if any(part in ("", ".", "..") or part.endswith((" ", ".")) or
           any(char in part for char in '<>:"|?*') or
           part.split(".")[0].upper() in {"CON", "PRN", "AUX", "NUL", *(f"COM{i}" for i in range(1, 10)), *(f"LPT{i}" for i in range(1, 10))}
           for part in parts):
        raise BuildError(f"unsafe ZIP path: {name!r}")
    return name


def _approved_members(inventory: Path) -> tuple[dict, dict[str, dict]]:
    document = json.loads(inventory.read_text(encoding="utf-8"))
    if document.get("status") != "PASS" or document.get("release_approved") is not True:
        raise BuildError("release inventory is not approved")
    assets = [a for a in document["assets"] if a.get("role") == "research_archive"]
    if len(assets) != 1 or not assets[0].get("release_approved"):
        raise BuildError("research archive is not uniquely release approved")
    asset = assets[0]
    expected: dict[str, dict] = {}
    folded: set[str] = set()
    for member in asset["members"]:
        name = _safe_name(member["name"])
        if not member.get("release_approved") or name in expected or name.casefold() in folded:
            raise BuildError(f"unapproved or duplicate inventory member: {name}")
        expected[name] = member
        folded.add(name.casefold())
    if not expected or not any(name.startswith("research/") for name in expected):
        raise BuildError("research members missing from inventory")
    return asset, expected


def _read_archive(source: Path | None, expected_asset: dict) -> bytes:
    if source is None:
        with urlopen(ARCHIVE_URL, timeout=60) as response:
            data = response.read(int(expected_asset["bytes"]) + 1)
    else:
        data = source.read_bytes()
    if len(data) != expected_asset["bytes"] or _sha256(data) != expected_asset["sha256"]:
        raise BuildError("research archive size or SHA-256 differs from release inventory")
    return data


def _extract_approved(data: bytes, expected: dict[str, dict], stage: Path) -> None:
    from io import BytesIO

    with zipfile.ZipFile(BytesIO(data)) as archive:
        infos = archive.infolist()
        names: set[str] = set()
        folded: set[str] = set()
        for info in infos:
            name = _safe_name(info.filename)
            if info.is_dir() or name in names or name.casefold() in folded:
                raise BuildError(f"directory or duplicate ZIP member: {name}")
            if stat.S_IFMT(info.external_attr >> 16) == stat.S_IFLNK:
                raise BuildError(f"ZIP symlink refused: {name}")
            names.add(name)
            folded.add(name.casefold())
        if names != expected.keys():
            raise BuildError(f"ZIP members differ from release inventory: missing={sorted(expected.keys() - names)}, extra={sorted(names - expected.keys())}")
        for info in infos:
            meta = expected[info.filename]
            if info.file_size != meta["bytes"]:
                raise BuildError(f"ZIP member declared size differs: {info.filename}")
            content = archive.read(info)
            if len(content) != meta["bytes"] or _sha256(content) != meta["sha256"]:
                raise BuildError(f"ZIP member size or SHA-256 differs: {info.filename}")
            if info.filename.startswith("research/") or info.filename in ("LICENSE", "THIRD_PARTY_NOTICES.md"):
                target = stage / PurePosixPath(info.filename)
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(content)


class _HTMLLinks(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.ids: set[str] = set()
        self.links: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = dict(attrs)
        if values.get("id"):
            self.ids.add(values["id"] or "")
        for key in ("href", "src", "poster"):
            if values.get(key):
                self.links.append(values[key] or "")
        if values.get("srcset"):
            self.links.extend(piece.strip().split()[0] for piece in (values["srcset"] or "").split(",") if piece.strip())
        if values.get("style"):
            self.links.extend(match.group(2) for match in CSS_URL.finditer(values["style"] or ""))


def _check_links(stage: Path) -> None:
    html: dict[Path, _HTMLLinks] = {}
    for path in stage.rglob("*.html"):
        parser = _HTMLLinks()
        parser.feed(path.read_text(encoding="utf-8"))
        html[path.resolve()] = parser
    links: list[tuple[Path, str]] = [(path, url) for path, parser in html.items() for url in parser.links]
    for path in stage.rglob("*.css"):
        css = path.read_text(encoding="utf-8")
        links.extend((path.resolve(), match.group(2)) for match in CSS_URL.finditer(css))
        links.extend((path.resolve(), match.group(2)) for match in CSS_IMPORT.finditer(css))
    root = stage.resolve()
    for origin, url in links:
        parsed = urlsplit(url)
        if parsed.scheme or parsed.netloc:
            continue
        decoded = unquote(parsed.path)
        if decoded.startswith(("/", "\\")) or "\\" in decoded:
            raise BuildError(f"unsafe local link in {origin.relative_to(root)}: {url}")
        target = (origin.parent / decoded).resolve() if decoded else origin
        if not target.is_relative_to(root) or not target.is_file():
            raise BuildError(f"missing local link in {origin.relative_to(root)}: {url}")
        if parsed.fragment and target.suffix.lower() == ".html":
            parser = html.get(target)
            if parser is None or unquote(parsed.fragment) not in parser.ids:
                raise BuildError(f"missing anchor in {origin.relative_to(root)}: {url}")


def build_site(archive: Path | None = None, output: Path = DEFAULT_OUTPUT, *, inventory: Path = INVENTORY, site: Path | None = None) -> Path:
    site = site or ROOT / "site"
    output = output.resolve()
    source_dir = site.resolve()
    if output == ROOT or ROOT.is_relative_to(output) or output == source_dir or output.is_relative_to(source_dir) or source_dir.is_relative_to(output):
        raise BuildError("output overlaps project or site source")
    asset, members = _approved_members(inventory)
    content = _read_archive(archive, asset)
    output.parent.mkdir(parents=True, exist_ok=True)
    stage = Path(tempfile.mkdtemp(prefix=".pages-stage-", dir=output.parent))
    backup: Path | None = None
    try:
        _extract_approved(content, members, stage)
        for name in ("index.html", "styles.css"):
            source = site / name
            if not source.is_file():
                raise BuildError(f"site source missing: {source}")
            shutil.copyfile(source, stage / name)
        landing = stage / "index.html"
        template = landing.read_text(encoding="utf-8")
        placeholders = {"<!-- HERO_CHART -->": "hero_markup", "<!-- TREND_CHARTS -->": "trend_markup", "<!-- TERRITORY_CHARTS -->": "territory_markup"}
        if any(token in template for token in placeholders):
            if not all(template.count(token) == 1 for token in placeholders):
                raise BuildError("chart template must contain each placeholder exactly once")
            if __package__:
                from .site_charts import render_charts
            else:
                from site_charts import render_charts
            fragments = render_charts(stage)
            for token, key in placeholders.items():
                template = template.replace(token, fragments[key])
            landing.write_text(template, encoding="utf-8", newline="\n")
        _check_links(stage)
        (stage / MARKER).write_text(json.dumps({"builder": "brujula-pages-v1", "archive_sha256": asset["sha256"]}) + "\n", encoding="utf-8")
        if output.exists():
            marker = output / MARKER
            try:
                previous = json.loads(marker.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError):
                raise BuildError(f"existing output is not marked as a Pages build: {output}") from None
            if previous != {"builder": "brujula-pages-v1", "archive_sha256": asset["sha256"]}:
                raise BuildError(f"existing output has an invalid Pages build marker: {output}")
            backup = Path(tempfile.mkdtemp(prefix=".pages-backup-", dir=output.parent))
            backup.rmdir()
            os.replace(output, backup)
        try:
            os.replace(stage, output)
        except Exception:
            if backup is not None:
                os.replace(backup, output)
                backup = None
            raise
        if backup is not None:
            shutil.rmtree(backup)
        return output
    finally:
        if stage.exists():
            shutil.rmtree(stage)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--archive", type=Path, help="Use a local copy of the fixed v1.0.0 release archive")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    try:
        output = args.output.resolve()
        cache = (ROOT / ".cache").resolve()
        if output == cache or not output.is_relative_to(cache):
            raise BuildError("--output must be a directory beneath the project's .cache")
        print(build_site(args.archive, args.output))
        return 0
    except (BuildError, OSError, zipfile.BadZipFile, KeyError, json.JSONDecodeError) as exc:
        print(f"site build blocked: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
