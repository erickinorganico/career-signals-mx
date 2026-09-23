"""Validated local builds with one authoritative pointer and immutable run evidence."""
from __future__ import annotations

import hashlib
import json
import os
import re
from datetime import date, datetime, timezone
from pathlib import Path, PurePosixPath
from uuid import uuid4

from .export import export_csv, write_exports
from .runlock import BuildLock
from .resources import CHECKOUT_ROOT, catalog_path, contract_path, fixture_path

ROOT = CHECKOUT_ROOT or Path.cwd()
ADAPTER_VERSION = "local-json/1.1"
RUN_ID = re.compile(r"\d{8}T\d{6}-[a-f0-9]{12}\Z")


def now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="milliseconds")


def json_bytes(value: object) -> bytes:
    return (json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + "\n").encode("utf-8")


def atomic_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.{uuid4().hex}.tmp")
    try:
        with temporary.open("xb") as handle:
            handle.write(json_bytes(value))
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
    finally:
        temporary.unlink(missing_ok=True)


def immutable_bytes(path: Path, content: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    try:
        with path.open("xb") as handle:
            handle.write(content)
            handle.flush()
            os.fsync(handle.fileno())
    except FileExistsError:
        if path.read_bytes() != content:
            raise ValueError(f"Immutable artifact collision: {path.name}")


def read_catalog() -> list[dict]:
    return json.loads(catalog_path().read_text(encoding="utf-8"))


def seal_receipt(path: Path, receipt: dict) -> None:
    from jsonschema import Draft202012Validator, FormatChecker
    schema = json.loads(contract_path("run.schema.json").read_text(encoding="utf-8"))
    Draft202012Validator(schema, format_checker=FormatChecker()).validate(receipt)
    immutable_bytes(path, json_bytes(receipt))


def make_comparisons(dataset: dict) -> list[dict]:
    from .quality import compare_observations

    periods = {p["id"]: p for p in dataset["dimensions"]["periods"]}
    groups: dict[tuple, list] = {}
    for row in dataset["observations"]:
        key = tuple(row[k] for k in ("concept_type", "concept_id", "geography_id", "metric_id"))
        groups.setdefault(key, []).append(row)
    result = []
    for key in sorted(groups):
        rows = sorted(groups[key], key=lambda row: periods[row["period_id"]]["start"])
        for previous, current in zip(rows, rows[1:]):
            result.append({"previous_id": previous["id"], "current_id": current["id"],
                           **compare_observations(previous, current, periods)})
    return result


def blocked_payload(receipt: dict, message: str) -> dict:
    return {"schema_version": "1.0", "generated_at": now(), "run_id": receipt["run_id"],
            "status": "BLOCKED", "publishable": False, "dataset": None,
            "quality": {"status": "BLOCKED", "publishable": False,
                        "checks": [{"id": "publication", "status": "BLOCKED", "message": message}]},
            "comparisons": [], "insights": [], "agent_run": None, "receipt": receipt,
            "catalog": [], "reports": {}, "error": message}


def current_report(out: Path, current: dict) -> None:
    """Human index has no active numeric content or direct link that could go stale."""
    message = f"# Brújula Laboral MX — {current['status']}\n\nEjecución: `{current['run_id']}`.\n\n"
    message += "Este índice puede quedar atrasado tras una interrupción. La autoridad es current.json.\n\n"
    message += "Resuelve y verifica el reporte con `python -m brujula report --output <directorio-de-salida>`.\n"
    if not current.get("publishable"):
        message += "\nPublicación retenida. Esta ejecución no ofrece cifras ni recomendaciones.\n"
    temporary = out / (".report-" + uuid4().hex + ".tmp")
    try:
        temporary.write_text(message, encoding="utf-8")
        os.replace(temporary, out / "report.md")
    finally:
        temporary.unlink(missing_ok=True)


def _run_path(out: Path, run_id: str) -> Path:
    if not isinstance(run_id, str) or not RUN_ID.fullmatch(run_id):
        raise ValueError("Invalid run identifier")
    path = out / "runs" / run_id
    if not path.resolve().is_relative_to(out.resolve()):
        raise ValueError("Run path leaves output directory")
    return path


def resolve_current(output: Path | str) -> dict:
    """Read current only after verifying the manifest and all sealed artifacts."""
    out = Path(output)
    current = json.loads((out / "current.json").read_text(encoding="utf-8"))
    if not isinstance(current, dict):
        raise ValueError("Invalid current pointer")
    if not current.get("publishable") or current.get("build_status") != "SUCCEEDED" or current.get("status") not in {"REVIEW", "MEASURED"}:
        raise ValueError("Current publication is BLOCKED or unavailable")
    run = _run_path(out, current.get("run_id"))
    raw_manifest = (run / "manifest.json").read_bytes()
    if hashlib.sha256(raw_manifest).hexdigest() != current.get("manifest_sha256"):
        raise ValueError("Manifest integrity check failed")
    manifest = json.loads(raw_manifest)
    if not isinstance(manifest, dict) or not {"receipt.json", "bundle.json", "report/report.md", "report/report.html"} <= set(manifest):
        raise ValueError("Incomplete manifest")
    for relative, digest in manifest.items():
        path = PurePosixPath(relative)
        target = run / relative
        if path.is_absolute() or ".." in path.parts or "\\" in relative or not target.resolve().is_relative_to(run.resolve()):
            raise ValueError("Unsafe manifest path")
        if not target.is_file() or hashlib.sha256(target.read_bytes()).hexdigest() != digest:
            raise ValueError(f"Artifact integrity check failed: {relative}")
    receipt = json.loads((run / "receipt.json").read_text(encoding="utf-8"))
    if any(current.get(key) != value for key, value in receipt.items()):
        raise ValueError("Current pointer and receipt disagree")
    digest = receipt.get("input_sha256")
    if not isinstance(digest, str) or not re.fullmatch(r"[a-f0-9]{64}", digest):
        raise ValueError("Invalid input hash")
    raw = out / "raw" / f"{digest}.json"
    if not raw.is_file() or hashlib.sha256(raw.read_bytes()).hexdigest() != digest:
        raise ValueError("Raw input integrity check failed")
    bundle = json.loads((run / "bundle.json").read_text(encoding="utf-8"))
    if bundle.get("run_id") != current["run_id"] or not bundle.get("publishable") or bundle.get("status") != current["status"]:
        raise ValueError("Bundle is not authorized by current")
    return {"current": current, "bundle": bundle, "markdown": run / "report/report.md", "html": run / "report/report.html"}


def _failure(out: Path, run_dir: Path, receipt: dict, exc: Exception, stage: str) -> dict:
    # Raw input and detailed quality diagnostics stay in the run, not in public errors.
    receipt = {**receipt, "status": "BLOCKED", "build_status": "FAILED", "completed_at": now(),
               "error": {"type": type(exc).__name__, "message": f"Build failed during {stage}"}}
    payload = blocked_payload(receipt, receipt["error"]["message"])
    final = run_dir / "receipt.json"
    if final.exists():
        # Artifact generation may have finished before publication failed. Never rewrite its sealed receipt.
        seal_receipt(run_dir / "publication-failure.json", receipt)
    else:
        seal_receipt(final, receipt)
    target = "failure.json" if (run_dir / "bundle.json").exists() else "bundle.json"
    immutable_bytes(run_dir / target, json_bytes(payload))
    atomic_json(run_dir / "journal.json", receipt)
    current = {**receipt, "publishable": False, "report": None, "manifest_sha256": None}
    atomic_json(out / "current.json", current)
    try:
        current_report(out, current)
    except OSError:
        pass  # The canonical BLOCKED pointer remains authoritative.
    return payload


def _recover_interrupted(out: Path) -> None:
    path = out / "current.json"
    if not path.exists():
        return
    current = json.loads(path.read_text(encoding="utf-8"))
    if current.get("build_status") != "RUNNING":
        return
    run = _run_path(out, current.get("run_id"))
    receipt = {key: value for key, value in current.items() if key not in {"publishable", "report", "manifest_sha256"}}
    _failure(out, run, receipt, RuntimeError("Interrupted execution"), "interrupted execution recovery")


def build(input_path: Path | str | None = None, output: Path | str | None = None,
          as_of: date | None = None) -> dict:
    source = Path(input_path) if input_path else fixture_path()
    out = Path(output) if output else ROOT / "artifacts"
    out.mkdir(parents=True, exist_ok=True)
    with BuildLock(out) as lock:
        _recover_interrupted(out)
        run_id = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S") + "-" + uuid4().hex[:12]
        run_dir = _run_path(out, run_id)
        run_dir.mkdir(parents=True)
        evaluation_date = as_of or date.today()
        receipt = {"schema_version": "1.0", "run_id": run_id, "status": "BLOCKED", "build_status": "RUNNING",
                   "input_name": source.name, "input_sha256": None, "adapter_version": ADAPTER_VERSION,
                   "started_at": now(), "completed_at": None, "as_of": evaluation_date.isoformat(),
                   "parameters": {"network": False}, "error": None}
        running = {**receipt, "publishable": False, "report": None, "manifest_sha256": None}
        atomic_json(out / "current.json", running)
        lock.record({"run_id": run_id})
        atomic_json(run_dir / "journal.json", receipt)
        stage = "input"
        try:
            from .data import load_dataset
            from .quality import validate_dataset
            from .warehouse import write_warehouse
            from .agents import run_agents, validate_agent_run
            from .report import render_report

            with source.open("rb") as handle:
                raw = handle.read(16_000_001)
            if len(raw) > 16_000_000:
                raise ValueError("Input exceeds 16 MB limit")
            digest = hashlib.sha256(raw).hexdigest()
            receipt["input_sha256"] = digest
            running["input_sha256"] = digest
            atomic_json(out / "current.json", running)
            atomic_json(run_dir / "journal.json", receipt)
            raw_path = out / "raw" / f"{digest}.json"
            immutable_bytes(raw_path, raw)
            dataset = load_dataset(raw_path)
            stage = "quality"
            quality = validate_dataset(dataset, as_of=evaluation_date)
            immutable_bytes(run_dir / "quality.json", json_bytes(quality))
            if not quality["publishable"]:
                raise ValueError("Quality gate denied publication")
            stage = "agents"
            catalog = read_catalog()
            comparisons = make_comparisons(dataset)
            agents = run_agents(dataset, quality, comparisons, catalog)
            errors = validate_agent_run(agents, dataset, quality)
            if errors or not agents["publication_allowed"]:
                raise ValueError("Agent publication gate denied publication")
            immutable_bytes(run_dir / "agent-run.json", json_bytes(agents))
            immutable_bytes(run_dir / "comparisons.json", json_bytes(comparisons))
            stage = "warehouse and exports"
            warehouse = write_warehouse(dataset, run_dir / "warehouse.duckdb")
            exports = write_exports(dataset, run_dir, quality)
            payload = {"schema_version": "1.0", "generated_at": receipt["started_at"], "run_id": run_id,
                       "status": quality["status"], "publishable": True, "dataset": dataset,
                       "quality": quality, "comparisons": comparisons, "insights": agents["insights"],
                       "agent_run": agents, "receipt": receipt, "catalog": catalog, "exports": exports}
            stage = "report rendering"
            payload["reports"] = render_report(payload, run_dir / "report")
            receipt.update(status=quality["status"], build_status="SUCCEEDED", completed_at=now(),
                           observation_count=len(dataset["observations"]), mode=dataset["mode"],
                           warehouse={"file": "warehouse.duckdb", "observation_count": warehouse["observation_count"]})
            stage = "artifact sealing"
            immutable_bytes(run_dir / "bundle.json", json_bytes(payload))
            seal_receipt(run_dir / "receipt.json", receipt)
            manifest = {p.relative_to(run_dir).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
                        for p in sorted(run_dir.rglob("*")) if p.is_file() and p.name != "journal.json"}
            manifest_bytes = json_bytes(manifest)
            immutable_bytes(run_dir / "manifest.json", manifest_bytes)
            stage = "publication commit"
            current = {**receipt, "publishable": True, "report": f"runs/{run_id}/report/report.md",
                       "manifest_sha256": hashlib.sha256(manifest_bytes).hexdigest()}
            atomic_json(out / "current.json", current)
        except Exception as exc:
            return _failure(out, run_dir, receipt, exc, stage)
        # The canonical commit succeeded. A failed convenience index cannot revoke it.
        try:
            atomic_json(run_dir / "journal.json", receipt)
            current_report(out, current)
        except OSError:
            pass
        return payload
