"""Pinned ENOE 2025-Q2 official aggregate comparison, without microdata output."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import re
import sys
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from brujula.acquisition import resolve_snapshot
from brujula.estimates import METHOD_ID
from brujula.research_contract import validate_public_research_v2, validate_research_v2
from brujula.source_inventory import inventory_snapshot

WORKBOOK_SHA256 = "21b45fb76a3f2df336529c3c9ac5cf7543c7d1ded477cc21f77bcc2db8ba267c"
SOURCE_SHA256 = "9530a017e3defb0658418b73a47a6039eeb54abf11342fa10693374736515127"
SNAPSHOT = "enoe_2025_q2"
HEADERS = {"I": "Clave_Entidad", "J": "Nombre_Entidad", "N": "Variable",
           "O": "Parametro", "P": "Estimación", "Q": "CV", "R": "ErrorEst",
           "S": "Niv_Conf", "T": "IntConf_Inf", "U": "IntConf_Sup"}
LABELS = {"Población de 15 años y más": "population_total",
          "Población económicamente activa (PEA)": "pea_total",
          "Población Desocupada": "unemployed_total",
          "Tasa de desocupación": "unemployment_rate"}
COUNT_EXPECTED = {"mx|population_total": 102615200, "mx|pea_total": 61065005,
                  "mx|unemployed_total": 1624245, "02|population_total": 3014248,
                  "02|pea_total": 1790619, "02|unemployed_total": 41435}
RATE_EXPECTED = {"mx|unemployment_rate": 2.6599, "02|unemployment_rate": 2.3140}
RATE_HALF_UNIT = 0.00005
STRICT_POINT_TOLERANCE = 1e-6
PDF_2026_Q2_SHA256 = "74cfc4f19f98ea25ba20d0e0dc70557855050cc3399bbdc25dd46e066a0b8fca"
PDF_2026_Q2_URL = "https://www.inegi.org.mx/contenidos/saladeprensa/boletines/2026/enoe/enoe2026_08.pdf"
PDF_2026_Q2_COUNTS = {"population_total": 104305022, "pea_total": 61676698,
                      "occupied_total": 60040094, "unemployed_total": 1636604,
                      "pnea_total": 42628324}
NS = "{http://schemas.openxmlformats.org/spreadsheetml/2006/main}"


def _numeric(raw: str) -> float:
    if not re.fullmatch(r"[+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][+-]?\d+)?", raw):
        raise ValueError("official numeric cell is invalid")
    value = float(raw)
    if not math.isfinite(value):
        raise ValueError("official numeric cell is nonfinite")
    return value


def workbook_cells(path: Path) -> dict[str, dict]:
    if hashlib.sha256(path.read_bytes()).hexdigest() != WORKBOOK_SHA256:
        raise ValueError("official workbook SHA-256 mismatch")
    with zipfile.ZipFile(path) as archive:
        strings_root = ET.fromstring(archive.read("xl/sharedStrings.xml"))
        strings = ["".join(t.text or "" for t in item.iter(NS + "t"))
                   for item in strings_root.findall(NS + "si")]
        sheets = ET.fromstring(archive.read("xl/workbook.xml"))
        names = [item.attrib.get("name") for item in sheets.iter(NS + "sheet")]
        if not names or names[0] != "INDICADORES":
            raise ValueError("official workbook edition/sheet mismatch")
        sheet = ET.fromstring(archive.read("xl/worksheets/sheet1.xml"))
    rows = []
    for row in sheet.iter(NS + "row"):
        cells = {}
        for cell in row.findall(NS + "c"):
            col = re.match(r"[A-Z]+", cell.attrib["r"]).group()
            value = cell.find(NS + "v")
            raw = "" if value is None else value.text or ""
            if cell.attrib.get("t") == "s" and raw:
                raw = strings[int(raw)]
            cells[col] = raw
        rows.append(cells)
    if not rows or any(rows[0].get(col) != label for col, label in HEADERS.items()):
        raise ValueError("official workbook headers mismatch")
    result = {}
    for row in rows[1:]:
        geo = {"00": "mx", "02": "02"}.get(row.get("I", "").zfill(2))
        metric = LABELS.get(row.get("N"))
        kind = {"Total": "count", "Tasa": "rate"}.get(row.get("O"))
        if geo is None or metric is None or kind is None:
            continue
        if kind != ("rate" if metric == "unemployment_rate" else "count"):
            raise ValueError("official parameter/universe mismatch")
        key = f"{geo}|{metric}"
        if key in result:
            raise ValueError("duplicate official cell")
        result[key] = {"estimate": _numeric(row["P"]),
                       "standard_error": _numeric(row["R"]), "kind": kind,
                       "confidence_level": _numeric(row["S"])}
    if set(result) != set(COUNT_EXPECTED) | set(RATE_EXPECTED):
        raise ValueError("official cell inventory incomplete")
    if any(result[key]["estimate"] != value for key, value in (COUNT_EXPECTED | RATE_EXPECTED).items()):
        raise ValueError("official workbook edition or universe mismatch")
    return result


def compare_official_cells(official: dict, computed: dict) -> dict:
    if set(official) != set(computed) or not official:
        return {"status": "BLOCKED", "reason": "missing_or_extra_official_cell", "cells": {}}
    ledger = {}
    for key in sorted(official):
        expected, actual = official[key], computed[key]
        p, se = actual.get("estimate"), actual.get("standard_error")
        official_p, official_se = expected["estimate"], expected["standard_error"]
        if not all(type(v) in (int, float) and math.isfinite(v) for v in (p, se, official_p, official_se)):
            return {"status": "BLOCKED", "reason": "nonfinite_or_missing_numeric_cell", "cells": ledger}
        difference = p - official_p
        se_difference = se - official_se
        exact = difference == 0
        interval = abs(difference) <= RATE_HALF_UNIT + 1e-14 if expected["kind"] == "rate" else exact
        ledger[key] = {"kind": expected["kind"], "official_estimate": official_p,
                       "project_estimate": p, "point_signed_difference": difference,
                       "strict_original_point_match": abs(difference) <= STRICT_POINT_TOLERANCE,
                       "point_match": interval, "official_standard_error": official_se,
                       "project_standard_error": se, "se_signed_difference": se_difference,
                       "se_relative_difference": se_difference / official_se if official_se else None,
                       "official_precision": False}
    return {"status": "PASS" if all(x["point_match"] for x in ledger.values()) else "BLOCKED",
            "cells": ledger, "precision_status": "REVIEW",
            "precision_note": "Project Taylor singleton adjustment; untuned official SE differences retained"}


def reconcile(output_root: Path, workbook: Path, records: list[dict]) -> dict:
    path, receipt = resolve_snapshot(SNAPSHOT, output_root)
    inventory = inventory_snapshot(SNAPSHOT, output_root)
    if receipt["sha256"] != SOURCE_SHA256 or inventory["raw_sha256"] != SOURCE_SHA256:
        raise ValueError("official comparison source SHA-256 mismatch")
    if not path.is_file():
        raise ValueError("pinned source missing")
    official = workbook_cells(workbook)
    computed = {}
    for record in records:
        if record["source_snapshot_id"] != SNAPSHOT or record["population_id"] != "national_15_plus_context":
            continue
        if record["field_of_study_id"] != "all" or record["recorded_sex_id"] != "all":
            continue
        if (record["period_id"] != "2025-Q2" or record["occupation_id"] != "all"
                or record["industry_id"] != "all" or record["method_id"] != METHOD_ID):
            raise ValueError("official comparison period, universe or method mismatch")
        key = f"{record['geography_id']}|{record['metric_id']}"
        if key in official:
            if key in computed:
                raise ValueError("duplicate project official comparison cell")
            computed[key] = {"estimate": record["estimate"],
                             "standard_error": record["precision"]["standard_error"]}
    ledger = compare_official_cells(official, computed)
    ledger.update({"snapshot_id": SNAPSHOT, "source_sha256": SOURCE_SHA256,
                   "workbook_sha256": WORKBOOK_SHA256,
                   "workbook_url": "https://www.inegi.org.mx/rnm/index.php/catalog/1121/download/35892",
                   "edition": "ENOE 2025-Q2, población de 15 años y más, INDICADORES",
                   "rounding_half_unit": RATE_HALF_UNIT})
    return ledger


def check_2026_pdf_benchmark(pdf: Path, records: list[dict]) -> dict:
    """Check pinned official national context totals; the PDF is a distinct edition."""
    if hashlib.sha256(pdf.read_bytes()).hexdigest() != PDF_2026_Q2_SHA256:
        raise ValueError("2026-Q2 official PDF SHA-256 mismatch")
    selected = {}
    for row in records:
        if (row["source_snapshot_id"] != "enoe_2026_q2"
                or row["population_id"] != "national_15_plus_context"
                or row["field_of_study_id"] != "all" or row["geography_id"] != "mx"
                or row["recorded_sex_id"] != "all"):
            continue
        if (row["period_id"] != "2026-Q2" or row["occupation_id"] != "all"
                or row["industry_id"] != "all" or row["method_id"] != METHOD_ID):
            raise ValueError("2026-Q2 PDF comparison period, universe or method mismatch")
        if row["metric_id"] in selected:
            raise ValueError("duplicate 2026-Q2 PDF comparison metric")
        selected[row["metric_id"]] = row
    cells = {}
    for metric, official in PDF_2026_Q2_COUNTS.items():
        if metric == "pnea_total":
            if not {"population_total", "pea_total"} <= selected.keys():
                raise ValueError("2026-Q2 PDF comparison missing PNEA components")
            project = selected["population_total"]["estimate"] - selected["pea_total"]["estimate"]
        else:
            if metric not in selected:
                raise ValueError("2026-Q2 PDF comparison missing national metric")
            project = selected[metric]["estimate"]
        if type(project) not in (int, float) or not math.isfinite(project):
            raise ValueError("2026-Q2 PDF comparison has unavailable count")
        cells[metric] = {"official": official, "project": project,
                         "signed_difference": project - official, "exact_match": project == official}
    return {"status": "PASS" if all(cell["exact_match"] for cell in cells.values()) else "BLOCKED",
            "source_url": PDF_2026_Q2_URL, "pdf_sha256": PDF_2026_Q2_SHA256,
            "edition": "ENOE 2026-Q2 national population 15+ press release",
            "cells": cells, "precision_note": "PDF count benchmark only; no official SE comparison"}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-root", type=Path, default=Path("artifacts/enoe"))
    parser.add_argument("--workbook", type=Path, default=Path(".cache/research/precision_2025q2.xlsx"))
    parser.add_argument("--records", type=Path,
                        default=Path(".cache/research/phase2-acceptance/enoe_2025_q2-public-v2.json"),
                        help="Ignored local accepted aggregate research-v2 payload")
    parser.add_argument("--ledger", type=Path, required=True)
    args = parser.parse_args()
    try:
        payload = json.loads(args.records.read_text(encoding="utf-8"))
        records = payload.get("records")
        if not isinstance(records, list) or not records:
            raise ValueError("official input has no aggregate records")
        failures = validate_research_v2(payload) if "estimate" in records[0] else validate_public_research_v2(payload)
        if failures:
            raise ValueError("official input is not strict research-v2")
        sources = payload.get("sources", [])
        if len(sources) != 1 or sources[0]["id"] != SNAPSHOT or sources[0]["sha256"] != SOURCE_SHA256:
            raise ValueError("official input source identity mismatch")
        if records and "estimate" not in records[0]:
            records = [{**row, "estimate": row["value"]} for row in records]
        result = reconcile(args.output_root, args.workbook, records)
    except (OSError, ValueError, KeyError, zipfile.BadZipFile) as exc:
        result = {"status": "BLOCKED", "reason": f"{type(exc).__name__}: {exc}"}
    args.ledger.parent.mkdir(parents=True, exist_ok=True)
    args.ledger.write_text(json.dumps(result, sort_keys=True, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": result["status"], "ledger": str(args.ledger)}))
    return 0 if result["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
