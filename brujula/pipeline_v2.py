"""Sealed offline v2 publication and live source resolution."""

from __future__ import annotations

import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path, PurePosixPath
from uuid import uuid4

from jsonschema import Draft202012Validator, FormatChecker

from .acquisition import resolve_snapshot
from .analysis_v2 import _content_digest, _digest
from .enoe_acceptance import CODE_FILES, NUMERIC_RESOURCES, _code_hashes, _numeric_resource_digests
from .export_v2 import _table_data, export_public_tables
from .findings_v2 import build_analysis_packet, validate_analysis_packet
from .pipeline import atomic_json, immutable_bytes, json_bytes, now
from .publication_v2 import build_publication_model, validate_publication_model
from .resources import authored_resource_digests, contract_path
from .runlock import BuildLock
from .source_inventory import PERIODS, inventory_all

SNAPSHOTS = tuple("enoe_" + period.lower().replace("-", "_") for period in PERIODS)
RUN_ID = re.compile(r"\d{8}T\d{6}-[a-f0-9]{12}\Z")
HEX = re.compile(r"[a-f0-9]{64}\Z")
FONT_NAMES = ("DejaVuSans.ttf", "DejaVuSans-Bold.ttf", "DejaVuSerif.ttf",
              "DejaVuSerif-Bold.ttf", "LICENSE_DEJAVU")
FONT_PATHS = {f"assets/fonts/{name}" for name in FONT_NAMES}
BASE_PATHS = {"analysis.json", "report.html", "report.md", "report.pdf"} | FONT_PATHS
RECEIPT_PRIVATE = {"started_at", "completed_at"}


def _sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _read(path: Path) -> tuple[dict, str]:
    raw = path.read_bytes()
    value = json.loads(raw)
    if not isinstance(value, dict):
        raise ValueError("JSON object required")
    return value, _sha(raw)


def _strict_roots(*paths: Path) -> tuple[Path, ...]:
    roots = tuple(Path(path).resolve() for path in paths)
    if any(a.is_relative_to(b) or b.is_relative_to(a)
           for i, a in enumerate(roots) for b in roots[i + 1:]):
        raise ValueError("source, output and audit roots overlap")
    return roots


def _safe_file(root: Path, name: str) -> Path:
    if not isinstance(name, str) or not name or "\\" in name or ":" in name:
        raise ValueError("unsafe artifact path")
    rel = PurePosixPath(name)
    if rel.is_absolute() or any(p in ("", ".", "..") for p in rel.parts) or rel.as_posix() != name:
        raise ValueError("unsafe artifact path")
    path = root.joinpath(*rel.parts)
    if path.is_symlink() or any(p.is_symlink() for p in path.parents if p != root):
        raise ValueError("symlink artifact path")
    if not path.resolve().is_relative_to(root.resolve()):
        raise ValueError("escaped artifact path")
    return path


def _attempt_id() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S") + "-" + uuid4().hex[:12]


def _sources(source_root: Path) -> list[dict]:
    # resolve_snapshot checks each immutable receipt and raw ZIP; inventory_all
    # additionally checks all members and latest attempt at both ends.
    records = inventory_all(source_root)
    if tuple(item["snapshot_id"] for item in records) != SNAPSHOTS:
        raise ValueError("exact eight source inventory required")
    result = []
    for item in records:
        _, receipt = resolve_snapshot(item["snapshot_id"], source_root)
        if (receipt["run_id"] != item["receipt_run_id"]
                or receipt["sha256"] != item["raw_sha256"]
                or receipt["url"] != item["source_url"]):
            raise ValueError("source receipt identity changed")
        result.append({"snapshot_id": item["snapshot_id"],
                       "acquisition_attempt_id": item["receipt_run_id"],
                       "source_url": item["source_url"],
                       "source_sha256": item["raw_sha256"],
                       "period_id": item["period"],
                       "receipt_sha256": item["receipt_sha256"]})
    return result


