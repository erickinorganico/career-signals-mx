"""Descriptive comparisons of sanitized, accepted public ENOE estimates.

The input is ``build_profiles(...)["record_index"]``. This module never reads
person rows, internal estimates, or marginal intervals to infer change precision.
"""

from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path

from .populations import POPULATION_DEFINITIONS
from .metrics import load_metric_manifest
from .research_contract import GRAIN
from .resources import _resource
from .source_inventory import PERIODS


ROOT = Path(__file__).resolve().parents[1]
REVIEWED_ENTITY_REFERENCE = "02"
PRECISION_POLICY_VERSION = "normal/logit-90:CV15-30:singleton-adjust-v1"
SUPPRESSION_POLICY_VERSION = "research-v2-public:precision-gate-v1:complementary-parent-v1"
RAW_SHA256 = {
    "enoe_2024_q3": "f384a1b8872e051856ed2241289400302b13a8701489b1c596390452c183cd01",
    "enoe_2024_q4": "bb6d958c9bca11672d367d2c051cd08bf1654c471c2f32c8e21992c126a3b426",
    "enoe_2025_q1": "3931e7c9242147da6ebf9badb1e2b9a59d43d95a9811e077232be406c4ce6691",
    "enoe_2025_q2": "9530a017e3defb0658418b73a47a6039eeb54abf11342fa10693374736515127",
    "enoe_2025_q3": "7138b2bfabc740a9805b83b3fd0dae28287fc2aab3781a596a741b8fc7861566",
    "enoe_2025_q4": "e4d4284cc9924a40c39544a5530715f320a5627cd81997214c0430827616d9d6",
    "enoe_2026_q1": "429c288af46e408de743e5dfb92750f668df7e42789be5824f7cdf1c5ff56580",
    "enoe_2026_q2": "9ef8877c363f6097da1a04b2077cbda96300cc474b38f835c4963d1dd8f953df",
}
DICTIONARY_SHA256 = {
    "enoe_2024_q3": "ce67f37024a4a60767b0b140ad249e9eca98bf900459117cf82f63c3649d251b",
    "enoe_2024_q4": "ce67f37024a4a60767b0b140ad249e9eca98bf900459117cf82f63c3649d251b",
    "enoe_2025_q1": "410dff0ef72908a275e01be116e1bce949d79a38e17a403427840680c64cd51d",
    "enoe_2025_q2": "ce67f37024a4a60767b0b140ad249e9eca98bf900459117cf82f63c3649d251b",
    **{f"enoe_{year}_q{quarter}": "43dd74055f8d4c934c5101b68f70065517f4a4b538d8230592e273b4c0ec6cbe"
       for year, quarter in ((2025, 3), (2025, 4), (2026, 1), (2026, 2))},
}
REVISION_SHA256 = {
    "enoe_2024_q3": "cc3101c01a94cd7e9e810f82bc1cd2d49f3cf867d4ee5fc9e0761f6e283d565e",
    "enoe_2024_q4": "4716ded92c64ae5053e1f20c6d5df188eed8bf14e503ae88a86e7321cf4062e5",
}
METRIC_MANIFEST_SHA256 = "2ee87c8b7bfae9addcdf224ae93071023b918a5a22012e1355b9378b73e5827e"
POPULATION_SHA256 = "05822e8f3aefc64ab334cfe04cf986e409ebac811a073175aed1f43b33128ab4"
METHOD_VERSION = ("taylor_ultimate_cluster_wr_final_weights_v1:adapter:"
                  "cceacc5707f36e594d2659ed4a106ccee9bf6d9f0512296ac6d2380f132f19cc:metrics:"
                  + METRIC_MANIFEST_SHA256)
