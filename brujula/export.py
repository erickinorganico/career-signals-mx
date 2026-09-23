"""Deterministic exports from validated data; publication still requires the run commit."""
from __future__ import annotations

import csv
import io
import json
from datetime import date
from pathlib import Path

import duckdb

FIELDS = ("id", "concept_type", "concept_id", "geography_id", "period_id", "metric_id", "value", "unit",
          "price_basis", "status", "source_id", "population", "methodology_id", "synthetic", "sample_size",
          "coefficient_variation", "precision_note", "evidence_refs")


def export_csv(dataset: dict) -> str:
    """Missing numbers are empty; JSON ref arrays round-trip without delimiter ambiguity."""
    buffer = io.StringIO(newline="")
    writer = csv.DictWriter(buffer, fieldnames=FIELDS, lineterminator="\n")
    writer.writeheader()
    for observation in dataset["observations"]:
        row = {key: observation[key] for key in FIELDS}
        row["evidence_refs"] = json.dumps(row["evidence_refs"], ensure_ascii=False)
        for key, value in row.items():
            if isinstance(value, str) and value.lstrip().startswith(("=", "+", "-", "@")):
                row[key] = "'" + value
        writer.writerow(row)
    return buffer.getvalue()


def write_exports(dataset: dict, output: Path, quality: dict) -> dict:
    from .quality import validate_dataset

    as_of = date.fromisoformat(quality["freshness"]["as_of"])
    if not quality.get("publishable") or not validate_dataset(dataset, as_of=as_of)["publishable"]:
        raise ValueError("Exports require a currently validated, publishable dataset")
    output = Path(output)
    warehouse = output / "warehouse.duckdb"
    if not warehouse.is_file():
        raise ValueError("Validated warehouse required before exports")
    csv_path = output / "observations.csv"
    parquet_path = output / "observations.parquet"
    json_path = output / "observations.json"
    if any(p.exists() for p in (csv_path, parquet_path, json_path)):
        raise FileExistsError("Export already exists; use a new run directory")
    # JSON retains the full contract, including dimensions and evidence lookups.
    json_path.write_text(json.dumps(dataset, ensure_ascii=False, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    csv_path.write_text(export_csv(dataset), encoding="utf-8-sig", newline="")
    with duckdb.connect(str(warehouse), read_only=True) as con:
        target = str(parquet_path).replace("'", "''")
        con.execute(f"COPY (SELECT {','.join(FIELDS)} FROM observation ORDER BY id) TO '{target}' (FORMAT PARQUET)")
    return {"csv": csv_path.name, "parquet": parquet_path.name, "json": json_path.name}
