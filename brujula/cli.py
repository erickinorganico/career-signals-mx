"""Offline analytical research CLI; no application or HTTP server."""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import date
from pathlib import Path

from .pipeline import ROOT, atomic_json, build, now, resolve_current
from .resources import CHECKOUT_ROOT


def _real_parser(sub, name: str, help_text: str, flags: tuple[str, ...]):
    command = sub.add_parser(name, help=help_text)
    for flag in flags:
        command.add_argument("--" + flag.replace("_", "-"), type=Path, required=True)
    return command


def _refresh(source_root: Path, output_root: Path) -> list[dict]:
    from .acquisition import acquire_snapshot
    from .pipeline_v2 import SNAPSHOTS, _strict_roots
    from .runlock import BuildLock

    source_root, output_root = _strict_roots(source_root, output_root)
    output_root.mkdir(parents=True, exist_ok=True)
    with BuildLock(output_root):
        atomic_json(output_root / "current.json",
                    {"schema_version": "2.0", "status": "BLOCKED",
                     "build_status": "RUNNING", "reason": "source refresh"})
        results = [acquire_snapshot(sid, source_root) for sid in SNAPSHOTS]
        atomic_json(output_root / "current.json",
                    {"schema_version": "2.0", "status": "BLOCKED",
                     "build_status": "FAILED" if any(r["status"] != "SUCCEEDED" for r in results)
                     else "SUCCEEDED", "reason": "publication requires a new sealed build"})
    return results


