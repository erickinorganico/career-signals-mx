"""Read public exports back through all three independent containers."""

import csv
import json
from pathlib import Path

import duckdb
import pytest

from brujula.export_v2 import export_public_tables
from brujula.publication_v2 import build_publication_model


PACKET = Path(__file__).resolve().parents[1] / ".cache/research/phase3-analysis/analysis.json"


@pytest.fixture(scope="module")
def model():
    return build_publication_model(json.loads(PACKET.read_text(encoding="utf-8")))


def test_actual_export_round_trip(model, tmp_path):
    target = tmp_path / "public"
    result = export_public_tables(model, target)
    assert result["counts"]["public_records"] == 6739
    assert len({item["record"]["metric_id"] for item in model["records"].values()}) == 23
    assert all((target / name).is_file() for name in result["files"])
    db = duckdb.connect(str(target / "public.duckdb"), read_only=True)
    db_rows = db.execute("SELECT record_id, value, standard_error, field_of_study_id FROM public_records ORDER BY record_id").fetchall()
    pq_rows = duckdb.query(f"SELECT record_id, value, standard_error, field_of_study_id FROM read_parquet('{(target / 'public-records.parquet').as_posix()}') ORDER BY record_id").fetchall()
    with (target / "public-records.csv").open(encoding="utf-8", newline="") as stream:
        csv_rows = list(csv.DictReader(stream))
    assert len(csv_rows) == len(db_rows) == len(pq_rows) == 6739
    assert db_rows == pq_rows
    assert [row["record_id"] for row in csv_rows] == [row[0] for row in db_rows]
    assert any(row["field_of_study_id"].startswith("0") for row in csv_rows)
    for key, value, se, _field in db_rows:
        record = model["records"][key]["record"]
        assert value == record["value"]
        assert se == record["precision"]["standard_error"]
    assert db.execute("SELECT count(*) FROM figure_record_links").fetchone()[0] > 32
    db.close()


def test_invalid_model_never_creates_output(model, tmp_path):
    malformed = dict(model)
    malformed["internal_estimate"] = 42
    target = tmp_path / "rejected"
    with pytest.raises(ValueError):
        export_public_tables(malformed, target)
    assert not target.exists()
