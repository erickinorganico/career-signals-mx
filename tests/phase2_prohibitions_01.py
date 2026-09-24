"""Content-dependent Phase 2 controls using only disposable synthetic rows."""

from __future__ import annotations

import contextlib
import ast
import csv
import io
import json
import logging
import subprocess
import sys
import zipfile
from pathlib import Path
from tempfile import TemporaryDirectory

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(Path(__file__).parent))

from brujula.enoe_adapter import load_snapshot_frame
from brujula.metrics import metric_vectors
from brujula.populations import (
    COMPLETED_PROFESSIONAL_KNOWN_AGE, NATIONAL_15_PLUS_CONTEXT,
    classify_eligibility, normalize_cmpe_key,
)
from test_enoe_adapter import fixture


PERSON_KEYS = {"r_def", "c_res", "eda", "fac_tri", "est_d_tri", "upm", "clase2", "ingocup"}
ARTIFACT_SUFFIXES = {".json", ".jsonl", ".csv", ".zip", ".md", ".html", ".txt", ".log"}


def _person_structure(value):
    if isinstance(value, dict):
        keys = {str(key).lower() for key in value}
        if (len(keys & PERSON_KEYS) >= 5 and {"fac_tri", "upm"} <= keys
                and all(not isinstance(item, (dict, list)) for key, item in value.items()
                        if str(key).lower() in PERSON_KEYS)):
            return True
        return any(_person_structure(item) for item in value.values())
    if isinstance(value, list):
        return any(_person_structure(item) for item in value)
    return False


def _payload_has_person(payload: bytes, suffix: str) -> bool:
    if suffix == ".zip":
        with zipfile.ZipFile(io.BytesIO(payload)) as archive:
            return any(_payload_has_person(archive.read(name), Path(name).suffix.lower())
                       for name in archive.namelist() if not name.endswith("/"))
    if suffix == ".json":
        try:
            return _person_structure(json.loads(payload.decode("utf-8")))
        except (UnicodeDecodeError, json.JSONDecodeError):
            return False
    if suffix == ".csv":
        try:
            reader = csv.DictReader(io.StringIO(payload.decode("utf-8-sig")))
            keys = {x.lower() for x in reader.fieldnames or []}
            return len(keys & PERSON_KEYS) >= 5 and {"fac_tri", "upm"} <= keys and next(reader, None) is not None
        except (UnicodeDecodeError, csv.Error):
            return False
    if suffix in {".jsonl", ".md", ".html", ".txt", ".log"}:
        return _stream_has_person(payload.decode("utf-8", errors="replace"))
    return False


def _stream_has_person(text: str) -> bool:
    decoder = json.JSONDecoder()
    # A logger may prefix a JSON object, and either JSON or repr can span
    # lines. Inspect balanced objects starting at each opening delimiter.
    for start, char in enumerate(text):
        if char not in "{[":
            continue
        try:
            value, _ = decoder.raw_decode(text[start:])
        except json.JSONDecodeError:
            value = None
        if _person_structure(value):
            return True
        depth, quote, escaped = 0, None, False
        for end in range(start, len(text)):
            token = text[end]
            if quote:
                if escaped:
                    escaped = False
                elif token == "\\":
                    escaped = True
                elif token == quote:
                    quote = None
            elif token in "\"'":
                quote = token
            elif token in "{[":
                depth += 1
            elif token in "}]":
                depth -= 1
                if depth == 0:
                    try:
                        if _person_structure(ast.literal_eval(text[start:end + 1])):
                            return True
                    except (ValueError, SyntaxError, MemoryError, RecursionError):
                        pass
                    break
    lines = text.splitlines()
    for index, line in enumerate(lines[:-1]):
        # A CSV header may itself carry a logger prefix. Start at the first
        # recognized column name and require an actual following data row.
        positions = [line.lower().find(key) for key in PERSON_KEYS]
        positions = [position for position in positions if position >= 0]
        if positions and _payload_has_person((line[min(positions):] + "\n" + lines[index + 1]).encode(), ".csv"):
            return True
    return False


def _tracked_phase2_data_artifacts():
    result = subprocess.run(["git", "ls-files", "--", "data", "artifacts"], cwd=ROOT,
                            capture_output=True, text=True, check=True)
    for relative in result.stdout.splitlines():
        path = ROOT / relative
        # Explicit synthetic test fixtures are legitimate boundary examples.
        if path.is_file() and path.suffix.lower() in ARTIFACT_SUFFIXES:
            yield path.read_bytes(), path.suffix.lower()


def _staged_artifacts(stage: Path):
    for path in stage.rglob("*"):
        if path.is_file() and path.suffix.lower() in ARTIFACT_SUFFIXES:
            yield path.read_bytes(), path.suffix.lower()


