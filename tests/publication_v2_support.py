"""Compact independently pinned Phase 3 packet for portable publication tests."""

from copy import deepcopy

from brujula import findings_v2
from brujula.comparisons_v2 import load_definition_registry
from tests.test_analysis_v2 import synthetic_inputs


def pinned_synthetic_packet(monkeypatch, *, complementary: bool = True) -> dict:
    """Build through the Phase 3 public path, then freeze its independent test pins."""
    publics, accepted = synthetic_inputs(monkeypatch, complementary=complementary)
    registry = load_definition_registry(entity_reference_code="02")
    registry["metric_manifest_sha256"] = accepted["manifest"]["metric_manifest_sha256"]
    monkeypatch.setattr(findings_v2, "load_definition_registry", lambda **_kwargs: deepcopy(registry))
    candidate = findings_v2._assemble(publics, accepted["manifest"], accepted["audits"], registry)
    frozen = deepcopy(findings_v2._reference_from_packet(candidate))
    monkeypatch.setattr(findings_v2, "_load_reference", lambda: deepcopy(frozen))
    packet = findings_v2.build_analysis_packet(publics, accepted["manifest"], accepted["audits"], registry)
    assert findings_v2.validate_analysis_packet(packet) == []
    return packet
