from copy import deepcopy
from pathlib import Path

import duckdb
import pytest

from brujula.data import load_dataset
from brujula.warehouse import write_warehouse

FIXTURE = Path(__file__).parents[1] / "data/fixtures/pilot.json"


def test_warehouse_preserves_provenance_and_separate_concepts(tmp_path):
    data = load_dataset(FIXTURE)
    path = tmp_path / "tables.duckdb"
    write_warehouse(data, path)
    with duckdb.connect(str(path), read_only=True) as con:
        assert con.execute("SELECT count(*) FROM observation_evidence").fetchone()[0] == sum(len(r["evidence_refs"]) for r in data["observations"])
        assert con.execute("SELECT count(*) FROM evidence").fetchone()[0] == len(data["evidence"])
        assert con.execute("SELECT count(*) FROM observation WHERE concept_type='occupation'").fetchone()[0] == 0
        assert con.execute("SELECT license FROM source").fetchone()[0] == data["sources"][0]["license"]
        assert con.execute("SELECT evidence_refs FROM observation WHERE id=?", [data["observations"][0]["id"]]).fetchone()[0] == data["observations"][0]["evidence_refs"]
    with pytest.raises(FileExistsError):
        write_warehouse(data, path)


def test_empty_optional_dimensions_and_bridges(tmp_path):
    data = deepcopy(load_dataset(FIXTURE))
    for key in ("occupations", "industries", "bridges"):
        data["dimensions"][key] = []
    receipt = write_warehouse(data, tmp_path / "empty.duckdb")
    assert receipt["observation_count"] == len(data["observations"])
