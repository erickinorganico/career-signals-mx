"""Machine-proven content mutations against current claim and packet APIs."""

from copy import deepcopy
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from pytest import MonkeyPatch

from brujula import findings_v2
from brujula.analysis_v2 import _digest
from brujula.claims_v2 import make_claim, validate_claim
from brujula.comparisons_v2 import load_definition_registry
from tests.test_analysis_v2 import synthetic_inputs
from tests.test_claims_v2 import _item


def _computed_claim() -> tuple[dict, dict]:
    item = _item()
    index = {item["record_id"]: item}
    claim = make_claim("observation", item["record_id"], public_index=index, comparison_ledger={})
    assert validate_claim(claim, public_index=index, comparison_ledger={}) == []
    return claim, index


def _computed_packet() -> tuple[dict, dict, MonkeyPatch]:
    monkeypatch = MonkeyPatch()
    publics, accepted = synthetic_inputs(monkeypatch, complementary=True)
    registry = load_definition_registry(entity_reference_code="02")
    registry["metric_manifest_sha256"] = accepted["manifest"]["metric_manifest_sha256"]
    monkeypatch.setattr(findings_v2, "load_definition_registry", lambda **_kwargs: deepcopy(registry))
    initial = findings_v2._assemble(publics, accepted["manifest"], accepted["audits"], registry)
    frozen = deepcopy(findings_v2._reference_from_packet(initial))
    monkeypatch.setattr(findings_v2, "_load_reference", lambda: deepcopy(frozen))
    packet = findings_v2.build_analysis_packet(publics, accepted["manifest"], accepted["audits"], registry)
    assert findings_v2.validate_analysis_packet(packet) == []
    return packet, frozen, monkeypatch


def _check_p5(subject: dict) -> None:
    claim, index = _computed_claim()
    if subject["case"] == "p5":
        assert subject["mutation"] == "causal_profession_substitution"
        claim["interpretation"] = "Estudiar Ciencias políticas causó empleo en esa profesión."
        assert validate_claim(claim, public_index=index, comparison_ledger={})
    assert claim["record_ids"] == list(index)
    assert "campo de estudio no identifica la ocupación ejercida" in claim["interpretation"]
    assert validate_claim(claim, public_index=index, comparison_ledger={}) == []


def _check_p6(subject: dict) -> None:
    claim, index = _computed_claim()
    if subject["case"] == "p6":
        assert subject["mutation"] == "advice_new_number_significance"
        claim["observation"] += " Te conviene elegir esta carrera: 99 % de efecto significativo."
        assert validate_claim(claim, public_index=index, comparison_ledger={})
    assert "Te conviene" not in claim["observation"]
    assert "significativo" not in claim["observation"]
    assert validate_claim(claim, public_index=index, comparison_ledger={}) == []


def _check_p7(subject: dict) -> None:
    packet, frozen, monkeypatch = _computed_packet()
    try:
        redacted = next(item for item in packet["record_index"].values()
                        if item.get("redaction_reason") == "complementary_suppression")
        if subject["case"] == "p7":
            assert subject["mutation"] == "activate_source_restore_suppressed"
            source_only = deepcopy(packet)
            source_only["source_manifest"]["sources"][redacted["record"]["source_snapshot_id"]]["status"] = "active"
            source_only["content_digest"] = _digest({key: value for key, value in source_only.items()
                                                       if key != "content_digest"})
            assert findings_v2.validate_analysis_packet(source_only)
            suppressed_only = deepcopy(packet)
            suppressed_only["record_index"][redacted["record_id"]]["record"]["value"] = 3100.0
            suppressed_only["claims"].append({"claim_id": "v2k:proposal", "record_ids": [redacted["record_id"]],
                                              "observation": "Cifra recuperada: 3 100 personas."})
            suppressed_only["content_digest"] = _digest({key: value for key, value in suppressed_only.items()
                                                           if key != "content_digest"})
            assert findings_v2.validate_analysis_packet(suppressed_only)
            source = packet["source_manifest"]["sources"][redacted["record"]["source_snapshot_id"]]
            source["status"] = "active"
            packet["claims"].append({"claim_id": "v2k:proposal", "record_ids": [redacted["record_id"]],
                                     "observation": "Cifra recuperada: 3 100 personas."})
            packet["content_digest"] = _digest({key: value for key, value in packet.items()
                                                 if key != "content_digest"})
            assert findings_v2.validate_analysis_packet(packet)
        assert all("status" not in source for source in packet["source_manifest"]["sources"].values())
        assert redacted["record"]["value"] is None
        assert all(redacted["record_id"] not in claim["record_ids"] for claim in packet["claims"])
        assert findings_v2._reference_from_packet(packet) == frozen
        assert findings_v2.validate_analysis_packet(packet) == []
    finally:
        monkeypatch.undo()


def main(case: str, subject_path: str) -> None:
    subject = json.loads((ROOT / subject_path).read_text(encoding="utf-8"))
    assert subject["synthetic"] is True and subject["case"] in ("clean", "p5", "p6", "p7")
    {"p5": _check_p5, "p6": _check_p6, "p7": _check_p7}[case](subject)
    print("checked current Phase 3 claim and packet APIs (synthetic fixture)")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
