"""Aggregate-only analytical handoff and independent provenance controls."""

from copy import deepcopy
import json
import os
from pathlib import Path

import pytest

from brujula import findings_v2
from brujula.analysis_v2 import _digest
from brujula.comparisons_v2 import load_definition_registry
from tests.test_analysis_v2 import synthetic_inputs


ROOT = Path(__file__).resolve().parents[1]


def _synthetic_packet(monkeypatch, *, complementary=False):
    publics, accepted = synthetic_inputs(monkeypatch, complementary=complementary)
    registry = load_definition_registry(entity_reference_code="02")
    registry["metric_manifest_sha256"] = accepted["manifest"]["metric_manifest_sha256"]
    monkeypatch.setattr(findings_v2, "load_definition_registry", lambda **_kwargs: deepcopy(registry))
    packet = findings_v2._assemble(publics, accepted["manifest"], accepted["audits"], registry)
    frozen = findings_v2._reference_from_packet(packet)
    monkeypatch.setattr(findings_v2, "_load_reference", lambda: deepcopy(frozen))
    return packet, publics, accepted, registry


def test_synthetic_packet_has_complete_public_only_shape(monkeypatch):
    packet, publics, accepted, registry = _synthetic_packet(monkeypatch)
    assert findings_v2.validate_analysis_packet(packet) == []
    again = findings_v2.build_analysis_packet(publics, accepted["manifest"], accepted["audits"], registry)
    assert packet == again
    assert set(packet) == {"schema_version", "source_manifest", "record_index", "profiles",
                           "coverage", "comparisons", "claims", "opening_claim_ids",
                           "limitations", "content_digest"}
    assert packet["coverage"]["expected_cells"]["national"] == 8 * 5
    assert packet["opening_claim_ids"] == []
    assert findings_v2.VALID_LIMITATIONS["empty"] in packet["limitations"]
    assert '"estimate":' not in json.dumps(packet)


def test_saved_json_packet_remains_valid_after_round_trip(monkeypatch):
    packet, _, _, _ = _synthetic_packet(monkeypatch, complementary=True)
    loaded = json.loads(json.dumps(packet, ensure_ascii=False, allow_nan=False))
    assert findings_v2.validate_analysis_packet(loaded) == []
    assert loaded == packet


def test_acquisition_clock_is_verified_but_not_analytical_identity(monkeypatch):
    packet, publics, accepted, registry = _synthetic_packet(monkeypatch)
    changed = deepcopy(publics)
    sid = sorted(changed)[0]
    changed[sid]["sources"][0]["acquired_at"] = "2026-09-24T00:00:00Z"
    accepted["manifest"]["snapshots"][sid]["public_v2_digest"] = _digest(changed[sid])
    replayed = findings_v2.build_analysis_packet(changed, accepted["manifest"],
                                                  accepted["audits"], registry)
    assert replayed == packet
    assert findings_v2.validate_analysis_packet(replayed) == []
    accepted["manifest"]["snapshots"][sid]["public_v2_digest"] = "0" * 64
    with pytest.raises(ValueError, match="accepted hash"):
        findings_v2.build_analysis_packet(changed, accepted["manifest"],
                                          accepted["audits"], registry)


@pytest.mark.parametrize("target", ["source", "record", "label", "coverage", "comparison",
                                     "opening", "limitations", "claim"])
def test_coherently_rehashed_packet_tampering_fails(monkeypatch, target):
    packet, _, _, _ = _synthetic_packet(monkeypatch, complementary=True)
    assert findings_v2.validate_analysis_packet(packet) == []
    altered = deepcopy(packet)
    if target == "source":
        altered["source_manifest"]["acceptance"]["numeric_content_digest"] = "0" * 64
    elif target == "record":
        item = next(x for x in altered["record_index"].values() if x["record"]["value"] is not None)
        item["record"]["value"] += 1
    elif target == "label":
        next(iter(altered["record_index"].values()))["display"]["field"] = "Ocupación inventada"
    elif target == "coverage":
        altered["coverage"]["expected_cells"]["national"] += 1
    elif target == "comparison":
        altered["comparisons"][0]["limitations"] = []
    elif target == "opening":
        altered["opening_claim_ids"] = ["v2k:invented"]
    elif target == "limitations":
        altered["limitations"] = []
    else:
        altered["claims"] = [{"claim_id": "v2k:invented", "observation": "Comprobado: 999."}]
    altered["content_digest"] = _digest({k: v for k, v in altered.items() if k != "content_digest"})
    assert findings_v2.validate_analysis_packet(altered)


