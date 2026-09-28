"""Release gate controls use sealed bytes and mocked GitHub boundaries."""

import json
from pathlib import Path
import zipfile
from io import BytesIO

import pytest

from scripts import verify_release as v

TARGET = "a" * 40


def put(root: Path, name: str, data: bytes) -> None:
    path = root / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)


def fixture(root: Path) -> dict:
    run = "run/r1"
    content = {f"exports/table-{i:02d}.csv": f"row-{i}".encode() for i in range(66)}
    content.update({"analysis.json": b"analysis", "report.pdf": b"pdf", "report.html": b"html",
                    "report.md": b"markdown", "figures/one.svg": b"figure",
                    "exports/public.duckdb": b"duckdb", "assets/fonts/LICENSE_DEJAVU": b"license"})
    assert len(content) == 73
    for name, data in content.items():
        put(root, f"{run}/{name}", data)
    put(root, f"{run}/receipt.json", b"receipt")
    manifest = {"run_id": "r1", "artifact_hashes": {n: v.digest(b) for n, b in content.items()},
                "receipt_sha256": v.digest(b"receipt")}
    manifest_bytes = json.dumps(manifest).encode()
    put(root, f"{run}/manifest.json", manifest_bytes)
    put(root, "docs/evidence/phase-04-publication-acceptance.json", json.dumps({
        "status": "PASS_PHASE4_ACCEPTANCE", "integrated_installed_publication": {
            "run_id": "r1", "manifest_sha256": v.digest(manifest_bytes), "content_artifact_count": 73}}).encode())
    decision = b"Reviewed redistributable assets"
    put(root, "decision.txt", decision)
    approval = {"redistribution_decision": "approved", "decision_evidence_path": "decision.txt",
                "decision_evidence_sha256": v.digest(decision)}
    folder = root / "assets"
    folder.mkdir()
    with zipfile.ZipFile(folder / "research.zip", "w") as z:
        for name, data in content.items():
            z.writestr("research/" + name, data)
        z.writestr("research/manifest.json", manifest_bytes)
        z.writestr("research/receipt.json", b"receipt")
    with zipfile.ZipFile(folder / "package.whl", "w") as z:
        z.writestr("brujula/__init__.py", "version=1")
    (folder / "report.pdf").write_bytes(b"pdf")
    (folder / "manifest.json").write_bytes(manifest_bytes)
    roles = {"research.zip": "research_archive", "package.whl": "wheel", "report.pdf": "report_pdf",
             "manifest.json": "manifest", "SHA256SUMS.txt": "checksums"}
    (folder / "SHA256SUMS.txt").write_text("".join(
        f"{v.digest((folder / n).read_bytes())}  {n}\n" for n in sorted(roles) if n != "SHA256SUMS.txt"))
    items = []
    for name, role in roles.items():
        data = (folder / name).read_bytes()
        item = {"name": name, "role": role, "bytes": len(data), "sha256": v.digest(data),
                "release_approved": True, **approval}
        if role == "wheel":
            item["target_commit"] = TARGET
        if name.endswith((".zip", ".whl")):
            with zipfile.ZipFile(folder / name) as z:
                item["members"] = [{"name": n, "bytes": len(z.read(n)), "sha256": v.digest(z.read(n)),
                                    "release_approved": True, **approval} for n in z.namelist()]
        items.append(item)
    decisions = []
    for item in items:
        decisions.append({"asset": item["name"], "member": None, "bytes": item["bytes"],
                          "sha256": item["sha256"], "redistributable": True,
                          "decision": "APPROVED_CANDIDATE", "basis": "reviewed"})
        for member in item.get("members", []):
            decisions.append({"asset": item["name"], "member": member["name"], "bytes": member["bytes"],
                              "sha256": member["sha256"], "redistributable": True,
                              "decision": "APPROVED_CANDIDATE", "basis": "reviewed"})
    put(root, "docs/evidence/phase-05-asset-review.json", json.dumps({
        "status": "PASS_CANDIDATE_BOUND", "technical_distribution_approved": True,
        "target_commit": TARGET,
        "source_run_id": "r1", "source_manifest_sha256": v.digest(manifest_bytes),
        "assets": {"wheel_sha256": next(i["sha256"] for i in items if i["role"] == "wheel"),
                   "research_archive_sha256": next(i["sha256"] for i in items if i["role"] == "research_archive"),
                   "report_pdf_sha256": next(i["sha256"] for i in items if i["role"] == "report_pdf"),
                   "loose_manifest_sha256": next(i["sha256"] for i in items if i["role"] == "manifest"),
                   "checksum_file_sha256": next(i["sha256"] for i in items if i["role"] == "checksums")},
        "item_decisions": decisions}).encode())
    return {"status": "PASS", "release_approved": True, "target_commit": TARGET,
            "source_run_path": run, "source_run_id": "r1", "manifest_sha256": v.digest(manifest_bytes),
            "acceptance_path": "docs/evidence/phase-04-publication-acceptance.json", "asset_dir": "assets",
            "assets": items, "privacy_review": "PASS", "license_review": "PASS", "terms_review": "PASS",
            "asset_review_path": "docs/evidence/phase-05-asset-review.json"}