DESIGN_ID = "enoe_fac_tri_est_d_tri_upm_full_frame"
PRECISION_METHOD = "taylor_ultimate_cluster_wr_final_weights_v1_singleton_adjust"
CATALOG_SHA256 = "b521d2b5a07e3471da1bd6792183bb2c6864a38e022f74a6a919990c49f4a871"
ENT_CATALOG_SHA256 = "ea2e8198df208d0b662c00766739eb39c5a6b9a198821903d1a9416cdf9c7c1a"
CVE_CATALOG_SHA256 = "f297f6856885a3da13f754749000e0a35d8c1745e7f2cf474a1e2adc01e07ddf"
GEO_ASSERTION = "reviewed_candidate_signature_2026-09-22"
STATE_LIST_SHA256 = "0bda3e1035e65037524bebe92c02387851e85a43ed4830709e67dcbcf05df4ff"
APPROVED_SNAPSHOTS_SHA256 = "2edea1c722262efc8ce3f43dc4f0418eb704f5575b9d08933e4c802bff581670"
SNAPSHOT_IDS = tuple(RAW_SHA256)
_PINNED_SNAPSHOT_IDENTITY = {
    "enoe_2024_q3": ("2024-Q3", "ENT", ENT_CATALOG_SHA256),
    "enoe_2024_q4": ("2024-Q4", "ENT", ENT_CATALOG_SHA256),
    "enoe_2025_q1": ("2025-Q1", "ENT", ENT_CATALOG_SHA256),
    "enoe_2025_q2": ("2025-Q2", "ENT", ENT_CATALOG_SHA256),
    "enoe_2025_q3": ("2025-Q3", "CVE_ENT", CVE_CATALOG_SHA256),
    "enoe_2025_q4": ("2025-Q4", "CVE_ENT", CVE_CATALOG_SHA256),
    "enoe_2026_q1": ("2026-Q1", "CVE_ENT", CVE_CATALOG_SHA256),
    "enoe_2026_q2": ("2026-Q2", "CVE_ENT", CVE_CATALOG_SHA256),
}


def _digest(value: object) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=False,
                                     separators=(",", ":")).encode("utf-8")).hexdigest()


def _period_snapshot(period: str) -> str:
    return "enoe_" + period.lower().replace("-", "_")


