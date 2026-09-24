"""Behavioral readback for every exact Phase 4 edge-probe pair.

The shared subject is generated from a disposable, independently pinned
synthetic packet.  The real eight-snapshot release receipt is checked
separately because it must never be a tracked or repinned test fixture.
"""

from __future__ import annotations

from copy import deepcopy
import csv
import hashlib
import json
from pathlib import Path
import re

import duckdb
from PIL import Image
from pypdf import PdfReader
import pytest

from brujula.analysis_v2 import _digest
from brujula.export_v2 import _csv_value, _table_data, export_public_tables
from brujula.pdf_v2 import LocalOnlyFetcher, render_pdf
from brujula.publication_v2 import build_publication_model, validate_publication_model
from brujula.report_v2 import (_figure_alt, _plot, _plot_figure, _style,
                               build_editorial_document, render_publication)
from tests.phase4_prohibitions import run_prohibition_case
from tests.publication_v2_support import pinned_synthetic_packet
from tests.test_report_v2 import _point


ROOT = Path(__file__).resolve().parents[1]
PROBE = ROOT / ".planning/phases/04-offline-publication-and-reproducible-operation/04-EDGE-PROBE.json"


@pytest.fixture(scope="module")
def subject(tmp_path_factory):
    root = tmp_path_factory.mktemp("phase4-edge")
    with pytest.MonkeyPatch.context() as patch:
        packet = pinned_synthetic_packet(patch, complementary=True)
        model = build_publication_model(packet)
        report = root / "report"
        result = render_publication(model, report)
        export = root / "exports"
        exported = export_public_tables(model, export)
        allowed = {p.relative_to(report).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
                   for p in report.rglob("*") if p.is_file()}
        pdf = render_pdf(report / result["html"], report, report / "report.pdf",
                         allowed_assets=allowed)
        sample = {
            "root": root, "packet": packet, "model": model, "report": report,
            "html": (report / result["html"]).read_text(encoding="utf-8"),
            "markdown": (report / result["markdown"]).read_text(encoding="utf-8"),
            "pdf": pdf, "pdf_text": "\n".join(p.extract_text() for p in PdfReader(pdf).pages),
            "exports": export, "exported": exported,
            "document": build_editorial_document(model),
        }
        yield sample


def _rows(s, table="public-records"):
    with (s["exports"] / f"{table}.csv").open(encoding="utf-8", newline="") as stream:
        return list(csv.DictReader(stream))


def _db(s, query, params=()):
    conn = duckdb.connect(str(s["exports"] / "public.duckdb"), read_only=True)
    try:
        return conn.execute(query, params).fetchall()
    finally:
        conn.close()


def _parquet(s, table="public-records"):
    path = (s["exports"] / f"{table}.parquet").as_posix().replace("'", "''")
    return duckdb.query(f"SELECT * FROM read_parquet('{path}') ORDER BY 1").fetchall()


def _figure(s, *, unavailable=False):
    values = [_point("v2r:edge-a", value=70.0, period="2025-Q1"),
              _point("v2r:edge-b", value=None if unavailable else 71.0, period="2025-Q2"),
              _point("v2r:edge-c", value=72.0, period="2025-Q3")]
    for point in values:
        point["source_id"] = "enoe_2025_q1"
    fig = {"slug": "edge-trend", "figure_id": "figure:edge-trend", "table_id": "table:edge-trend",
           "title": "¿Qué cambió en México?", "points": values,
           "periods": [p["period"] for p in values], "source_ids": ["enoe_2025_q1"],
           "synthetic": True, "comparisons": []}
    return fig, values


def _new_plot(s, fig):
    folder = s["root"] / ("unavailable" if any(p["value"] is None for p in fig["points"]) else "visible")
    folder.mkdir(exist_ok=True)
    svg, png = _plot(fig, folder)
    return (folder / svg).read_text(encoding="utf-8"), Image.open(folder / png).info["Description"]


def _mutated(model, action):
    changed = deepcopy(model)
    action(changed)
    changed["content_digest"] = _digest({k: v for k, v in changed.items() if k != "content_digest"})
    return changed