def _accepted(audit_dir: Path, selected: Path | None = None) -> tuple[dict, str]:
    current, _ = _read(audit_dir / "current.json")
    if current.get("status") != "PASS" or current.get("operation") is not None:
        raise ValueError("numerical current is not accepted")
    attempt_id = current.get("attempt_id")
    if not isinstance(attempt_id, str) or not re.fullmatch(r"[a-f0-9-]{36}", attempt_id):
        raise ValueError("invalid numerical attempt ID")
    immutable = audit_dir / "attempts" / f"{attempt_id}.json"
    if selected is not None and Path(selected).resolve() != immutable.resolve():
        raise ValueError("selected acceptance is not current")
    receipt, digest = _read(immutable)
    if (receipt.get("status") != "PASS" or receipt.get("operation") is not None
            or {k: v for k, v in receipt.items() if k not in RECEIPT_PRIVATE} != current):
        raise ValueError("numerical current and immutable receipt disagree")
    if set(receipt.get("snapshots", {})) != set(SNAPSHOTS):
        raise ValueError("numerical eight-snapshot inventory incomplete")
    if set(receipt.get("code_sha256", {})) != CODE_FILES or receipt["code_sha256"] != _code_hashes():
        raise ValueError("numerical code inventory changed")
    if set(receipt.get("resource_sha256", {})) != NUMERIC_RESOURCES or receipt["resource_sha256"] != _numeric_resource_digests():
        raise ValueError("numerical resource inventory changed")
    return receipt, digest


def _summary(packet: dict, acceptance: dict, acceptance_sha: str,
             sources: list[dict]) -> dict:
    manifest = packet["source_manifest"]
    proof = manifest["acceptance"]
    fields = ("public_content_sha256", "numeric_digest", "requested_count")
    expected = {"status": acceptance["status"],
                "numeric_content_digest": acceptance["numeric_content_digest"],
                "metric_manifest_sha256": acceptance["metric_manifest_sha256"],
                "code_sha256": dict(sorted(acceptance["code_sha256"].items())),
                "snapshots": {sid: {k: acceptance["snapshots"][sid][k] for k in fields}
                              for sid in SNAPSHOTS}}
    if proof != expected:
        raise ValueError("packet and selected numerical acceptance differ")
    if {item["snapshot_id"]: item["acquisition_attempt_id"] for item in sources} != acceptance["source_receipt_ids"]:
        raise ValueError("selected acceptance source identities differ")
    for source in sources:
        sid = source["snapshot_id"]
        packet_source = manifest["sources"][sid]
        if (packet_source["sha256"] != source["source_sha256"]
                or packet_source["url"] != source["source_url"]
                or packet_source["period_id"] != source["period_id"]):
            raise ValueError("packet and current sources differ")
    publics, _ = _accepted_payloads(acceptance, sources)
    for sid in SNAPSHOTS:
        public = publics[sid]
        packet_source = manifest["sources"][sid]
        if (public["periods"][0]["id"] != packet_source["period_id"]
                or public["methods"][0]["version"] != packet_source["method_version"]):
            raise ValueError("packet and accepted method or period differ")
    return {"attempt_id": acceptance["attempt_id"], "receipt_sha256": acceptance_sha,
            "numeric_content_digest": acceptance["numeric_content_digest"],
            "metric_manifest_sha256": acceptance["metric_manifest_sha256"],
            "code_sha256": expected["code_sha256"],
            "resource_sha256": dict(sorted(acceptance["resource_sha256"].items())),
            "source_manifest": manifest}


def _export_names(model: dict) -> set[str]:
    tables = _table_data(model)
    if len(tables) != 22:
        raise ValueError("public table definitions changed")
    names = {"public.duckdb", "data-dictionary.md"}
    for table in tables:
        stem = "public-records" if table == "public_records" else table.replace("_", "-")
        names.update({f"{stem}.csv", f"{stem}.parquet"})
    if len(names) != 46:
        raise ValueError("public export names collide")
    return names


def _figure_names(model: dict) -> set[str]:
    # Report filename convention is one ASCII slug per declared figure ID.
    names = set()
    for figure in model["figure_links"]:
        fid = figure["figure_id"]
        if not isinstance(fid, str) or not fid.startswith("figure:"):
            raise ValueError("invalid figure ID")
        slug = fid.removeprefix("figure:")
        if not re.fullmatch(r"[a-z0-9-]+", slug):
            raise ValueError("unsafe figure slug")
        names.update({f"figures/{slug}.svg", f"figures/{slug}.png"})
    if len(names) != 2 * len(model["figure_links"]):
        raise ValueError("figure filename collision")
    return names


