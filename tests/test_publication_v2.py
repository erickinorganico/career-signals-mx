"""The publication boundary is the independently accepted Phase 3 packet."""

from copy import deepcopy
import json
from pathlib import Path

import pytest

from brujula.publication_v2 import build_publication_model, validate_publication_model
from brujula.publication_v2 import _figure_links
from brujula.analysis_v2 import _digest
from tests.publication_v2_support import pinned_synthetic_packet


PACKET = Path(__file__).resolve().parents[1] / ".cache/research/phase3-analysis/analysis.json"


@pytest.fixture
def packet(monkeypatch):
    return pinned_synthetic_packet(monkeypatch)


@pytest.fixture
def model(packet):
    return build_publication_model(packet)


@pytest.fixture(scope="module")
def real_packet():
    if not PACKET.is_file():
        pytest.skip("optional persisted real Phase 3 packet is unavailable")
    return json.loads(PACKET.read_text(encoding="utf-8"))


def test_synthetic_packet_boundary_is_complete_without_real_cache(packet, model):
    assert validate_publication_model(model) == []
    assert set(model["records"]) == set(packet["record_index"])
    assert model["opening_claim_ids"] == packet["opening_claim_ids"]
    assert model["figure_links"] == []  # fixture has only population_total, no matching figure


def test_actual_packet_is_complete_and_exact(real_packet):
    model = build_publication_model(real_packet)
    assert validate_publication_model(model) == []
    assert len(model["records"]) == 6739
    assert len(model["profiles"]["metric_ids"]) == 23
    assert set(model["records"]) == set(real_packet["record_index"])
    assert model["opening_claim_ids"] == real_packet["opening_claim_ids"]
    assert len(model["figure_links"]) == 9
    state = next(link for link in model["figure_links"] if link["figure_id"] == "figure:state-availability")
    assert len(state["record_ids"]) == 32


def test_changed_packet_and_model_are_rejected(packet, model):
    altered = deepcopy(packet)
    rid = next(iter(altered["record_index"]))
    altered["record_index"][rid]["record"]["value"] = 99.123456789
    altered["content_digest"] = _digest({k: v for k, v in altered.items() if k != "content_digest"})
    with pytest.raises(ValueError):
        build_publication_model(altered)
    public = deepcopy(model)
    public["records"][rid]["record"]["value"] = 99.123456789
    public["content_digest"] = _digest({k: v for k, v in public.items() if k != "content_digest"})
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
    altered["content_digest"] = _digest({k: v for k, v in altered.items() if k != "content_digest"})
    assert validate_publication_model(altered)
    altered = deepcopy(model)
    altered["records"][rid]["record"]["value"] = float("nan")
    assert validate_publication_model(altered)


def test_orphan_figure_and_unknown_root_are_rejected(model):
    altered = deepcopy(model)
    altered["figure_links"].append({"figure_id": "figure:orphan", "table_id": "table:orphan",
                                    "record_ids": ["v2r:" + "0" * 64], "comparison_ids": [],
                                    "claim_ids": [], "source_ids": ["unknown"]})
    altered["content_digest"] = _digest({k: v for k, v in altered.items() if k != "content_digest"})
    assert validate_publication_model(altered)
    altered = deepcopy(model)
    altered["diagnostic"] = 7
    assert validate_publication_model(altered)


def test_figure_comparisons_exclude_blocked_even_with_both_endpoints():
    earlier, later = "v2r:" + "1" * 64, "v2r:" + "2" * 64
    records = {rid: {"record": {"period_id": period, "field_of_study_id": "033100",
                                "geography_id": "mx", "recorded_sex_id": "all",
                                "metric_id": "employment_rate", "source_snapshot_id": "source-1"}}
               for rid, period in ((earlier, "2026-Q1"), (later, "2026-Q2"))}
    comparisons = [{"comparison_id": "v2c:" + char * 64,
                    "previous_record_id": earlier, "current_record_id": later,
                    "comparable": comparable, "status": status}
                   for char, comparable, status in (("a", True, "REVIEW"),
                                                     ("b", False, "BLOCKED"))]
    profiles = {"periods": ["2024-Q3", "2024-Q4", "2025-Q1", "2025-Q2",
                            "2025-Q3", "2025-Q4", "2026-Q1", "2026-Q2"],
                "latest_recorded_sexes": [], "latest_states": [], "latest_fields": []}
    links = _figure_links([], [], records, profiles, comparisons)
    trend = next(link for link in links if link["figure_id"] == "figure:eight-quarter-trends")
    assert trend["record_ids"] == [earlier, later]
    assert trend["comparison_ids"] == ["v2c:" + "a" * 64]