def _linked_fixture(model, *, with_claim=False):
    """Small declared relation for renderer/export behavior, not a trusted packet."""
    linked = deepcopy(model)
    latest = linked["profiles"]["periods"][-1]
    selected = [rid for rid, item in linked["records"].items()
                if item["record"]["period_id"] == latest
                and item["record"]["field_of_study_id"] in ("033100", "032100")
                and item["record"]["geography_id"] == "mx"
                and item["record"]["recorded_sex_id"] == "all"]
    assert len(selected) == 2
    link = {"figure_id": "figure:focal-latest", "table_id": "table:focal-latest",
            "record_ids": sorted(selected), "comparison_ids": [], "claim_ids": [],
            "source_ids": sorted({linked["records"][rid]["record"]["source_snapshot_id"]
                                  for rid in selected})}
    if with_claim:
        claim_id = "v2k:synthetic-link"
        linked["claims"] = [{"claim_id": claim_id, "quantities": {}, "record_ids": [selected[0]],
                             "evidence_refs": [], "title": "Relación sintética"}]
        link["claim_ids"] = [claim_id]
    linked["figure_links"] = [link]
    linked["content_digest"] = _digest({k: v for k, v in linked.items() if k != "content_digest"})
    return linked, link


# PUB-01: editorial opening, scope, missingness, encoding, order and precision.
def pub01_boundary(s, *_):
    assert s["document"]["opening_claim_ids"] == []
    altered = _mutated(s["model"], lambda m: m["opening_claim_ids"].extend(["v2k:missing"] * 4))
    assert validate_publication_model(altered)


def pub01_adjacency(s, *_):
    rows = _rows(s)
    ids = {r["record_id"] for r in rows}
    grains = {(r["population_id"], r["field_of_study_id"], r["occupation_id"],
               r["industry_id"], r["geography_id"], r["period_id"]) for r in rows}
    assert len(ids) == len(rows) and len(grains) > len(s["model"]["profiles"]["periods"])
    assert {"all", "033100"} <= {r["field_of_study_id"] for r in rows}


def pub01_empty(s, *_):
    phrase = "No hay hallazgos de apertura respaldados"
    assert phrase in s["html"] and phrase in s["markdown"]
    assert "No disponible" in s["html"] and "unknown" in s["markdown"]


def pub01_encoding(s, *_):
    assert "Ciencias políticas" in s["html"] and "Ciencias políticas" in s["markdown"]
    assert "México" in s["html"] and "México" in s["markdown"]
    assert any("México" in r["geography_label"] for r in _rows(s))


def pub01_ordering(s, *_):
    ids = [x["id"] for x in s["document"]["sections"]]
    assert ids == ["hallazgos", "lectura", "contexto", "derecho", "comunicacion",
                   "politicas", "evolucion", "sexo-territorio", "otros-campos",
                   "cobertura", "metodos", "fuentes", "evidencia"]
    assert s["document"]["periods"] == sorted(s["document"]["periods"])
    assert [s["html"].index(f'id="{key}"') for key in ids] == sorted(
        s["html"].index(f'id="{key}"') for key in ids)


def pub01_precision(s, *_):
    assert "nominal" in s["html"].lower()
    assert "no precisión oficial" in s["html"].lower()
    assert "estudios profesionales terminados" in s["html"].lower()
    assert "Unrounded canonical public numeric value" in (s["exports"] / "data-dictionary.md").read_text(encoding="utf-8")


# PUB-02: three report formats from one editorial model.
def pub02_adjacency(s, *_):
    title = s["document"]["sections"][0]["title"]
    assert title in s["html"] and title in s["markdown"] and title in s["pdf_text"]
    for label in ("Derecho", "Comunicación y periodismo", "Ciencias políticas"):
        assert label in s["html"] and label in s["markdown"] and label in s["pdf_text"]


def pub02_empty(s, tmp_path, *_):
    html = tmp_path / "report.html"
    html.write_text("<h1>Informe</h1>", encoding="utf-8")
    with pytest.raises((ValueError, FileNotFoundError)):
        render_pdf(html, tmp_path, tmp_path / "bad.pdf", allowed_assets={"report.html": "0" * 64})
    assert not (tmp_path / "bad.pdf").exists()


def pub02_encoding(s, *_):
    assert "México" in s["pdf_text"] and "Ciencias políticas" in s["pdf_text"]
    assert "Brújula Laboral MX" in s["pdf_text"]