def load_definition_registry(*, entity_reference_code: str | None = None) -> dict:
    """Load the reviewed registry only after checking independent accepted pins."""
    geo = json.loads(_resource("catalog", "data/catalog", "enoe-geography-equivalence.json").read_text(encoding="utf-8"))
    metric = load_metric_manifest()
    if (geo.get("concept_assertion") != GEO_ASSERTION or geo.get("review_status") != "REVIEW"
            or geo.get("evidence", {}).get("ent_catalog_sha256") != ENT_CATALOG_SHA256
            or geo.get("evidence", {}).get("cve_ent_catalog_sha256") != CVE_CATALOG_SHA256
            or geo.get("native_aliases") != {"ENT": "CVE_ENT", "CVE_ENT": "CVE_ENT"}):
        raise ValueError("geography concept assertion or catalog hashes differ from review")
    states = geo.get("states", [])
    if (len(states) != 32 or _digest(states) != STATE_LIST_SHA256
            or [x.get("code") for x in states] != [f"{n:02d}" for n in range(1, 33)]
            or len({x.get("name") for x in states}) != 32
            or any(x.get("ent") != str(i) or x.get("cve_ent") != f"{i:02d}"
                   for i, x in enumerate(states, 1))):
        raise ValueError("state equivalence must contain exact 32 code/name keys")
    population_definitions = {k: dict(v) for k, v in POPULATION_DEFINITIONS.items()}
    if _digest(population_definitions) != POPULATION_SHA256:
        raise ValueError("population definitions differ from reviewed version")
    if (metric.get("content_sha256") != METRIC_MANIFEST_SHA256
            or metric.get("version") != "enoe-metrics-2026-09-22"
            or set(metric.get("dictionary_refs", {})) != set(PERIODS)):
        raise ValueError("metric definitions differ from accepted manifest")
    approved_snapshots = geo.get("approved_snapshots", {})
    if (_digest(approved_snapshots) != APPROVED_SNAPSHOTS_SHA256
            or set(approved_snapshots) != set(RAW_SHA256)):
        raise ValueError("approved eight-snapshot source metadata differs from reviewed pins")
    snapshots = {}
    for i, period in enumerate(PERIODS):
        sid = _period_snapshot(period)
        approved = approved_snapshots[sid]
        native = "ENT" if i < 4 else "CVE_ENT"
        revision_sha = approved.get("revision_sha256")
        if (approved.get("raw_sha256") != RAW_SHA256[sid]
                or approved.get("period") != period
                or approved.get("source_id") != "inegi_enoe"
                or approved.get("source_url") is None
                or approved.get("catalog_title") != f"{period[:4]}|{('I', 'II', 'III', 'IV')[int(period[-1]) - 1]} Trimestre (ENOE)"
                or approved.get("dictionary_sha256") != DICTIONARY_SHA256[sid]
                or approved.get("field_catalog_sha256") != CATALOG_SHA256
                or approved.get("native_geography_field") != native
                or approved.get("state_catalog_sha256") != (ENT_CATALOG_SHA256 if native == "ENT" else CVE_CATALOG_SHA256)
                or revision_sha != REVISION_SHA256.get(sid)
                or approved.get("revision_status") != ("sdem_bitacora_present" if sid in REVISION_SHA256
                                              else "no_sdem_bitacora_member_found")):
            raise ValueError(f"unapproved source, dictionary, catalog or correction: {sid}")
        snapshots[sid] = {"period": period, "raw_sha256": RAW_SHA256[sid],
                          "source_family": "INEGI ENOE", "edition": "ENOE 15+ quarterly SDEM",
                          "edition_review": GEO_ASSERTION, "edition_date": None,
                          "correction_review": "reviewed_exact_snapshot_revision",
                          "revision_sha256": revision_sha, "source_url": approved["source_url"],
                          "native_geography_field": native,
                          "dictionary_sha256": DICTIONARY_SHA256[sid],
                          "state_catalog_sha256": ENT_CATALOG_SHA256 if native == "ENT" else CVE_CATALOG_SHA256,
                          "field_catalog_sha256": CATALOG_SHA256}
    registry = {"schema_version": "1.0", "grain": tuple(GRAIN), "periods": tuple(PERIODS),
                "snapshots": snapshots, "states": {x["code"]: x for x in states},
                "geography_concept": "ENOE national or 32 entity concepts under reviewed candidate signature",
                "geography_concept_assertion": GEO_ASSERTION,
                "population_versions": {key: POPULATION_SHA256 for key in POPULATION_DEFINITIONS},
                "classification_versions": {"field_of_study": "CMPE 2016:" + CATALOG_SHA256,
                                            "occupation": "separate-all-v1", "industry": "separate-all-v1"},
                "metric_manifest_sha256": METRIC_MANIFEST_SHA256,
                "metric_version": metric["version"],
                "metrics": {x["id"]: x for x in metric["metrics"]},
                "method_version": METHOD_VERSION, "design_id": DESIGN_ID,
                "precision_method": PRECISION_METHOD,
                "estimator_version": "taylor_ultimate_cluster_wr_final_weights_v1",
                "suppression_policy_version": SUPPRESSION_POLICY_VERSION,
                "precision_policy_version": PRECISION_POLICY_VERSION}
    if entity_reference_code is not None:
        if entity_reference_code != REVIEWED_ENTITY_REFERENCE:
            raise ValueError("reviewed entity reference is fixed to Baja California 02")
        registry["entity_reference_code"] = entity_reference_code
    return registry


