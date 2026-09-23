"""Read public exports back through all three independent containers."""

import csv
import json
from pathlib import Path

import duckdb
import pytest

from brujula.export_v2 import export_public_tables
from brujula.export_v2 import _csv_value
from brujula.publication_v2 import build_publication_model
from tests.publication_v2_support import pinned_synthetic_packet


PACKET = Path(__file__).resolve().parents[1] / ".cache/research/phase3-analysis/analysis.json"


@pytest.fixture
def synthetic_packet(monkeypatch):
    return pinned_synthetic_packet(monkeypatch)


@pytest.fixture
def model(synthetic_packet):
    return build_publication_model(synthetic_packet)


@pytest.fixture(scope="module")
def real_packet():
    if not PACKET.is_file():
        pytest.skip("optional persisted real Phase 3 packet is unavailable")
    return json.loads(PACKET.read_text(encoding="utf-8"))


def test_actual_export_round_trip(real_packet, tmp_path):
    model = build_publication_model(real_packet)
    target = tmp_path / "public"
    result = export_public_tables(model, target)
    assert result["counts"]["public_records"] == 6739
    assert len({item["record"]["metric_id"] for item in model["records"].values()}) == 23
    assert all((target / name).is_file() for name in result["files"])
    db = duckdb.connect(str(target / "public.duckdb"), read_only=True)
    db_rows = db.execute("SELECT * FROM public_records ORDER BY record_id").fetchall()
    columns = [column[0] for column in db.description]
    pq_rows = duckdb.query(f"SELECT * FROM read_parquet('{(target / 'public-records.parquet').as_posix()}') ORDER BY record_id").fetchall()
    with (target / "public-records.csv").open(encoding="utf-8", newline="") as stream:
        csv_rows = list(csv.DictReader(stream))
    assert len(csv_rows) == len(db_rows) == len(pq_rows) == 6739
    assert db_rows == pq_rows
    assert [row["record_id"] for row in csv_rows] == [row[0] for row in db_rows]
    assert any(row["field_of_study_id"].startswith("0") for row in csv_rows)
    for csv_row, db_row in zip(csv_rows, db_rows):
        typed = dict(zip(columns, db_row))
        key, value, se = typed["record_id"], typed["value"], typed["standard_error"]
        record = model["records"][key]["record"]
        assert value == record["value"]
        assert se == record["precision"]["standard_error"]
        for column, db_value in typed.items():
            assert csv_row[column] == ("" if db_value is None else str(_csv_value(db_value)))
        assert csv_row["status"] == record["status"]
        assert csv_row["reason"] == (record["reason"] or "")
    assert db.execute("SELECT count(*) FROM figure_record_links").fetchone()[0] > 32
    assert db.execute("SELECT count(DISTINCT metric_id) FROM public_records").fetchone()[0] == 23
    assert db.execute("SELECT count(*) FROM comparisons").fetchone()[0] == 4209
    assert db.execute("SELECT count(*) FROM claims").fetchone()[0] == 38
    assert db.execute("SELECT count(*) FROM record_evidence").fetchone()[0] >= 6739
    _assert_comparison_parity(real_packet, target, db)
    db.close()


def _canonical(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True,
                      separators=(",", ":"), allow_nan=False)


def _assert_comparison_parity(packet, target, db):
    rows = db.execute("SELECT * FROM comparisons ORDER BY comparison_id").fetchall()
    columns = [item[0] for item in db.description]
    parquet = duckdb.query(f"SELECT * FROM read_parquet('{(target / 'comparisons.parquet').as_posix()}') ORDER BY comparison_id").fetchall()
    with (target / "comparisons.csv").open(encoding="utf-8", newline="") as stream:
        csv_rows = list(csv.DictReader(stream))
    assert rows == parquet
    assert len(rows) == len(packet["comparisons"])
    expected = {item["comparison_id"]: item for item in packet["comparisons"]}
    for csv_row, row in zip(csv_rows, rows):
        exported = dict(zip(columns, row))
        source = expected[exported["comparison_id"]]
        assert set(source) - set(columns) == {"evidence_refs"}
        for column, value in exported.items():
            if column in ("signature_previous", "signature_current", "reasons", "limitations",
                          "source_snapshot_ids", "source_sha256s", "slot_periods"):
                assert value == _canonical(source[column])
                assert json.loads(value) == source[column]
            else:
                assert value == source[column]
            assert csv_row[column] == ("" if value is None else str(_csv_value(value)))
    evidence = db.execute("SELECT comparison_id, evidence_ref FROM comparison_evidence ORDER BY comparison_id, evidence_ref").fetchall()
    assert evidence == sorted((item["comparison_id"], ref)
                              for item in packet["comparisons"] for ref in item["evidence_refs"])


def test_compact_pinned_packet_exports_lossless_comparisons(synthetic_packet, model, tmp_path):
    target = tmp_path / "synthetic"
    inventory = export_public_tables(model, target)
    assert inventory["counts"]["public_records"] == len(synthetic_packet["record_index"])
    assert all((target / name).is_file() for name in inventory["files"])
    db = duckdb.connect(str(target / "public.duckdb"), read_only=True)
    _assert_comparison_parity(synthetic_packet, target, db)
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
    ("'=literal", "''=literal"), ("'ordinary", "''ordinary"),
    ("031300", "031300"), ("México", "México"),
    (0.0, 0.0), (None, ""),
])
def test_csv_text_convention_and_zero_null(source, encoded):
    assert _csv_value(source) == encoded