def pub02_ordering(s, *_):
    assert len(PdfReader(s["pdf"]).pages) >= 2
    first, last = s["document"]["sections"][0]["title"], s["document"]["sections"][-1]["title"]
    assert s["pdf_text"].index(first) < s["pdf_text"].index(last)
    assert s["html"].index('id="hallazgos"') < s["html"].index('id="metodos"')


def pub02_concurrency(s, tmp_path, *_):
    html = tmp_path / "report.html"
    html.write_text("<h1>Parcial</h1>", encoding="utf-8")
    with pytest.raises((ValueError, FileNotFoundError)):
        render_pdf(html, tmp_path, tmp_path / "report.pdf", allowed_assets={"report.html": "f" * 64})
    assert not (tmp_path / "report.pdf").exists()


# PUB-03: current figure output and semantic alternatives.
def pub03_boundary(s, *_):
    css = _style()
    assert "overflow-x:auto" in css and "@media" in css
    pages = PdfReader(s["pdf"]).pages
    assert all(590 < float(page.mediabox.width) < 600 and 840 < float(page.mediabox.height) < 845 for page in pages)


def pub03_adjacency(s, *_):
    fig, points = _figure(s, unavailable=True)
    chart = _plot_figure(fig, points)
    try:
        assert not any(len(line.get_xdata()) == 2 for line in chart.axes[0].lines)
        svg, png = _new_plot(s, fig)
        assert '"value":null' in svg and '"value":null' in png
    finally:
        import matplotlib.pyplot as plt
        plt.close(chart)


def pub03_empty(s, *_):
    fig, points = _figure(s, unavailable=True)
    fig["points"] = [points[1]]
    fig["points"][0]["population_id"] = "completed_professional_known_age"
    chart = _plot_figure(fig, fig["points"])
    try:
        assert not chart.axes[0].lines
        assert "sin valores autorizados" in _figure_alt(fig).lower()
    finally:
        import matplotlib.pyplot as plt
        plt.close(chart)


def pub03_encoding(s, *_):
    fig, _ = _figure(s)
    svg, png = _new_plot(s, fig)
    assert "México" in svg and "México" in png
    assert "¿Qué cambió" in svg and "¿Qué cambió" in png
    assert "enoe_2025_q1" in svg and "enoe_2025_q1" in png


def pub03_ordering(s, *_):
    fig, points = _figure(s)
    svg, png = _new_plot(s, fig)
    assert all(rid in svg and rid in png for rid in [p["record_id"] for p in points])
    assert [p["period"] for p in points] == fig["periods"]


def pub03_precision(s, *_):
    fig, points = _figure(s)
    svg, png = _new_plot(s, fig)
    chart = _plot_figure(fig, points)
    try:
        observed = [tuple(tuple(map(float, xy)) for xy in segment) for collection in chart.axes[0].collections
                    for segment in collection.get_segments()]
        expected = [((point["ci90_lower"], index), (point["ci90_upper"], index))
                    for index, point in enumerate(points)]
        assert observed == expected
        markers = [(float(line.get_xdata()[0]), int(line.get_ydata()[0]))
                   for line in chart.axes[0].lines if len(line.get_xdata()) == 1]
        assert all((point["value"], index) in markers for index, point in enumerate(points))
    finally:
        import matplotlib.pyplot as plt
        plt.close(chart)
    for point in points:
        assert f'"value":{point["value"]}' in svg
        assert f'"ci90_lower":{point["ci90_lower"]}' in png


