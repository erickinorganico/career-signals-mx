from __future__ import annotations

from pathlib import Path
from typing import Any

import duckdb


def write_warehouse(dataset: dict[str, Any], path: Path) -> dict[str, Any]:
    """Materialize the dataset into explicit normalized DuckDB tables."""
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    con = duckdb.connect(str(target))
    try:
        con.execute("CREATE OR REPLACE TABLE dim_field (id VARCHAR PRIMARY KEY, label VARCHAR, description VARCHAR)")
        con.execute("CREATE OR REPLACE TABLE dim_occupation (id VARCHAR PRIMARY KEY, label VARCHAR, description VARCHAR)")
        con.execute("CREATE OR REPLACE TABLE dim_industry (id VARCHAR PRIMARY KEY, label VARCHAR, description VARCHAR)")
        con.execute("CREATE OR REPLACE TABLE dim_geography (id VARCHAR PRIMARY KEY, label VARCHAR)")
        con.execute("CREATE OR REPLACE TABLE dim_period (id VARCHAR PRIMARY KEY, label VARCHAR, start_date DATE, end_date DATE)")
        con.execute("CREATE OR REPLACE TABLE metric (id VARCHAR PRIMARY KEY, label VARCHAR, unit VARCHAR, description VARCHAR, price_basis VARCHAR)")
        con.execute("CREATE OR REPLACE TABLE source (id VARCHAR PRIMARY KEY, name VARCHAR, approved BOOLEAN, authority VARCHAR, access_status VARCHAR)")
        con.execute("CREATE OR REPLACE TABLE bridge (id VARCHAR PRIMARY KEY, from_type VARCHAR, from_id VARCHAR, to_type VARCHAR, to_id VARCHAR, method VARCHAR, confidence DOUBLE, status VARCHAR)")
        con.execute("CREATE OR REPLACE TABLE observation (id VARCHAR PRIMARY KEY, concept_type VARCHAR, concept_id VARCHAR, geography_id VARCHAR, period_id VARCHAR, metric_id VARCHAR, value DOUBLE, source_id VARCHAR, population VARCHAR, methodology_id VARCHAR, unit VARCHAR, price_basis VARCHAR, sample_size INTEGER, coefficient_variation DOUBLE, status VARCHAR, precision_note VARCHAR, synthetic BOOLEAN)")
        d = dataset["dimensions"]
        con.executemany("INSERT INTO dim_field VALUES (?, ?, ?)", [(x["id"], x["label"], x["description"]) for x in d["fields"]])
        con.executemany("INSERT INTO dim_occupation VALUES (?, ?, ?)", [(x["id"], x["label"], x["description"]) for x in d["occupations"]])
        con.executemany("INSERT INTO dim_industry VALUES (?, ?, ?)", [(x["id"], x["label"], x["description"]) for x in d["industries"]])
        con.executemany("INSERT INTO dim_geography VALUES (?, ?)", [(x["id"], x["label"]) for x in d["geographies"]])
        con.executemany("INSERT INTO dim_period VALUES (?, ?, ?, ?)", [(x["id"], x["label"], x["start"], x["end"]) for x in d["periods"]])
        con.executemany("INSERT INTO metric VALUES (?, ?, ?, ?, ?)", [(x["id"], x["label"], x["unit"], x["description"], x["price_basis"]) for x in dataset["metrics"]])
        con.executemany("INSERT INTO source VALUES (?, ?, ?, ?, ?)", [(x["id"], x["name"], x["approved"], x["authority"], x["access_status"]) for x in dataset["sources"]])
        con.executemany("INSERT INTO bridge VALUES (?, ?, ?, ?, ?, ?, ?, ?)", [(x["id"], x["from_type"], x["from_id"], x["to_type"], x["to_id"], x["method"], x["confidence"], x["status"]) for x in d["bridges"]])
        con.executemany("INSERT INTO observation VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", [(x["id"], x["concept_type"], x["concept_id"], x["geography_id"], x["period_id"], x["metric_id"], x["value"], x["source_id"], x["population"], x["methodology_id"], x["unit"], x["price_basis"], x["sample_size"], x["coefficient_variation"], x["status"], x["precision_note"], x["synthetic"]) for x in dataset["observations"]])
        count = con.execute("SELECT count(*) FROM observation").fetchone()[0]
    finally:
        con.close()
    return {"path": str(target), "observation_count": count}
