"""Versioned full-frame ENOE metric vectors and aggregate-only coverage."""

from __future__ import annotations

import hashlib
import json
import math
from collections import Counter
from collections.abc import Mapping

import numpy as np

from .enoe_adapter import Frame
from .populations import (
    COMPLETED_PROFESSIONAL_KNOWN_AGE,
    NATIONAL_15_PLUS_CONTEXT,
    POPULATION_DEFINITIONS,
    normalize_cmpe_key,
)
from .resources import _resource


def load_metric_manifest() -> dict:
    """Return canonical definitions with a content digest for method identity."""
    path = _resource("catalog", "data/catalog", "enoe-metrics.json")
    document = json.loads(path.read_text(encoding="utf-8"))
    declared = document.pop("content_sha256", None)
    canonical = json.dumps(document, sort_keys=True, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
    digest = hashlib.sha256(canonical).hexdigest()
    if declared is not None and declared != digest:
        raise ValueError("ENOE metric manifest content SHA-256 mismatch")
    if document.get("source_id") != "inegi_enoe" or not document.get("version"):
        raise ValueError("ENOE metric manifest identity is invalid")
    metrics = document.get("metrics")
    if not isinstance(metrics, list) or len({m["id"] for m in metrics}) != len(metrics):
        raise ValueError("ENOE metric definitions missing or duplicated")
    for item in metrics:
        if not {"id", "operation", "numerator", "denominator", "unit", "price_basis", "valid_categories", "sentinels", "dictionary_refs"} <= item.keys():
            raise ValueError("ENOE metric definition is incomplete")
    document["content_sha256"] = digest
    document["method_version"] = f"{document['version']}:{digest}"
    return document


def _domain(frame: Frame, population_id: str, selector: Mapping) -> np.ndarray:
    if population_id not in POPULATION_DEFINITIONS:
        raise ValueError("unknown ENOE population")
    if not isinstance(selector, Mapping):
        raise TypeError("domain selector must be a mapping")
    extra = set(selector) - {"field_of_study", "sex", "entity", "geography", "all_fields"}
    if extra:
        raise ValueError("unsupported ENOE domain selector")
    age = frame.eda
    mask = (age >= 15) & (age <= (98 if population_id == NATIONAL_15_PLUS_CONTEXT else 97))
    if population_id == COMPLETED_PROFESSIONAL_KNOWN_AGE:
        mask &= (frame.cs_p13_1 == 7) & (frame.cs_p16 == 1)
    if selector.get("all_fields") not in (None, True):
        raise ValueError("all_fields only accepts true")
    field = selector.get("field_of_study")
    if field is not None:
        key = normalize_cmpe_key(field, frame.cmpe_catalog_keys)
        if key is None:
            raise ValueError("field_of_study is absent from quarter catalog")
        mask &= frame.cs_p14_c == key
    sex = selector.get("sex")
    if sex is not None:
        if isinstance(sex, str) and sex.strip(" ") in ("1", "2"):
            sex = int(sex.strip(" "))
        if type(sex) is not int or sex not in (1, 2):
            raise ValueError("sex selector requires official recorded code 1 or 2")
        mask &= frame.sex == sex
    entity = selector.get("entity", selector.get("geography"))
    if entity is not None:
        if isinstance(entity, str) and entity.strip(" ").isascii() and entity.strip(" ").isdigit():
            entity = int(entity.strip(" "))
        if type(entity) is not int or not 1 <= entity <= 32:
            raise ValueError("entity selector must be an official 01..32 code")
        mask &= frame.columns[frame.inventory["geography_header"].lower()] == entity
    return mask


def _states(frame: Frame, domain: np.ndarray) -> dict[str, np.ndarray | dict]:
    occupied = frame.clase2 == 1
    pea = frame.clase1 == 1
    unemployed = pea & (frame.clase2 == 2)
    known_clase1 = np.isin(frame.clase1, [1, 2])
    known_clase2 = np.isin(frame.clase2, [1, 2, 3, 4])
    known_pea_status = pea & np.isin(frame.clase2, [1, 2])
    band = frame.ing7c
    amount = frame.ingocup
    positive_amount = (amount >= 1) & (amount <= 999998)
    positive_income = occupied & np.isin(band, [1, 2, 3, 4, 5]) & positive_amount
    conflicting = occupied & np.isin(band, [0, 6, 7]) & positive_amount
    no_income = occupied & (band == 6) & ~positive_amount
    unspecified_income = occupied & (band == 7) & ~positive_amount
    consistent_income = positive_income | no_income | unspecified_income
    hour = frame.hrsocup
    duration = frame.dur9c
    known_hours = occupied & (((hour >= 1) & (hour <= 168) & (duration >= 2) & (duration <= 8)) | ((hour == 0) & (duration == 1)))
    relevant = domain & occupied
    exclusions = Counter({
        "unknown_clase1": int(np.count_nonzero(domain & ~np.isin(frame.clase1, [1, 2]))),
        "unknown_clase2": int(np.count_nonzero(domain & ~np.isin(frame.clase2, [1, 2, 3, 4]))),
        "income_conflicting": int(np.count_nonzero(relevant & conflicting)),
        "income_amount_unknown": int(np.count_nonzero(relevant & np.isin(band, [1, 2, 3, 4, 5]) & ~positive_amount)),
        "no_income": int(np.count_nonzero(relevant & no_income)),
        "income_unspecified": int(np.count_nonzero(relevant & unspecified_income)),
        "hours_unknown": int(np.count_nonzero(relevant & ~known_hours)),
        "hours_dur9c_9_zero": int(np.count_nonzero(relevant & (hour == 0) & (duration == 9))),
        "unknown_emp_ppal": int(np.count_nonzero(relevant & ~np.isin(frame.emp_ppal, [1, 2]))),
        "unknown_pos_ocu": int(np.count_nonzero(relevant & ~np.isin(frame.pos_ocu, [1, 2, 3, 4]))),
        "unknown_sex": int(np.count_nonzero(relevant & ~np.isin(frame.sex, [1, 2]))),
        "unknown_field": int(np.count_nonzero(domain & np.equal(frame.cs_p14_c, None))),
        "unknown_age_98": int(np.count_nonzero(domain & (frame.eda == 98))),
    })
    return locals() | {"exclusions": {k: v for k, v in sorted(exclusions.items()) if v}}


def metric_vectors(frame: Frame, population_id: str, domain: dict, metric_id: str) -> dict:
    """Build full-length aligned vectors without dropping zero-domain clusters."""
    if not isinstance(frame, Frame):
        raise TypeError("metric_vectors requires a verified Frame")
    manifest = load_metric_manifest()
    definitions = {item["id"]: item for item in manifest["metrics"]}
    if metric_id not in definitions:
        raise ValueError("unknown ENOE metric")
    if frame.period not in manifest["dictionary_refs"]:
        raise ValueError("quarter lacks metric dictionary reference")
    d = _domain(frame, population_id, domain)
    state = _states(frame, d)
    o = state["occupied"]
    pea = state["pea"]
    unemployed = state["unemployed"]
    positive = state["positive_income"]
    no_income = state["no_income"]
    unspecified = state["unspecified_income"]
    consistent = state["consistent_income"]
    known_hours = state["known_hours"]
    zero = np.zeros(len(frame), dtype=np.float64)
    specs: dict[str, tuple[np.ndarray, np.ndarray]] = {
        "population_total": (d, zero),
        "occupied_total": (d & o, zero),
        "pea_total": (d & pea, zero),
        "unemployed_total": (d & unemployed, zero),
        "employment_rate": (d & o, d & state["known_clase2"]),
        "participation_rate": (d & pea, d & state["known_clase1"]),
        "unemployment_rate": (d & unemployed, d & state["known_pea_status"]),
        "positive_income_mean": (np.where(d & positive, frame.ingocup, 0), d & positive),
        "positive_income_coverage": (d & positive, d & o),
        "no_income_count": (d & no_income, zero),
        "no_income_share": (d & no_income, d & consistent),
        "unspecified_income_count": (d & unspecified, zero),
        "unspecified_income_share": (d & unspecified, d & consistent),
        "main_job_informality_rate": (d & o & (frame.emp_ppal == 1), d & o & np.isin(frame.emp_ppal, [1, 2])),
        "women_occupied_share": (d & o & (frame.sex == 2), d & o & np.isin(frame.sex, [1, 2])),
        "suboccupied_count": (d & o & (frame.sub_o == 1), zero),
        "suboccupied_rate": (d & o & (frame.sub_o == 1), d & o),
        "known_hours_mean": (np.where(d & known_hours, frame.hrsocup, 0), d & known_hours),
        "known_hours_coverage": (d & known_hours, d & o),
    }
    for code in (1, 2, 3, 4):
        specs[f"position_{code}_share"] = (d & o & (frame.pos_ocu == code), d & o & np.isin(frame.pos_ocu, [1, 2, 3, 4]))
    if metric_id not in specs:
        raise ValueError("metric definition has no vector implementation")
    numerator, denominator = specs[metric_id]
    numerator = np.asarray(numerator, dtype=np.float64)
    denominator = np.asarray(denominator, dtype=np.float64)
    if not np.all(np.isfinite(numerator)) or not np.all(np.isfinite(denominator)):
        raise ValueError("metric vector is nonfinite")
    eligible_n = int(np.count_nonzero(denominator if definitions[metric_id]["operation"] != "total" else numerator))
    if definitions[metric_id]["operation"] == "total":
        weighted_denominator = None
    elif eligible_n == 0:
        weighted_denominator = None
    else:
        weighted_denominator = float(np.sum(frame.weight * denominator, dtype=np.float64))
        if not math.isfinite(weighted_denominator):
            raise ValueError("metric weighted denominator is nonfinite")
    coverage = {
        "domain_n": int(np.count_nonzero(d)),
        "eligible_n": eligible_n,
        "weighted_denominator": weighted_denominator,
        "reason": "empty_denominator" if definitions[metric_id]["operation"] != "total" and eligible_n == 0 else None,
    }
    return {
        "numerator": numerator, "denominator": denominator, "domain": d,
        "coverage": coverage, "exclusions": state["exclusions"],
        "method_version": manifest["method_version"],
    }
