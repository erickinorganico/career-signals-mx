"""Versioned full-frame ENOE metric vectors and aggregate-only coverage."""

from __future__ import annotations

import hashlib
import json
import math
from copy import deepcopy
from collections import Counter
from collections.abc import Mapping
from functools import lru_cache

import numpy as np

from .enoe_adapter import Frame
from .populations import (
    COMPLETED_PROFESSIONAL_KNOWN_AGE,
    NATIONAL_15_PLUS_CONTEXT,
    POPULATION_DEFINITIONS,
    normalize_cmpe_key,
)
from .resources import _resource


@lru_cache(maxsize=1)
def _metric_manifest_cached() -> dict:
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


def load_metric_manifest() -> dict:
    """Return a defensive copy; callers cannot mutate cached method identity."""
    return deepcopy(_metric_manifest_cached())


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


def _base_states(frame: Frame) -> dict[str, np.ndarray]:
    cached = frame.metric_cache.get("base")
    if cached is not None:
        return cached
    occupied = frame.clase2 == 1
    pea = frame.clase1 == 1
    unemployed = pea & (frame.clase2 == 2)
    known_clase1 = np.isin(frame.clase1, [1, 2])
    known_clase2 = np.isin(frame.clase2, [1, 2, 3, 4])
    known_pea_status = pea & np.isin(frame.clase2, [1, 2])
    known_suboccupation = occupied & np.isin(frame.sub_o, [0, 1])
    band = frame.ing7c
    amount = frame.ingocup
    positive_amount = (amount >= 1) & (amount <= 999998)
    positive_income = occupied & np.isin(band, [1, 2, 3, 4, 5]) & positive_amount
    conflicting = occupied & np.isin(band, [0, 6, 7]) & positive_amount
    no_income = occupied & (band == 6) & ~positive_amount
    unspecified_income = occupied & (band == 7) & ~positive_amount
    # A known ING7C band remains usable for state shares even when its exact
    # amount is unavailable; only a contradictory 6/7 band with positive
    # amount is excluded. The positive-amount mean keeps its narrower mask.
    consistent_income = occupied & (band >= 1) & (band <= 7) & ~conflicting
    hour = frame.hrsocup
    duration = frame.dur9c
    known_hours = occupied & (((hour >= 1) & (hour <= 168) & (duration >= 2) & (duration <= 8)) | ((hour == 0) & (duration == 1)))
    base = {key: value for key, value in locals().items() if isinstance(value, np.ndarray) and value.dtype == np.bool}
    frame.metric_cache["base"] = base
    return base


def _states(frame: Frame, domain: np.ndarray) -> dict[str, np.ndarray | dict]:
    base = _base_states(frame)
    occupied = base["occupied"]
    conflicting = base["conflicting"]
    positive_amount = base["positive_amount"]
    no_income = base["no_income"]
    unspecified_income = base["unspecified_income"]
    known_hours = base["known_hours"]
    band = frame.ing7c
    hour = frame.hrsocup
    duration = frame.dur9c
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
        "unknown_sub_o": int(np.count_nonzero(relevant & ~np.isin(frame.sub_o, [0, 1]))),
        "unknown_field": int(np.count_nonzero(domain & np.equal(frame.cs_p14_c, None))),
        "unknown_age_98": int(np.count_nonzero(domain & (frame.eda == 98))),
    })
    return base | {"exclusions": {k: v for k, v in sorted(exclusions.items()) if v}}


