"""The publication boundary is the independently accepted Phase 3 packet."""

from copy import deepcopy
import json
from pathlib import Path

import pytest

from brujula.publication_v2 import build_publication_model, validate_publication_model


PACKET = Path(__file__).resolve().parents[1] / ".cache/research/phase3-analysis/analysis.json"


@pytest.fixture(scope="module")
def packet():
    return json.loads(PACKET.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def model(packet):
    return build_publication_model(packet)


def test_actual_packet_is_complete_and_exact(packet, model):
    assert validate_publication_model(model) == []
    assert len(model["records"]) == 6739
    assert len(model["profiles"]["metric_ids"]) == 23
    assert set(model["records"]) == set(packet["record_index"])
    assert model["opening_claim_ids"] == packet["opening_claim_ids"]
    assert len(model["figure_links"]) == 9
    assert all(link["record_ids"] for link in model["figure_links"])
    state = next(link for link in model["figure_links"] if link["figure_id"] == "figure:state-availability")
    assert len(state["record_ids"]) == 32


def test_changed_packet_and_model_are_rejected(packet, model):
    altered = deepcopy(packet)
    rid = next(iter(altered["record_index"]))
    altered["record_index"][rid]["record"]["value"] = 99.123456789
    with pytest.raises(ValueError):
        build_publication_model(altered)
    public = deepcopy(model)
    public["records"][rid]["record"]["value"] = 99.123456789
    assert validate_publication_model(public)


def test_suppression_and_nonfinite_are_rejected(model):
    rid = next(r for r, item in model["records"].items() if item.get("redaction_reason"))
    item = model["records"][rid]["record"]
    assert item["value"] is None
    assert item["weighted_denominator"] is None
    assert item["support"]["weighted_support_total"] is None
    assert all(item["precision"][name] is None for name in
               ("standard_error", "coefficient_variation", "ci90_lower", "ci90_upper"))
    altered = deepcopy(model)
    altered["records"][rid]["record"]["precision"]["standard_error"] = 876543.25
    assert validate_publication_model(altered)
    altered = deepcopy(model)
    altered["records"][rid]["record"]["value"] = float("nan")
    assert validate_publication_model(altered)


def test_orphan_figure_and_unknown_root_are_rejected(model):
    altered = deepcopy(model)
    altered["figure_links"][0]["record_ids"].append("v2r:" + "0" * 64)
    assert validate_publication_model(altered)
    altered = deepcopy(model)
    altered["diagnostic"] = 7
    assert validate_publication_model(altered)