def test_complementary_parent_stays_null_everywhere(monkeypatch):
    packet, _, _, _ = _synthetic_packet(monkeypatch, complementary=True)
    parents = [x for x in packet["record_index"].values() if x.get("redaction_reason")]
    assert parents and all(x["record"]["value"] is None for x in parents)
    for section in packet["profiles"].values():
        if isinstance(section, list):
            for cell in section:
                if isinstance(cell, dict) and cell.get("record_id") in {x["record_id"] for x in parents}:
                    assert cell["value"] is None
    assert findings_v2.validate_analysis_packet(packet) == []


def test_cyclic_or_nonfinite_packet_is_a_validation_error():
    cyclic = {}
    cyclic["self"] = cyclic
    assert findings_v2.validate_analysis_packet(cyclic)[0]["id"] == "json_scalars"
    assert findings_v2.validate_analysis_packet({"value": float("nan")})[0]["id"] == "json_scalars"


def test_real_accepted_aggregate_packet(monkeypatch):
    base = ROOT / ".cache/research/phase4-acceptance/output"
    sealed = ROOT / ".cache/research/phase4-acceptance/audit/current.json"
    if not sealed.is_file():
        pytest.skip("fresh installed aggregate acceptance unavailable")
    manifest = json.loads(sealed.read_text(encoding="utf-8"))
    publics = {sid: json.loads(path.read_text(encoding="utf-8")) for sid in manifest["snapshots"]
               for path in [base / f"{sid}-public-v2.json"]}
    audits = {sid: json.loads((base / f"{sid}-aggregate.json").read_text(encoding="utf-8"))
              for sid in manifest["snapshots"]}
    registry = load_definition_registry(entity_reference_code="02")
    packet = findings_v2.build_analysis_packet(publics, manifest, audits, registry)
    # The publication handoff is a persisted JSON artifact, not only an in-memory object.
    packet = json.loads(json.dumps(packet, ensure_ascii=False, allow_nan=False))
    assert findings_v2.validate_analysis_packet(packet) == []
    assert len(packet["record_index"]) == 6739
    assert len(packet["comparisons"]) == 4209
    assert len(packet["opening_claim_ids"]) <= 3
    assert all(packet["record_index"][rid]["record"]["value"] is not None
               for claim in packet["claims"] for rid in claim["record_ids"])
    destination = os.environ.get("BRUJULA_SAVE_ACCEPTED_PACKET")
    if destination:
        output = Path(destination)
        output.mkdir(parents=True, exist_ok=True)
        (output / "analysis.json").write_text(
            json.dumps(packet, ensure_ascii=False, sort_keys=True, indent=2) + "\n", encoding="utf-8")
        receipt = {"schema_version": "1.0", "status": "PASS", "synthetic": False,
                   "accepted_numeric_digest": manifest["numeric_content_digest"],
                   "analysis_content_digest": packet["content_digest"],
                   "source_snapshot_ids": sorted(publics), "record_count": len(packet["record_index"]),
                   "comparison_count": len(packet["comparisons"]), "claim_count": len(packet["claims"]),
                   "opening_claim_ids": packet["opening_claim_ids"],
                   "profile_cells": packet["coverage"]["expected_cells"]}
        (output / "receipt.json").write_text(
            json.dumps(receipt, ensure_ascii=False, sort_keys=True, indent=2) + "\n", encoding="utf-8")
