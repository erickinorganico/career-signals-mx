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
    parser = argparse.ArgumentParser(prog="brujula", description="Brújula Laboral MX · demo local reproducible")
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
    args = parser.parse_args(argv)
    try:
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
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    return 0
