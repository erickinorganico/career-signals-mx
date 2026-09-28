"""Synthetic fixtures for the release ZIP gate and atomic Pages output."""

import hashlib
import json
from pathlib import Path
import sys
import zipfile

import pytest

from scripts.build_site import BuildError, build_site, main


def _hash(content):
    return hashlib.sha256(content).hexdigest()


def _fixture(tmp_path, *, landing='<a href="research/report.html#part">Report</a>'):
    members = {
        "LICENSE": b"Synthetic test license",
        "THIRD_PARTY_NOTICES.md": b"Synthetic test notice",
        "research/report.html": b'<h1 id="part">Synthetic report</h1><img src="figures/chart.svg">',
        "research/figures/chart.svg": b'<svg xmlns="http://www.w3.org/2000/svg"/>',
    }
    archive = tmp_path / "synthetic.zip"
    with zipfile.ZipFile(archive, "w") as zip_file:
        for name, content in members.items():
            zip_file.writestr(name, content)
    raw = archive.read_bytes()
    inventory = tmp_path / "inventory.json"
    inventory.write_text(json.dumps({"status": "PASS", "release_approved": True, "assets": [{
        "name": "synthetic.zip", "role": "research_archive", "release_approved": True,
        "bytes": len(raw), "sha256": _hash(raw),
        "members": [{"name": name, "bytes": len(content), "sha256": _hash(content), "release_approved": True}
                    for name, content in members.items()],
    }]}), encoding="utf-8")
    site = tmp_path / "site"
    site.mkdir()
    (site / "index.html").write_text(f'<main id="home">{landing}</main>', encoding="utf-8")
    (site / "styles.css").write_text("body { color: navy; }", encoding="utf-8")
    return archive, inventory, site


def _build(tmp_path, archive, inventory, site):
    return build_site(archive, tmp_path / "pages", inventory=inventory, site=site)


def test_builds_approved_archive_and_links(tmp_path):
    archive, inventory, site = _fixture(tmp_path)
    output = _build(tmp_path, archive, inventory, site)
    assert (output / "research/report.html").is_file()
    assert (output / "research/figures/chart.svg").is_file()
    assert (output / "LICENSE").read_bytes() == b"Synthetic test license"
    assert (output / "THIRD_PARTY_NOTICES.md").is_file()
    assert not list(tmp_path.glob(".pages-stage-*"))


def test_replaces_previous_output_only_after_validation(tmp_path):
    archive, inventory, site = _fixture(tmp_path)
    output = tmp_path / "pages"
    _build(tmp_path, archive, inventory, site)
    (output / "stale.txt").write_text("old", encoding="utf-8")
    _build(tmp_path, archive, inventory, site)
    assert not (output / "stale.txt").exists()
    assert (output / "index.html").is_file()


def test_refuses_to_replace_unmarked_directory(tmp_path):
    archive, inventory, site = _fixture(tmp_path)
    output = tmp_path / "pages"
    output.mkdir()
    (output / "user.txt").write_text("keep", encoding="utf-8")
    with pytest.raises(BuildError, match="not marked"):
        _build(tmp_path, archive, inventory, site)
    assert (output / "user.txt").read_text(encoding="utf-8") == "keep"


def test_cli_rejects_output_outside_project_cache(monkeypatch, tmp_path):
    monkeypatch.setattr(sys, "argv", ["build_site.py", "--output", str(tmp_path)])
    assert main() == 1


def test_rejects_output_overlapping_site_source(tmp_path):
    archive, inventory, site = _fixture(tmp_path)
    with pytest.raises(BuildError, match="overlaps"):
        build_site(archive, site, inventory=inventory, site=site)
    assert (site / "index.html").is_file()


def test_rejects_archive_hash_mismatch_without_touching_output(tmp_path):
    archive, inventory, site = _fixture(tmp_path)
    output = tmp_path / "pages"
    output.mkdir()
    (output / "old.txt").write_text("old", encoding="utf-8")
    archive.write_bytes(archive.read_bytes() + b"changed")
    with pytest.raises(BuildError, match="archive size or SHA-256"):
        _build(tmp_path, archive, inventory, site)
    assert (output / "old.txt").read_text(encoding="utf-8") == "old"
    assert sorted(p.name for p in output.iterdir()) == ["old.txt"]


@pytest.mark.parametrize("extra", ["research/unlisted.txt", "../escape.txt", "research/report.html"])
def test_rejects_extra_unsafe_or_duplicate_zip_members(tmp_path, extra):
    archive, inventory, site = _fixture(tmp_path)
    with zipfile.ZipFile(archive, "a") as zip_file:
        zip_file.writestr(extra, "Synthetic extra")
    data = json.loads(inventory.read_text(encoding="utf-8"))
    raw = archive.read_bytes()
    data["assets"][0].update(bytes=len(raw), sha256=_hash(raw))
    inventory.write_text(json.dumps(data), encoding="utf-8")
    with pytest.raises(BuildError, match="ZIP member|unsafe ZIP path"):
        _build(tmp_path, archive, inventory, site)
    assert not (tmp_path / "pages").exists()
    assert not (tmp_path / "escape.txt").exists()


@pytest.mark.parametrize("landing", [
    '<a href="research/report.html#absent">Broken anchor</a>',
    '<img src="research/figures/missing.svg">',
    '<a href="../outside.html">Outside</a>',
])
def test_rejects_broken_local_links_and_preserves_previous_output(tmp_path, landing):
    archive, inventory, site = _fixture(tmp_path, landing=landing)
    output = tmp_path / "pages"
    output.mkdir()
    (output / "old.txt").write_text("old", encoding="utf-8")
    with pytest.raises(BuildError, match="missing anchor|missing local link"):
        _build(tmp_path, archive, inventory, site)
    assert (output / "old.txt").read_text(encoding="utf-8") == "old"
    assert sorted(p.name for p in output.iterdir()) == ["old.txt"]


def test_rejects_member_hash_mismatch_even_when_archive_hash_matches(tmp_path):
    archive, inventory, site = _fixture(tmp_path)
    data = json.loads(inventory.read_text(encoding="utf-8"))
    data["assets"][0]["members"][0]["sha256"] = "0" * 64
    inventory.write_text(json.dumps(data), encoding="utf-8")
    with pytest.raises(BuildError, match="ZIP member size or SHA-256"):
        _build(tmp_path, archive, inventory, site)
    assert not (tmp_path / "pages").exists()


@pytest.mark.parametrize("level", ["inventory", "asset", "member"])
def test_rejects_unapproved_archive_or_member(tmp_path, level):
    archive, inventory, site = _fixture(tmp_path)
    data = json.loads(inventory.read_text(encoding="utf-8"))
    asset = data["assets"][0]
    if level == "inventory":
        data["release_approved"] = False
    elif level == "asset":
        asset["release_approved"] = False
    else:
        asset["members"][0]["release_approved"] = False
    inventory.write_text(json.dumps(data), encoding="utf-8")
    with pytest.raises(BuildError, match="approved|unapproved"):
        _build(tmp_path, archive, inventory, site)
    assert not (tmp_path / "pages").exists()
