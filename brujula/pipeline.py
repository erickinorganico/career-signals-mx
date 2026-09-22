"""Build only from validated local data; preserve raw inputs and failure receipts."""
from __future__ import annotations

import csv
import hashlib
import io
import json
import os
from datetime import date, datetime, timezone
from pathlib import Path
from uuid import uuid4

ROOT = Path(__file__).resolve().parents[1]
ADAPTER_VERSION = "local-json/1.0"


def now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="milliseconds")


def json_bytes(value: object) -> bytes:
    return (json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + "\n").encode("utf-8")


def atomic_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.{uuid4().hex}.tmp")
    try:
        temporary.write_bytes(json_bytes(value))
        os.replace(temporary, path)
    finally:
        temporary.unlink(missing_ok=True)


def immutable_bytes(path: Path, content: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    try:
        with path.open("xb") as handle:
            handle.write(content)
    except FileExistsError:
        if path.read_bytes() != content:
            raise ValueError(f"Immutable artifact collision: {path.name}")


def read_catalog() -> list[dict]:
    source = ROOT / "data/catalog/sources.json"
    if source.exists():
        return json.loads(source.read_text(encoding="utf-8"))
    raise ValueError("Audited source catalog is missing")


def make_comparisons(dataset: dict) -> list[dict]:
    from .quality import compare_observations

    period_order = {p["id"]: p["start"] for p in dataset["dimensions"]["periods"]}
    groups: dict[tuple, list] = {}
    for row in dataset["observations"]:
        # Deliberately do not group by method/source: a change must be visible as blocked.
        key = tuple(row[k] for k in ("concept_type", "concept_id", "geography_id", "metric_id"))
        groups.setdefault(key, []).append(row)
    result = []
    for rows in groups.values():
        rows.sort(key=lambda r: period_order[r["period_id"]])
        for previous, current in zip(rows, rows[1:]):
            comparison = compare_observations(previous, current)
            result.append({"previous_id": previous["id"], "current_id": current["id"], **comparison})
    return result


def export_csv(dataset: dict) -> str:
    columns = ["id", "concept_type", "concept_id", "geography_id", "period_id", "metric_id",
               "value", "unit", "price_basis", "status", "source_id", "population", "synthetic",
               "precision_note", "evidence_refs"]
    buffer = io.StringIO(newline="")
    writer = csv.DictWriter(buffer, fieldnames=columns, lineterminator="\n")
    writer.writeheader()
    for observation in dataset["observations"]:
        row = {key: observation[key] for key in columns}
        row["evidence_refs"] = "|".join(row["evidence_refs"])
        for key, value in row.items():
            # Spreadsheet formula injection prevention for user-supplied textual labels.
            if isinstance(value, str) and value.lstrip().startswith(("=", "+", "-", "@")):
                row[key] = "'" + value
        writer.writerow(row)
    return buffer.getvalue()


def blocked_payload(receipt: dict, message: str) -> dict:
    return {"schema_version": "1.0", "generated_at": now(), "run_id": receipt["run_id"],
            "status": "BLOCKED", "publishable": False, "dataset": None,
            "quality": {"status": "BLOCKED", "publishable": False,
                        "checks": [{"id": "publication", "status": "BLOCKED", "message": message}]},
            "comparisons": [], "insights": [], "agent_run": None, "receipt": receipt,
            "catalog": [], "error": message}


def current_report(out: Path, receipt: dict, report_path: str | None = None) -> None:
    """Publish a current pointer, never silently fall back to an old report."""
    message = f"# Brújula Laboral MX — {receipt['status']}\n\nEjecución: `{receipt['run_id']}`.\n\n"
    if report_path:
        message += f"[Abrir el reporte verificado de esta ejecución]({report_path}).\n\n"
        message += "Los directorios de otras ejecuciones son evidencia histórica.\n"
    else:
        message += "Publicación retenida. Esta ejecución no ofrece cifras ni recomendaciones.\n"
        if receipt.get("error"):
            message += f"\nError: {receipt['error']['type']}. Consulta current.json para el diagnóstico.\n"
    temporary = out / (".report-" + uuid4().hex + ".tmp")
    temporary.write_text(message, encoding="utf-8")
    os.replace(temporary, out / "report.md")
    atomic_json(out / "current.json", {**receipt, "report": report_path})


def build(input_path: Path | str | None = None, output: Path | str | None = None,
          as_of: date | None = None) -> dict:
    """One atomic current publication, plus immutable evidence for every attempt.

    A failed refresh replaces the current pointer with BLOCKED. Prior successful runs
    remain inspectable in runs/, but are never used as a fallback for current data.
    """
    from .data import load_dataset
    from .quality import validate_dataset
    from .warehouse import write_warehouse
    from .agents import run_agents, validate_agent_run
    from .report import render_report

    source = Path(input_path) if input_path else ROOT / "data/fixtures/pilot.json"
    out = Path(output) if output else ROOT / "artifacts"
    out.mkdir(parents=True, exist_ok=True)
    lock = out / ".build.lock"
    try:
        handle = lock.open("x", encoding="utf-8")
    except FileExistsError as exc:
        raise RuntimeError("A build is running, or a stopped build left .build.lock. Check before removing it.") from exc
    with handle:
        handle.write(str(os.getpid()))
    run_id = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S") + "-" + uuid4().hex[:12]
    run_dir = out / "runs" / run_id
    run_dir.mkdir(parents=True)
    receipt = {"schema_version": "1.0", "run_id": run_id, "status": "BLOCKED", "build_status": "RUNNING",
               "input_name": source.name, "input_sha256": None, "adapter_version": ADAPTER_VERSION,
               "started_at": now(), "completed_at": None, "as_of": (as_of or date.today()).isoformat(),
               "parameters": {"network": False}, "error": None}
    try:
        # First action invalidates previous publication, even if reading the new input fails.
        current_report(out, receipt)
        raw = source.read_bytes()
        if len(raw) > 16_000_000:
            raise ValueError("Input exceeds local 16 MB contract limit")
        digest = hashlib.sha256(raw).hexdigest()
        receipt["input_sha256"] = digest
        raw_path = out / "raw" / f"{digest}.json"
        immutable_bytes(raw_path, raw)
        dataset = load_dataset(raw_path)
        quality = validate_dataset(dataset, as_of=as_of)
        atomic_json(run_dir / "quality.json", quality)
        if not quality["publishable"]:
            failures = [c["message"] for c in quality["checks"] if c["status"] == "BLOCKED"]
            raise ValueError("Quality gate: " + "; ".join(failures))
        catalog = read_catalog()
        comparisons = make_comparisons(dataset)
        agents = run_agents(dataset, quality, comparisons, catalog)
        errors = validate_agent_run(agents, dataset, quality)
        if errors or not agents["publication_allowed"]:
            raise ValueError("Agent publication gate: " + "; ".join(errors or ["release denied"]))
        warehouse = write_warehouse(dataset, run_dir / "warehouse.duckdb")
        atomic_json(run_dir / "agent-run.json", agents)
        atomic_json(run_dir / "comparisons.json", comparisons)
        receipt.update(status=quality["status"], build_status="SUCCEEDED", completed_at=now(),
                       observation_count=len(dataset["observations"]), mode=dataset["mode"],
                       warehouse={"file": "warehouse.duckdb", "observation_count": warehouse["observation_count"]})
        payload = {"schema_version": "1.0", "generated_at": now(), "run_id": run_id,
                   "status": quality["status"], "publishable": True, "dataset": dataset,
                   "quality": quality, "comparisons": comparisons, "insights": agents["insights"],
                   "agent_run": agents, "receipt": receipt, "catalog": catalog}
        reports = render_report(payload, run_dir / "report")
        payload["reports"] = reports
        (run_dir / "observations.csv").write_text(export_csv(dataset), encoding="utf-8-sig", newline="")
        import duckdb
        with duckdb.connect(str(run_dir / "warehouse.duckdb"), read_only=True) as connection:
            parquet_target = str(run_dir / "observations.parquet").replace("'", "''")
            connection.execute(f"COPY observation TO '{parquet_target}' (FORMAT PARQUET)")
        atomic_json(run_dir / "bundle.json", payload)
        manifest = {str(p.relative_to(run_dir)).replace("\\", "/"): hashlib.sha256(p.read_bytes()).hexdigest()
                    for p in sorted(run_dir.rglob("*")) if p.is_file()}
        atomic_json(run_dir / "manifest.json", manifest)
        immutable_bytes(run_dir / "receipt.json", json_bytes(receipt))
        current_report(out, receipt, f"runs/{run_id}/report/{reports['markdown']}")
        return payload
    except Exception as exc:
        receipt.update(status="BLOCKED", build_status="FAILED", completed_at=now(),
                       error={"type": type(exc).__name__, "message": str(exc)})
        blocked = blocked_payload(receipt, str(exc))
        atomic_json(run_dir / "bundle.json", blocked)
        immutable_bytes(run_dir / "receipt.json", json_bytes(receipt))
        current_report(out, receipt)
        return blocked
    finally:
        lock.unlink(missing_ok=True)
