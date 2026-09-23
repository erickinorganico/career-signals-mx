"""Normalized analytical tables; callers validate the dataset before materializing."""
from __future__ import annotations

from pathlib import Path
import duckdb


def write_warehouse(dataset: dict, path: Path) -> dict:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    if target.exists():
        raise FileExistsError("Warehouse already exists; use a new run directory")
    dims = dataset["dimensions"]
    with duckdb.connect(str(target)) as con:
        con.execute("BEGIN TRANSACTION")

        def table(name, definition, fields, rows):
            con.execute(f"CREATE TABLE {name} ({definition})")
            values = [tuple(row[field] for field in fields) for row in rows]
            if values:
                con.executemany(f"INSERT INTO {name} VALUES ({','.join('?' for _ in fields)})", values)

        for name, key in (("dim_field", "fields"), ("dim_occupation", "occupations"), ("dim_industry", "industries")):
            table(name, "id VARCHAR PRIMARY KEY, label VARCHAR, description VARCHAR",
                  ("id", "label", "description"), dims[key])
        table("dim_geography", "id VARCHAR PRIMARY KEY, label VARCHAR", ("id", "label"), dims["geographies"])
        table("dim_period", "id VARCHAR PRIMARY KEY, label VARCHAR, start_date DATE, end_date DATE",
              ("id", "label", "start", "end"), dims["periods"])
        table("metric", "id VARCHAR PRIMARY KEY, label VARCHAR, unit VARCHAR, description VARCHAR, price_basis VARCHAR",
              ("id", "label", "unit", "description", "price_basis"), dataset["metrics"])
        source_fields = ("id", "name", "url", "terms_url", "license", "authority", "access_status", "approved",
                         "checked_at", "population", "coverage", "periodicity", "methodology", "notes")
        table("source", ", ".join(f"{key} {'BOOLEAN' if key == 'approved' else 'VARCHAR'}" +
                                  (" PRIMARY KEY" if key == "id" else "") for key in source_fields),
              source_fields, dataset["sources"])
        table("evidence", "id VARCHAR PRIMARY KEY, source_id VARCHAR REFERENCES source(id), label VARCHAR, url VARCHAR, kind VARCHAR, note VARCHAR",
              ("id", "source_id", "label", "url", "kind", "note"), dataset["evidence"])
        table("bridge", "id VARCHAR PRIMARY KEY, from_type VARCHAR, from_id VARCHAR, to_type VARCHAR, to_id VARCHAR, method VARCHAR, confidence DOUBLE, status VARCHAR",
              ("id", "from_type", "from_id", "to_type", "to_id", "method", "confidence", "status"), dims["bridges"])
        fields = ("id", "concept_type", "concept_id", "geography_id", "period_id", "metric_id", "value", "source_id",
                  "population", "methodology_id", "unit", "price_basis", "sample_size", "coefficient_variation",
                  "status", "precision_note", "evidence_refs", "synthetic")
        definition = """id VARCHAR PRIMARY KEY, concept_type VARCHAR, concept_id VARCHAR,
            geography_id VARCHAR REFERENCES dim_geography(id), period_id VARCHAR REFERENCES dim_period(id),
            metric_id VARCHAR REFERENCES metric(id), value DOUBLE, source_id VARCHAR REFERENCES source(id),
            population VARCHAR, methodology_id VARCHAR, unit VARCHAR, price_basis VARCHAR,
            sample_size BIGINT, coefficient_variation DOUBLE, status VARCHAR, precision_note VARCHAR,
            evidence_refs VARCHAR[], synthetic BOOLEAN,
            UNIQUE(concept_type, concept_id, geography_id, period_id, metric_id)"""
        table("observation", definition, fields, dataset["observations"])
        for name, rows in (("observation", dataset["observations"]), ("bridge", dims["bridges"])):
            con.execute(f"CREATE TABLE {name}_evidence ({name}_id VARCHAR REFERENCES {name}(id), evidence_id VARCHAR REFERENCES evidence(id), PRIMARY KEY ({name}_id,evidence_id))")
            refs = [(row["id"], ref) for row in rows for ref in row["evidence_refs"]]
            if refs:
                con.executemany(f"INSERT INTO {name}_evidence VALUES (?, ?)", refs)
        count = con.execute("SELECT count(*) FROM observation").fetchone()[0]
        con.execute("COMMIT")
    return {"path": str(target), "observation_count": count}