# PUB-04: typed export readback and exact relational joins.
def pub04_boundary(s, tmp_path, monkeypatch):
    rid = next(rid for rid, item in s["model"]["records"].items()
               if item["record"]["value"] is None)
    assert _db(s, "SELECT value FROM public_records WHERE record_id=?", [rid]) == [(None,)]
    # Isolate serialization of a zero-valued row. The accepted test packet has
    # no zero, so this fixture changes only the row fed to the real exporter.
    zero = deepcopy(s["model"])
    finite_id = next(key for key, item in zero["records"].items() if item["record"]["value"] is not None)
    zero["records"][finite_id]["record"]["value"] = 0.0
    with pytest.MonkeyPatch.context() as fixture:
        fixture.setattr("brujula.export_v2.validate_publication_model", lambda _model: [])
        target = tmp_path / "zero-roundtrip"
        export_public_tables(zero, target)
    with (target / "public-records.csv").open(encoding="utf-8", newline="") as stream:
        csv_rows = {row["record_id"]: row for row in csv.DictReader(stream)}
    assert csv_rows[finite_id]["value"] == "0.0" and csv_rows[rid]["value"] == ""
    db = duckdb.connect(str(target / "public.duckdb"), read_only=True)
    try:
        assert db.execute("SELECT value FROM public_records WHERE record_id=?", [finite_id]).fetchone() == (0.0,)
        assert db.execute("SELECT value FROM public_records WHERE record_id=?", [rid]).fetchone() == (None,)
    finally:
        db.close()
    parquet = (target / "public-records.parquet").as_posix().replace("'", "''")
    assert duckdb.query(f"SELECT value FROM read_parquet('{parquet}') WHERE record_id='{finite_id}'").fetchone() == (0.0,)
    assert duckdb.query(f"SELECT value FROM read_parquet('{parquet}') WHERE record_id='{rid}'").fetchone() == (None,)
    bad = deepcopy(s["model"])
    bad["records"][rid]["record"]["value"] = float("nan")
    assert validate_publication_model(bad)


def pub04_adjacency(s, tmp_path, *_):
    pairs = _db(s, "SELECT comparison_id, previous_record_id, current_record_id FROM comparisons")
    records = {r[0] for r in _db(s, "SELECT record_id FROM public_records")}
    assert pairs and all(a in records and b in records for _, a, b in pairs)
    assert len(records) == len(s["model"]["records"])
    linked, link = _linked_fixture(s["model"], with_claim=True)
    # The one-metric packet has no accepted claim/figure; the fixture tests
    # the actual relational writer and joins with explicit nonempty links.
    with pytest.MonkeyPatch.context() as fixture:
        fixture.setattr("brujula.export_v2.validate_publication_model", lambda _model: [])
        target = tmp_path / "linked-export"
        export_public_tables(linked, target)
    db = duckdb.connect(str(target / "public.duckdb"), read_only=True)
    try:
        figure_rows = db.execute("SELECT f.figure_id, r.record_id FROM figures f "
                                 "JOIN figure_record_links r ON f.figure_id=r.figure_id ORDER BY r.record_id").fetchall()
        claim_rows = db.execute("SELECT c.claim_id, r.record_id FROM claims c "
                                "JOIN claim_record_links r ON c.claim_id=r.claim_id").fetchall()
        figure_claim = db.execute("SELECT figure_id, claim_id FROM figure_claim_links").fetchall()
        assert figure_rows == [(link["figure_id"], rid) for rid in link["record_ids"]]
        assert claim_rows == [(link["claim_ids"][0], linked["claims"][0]["record_ids"][0])]
        assert figure_claim == [(link["figure_id"], link["claim_ids"][0])]
        assert {rid for _, rid in figure_rows + claim_rows} <= records
    finally:
        db.close()


def pub04_empty(s, *_):
    row = next(r for r in _rows(s) if r["value"] == "")
    typed = _db(s, "SELECT value, weighted_denominator, weighted_support_total, "
                   "standard_error, coefficient_variation, ci90_lower, ci90_upper, status, reason "
                   "FROM public_records WHERE record_id=?", [row["record_id"]])[0]
    assert typed[:7] == (None,) * 7
    assert row["status"] == typed[7] and row["reason"] == typed[8]


def pub04_encoding(s, *_):
    rows = _rows(s)
    assert any(r["field_of_study_id"].startswith("0") for r in rows)
    assert any("México" in r["geography_label"] for r in rows)
    assert _csv_value("=SUM(1,2)") == "'=SUM(1,2)"
    assert "leading apostrophe" in (s["exports"] / "data-dictionary.md").read_text(encoding="utf-8")


def pub04_ordering(s, tmp_path, *_):
    names = s["exported"]["files"]
    assert len(names) == 46 and names == sorted(names)
    assert [r["record_id"] for r in _rows(s)] == sorted(s["model"]["records"])
    permuted = deepcopy(s["model"])
    permuted["records"] = dict(reversed(list(permuted["records"].items())))
    permuted["content_digest"] = _digest({k: v for k, v in permuted.items() if k != "content_digest"})
    assert validate_publication_model(permuted) == []
    other = tmp_path / "permuted"
    export_public_tables(permuted, other)
    assert (other / "public-records.csv").read_bytes() == (s["exports"] / "public-records.csv").read_bytes()
    with (other / "public-records.csv").open(encoding="utf-8", newline="") as stream:
        assert [row["record_id"] for row in csv.DictReader(stream)] == sorted(s["model"]["records"])
    dictionary = (s["exports"] / "data-dictionary.md").read_text(encoding="utf-8")
    assert all(f"## {name}" in dictionary for name in _table_data(s["model"]))