def _signature(record: dict, provenance: dict, registry: dict) -> tuple[dict, list[str]]:
    reasons: list[str] = []
    expected_grain = tuple(record.get(key) for key in GRAIN)
    if (tuple(provenance.get("grain", ())) != expected_grain
            or provenance.get("record_id") != "v2r:" + _digest(list(expected_grain))):
        reasons.append("grain_identity")
    sid = record.get("source_snapshot_id")
    approved = registry.get("snapshots", {}).get(sid)
    pinned_identity = _PINNED_SNAPSHOT_IDENTITY.get(sid)
    if sid not in RAW_SHA256 or not approved or approved.get("raw_sha256") != RAW_SHA256.get(sid):
        reasons.append("unapproved_snapshot")
        approved = {}
    elif provenance.get("snapshot_sha256") != RAW_SHA256[sid]:
        reasons.append("unapproved_snapshot")
    expected_url = (f"https://www.inegi.org.mx/contenidos/programas/enoe/15ymas/datosabiertos/"
                    f"{sid[5:9]}/conjunto_de_datos_enoe_{sid[5:9]}_{sid[-1]}t_csv.zip") if sid in RAW_SHA256 else None
    if (approved.get("source_family") != "INEGI ENOE"
            or approved.get("edition") != "ENOE 15+ quarterly SDEM"
            or approved.get("edition_review") != GEO_ASSERTION
            or approved.get("edition_date") is not None
            or approved.get("correction_review") != "reviewed_exact_snapshot_revision"
            or approved.get("source_url") != expected_url
            or approved.get("revision_sha256") != REVISION_SHA256.get(sid)
            or approved.get("dictionary_sha256") != DICTIONARY_SHA256.get(sid)
            or approved.get("field_catalog_sha256") != CATALOG_SHA256):
        reasons.append("edition_revision")
    if (not pinned_identity
            or approved.get("period") != pinned_identity[0]
            or record.get("period_id") != pinned_identity[0]):
        reasons.append("period_provenance")
    if (pinned_identity
            and (approved.get("native_geography_field") != pinned_identity[1]
                 or approved.get("state_catalog_sha256") != pinned_identity[2])):
        reasons.append("geography_snapshot_identity")
    population = record.get("population_id")
    if registry.get("population_versions", {}).get(population) != POPULATION_SHA256:
        reasons.append("population_version")
    metric_id = record.get("metric_id")
    metric = registry.get("metrics", {}).get(metric_id)
    if (not metric or registry.get("metric_manifest_sha256") != METRIC_MANIFEST_SHA256
            or registry.get("metric_version") != "enoe-metrics-2026-09-22"
            or metric != next((x for x in load_metric_manifest()["metrics"] if x["id"] == metric_id), None)):
        reasons.append("metric_definition")
        metric = {}
    if metric and (record.get("unit") != metric.get("unit")
                   or record.get("price_basis") != metric.get("price_basis")):
        reasons.append("metric_unit_basis")
    if (record.get("method_version") != METHOD_VERSION
            or provenance.get("method_version") != record.get("method_version")
            or record.get("design_id") != DESIGN_ID
            or registry.get("method_version") != METHOD_VERSION
            or registry.get("design_id") != DESIGN_ID
            or registry.get("estimator_version") != "taylor_ultimate_cluster_wr_final_weights_v1"):
        reasons.append("method_version")
    precision = record.get("precision") or {}
    if (precision.get("method") != PRECISION_METHOD
            or precision.get("singleton_policy") not in ("adjust", "fail")
            or not precision.get("ci_method")
            or type(precision.get("official_precision")) is not bool
            or registry.get("precision_method") != PRECISION_METHOD
            or registry.get("precision_policy_version") != PRECISION_POLICY_VERSION
            or registry.get("suppression_policy_version") != SUPPRESSION_POLICY_VERSION):
        reasons.append("precision_policy")
    geo = record.get("geography_id")
    native = approved.get("native_geography_field")
    states = registry.get("states", {})
    state = states.get(geo)
    if (set(states) != {f"{n:02d}" for n in range(1, 33)}
            or _digest([states[f"{n:02d}"] for n in range(1, 33)]
                       if len(states) == 32 else []) != STATE_LIST_SHA256):
        reasons.append("geography_catalog")
    if geo == "mx":
        geo_type, geo_key, geo_name = "national", "mx", "México"
    elif state and native in ("ENT", "CVE_ENT") and geo.isascii() and geo.isdigit():
        geo_type, geo_key, geo_name = "entity", state.get("code"), state.get("name")
        expected_sha = ENT_CATALOG_SHA256 if native == "ENT" else CVE_CATALOG_SHA256
        if (state.get("code") != geo or state.get("ent") != str(int(geo))
                or state.get("cve_ent") != geo
                or not geo_name or approved.get("state_catalog_sha256") != expected_sha):
            reasons.append("geography_alias_code_name")
    else:
        geo_type, geo_key, geo_name = None, None, None
        reasons.append("geography_alias_code_name")
    if (registry.get("geography_concept_assertion") != GEO_ASSERTION
            or not registry.get("geography_concept")):
        reasons.append("geography_concept_review")
    classifications = registry.get("classification_versions", {})
    if classifications.get("field_of_study") != "CMPE 2016:" + CATALOG_SHA256:
        reasons.append("field_classification")
    if classifications.get("occupation") != "separate-all-v1" or classifications.get("industry") != "separate-all-v1":
        reasons.append("concept_classification")
    if record.get("occupation_id") != "all" or record.get("industry_id") != "all":
        reasons.append("unsupported_concept")
    signature = {"source_family": approved.get("source_family"), "edition": approved.get("edition"),
                 "edition_review": approved.get("edition_review"),
                 "population_id": population, "population_version": registry.get("population_versions", {}).get(population),
                 "geography_type": geo_type, "geography_concept": registry.get("geography_concept"),
                 "geography_key": geo_key, "geography_name": geo_name,
                 "recorded_sex_id": record.get("recorded_sex_id"),
                 "field_of_study_id": record.get("field_of_study_id"),
                 "field_classification": classifications.get("field_of_study"),
                 "occupation_id": record.get("occupation_id"),
                 "occupation_classification": classifications.get("occupation"),
                 "industry_id": record.get("industry_id"),
                 "industry_classification": classifications.get("industry"),
                 "metric_id": metric_id, "metric_version": registry.get("metric_version"),
                 "metric_numerator": metric.get("numerator"), "metric_denominator": metric.get("denominator"),
                 "metric_dictionary_refs": tuple(metric.get("dictionary_refs", ())),
                 "unit": record.get("unit"), "price_basis": record.get("price_basis"),
                 "method_id": record.get("method_id"), "method_version": record.get("method_version"),
                 "design_id": record.get("design_id"), "estimator_version": registry.get("estimator_version"),
                 "precision_method": precision.get("method"), "ci_method": precision.get("ci_method"),
                 "singleton_policy": precision.get("singleton_policy"),
                 "official_precision": precision.get("official_precision"),
                 "precision_policy_version": registry.get("precision_policy_version"),
                 "suppression_policy_version": registry.get("suppression_policy_version"),
                 "native_geography_field": native, "state_catalog_sha256": approved.get("state_catalog_sha256")}
    return signature, sorted(set(reasons))