def _expected(model: dict) -> set[str]:
    return BASE_PATHS | _figure_names(model) | {f"exports/{name}" for name in _export_names(model)}


def _disk_files(run: Path) -> set[str]:
    result = set()
    for path in run.rglob("*"):
        if path.is_symlink():
            raise ValueError("symlink in sealed run")
        if path.is_file():
            result.add(path.relative_to(run).as_posix())
    return result


def _inventory(run: Path, expected: set[str]) -> dict[str, str]:
    disk = _disk_files(run) - {"journal.json", "receipt.json", "manifest.json", "publication-failure.json"}
    if disk != expected:
        raise ValueError("publication artifact inventory differs")
    return {name: _sha(_safe_file(run, name).read_bytes()) for name in sorted(expected)}


def _render(model: dict, run: Path) -> dict[str, str]:
    from .pdf_v2 import render_pdf
    from .report_v2 import FONT_SHA256, render_publication

    rendered = render_publication(model, run)
    expected_figures = _figure_names(model)
    returned_figures = {item[key] for item in rendered["figures"] for key in ("svg", "png")}
    if returned_figures != expected_figures or set(rendered["fonts"]) != FONT_PATHS:
        raise ValueError("renderer declared assets differ")
    report_names = {"report.html", "report.md"} | expected_figures | FONT_PATHS
    if set(rendered["artifact_hashes"]) != report_names:
        raise ValueError("renderer artifact map incomplete")
    for name, digest in rendered["artifact_hashes"].items():
        if _sha(_safe_file(run, name).read_bytes()) != digest:
            raise ValueError("renderer asset changed")
    for font in FONT_NAMES:
        if rendered["artifact_hashes"][f"assets/fonts/{font}"] != FONT_SHA256[font]:
            raise ValueError("staged font differs from package audit")
    render_pdf(run / "report.html", run, run / "report.pdf",
               allowed_assets=rendered["artifact_hashes"])
    names = _export_names(model)
    result = export_public_tables(model, run / "exports")
    if set(result["files"]) != names or _disk_files(run / "exports") != names:
        raise ValueError("export inventory differs")
    return _inventory(run, _expected(model))


def _manifest_schema() -> dict:
    return json.loads(contract_path("publication-manifest-v2.schema.json").read_text(encoding="utf-8"))


def _validate_manifest(manifest: dict) -> None:
    Draft202012Validator(_manifest_schema(), format_checker=FormatChecker()).validate(manifest)


def _failure(run: Path, output_root: Path, run_id: str, stage: str, exc: Exception) -> dict:
    reason = {"schema_version": "2.0", "run_id": run_id, "status": "BLOCKED",
              "build_status": "FAILED", "stage": stage,
              "error": {"code": type(exc).__name__[:60], "reason": "publication stage failed"},
              "completed_at": now()}
    target = run / ("publication-failure.json" if (run / "receipt.json").exists() else "receipt.json")
    immutable_bytes(target, json_bytes(reason))
    atomic_json(run / "journal.json", reason)
    atomic_json(output_root / "current.json", reason)
    return reason