def pub04_precision(s, *_):
    rows = _rows(s)
    for row in rows:
        rid = row["record_id"]
        value = s["model"]["records"][rid]["record"]["value"]
        if value is not None:
            assert float(row["value"]) == value
            assert _db(s, "SELECT value FROM public_records WHERE record_id=?", [rid])[0][0] == value
    assert "not a weighted population total" in (s["exports"] / "data-dictionary.md").read_text(encoding="utf-8")


def pub04_concurrency(s, tmp_path, monkeypatch):
    monkeypatch.setattr("brujula.export_v2.duckdb.connect", lambda *_a: (_ for _ in ()).throw(OSError("interrupted")))
    target = tmp_path / "interrupted"
    with pytest.raises(OSError, match="interrupted"):
        export_public_tables(s["model"], target)
    assert not target.exists()


# PUB-05: suppression and complement controls on generated output.
def pub05_boundary(s, *_):
    result = run_prohibition_case("suppressed")
    assert result["checked_text_files"] >= 25 and result["checked_typed_containers"] == 2
    assert result["pdf_pages"] >= 1 and result["bad_rejected"]


def pub05_adjacency(s, *_):
    result = run_prohibition_case("complement")
    assert result["duplicate_appearances"] >= 1 and result["bad_rejected"]


def pub05_empty(s, *_):
    row = next(r for r in _rows(s) if r["redaction_reason"] == "complementary_suppression")
    assert all(row[key] == "" for key in ("value", "weighted_denominator", "weighted_support_total",
                                          "standard_error", "coefficient_variation", "ci90_lower", "ci90_upper"))
    assert row["reason"] == "review_required"


def pub05_encoding(s, *_):
    result = run_prohibition_case("suppressed")
    assert result["pdf_sha256"] and result["checked_text_files"] > 25


def pub05_ordering(s, tmp_path, *_):
    original, link = _linked_fixture(s["model"])
    changed = deepcopy(original)
    changed["records"] = dict(reversed(list(changed["records"].items())))
    changed["content_digest"] = _digest({k: v for k, v in changed.items() if k != "content_digest"})
    assert _table_data(changed)["public_records"][1] == _table_data(original)["public_records"][1]
    assert changed["opening_claim_ids"] == original["opening_claim_ids"]
    assert changed["figure_links"] == original["figure_links"]
    with pytest.MonkeyPatch.context() as fixture:
        fixture.setattr("brujula.report_v2.validate_publication_model", lambda _model: [])
        fixture.setattr("brujula.export_v2.validate_publication_model", lambda _model: [])
        document_a = build_editorial_document(original)
        document_b = build_editorial_document(changed)
        first = tmp_path / "linked-first"
        second = tmp_path / "linked-reversed"
        a, b = render_publication(original, first), render_publication(changed, second)
        ea = export_public_tables(original, tmp_path / "export-first")
        eb = export_public_tables(changed, tmp_path / "export-reversed")
    assert len(a["figures"]) == len(b["figures"]) == 1
    assert [point["record_id"] for point in document_a["figures"][0]["points"]] == [
        point["record_id"] for point in document_b["figures"][0]["points"]]
    assert set(link["record_ids"]) == {point["record_id"] for point in document_a["figures"][0]["points"]}
    for key in ("svg", "png"):
        assert a["figures"][0][key] == b["figures"][0][key]
    for rid in link["record_ids"]:
        assert rid in (first / a["figures"][0]["svg"]).read_text(encoding="utf-8")
        assert rid in (second / b["figures"][0]["svg"]).read_text(encoding="utf-8")
    assert (tmp_path / "export-first/public-records.csv").read_bytes() == (tmp_path / "export-reversed/public-records.csv").read_bytes()
    assert len(ea["files"]) == len(eb["files"]) == 46
    assert {rid for rid in link["record_ids"]} == {rid for rid in changed["figure_links"][0]["record_ids"]}


