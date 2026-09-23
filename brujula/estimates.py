"""Complete-frame ENOE estimates and the strict research-v2 public boundary.

The returned audit and payloads contain aggregates only. Individual columns
remain inside the verified Frame and never enter a serialized result.
"""

from __future__ import annotations

import hashlib
from datetime import date
from pathlib import Path

import numpy as np

from . import enoe_adapter
from .enoe_adapter import load_snapshot_frame
from .metrics import load_metric_manifest, metric_vectors
from .populations import COMPLETED_PROFESSIONAL_KNOWN_AGE, NATIONAL_15_PLUS_CONTEXT
from .research_contract import GRAIN, public_research_projection, validate_public_research_v2, validate_research_v2
from .source_inventory import FOCUS_CODES, PERIODS
from .survey import SurveyDesign, VARIANCE_METHOD


METHOD_ID = "enoe_taylor_project_adjust"
DESIGN_ID = "enoe_fac_tri_est_d_tri_upm_full_frame"
FOCAL_FIELDS = tuple(sorted(code.zfill(6) for code in FOCUS_CODES))


def _quarter(snapshot_id: str) -> str:
    for period in PERIODS:
        if snapshot_id == "enoe_" + period.lower().replace("-", "_"):
            return period
    raise ValueError("snapshot_id is not an approved ENOE quarter")


def _cell(population: str, field: str = "all", geography: str = "mx", sex: str = "all") -> dict:
    return {"population_id": population, "field_of_study_id": field,
            "geography_id": geography, "recorded_sex_id": sex}


def required_estimation_domains(snapshot_id: str, *, latest_snapshot_id: str,
                                field_ids: list[str]) -> list[dict]:
    """Build the declared quarter inventory; the caller verifies fields on load."""
    _quarter(snapshot_id)
    _quarter(latest_snapshot_id)
    if not isinstance(field_ids, list) or len(field_ids) != len(set(field_ids)):
        raise ValueError("field_ids must be unique verified catalog keys")
    if any(not isinstance(code, str) or len(code) != 6 or not code.isascii() or not code.isdigit()
           or code == "999999" for code in field_ids):
        raise ValueError("field_ids must be six-digit catalog keys")
    domains = [_cell(NATIONAL_15_PLUS_CONTEXT), _cell(COMPLETED_PROFESSIONAL_KNOWN_AGE)]
    domains.extend(_cell(COMPLETED_PROFESSIONAL_KNOWN_AGE, code) for code in FOCAL_FIELDS)
    if snapshot_id == latest_snapshot_id:
        # All-fields cohort and each named field are deliberately distinct.
        domains.extend(_cell(COMPLETED_PROFESSIONAL_KNOWN_AGE, code) for code in sorted(field_ids))
        for field in ("all", *FOCAL_FIELDS):
            domains.extend(_cell(COMPLETED_PROFESSIONAL_KNOWN_AGE, field, f"{entity:02d}")
                           for entity in range(1, 33))
            domains.extend(_cell(COMPLETED_PROFESSIONAL_KNOWN_AGE, field, "mx", str(sex))
                           for sex in (1, 2))
    unique = {tuple(item[key] for key in ("population_id", "field_of_study_id", "geography_id", "recorded_sex_id")): item
              for item in domains}
    return sorted(unique.values(), key=lambda item: tuple(item[key] for key in
                  ("population_id", "field_of_study_id", "geography_id", "recorded_sex_id")))


def _verified_fields(frame) -> list[str]:
    cohort = (frame.eda >= 15) & (frame.eda <= 97) & (frame.cs_p13_1 == 7) & (frame.cs_p16 == 1)
    seen = set(frame.cs_p14_c[cohort]) - {None}
    if not seen <= frame.cmpe_catalog_keys:
        raise ValueError("observed professional field absent from verified quarter catalog")
    return sorted(seen)


def _domain_selector(domain: dict, verified_fields: set[str]) -> tuple[str, dict]:
    if not isinstance(domain, dict) or set(domain) != {
        "population_id", "field_of_study_id", "geography_id", "recorded_sex_id"
    }:
        raise ValueError("domain must provide exact population, field, geography and recorded sex")
    population = domain["population_id"]
    if population not in {NATIONAL_15_PLUS_CONTEXT, COMPLETED_PROFESSIONAL_KNOWN_AGE}:
        raise ValueError("unrecognized population")
    field, geography, sex = (domain[key] for key in ("field_of_study_id", "geography_id", "recorded_sex_id"))
    if field != "all" and field not in verified_fields:
        raise ValueError("field is absent from verified observed quarter catalog")
    if geography != "mx" and geography not in {f"{i:02d}" for i in range(1, 33)}:
        raise ValueError("geography must be national or an official entity code")
    if sex not in {"all", "1", "2"}:
        raise ValueError("recorded sex must be all, 1 or 2")
    if population == NATIONAL_15_PLUS_CONTEXT and field != "all":
        raise ValueError("context population cannot claim a professional field")
    selector = {}
    if field != "all":
        selector["field_of_study"] = field
    if geography != "mx":
        selector["entity"] = geography
    if sex != "all":
        selector["sex"] = sex
    return population, selector