def build_publication(source_root: Path, output_root: Path, audit_dir: Path,
                      analysis_packet_path: Path) -> dict:
    """Seal a validated aggregate run, then atomically promote current."""
    source_root, output_root, audit_dir = _strict_roots(source_root, output_root, audit_dir)
    analysis_packet_path = Path(analysis_packet_path).resolve()
    if (analysis_packet_path.is_relative_to(source_root)
            or analysis_packet_path.is_relative_to(output_root)):
        raise ValueError("analysis input and source/output roots overlap")
    output_root.mkdir(parents=True, exist_ok=True)
    with BuildLock(output_root):
        run_id = _attempt_id()
        run = output_root / "runs" / run_id
        run.mkdir(parents=True, exist_ok=False)
        stage = "start"
        atomic_json(output_root / "current.json", {"schema_version": "2.0", "run_id": run_id,
                                                    "status": "BLOCKED", "build_status": "RUNNING"})
        atomic_json(run / "journal.json", {"run_id": run_id, "build_status": "RUNNING"})
        try:
            stage = "source"
            sources = _sources(source_root)
            stage = "acceptance"
            acceptance, acceptance_sha = _accepted(audit_dir)
            stage = "analysis"
            packet, _ = _read(analysis_packet_path)
            if validate_analysis_packet(packet):
                raise ValueError("analysis packet rejected")
            summary = _summary(packet, acceptance, acceptance_sha, sources)
            immutable_bytes(run / "analysis.json", json_bytes(packet))
            persisted, _ = _read(run / "analysis.json")
            if persisted != packet or validate_analysis_packet(persisted):
                raise ValueError("persisted analysis changed")
            model = build_publication_model(persisted)
            if validate_publication_model(model):
                raise ValueError("publication model rejected")
            stage = "render_export"
            artifact_hashes = _render(model, run)
            if set(artifact_hashes) != _expected(model):
                raise ValueError("staged artifact set differs")
            if (_sources(source_root) != sources or _accepted(audit_dir)[1] != acceptance_sha
                    or _summary(packet, acceptance, acceptance_sha, sources) != summary):
                raise ValueError("input identity changed during build")
            stage = "receipt"
            receipt = {"schema_version": "2.0", "run_id": run_id, "status": "REVIEW",
                       "build_status": "SUCCEEDED", "numerical_acceptance_attempt_id": acceptance["attempt_id"],
                       "numerical_acceptance_sha256": acceptance_sha,
                       "numeric_content_digest": acceptance["numeric_content_digest"],
                       "analysis_content_digest": packet["content_digest"],
                       "publication_content_digest": model["content_digest"],
                       "source_dependencies": sources, "completed_at": now()}
            immutable_bytes(run / "receipt.json", json_bytes(receipt))
            stage = "manifest"
            manifest = {"schema_version": "2.0", "run_id": run_id, "status": "REVIEW",
                        "source_dependencies": sources, "numerical_acceptance": summary,
                        "analysis_content_digest": packet["content_digest"],
                        "publication_content_digest": model["content_digest"],
                        "artifact_hashes": artifact_hashes,
                        "receipt_sha256": _sha((run / "receipt.json").read_bytes()),
                        "sealed_at": now()}
            _validate_manifest(manifest)
            immutable_bytes(run / "manifest.json", json_bytes(manifest))
            stage = "pointer"
            pointer = {"schema_version": "2.0", "run_id": run_id, "status": "REVIEW",
                       "build_status": "SUCCEEDED", "manifest_sha256": _sha((run / "manifest.json").read_bytes())}
            atomic_json(output_root / "current.json", pointer)
            stage = "final_index"
            atomic_json(run / "journal.json", {"run_id": run_id, "build_status": "SUCCEEDED"})
            return {"current": pointer, "receipt": receipt, "manifest": manifest, "run": run}
        except Exception as exc:
            _failure(run, output_root, run_id, stage, exc)
            raise