def test_inventory_sealed_source_and_required_assets(tmp_path):
    receipt = fixture(tmp_path)
    v.inventory(receipt, tmp_path)
    receipt["manifest_sha256"] = "f" * 64
    with pytest.raises(v.EvidenceError, match="hash differs"):
        v.inventory(receipt, tmp_path)
    receipt["manifest_sha256"] = v.digest((tmp_path / "run/r1/manifest.json").read_bytes())
    receipt["assets"] = [i for i in receipt["assets"] if i["role"] != "report_pdf"]
    with pytest.raises(v.EvidenceError, match="roles"):
        v.inventory(receipt, tmp_path)


def test_inventory_rejects_cross_target_audit_and_changed_role_hash(tmp_path):
    receipt = fixture(tmp_path)
    receipt["target_commit"] = "b" * 40
    next(item for item in receipt["assets"] if item["role"] == "wheel")["target_commit"] = "b" * 40
    with pytest.raises(v.EvidenceError, match="target and source run"):
        v.inventory(receipt, tmp_path)
    receipt["target_commit"] = TARGET
    next(item for item in receipt["assets"] if item["role"] == "wheel")["target_commit"] = TARGET
    audit_path = tmp_path / "docs/evidence/phase-05-asset-review.json"
    audit = json.loads(audit_path.read_text())
    audit["assets"]["wheel_sha256"] = "f" * 64
    audit_path.write_text(json.dumps(audit))
    with pytest.raises(v.EvidenceError, match="five asset hashes"):
        v.inventory(receipt, tmp_path)


def test_nested_asset_and_unsafe_members_fail(tmp_path):
    receipt = fixture(tmp_path)
    put(tmp_path, "assets/nested/extra", b"extra")
    with pytest.raises(v.EvidenceError, match="unexpected asset directory"):
        v.inventory(receipt, tmp_path)
    for name in ("C:/private", "..\\private", "a/../private"):
        with pytest.raises(v.EvidenceError, match="unsafe"):
            v.relative(name, "member")
        unsafe = tmp_path / "unsafe.zip"
        with zipfile.ZipFile(unsafe, "w") as z:
            z.writestr(name, "data")
        with pytest.raises(v.EvidenceError, match="unsafe"):
            v._members(unsafe)


def test_draft_reads_live_release_and_bytes(tmp_path, monkeypatch):
    approved = fixture(tmp_path)
    put(tmp_path, "inventory.json", json.dumps(approved).encode())
    assets = [{"id": i + 1, "name": item["name"], "size": item["bytes"], "state": "uploaded"}
              for i, item in enumerate(approved["assets"])]
    live = {"id": 42, "tag_name": "v1.0.0", "draft": True, "target_commitish": TARGET,
            "prerelease": False, "assets": assets}
    monkeypatch.setattr(v, "github_json", lambda *args, **kwargs: live)
    monkeypatch.setattr(v, "github_bytes", lambda endpoint, authenticated=False: (
        tmp_path / "assets" / next(a["name"] for a in assets if endpoint.endswith("/" + str(a["id"])))).read_bytes())
    receipt = {"tag": "v1.0.0", "target_commit": TARGET, "inventory_path": "inventory.json", "release_id": 42}
    v.remote(receipt, tmp_path, "draft")
    live["draft"] = False
    with pytest.raises(v.EvidenceError, match="state/target"):
        v.remote(receipt, tmp_path, "draft")


def test_public_checks_tag_ref(tmp_path, monkeypatch):
    approved = fixture(tmp_path)
    put(tmp_path, "inventory.json", json.dumps(approved).encode())
    monkeypatch.setattr(v, "github_json", lambda *args, **kwargs: {"id": 42})
    monkeypatch.setattr(v, "tag_commit", lambda tag: "b" * 40)
    receipt = {"tag": "v1.0.0", "target_commit": TARGET, "inventory_path": "inventory.json", "release_id": 42}
    with pytest.raises(v.EvidenceError, match="tag resolves"):
        v.remote(receipt, tmp_path, "public")


def test_review_rejects_partial_scope(tmp_path):
    inventory = fixture(tmp_path)
    receipt = {"status": "PASS", "reviewer": {"agent": "other", "independence_basis": "separate",
               "report_author": "person"}, "input": {"source_run_path": "run/r1", "run_id": "r1",
               "manifest_sha256": inventory["manifest_sha256"],
               "analysis_sha256": v.digest(b"analysis")}, "inspected_artifacts": ["manifest.json"],
               "findings": [], "material_open_findings": 0, "affected_reruns": [], "final_release_approved": False,
               "reviewer_report_path": "decision.txt", "reviewer_report_sha256": v.digest(b"Reviewed redistributable assets"),
               "local_evidence": [{"path": "decision.txt", "sha256": v.digest(b"Reviewed redistributable assets")}]}
    with pytest.raises(v.EvidenceError, match="scope"):
        v.review(receipt, tmp_path)