def pub05_precision(s, *_):
    suppressed = [r for r in _rows(s) if r["value"] == ""]
    assert suppressed
    assert all(all(r[key] == "" for key in ("standard_error", "coefficient_variation",
                                                 "ci90_lower", "ci90_upper", "weighted_support_total"))
               for r in suppressed)


# OPS-01/02/03: generated immutable run and current custody API.
def _service(tmp_path, monkeypatch):
    from brujula import pipeline_v2 as p
    from tests.test_pipeline_v2 import _stub_build
    source, out, audit, analysis, names = _stub_build(monkeypatch, tmp_path)
    built = p.build_publication(source, out, audit, analysis)
    return p, source, out, audit, analysis, names, built


def ops01_adjacency(s, tmp_path, monkeypatch):
    _, _, _, _, _, _, built = _service(tmp_path, monkeypatch)
    assert len(built["manifest"]["source_dependencies"]) == 8
    assert built["receipt"]["numerical_acceptance_attempt_id"] == "sample"
    assert built["receipt"]["run_id"] != "sample"


def ops01_empty(s, tmp_path, *_):
    from brujula import pipeline_v2 as p
    with pytest.raises(FileNotFoundError):
        p.analyze_acceptance(tmp_path / "source", tmp_path / "numeric/attempts/missing.json",
                             tmp_path / "packet.json", tmp_path / "analysis-audit")
    current = json.loads((tmp_path / "analysis-audit/current.json").read_text(encoding="utf-8"))
    assert current["status"] == "BLOCKED" and not (tmp_path / "packet.json").exists()


def ops01_ordering(s, tmp_path, monkeypatch):
    p, source, out, audit, analysis, _, first = _service(tmp_path, monkeypatch)
    second = p.build_publication(source, out, audit, analysis)
    assert first["receipt"]["run_id"] != second["receipt"]["run_id"]
    assert first["receipt"]["publication_content_digest"] == second["receipt"]["publication_content_digest"]


def ops01_idempotency(s, tmp_path, monkeypatch):
    p, source, out, audit, analysis, _, first = _service(tmp_path, monkeypatch)
    old = (first["run"] / "receipt.json").read_bytes()
    second = p.build_publication(source, out, audit, analysis)
    assert old == (first["run"] / "receipt.json").read_bytes()
    assert (second["run"] / "receipt.json").is_file()


def ops01_concurrency(s, tmp_path, *_):
    from brujula.runlock import BuildLock
    lock = tmp_path / "source"
    lock.mkdir()
    with BuildLock(lock):
        with pytest.raises(Exception):
            with BuildLock(lock):
                pass


def ops02_adjacency(s, tmp_path, monkeypatch):
    _, _, out, _, _, names, built = _service(tmp_path, monkeypatch)
    current = json.loads((out / "current.json").read_text(encoding="utf-8"))
    assert set(built["manifest"]["artifact_hashes"]) == names
    assert (built["run"] / "receipt.json").is_file() and (built["run"] / "manifest.json").is_file()
    assert current["manifest_sha256"] == hashlib.sha256((built["run"] / "manifest.json").read_bytes()).hexdigest()


def ops02_empty(s, tmp_path, monkeypatch):
    p, _, _, _, _, _, built = _service(tmp_path, monkeypatch)
    (built["run"] / "report.html").unlink()
    with pytest.raises(ValueError, match="inventory"):
        p._inventory(built["run"], set(built["manifest"]["artifact_hashes"]) | {"receipt.json", "manifest.json", "journal.json"})


