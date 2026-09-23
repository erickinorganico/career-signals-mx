import json
from pathlib import Path

import duckdb
import pytest
from jsonschema import ValidationError

from brujula.data import load_dataset
from brujula.warehouse import write_warehouse

FIXTURE = Path(__file__).parents[1] / "data" / "fixtures" / "pilot.json"


def test_load_fixture_is_strict_and_keeps_nulls():
    dataset = load_dataset(FIXTURE)
    assert dataset["mode"] == "illustrative"
    assert len(dataset["dimensions"]["fields"]) == 3
    assert len(dataset["observations"]) == 54
    assert len({(r["concept_id"], r["geography_id"], r["period_id"], r["metric_id"]) for r in dataset["observations"]}) == 54
    assert any(row["value"] is None for row in dataset["observations"])


def test_schema_rejects_unknown_properties(tmp_path):
    payload = json.loads(FIXTURE.read_text(encoding="utf-8"))
    payload["unexpected"] = True
    target = tmp_path / "invalid.json"
    target.write_text(json.dumps(payload), encoding="utf-8")
    with pytest.raises(ValidationError):
        load_dataset(target)


@pytest.mark.parametrize("payload", [
    '{"schema_version":"1.0","value":1e999}',
    '{"schema_version":"1.0","schema_version":"1.0"}',
])
def test_loader_rejects_nonfinite_numbers_and_duplicate_keys(tmp_path, payload):
    target = tmp_path / "invalid.json"
    target.write_text(payload, encoding="utf-8")
    with pytest.raises((ValueError, ValidationError)):
        load_dataset(target)


def test_warehouse_materializes_normalized_tables(tmp_path):
    dataset = load_dataset(FIXTURE)
    receipt = write_warehouse(dataset, tmp_path / "pilot.duckdb")
    assert receipt["observation_count"] == len(dataset["observations"])
    con = duckdb.connect(receipt["path"], read_only=True)
    try:
        assert con.execute("select count(*) from dim_field").fetchone()[0] == 3
        assert con.execute("select count(*) from bridge").fetchone()[0] == 1
        assert con.execute("select count(*) from observation where value is null").fetchone()[0] >= 2
    finally:
        con.close()
