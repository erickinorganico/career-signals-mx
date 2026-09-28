"""Fail-closed checks for recorded release evidence; no publication side effects.

Receipts are intentionally distinct: installed hosts, independent content review,
closed local inventory, remote byte readback, and GSD traceability.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys
from urllib.request import Request, urlopen
import zipfile
from io import BytesIO

ROOT = Path(__file__).resolve().parents[1]
SHA = re.compile(r"[0-9a-f]{64}\Z")
COMMIT = re.compile(r"[0-9a-f]{40}\Z")
NAME = re.compile(r"[A-Za-z0-9][A-Za-z0-9._-]*\Z")
REPO = "erickinorganico/career-signals-mx"
API = f"https://api.github.com/repos/{REPO}"
ROLES = {"wheel", "report_pdf", "research_archive", "manifest", "checksums"}


class EvidenceError(ValueError):
    """The receipt does not establish its claimed gate."""


def require(condition: bool, message: str) -> None:
    if not condition:
        raise EvidenceError(message)


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def read_json(path: Path) -> dict:
    value = json.loads(path.read_text(encoding="utf-8"))
    require(isinstance(value, dict), "receipt must be an object")
    return value


def sha(value: object, label: str) -> str:
    require(isinstance(value, str) and SHA.fullmatch(value) is not None, f"invalid {label} SHA-256")
    return value


def commit(value: object, label: str) -> str:
    require(isinstance(value, str) and COMMIT.fullmatch(value) is not None, f"invalid {label} commit")
    return value


def path_inside(path: Path, root: Path) -> Path:
    resolved = path.resolve(strict=True)
    require(resolved.is_relative_to(root.resolve(strict=True)), "file escapes evidence root")
    require(resolved.is_file(), "evidence file missing")
    return resolved


def relative(name: object, label: str) -> str:
    require(isinstance(name, str) and name and "\\" not in name and not name.startswith("/"),
            f"unsafe {label}")
    require(not re.match(r"^[A-Za-z]:", name) and all(p not in {"", ".", ".."} for p in name.split("/")),
            f"unsafe {label}")
    return name


def checked_file(root: Path, name: object, expected: object = None) -> bytes:
    data = path_inside(root / relative(name, "evidence path"), root).read_bytes()
    if expected is not None:
        require(digest(data) == sha(expected, "evidence"), f"evidence hash differs: {name}")
    return data


def github_json(endpoint: str, authenticated: bool = False) -> dict:
    require(endpoint.startswith(API + "/"), "GitHub endpoint escapes pinned repository")
    if authenticated:
        result = subprocess.run(["gh", "api", endpoint], capture_output=True, text=True, timeout=45, check=True)
        value = json.loads(result.stdout)
    else:
        with urlopen(Request(endpoint, headers={"Accept": "application/vnd.github+json",
                                                "User-Agent": "career-signals-mx-release-check"}), timeout=30) as response:
            value = json.load(response)
    require(isinstance(value, dict), "GitHub API object missing")
    return value


def github_bytes(endpoint: str, authenticated: bool = False) -> bytes:
    require(endpoint.startswith(API + "/"), "GitHub endpoint escapes pinned repository")
    if authenticated:
        return subprocess.run(["gh", "api", "-H", "Accept: application/octet-stream", endpoint],
                              capture_output=True, timeout=120, check=True).stdout
    with urlopen(Request(endpoint, headers={"Accept": "application/octet-stream",
                                           "User-Agent": "career-signals-mx-release-check"}), timeout=120) as response:
        return response.read()


def tag_commit(tag: str) -> str:
    obj = github_json(f"{API}/git/ref/tags/{tag}")["object"]
    for _ in range(4):
        if obj.get("type") == "commit":
            return commit(obj.get("sha"), "tag")
        require(obj.get("type") == "tag", "tag does not resolve to commit")
        obj = github_json(f"{API}/git/tags/{commit(obj.get('sha'), 'annotated tag')}")["object"]
    raise EvidenceError("tag dereference depth exceeded")


def host(receipt: dict, root: Path) -> None:
    require(receipt.get("status") == "PASS", "host gate is not PASS")
    target = commit(receipt.get("target_commit"), "target")
    run = receipt.get("run") or {}
    require(isinstance(run.get("id"), int) and run["id"] > 0, "hosted run ID missing")
    live = github_json(f"{API}/actions/runs/{run['id']}", authenticated=True)
    require(live.get("repository", {}).get("full_name") == REPO and live.get("conclusion") == "success"
            and live.get("status") == "completed", "hosted run did not succeed in pinned repository")
    require(commit(live.get("head_sha"), "hosted run") == target, "hosted run targets different commit")
    require(live.get("path", "").startswith(".github/workflows/verify.yml"), "unexpected CI workflow")
    jobs = github_json(f"{API}/actions/runs/{run['id']}/jobs?per_page=100", authenticated=True).get("jobs", [])
    require(isinstance(jobs, list) and any(j.get("conclusion") == "success" and "windows" in j.get("name", "").lower() for j in jobs)
            and any(j.get("conclusion") == "success" and "ubuntu" in j.get("name", "").lower() for j in jobs),
            "successful Windows and Ubuntu jobs absent")
    artifacts = github_json(f"{API}/actions/runs/{run['id']}/artifacts?per_page=100", authenticated=True).get("artifacts", [])
    require(isinstance(artifacts, list), "CI artifact listing absent")
    require(receipt.get("package_version") == "1.0.0", "wrong final package version")
    approved = read_json(path_inside(root / relative(receipt.get("inventory_path"), "inventory path"), root))
    inventory(approved, root)
    require(approved.get("target_commit") == target, "host inventory target differs")
    wheel_item = next(i for i in approved["assets"] if i["role"] == "wheel")
    candidate_members = {n: row["sha256"] for n, row in _items(wheel_item["members"], "wheel members").items()
                         if n.startswith("brujula/")}
    require(candidate_members, "audited wheel code/resources absent")
    hosts = receipt.get("hosts")
    require(isinstance(hosts, dict) and set(hosts) == {"Windows", "Linux"}, "both hosts required")
    identities: set[tuple[str, str]] = set()
    for os_name, item in hosts.items():
        require(isinstance(item, dict), f"{os_name} host entry missing")
        artifact = next((a for a in artifacts if a.get("id") == item.get("artifact_id") and not a.get("expired")), None)
        require(artifact is not None and artifact.get("workflow_run", {}).get("head_sha", target) == target,
                f"{os_name} CI artifact absent")
        payload = github_bytes(f"{API}/actions/artifacts/{item['artifact_id']}/zip", authenticated=True)
        with zipfile.ZipFile(BytesIO(payload)) as archive:
            names = set(archive.namelist())
            require(names == {"phase4-installed-runtime.json", "installed.whl"}, f"{os_name} CI artifact members differ")
            data = archive.read("phase4-installed-runtime.json")
            wheel = archive.read("installed.whl")
        require(digest(data) == sha(item.get("receipt_sha256"), os_name), f"{os_name} receipt hash differs")
        observed = json.loads(data)
        require(observed.get("status") == "PASS" and observed.get("host_os") == os_name,
                f"{os_name} helper did not pass")
        require(observed.get("package_version") == "1.0.0" and observed.get("installed_outside_checkout") is True,
                f"{os_name} installation identity differs")
        require(observed.get("module_within_installed_package") is True
                and observed.get("missing_resource_blocked") is True, f"{os_name} resource guards absent")
        pdf = observed.get("pdf") or {}
        require(pdf.get("searchable_spanish") is True and pdf.get("embedded_dejavu") is True
                and pdf.get("altered_font_blocked") is True and pdf.get("local_url_rejections") == 4,
                f"{os_name} Spanish PDF/asset proof absent")
        require(isinstance(observed.get("native_versions"), dict) and observed["native_versions"],
                f"{os_name} native proof absent")
        wheel_hash = sha(observed.get("wheel_sha256"), "wheel")
        require(wheel_hash == digest(wheel) == sha(item.get("wheel_sha256"), f"{os_name} wheel"),
                f"{os_name} host wheel identity differs")
        with zipfile.ZipFile(BytesIO(wheel)) as package:
            member_hashes = {n: digest(package.read(n)) for n in package.namelist() if n.startswith("brujula/") and not n.endswith("/")}
        require(member_hashes == candidate_members == item.get("installed_members_sha256"),
                f"{os_name} installed wheel members differ from audited release wheel")
        identities.add((sha(observed.get("installed_code_and_resource_sha256"), "code/resources"),
                        json.dumps(observed.get("authored_resource_sha256"), sort_keys=True)))
    require(len(identities) == 1, "host code/resource identities differ")
    code_hash, _ = identities.pop()
    require(code_hash == sha(receipt.get("installed_code_and_resource_sha256"), "expected code/resources"),
            "expected code/resource identity differs")


def review(receipt: dict, root: Path) -> None:
    require(receipt.get("status") == "PASS", "review is not PASS")
    reviewer = receipt.get("reviewer") or {}
    require(isinstance(reviewer, dict) and reviewer.get("independence_basis")
            and (reviewer.get("agent") or reviewer.get("name")), "independent reviewer basis missing")
    source = receipt.get("input") or {}
    run_path = relative(source.get("source_run_path"), "source run path")
    manifest_bytes = checked_file(root, f"{run_path}/manifest.json", source.get("manifest_sha256"))
    manifest = json.loads(manifest_bytes)
    require(manifest.get("run_id") == source.get("run_id"), "review source run differs")
    sealed = manifest.get("artifact_hashes") or {}
    require(len(sealed) == 73 and sealed.get("analysis.json") == source.get("analysis_sha256"),
            "review analysis or 73-item manifest differs")
    required = {"manifest.json", "analysis.json", "report.html", "report.md", "report.pdf",
                "exports/public.duckdb", "assets/fonts/LICENSE_DEJAVU"}
    required.update(p for p in sealed if p.startswith("figures/") or p.startswith("exports/"))
    artifacts = receipt.get("inspected_artifacts")
    require(isinstance(artifacts, list) and set(artifacts) == required and len(artifacts) == len(required),
            "independent review scope differs from sealed artifacts")
    for name in required:
        if name != "manifest.json":
            checked_file(root, f"{run_path}/{name}", sealed[name])
    report = checked_file(root, receipt.get("reviewer_report_path"), receipt.get("reviewer_report_sha256"))
    require(report.strip() and receipt.get("reviewer", {}).get("report_author"), "attributable reviewer report absent")
    findings = receipt.get("findings")
    require(isinstance(findings, list) and receipt.get("material_open_findings") == 0,
            "material review finding remains open")
    require(isinstance(receipt.get("affected_reruns"), list), "affected rerun disposition absent")
    require(receipt.get("final_release_approved") is False or receipt.get("final_custody_evidence"),
            "content review cannot silently approve final custody")
    for finding in findings:
        require(isinstance(finding, dict) and finding.get("disposition") in {"resolved", "not_material"},
                "review finding disposition missing")
        if finding.get("disposition") == "resolved":
            require(finding.get("rerun_id"), "resolved finding lacks affected rerun")
    evidence = receipt.get("local_evidence")
    require(isinstance(evidence, list) and evidence, "review evidence absent")
    for item in evidence:
        checked_file(root, item.get("path"), item.get("sha256"))
    for rerun in receipt["affected_reruns"]:
        require(isinstance(rerun, dict) and rerun.get("finding_id") and rerun.get("evidence_path"),
                "affected rerun link absent")
        checked_file(root, rerun["evidence_path"], rerun.get("evidence_sha256"))


def _members(path: Path) -> dict[str, tuple[int, str]]:
    with zipfile.ZipFile(path) as archive:
        names = archive.namelist()
        require(len(names) == len(set(names)), "duplicate archive member")
        result = {}
        for name in names:
            relative(name.rstrip("/"), "archive member")
            if name.endswith("/"):
                continue
            data = archive.read(name)
            result[name] = (len(data), digest(data))
        return result


def _items(items: object, label: str) -> dict[str, dict]:
    require(isinstance(items, list) and items, f"{label} item set missing")
    mapped = {}
    for item in items:
        require(isinstance(item, dict), f"{label} item invalid")
        name = item.get("name") or item.get("path")
        relative(name, f"{label} name")
        require(name not in mapped, f"{label} duplicate name")
        require(type(item.get("bytes")) is int and item["bytes"] >= 0, f"{label} size absent")
        sha(item.get("sha256"), label)
        require(item.get("release_approved") is True, f"{label} item is not approved")
        mapped[name] = item
    return mapped


def inventory(receipt: dict, root: Path) -> None:
    require(receipt.get("status") == "PASS" and receipt.get("release_approved") is True,
            "release inventory is not approved")
    commit(receipt.get("target_commit"), "inventory target")
    run_path = relative(receipt.get("source_run_path"), "source run path")
    manifest_data = checked_file(root, f"{run_path}/manifest.json", receipt.get("manifest_sha256"))
    manifest = json.loads(manifest_data)
    sealed = manifest.get("artifact_hashes") or {}
    require(manifest.get("run_id") == receipt.get("source_run_id") and len(sealed) == 73,
            "sealed source run or 73-item manifest differs")
    require(receipt.get("acceptance_path") == "docs/evidence/phase-04-publication-acceptance.json",
            "Phase 4 acceptance path differs")
    acceptance = read_json(path_inside(root / receipt["acceptance_path"], root))
    accepted = acceptance.get("integrated_installed_publication") or {}
    require(acceptance.get("status") == "PASS_PHASE4_ACCEPTANCE"
            and accepted.get("run_id") == manifest["run_id"]
            and accepted.get("manifest_sha256") == digest(manifest_data)
            and accepted.get("content_artifact_count") == 73,
            "Phase 4 acceptance does not bind sealed run")
    for name, expected in sealed.items():
        checked_file(root, f"{run_path}/{relative(name, 'sealed member')}", expected)
    checked_file(root, f"{run_path}/receipt.json", manifest.get("receipt_sha256"))
    items = _items(receipt.get("assets"), "asset")
    require({item.get("role") for item in items.values()} == ROLES and len(items) == 5,
            "required five release asset roles absent")
    require(receipt.get("asset_review_path") == "docs/evidence/phase-05-asset-review.json",
            "asset review path differs")
    audit = read_json(path_inside(root / receipt["asset_review_path"], root))
    require(audit.get("status") == "PASS_CANDIDATE_BOUND" and audit.get("technical_distribution_approved") is True
            and audit.get("target_commit") == receipt["target_commit"]
            and audit.get("source_run_id") == manifest["run_id"]
            and audit.get("source_manifest_sha256") == digest(manifest_data),
            "independent asset review does not bind target and source run")
    role_keys = {"wheel": "wheel_sha256", "research_archive": "research_archive_sha256",
                 "report_pdf": "report_pdf_sha256", "manifest": "loose_manifest_sha256",
                 "checksums": "checksum_file_sha256"}
    audited_assets = audit.get("assets")
    require(isinstance(audited_assets, dict)
            and audited_assets == {role_keys[item["role"]]: item["sha256"] for item in items.values()},
            "independent asset review does not bind exact five asset hashes")
    decisions = audit.get("item_decisions") or []
    require(isinstance(decisions, list) and len(decisions) == sum(1 + len(i.get("members", [])) for i in items.values()),
            "item-level redistribution review is incomplete")
    indexed = {(d.get("asset"), d.get("member")): d for d in decisions}
    require(len(indexed) == len(decisions), "duplicate item decision")
    def decision(asset: str, member: str | None, size: int, value: str) -> None:
        reviewed = indexed.get((asset, member)) or {}
        require(reviewed.get("bytes") == size and reviewed.get("sha256") == value
                and reviewed.get("redistributable") is True and reviewed.get("decision") == "APPROVED_CANDIDATE"
                and reviewed.get("basis"), f"asset/member lacks hash-bound redistribution decision: {asset}/{member}")
    require(isinstance(receipt.get("asset_dir"), str) and receipt["asset_dir"], "asset directory missing")
    directory_path = root / relative(receipt["asset_dir"], "asset directory")
    require(not directory_path.is_symlink(), "asset directory symlink")
    directory = directory_path.resolve(strict=True)
    require(directory.is_relative_to(root.resolve(strict=True)) and directory.is_dir(), "asset directory escapes evidence root")
    actual = {}
    for p in directory.rglob("*"):
        require(not p.is_symlink(), "asset symlink")
        require(p.is_file(), "unexpected asset directory or non-file entry")
        actual[p.relative_to(directory).as_posix()] = p
    require(set(actual) == set(items), "asset set differs from closed allowlist")
    for name, item in items.items():
        data = actual[name].read_bytes()
        require(len(data) == item["bytes"] and digest(data) == item["sha256"], f"asset differs: {name}")
        decision(name, None, item["bytes"], item["sha256"])
        if name.endswith((".zip", ".whl")):
            expected = _items(item.get("members"), f"{name} members")
            observed = _members(actual[name])
            require(set(expected) == set(observed), f"{name} member set differs")
            for member, size_hash in observed.items():
                require(size_hash == (expected[member]["bytes"], expected[member]["sha256"]),
                        f"{name} member differs: {member}")
            if item["role"] == "research_archive":
                expected_run = {f"research/{p}": h for p, h in sealed.items()}
                expected_run["research/manifest.json"] = digest(manifest_data)
                expected_run["research/receipt.json"] = manifest["receipt_sha256"]
                require({p: h for p, (_, h) in observed.items() if p.startswith("research/")} == expected_run,
                        "research archive does not exactly map sealed run")
            for member in expected:
                decision(name, member, expected[member]["bytes"], expected[member]["sha256"])
        if item["role"] == "manifest":
            require(data == manifest_data, "loose manifest differs from sealed run")
        if item["role"] == "report_pdf":
            require(digest(data) == sealed["report.pdf"], "loose PDF differs from sealed run")
        if item["role"] == "wheel":
            require(item.get("target_commit") == receipt["target_commit"], "wheel target commit differs")
    sums = next(actual[n].read_text(encoding="utf-8") for n, i in items.items() if i["role"] == "checksums")
    checksums_name = next(n for n, i in items.items() if i["role"] == "checksums")
    expected_sums = "".join(f"{items[n]['sha256']}  {n}\n" for n in sorted(items) if n != checksums_name)
    require(sums == expected_sums, "checksums do not bind exact release assets")
    require(receipt.get("privacy_review") == "PASS" and receipt.get("license_review") == "PASS"
            and receipt.get("terms_review") == "PASS", "privacy/license/terms gate absent")


def remote(receipt: dict, root: Path, stage: str) -> None:
    require(receipt.get("tag") == "v1.0.0", "wrong release tag")
    target = commit(receipt.get("target_commit"), "release target")
    inventory_path = path_inside(root / receipt["inventory_path"], root)
    approved = read_json(inventory_path)
    inventory(approved, root)
    require(approved.get("target_commit") == target, "remote target lacks approved inventory")
    expected = _items(approved.get("assets"), "approved asset")
    if stage == "draft":
        release_id = receipt.get("release_id")
        require(isinstance(release_id, int) and release_id > 0, "draft release ID absent")
        live = github_json(f"{API}/releases/{release_id}", authenticated=True)
    else:
        live = github_json(f"{API}/releases/tags/v1.0.0")
        require(tag_commit("v1.0.0") == target, "public tag resolves to different commit")
    require(live.get("tag_name") == "v1.0.0" and live.get("draft") is (stage == "draft")
            and live.get("target_commitish") == target and not live.get("prerelease"),
            "live release state/target differs")
    require(live.get("id") == receipt.get("release_id"), "release identity differs")
    live_assets = live.get("assets") or []
    require(isinstance(live_assets, list) and len(live_assets) == len(expected), "live asset count differs")
    actual = {a.get("name"): a for a in live_assets}
    require(set(actual) == set(expected), "live asset set differs")
    for name, item in expected.items():
        observed = actual[name]
        require(isinstance(observed.get("id"), int) and observed.get("size") == item["bytes"]
                and observed.get("state") == "uploaded", f"live asset metadata differs: {name}")
        if stage == "public":
            url = observed.get("browser_download_url", "")
            require(url == f"https://github.com/{REPO}/releases/download/v1.0.0/{name}",
                    f"public URL missing: {name}")
            with urlopen(url, timeout=120) as response:
                data = response.read()
        else:
            data = github_bytes(f"{API}/releases/assets/{observed['id']}", authenticated=True)
        require(len(data) == item["bytes"] and digest(data) == item["sha256"],
                f"downloaded asset differs: {name}")


def trace(receipt: dict, root: Path) -> None:
    require(receipt.get("status") == "PASS", "GSD trace is not PASS")
    registry = (root / ".planning/REQUIREMENTS.md").read_text(encoding="utf-8")
    required = set(re.findall(r"^- \[[ x]\] \*\*([A-Z]+-\d+)\*\*:", registry, re.M))
    require(len(required) == 31, "canonical milestone requirement registry differs")
    require(set(receipt.get("required_ids") or []) == required, "required IDs differ from canonical registry")
    rows = receipt.get("requirements")
    require(isinstance(rows, list) and len(rows) == 31, "requirement trace row count differs")
    mapped = {}
    for row in rows:
        require(isinstance(row, dict) and row.get("id") not in mapped, "duplicate requirement ID")
        mapped[row["id"]] = row
        require(row.get("status") == "satisfied", f"requirement unresolved: {row['id']}")
        for key in ("plan", "summary", "verification", "evidence"):
            paths = row.get(key)
            if isinstance(paths, str):
                paths = [paths]
            require(isinstance(paths, list) and paths, f"{row['id']} {key} missing")
            require(len(set(paths)) == len(paths), "duplicate trace evidence path")
            for value in paths:
                require(isinstance(value, str), "evidence path invalid")
                path = path_inside(root / relative(value, "trace path"), root)
                content = path.read_text(encoding="utf-8", errors="replace")
                require(row["id"] in content, f"trace evidence does not cite requirement: {row['id']}")
                if key == "verification":
                    require(re.search(r"(?im)^(status|result|verdict):\s*(pass|verified|complete)\b", content)
                            or re.search(r"(?im)^\*\*status:\*\*\s*(pass|verified|complete)\b", content),
                            f"verification evidence has no accepted status: {value}")
                if key == "evidence":
                    require(re.search(r"(?im)\b(pass|accepted|verified)\b", content),
                            f"evidence lacks accepted result: {value}")
        require(len({p for key in ("plan", "summary", "verification", "evidence")
                     for p in ([row[key]] if isinstance(row[key], str) else row[key])}) >= 3,
                f"{row['id']} placeholder evidence reused")
    require(set(mapped) == required, "missing or unplanned requirement ID")
    require(receipt.get("all_phases_verified") is True and receipt.get("nyquist_compliant") is True
            and receipt.get("material_security_open") == 0 and receipt.get("uat_open") == 0
            and receipt.get("audit_open") == 0, "GSD closure gate remains open")
    for key in ("security_report", "validation_report", "milestone_audit"):
        item = receipt.get(key) or {}
        content = checked_file(root, item.get("path"), item.get("sha256")).decode("utf-8")
        require(re.search(r"(?im)^(status|result|verdict):\s*(pass|verified|complete)\b", content),
                f"{key} is not accepted")
        require(target := receipt.get("target_commit"), "trace target absent")
        require(target in content, f"{key} does not bind target commit")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("gate", choices=("host", "review", "inventory", "remote", "trace"))
    parser.add_argument("receipt", type=Path)
    parser.add_argument("--stage", choices=("draft", "public"))
    args = parser.parse_args()
    try:
        evidence = read_json(args.receipt)
        if args.gate == "remote":
            require(args.stage is not None, "remote stage required")
            remote(evidence, ROOT, args.stage)
        else:
            globals()[args.gate](evidence, ROOT)
    except (EvidenceError, OSError, ValueError, KeyError, zipfile.BadZipFile,
            subprocess.SubprocessError) as exc:
        print(json.dumps({"status": "FAIL", "gate": args.gate, "reason": str(exc)}, ensure_ascii=False))
        return 1
    print(json.dumps({"status": "PASS", "gate": args.gate}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
