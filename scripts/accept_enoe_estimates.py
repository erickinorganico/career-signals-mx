"""Offline eight-quarter numerical acceptance; writes aggregate ledgers only.

An intentional public baseline change requires an evidence-reviewed manual
update of the aggregate golden fixture from verified public payloads. The
--generate-golden option only initializes internal diagnostic hashes and
cannot replace the pinned public, source, oracle, or official evidence.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import os
import platform
import subprocess
import sys
import time
import uuid
from copy import deepcopy
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import patch

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from brujula import estimates
from brujula.enoe_adapter import load_snapshot_frame
from brujula.metrics import load_metric_manifest
from brujula.populations import COMPLETED_PROFESSIONAL_KNOWN_AGE, NATIONAL_15_PLUS_CONTEXT
from brujula.research_contract import GRAIN, validate_public_research_v2, validate_research_v2
from brujula.source_inventory import FOCUS_CODES, inventory_all
from brujula.survey import SurveyDesign

RTOL = 1e-10
ATOL = 1e-8
LATEST = "enoe_2026_q2"
GOLDEN = ROOT / "data/fixtures/enoe-aggregate-golden.json"
R_SCRIPT = ROOT / "scripts/enoe_survey_oracle.R"


def _digest(value: object) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"),
                                     ensure_ascii=False, allow_nan=False).encode("utf-8")).hexdigest()


def _canonical_research_content(document: dict) -> dict:
    """Keep all research content except the adapter-source method version."""
    content = deepcopy(document)
    for row in content["records"]:
        row.pop("method_version", None)
    for method in content["methods"]:
        method.pop("version", None)  # root catalog copy of method_version
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
    """Add internal hashes only; every approved public/official pin stays fixed."""
    without_internal = lambda value: {key: item for key, item in value.items()
                                      if key != "internal_content_sha256_by_snapshot"}
    if without_internal(prior) != without_internal(candidate):
        raise ValueError("golden initialization would change approved public or official evidence")
    return {**prior, "internal_content_sha256_by_snapshot": candidate["internal_content_sha256_by_snapshot"]}


def _code_hashes() -> dict[str, str]:
    names = ("scripts/accept_enoe_estimates.py", "scripts/enoe_survey_oracle.R",
             "scripts/official_reconciliation.py", "brujula/acquisition.py",
             "brujula/source_inventory.py", "brujula/enoe_adapter.py", "brujula/populations.py",
             "brujula/metrics.py", "brujula/survey.py", "brujula/estimates.py",
             "brujula/research_contract.py")
    return {name: hashlib.sha256((ROOT / name).read_bytes().replace(b"\r\n", b"\n")).hexdigest()
            for name in names}


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


def run_attempt(audit_dir: Path, operation) -> dict:
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
    result = {**result, "attempt_id": attempt_id}
    receipt = {"attempt_id": attempt_id, "started_at": started_at,
               "completed_at": datetime.now(timezone.utc).isoformat(),
               "status": result["status"], "reason": result.get("reason"),
               "numeric_content_digest": result.get("numeric_content_digest")}
    receipts = audit_dir / "attempts"
    receipts.mkdir(parents=True, exist_ok=True)
    with (receipts / f"{attempt_id}.json").open("x", encoding="utf-8") as stream:
        json.dump(receipt, stream, indent=2, sort_keys=True)
        stream.write("\n")
    write_attempt(audit_dir, result)
    return result


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


def _run_oracle(frame, records: list[dict], audit_dir: Path) -> dict:
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
        oracle = _execute_r(frame_path, cases_path, ledger_path)
    finally:
        frame_path.unlink(missing_ok=True)
    comparison = compare_oracle_cases(expected, oracle["cases"])
    comparison.update({"r_version": oracle["r_version"], "survey_version": oracle["survey_version"],
                       "design_df": oracle["design_df"], "singleton_policy": oracle["singleton_policy"],
                       "source_sha256": frame.inventory["raw_sha256"], "case_ids": sorted(x["id"] for x in specs)})
    return comparison


def _execute_r(frame_path: Path, cases_path: Path, ledger_path: Path) -> dict:
    local_rscript = ROOT / ".cache/R-4.6.1/bin/Rscript.exe"
    rscript = os.environ.get("BRUJULA_RSCRIPT") or (str(local_rscript) if local_rscript.is_file() else "Rscript")
    process = subprocess.run([rscript, str(R_SCRIPT), "--frame", str(frame_path),
                              "--cases", str(cases_path), "--output", str(ledger_path)],
                             cwd=ROOT, capture_output=True, text=True, timeout=900,
                             env={**os.environ, "BRUJULA_R_LIB": os.environ.get(
                                 "BRUJULA_R_LIB", str(ROOT / ".cache/R-library"))})
    if process.returncode:
        raise ValueError(f"R oracle exit {process.returncode}: {process.stderr[-1000:]}")
    return json.loads(ledger_path.read_text(encoding="utf-8"))


def _run_analytic_oracle(audit_dir: Path) -> dict:
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
        oracle = _execute_r(frame_path, cases_path, output_path)
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


def _prior_semantic_baseline() -> dict:
    """Seed only from the prior independent aggregate audit; never row data."""
    path = ROOT / ".cache/research/eight-quarter-audit.json"
    prior = json.loads(path.read_text(encoding="utf-8"))
    if prior.get("status") != "PASS" or len(prior.get("snapshots", [])) != 8:
        raise ValueError("prior independent aggregate audit unavailable")
    fields = ("occupied_rows_clase2_eq_1", "pea_rows_clase1_eq_1", "sub_o_by_clase2",
              "hours_duration_joint_occupied", "principal_cohort", "n_psus", "n_strata",
              "singleton_strata")
    return {item["snapshot_id"]: {**{name: item["numeric"][name] for name in fields},
                                  "source_member_sha256": item["source_member_sha256"],
                                  "dictionary_sha256": item["dictionary_sha256"]}
            for item in prior["snapshots"]}


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


def accept(output_root: Path, audit_dir: Path, *, generate_golden: bool = False) -> dict:
    from scripts.official_reconciliation import (
        reconcile, check_2026_pdf_benchmark, COUNT_EXPECTED, RATE_EXPECTED,
        PDF_2026_Q2_SHA256,
    )
    started = time.monotonic()
    entry_code_hashes = _code_hashes()
    inventory = inventory_all(output_root)
    if len(inventory) != 8:
        raise ValueError("exactly eight pinned snapshots required")
    registry = json.loads((ROOT / "data/catalog/enoe-snapshots.json").read_text(encoding="utf-8"))
    ids = [item["id"] for item in registry["snapshots"]]
    if [item["snapshot_id"] for item in inventory] != ids:
        raise ValueError("approved catalog order or inventory mismatch")
    metric_manifest = load_metric_manifest()
    metrics = sorted(item["id"] for item in metric_manifest["metrics"])
    if len(metrics) != 23:
        raise ValueError("metric catalog is incomplete")
    analytic_oracle = _run_analytic_oracle(audit_dir)
    (audit_dir / "analytic-oracle-comparison.json").write_text(json.dumps(
        analytic_oracle, indent=2, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8")
    quarter_ledgers = {}
    oracle = official = pdf_benchmark = None
    golden_cases = {}
    prior_golden = json.loads(GOLDEN.read_text(encoding="utf-8"))
    semantic_baseline = prior_golden["semantic_baseline"]
    internal_digests = {}
    for item in inventory:
        snapshot = item["snapshot_id"]
        period = item["period"]
        mark = time.monotonic()
        frame, frame_audit = load_snapshot_frame(snapshot, output_root)
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
            result = estimates.estimate_snapshot(snapshot, output_root, domains=domains)
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
        ledger_path = audit_dir / f"{snapshot}-aggregate.json"
        public_path = audit_dir / f"{snapshot}-public-v2.json"
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
            official = reconcile(output_root, ROOT / ".cache/research/precision_2025q2.xlsx",
                                 result["internal"]["records"])
            (audit_dir / "official-aggregate.json").write_text(json.dumps(official, indent=2,
                    sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8")
            if official["status"] != "PASS":
                raise ValueError("official compatible count/rate reconciliation failed")
        if snapshot == LATEST:
            pdf_benchmark = check_2026_pdf_benchmark(ROOT / ".cache/research/enoe2026_08.pdf",
                                                     result["internal"]["records"])
            (audit_dir / "official-2026q2-pdf-aggregate.json").write_text(
                json.dumps(pdf_benchmark, indent=2, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8")
            if pdf_benchmark["status"] != "PASS":
                raise ValueError("2026-Q2 pinned official PDF national counts failed")
            oracle = _run_oracle(frame, result["internal"]["records"], audit_dir)
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
    initialized = initialize_internal_golden(prior_golden, golden) if generate_golden else None
    if not generate_golden and prior_golden != golden:
        raise ValueError("aggregate golden fixture differs from approved numeric content")
    claim_guard = quarter_claim_guard([{"snapshot_id": key, **value} for key, value in quarter_ledgers.items()])
    if _code_hashes() != entry_code_hashes:
        raise ValueError("acceptance code changed during run; results are exploratory only")
    if initialized is not None:
        GOLDEN.write_text(json.dumps(initialized, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    manifest = {"status": "PASS", "snapshots": quarter_ledgers,
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
    return manifest


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-root", type=Path, default=Path("artifacts/enoe"))
    parser.add_argument("--audit-dir", type=Path, default=Path(".cache/research/phase2-acceptance"))
    parser.add_argument("--generate-golden", action="store_true",
                        help="initialize internal hashes after all existing public and official pins match")
    args = parser.parse_args()
    args.audit_dir.mkdir(parents=True, exist_ok=True)
    result = run_attempt(args.audit_dir, lambda: accept(args.output_root, args.audit_dir,
                                                       generate_golden=args.generate_golden))
    print(json.dumps({"status": result["status"], "reason": result.get("reason"),
                      "current": str(args.audit_dir / "current.json")}), flush=True)
    return 0 if result["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