def ops02_ordering(s, tmp_path, monkeypatch):
    from brujula import pipeline_v2 as p
    original_render, original_expected = p._render, p._expected
    p, source, out, audit, analysis, _, good = _service(tmp_path, monkeypatch)
    sealed = (good["run"] / "manifest.json").read_bytes()
    for stage in ("source", "pdf", "export", "receipt", "manifest", "pointer", "final_index"):
        with pytest.MonkeyPatch.context() as fault:
            if stage == "source":
                fault.setattr(p, "_sources", lambda *_: (_ for _ in ()).throw(OSError("source fault")))
            elif stage in ("pdf", "export"):
                fault.setattr(p, "_render", original_render)
                fault.setattr(p, "_expected", original_expected)
                fault.setattr(p, "build_publication_model", lambda *_: s["model"])
                target = "brujula.pdf_v2.render_pdf" if stage == "pdf" else "brujula.pipeline_v2.export_public_tables"
                fault.setattr(target, lambda *_a, **_k: (_ for _ in ()).throw(OSError(stage + " fault")))
            elif stage == "receipt":
                original = p.immutable_bytes
                armed = [True]
                def fail_receipt(path, content):
                    if armed[0] and path.name == "receipt.json":
                        armed[0] = False
                        raise OSError("receipt fault")
                    return original(path, content)
                fault.setattr(p, "immutable_bytes", fail_receipt)
            elif stage == "manifest":
                fault.setattr(p, "_validate_manifest", lambda *_: (_ for _ in ()).throw(OSError("manifest fault")))
            else:
                original = p.atomic_json
                armed = [True]
                def fail_promotion(path, value):
                    if armed[0] and ((stage == "pointer" and path.name == "current.json" and value.get("status") == "REVIEW")
                                     or (stage == "final_index" and path.name == "journal.json" and value.get("build_status") == "SUCCEEDED")):
                        armed[0] = False
                        raise OSError(stage + " fault")
                    return original(path, value)
                fault.setattr(p, "atomic_json", fail_promotion)
            with pytest.raises(OSError, match=stage):
                p.build_publication(source, out, audit, analysis)
        current = json.loads((out / "current.json").read_text(encoding="utf-8"))
        assert current["status"] == "BLOCKED" and current["stage"] == ("render_export" if stage in ("pdf", "export") else stage)
        assert (out / "runs" / current["run_id"] / "receipt.json").is_file()
        assert (good["run"] / "manifest.json").read_bytes() == sealed


def ops02_idempotency(s, tmp_path, monkeypatch):
    p, source, out, audit, analysis, _, good = _service(tmp_path, monkeypatch)
    monkeypatch.setattr(p, "_attempt_id", lambda: good["receipt"]["run_id"])
    with pytest.raises(FileExistsError):
        p.build_publication(source, out, audit, analysis)
    assert (good["run"] / "manifest.json").is_file()


def ops02_concurrency(s, tmp_path, monkeypatch):
    from brujula import pipeline_v2 as p
    from brujula.runlock import BuildLock
    source, out, audit, analysis, _ = __import__("tests.test_pipeline_v2", fromlist=["_stub_build"])._stub_build(monkeypatch, tmp_path)
    original = p._sources
    armed = [True]
    def crash(root):
        if armed[0]:
            armed[0] = False
            raise KeyboardInterrupt("abrupt builder exit")
        return original(root)
    monkeypatch.setattr(p, "_sources", crash)
    with pytest.raises(KeyboardInterrupt):
        p.build_publication(source, out, audit, analysis)
    interrupted = json.loads((out / "current.json").read_text(encoding="utf-8"))
    assert interrupted["build_status"] == "RUNNING"
    with BuildLock(out):
        with pytest.raises(Exception):
            p.build_publication(source, out, audit, analysis)
    rebuilt = p.build_publication(source, out, audit, analysis)
    failed = json.loads((out / "runs" / interrupted["run_id"] / "receipt.json").read_text(encoding="utf-8"))
    assert failed["stage"] == "interrupted_recovery" and failed["build_status"] == "FAILED"
    assert rebuilt["current"]["run_id"] != interrupted["run_id"]


def ops03_adjacency(s, tmp_path, monkeypatch):
    p, _, _, _, _, _, good = _service(tmp_path, monkeypatch)
    assert {dep["snapshot_id"] for dep in good["manifest"]["source_dependencies"]} == set(p.SNAPSHOTS)


def ops03_empty(s, tmp_path, monkeypatch):
    p, _, _, _, _, names, good = _service(tmp_path, monkeypatch)
    (good["run"] / "report.pdf").unlink()
    with pytest.raises(ValueError):
        p._inventory(good["run"], names | {"receipt.json", "manifest.json", "journal.json"})


def ops03_ordering(s, tmp_path, monkeypatch):
    result = run_prohibition_case("stale-current")
    assert result["bad_rejected"] and result["clean_accepted"]
    assert result["failed_acquisition_rejected"]
    assert result["producer"].endswith("live_source_service_double")