def comparison_signature(record: dict, provenance: dict, definition_registry: dict) -> dict:
    signature, reasons = _signature(record, provenance, definition_registry)
    return {**signature, "validation_reasons": reasons}


def _result(left: dict | None, right: dict | None, registry: dict, *, axis: str | None) -> dict:
    a, b = (left or {}).get("record", {}), (right or {}).get("record", {})
    reasons: list[str] = []
    if not left:
        reasons.append("missing_previous_endpoint")
    if not right:
        reasons.append("missing_current_endpoint")
    if axis == "entity" and registry.get("entity_reference_code") != REVIEWED_ENTITY_REFERENCE:
        reasons.append("entity_reference_code")
    ls, le = _signature(a, left, registry) if left else ({}, [])
    rs, re = _signature(b, right, registry) if right else ({}, [])
    reasons.extend(le + re)
    if left and right:
        if axis is None:
            try:
                pi, ci = registry["periods"].index(a.get("period_id")), registry["periods"].index(b.get("period_id"))
                if ci - pi not in (1, 4):
                    reasons.append("period_adjacency")
            except ValueError:
                reasons.append("period_adjacency")
        else:
            if a.get("period_id") != b.get("period_id"):
                reasons.append("period_id")
            if a.get("source_snapshot_id") != b.get("source_snapshot_id"):
                reasons.append("source_snapshot_id")
            if left.get("snapshot_sha256") != right.get("snapshot_sha256"):
                reasons.append("source_snapshot_sha256")
            if axis == "sex":
                if (ls.get("geography_key") != "mx" or rs.get("geography_key") != "mx"
                        or {a.get("recorded_sex_id"), b.get("recorded_sex_id")} != {"1", "2"}):
                    reasons.append("sex_axis")
            elif axis == "entity":
                reference = registry.get("entity_reference_code")
                if reference != REVIEWED_ENTITY_REFERENCE:
                    reasons.append("entity_reference_code")
                if (ls.get("geography_type") != "entity" or rs.get("geography_type") != "entity"
                        or ls.get("geography_key") == rs.get("geography_key")
                        or reference not in (ls.get("geography_key"), rs.get("geography_key"))):
                    reasons.append("entity_axis")
            else:
                reasons.append("unsupported_axis")
        ignored = {"native_geography_field", "state_catalog_sha256"}
        if axis == "sex":
            ignored.add("recorded_sex_id")
        if axis == "entity":
            ignored.update(("geography_key", "geography_name"))
        for name in sorted(set(ls) | set(rs) - ignored):
            if name in ignored:
                continue
            if ls.get(name) is None or rs.get(name) is None or ls.get(name) != rs.get(name):
                reasons.append(name)
        if axis is None and ls.get("geography_type") == "entity" and rs.get("geography_type") == "entity":
            if (registry.get("geography_concept_assertion") != GEO_ASSERTION
                    or ls.get("geography_name") != rs.get("geography_name")):
                reasons.append("geography_concept_review")
        for item, row, label in ((left, a, "previous"), (right, b, "current")):
            if item.get("redaction_reason"):
                reasons.append(item["redaction_reason"])
            if row.get("status") not in ("MEASURED", "REVIEW") or row.get("value") is None:
                reasons.append(label + "_unsupported")
            elif type(row["value"]) not in (int, float) or not math.isfinite(row["value"]):
                reasons.append(label + "_nonfinite")
    reasons = sorted(set(reasons))
    comparable = not reasons
    delta = b["value"] - a["value"] if comparable else None
    relative = (100 * delta / a["value"] if comparable and a["value"] else None)
    unit = a.get("unit") if left else b.get("unit")
    display = ("percentage points" if unit == "percent" else
               "nominal MXN/month" if unit == "MXN/month" else unit)
    limitations = (["descriptive_change_only", "quarterly_samples_may_overlap"]
                   if axis is None else ["descriptive_difference_only"])
    if axis is None and left and right:
        limitations.append("seasonality_qoq" if registry["periods"].index(b["period_id"]) -
                           registry["periods"].index(a["period_id"]) == 1 else "like_quarter_yoy") if "period_adjacency" not in reasons else None
    if (left and registry.get("snapshots", {}).get(a.get("source_snapshot_id"), {}).get("edition_date") is None
            or right and registry.get("snapshots", {}).get(b.get("source_snapshot_id"), {}).get("edition_date") is None):
        limitations.append("unknown_edition_date")
    if axis is not None:
        limitations.append("same_period_descriptive_slice")
    return {"comparison_id": "v2c:" + _digest([axis or "time", (left or {}).get("record_id"),
                                                (right or {}).get("record_id")]),
            "previous_record_id": (left or {}).get("record_id"),
            "current_record_id": (right or {}).get("record_id"),
            "status": "REVIEW" if comparable else "BLOCKED", "comparable": comparable,
            "absolute_change": delta, "relative_change_pct": relative,
            "display_unit": display, "reasons": reasons, "limitations": limitations,
            "evidence_refs": sorted(set(a.get("evidence_refs", []) + b.get("evidence_refs", []))),
            "source_snapshot_ids": [a.get("source_snapshot_id"), b.get("source_snapshot_id")],
            "source_sha256s": [(left or {}).get("snapshot_sha256"), (right or {}).get("snapshot_sha256")],
            "signature_previous": ls, "signature_current": rs}