def verify() -> int:
    if CHECKOUT_ROOT is None:
        raise RuntimeError("verify requires the source checkout containing tests, evals and documentation")
    results = []
    commands = [[sys.executable, "scripts/check_docs.py"],
                [sys.executable, "-m", "evals.run"],
                [sys.executable, "-m", "pytest", "-q", "--junitxml=artifacts/verification/junit.xml"]]
    for command in commands:
        try:
            run = subprocess.run(command, cwd=ROOT, check=False)
            results.append({"command": ["python", *command[1:]], "exit_code": run.returncode})
        except OSError as exc:
            results.append({"command": ["python", *command[1:]], "exit_code": 127, "error": type(exc).__name__})
    report = {"checked_at": now(), "status": "PASS" if all(r["exit_code"] == 0 for r in results) else "FAIL",
              "scope": "unit, integration, analytical E2E, negative controls, reports and agents; offline", "checks": results}
    atomic_json(ROOT / "artifacts/verification/verify.json", report)
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if report["status"] == "PASS" else 1


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="brujula", description="Brújula Laboral MX · investigación laboral local reproducible")
    sub = parser.add_subparsers(dest="command", required=True)
    for name in ("build", "demo"):
        cmd = sub.add_parser(name, help="Validar, materializar y preparar la demo" if name == "build" else "Construir reportes y gráficas reproducibles")
        cmd.add_argument("--input", type=Path)
        cmd.add_argument("--output", type=Path, default=ROOT / "artifacts")
        cmd.add_argument("--as-of", type=date.fromisoformat, help="Fecha ISO de evaluación; la fecha de ejecución se conserva aparte")
    checks = sub.add_parser("verify", help="Pruebas unitarias, integración, E2E analítico y controles negativos")
    report = sub.add_parser("report", help="Resolver el reporte actual después de validar estado y hashes")
    report.add_argument("--output", type=Path, default=ROOT / "artifacts")
    report.add_argument("--format", choices=("html", "markdown"), default="html")
    scout = sub.add_parser("scout", help="Revisar una página INEGI autorizada; genera propuesta, nunca publica cifras")
    scout.add_argument("--source", default="inegi_enoe_2025_q2")
    scout.add_argument("--output", type=Path, default=ROOT / "artifacts/scout")
    _real_parser(sub, "enoe-refresh",
                 "Refresh the eight approved acquisitions; source custody and dependent publication roots",
                 ("source_root", "output_root"))
    accept = _real_parser(sub, "enoe-accept",
                          "Numerical acceptance; output is fresh numerical aggregates, audit stores immutable receipts",
                          ("source_root", "output_root", "audit_dir", "workbook", "pdf", "r_lib"))
    replay_num = _real_parser(sub, "enoe-replay",
                              "Full offline numerical recomputation; run is immutable acceptance receipt, audit is new",
                              ("source_root", "run", "audit_dir", "r_lib"))
    for command in (accept, replay_num):
        command.add_argument("--rscript", type=Path)
        command.add_argument("--r-home", type=Path)
    _real_parser(sub, "research-analyze",
                 "Build fresh guarded analysis; receipt is immutable accepted attempt, audit is new operation root",
                 ("source_root", "acceptance_receipt", "analysis_output", "audit_dir"))
    _real_parser(sub, "research-build",
                 "Seal aggregate publication; audit is read-only numerical acceptance root",
                 ("source_root", "output_root", "audit_dir", "analysis_packet"))
    _real_parser(sub, "research-replay",
                 "Reconstruct publication in a new audit root; run is sealed publication directory",
                 ("source_root", "run", "audit_dir"))
    opened = _real_parser(sub, "research-open",
                          "Resolve only a live verified current report or export",
                          ("source_root", "output_root"))
    opened.add_argument("--format", choices=("html", "markdown", "pdf", "csv", "parquet", "duckdb"),
                        default="html")
    args = parser.parse_args(argv)
    try:
        if args.command in {"enoe-refresh", "enoe-accept", "enoe-replay",
                            "research-analyze", "research-build", "research-replay",
                            "research-open"}:
            from . import pipeline_v2
            if args.command == "enoe-refresh":
                receipts = _refresh(args.source_root, args.output_root)
                print(json.dumps({"status": "PASS" if all(r["status"] == "SUCCEEDED" for r in receipts) else "BLOCKED",
                                  "acquisition_attempt_ids": {r["snapshot_id"]: r["run_id"] for r in receipts}}))
                return 0 if all(r["status"] == "SUCCEEDED" for r in receipts) else 1
            if args.command == "enoe-accept":
                from .enoe_acceptance import accept as accept_numeric
                result = accept_numeric(args.output_root, args.audit_dir,
                                        source_root=args.source_root, workbook=args.workbook,
                                        pdf=args.pdf, rscript=args.rscript, r_home=args.r_home,
                                        r_lib=args.r_lib)
                print(json.dumps({"status": result["status"], "attempt_id": result["attempt_id"],
                                  "numeric_content_digest": result.get("numeric_content_digest")}))
                return 0 if result["status"] == "PASS" else 1
            if args.command == "enoe-replay":
                from .enoe_acceptance import replay as replay_numeric
                result = replay_numeric(args.source_root, args.run, args.audit_dir,
                                        rscript=args.rscript, r_home=args.r_home, r_lib=args.r_lib)
                print(json.dumps({"status": result["status"], "attempt_id": result["attempt_id"],
                                  "numeric_content_digest": result.get("numeric_content_digest")}))
                return 0 if result["status"] == "PASS" else 1
            if args.command == "research-analyze":
                result = pipeline_v2.analyze_acceptance(
                    args.source_root, args.acceptance_receipt, args.analysis_output, args.audit_dir)
                print(json.dumps({"status": result["status"], "attempt_id": result["attempt_id"],
                                  "analysis_content_digest": result.get("analysis_content_digest")}))
                return 0 if result["status"] == "PASS" else 1
            if args.command == "research-build":
                result = pipeline_v2.build_publication(
                    args.source_root, args.output_root, args.audit_dir, args.analysis_packet)
                print(json.dumps({"status": result["receipt"]["status"],
                                  "run_id": result["receipt"]["run_id"],
                                  "publication_content_digest": result["receipt"]["publication_content_digest"]}))
                return 0
            if args.command == "research-replay":
                result = pipeline_v2.replay_publication(args.source_root, args.run, args.audit_dir)
                print(json.dumps({"status": result["status"], "attempt_id": result["attempt_id"],
                                  "publication_content_digest": result.get("publication_content_digest")}))
                return 0 if result["status"] == "PASS" else 1
            resolved = pipeline_v2.resolve_publication_current(args.output_root, args.source_root)
            print(resolved[args.format])
            return 0
        if args.command in {"build", "demo"}:
            result = build(args.input, args.output, args.as_of)
            print(json.dumps(result["receipt"], ensure_ascii=False, indent=2), flush=True)
            if not result["publishable"]:
                return 1
            report = resolve_current(args.output)
            print("Reporte actual verificado:", report["html"])
        elif args.command == "verify":
            return verify()
        elif args.command == "report":
            report = resolve_current(args.output)
            print(report[args.format])
        elif args.command == "scout":
            from .scout import scout_source
            result = scout_source(args.source, args.output)
            print(json.dumps(result, ensure_ascii=False, indent=2))
            return 1 if result["status"] == "BLOCKED" else 0
    except (OSError, ValueError, RuntimeError) as exc:
        if args.command in {"enoe-refresh", "enoe-accept", "enoe-replay",
                            "research-analyze", "research-build", "research-replay",
                            "research-open"}:
            print(f"ERROR: {type(exc).__name__}: operation blocked", file=sys.stderr)
        else:
            print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    return 0