def ops03_idempotency(s, tmp_path, monkeypatch):
    result = run_prohibition_case("stale-current")
    assert result["bad_rejected"] and result["clean_accepted"]
    assert result["producer"].startswith("pipeline_v2.build_publication+real_verify_sealed")


def ops03_concurrency(s, tmp_path, monkeypatch):
    from brujula import pipeline_v2 as p
    source, out = tmp_path / "source", tmp_path / "out"
    out.mkdir()
    p.atomic_json(out / "current.json", {"schema_version": "2.0",
        "run_id": "20260924T000000-aaaaaaaaaaaa", "status": "REVIEW",
        "build_status": "SUCCEEDED", "manifest_sha256": "a" * 64})
    count = 0
    def verify(*_args):
        nonlocal count
        count += 1
        return {"sources": [{"attempt": count}], "artifact_hashes": {}, "manifest": {}, "receipt": {}}
    monkeypatch.setattr(p, "_verify_sealed", verify)
    with pytest.raises(ValueError, match="changed during resolution"):
        p.resolve_publication_current(out, source)
    assert count == 2


CHECKS = {
    ("PUB-01", "boundary"): pub01_boundary, ("PUB-01", "adjacency"): pub01_adjacency,
    ("PUB-01", "empty"): pub01_empty, ("PUB-01", "encoding"): pub01_encoding,
    ("PUB-01", "ordering"): pub01_ordering, ("PUB-01", "precision"): pub01_precision,
    ("PUB-02", "adjacency"): pub02_adjacency, ("PUB-02", "empty"): pub02_empty,
    ("PUB-02", "encoding"): pub02_encoding, ("PUB-02", "ordering"): pub02_ordering,
    ("PUB-02", "concurrency"): pub02_concurrency,
    ("PUB-03", "boundary"): pub03_boundary, ("PUB-03", "adjacency"): pub03_adjacency,
    ("PUB-03", "empty"): pub03_empty, ("PUB-03", "encoding"): pub03_encoding,
    ("PUB-03", "ordering"): pub03_ordering, ("PUB-03", "precision"): pub03_precision,
    ("PUB-04", "boundary"): pub04_boundary, ("PUB-04", "adjacency"): pub04_adjacency,
    ("PUB-04", "empty"): pub04_empty, ("PUB-04", "encoding"): pub04_encoding,
    ("PUB-04", "ordering"): pub04_ordering, ("PUB-04", "precision"): pub04_precision,
    ("PUB-04", "concurrency"): pub04_concurrency,
    ("PUB-05", "boundary"): pub05_boundary, ("PUB-05", "adjacency"): pub05_adjacency,
    ("PUB-05", "empty"): pub05_empty, ("PUB-05", "encoding"): pub05_encoding,
    ("PUB-05", "ordering"): pub05_ordering, ("PUB-05", "precision"): pub05_precision,
    ("OPS-01", "adjacency"): ops01_adjacency, ("OPS-01", "empty"): ops01_empty,
    ("OPS-01", "ordering"): ops01_ordering, ("OPS-01", "idempotency"): ops01_idempotency,
    ("OPS-01", "concurrency"): ops01_concurrency,
    ("OPS-02", "adjacency"): ops02_adjacency, ("OPS-02", "empty"): ops02_empty,
    ("OPS-02", "ordering"): ops02_ordering, ("OPS-02", "idempotency"): ops02_idempotency,
    ("OPS-02", "concurrency"): ops02_concurrency,
    ("OPS-03", "adjacency"): ops03_adjacency, ("OPS-03", "empty"): ops03_empty,
    ("OPS-03", "ordering"): ops03_ordering, ("OPS-03", "idempotency"): ops03_idempotency,
    ("OPS-03", "concurrency"): ops03_concurrency,
}


def test_exact_probe_mapping_has_no_missing_or_duplicate_pair():
    items = json.loads(PROBE.read_text(encoding="utf-8"))["items"]
    pairs = [(item["requirement_id"], item["category"]) for item in items]
    assert len(pairs) == len(set(pairs)) == 45
    assert set(pairs) == set(CHECKS)
    assert len(set(CHECKS.values())) == 45


@pytest.mark.parametrize("pair", sorted(CHECKS), ids=lambda p: f"{p[0]}-{p[1]}")
def test_phase4_edge_pair_on_computed_subject(pair, subject, tmp_path, monkeypatch):
    CHECKS[pair](subject, tmp_path, monkeypatch)
