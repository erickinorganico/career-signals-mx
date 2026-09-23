"""One independently pinned, sanitized public projection for offline publishing."""

from __future__ import annotations

from copy import deepcopy
import json

from jsonschema import Draft202012Validator

from .analysis_v2 import _digest
from .findings_v2 import _json_safe, validate_analysis_packet
from .resources import contract_path


MODEL_KEYS = frozenset({"schema_version", "source_manifest", "records", "profiles",
                        "coverage", "comparisons", "claims", "opening_claim_ids",
                        "limitations", "figure_links", "content_digest"})


def _figure_links(claims: list[dict], opening_ids: list[str], records: dict,
                  profiles: dict, comparisons: list[dict]) -> list[dict]:
    by_id = {claim["claim_id"]: claim for claim in claims}
    links = []
    latest = profiles["periods"][-1]
    focal = ("033100", "032100", "031300")

    def add(name: str, ids: list[str], claim_ids: list[str] | None = None) -> None:
        selected = sorted(set(ids))
        if not selected:
            return  # A sparse accepted packet may have no supported row for this figure.
        present = set(selected)
        comparison_ids = sorted(c["comparison_id"] for c in comparisons
                                if c["previous_record_id"] in present
                                and c["current_record_id"] in present
                                and c["comparable"] is True and c["status"] == "REVIEW")
        links.append({"figure_id": "figure:" + name, "table_id": "table:" + name,
                      "record_ids": selected, "comparison_ids": comparison_ids,
                      "claim_ids": claim_ids or [],
                      "source_ids": sorted({records[rid]["record"]["source_snapshot_id"]
                                            for rid in selected})})

    add("national-context", [rid for rid, item in records.items()
                             if item["record"]["period_id"] == latest
                             and item["record"]["field_of_study_id"] == "all"
                             and item["record"]["geography_id"] == "mx"
                             and item["record"]["recorded_sex_id"] == "all"
                             and item["record"]["metric_id"] in
                             ("employment_rate", "positive_income_mean", "positive_income_coverage")])
    add("focal-latest", [rid for rid, item in records.items()
                         if item["record"]["period_id"] == latest
                         and item["record"]["field_of_study_id"] in focal
                         and item["record"]["geography_id"] == "mx"
                         and item["record"]["recorded_sex_id"] == "all"
                         and item["record"]["metric_id"] in
                         ("employment_rate", "positive_income_mean", "positive_income_coverage")])
    add("eight-quarter-trends", [rid for rid, item in records.items()
                                 if item["record"]["period_id"] in profiles["periods"]
                                 and item["record"]["field_of_study_id"] in focal
                                 and item["record"]["geography_id"] == "mx"
                                 and item["record"]["recorded_sex_id"] == "all"
                                 and item["record"]["metric_id"] in
                                 ("employment_rate", "positive_income_mean", "positive_income_coverage")])
    add("recorded-sex", [cell["record_id"] for cell in profiles["latest_recorded_sexes"]
                         if cell["field_of_study_id"] in focal
                         and cell["metric_id"] in ("employment_rate", "positive_income_mean")])
    add("state-availability", [cell["record_id"] for cell in profiles["latest_states"]
                               if cell["field_of_study_id"] == "033100"
                               and cell["metric_id"] == "employment_rate"])
    add("other-fields", [cell["record_id"] for cell in profiles["latest_fields"]
                         if cell["field_of_study_id"] not in focal
                         and cell["metric_id"] == "employment_rate"])
    for claim_id in opening_ids:
        claim = by_id[claim_id]
        add("opening-" + claim_id[4:], claim["record_ids"], [claim_id])
    return links


def build_publication_model(packet: dict) -> dict:
    """Accept only the installed validator's independently pinned Phase 3 packet."""
    errors = validate_analysis_packet(packet)
    if errors:
        raise ValueError(f"Phase 3 packet rejected: {errors[:3]}")
    model = {"schema_version": "2.0",
             "source_manifest": deepcopy(packet["source_manifest"]),
             "records": deepcopy(dict(sorted(packet["record_index"].items()))),
             "profiles": deepcopy(packet["profiles"]), "coverage": deepcopy(packet["coverage"]),
             "comparisons": deepcopy(packet["comparisons"]), "claims": deepcopy(packet["claims"]),
             "opening_claim_ids": list(packet["opening_claim_ids"]),
             "limitations": list(packet["limitations"])}
    model["figure_links"] = _figure_links(model["claims"], model["opening_claim_ids"],
                                          model["records"], model["profiles"],
                                          model["comparisons"])
    model["content_digest"] = _digest(model)
    errors = validate_publication_model(model)
    if errors:
        raise ValueError(f"Public model rejected: {errors[:3]}")
    return model


def validate_publication_model(model: dict) -> list[dict]:
    """Reject altered values, unsupported joins, extra fields and diagnostic data."""
    if not isinstance(model, dict) or not _json_safe(model):
        return [{"id": "json_scalars", "message": "unsafe JSON value"}]
    if set(model) != MODEL_KEYS:
        return [{"id": "root_keys", "message": "public model keys differ"}]
    if _digest({k: v for k, v in model.items() if k != "content_digest"}) != model["content_digest"]:
        return [{"id": "content_digest", "message": "public content changed"}]
    schema = json.loads(contract_path("publication-v2.schema.json").read_text(encoding="utf-8"))
    errors = [{"id": "schema", "message": f"{'/'.join(map(str, err.path))}: {err.message}"}
              for err in Draft202012Validator(schema).iter_errors(model)]
    if errors:
        return errors[:20]
    records = model["records"]
    try:
        expected_links = _figure_links(model["claims"], model["opening_claim_ids"], records,
                                       model["profiles"], model["comparisons"])
        if expected_links != model["figure_links"]:
            return [{"id": "figure_links", "message": "figure links differ from accepted claims"}]
        source_ids = set(model["source_manifest"]["sources"])
        comparison_ids = {item["comparison_id"] for item in model["comparisons"]}
        claim_ids = {item["claim_id"] for item in model["claims"]}
        for link in model["figure_links"]:
            if (not set(link["record_ids"]) <= set(records)
                    or not set(link["comparison_ids"]) <= comparison_ids
                    or not set(link["claim_ids"]) <= claim_ids
                    or not set(link["source_ids"]) <= source_ids):
                return [{"id": "figure_reference", "message": "orphan figure reference"}]
        packet = {"schema_version": model["schema_version"],
                  "source_manifest": model["source_manifest"], "record_index": records,
                  "profiles": model["profiles"], "coverage": model["coverage"],
                  "comparisons": model["comparisons"], "claims": model["claims"],
                  "opening_claim_ids": model["opening_claim_ids"],
                  "limitations": model["limitations"]}
        packet["content_digest"] = _digest(packet)
        return validate_analysis_packet(packet)
    except (KeyError, TypeError, ValueError) as exc:
        return [{"id": "reference", "message": str(exc)}]