def compare_public_records(previous: dict, current: dict, *, registry: dict) -> dict:
    return _result(previous, current, registry, axis=None)


def compare_public_slices(left: dict, right: dict, *, axis: str, registry: dict) -> dict:
    return _result(left, right, registry, axis=axis)


def build_comparison_ledger(profiles: dict, *, registry: dict) -> list[dict]:
    """Keep all expected time slots and available latest-quarter slice slots."""
    periods = tuple(registry["periods"])
    if set(profiles.get("periods", ())) != set(periods) or len(profiles.get("periods", ())) != len(periods):
        raise ValueError("profiles must declare the exact eight accepted quarters")
    index = profiles["record_index"]
    by_key = {}
    for record_id, item in index.items():
        if item.get("record_id") != record_id:
            raise ValueError("sanitized index key differs from stable record ID")
        row = item["record"]
        grain = tuple(row.get(name) for name in GRAIN)
        if tuple(item.get("grain", ())) != grain or record_id != "v2r:" + _digest(list(grain)):
            raise ValueError("sanitized record grain or canonical ID differs from the public index")
        key = (row["population_id"], row["field_of_study_id"], row["occupation_id"],
               row["industry_id"], row["geography_id"], row["recorded_sex_id"], row["metric_id"], row["period_id"])
        if key in by_key:
            raise ValueError("duplicate public comparison grain")
        by_key[key] = item
    national = profiles.get("national", [])
    for cell in national:
        item = index.get(cell.get("record_id"))
        if (item is None or cell.get("source_sha256", item["snapshot_sha256"]) != item["snapshot_sha256"]
                or any(cell.get(name) != item["record"].get(name) for name in GRAIN)
                or cell.get("value") != item["record"].get("value")):
            raise ValueError("national profile cell differs from sanitized record index")
    series = sorted({(c["population_id"], c["field_of_study_id"], c["occupation_id"],
                      c["industry_id"], c["geography_id"], c["recorded_sex_id"], c["metric_id"])
                     for c in national})
    ledger = []
    for key in series:
        for offset, label in ((1, "adjacent_quarter"), (4, "like_quarter_annual")):
            for i in range(len(periods) - offset):
                left = by_key.get((*key, periods[i]))
                right = by_key.get((*key, periods[i + offset]))
                entry = _result(left, right, registry, axis=None)
                entry["comparison_type"] = label
                entry["slot_periods"] = [periods[i], periods[i + offset]]
                entry["comparison_id"] = "v2c:" + _digest([label, key, *entry["slot_periods"],
                                                            entry["previous_record_id"], entry["current_record_id"]])
                ledger.append(entry)
    latest = periods[-1]
    slice_keys = sorted({(c["population_id"], c["field_of_study_id"], c["occupation_id"],
                         c["industry_id"], c["metric_id"])
                        for c in profiles.get("latest_recorded_sexes", []) + profiles.get("latest_states", [])})
    for population, field, occupation, industry, metric in slice_keys:
        prefix = (population, field, occupation, industry)
        left = by_key.get((*prefix, "mx", "1", metric, latest))
        right = by_key.get((*prefix, "mx", "2", metric, latest))
        if left or right:
            entry = _result(left, right, registry, axis="sex")
            entry["comparison_type"] = "recorded_sex_slice"
            entry["slot_periods"] = [latest, latest]
            entry["comparison_id"] = "v2c:" + _digest(["recorded_sex_slice", prefix, metric, latest,
                                                        entry["previous_record_id"], entry["current_record_id"]])
            ledger.append(entry)
        for state in sorted(registry["states"]):
            if state == REVIEWED_ENTITY_REFERENCE:
                continue
            left = by_key.get((*prefix, REVIEWED_ENTITY_REFERENCE, "all", metric, latest))
            right = by_key.get((*prefix, state, "all", metric, latest))
            if left or right:
                entry = _result(left, right, registry, axis="entity")
                entry["comparison_type"] = "entity_slice"
                entry["slot_periods"] = [latest, latest]
                entry["comparison_id"] = "v2c:" + _digest(["entity_slice", prefix, metric, latest,
                                                            REVIEWED_ENTITY_REFERENCE, state,
                                                            entry["previous_record_id"], entry["current_record_id"]])
                ledger.append(entry)
    return ledger