def metric_vectors(frame: Frame, population_id: str, domain: dict, metric_id: str) -> dict:
    """Build full-length aligned vectors without dropping zero-domain clusters."""
    if not isinstance(frame, Frame):
        raise TypeError("metric_vectors requires a verified Frame")
    if type(frame.synthetic) is not bool:
        raise ValueError("frame provenance is unclassified")
    manifest = _metric_manifest_cached()
    definitions = {item["id"]: item for item in manifest["metrics"]}
    if metric_id not in definitions:
        raise ValueError("unknown ENOE metric")
    expected_dictionary = manifest["dictionary_refs"].get(frame.period)
    if expected_dictionary is None:
        raise ValueError("quarter lacks metric dictionary reference")
    actual_dictionary = frame.inventory.get("dictionary_member", {}).get("sha256")
    if not isinstance(actual_dictionary, str) or len(actual_dictionary) != 64:
        raise ValueError("frame dictionary digest is invalid")
    if not frame.synthetic and actual_dictionary != expected_dictionary:
        raise ValueError("frame dictionary SHA-256 does not match official quarter definition")
    dictionary_binding = "synthetic_fixture" if frame.synthetic else "official_verified"
    selector_key = (population_id, tuple(sorted(domain.items())))
    cached = frame.metric_cache.get("domain_state")
    if cached is not None and cached[0] == selector_key:
        d, state = cached[1], cached[2]
    else:
        d = _domain(frame, population_id, domain)
        state = _states(frame, d)
        # Only the latest domain is kept: bounded memory across hundreds of
        # entity/field/sex cells, with per-frame base masks reused throughout.
        frame.metric_cache["domain_state"] = (selector_key, d, state)
    o = state["occupied"]
    pea = state["pea"]
    unemployed = state["unemployed"]
    positive = state["positive_income"]
    no_income = state["no_income"]
    unspecified = state["unspecified_income"]
    consistent = state["consistent_income"]
    known_hours = state["known_hours"]
    if metric_id == "population_total":
        numerator, denominator = d, None
    elif metric_id == "occupied_total":
        numerator, denominator = d & o, None
    elif metric_id == "pea_total":
        numerator, denominator = d & pea, None
    elif metric_id == "unemployed_total":
        numerator, denominator = d & unemployed, None
    elif metric_id == "employment_rate":
        numerator, denominator = d & o, d & state["known_clase2"]
    elif metric_id == "participation_rate":
        numerator, denominator = d & pea, d & state["known_clase1"]
    elif metric_id == "unemployment_rate":
        numerator, denominator = d & unemployed, d & state["known_pea_status"]
    elif metric_id == "positive_income_mean":
        numerator, denominator = np.where(d & positive, frame.ingocup, 0), d & positive
    elif metric_id == "positive_income_coverage":
        numerator, denominator = d & positive, d & o
    elif metric_id == "no_income_count":
        numerator, denominator = d & no_income, None
    elif metric_id == "no_income_share":
        numerator, denominator = d & no_income, d & consistent
    elif metric_id == "unspecified_income_count":
        numerator, denominator = d & unspecified, None
    elif metric_id == "unspecified_income_share":
        numerator, denominator = d & unspecified, d & consistent
    elif metric_id == "main_job_informality_rate":
        numerator, denominator = d & o & (frame.emp_ppal == 1), d & o & np.isin(frame.emp_ppal, [1, 2])
    elif metric_id == "women_occupied_share":
        numerator, denominator = d & o & (frame.sex == 2), d & o & np.isin(frame.sex, [1, 2])
    elif metric_id.startswith("position_") and metric_id.endswith("_share"):
        code = int(metric_id.split("_")[1])
        numerator, denominator = d & o & (frame.pos_ocu == code), d & o & np.isin(frame.pos_ocu, [1, 2, 3, 4])
    elif metric_id == "suboccupied_count":
        numerator, denominator = d & o & (frame.sub_o == 1), None
    elif metric_id == "suboccupied_rate":
        numerator, denominator = d & o & (frame.sub_o == 1), d & state["known_suboccupation"]
    elif metric_id == "known_hours_mean":
        numerator, denominator = np.where(d & known_hours, frame.hrsocup, 0), d & known_hours
    elif metric_id == "known_hours_coverage":
        numerator, denominator = d & known_hours, d & o
    else:
        raise ValueError("metric definition has no vector implementation")
    numerator = np.asarray(numerator, dtype=np.float64)
    denominator = np.zeros(len(frame), dtype=np.float64) if denominator is None else np.asarray(denominator, dtype=np.float64)
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
        "numerator": numerator, "denominator": denominator, "domain": d.copy(),
        "coverage": coverage, "exclusions": state["exclusions"],
        "method_version": manifest["method_version"] if not frame.synthetic else f"{manifest['method_version']}:synthetic:{actual_dictionary}",
        "synthetic": frame.synthetic, "dictionary_binding": dictionary_binding,
    }