def _verify_sealed(run: Path, source_root: Path, expected_manifest_sha: str | None = None) -> dict:
    if not RUN_ID.fullmatch(run.name) or run.parent.name != "runs" or run.is_symlink():
        raise ValueError("invalid sealed run path")
    if (run / "manifest.json").is_symlink() or (run / "receipt.json").is_symlink():
        raise ValueError("symlink sealed authority")
    raw_manifest = (run / "manifest.json").read_bytes()
    manifest_sha = _sha(raw_manifest)
    if expected_manifest_sha is not None and manifest_sha != expected_manifest_sha:
        raise ValueError("current manifest hash changed")
    manifest = json.loads(raw_manifest)
    _validate_manifest(manifest)
    if manifest["run_id"] != run.name:
        raise ValueError("manifest run identity differs")
    receipt, receipt_sha = _read(run / "receipt.json")
    if receipt_sha != manifest["receipt_sha256"] or receipt.get("run_id") != run.name:
        raise ValueError("sealed receipt hash or run identity differs")
    if receipt.get("status") != "REVIEW" or receipt.get("build_status") != "SUCCEEDED":
        raise ValueError("sealed receipt is not successful")
    sources = _sources(source_root)
    if manifest["source_dependencies"] != sources or receipt["source_dependencies"] != sources:
        raise ValueError("live source dependencies changed")
    packet, packet_sha = _read(run / "analysis.json")
    if validate_analysis_packet(packet):
        raise ValueError("sealed analysis packet rejected")
    model = build_publication_model(packet)
    if (manifest["analysis_content_digest"] != packet["content_digest"]
            or receipt["analysis_content_digest"] != packet["content_digest"]
            or manifest["publication_content_digest"] != model["content_digest"]
            or receipt["publication_content_digest"] != model["content_digest"]):
        raise ValueError("sealed canonical content differs")
    selected = manifest["numerical_acceptance"]
    if (selected["source_manifest"] != packet["source_manifest"]
            or selected["numeric_content_digest"] != packet["source_manifest"]["acceptance"]["numeric_content_digest"]
            or selected["metric_manifest_sha256"] != packet["source_manifest"]["acceptance"]["metric_manifest_sha256"]
            or selected["code_sha256"] != packet["source_manifest"]["acceptance"]["code_sha256"]
            or selected["code_sha256"] != _code_hashes()
            or selected["resource_sha256"] != _numeric_resource_digests()
            or selected["attempt_id"] != receipt["numerical_acceptance_attempt_id"]
            or selected["receipt_sha256"] != receipt["numerical_acceptance_sha256"]
            or selected["numeric_content_digest"] != receipt["numeric_content_digest"]):
        raise ValueError("sealed acceptance lineage differs")
    for dep in sources:
        sid = dep["snapshot_id"]
        item = packet["source_manifest"]["sources"][sid]
        if (item["period_id"] != dep["period_id"] or item["sha256"] != dep["source_sha256"]
                or item["url"] != dep["source_url"]):
            raise ValueError("sealed source summary differs")
    expected = _expected(model)
    if set(manifest["artifact_hashes"]) != expected or len(expected) != 73:
        raise ValueError("sealed artifact allowlist differs")
    observed = _inventory(run, expected)
    if observed != manifest["artifact_hashes"] or observed["analysis.json"] != packet_sha:
        raise ValueError("sealed artifact hashes differ")
    authored = authored_resource_digests()
    if any(observed[name] != authored[name] for name in FONT_PATHS):
        raise ValueError("staged font differs from reviewed package")
    return {"manifest": manifest, "manifest_sha256": manifest_sha,
            "receipt": receipt, "packet": packet, "model": model,
            "sources": sources, "artifact_hashes": observed}


def resolve_publication_current(output_root: Path, source_root: Path) -> dict:
    """Return current paths only after two complete independent live checks."""
    output_root, source_root = _strict_roots(output_root, source_root)
    current_path = output_root / "current.json"
    if current_path.is_symlink():
        raise ValueError("symlink current pointer")
    current, pointer_sha = _read(current_path)
    run_id = current.get("run_id")
    if (set(current) != {"schema_version", "run_id", "status", "build_status", "manifest_sha256"}
            or current.get("schema_version") != "2.0"
            or current.get("status") != "REVIEW" or current.get("build_status") != "SUCCEEDED"
            or not isinstance(run_id, str) or not RUN_ID.fullmatch(run_id)
            or not isinstance(current.get("manifest_sha256"), str)
            or not HEX.fullmatch(current["manifest_sha256"])):
        raise ValueError("current publication is blocked or invalid")
    run = output_root / "runs" / run_id
    first = _verify_sealed(run, source_root, current["manifest_sha256"])
    second = _verify_sealed(run, source_root, current["manifest_sha256"])
    if first["sources"] != second["sources"] or first["artifact_hashes"] != second["artifact_hashes"]:
        raise ValueError("publication changed during resolution")
    if _sha(current_path.read_bytes()) != pointer_sha:
        raise ValueError("current pointer changed during resolution")
    return {"run_id": run_id, "manifest": second["manifest"], "receipt": second["receipt"],
            "html": run / "report.html", "markdown": run / "report.md",
            "pdf": run / "report.pdf", "csv": run / "exports/public-records.csv",
            "parquet": run / "exports/public-records.parquet",
            "duckdb": run / "exports/public.duckdb"}


