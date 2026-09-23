"""Pure ENOE population and denominator rules for verified SDEM rows.

Callers must supply period-specific catalog keys separately.  These helpers do
not estimate survey variance or interpret study field as occupation/industry.
Only ASCII U+0020 padding is removed from CSV lexemes; Unicode lookalikes,
numeric casts, and inferred zero values are deliberately rejected.
"""

from __future__ import annotations

import math
import re
from collections import Counter
from collections.abc import Collection, Iterable, Mapping
from decimal import Decimal
from types import MappingProxyType


NATIONAL_15_PLUS_CONTEXT = "national_15_plus_context"
COMPLETED_PROFESSIONAL_KNOWN_AGE = "completed_professional_known_age"

POPULATION_DEFINITIONS = MappingProxyType({
    NATIONAL_15_PLUS_CONTEXT: MappingProxyType({
        "label": "National resident context, operational ages 15–98",
        "response": "R_DEF=00 (ASCII 0 and 00)",
        "residence": "C_RES in {1,3}",
        "age": "EDA 15–98 inclusive; 98 is unknown age, never stated 98 years",
        "education": None,
    }),
    COMPLETED_PROFESSIONAL_KNOWN_AGE: MappingProxyType({
        "label": "Resident people with completed professional studies and known age",
        "response": "R_DEF=00 (ASCII 0 and 00)",
        "residence": "C_RES in {1,3}",
        "age": "EDA 15–97 inclusive; 97 means 97 or more",
        "education": "CS_P13_1=07 professional, CS_P16=1 completed; excludes technical and postgraduate",
    }),
})


def _lexeme(value: object, width: int) -> str | None:
    if not isinstance(value, str):
        return None
    text = value.strip(" ")
    if not text or re.fullmatch(r"[0-9]{1," + str(width) + r"}", text) is None:
        return None
    return text.zfill(width)


def _blank(value: object) -> bool:
    return value is None or isinstance(value, str) and not value.strip(" ")


def _row_code(row: Mapping[str, object], name: str, width: int) -> str | None:
    return _lexeme(row.get(name), width)


def classify_eligibility(row: Mapping[str, object], population_id: str) -> dict:
    """Classify a single row; all reasons are retained in stable order.

    A missing study field remains an eligible person in the named professional
    cohort, but ``field_unknown`` prevents a named-field claim downstream.
    """
    if population_id not in POPULATION_DEFINITIONS:
        raise ValueError(f"unknown population_id: {population_id}")
    if not isinstance(row, Mapping):
        raise TypeError("row must be a mapping")
    reasons: list[str] = []
    response = _row_code(row, "r_def", 2)
    if response != "00":
        reasons.append("unknown_response" if _blank(row.get("r_def")) else "nonresponse" if response == "15" else "invalid_response")
    residence = _row_code(row, "c_res", 1)
    if residence not in ("1", "3"):
        reasons.append("unknown_residence" if _blank(row.get("c_res")) else "nonresident" if residence == "2" else "invalid_residence")
    age = _row_code(row, "eda", 2)
    raw_age = row.get("eda")
    age_missing = _blank(raw_age) or raw_age in (-1, "-1")
    age_unknown = age in ("98", "99") or age_missing
    if age_unknown:
        if age != "98" or population_id == COMPLETED_PROFESSIONAL_KNOWN_AGE:
            reasons.append("age_unknown")
    elif age is None:
        reasons.append("age_invalid")
    elif int(age) < 15:
        reasons.append("age_below_15")
    elif int(age) > (98 if population_id == NATIONAL_15_PLUS_CONTEXT else 97):
        reasons.append("age_above_population_max")
    if population_id == COMPLETED_PROFESSIONAL_KNOWN_AGE:
        education = _row_code(row, "cs_p13_1", 2)
        if education != "07":
            raw_education = row.get("cs_p13_1")
            if _blank(raw_education) or raw_education in (-1, "-1") or education == "99":
                reasons.append("unknown_education")
            elif education == "06":
                reasons.append("technical_education")
            elif education in ("08", "09"):
                reasons.append("postgraduate_education")
            elif education is None:
                reasons.append("invalid_education")
            else:
                reasons.append("other_education")
        completion = _row_code(row, "cs_p16", 1)
        if completion != "1":
            if _blank(row.get("cs_p16")) or completion == "9":
                reasons.append("unknown_completion")
            elif completion == "2":
                reasons.append("incomplete_education")
            else:
                reasons.append("invalid_completion")
    field = row.get("cs_p14_c")
    normalized_field = _lexeme(field, 6)
    field_unknown = normalized_field is None or normalized_field == "999999"
    return {
        "population_id": population_id,
        "eligible": not reasons,
        "age_unknown": age_unknown,
        "field_unknown": field_unknown,
        "exclusion_reasons": reasons,
    }


def _weight(value: object) -> float | None:
    if value is None or _blank(value):
        return None
    if isinstance(value, bool):
        raise ValueError("FAC_TRI must be a finite positive numeric value")
    if isinstance(value, str):
        text = value.strip(" ")
        if re.fullmatch(r"[0-9]+(?:\.[0-9]+)?", text) is None:
            raise ValueError("FAC_TRI must use ASCII digits")
        number = float(text)
    elif isinstance(value, (int, float, Decimal)):
        try:
            number = float(value)
        except OverflowError as exc:
            raise ValueError("FAC_TRI must be finite and positive") from exc
    else:
        raise ValueError("FAC_TRI must be numeric")
    if not math.isfinite(number) or number <= 0:
        raise ValueError("FAC_TRI must be finite and positive")
    return number