def p1(mutation: str | None):
    with TemporaryDirectory() as directory:
        sid, root, registry = fixture(Path(directory))
        stdout, stderr, logs = io.StringIO(), io.StringIO(), io.StringIO()
        handler = logging.StreamHandler(logs)
        logger = logging.getLogger("brujula")
        logger.addHandler(handler)
        try:
            with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
                frame, audit = load_snapshot_frame(sid, root, registry)
                vectors = metric_vectors(frame, NATIONAL_15_PLUS_CONTEXT, {}, "occupied_total")
        finally:
            logger.removeHandler(handler)
        synthetic_row = {"r_def": "0", "c_res": "1", "eda": "30", "fac_tri": "2", "est_d_tri": "1", "upm": "11", "clase2": "1", "ingocup": "100"}
        stage = Path(directory) / "staged-package"
        stage.mkdir()
        aggregate = {"audit": audit, "metric_coverage": vectors["coverage"],
                     "metric_exclusions": vectors["exclusions"]}
        (stage / "audit.json").write_text(json.dumps(aggregate), encoding="utf-8")
        report = f"# Synthetic aggregate audit\n\nFrame rows: {audit['frame_rows']}\n"
        with zipfile.ZipFile(stage / "package.zip", "w") as archive:
            archive.writestr("audit.json", json.dumps(aggregate))
            archive.writestr("report.md", json.dumps(synthetic_row) if mutation == "inject_untracked_package" else report)
        if mutation == "inject_untracked_package":
            (stage / "report.md").write_text(json.dumps(synthetic_row), encoding="utf-8")
        else:
            (stage / "report.md").write_text(report, encoding="utf-8")
        artifact_view = list(_tracked_phase2_data_artifacts()) + list(_staged_artifacts(stage))
        surfaces = {
            "audit": _person_structure(audit),
            "stdout": _stream_has_person(stdout.getvalue()),
            "stderr": _stream_has_person(stderr.getvalue()),
            "logger": _stream_has_person(logs.getvalue()),
            "tracked_or_packaged": any(_payload_has_person(data, suffix) for data, suffix in artifact_view),
        }
        # Independently demonstrate that every surface's scanner detects a
        # disposable row. The bad subject changes computed views, never Git.
        inject = json.dumps(synthetic_row)
        probes = {
            "audit": _person_structure({"audit": audit, "injected": synthetic_row}),
            "stdout": _stream_has_person(stdout.getvalue() + inject),
            "stderr": _stream_has_person(stderr.getvalue() + inject),
            "logger": _stream_has_person(logs.getvalue() + inject),
            "tracked_or_packaged": _payload_has_person(json.dumps({"records": [synthetic_row]}).encode(), ".json"),
        }
        assert all(probes.values()), "a person-row surface scanner is ineffective"
        if mutation == "inject_all":
            surfaces = probes
        elif mutation == "inject_prefixed_logger":
            surfaces["logger"] = _stream_has_person("INFO person=" + inject)
        elif mutation == "inject_multiline_json":
            surfaces["stderr"] = _stream_has_person("WARNING person=\n" + json.dumps(synthetic_row, indent=2))
        elif mutation == "inject_python_repr":
            surfaces["stdout"] = _stream_has_person("INFO person=" + repr(synthetic_row))
        elif mutation == "inject_csv":
            output = io.StringIO()
            writer = csv.DictWriter(output, fieldnames=list(synthetic_row))
            writer.writeheader(); writer.writerow(synthetic_row)
            surfaces["stdout"] = _stream_has_person(output.getvalue())
        assert not any(surfaces.values()), f"individual row leaked on {sorted(k for k, v in surfaces.items() if v)}"


def p2(mutation: str | None):
    with TemporaryDirectory() as directory:
        sid, root, registry = fixture(Path(directory))
        frame, _ = load_snapshot_frame(sid, root, registry)
        income = metric_vectors(frame, NATIONAL_15_PLUS_CONTEXT, {}, "positive_income_mean")
        hours = metric_vectors(frame, NATIONAL_15_PLUS_CONTEXT, {}, "known_hours_mean")
        age = classify_eligibility({"r_def": "0", "c_res": "1", "eda": "98", "cs_p13_1": "7", "cs_p16": "1", "cs_p14_c": ""}, COMPLETED_PROFESSIONAL_KNOWN_AGE)
        field = normalize_cmpe_key("999999", frame.cmpe_catalog_keys)
        observed = {
            "age_eligible": age["eligible"], "field": field,
            "sentinel_income_denominator": income["denominator"][1],
            "no_income_denominator": income["denominator"][2],
            "unknown_hours_denominator": hours["denominator"][1],
            "unknown_hours_numerator": hours["numerator"][1],
        }
        if mutation == "promote_missing":
            observed.update(age_eligible=True, field="033100", sentinel_income_denominator=1,
                            no_income_denominator=1, unknown_hours_denominator=1)
        assert observed["age_eligible"] is False
        assert observed["field"] is None
        assert observed["sentinel_income_denominator"] == 0
        assert observed["no_income_denominator"] == 0
        assert observed["unknown_hours_denominator"] == 0
        assert observed["unknown_hours_numerator"] == 0


if __name__ == "__main__":
    case = sys.argv[1]
    subject = json.loads((ROOT / sys.argv[2]).read_text(encoding="utf-8"))
    assert subject["case"] in ("clean", "p1", "p2")
    assert subject["mutation"] in (None, "inject_all", "inject_prefixed_logger", "inject_multiline_json",
                                   "inject_python_repr", "inject_csv", "inject_untracked_package", "promote_missing")
    {"p1": p1, "p2": p2}[case](subject["mutation"] if subject["case"] == case else None)
    print("checked actual Phase 2 API")