def _accepted_payloads(acceptance: dict, sources: list[dict]) -> tuple[dict, dict]:
    root = Path(acceptance["output_root"])
    if root.is_symlink():
        raise ValueError("symlink numerical output root")
    root = root.resolve(strict=True)
    publics, audits = {}, {}
    for dep in sources:
        sid = dep["snapshot_id"]
        pin = acceptance["snapshots"][sid]
        for key, suffix, destination in (("public_v2_path", "-public-v2.json", publics),
                                         ("path", "-aggregate.json", audits)):
            candidate = Path(pin[key])
            if candidate.is_symlink() or candidate.resolve(strict=True) != root / f"{sid}{suffix}":
                raise ValueError("accepted output file escaped or changed")
            destination[sid] = _read(candidate)[0]
        public, audit = publics[sid], audits[sid]
        if (_digest(public) != pin["public_v2_digest"]
                or _content_digest(public) != pin["public_content_sha256"]
                or _digest(public["records"]) != pin["numeric_digest"]
                or audit["numeric_digest"] != pin["numeric_digest"]
                or audit["source_sha256"] != dep["source_sha256"]
                or public["sources"][0]["url"] != dep["source_url"]
                or public["sources"][0]["sha256"] != dep["source_sha256"]):
            raise ValueError("accepted public or aggregate output differs")
    return publics, audits


def _operation_receipt(audit: Path, result: dict) -> dict:
    audit.mkdir(parents=True, exist_ok=True)
    with BuildLock(audit):
        attempt_id = _attempt_id()
        payload = {**result, "attempt_id": attempt_id, "completed_at": now()}
        immutable_bytes(audit / "attempts" / f"{attempt_id}.json", json_bytes(payload))
        atomic_json(audit / "current.json", payload)
        return payload


def analyze_acceptance(source_root: Path, acceptance_receipt: Path,
                       analysis_output: Path, audit_dir: Path) -> dict:
    """Build a new independently guarded packet from the current immutable acceptance."""
    acceptance_receipt = Path(acceptance_receipt).resolve()
    numerical_audit = acceptance_receipt.parent.parent
    if acceptance_receipt.parent.name != "attempts":
        raise ValueError("immutable acceptance receipt required")
    source_root, audit_dir, numerical_audit = _strict_roots(source_root, audit_dir, numerical_audit)
    analysis_output = Path(analysis_output).resolve()
    if (analysis_output.exists() or analysis_output.is_relative_to(source_root)
            or analysis_output.is_relative_to(numerical_audit)
            or analysis_output.is_relative_to(audit_dir)):
        raise ValueError("analysis output overlaps input or already exists")
    accepted, accepted_sha = _accepted(numerical_audit, acceptance_receipt)
    accepted_output = Path(accepted["output_root"]).resolve()
    _strict_roots(source_root, audit_dir, numerical_audit, accepted_output)
    if analysis_output.is_relative_to(accepted_output):
        raise ValueError("analysis output overlaps accepted output")
    try:
        sources = _sources(source_root)
        publics, audits = _accepted_payloads(accepted, sources)
        from .comparisons_v2 import load_definition_registry

        packet = build_analysis_packet(publics, accepted, audits,
                                       load_definition_registry(entity_reference_code="02"))
        _summary(packet, accepted, accepted_sha, sources)
        if validate_analysis_packet(packet):
            raise ValueError("new analysis packet rejected")
        current_publics, current_audits = _accepted_payloads(accepted, sources)
        if (_sources(source_root) != sources
                or _accepted(numerical_audit, acceptance_receipt)[1] != accepted_sha
                or current_publics != publics or current_audits != audits):
            raise ValueError("analysis input changed")
        if analysis_output.exists():
            raise FileExistsError("analysis output already exists")
        immutable_bytes(analysis_output, json_bytes(packet))
        persisted, digest = _read(analysis_output)
        if persisted != packet or validate_analysis_packet(persisted):
            raise ValueError("persisted analysis packet rejected")
        return _operation_receipt(audit_dir, {"status": "PASS", "operation": "research_analyze",
                      "acceptance_attempt_id": accepted["attempt_id"],
                      "acceptance_receipt_sha256": accepted_sha,
                      "numeric_content_digest": accepted["numeric_content_digest"],
                      "analysis_content_digest": packet["content_digest"],
                      "analysis_sha256": digest,
                      "record_count": len(packet["record_index"]),
                      "comparison_count": len(packet["comparisons"]),
                      "claim_count": len(packet["claims"])})
    except Exception as exc:
        _operation_receipt(audit_dir, {"status": "BLOCKED", "operation": "research_analyze",
                           "error": {"code": type(exc).__name__[:60], "reason": "analysis stage failed"}})
        raise


