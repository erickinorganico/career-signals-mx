"""Read public exports back through all three independent containers."""

import csv
import json
from pathlib import Path

import duckdb
import pytest

from brujula.export_v2 import export_public_tables
from brujula.export_v2 import _csv_value
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
    for csv_row, (key, value, se, _field) in zip(csv_rows, db_rows):
        record = model["records"][key]["record"]
        assert value == record["value"]
        assert se == record["precision"]["standard_error"]
        assert (None if csv_row["value"] == "" else float(csv_row["value"])) == value
        assert (None if csv_row["standard_error"] == "" else float(csv_row["standard_error"])) == se
        assert csv_row["status"] == record["status"]
        assert csv_row["reason"] == (record["reason"] or "")
    assert db.execute("SELECT count(*) FROM figure_record_links").fetchone()[0] > 32
    assert db.execute("SELECT count(DISTINCT metric_id) FROM public_records").fetchone()[0] == 23
    assert db.execute("SELECT count(*) FROM record_evidence").fetchone()[0] >= 6739
    db.close()


def test_invalid_model_never_creates_output(model, tmp_path):
    malformed = dict(model)
    malformed["internal_estimate"] = 42
    target = tmp_path / "rejected"
    with pytest.raises(ValueError):
        export_public_tables(malformed, target)
    assert not target.exists()


def test_interrupted_export_leaves_no_declared_set(model, tmp_path, monkeypatch):
    def interrupted(_path):
        raise OSError("interrupted before seal")

    monkeypatch.setattr("brujula.export_v2.duckdb.connect", interrupted)
    target = tmp_path / "interrupted"
    with pytest.raises(OSError, match="interrupted"):
        export_public_tables(model, target)
    assert not target.exists()
    assert not list(tmp_path.glob(".public-export-*"))


@pytest.mark.parametrize("source,encoded", [
    ("=SUM(1,2)", "'=SUM(1,2)"), ("+cmd", "'+cmd"),
    ("-cmd", "'-cmd"), ("@cmd", "'@cmd"),
    ("031300", "031300"), ("México", "México"),
    (0.0, 0.0), (None, ""),
])
def test_csv_text_convention_and_zero_null(source, encoded):
    assert _csv_value(source) == encoded