def _period_record(period: str) -> dict:
    year, quarter = period.split("-Q")
    month = (int(quarter) - 1) * 3 + 1
    end_month = month + 2
    end_day = (date(int(year) + (end_month == 12), end_month % 12 + 1, 1) - date.resolution).day
    return {"id": period, "label": period, "start": f"{year}-{month:02d}-01",
            "end": f"{year}-{end_month:02d}-{end_day:02d}"}


def _method_version(manifest: dict) -> str:
    # Git checkouts may use CRLF on Windows and LF on Unix. Hash canonical
    # source text so identical algorithms share one replay identity.
    adapter_source = Path(enoe_adapter.__file__).read_bytes().replace(b"\r\n", b"\n")
    adapter_hash = hashlib.sha256(adapter_source).hexdigest()
    return f"{VARIANCE_METHOD}:adapter:{adapter_hash}:metrics:{manifest['content_sha256']}"


def _record(frame, domain: dict, metric: dict, vectors: dict, design: SurveyDesign,
            method_version: str, evidence_id: str, *, synthetic: bool) -> dict:
    operation = metric["operation"]
    numerator, denominator = vectors["numerator"], vectors["denominator"]
    if operation == "total":
        result = design.total(numerator, vectors["domain"])
        support_mask = vectors["domain"] & (numerator != 0) & (design.weights > 0)
    else:
        result = design.ratio(numerator, denominator, vectors["domain"],
                              percent=metric["unit"] == "percent")
        support_mask = vectors["domain"] & (denominator > 0) & (design.weights > 0)
    weighted_support = float(np.sum(design.weights[support_mask], dtype=np.float64))
    weighted_denominator = result["weighted_denominator"]
    if operation == "total":
        # A total's denominator is the weighted population eligible for this
        # request; numerator support is a subset and may be zero.
        weighted_denominator = float(np.sum(design.weights[vectors["domain"]], dtype=np.float64))
    if not np.isfinite(weighted_support) or not np.isfinite(weighted_denominator):
        raise ValueError("nonfinite weighted support")
    status = result["status"]
    value = result["value"]
    if synthetic and value is not None:
        status = "REVIEW"
    reason = result["suppression_reason"]
    if value is not None and status == "REVIEW":
        reason = "Synthetic fixture" if synthetic else "Project singleton adjustment" if design.singleton_policy == "adjust" else "precision"
    elif value is None and reason is None:
        reason = "unsupported"
    return {
        "source_snapshot_id": frame.snapshot_id, "population_id": domain["population_id"],
        "field_of_study_id": domain["field_of_study_id"], "occupation_id": "all",
        "industry_id": "all", "geography_id": domain["geography_id"],
        "recorded_sex_id": domain["recorded_sex_id"], "period_id": frame.period,
        "metric_id": metric["id"], "method_id": METHOD_ID, "unit": metric["unit"],
        "price_basis": metric["price_basis"], "method_version": method_version,
        "design_id": DESIGN_ID, "sample_size": result["sample_size"],
        "weighted_denominator": weighted_denominator,
        "support": {"n_psu_design": result["n_psu_design"], "n_strata_design": result["n_strata_design"],
                    "n_psu_domain": result["n_psu_domain"], "n_strata_domain": result["n_strata_domain"],
                    "design_df": result["design_df"], "weighted_support_total": weighted_support},
        "precision": {"standard_error": result["standard_error"],
                      "coefficient_variation": result["coefficient_variation"],
                      "ci90_lower": result["ci_lower"], "ci90_upper": result["ci_upper"],
                      "method": result["variance_method"], "ci_method": result["ci_method"],
                      "level": result["confidence_level"], "singleton_policy": result["singleton_policy"],
                      "official_precision": False},
        "status": status, "reason": reason, "estimate": result["estimate"],
        "value": value, "evidence_refs": [evidence_id], "synthetic": synthetic,
    }