def test_trace_canonical_ids_and_failed_verification(tmp_path):
    registry = (v.ROOT / ".planning/REQUIREMENTS.md").read_bytes()
    put(tmp_path, ".planning/REQUIREMENTS.md", registry)
    ids = sorted(set(v.re.findall(r"^- \[[ x]\] \*\*([A-Z]+-\d+)\*\*:", registry.decode(), v.re.M)))
    for name, status in (("plan.md", ""), ("summary.md", ""), ("verification.md", "status: FAIL"),
                         ("evidence.md", "accepted")):
        put(tmp_path, name, (" ".join(ids) + "\n" + status).encode())
    rows = [{"id": i, "status": "satisfied", "plan": "plan.md", "summary": "summary.md",
             "verification": "verification.md", "evidence": "evidence.md"} for i in ids]
    receipt = {"status": "PASS", "required_ids": ids, "requirements": rows}
    with pytest.raises(v.EvidenceError, match="accepted status"):
        v.trace(receipt, tmp_path)
    receipt["required_ids"] = ids[1:] + ["FAKE-01"]
    with pytest.raises(v.EvidenceError, match="canonical"):
        v.trace(receipt, tmp_path)


def test_host_rejects_forged_run_and_stale_wheel(tmp_path, monkeypatch):
    approved = fixture(tmp_path)
    put(tmp_path, "inventory.json", json.dumps(approved).encode())
    wheel = (tmp_path / "assets/package.whl").read_bytes()
    helper = {"status": "PASS", "host_os": "Windows", "package_version": "1.0.0",
              "installed_outside_checkout": True, "module_within_installed_package": True,
              "missing_resource_blocked": True, "wheel_sha256": v.digest(wheel),
              "installed_code_and_resource_sha256": "c" * 64,
              "authored_resource_sha256": {"x": "d" * 64}, "native_versions": {"x": "1"},
              "pdf": {"searchable_spanish": True, "embedded_dejavu": True,
                      "altered_font_blocked": True, "local_url_rejections": 4}}
    def artifact(os_name):
        helper["host_os"] = os_name
        raw = json.dumps(helper).encode()
        archive = BytesIO()
        with zipfile.ZipFile(archive, "w") as z:
            z.writestr("phase4-installed-runtime.json", raw)
            z.writestr("installed.whl", wheel)
        return raw, archive.getvalue()
    win, winzip = artifact("Windows")
    linux, linuxzip = artifact("Linux")
    entries = {"Windows": {"artifact_id": 11, "receipt_sha256": v.digest(win),
                           "wheel_sha256": v.digest(wheel),
                           "installed_members_sha256": {"brujula/__init__.py": v.digest(b"version=1")}},
               "Linux": {"artifact_id": 12, "receipt_sha256": v.digest(linux),
                         "wheel_sha256": v.digest(wheel),
                         "installed_members_sha256": {"brujula/__init__.py": v.digest(b"version=1")}}}
    live = {"repository": {"full_name": v.REPO}, "conclusion": "success", "status": "completed",
            "head_sha": TARGET, "path": ".github/workflows/verify.yml"}
    jobs = {"jobs": [{"name": "verify (windows-latest)", "conclusion": "success"},
                     {"name": "verify (ubuntu-latest)", "conclusion": "success"}]}
    artifacts = {"artifacts": [{"id": 11, "expired": False}, {"id": 12, "expired": False}]}
    def read(endpoint, authenticated=False):
        assert authenticated
        return jobs if endpoint.endswith("/jobs?per_page=100") else (
            artifacts if endpoint.endswith("/artifacts?per_page=100") else live)
    monkeypatch.setattr(v, "github_json", read)
    monkeypatch.setattr(v, "github_bytes", lambda endpoint, authenticated=False: winzip if endpoint.endswith("/11/zip") else linuxzip)
    receipt = {"status": "PASS", "target_commit": TARGET, "run": {"id": 123},
               "inventory_path": "inventory.json",
               "package_version": "1.0.0", "hosts": entries,
               "installed_code_and_resource_sha256": "c" * 64}
    v.host(receipt, tmp_path)
    live["head_sha"] = "b" * 40
    with pytest.raises(v.EvidenceError, match="different commit"):
        v.host(receipt, tmp_path)
    live["head_sha"] = TARGET
    entries["Windows"]["wheel_sha256"] = "f" * 64
    with pytest.raises(v.EvidenceError, match="wheel identity"):
        v.host(receipt, tmp_path)
