"""Synthetic inventory and failure-state acceptance controls."""

import json

import pytest

from scripts.accept_enoe_estimates import compare_inventory, write_attempt


def test_missing_or_duplicate_evaluation_blocks():
    assert compare_inventory(["a", "b"], ["a"], ["a", "b"])["status"] == "BLOCKED"
    assert compare_inventory(["a"], ["a", "a"], ["a"])["status"] == "BLOCKED"


def test_failure_invalidates_previous_success(tmp_path):
    write_attempt(tmp_path, {"status": "PASS", "digest": "old"})
    write_attempt(tmp_path, {"status": "BLOCKED", "reason": "numerical_failure"})
    assert json.loads((tmp_path / "current.json").read_text())["status"] == "BLOCKED"
    assert not (tmp_path / "current.json").read_text().count("old")
