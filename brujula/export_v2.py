"""Typed, joined aggregate exports from the independently pinned public model."""

from __future__ import annotations

import csv
import os
from pathlib import Path
import shutil
import tempfile

import duckdb

from .publication_v2 import validate_publication_model


RECORD_COLUMNS = {
    "record_id": "VARCHAR PRIMARY KEY", "source_snapshot_id": "VARCHAR", "population_id": "VARCHAR",
    "field_of_study_id": "VARCHAR", "occupation_id": "VARCHAR", "industry_id": "VARCHAR",
    "geography_id": "VARCHAR", "recorded_sex_id": "VARCHAR", "period_id": "VARCHAR",
    "metric_id": "VARCHAR", "method_id": "VARCHAR", "value": "DOUBLE", "unit": "VARCHAR",
    "price_basis": "VARCHAR", "status": "VARCHAR", "reason": "VARCHAR", "sample_size": "BIGINT",
    "weighted_denominator": "DOUBLE", "weighted_support_total": "DOUBLE",
    "n_psu_design": "BIGINT", "n_strata_design": "BIGINT", "n_psu_domain": "BIGINT",
    "n_strata_domain": "BIGINT", "design_df": "BIGINT", "standard_error": "DOUBLE",
    "coefficient_variation": "DOUBLE", "ci90_lower": "DOUBLE", "ci90_upper": "DOUBLE",
    "ci_method": "VARCHAR", "precision_method": "VARCHAR", "precision_level": "DOUBLE",
    "singleton_policy": "VARCHAR", "official_precision": "BOOLEAN", "method_version": "VARCHAR",
    "design_id": "VARCHAR", "source_sha256": "VARCHAR", "synthetic": "BOOLEAN",
    "redaction_reason": "VARCHAR", "field_label": "VARCHAR", "population_label": "VARCHAR",
    "metric_label": "VARCHAR", "geography_label": "VARCHAR", "recorded_sex_label": "VARCHAR",
}

COMPARISON_COLUMNS = {
    "comparison_id": "VARCHAR PRIMARY KEY", "previous_record_id": "VARCHAR", "current_record_id": "VARCHAR",
    "comparison_type": "VARCHAR", "status": "VARCHAR", "comparable": "BOOLEAN",
    "absolute_change": "DOUBLE", "relative_change_pct": "DOUBLE", "display_unit": "VARCHAR",
    "reasons": "VARCHAR", "limitations": "VARCHAR", "source_snapshot_ids": "VARCHAR",
    "source_sha256s": "VARCHAR", "slot_periods": "VARCHAR",
}

CLAIM_COLUMNS = {
    "claim_id": "VARCHAR PRIMARY KEY", "kind": "VARCHAR", "subject_id": "VARCHAR",
    "comparison_id": "VARCHAR", "metric_id": "VARCHAR", "population_id": "VARCHAR",
    "title": "VARCHAR", "observation": "VARCHAR", "interpretation": "VARCHAR",
    "limitation": "VARCHAR", "synthetic": "BOOLEAN", "current_value": "DOUBLE",
    "previous_value": "DOUBLE", "absolute_change": "DOUBLE", "unit": "VARCHAR",
    "display_unit": "VARCHAR",
}

FIGURE_COLUMNS = {"figure_id": "VARCHAR PRIMARY KEY", "table_id": "VARCHAR"}
LINK_COLUMNS = {"figure_id": "VARCHAR", "record_id": "VARCHAR"}


def _record_rows(model: dict) -> list[tuple]:
    rows = []
    for rid, item in sorted(model["records"].items()):
        row, support, precision, display = (item["record"], item["record"]["support"],
                                            item["record"]["precision"], item["display"])
        values = {**row, **support, **precision,
                  "record_id": rid, "weighted_support_total": support["weighted_support_total"],
                  "precision_method": precision["method"], "precision_level": precision["level"],
                  "source_sha256": item["snapshot_sha256"],
                  "redaction_reason": item.get("redaction_reason"),
                  **{name + "_label": display[name] for name in
                     ("field", "population", "metric", "geography", "recorded_sex")}}
        rows.append(tuple(values.get(name) for name in RECORD_COLUMNS))
    return rows