def _sum_weights(weights: list[float], missing: bool) -> float | None:
    if not weights or missing:
        return None
    try:
        total = math.fsum(weights)
    except OverflowError as exc:
        raise ValueError("weighted denominator overflow") from exc
    if not math.isfinite(total):
        raise ValueError("weighted denominator is nonfinite")
    return total


def summarize_denominators(rows: Iterable[Mapping[str, object]], population_id: str) -> dict:
    """Count row support separately from its weighted population denominator."""
    if population_id not in POPULATION_DEFINITIONS:
        raise ValueError(f"unknown population_id: {population_id}")
    observed = valid_response = eligible = unknown_field = 0
    exclusions: Counter[str] = Counter()
    weights: list[float] = []
    missing_weight = False
    for row in rows:
        result = classify_eligibility(row, population_id)
        observed += 1
        valid_response += _row_code(row, "r_def", 2) == "00"
        exclusions.update(result["exclusion_reasons"])
        if result["eligible"]:
            eligible += 1
            unknown_field += result["field_unknown"]
            weight = _weight(row.get("fac_tri"))
            if weight is None:
                missing_weight = True
            else:
                weights.append(weight)
    return {
        "population_id": population_id,
        "observed_rows_n": observed,
        "valid_response_n": valid_response,
        "observed_eligible_n": eligible,
        "unknown_field_eligible_n": unknown_field,
        "excluded_rows_n": observed - eligible,
        "exclusion_counts": dict(sorted(exclusions.items())),
        "weighted_eligible_denominator": _sum_weights(weights, missing_weight),
    }


def normalize_cmpe_key(raw: object, valid_catalog_keys: Collection[str]) -> str | None:
    """Return a six-digit key only when the verified period catalog contains it.

    Catalog keys are expected in their official unpadded ASCII spelling; a
    normalized collision is an error.  Person-row keys may have ASCII spaces.
    No field/occupation/industry bridge is inferred here.
    """
    keys: set[str] = set()
    for key in valid_catalog_keys:
        if not isinstance(key, str) or re.fullmatch(r"[0-9]{1,6}", key) is None or key == "999999":
            raise ValueError("period CMPE catalog contains an invalid key")
        normalized = key.zfill(6)
        if normalized in keys:
            raise ValueError("period CMPE catalog has duplicate normalized keys")
        keys.add(normalized)
    if not keys:
        raise ValueError("period CMPE catalog is empty")
    candidate = _lexeme(raw, 6)
    if candidate == "999999" or candidate not in keys:
        return None
    return candidate


def classify_income_state(row: Mapping[str, object]) -> dict:
    """Classify monthly occupied income without interpreting a physical zero.

    ING7C 1–5 identifies a known income band, 6 no income, 7 unspecified,
    and 0 not applicable. INGOCUP must be an exact positive ASCII integer in
    the package dictionary's 1–999998 range for a positive-known amount.
    """
    if not isinstance(row, Mapping):
        raise TypeError("row must be a mapping")
    band = _lexeme(row.get("ing7c"), 1)
    raw_amount = row.get("ingocup")
    amount_text = raw_amount.strip(" ") if isinstance(raw_amount, str) else None
    amount = int(amount_text) if amount_text and re.fullmatch(r"[0-9]{1,6}", amount_text) else None
    positive_amount = amount is not None and 1 <= amount <= 999998
    if band in ("1", "2", "3", "4", "5"):
        state = "positive_known" if positive_amount else "amount_unknown"
    elif band == "6":
        state = "conflicting" if positive_amount else "no_income"
    elif band == "7":
        state = "conflicting" if positive_amount else "unspecified"
    elif band == "0":
        state = "conflicting" if positive_amount else "not_applicable"
    elif _blank(row.get("ing7c")):
        state = "unknown_income_state"
    else:
        state = "invalid_income_state"
    return {"state": state, "positive_known": state == "positive_known"}


def summarize_measure_denominator(rows: Iterable[Mapping[str, object]], measure_id: str) -> dict:
    """Summarize measure support for rows already screened to one population.

    Employment is occupied count over respondents with known CLASE2 1–4.
    Positive-known income is among occupied people with a valid positive
    INGOCUP and consistent ING7C. Numeric estimates and variances belong to
    Phase 2; no person rows or amounts are returned.
    """
    if measure_id not in ("employment", "positive_known_income"):
        raise ValueError(f"unknown measure_id: {measure_id}")
    observed = valid = occupied = 0
    excluded: Counter[str] = Counter()
    weights: list[float] = []
    missing_weight = False
    for row in rows:
        if not isinstance(row, Mapping):
            raise TypeError("row must be a mapping")
        observed += 1
        class2 = _row_code(row, "clase2", 1)
        is_occupied = class2 == "1"
        occupied += is_occupied
        if class2 not in ("1", "2", "3", "4"):
            excluded["unknown_occupation_status" if _blank(row.get("clase2")) else "invalid_occupation_status"] += 1
            continue
        if measure_id == "positive_known_income":
            if not is_occupied:
                excluded["not_occupied"] += 1
                continue
            income = classify_income_state(row)
            if not income["positive_known"]:
                excluded[income["state"]] += 1
                continue
        valid += 1
        weight = _weight(row.get("fac_tri"))
        if weight is None:
            missing_weight = True
        else:
            weights.append(weight)
    return {
        "measure_id": measure_id,
        "observed_rows_n": observed,
        "observed_valid_n": valid,
        "observed_occupied_n": occupied,
        "excluded_rows_n": observed - valid,
        "excluded_counts": dict(sorted(excluded.items())),
        "weighted_denominator": _sum_weights(weights, missing_weight),
    }
