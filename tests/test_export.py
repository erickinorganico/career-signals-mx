import csv
import io
import json
from copy import deepcopy
from datetime import date
from pathlib import Path

import duckdb
import pytest

from brujula.data import load_dataset
from brujula.export import export_csv, write_exports
from brujula.quality import validate_dataset
from brujula.warehouse import write_warehouse

FIXTURE = Path(__file__).parents[1] / "data/fixtures/pilot.json"


def test_csv_values_nulls_evidence_and_formula_safety():
    data = deepcopy(load_dataset(FIXTURE))
    for prefix in ("=", "+", "-", "@", "\t=", "\r+"):
        data["observations"][0]["precision_note"] = prefix + "UNTRUSTED"
        rows = list(csv.DictReader(io.StringIO(export_csv(data))))
        assert rows[0]["precision_note"].startswith("'")
        assert json.loads(rows[0]["evidence_refs"]) == data["observations"][0]["evidence_refs"]
        assert any(r["value"] == "" and r["status"] == "UNKNOWN" for r in rows)


def test_export_round_trip_and_reject_blocked(tmp_path):
    data = load_dataset(FIXTURE)
    quality = validate_dataset(data, as_of=date(2026, 9, 22))
    assert quality["publishable"], quality
    write_warehouse(data, tmp_path / "warehouse.duckdb")
    files = write_exports(data, tmp_path, quality)
    assert json.loads((tmp_path / files["json"]).read_text(encoding="utf-8")) == data
    with duckdb.connect() as con:
        records = con.execute("SELECT id,value,evidence_refs,synthetic FROM read_parquet(?)", [str(tmp_path / files["parquet"])]).fetchall()
    original = {row["id"]: row for row in data["observations"]}
    for ident, value, refs, synthetic in records:
        assert (value, refs, synthetic) == (original[ident]["value"], original[ident]["evidence_refs"], True)
    with pytest.raises(ValueError, match="validated"):
        write_exports(data, tmp_path / "blocked", {**quality, "publishable": False})
    assert not (tmp_path / "blocked").exists()