def _logical_exports(old: Path, new: Path, tables: set[str]) -> bool:
    import duckdb

    old_db = duckdb.connect(str(old / "public.duckdb"), read_only=True)
    new_db = duckdb.connect(str(new / "public.duckdb"), read_only=True)
    try:
        for table in sorted(tables):
            if old_db.execute(f"SELECT * FROM {table} ORDER BY 1").fetchall() != new_db.execute(
                    f"SELECT * FROM {table} ORDER BY 1").fetchall():
                return False
        return True
    finally:
        old_db.close()
        new_db.close()


def replay_publication(source_root: Path, sealed_run: Path, audit_dir: Path) -> dict:
    """Reconstruct aggregate outputs into a separate receipt and artifact tree."""
    source_root, sealed_run, audit_dir = _strict_roots(source_root, sealed_run, audit_dir)
    if sealed_run.parent.name != "runs" or not RUN_ID.fullmatch(sealed_run.name):
        raise ValueError("sealed publication run required")
    audit_dir.mkdir(parents=True, exist_ok=True)
    with BuildLock(audit_dir):
        attempt_id = _attempt_id()
        attempt = audit_dir / "replay-runs" / attempt_id
        attempt.mkdir(parents=True, exist_ok=False)
        try:
            baseline = _verify_sealed(sealed_run, source_root)
            packet = baseline["packet"]
            model = build_publication_model(packet)
            immutable_bytes(attempt / "analysis.json", json_bytes(packet))
            fresh_hashes = _render(model, attempt)
            if set(fresh_hashes) != set(baseline["artifact_hashes"]):
                raise ValueError("replay artifact inventory differs")
            tables = set(_table_data(model))
            if not _logical_exports(sealed_run / "exports", attempt / "exports", tables):
                raise ValueError("replay logical export tables differ")
            end = _verify_sealed(sealed_run, source_root, baseline["manifest_sha256"])
            if end["sources"] != baseline["sources"] or end["artifact_hashes"] != baseline["artifact_hashes"]:
                raise ValueError("baseline or sources changed during replay")
            result = {"status": "PASS", "operation": "research_replay",
                      "sealed_run_id": sealed_run.name,
                      "analysis_content_digest": packet["content_digest"],
                      "publication_content_digest": model["content_digest"],
                      "numeric_content_digest": baseline["manifest"]["numerical_acceptance"]["numeric_content_digest"],
                      "record_ids_sha256": _digest(sorted(model["records"])),
                      "comparison_ids_sha256": _digest(sorted(c["comparison_id"] for c in model["comparisons"])),
                      "claim_ids_sha256": _digest(sorted(c["claim_id"] for c in model["claims"])),
                      "figure_ids_sha256": _digest(sorted(f["figure_id"] for f in model["figure_links"])),
                      "artifact_hashes": fresh_hashes, "attempt_id": attempt_id, "completed_at": now()}
        except Exception as exc:
            result = {"status": "BLOCKED", "operation": "research_replay",
                      "sealed_run_id": sealed_run.name, "attempt_id": attempt_id,
                      "error": {"code": type(exc).__name__[:60], "reason": "publication replay failed"},
                      "completed_at": now()}
            immutable_bytes(audit_dir / "attempts" / f"{attempt_id}.json", json_bytes(result))
            atomic_json(audit_dir / "current.json", result)
            raise
        immutable_bytes(audit_dir / "attempts" / f"{attempt_id}.json", json_bytes(result))
        atomic_json(audit_dir / "current.json", result)
        return result
