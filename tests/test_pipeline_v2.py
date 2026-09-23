"""Sealed v2 publication boundary checks."""

from pathlib import Path

import pytest


def test_v2_publication_service_exists():
    from brujula import pipeline_v2

    assert callable(pipeline_v2.build_publication)
    assert callable(pipeline_v2.resolve_publication_current)
    assert callable(pipeline_v2.analyze_acceptance)
    assert callable(pipeline_v2.replay_publication)


def test_unsafe_roots_rejected_before_writes(tmp_path: Path):
    from brujula.pipeline_v2 import build_publication

    root = tmp_path / "source"
    with pytest.raises(ValueError, match="overlap"):
        build_publication(root, root / "publication", tmp_path / "audit", tmp_path / "analysis.json")
    assert not root.exists()
