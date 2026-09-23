"""Installed eight-quarter numerical acceptance and immutable offline replay.

Golden authoring is outside this ordinary acceptance service. Every run checks
the independently pinned public and internal aggregate content.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import os
import platform
import shutil
import subprocess
import time
import uuid
from copy import deepcopy
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import patch

import numpy as np

from . import estimates
from .enoe_adapter import load_snapshot_frame
from .metrics import load_metric_manifest
from .populations import COMPLETED_PROFESSIONAL_KNOWN_AGE, NATIONAL_15_PLUS_CONTEXT
from .research_contract import GRAIN, validate_public_research_v2, validate_research_v2
from .source_inventory import FOCUS_CODES, inventory_all
from .survey import SurveyDesign
from .resources import (_bundled, aggregate_golden_path, contract_path,
                        metric_catalog_path, snapshot_catalog_path, oracle_script_path,
                        require_installed_package_path)
from .runlock import BuildLock

RTOL = 1e-10
ATOL = 1e-8
LATEST = "enoe_2026_q2"
CODE_FILES = frozenset({
    "brujula/enoe_acceptance.py", "brujula/oracle/enoe_survey_oracle.R",
    "brujula/official_reconciliation.py", "brujula/acquisition.py",
    "brujula/source_inventory.py", "brujula/enoe_adapter.py",
    "brujula/populations.py", "brujula/metrics.py", "brujula/survey.py",
    "brujula/estimates.py", "brujula/research_contract.py",
})
GOLDEN_LF_SHA256 = "86bf44b6ab70b78c3b40f03c7366188912d0e7d4de81e87a6b4773b7e7f6764d"
NUMERIC_DIGEST = "8db575e9d664864d1513e3b9658bd9b060c4cb3bed8b51561f208adeb97b9a00"
NUMERIC_RESOURCES = frozenset({
    "catalog/enoe-snapshots.json", "catalog/enoe-metrics.json",
    "catalog/enoe-geography-equivalence.json", "fixtures/enoe-aggregate-golden.json",
    "oracle/enoe_survey_oracle.R", "contracts/research-v2.schema.json",
    "contracts/research-v2-public.schema.json",
})


def _numeric_resource_digests() -> dict[str, str]:
    paths = {
        "catalog/enoe-snapshots.json": snapshot_catalog_path(),
        "catalog/enoe-metrics.json": metric_catalog_path(),
        "catalog/enoe-geography-equivalence.json": _bundled(
            "catalog", "enoe-geography-equivalence.json"),
        "fixtures/enoe-aggregate-golden.json": aggregate_golden_path(),
        "oracle/enoe_survey_oracle.R": oracle_script_path(),
        "contracts/research-v2.schema.json": contract_path("research-v2.schema.json"),
        "contracts/research-v2-public.schema.json": contract_path("research-v2-public.schema.json"),
    }
    if set(paths) != NUMERIC_RESOURCES:
        raise AssertionError("numeric resource inventory drift")
    return {name: hashlib.sha256(require_installed_package_path(path).read_bytes()
                                 .replace(b"\r\n", b"\n")).hexdigest()
            for name, path in sorted(paths.items())}


def _digest(value: object) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"),
                                     ensure_ascii=False, allow_nan=False).encode("utf-8")).hexdigest()


def _canonical_research_content(document: dict) -> dict:
    """Hash identity-sorted content without operational clock or code hash."""
    content = deepcopy(document)
    for row in content["records"]:
        row.pop("method_version", None)
    for method in content["methods"]:
        method.pop("version", None)  # root catalog copy of method_version
    for source in content["sources"]:
        source.pop("acquired_at", None)  # successful acquisition receipt clock
    content["records"].sort(key=lambda row: tuple(row[key] for key in GRAIN))
    for catalog in ("sources", "populations", "fields_of_study", "occupations",
                    "industries", "geographies", "recorded_sexes", "periods",
                    "metrics", "methods", "evidence"):
        if catalog in content:
            content[catalog].sort(key=lambda item: item["id"])
    return content


def compare_pinned_numeric_content(public: dict, internal: dict, golden: dict,
                                   snapshot: str, metric_manifest_sha256: str,
                                   *, require_internal: bool = True) -> dict:
    """Compare complete public content and hash-only internal diagnostics."""
    if golden.get("metric_manifest_sha256") != metric_manifest_sha256:
        raise ValueError("pinned metric manifest digest differs from current definitions")
    public_pin = golden.get("public_content_sha256_by_snapshot", {}).get(snapshot)
    public_digest = _digest(_canonical_research_content(public))
    if public_pin != public_digest:
        raise ValueError(f"pinned public numeric content differs for {snapshot}")
    internal_digest = _digest(_canonical_research_content(internal))
    if require_internal and golden.get("internal_content_sha256_by_snapshot", {}).get(snapshot) != internal_digest:
        raise ValueError(f"pinned internal numeric diagnostics differ for {snapshot}")
    return {"public_content_sha256": public_digest, "internal_content_sha256": internal_digest}


def initialize_internal_golden(prior: dict, candidate: dict) -> dict:
    """Initialize absent internal hashes; an existing pin is immutable."""
    without_internal = lambda value: {key: item for key, item in value.items()
                                      if key != "internal_content_sha256_by_snapshot"}
    if without_internal(prior) != without_internal(candidate):
        raise ValueError("golden initialization would change approved public or official evidence")
    if ("internal_content_sha256_by_snapshot" in prior
            and prior["internal_content_sha256_by_snapshot"] != candidate["internal_content_sha256_by_snapshot"]):
        raise ValueError("golden initialization would change approved internal diagnostics")
    return {**prior, "internal_content_sha256_by_snapshot": candidate["internal_content_sha256_by_snapshot"]}


def _code_hashes() -> dict[str, str]:
    root = Path(__file__).resolve().parent
    return {name: hashlib.sha256((root / name.removeprefix("brujula/")).read_bytes()
                                 .replace(b"\r\n", b"\n")).hexdigest()
            for name in sorted(CODE_FILES)}


def _unique(items: list[str]) -> bool:
    return len(items) == len(set(items))


def compare_inventory(expected: list[str], requested: list[str], evaluated: list[str],
                      internal: list[str] | None = None, public: list[str] | None = None) -> dict:
    groups = {"expected": expected, "requested": requested, "evaluated": evaluated}
    if internal is not None:
        groups["internal"] = internal
    if public is not None:
        groups["public"] = public
    ok = all(_unique(values) and set(values) == set(expected) for values in groups.values())
    return {"status": "PASS" if ok and bool(expected) else "BLOCKED",
            "counts": {key: len(values) for key, values in groups.items()},
            "missing": {key: sorted(set(expected) - set(values))[:20] for key, values in groups.items()},
            "extra": {key: sorted(set(values) - set(expected))[:20] for key, values in groups.items()}}


def compare_oracle_cases(expected: list[dict], actual: list[dict]) -> dict:
    eids = [item.get("id") for item in expected]
    aids = [item.get("id") for item in actual]
    if not eids or not _unique(eids) or not _unique(aids) or set(eids) != set(aids):
        return {"status": "BLOCKED", "reason": "missing_or_duplicate_oracle_case", "cases": {}}
    emap, amap = ({item["id"]: item for item in values} for values in (expected, actual))
    ledger = {}
    for case_id in sorted(eids):
        e, a = emap[case_id], amap[case_id]
        values = [e.get("estimate"), e.get("standard_error"), a.get("estimate"), a.get("standard_error")]
        if any(type(x) not in (int, float) or not math.isfinite(x) for x in values):
            return {"status": "BLOCKED", "reason": "nonfinite_or_missing_oracle_value", "cases": ledger}
        point = a["estimate"] - e["estimate"]
        se = a["standard_error"] - e["standard_error"]
        point_pass = abs(point) <= ATOL + RTOL * abs(e["estimate"])
        se_pass = abs(se) <= ATOL + RTOL * abs(e["standard_error"])
        ledger[case_id] = {"point_signed_difference": point,
                           "point_relative_difference": point / e["estimate"] if e["estimate"] else None,
                           "se_signed_difference": se,
                           "se_relative_difference": se / e["standard_error"] if e["standard_error"] else None,
                           "point_pass": point_pass, "se_pass": se_pass}
    return {"status": "PASS" if all(v["point_pass"] and v["se_pass"] for v in ledger.values()) else "BLOCKED",
            "rtol": RTOL, "atol": ATOL, "cases": ledger}


def write_attempt(audit_dir: Path, result: dict) -> Path:
    audit_dir.mkdir(parents=True, exist_ok=True)
    current = audit_dir / "current.json"
    staged = audit_dir / "current.tmp"
    staged.write_text(json.dumps(result, sort_keys=True, ensure_ascii=False, allow_nan=False, indent=2) + "\n",
                      encoding="utf-8")
    os.replace(staged, current)
    return current


def _run_attempt_locked(audit_dir: Path, operation, context: dict) -> dict:
    """Fail closed around a complete acceptance operation, including local fixtures."""
    attempt_id = str(uuid.uuid4())
    started_at = datetime.now(timezone.utc).isoformat()
    write_attempt(audit_dir, {"status": "BLOCKED", "reason": "RUNNING; prior success invalidated",
                              "attempt_id": attempt_id})
    try:
        result = operation()
        if not isinstance(result, dict) or result.get("status") != "PASS":
            raise ValueError("acceptance operation did not pass")
    except Exception as exc:
        result = {"status": "BLOCKED", "reason": f"{type(exc).__name__}: {exc}"}
    result = {**context, **result, "attempt_id": attempt_id}
    receipt = {**result, "started_at": started_at,
               "completed_at": datetime.now(timezone.utc).isoformat(),
               "audit_dir": str(audit_dir)}
    receipts = audit_dir / "attempts"
    receipts.mkdir(parents=True, exist_ok=True)
    with (receipts / f"{attempt_id}.json").open("x", encoding="utf-8") as stream:
        json.dump(receipt, stream, indent=2, sort_keys=True)
        stream.write("\n")
    write_attempt(audit_dir, result)
    return result


def run_attempt(audit_dir: Path, operation, *, context: dict | None = None) -> dict:
    """Serialize acceptance attempts and seal a distinct receipt for each call."""
    audit_dir = Path(audit_dir).resolve()
    audit_dir.mkdir(parents=True, exist_ok=True)
    with BuildLock(audit_dir):
        return _run_attempt_locked(audit_dir, operation, context or {})


def _grain(snapshot: str, period: str, domain: dict, metric: str) -> str:
    return "|".join((snapshot, domain["population_id"], domain["field_of_study_id"], "all", "all",
                     domain["geography_id"], domain["recorded_sex_id"], period, metric, estimates.METHOD_ID))


DOMAIN_KEYS = ("population_id", "field_of_study_id", "geography_id", "recorded_sex_id")


def expected_acceptance_domains(snapshot: str, observed_fields: list[str],
                                catalog_keys: set[str] | frozenset[str]) -> list[dict]:
    """Independent complete gate inventory; partial estimator requests remain valid."""
    focal = {code.zfill(6) for code in FOCUS_CODES}
    observed = set(observed_fields)
    if (len(observed) != len(observed_fields) or not observed <= set(catalog_keys)
            or not focal <= set(catalog_keys)):
        raise ValueError("acceptance field inventory differs from verified quarter catalog")
    domains = set()

    def add(population: str, field: str = "all", geo: str = "mx", sex: str = "all") -> None:
        domains.add((population, field, geo, sex))

    add(NATIONAL_15_PLUS_CONTEXT)
    add(COMPLETED_PROFESSIONAL_KNOWN_AGE)
    for field in focal:
        add(COMPLETED_PROFESSIONAL_KNOWN_AGE, field)
    if snapshot == LATEST:
        for field in observed:
            add(COMPLETED_PROFESSIONAL_KNOWN_AGE, field)
        for field in ("all", *sorted(focal)):
            for entity in range(1, 33):
                add(COMPLETED_PROFESSIONAL_KNOWN_AGE, field, f"{entity:02d}")
            for sex in ("1", "2"):
                add(COMPLETED_PROFESSIONAL_KNOWN_AGE, field, "mx", sex)
    if snapshot in {"enoe_2025_q2", LATEST}:
        add(NATIONAL_15_PLUS_CONTEXT, "all", "02")
    return [dict(zip(DOMAIN_KEYS, values)) for values in sorted(domains)]


def verify_acceptance_domains(actual: list[dict], required: list[dict]) -> dict:
    def key(domain: dict) -> str:
        return "|".join(str(domain[name]) for name in DOMAIN_KEYS)
    ledger = compare_inventory([key(d) for d in required], [key(d) for d in actual],
                               [key(d) for d in actual])
    if ledger["status"] != "PASS":
        raise ValueError(f"complete acceptance domain inventory mismatch: {ledger}")
    return ledger


def _oracle_specs() -> list[dict]:
    specs = []
    def add(population, field, geo, metric):
        specs.append({"id": "|".join((population, field, geo, metric)),
                      "population_id": population, "field_of_study_id": field,
                      "geography_id": geo, "metric_id": metric})
    for metric in ("population_total", "occupied_total", "pea_total", "unemployed_total",
                   "participation_rate", "unemployment_rate", "positive_income_mean"):
        add("national_15_plus_context", "all", "mx", metric)
    for field in ("all", *estimates.FOCAL_FIELDS):
        for metric in ("population_total", "occupied_total", "participation_rate", "positive_income_mean"):
            add("completed_professional_known_age", field, "mx", metric)
    for metric in ("population_total", "unemployment_rate", "positive_income_mean"):
        add("national_15_plus_context", "all", "02", metric)
    return specs


def _write_oracle_frame(frame, path: Path) -> None:
    names = ("stratum", "psu", "weight", "eda", "cs_p13_1", "cs_p16", "cs_p14_c",
             "entity", "clase1", "clase2", "ing7c", "ingocup")
    columns = (frame.est_d_tri, frame.upm, frame.weight, frame.eda, frame.cs_p13_1,
               frame.cs_p16, frame.cs_p14_c,
               frame.columns[frame.inventory["geography_header"].lower()], frame.clase1,
               frame.clase2, frame.ing7c, frame.ingocup)
    with path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.writer(stream)
        writer.writerow(names)
        writer.writerows(zip(*columns))


def _run_oracle(frame, records: list[dict], audit_dir: Path, runtime: dict) -> dict:
    specs = _oracle_specs()
    keyed = {"|".join((row["population_id"], row["field_of_study_id"], row["geography_id"], row["metric_id"])): row
             for row in records if row["recorded_sex_id"] == "all"}
    expected = []
    for spec in specs:
        row = keyed.get(spec["id"])
        if row is None or row["estimate"] is None or row["precision"]["standard_error"] is None:
            raise ValueError(f"oracle case unavailable: {spec['id']}")
        expected.append({"id": spec["id"], "estimate": row["estimate"],
                         "standard_error": row["precision"]["standard_error"]})
    frame_path = audit_dir / "oracle-frame.csv"
    cases_path = audit_dir / "oracle-cases.json"
    ledger_path = audit_dir / "oracle-r-aggregate.json"
    cases_path.write_text(json.dumps({"cases": specs}, sort_keys=True), encoding="utf-8")
    _write_oracle_frame(frame, frame_path)
    try:
        oracle = _execute_r(frame_path, cases_path, ledger_path, runtime)
    finally:
        frame_path.unlink(missing_ok=True)
    comparison = compare_oracle_cases(expected, oracle["cases"])
    comparison.update({"r_version": oracle["r_version"], "survey_version": oracle["survey_version"],
                       "design_df": oracle["design_df"], "singleton_policy": oracle["singleton_policy"],
                       "source_sha256": frame.inventory["raw_sha256"], "case_ids": sorted(x["id"] for x in specs)})
    return comparison


def _r_runtime(rscript: Path | None, r_home: Path | None, r_lib: Path | None) -> dict:
    candidate = rscript or os.environ.get("BRUJULA_RSCRIPT")
    if candidate is None and r_home is not None:
        candidate = Path(r_home) / "bin" / ("Rscript.exe" if os.name == "nt" else "Rscript")
    if candidate is None:
        candidate = shutil.which("Rscript")
    if candidate is None:
        raise FileNotFoundError("Rscript executable is required")
    executable = Path(candidate).resolve()
    if not executable.is_file():
        raise FileNotFoundError(f"Rscript executable unavailable: {executable}")
    library = Path(r_lib).resolve() if r_lib is not None else None
    if library is None or not library.is_dir():
        raise FileNotFoundError("explicit R survey library is required")
    env = {**os.environ, "BRUJULA_R_LIB": str(library)}
    if r_home is not None:
        home = Path(r_home).resolve()
        if not home.is_dir():
            raise FileNotFoundError(f"R home unavailable: {home}")
        env["R_HOME"] = str(home)
    version = subprocess.run([str(executable), "--version"], capture_output=True,
                             text=True, timeout=30, env=env)
    if version.returncode != 0 or "version" not in version.stdout + version.stderr:
        raise ValueError("Rscript version check failed")
    expression = ('lib <- Sys.getenv("BRUJULA_R_LIB"); '
                  'for (p in c("survey", "jsonlite")) { '
                  'path <- find.package(p, lib.loc=lib, quiet=TRUE); '
                  'if (length(path) != 1) quit(status=3); '
                  'cat(p, as.character(packageVersion(p, lib.loc=lib)), '
                  'normalizePath(path, winslash="/"), sep="\\t"); cat("\\n") }')
    packages = subprocess.run([str(executable), "--vanilla", "-e", expression],
                              capture_output=True, text=True, timeout=30, env=env)
    lines = [line.split("\t") for line in packages.stdout.splitlines() if line.strip()]
    if (packages.returncode != 0 or len(lines) != 2
            or {parts[0] for parts in lines if len(parts) == 3} != {"survey", "jsonlite"}
            or any(not Path(parts[2]).resolve().is_relative_to(library) for parts in lines if len(parts) == 3)):
        raise ValueError("explicit R library lacks survey/jsonlite packages")
    package_versions = {name: {"version": pkg_version, "path": path}
                        for name, pkg_version, path in lines}
    return {"rscript": str(executable), "rscript_sha256": hashlib.sha256(executable.read_bytes()).hexdigest(),
            "r_home": str(r_home) if r_home else None,
            "r_lib": str(library), "version": (version.stdout + version.stderr).strip(),
            "packages": package_versions, "env": env}


def _execute_r(frame_path: Path, cases_path: Path, ledger_path: Path, runtime: dict) -> dict:
    process = subprocess.run([runtime["rscript"], str(oracle_script_path()), "--frame", str(frame_path),
                              "--cases", str(cases_path), "--output", str(ledger_path)],
                             capture_output=True, text=True, timeout=900, env=runtime["env"])
    if process.returncode:
        raise ValueError(f"R oracle exit {process.returncode}: {process.stderr[-1000:]}")
    return json.loads(ledger_path.read_text(encoding="utf-8"))


def _run_analytic_oracle(audit_dir: Path, runtime: dict) -> dict:
    """Independent small full-design control with the age 97/98 cohort edge."""
    rows = []
    for i in range(40):
        age = 97 if i < 4 else 98 if i < 6 else 30
        field = "033100" if i < 6 else "031300"
        rows.append({"stratum": str(i // 20 + 1), "psu": str(i + 1), "weight": str(i + 1),
                     "eda": str(age), "cs_p13_1": "7", "cs_p16": "1",
                     "cs_p14_c": field, "entity": "2" if i < 20 else "1",
                     "clase1": "1" if i % 3 else "2", "clase2": "1" if i % 2 else "2",
                     "ing7c": "1", "ingocup": str(100 + i)})
    specs = [
        {"id": "analytic_national_population", "population_id": "national_15_plus_context",
         "field_of_study_id": "all", "geography_id": "mx", "metric_id": "population_total"},
        {"id": "analytic_derecho_known_age", "population_id": "completed_professional_known_age",
         "field_of_study_id": "033100", "geography_id": "mx", "metric_id": "population_total"},
        {"id": "analytic_derecho_occupied", "population_id": "completed_professional_known_age",
         "field_of_study_id": "033100", "geography_id": "mx", "metric_id": "occupied_total"},
        {"id": "analytic_derecho_bc", "population_id": "completed_professional_known_age",
         "field_of_study_id": "033100", "geography_id": "02", "metric_id": "population_total"},
    ]
    frame_path = audit_dir / "analytic-frame.csv"
    cases_path = audit_dir / "analytic-cases.json"
    output_path = audit_dir / "analytic-r-aggregate.json"
    with frame_path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    cases_path.write_text(json.dumps({"cases": specs}), encoding="utf-8")
    weights = [float(row["weight"]) for row in rows]
    design = SurveyDesign(weights, [row["stratum"] for row in rows],
                          [row["psu"] for row in rows], singleton_policy="adjust")
    expected = []
    for spec in specs:
        domain = [15 <= int(row["eda"]) <= (98 if spec["population_id"] == "national_15_plus_context" else 97)
                  and (spec["field_of_study_id"] == "all" or row["cs_p14_c"] == spec["field_of_study_id"])
                  and (spec["geography_id"] == "mx" or int(row["entity"]) == int(spec["geography_id"]))
                  for row in rows]
        indicator = [int(row["clase2"] == "1") if spec["metric_id"] == "occupied_total" else 1 for row in rows]
        result = design.total(indicator, domain=domain)
        expected.append({"id": spec["id"], "estimate": result["estimate"],
                         "standard_error": result["standard_error"]})
    try:
        oracle = _execute_r(frame_path, cases_path, output_path, runtime)
    finally:
        frame_path.unlink(missing_ok=True)
    comparison = compare_oracle_cases(expected, oracle["cases"])
    comparison.update({"known_age_97_included_n": 4, "age_98_excluded_n": 2,
                       "r_version": oracle["r_version"], "survey_version": oracle["survey_version"]})
    if comparison["status"] != "PASS":
        raise ValueError("analytic R oracle control failed")
    return comparison


def _verify_result(result: dict, domains: list[dict], metric_ids: list[str],
                   snapshot: str, period: str, required_domains: list[dict] | None = None) -> dict:
    audit, internal, public = result["audit"], result["internal"], result["public"]
    if validate_research_v2(internal) or validate_public_research_v2(public):
        raise ValueError("strict v2 validation failed")
    if any(value is not True for value in audit["requested_cells"].values()):
        raise ValueError("requested cell was not declared true")
    if required_domains is not None:
        verify_acceptance_domains(domains, required_domains)
    expected = [_grain(snapshot, period, domain, metric)
                for domain in (required_domains if required_domains is not None else domains)
                for metric in metric_ids]
    def keyed(rows):
        return {"|".join(str(row[k]) for k in GRAIN): row for row in rows}
    internal_by = keyed(internal["records"])
    public_by = keyed(public["records"])
    ledger = compare_inventory(expected, list(audit["requested_cells"]), list(audit["evaluated_cells"]),
                               ["|".join(str(row[k]) for k in GRAIN) for row in internal["records"]],
                               ["|".join(str(row[k]) for k in GRAIN) for row in public["records"]])
    if ledger["status"] != "PASS":
        raise ValueError(f"request/evaluation/record grain mismatch: {ledger}")
    for key in sorted(internal_by):
        row, visible = internal_by[key], public_by[key]
        evaluation = audit["evaluated_cells"][key]
        if (evaluation["status"] != row["status"]
                or evaluation["has_estimate"] != (row["estimate"] is not None)
                or evaluation["reason"] != row["reason"]
                or evaluation["coverage"]["eligible_n"] != row["sample_size"]
                or evaluation["method_version"] != row["method_version"]
                or evaluation["synthetic"] != row["synthetic"]):
            raise ValueError("evaluated-cell metadata differs from computed record")
        if row["value"] is None:
            if not row["reason"] or not evaluation["reason"]:
                raise ValueError("suppressed cell lacks computed reason")
            if row["estimate"] is None and evaluation["coverage"]["eligible_n"] > 0:
                raise ValueError("fabricated unavailable estimate despite eligible denominator")
            if any(visible[k] is not None for k in ("value", "weighted_denominator")):
                raise ValueError("suppressed public numeric leak")
            if visible["support"]["weighted_support_total"] is not None or any(
                visible["precision"][k] is not None for k in
                ("standard_error", "coefficient_variation", "ci90_lower", "ci90_upper")):
                raise ValueError("suppressed public precision leak")
        elif visible["value"] != row["value"]:
            raise ValueError("public value differs from authorized internal value")
        if row["precision"]["official_precision"] is not False:
            raise ValueError("project precision mislabeled official")
    if audit["synthetic"] or audit["provenance"] != "approved_pinned_snapshot":
        raise ValueError("real source provenance failed")
    return ledger


def _semantic_audit(frame, frame_audit: dict) -> dict:
    """Recount corrected raw category joints on the already loaded frame."""
    occupied = frame.clase2 == 1
    sub_joint = {}
    for clase2, sub_o in zip(frame.clase2, frame.sub_o):
        key = f"clase2={clase2}|sub_o={sub_o}"
        sub_joint[key] = sub_joint.get(key, 0) + 1
    hours_joint = {}
    for hours, duration in zip(frame.hrsocup[occupied], frame.dur9c[occupied]):
        label = "zero" if hours == 0 else "valid_1_168" if 1 <= hours <= 168 else "other"
        key = f"hours={label}|dur9c={duration}"
        hours_joint[key] = hours_joint.get(key, 0) + 1
    cohort = (frame.eda >= 15) & (frame.eda <= 97) & (frame.cs_p13_1 == 7) & (frame.cs_p16 == 1)
    return {"occupied_rows_clase2_eq_1": int(np.count_nonzero(occupied)),
            "pea_rows_clase1_eq_1": int(np.count_nonzero(frame.clase1 == 1)),
            "sub_o_by_clase2": dict(sorted(sub_joint.items())),
            "hours_duration_joint_occupied": dict(sorted(hours_joint.items())),
            "principal_cohort": {"rows": int(np.count_nonzero(cohort)),
                                 "weighted_rows": int(np.sum(frame.weight[cohort], dtype=np.float64))},
            "n_psus": frame_audit["design"]["psus"],
            "n_strata": frame_audit["design"]["strata"],
            "singleton_strata": frame_audit["design"]["singleton_strata"],
            "source_member_sha256": frame.inventory["sdem_member"]["sha256"],
            "dictionary_sha256": frame.inventory["dictionary_member"]["sha256"]}


def quarter_claim_guard(quarter_outputs: list[dict]) -> dict:
    """Keep each quarter as a separate accepted estimate, without panel claims."""
    ids = [item["snapshot_id"] for item in quarter_outputs]
    if not ids or not _unique(ids):
        raise ValueError("duplicate or absent quarter in claim guard")
    forbidden = {"distinct_people_8q", "independent_quarter_significance",
                 "temporal_significance", "combined_person_count"}
    for item in quarter_outputs:
        if forbidden & item.keys():
            raise ValueError("unsupported distinct-person or significance claim")
    return {"quarters": [{"snapshot_id": item["snapshot_id"],
                           "numeric_digest": item["numeric_digest"]} for item in quarter_outputs],
            "no_distinct_person_sum": True, "no_independent_quarter_significance": True}


def _accept_unlocked(output_root: Path, audit_dir: Path, *, source_root: Path,
                     workbook: Path, pdf: Path, rscript: Path | None = None,
                     r_home: Path | None = None, r_lib: Path | None = None,
                     generate_golden: bool = False) -> dict:
    from .official_reconciliation import (
        reconcile, check_2026_pdf_benchmark, COUNT_EXPECTED, RATE_EXPECTED,
        PDF_2026_Q2_SHA256, WORKBOOK_SHA256,
    )
    if generate_golden:
        raise ValueError("ordinary installed acceptance cannot generate golden")
    output_root, audit_dir, source_root = _separate_roots(output_root, audit_dir, source_root)
    if any(path.name != ".build.lock" for path in output_root.iterdir()):
        raise FileExistsError("acceptance output root already contains historical artifacts")
    if hashlib.sha256(Path(workbook).read_bytes()).hexdigest() != WORKBOOK_SHA256:
        raise ValueError("official workbook SHA-256 mismatch")
    if hashlib.sha256(Path(pdf).read_bytes()).hexdigest() != PDF_2026_Q2_SHA256:
        raise ValueError("2026-Q2 official PDF SHA-256 mismatch")
    output_root.mkdir(parents=True, exist_ok=True)
    audit_dir.mkdir(parents=True, exist_ok=True)
    golden_path = require_installed_package_path(aggregate_golden_path())
    if hashlib.sha256(golden_path.read_bytes().replace(b"\r\n", b"\n")).hexdigest() != GOLDEN_LF_SHA256:
        raise ValueError("independent package golden digest differs")
    resources = _numeric_resource_digests()
    runtime = _r_runtime(rscript, r_home, r_lib)
    started = time.monotonic()
    entry_code_hashes = _code_hashes()
    inventory = inventory_all(source_root)
    if len(inventory) != 8:
        raise ValueError("exactly eight pinned snapshots required")
    registry = json.loads(snapshot_catalog_path().read_text(encoding="utf-8"))
    ids = [item["id"] for item in registry["snapshots"]]
    if [item["snapshot_id"] for item in inventory] != ids:
        raise ValueError("approved catalog order or inventory mismatch")
    metric_manifest = load_metric_manifest()
    metrics = sorted(item["id"] for item in metric_manifest["metrics"])
    if len(metrics) != 23:
        raise ValueError("metric catalog is incomplete")
    analytic_oracle = _run_analytic_oracle(audit_dir, runtime)
    (audit_dir / "analytic-oracle-comparison.json").write_text(json.dumps(
        analytic_oracle, indent=2, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8")
    quarter_ledgers = {}
    oracle = official = pdf_benchmark = None
    golden_cases = {}
    prior_golden = json.loads(golden_path.read_text(encoding="utf-8"))
    semantic_baseline = prior_golden["semantic_baseline"]
    internal_digests = {}
    for item in inventory:
        snapshot = item["snapshot_id"]
        period = item["period"]
        mark = time.monotonic()
        frame, frame_audit = load_snapshot_frame(snapshot, source_root)
        if frame.synthetic or frame.provenance != "approved_pinned_snapshot":
            raise ValueError("real frame provenance failed")
        semantic = _semantic_audit(frame, frame_audit)
        if semantic != semantic_baseline.get(snapshot):
            raise ValueError(f"corrected occupied/suboccupation/hours design audit mismatch: {snapshot}")
        field_ids = sorted(set(frame.cs_p14_c[(frame.eda >= 15) & (frame.eda <= 97) &
                                                   (frame.cs_p13_1 == 7) & (frame.cs_p16 == 1)]) - {None})
        required_domains = expected_acceptance_domains(snapshot, field_ids, frame.cmpe_catalog_keys)
        domains = estimates.required_estimation_domains(snapshot, latest_snapshot_id=LATEST, field_ids=field_ids)
        if snapshot in {"enoe_2025_q2", LATEST}:
            domains.append({"population_id": "national_15_plus_context", "field_of_study_id": "all",
                            "geography_id": "02", "recorded_sex_id": "all"})
        verify_acceptance_domains(domains, required_domains)
        with patch.object(estimates, "load_snapshot_frame", return_value=(frame, frame_audit)):
            result = estimates.estimate_snapshot(snapshot, source_root, domains=domains)
        coverage = _verify_result(result, domains, metrics, snapshot, period, required_domains)
        audit = result["audit"]
        public = result["public"]
        pinned = compare_pinned_numeric_content(public, result["internal"], prior_golden,
                                                snapshot, metric_manifest["content_sha256"],
                                                require_internal=not generate_golden)
        internal_digests[snapshot] = pinned["internal_content_sha256"]
        counts = {}
        for row in public["records"]:
            category = f"{row['metric_id']}|{row['status']}|{row['reason']}"
            counts[category] = counts.get(category, 0) + 1
        ledger = {"snapshot_id": snapshot, "period": period, "source_sha256": item["raw_sha256"],
                  "dictionary_sha256": audit["dictionary_sha256"], "method_version": audit["method_version"],
                  "design": audit["design"], "source_frame_audit": audit["source_frame_audit"],
                  "semantic_audit": semantic,
                  "population_coverage": audit["population_coverage"], "request_comparison": coverage,
                  "requested_cells": audit["requested_cells"],
                  "evaluated_cells": audit["evaluated_cells"],
                  "requested_count": audit["requested_count"], "evaluated_count": audit["evaluated_count"],
                  "metric_status_counts": dict(sorted(counts.items())),
                  "public_records": public["records"], "numeric_digest": _digest(public["records"]),
                  "public_content_sha256": pinned["public_content_sha256"],
                  "internal_content_sha256": pinned["internal_content_sha256"],
                  "elapsed_seconds": round(time.monotonic() - mark, 3)}
        ledger_path = output_root / f"{snapshot}-aggregate.json"
        public_path = output_root / f"{snapshot}-public-v2.json"
        public_path.write_text(json.dumps(public, sort_keys=True, ensure_ascii=False,
                                           allow_nan=False, indent=2) + "\n", encoding="utf-8")
        ledger_path.write_text(json.dumps(ledger, sort_keys=True, ensure_ascii=False,
                                          allow_nan=False, indent=2) + "\n", encoding="utf-8")
        quarter_ledgers[snapshot] = {"path": str(ledger_path), "public_v2_path": str(public_path),
                                     "public_v2_digest": _digest(public), "numeric_digest": ledger["numeric_digest"],
                                     "public_content_sha256": pinned["public_content_sha256"],
                                     "internal_content_sha256": pinned["internal_content_sha256"],
                                     "requested_count": ledger["requested_count"], "elapsed_seconds": ledger["elapsed_seconds"]}
        for row in result["internal"]["records"]:
            key = "|".join((snapshot, row["population_id"], row["field_of_study_id"],
                            row["geography_id"], row["recorded_sex_id"], row["metric_id"]))
            if key in ("enoe_2026_q2|national_15_plus_context|all|mx|all|population_total",
                       "enoe_2026_q2|completed_professional_known_age|033100|mx|all|population_total"):
                golden_cases[key] = {"estimate": row["estimate"],
                                     "standard_error": row["precision"]["standard_error"]}
        if snapshot == "enoe_2025_q2":
            official = reconcile(source_root, Path(workbook),
                                 result["internal"]["records"])
            (audit_dir / "official-aggregate.json").write_text(json.dumps(official, indent=2,
                    sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8")
            if official["status"] != "PASS":
                raise ValueError("official compatible count/rate reconciliation failed")
        if snapshot == LATEST:
            pdf_benchmark = check_2026_pdf_benchmark(Path(pdf),
                                                     result["internal"]["records"])
            (audit_dir / "official-2026q2-pdf-aggregate.json").write_text(
                json.dumps(pdf_benchmark, indent=2, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8")
            if pdf_benchmark["status"] != "PASS":
                raise ValueError("2026-Q2 pinned official PDF national counts failed")
            oracle = _run_oracle(frame, result["internal"]["records"], audit_dir, runtime)
            (audit_dir / "oracle-comparison.json").write_text(json.dumps(oracle, indent=2,
                    sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8")
            if oracle["status"] != "PASS":
                raise ValueError("independent R oracle failed")
        print(json.dumps({"snapshot": snapshot, "status": "PASS", "seconds": ledger["elapsed_seconds"],
                          "cells": ledger["evaluated_count"]}), flush=True)
    golden = {"schema_version": "1.0", "source_2025_q2_sha256": inventory[3]["raw_sha256"],
              "workbook_sha256": official["workbook_sha256"],
              "rounding_half_unit": official["rounding_half_unit"],
              "official_counts": COUNT_EXPECTED, "official_rates": RATE_EXPECTED,
              "latest_source_sha256": inventory[-1]["raw_sha256"],
              "pdf_2026_q2_sha256": PDF_2026_Q2_SHA256,
              "oracle_cases": golden_cases,
              "official_cells": official["cells"],
              "semantic_baseline": semantic_baseline,
              "metric_manifest_sha256": metric_manifest["content_sha256"],
              "public_content_sha256_by_snapshot": prior_golden["public_content_sha256_by_snapshot"],
              "internal_content_sha256_by_snapshot": internal_digests,
              "national_population_se_relative_difference":
                  official["cells"]["mx|population_total"]["se_relative_difference"]}
    if prior_golden != golden:
        raise ValueError("aggregate golden fixture differs from approved numeric content")
    claim_guard = quarter_claim_guard([{"snapshot_id": key, **value} for key, value in quarter_ledgers.items()])
    if inventory_all(source_root) != inventory:
        raise ValueError("approved source current changed during numerical acceptance")
    if _numeric_resource_digests() != resources:
        raise ValueError("numerical package resource changed during acceptance")
    final_runtime = _r_runtime(rscript, r_home, r_lib)
    if any(final_runtime[key] != runtime[key] for key in
           ("rscript_sha256", "version", "packages")):
        raise ValueError("R executable or explicit survey library changed during acceptance")
    if _code_hashes() != entry_code_hashes:
        raise ValueError("acceptance code changed during run; results are exploratory only")
    manifest = {"status": "PASS", "snapshots": quarter_ledgers,
                "source_root": str(source_root), "output_root": str(output_root),
                "audit_dir": str(audit_dir),
                "source_receipt_ids": {item["snapshot_id"]: item["receipt_run_id"] for item in inventory},
                "resource_sha256": resources,
                "rscript_sha256": runtime["rscript_sha256"],
                "workbook_path": str(Path(workbook).resolve()), "pdf_path": str(Path(pdf).resolve()),
                "rscript": runtime["rscript"], "r_home": runtime["r_home"],
                "r_lib": runtime["r_lib"], "rscript_version": runtime["version"],
                "r_packages": runtime["packages"],
                "runtime": {"python": platform.python_version(), "numpy": np.__version__},
                "metric_manifest_sha256": metric_manifest["content_sha256"],
                "code_sha256": entry_code_hashes,
                "oracle": {"status": oracle["status"], "r_version": oracle["r_version"],
                           "survey_version": oracle["survey_version"], "case_count": len(oracle["cases"])},
                "analytic_oracle": {"status": analytic_oracle["status"],
                                    "case_count": len(analytic_oracle["cases"])},
                "official": {"status": official["status"], "workbook_sha256": official["workbook_sha256"],
                             "national_population_se_relative_difference": golden["national_population_se_relative_difference"]},
                "pdf_2026_q2": {"status": pdf_benchmark["status"], "sha256": pdf_benchmark["pdf_sha256"]},
                "numeric_content_digest": _digest({key: value["numeric_digest"] for key, value in quarter_ledgers.items()}),
                "elapsed_seconds": round(time.monotonic() - started, 3),
                "no_distinct_person_sum": claim_guard["no_distinct_person_sum"],
                "no_independent_quarter_significance": claim_guard["no_independent_quarter_significance"],
                "official_precision": False}
    if manifest["numeric_content_digest"] != NUMERIC_DIGEST:
        raise ValueError("canonical numerical digest differs from accepted content")
    return manifest


def _separate_roots(output_root: Path, audit_dir: Path, source_root: Path) -> tuple[Path, Path, Path]:
    roots = tuple(Path(path).resolve() for path in (output_root, audit_dir, source_root))
    if any(a.is_relative_to(b) or b.is_relative_to(a)
           for i, a in enumerate(roots) for b in roots[i + 1:]):
        raise ValueError("source, output and audit roots must not overlap")
    return roots


def _accept_operation(output_root: Path, audit_dir: Path, *, source_root: Path,
                      workbook: Path, pdf: Path, rscript: Path | None = None,
                      r_home: Path | None = None, r_lib: Path | None = None,
                      generate_golden: bool = False) -> dict:
    output_root, audit_dir, source_root = _separate_roots(output_root, audit_dir, source_root)
    output_root.mkdir(parents=True, exist_ok=True)
    with BuildLock(output_root):
        return _accept_unlocked(output_root, audit_dir, source_root=source_root,
                                workbook=workbook, pdf=pdf, rscript=rscript,
                                r_home=r_home, r_lib=r_lib,
                                generate_golden=generate_golden)


def _replay_operation(source_root: Path, sealed_run: Path, audit_dir: Path, *,
                      rscript: Path | None = None, r_home: Path | None = None,
                      r_lib: Path | None = None) -> dict:
    """Read-only source and content proof over an existing sealed acceptance."""
    source_root, sealed_run, audit_dir = (Path(path).resolve() for path in
                                          (source_root, sealed_run, audit_dir))
    if audit_dir.is_relative_to(source_root) or source_root.is_relative_to(audit_dir):
        raise ValueError("replay audit and source roots overlap")
    if sealed_run.is_relative_to(audit_dir):
        raise ValueError("replay audit cannot contain the sealed baseline")
    if sealed_run.parent.name != "attempts":
        raise ValueError("replay requires an immutable acceptance attempt receipt")
    sealed = json.loads(sealed_run.read_text(encoding="utf-8"))
    if sealed.get("status") != "PASS" or sealed.get("numeric_content_digest") != NUMERIC_DIGEST:
        raise ValueError("sealed numerical acceptance is unavailable or changed")
    if sealed.get("code_sha256") != _code_hashes():
        raise ValueError("sealed executing code inventory changed")
    if sealed.get("resource_sha256") != _numeric_resource_digests():
        raise ValueError("sealed resource inventory changed")
    runtime = _r_runtime(rscript, r_home, r_lib)
    if (runtime["version"] != sealed.get("rscript_version")
            or runtime["packages"] != sealed.get("r_packages")
            or runtime["rscript_sha256"] != sealed.get("rscript_sha256")):
        raise ValueError("Rscript identity changed")
    inventory = inventory_all(source_root)
    if {item["snapshot_id"]: item["receipt_run_id"] for item in inventory} != sealed.get("source_receipt_ids"):
        raise ValueError("source current receipt identity changed")
    golden = json.loads(aggregate_golden_path().read_text(encoding="utf-8"))
    for item in inventory:
        sid = item["snapshot_id"]
        prior = sealed["snapshots"][sid]
        ledger = json.loads(Path(prior["path"]).read_text(encoding="utf-8"))
        public = json.loads(Path(prior["public_v2_path"]).read_text(encoding="utf-8"))
        if ledger["source_sha256"] != item["raw_sha256"] or ledger["public_records"] != public["records"]:
            raise ValueError(f"sealed public rows or source changed: {sid}")
        if _digest(public) != prior["public_v2_digest"] or _digest(public["records"]) != prior["numeric_digest"]:
            raise ValueError(f"sealed public digest changed: {sid}")
        if _digest(_canonical_research_content(public)) != golden["public_content_sha256_by_snapshot"][sid]:
            raise ValueError(f"independent public pin changed: {sid}")
    if _digest({sid: sealed["snapshots"][sid]["numeric_digest"] for sid in sorted(sealed["snapshots"])}) != NUMERIC_DIGEST:
        raise ValueError("canonical numerical content digest changed")
    replay_id = str(uuid.uuid4())
    replay_audit = audit_dir / "replay-runs" / replay_id
    output_root = audit_dir.parent / f"{audit_dir.name}-replay-outputs" / replay_id
    _separate_roots(output_root, replay_audit, source_root)
    prior_output = Path(sealed["output_root"]).resolve()
    if output_root.is_relative_to(prior_output) or prior_output.is_relative_to(output_root):
        raise ValueError("replay output overlaps sealed accepted output")
    recomputed = _accept_operation(output_root, replay_audit, source_root=source_root,
                                   workbook=Path(sealed["workbook_path"]),
                                   pdf=Path(sealed["pdf_path"]), rscript=rscript,
                                   r_home=r_home, r_lib=r_lib)
    if recomputed["numeric_content_digest"] != sealed["numeric_content_digest"]:
        raise ValueError("recomputed numerical digest differs from sealed acceptance")
    for sid in sorted(sealed["snapshots"]):
        old = json.loads(Path(sealed["snapshots"][sid]["public_v2_path"]).read_text(encoding="utf-8"))
        fresh = json.loads(Path(recomputed["snapshots"][sid]["public_v2_path"]).read_text(encoding="utf-8"))
        if fresh["records"] != old["records"] or fresh != old:
            raise ValueError(f"recomputed public rows differ from sealed acceptance: {sid}")
    if recomputed["oracle"] != sealed["oracle"] or recomputed["official"] != sealed["official"]:
        raise ValueError("recomputed independent R or official gate differs")
    return {"status": "PASS", "operation": "read_only_replay",
            "source_root": str(Path(source_root).resolve()), "audit_dir": str(Path(audit_dir).resolve()),
            "sealed_run": str(sealed_run), "output_root": str(output_root),
            "replay_audit": str(replay_audit),
            "recomputed_manifest": recomputed, "numeric_content_digest": NUMERIC_DIGEST,
            "source_receipt_ids": sealed["source_receipt_ids"], "code_sha256": sealed["code_sha256"],
            "resource_sha256": sealed["resource_sha256"], "rscript": runtime["rscript"],
            "rscript_sha256": runtime["rscript_sha256"],
            "rscript_version": runtime["version"], "r_packages": runtime["packages"],
            "official": recomputed["official"], "pdf_2026_q2": recomputed["pdf_2026_q2"],
            "r_home": runtime["r_home"], "r_lib": runtime["r_lib"]}


def accept(output_root: Path, audit_dir: Path, *, source_root: Path,
           workbook: Path, pdf: Path, rscript: Path | None = None,
           r_home: Path | None = None, r_lib: Path | None = None,
           generate_golden: bool = False) -> dict:
    """Run frozen acceptance with a current pointer and immutable full receipt."""
    context = {"source_root": str(Path(source_root).resolve()),
               "output_root": str(Path(output_root).resolve()),
               "workbook_path": str(Path(workbook).resolve()),
               "pdf_path": str(Path(pdf).resolve()),
               "rscript": str(Path(rscript).resolve()) if rscript else None}
    return run_attempt(audit_dir, lambda: _accept_operation(
        output_root, audit_dir, source_root=source_root, workbook=workbook, pdf=pdf,
        rscript=rscript, r_home=r_home, r_lib=r_lib,
        generate_golden=generate_golden), context=context)


def replay(source_root: Path, sealed_run: Path, audit_dir: Path, *,
           rscript: Path | None = None, r_home: Path | None = None,
           r_lib: Path | None = None) -> dict:
    """Recompute frozen inputs and seal a separate immutable replay receipt."""
    context = {"source_root": str(Path(source_root).resolve()),
               "sealed_run": str(Path(sealed_run).resolve()),
               "rscript": str(Path(rscript).resolve()) if rscript else None}
    return run_attempt(audit_dir, lambda: _replay_operation(
        source_root, sealed_run, audit_dir, rscript=rscript, r_home=r_home,
        r_lib=r_lib), context=context)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-root", type=Path, required=True)
    parser.add_argument("--output-root", type=Path)
    parser.add_argument("--audit-dir", type=Path, required=True)
    parser.add_argument("--workbook", type=Path)
    parser.add_argument("--pdf", type=Path)
    parser.add_argument("--rscript", type=Path)
    parser.add_argument("--r-home", type=Path)
    parser.add_argument("--r-lib", type=Path)
    parser.add_argument("--replay", type=Path, help="sealed acceptance JSON for read-only replay")
    parser.add_argument("--generate-golden", action="store_true")
    args = parser.parse_args()
    if args.replay:
        result = replay(args.source_root, args.replay, args.audit_dir,
                        rscript=args.rscript, r_home=args.r_home, r_lib=args.r_lib)
    else:
        if args.output_root is None or args.workbook is None or args.pdf is None:
            parser.error("--output-root, --workbook and --pdf are required for acceptance")
        result = accept(args.output_root, args.audit_dir, source_root=args.source_root,
                        workbook=args.workbook, pdf=args.pdf, rscript=args.rscript,
                        r_home=args.r_home, r_lib=args.r_lib,
                        generate_golden=args.generate_golden)
    print(json.dumps({"status": result["status"], "reason": result.get("reason"),
                      "current": str(args.audit_dir / "current.json")}), flush=True)
    return 0 if result["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