def estimate_snapshot(snapshot_id: str, output_root: Path, *, domains: list[dict] | None = None,
                      registry_path: Path | None = None) -> dict:
    """Evaluate every metric/request once and return internal, public and audit."""
    _quarter(snapshot_id)
    frame, frame_audit = load_snapshot_frame(snapshot_id, Path(output_root), registry_path)
    if frame.snapshot_id != snapshot_id or frame.period != _quarter(snapshot_id):
        raise ValueError("loaded frame identity differs from requested snapshot")
    verified_fields = _verified_fields(frame)
    if domains is None:
        domains = required_estimation_domains(snapshot_id, latest_snapshot_id="enoe_2026_q2",
                                              field_ids=verified_fields)
    if not isinstance(domains, list) or not domains:
        raise ValueError("estimate request inventory cannot be empty")
    parsed = [(domain, *_domain_selector(domain, set(frame.cmpe_catalog_keys))) for domain in domains]
    keys = [tuple(domain[key] for key in ("population_id", "field_of_study_id", "geography_id", "recorded_sex_id"))
            for domain, _, _ in parsed]
    if len(keys) != len(set(keys)):
        raise ValueError("duplicate estimation domain")
    design = SurveyDesign(frame.weight, frame.est_d_tri, frame.upm, singleton_policy="adjust")
    manifest = load_metric_manifest()
    method_version = _method_version(manifest)
    evidence_id = f"{snapshot_id}_custody"
    if type(frame_audit.get("synthetic")) is not bool or type(frame.synthetic) is not bool:
        raise ValueError("verified frame audit must declare synthetic provenance")
    if frame_audit["synthetic"] != frame.synthetic or frame_audit.get("provenance") != frame.provenance:
        raise ValueError("frame and audit synthetic provenance disagree")
    synthetic = frame_audit["synthetic"]
    records = []
    requested = {}
    evaluated = {}
    for domain, population, selector in sorted(parsed, key=lambda item: tuple(item[0][key] for key in
                                               ("population_id", "field_of_study_id", "geography_id", "recorded_sex_id"))):
        for metric in sorted(manifest["metrics"], key=lambda item: item["id"]):
            grain = (snapshot_id, domain["population_id"], domain["field_of_study_id"], "all", "all",
                     domain["geography_id"], domain["recorded_sex_id"], frame.period, metric["id"], METHOD_ID)
            ledger_key = "|".join(grain)
            requested[ledger_key] = True
            vectors = metric_vectors(frame, population, selector, metric["id"])
            record = _record(frame, domain, metric, vectors, design, method_version, evidence_id,
                             synthetic=synthetic)
            if tuple(record[name] for name in GRAIN) != grain:
                raise ValueError("evaluated record grain differs from request")
            evaluated[ledger_key] = {"status": record["status"], "has_estimate": record["estimate"] is not None,
                                     "reason": record["reason"]}
            records.append(record)
    if requested.keys() != evaluated.keys() or len(records) != len(requested):
        raise ValueError("estimation inventory has unevaluated cells")
    records.sort(key=lambda row: tuple(row[key] for key in GRAIN))
    fields = sorted({row["field_of_study_id"] for row in records})
    geographies = sorted({row["geography_id"] for row in records})
    sexes = sorted({row["recorded_sex_id"] for row in records})
    inventory = frame.inventory
    internal = {
        "schema_version": "2.0",
        "sources": [{"id": snapshot_id, "period_id": frame.period, "url": inventory["source_url"],
                     "sha256": inventory["raw_sha256"], "terms_url": inventory["terms_url"],
                     "authority": inventory["authority"], "acquired_at": inventory["acquired_at"]}],
        "populations": [{"id": name} for name in sorted({row["population_id"] for row in records})],
        "fields_of_study": [{"id": name, "label": frame.cmpe_catalog_labels[name] if name != "all" else "Todos los campos"}
                            for name in fields],
        "occupations": [{"id": "all", "label": "All occupations"}],
        "industries": [{"id": "all", "label": "All industries"}],
        "geographies": [{"id": name, "label": "Mexico" if name == "mx" else f"Entity {name}"}
                        for name in geographies],
        "recorded_sexes": [{"id": name, "label": "All recorded sexes" if name == "all" else f"Recorded sex {name}"}
                           for name in sexes],
        "periods": [_period_record(frame.period)],
        "metrics": [{"id": metric["id"], "label": metric["id"], "unit": metric["unit"],
                     "price_basis": metric["price_basis"]} for metric in manifest["metrics"]],
        "methods": [{"id": METHOD_ID, "design_id": DESIGN_ID, "version": method_version,
                     "source_snapshot_ids": [snapshot_id]}],
        "evidence": [{"id": evidence_id, "source_snapshot_id": snapshot_id, "label": "Verified ENOE source custody",
                      "url": inventory["source_url"], "kind": "source_receipt"}],
        "records": records,
    }
    failures = validate_research_v2(internal)
    if failures:
        raise ValueError(f"invalid internal research v2: {failures[:5]}")
    public = public_research_projection(internal)
    failures = validate_public_research_v2(public)
    if failures:
        raise ValueError(f"invalid public research v2: {failures[:5]}")
    audit = {"snapshot_id": snapshot_id, "period": frame.period, "raw_sha256": inventory["raw_sha256"],
             "synthetic": synthetic, "provenance": frame.provenance,
             "design": {"n_psu_design": design.n_psu_design, "n_strata_design": design.n_strata_design,
                        "design_df": design.design_df, "singleton_strata": design.singleton_strata_count},
             "requested_cells": requested, "evaluated_cells": evaluated,
             "requested_count": len(requested), "evaluated_count": len(evaluated)}
    return {"internal": internal, "public": public, "audit": audit}