def _table_data(model: dict) -> dict[str, tuple[dict[str, str], list[tuple]]]:
    tables: dict[str, tuple[dict[str, str], list[tuple]]] = {}
    tables["public_records"] = (RECORD_COLUMNS, _record_rows(model))
    tables["comparisons"] = (COMPARISON_COLUMNS, [tuple({**entry,
        "reasons": "|".join(entry["reasons"]),
        "limitations": "|".join(entry["limitations"]),
        "source_snapshot_ids": "|".join(entry["source_snapshot_ids"]),
        "source_sha256s": "|".join(entry["source_sha256s"]),
        "slot_periods": "|".join(entry["slot_periods"])}.get(name)
        for name in COMPARISON_COLUMNS) for entry in sorted(model["comparisons"], key=lambda e: e["comparison_id"])])
    tables["claims"] = (CLAIM_COLUMNS, [tuple({**claim, **claim["quantities"]}.get(name)
        for name in CLAIM_COLUMNS) for claim in sorted(model["claims"], key=lambda c: c["claim_id"])])
    tables["figures"] = (FIGURE_COLUMNS, [(f["figure_id"], f["table_id"])
        for f in sorted(model["figure_links"], key=lambda f: f["figure_id"])])
    for suffix, field, key in (("record", "record_ids", "record_id"),
                               ("comparison", "comparison_ids", "comparison_id"),
                               ("claim", "claim_ids", "claim_id"),
                               ("source", "source_ids", "source_snapshot_id")):
        tables[f"figure_{suffix}_links"] = ({"figure_id": "VARCHAR", key: "VARCHAR"},
            [(figure["figure_id"], identifier) for figure in sorted(model["figure_links"],
                key=lambda f: f["figure_id"]) for identifier in figure[field]])
    tables["claim_record_links"] = ({"claim_id": "VARCHAR", "record_id": "VARCHAR"},
        [(claim["claim_id"], rid) for claim in sorted(model["claims"], key=lambda c: c["claim_id"])
         for rid in claim["record_ids"]])
    for name, entries, id_key, evidence_key in (
        ("record_evidence", model["records"].items(), "record_id", "record"),
        ("comparison_evidence", ((c["comparison_id"], c) for c in model["comparisons"]),
         "comparison_id", None),
        ("claim_evidence", ((c["claim_id"], c) for c in model["claims"]),
         "claim_id", None)):
        tables[name] = ({id_key: "VARCHAR", "evidence_ref": "VARCHAR"},
            [(identifier, ref) for identifier, entry in sorted(entries)
             for ref in (entry[evidence_key]["evidence_refs"] if evidence_key else entry["evidence_refs"])])
    dims = (("sources", "source_snapshot_id", "period_id", "sha256", "url", "method_version"),
            ("populations", "population_id", "population_label"),
            ("fields", "field_of_study_id", "field_label"),
            ("occupations", "occupation_id"), ("industries", "industry_id"),
            ("geographies", "geography_id", "geography_label"),
            ("recorded_sexes", "recorded_sex_id", "recorded_sex_label"),
            ("periods", "period_id"),
            ("metrics", "metric_id", "metric_label", "unit", "price_basis"),
            ("methods", "method_id", "method_version"))
    records = [dict(zip(RECORD_COLUMNS, row)) for row in tables["public_records"][1]]
    for dim in dims:
        table, *columns = dim
        if table == "sources":
            rows = sorted((sid, src["period_id"], src["sha256"], src["url"], src["method_version"])
                          for sid, src in model["source_manifest"]["sources"].items())
        else:
            rows = sorted({tuple(row[column] for column in columns) for row in records})
        tables[table] = ({name: "VARCHAR" for name in columns}, rows)
    return tables


def _csv_value(value: object) -> object:
    if value is None:
        return ""
    if isinstance(value, str) and value.startswith(("=", "+", "-", "@", "'")):
        return "'" + value
    return value


def _dictionary(tables: dict) -> str:
    special = {
        "record_id": "Stable v2r key over ten distinct grain components; joins claims, comparisons and figures.",
        "comparison_id": "Stable v2c comparison key; endpoints join public_records.record_id.",
        "claim_id": "Stable v2k accepted claim key; record evidence joins through claim_record_links.",
        "figure_id": "Declared figure key; joins figure_record_links, figure_comparison_links and figure_claim_links.",
        "sample_size": "Observed sample count (n), not a weighted population total.",
        "weighted_denominator": "Estimated weighted denominator; null for suppressed or unsupported rows.",
        "weighted_support_total": "Estimated weighted support, distinct from observed n; null when suppressed.",
        "value": "Unrounded canonical public numeric value. Null is unavailable, distinct from zero.",
        "standard_error": "Project approximation, not official INEGI precision; null when unavailable.",
        "coefficient_variation": "Project CV; null when unavailable or suppressed.",
        "ci90_lower": "Project 90% lower bound; null when unavailable or suppressed.",
        "ci90_upper": "Project 90% upper bound; null when unavailable or suppressed.",
        "price_basis": "Nominal income or not_applicable; never inflation adjusted.",
        "status": "Public MEASURED/REVIEW/UNKNOWN/BLOCKED classification; read with reason.",
        "reason": "Public reason for limitation or missing value; CSV blank represents SQL null.",
        "field_of_study_id": "Text classification code; leading zeros are significant.",
        "geography_id": "Text geography code; leading zeros are significant.",
    }
    lines = ["# Brújula Laboral MX public data dictionary", "",
             "All tables derive from the independently pinned Phase 3 sanitized public packet.",
             "CSV is UTF-8. Empty CSV numeric/text fields represent SQL NULL; the literal numeric zero remains 0.",
             "CSV text beginning `=`, `+`, `-` or `@` gains one leading apostrophe; text already beginning `'` gains a second apostrophe. Decode by removing one apostrophe only from CSV text beginning `'=`, `'+`, `'-`, `'@` or `''`. DuckDB and Parquet keep the original string.",
             "Public values retain full binary floating precision. Display rounding belongs to report formatters only.",
             "The 10 grain columns of public_records remain separate; v2r is their canonical identity.",
             "Evidence refs are relational rows. Source snapshot hashes and method versions preserve provenance.", ""]
    for table, (columns, _) in tables.items():
        lines.extend((f"## {table}", "", "| Column | DuckDB type | Meaning |", "|---|---|---|"))
        for name, typ in columns.items():
            lines.append(f"| `{name}` | `{typ}` | {special.get(name, 'Public ' + name.replace('_', ' ') + '; nullable where source evidence is unavailable.')} |")
        lines.append("")
    return "\n".join(lines)


def export_public_tables(model: dict, output_dir: str | Path) -> dict:
    """Validate before I/O, stage all formats, then atomically expose one directory."""
    errors = validate_publication_model(model)
    if errors:
        raise ValueError(f"Public model rejected: {errors[:3]}")
    target = Path(output_dir)
    if target.exists():
        raise FileExistsError(f"export target already exists: {target}")
    target.parent.mkdir(parents=True, exist_ok=True)
    stage = Path(tempfile.mkdtemp(prefix=".public-export-", dir=target.parent))
    files = []
    db = None
    try:
        tables = _table_data(model)
        db = duckdb.connect(str(stage / "public.duckdb"))
        db.execute("BEGIN TRANSACTION")
        for name, (columns, rows) in tables.items():
            db.execute(f"CREATE TABLE {name} (" + ", ".join(f"{key} {typ}" for key, typ in columns.items()) + ")")
            if rows:
                load_path = stage / f".{name}.load.csv"
                with load_path.open("w", encoding="utf-8", newline="") as stream:
                    writer = csv.writer(stream)
                    writer.writerow(columns)
                    writer.writerows(tuple(r"\N" if value is None else value for value in row)
                                    for row in rows)
                literal = load_path.as_posix().replace("'", "''")
                db.execute(f"COPY {name} FROM '{literal}' (FORMAT CSV, HEADER TRUE, NULL '\\N')")
                load_path.unlink()
        db.execute("COMMIT")
        for name, (columns, rows) in tables.items():
            stem = "public-records" if name == "public_records" else name.replace("_", "-")
            csv_path = stage / f"{stem}.csv"
            with csv_path.open("w", encoding="utf-8", newline="") as stream:
                writer = csv.writer(stream)
                writer.writerow(columns)
                writer.writerows(tuple(_csv_value(value) for value in row) for row in rows)
            files.append(csv_path.name)
            parquet_path = stage / f"{stem}.parquet"
            literal = parquet_path.as_posix().replace("'", "''")
            db.execute(f"COPY (SELECT * FROM {name} ORDER BY 1) TO '{literal}' (FORMAT PARQUET)")
            files.append(parquet_path.name)
        db.close()
        db = None
        files.append("public.duckdb")
        (stage / "data-dictionary.md").write_text(_dictionary(tables), encoding="utf-8")
        files.append("data-dictionary.md")
        os.replace(stage, target)
    except BaseException:
        if db is not None:
            db.close()
        shutil.rmtree(stage, ignore_errors=True)
        raise
    return {"files": sorted(files), "counts": {name: len(rows) for name, (_, rows) in tables.items()}}
