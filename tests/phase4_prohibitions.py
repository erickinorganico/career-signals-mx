"""Computed Phase 4 bad/clean subjects for the canonical prohibition producer.

All mutations are disposable and synthetic.  The clean publication is built
through the current guarded packet, model, renderer and exporter APIs.
"""

from __future__ import annotations

from copy import deepcopy
import hashlib
import json
from pathlib import Path
import sys
from tempfile import TemporaryDirectory

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from pytest import MonkeyPatch

from brujula.analysis_v2 import _digest
from brujula import findings_v2
from brujula.comparisons_v2 import load_definition_registry
from brujula.export_v2 import export_public_tables
from brujula.pdf_v2 import LocalOnlyFetcher, render_pdf
from brujula.publication_v2 import build_publication_model, validate_publication_model
from brujula.report_v2 import _plot, render_publication, stage_report_fonts
from brujula.research_contract import public_research_projection, validate_public_research_v2
from tests.publication_v2_support import pinned_synthetic_packet
from tests.test_analysis_v2 import synthetic_inputs


CASES = {
    "suppressed": "nested_diagnostic_canaries",
    "complement": "restore_redacted_parent",
    "pdf-fetch": "external_and_missing_local_asset",
    "stale-current": "damage_sealed_artifact",
}


def _model(patch: MonkeyPatch) -> dict:
    return build_publication_model(pinned_synthetic_packet(patch, complementary=True))


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _canary_model(patch: MonkeyPatch) -> tuple[dict, dict, list[str]]:
    publics, accepted = synthetic_inputs(patch, complementary=True)
    snapshot = next(iter(publics))
    internal = deepcopy(publics[snapshot])
    for record in internal["records"]:
        record["estimate"] = record["value"]
    row = internal["records"][0]
    assert row["value"] is None
    row.update(estimate=123456.789, weighted_denominator=123456.789)
    row["support"]["weighted_support_total"] = 123456.789
    row["precision"].update(standard_error=987654.321,
                            coefficient_variation=987654.321,
                            ci90_lower=100000.125, ci90_upper=987654.321)
    projected = public_research_projection(internal)
    assert validate_public_research_v2(projected) == []
    # The canary-bearing validated internal input is the input for the actual
    # public packet.  Its projection must preserve the independently pinned
    # public fixture exactly, so no runtime reference is repinned.
    assert projected == publics[snapshot]
    publics[snapshot] = projected
    safe = projected["records"][0]
    assert safe["value"] is None and "estimate" not in safe
    assert safe["weighted_denominator"] is None
    assert safe["support"]["weighted_support_total"] is None
    assert all(safe["precision"][key] is None for key in
               ("standard_error", "coefficient_variation", "ci90_lower", "ci90_upper"))
    registry = load_definition_registry(entity_reference_code="02")
    registry["metric_manifest_sha256"] = accepted["manifest"]["metric_manifest_sha256"]
    patch.setattr(findings_v2, "load_definition_registry", lambda **_kwargs: deepcopy(registry))
    candidate = findings_v2._assemble(publics, accepted["manifest"], accepted["audits"], registry)
    frozen = deepcopy(findings_v2._reference_from_packet(candidate))
    patch.setattr(findings_v2, "_load_reference", lambda: deepcopy(frozen))
    packet = findings_v2.build_analysis_packet(publics, accepted["manifest"], accepted["audits"], registry)
    assert findings_v2.validate_analysis_packet(packet) == []
    model = build_publication_model(packet)
    assert validate_publication_model(model) == []
    return model, safe, ["123456.789", "987654.321", "100000.125"]


def _suppressed(model: dict, safe: dict, canaries: list[str], root: Path) -> dict:
    rid, item = next((rid, item) for rid, item in model["records"].items()
                     if item["record"]["source_snapshot_id"] == safe["source_snapshot_id"]
                     and item["record"]["population_id"] == safe["population_id"]
                     and item["record"]["field_of_study_id"] == safe["field_of_study_id"]
                     and item["record"]["geography_id"] == safe["geography_id"])
    assert item["record"] == safe
    assert item["record"]["value"] is None
    bad = deepcopy(model)
    bad["records"][rid]["record"]["value"] = 123456.789
    bad["records"][rid]["record"]["weighted_denominator"] = 123456.789
    bad["records"][rid]["record"]["support"]["weighted_support_total"] = 123456.789
    bad["records"][rid]["record"]["precision"].update(
        standard_error=987654.321, coefficient_variation=987654.321,
        ci90_lower=100000.125, ci90_upper=987654.321)
    bad["content_digest"] = _digest({k: v for k, v in bad.items() if k != "content_digest"})
    rejection = validate_publication_model(bad)
    assert rejection, "mutated suppressed public row was accepted"
    assert validate_publication_model(model) == []
    report = root / "report"
    export = root / "export"
    rendered = render_publication(model, report)
    exported = export_public_tables(model, export)
    point = {"record_id": rid, "field_code": "033100", "field": "Derecho",
             "metric_id": "population_total", "metric": "Población total",
             "unit": "people", "population": "personas profesionales",
             "population_id": "completed_professional_known_age", "period": "2025-Q2",
             "value": safe["value"], "ci90_lower": safe["precision"]["ci90_lower"],
             "ci90_upper": safe["precision"]["ci90_upper"], "status": safe["status"],
             "reason": safe["reason"], "geography_id": "mx", "geography": "México",
             "recorded_sex_id": "all", "recorded_sex": "todos",
             "source_id": "enoe_2025_q2"}
    figure = {"slug": "canary-redaction", "figure_id": "figure:canary-redaction",
              "table_id": "table:canary-redaction", "title": "¿Hay un valor disponible?",
              "points": [point], "periods": [point["period"]],
              "source_ids": [point["source_id"]], "synthetic": True}
    svg, png = _plot(figure, report)
    from pypdf import PdfReader
    import re
    allowed = {path.relative_to(report).as_posix(): _sha(path)
               for path in report.rglob("*") if path.is_file()}
    pdf = render_pdf(report / rendered["html"], report, report / "report.pdf",
                     allowed_assets=allowed)
    pdf_text = "\n".join(page.extract_text() for page in PdfReader(pdf).pages)
    assert all(token not in pdf_text for token in canaries)
    text_paths = [report / rendered["html"], report / rendered["markdown"],
                  *(report / fig[key] for fig in rendered["figures"] for key in ("svg", "png")),
                  report / svg, report / png,
                  *(export / name for name in exported["files"] if name.endswith((".csv", ".md")))]
    for path in text_paths:
        content = path.read_bytes()
        variants = {token.encode() for token in canaries}
        variants.update(re.escape(token).encode() for token in canaries)
        assert all(token not in content for token in variants), path
    from PIL import Image
    png_description = Image.open(report / png).info["Description"]
    assert '"value":null' in png_description
    assert all(token not in png_description for token in canaries)
    import duckdb
    db = duckdb.connect(str(export / "public.duckdb"), read_only=True)
    db_values = db.execute("SELECT value, weighted_denominator, weighted_support_total, "
                           "standard_error, coefficient_variation, ci90_lower, ci90_upper "
                           "FROM public_records WHERE record_id=?", [rid]).fetchone()
    db.close()
    parquet_values = duckdb.query(
        "SELECT value, weighted_denominator, weighted_support_total, standard_error, "
        "coefficient_variation, ci90_lower, ci90_upper FROM read_parquet('" +
        (export / "public-records.parquet").as_posix().replace("'", "''") +
        "') WHERE record_id='" + rid + "'").fetchone()
    assert db_values == parquet_values == (None,) * 7
    assert safe["reason"] == "unknown" and item["record"]["reason"] == "unknown"
    return {"bad_rejected": bool(rejection), "clean_accepted": True,
            "producer": "public_research_projection+publication_v2+report_v2+export_v2",
            "checked_text_files": len(text_paths), "checked_typed_containers": 2,
            "pdf_sha256": _sha(pdf), "pdf_pages": len(PdfReader(pdf).pages),
            "redacted_record_id": rid, "rejection_ids": [e["id"] for e in rejection[:3]]}


def _complement(model: dict, root: Path) -> dict:
    redacted = [(rid, item) for rid, item in model["records"].items()
                if item.get("redaction_reason") == "complementary_suppression"]
    assert len(redacted) >= 1
    rid = redacted[0][0]
    bad = deepcopy(model)
    bad["records"][rid]["record"].update(value=3100.0, status="REVIEW",
                                             reason="synthetic_fixture")
    bad["content_digest"] = _digest({k: v for k, v in bad.items() if k != "content_digest"})
    rejection = validate_publication_model(bad)
    assert rejection
    assert validate_publication_model(model) == []
    linked = [cell for name in ("national", "latest_fields", "latest_states", "latest_recorded_sexes")
              for cell in model["profiles"][name] if cell["record_id"] == rid]
    assert linked and all(cell["value"] is None for cell in linked)
    assert model["records"][rid]["record"]["value"] is None
    return {"bad_rejected": True, "clean_accepted": True,
            "producer": "analysis_v2+publication_v2",
            "redacted_record_id": rid, "duplicate_appearances": len(linked),
            "rejection_ids": [e["id"] for e in rejection[:3]]}


def _pdf_fetch(root: Path) -> dict:
    html = root / "report.html"
    html.write_text('<!doctype html><html lang="es"><head><meta charset="utf-8">'
                    '<style>@font-face{font-family:LocalSans;src:url("assets/fonts/DejaVuSans.ttf")}'
                    'body{font-family:LocalSans}</style></head><body><h1>Árbol y profesión</h1></body></html>',
                    encoding="utf-8")
    fonts = stage_report_fonts(root)
    allowed = {name: _sha(root / name) for name in ("report.html", *fonts)}
    fetcher = LocalOnlyFetcher(root, allowed)
    rejected = 0
    for url in ("https://example.org/unapproved", "data:text/plain,private", "../escaped.css",
                (root / "missing.css").as_uri()):
        try:
            fetcher(url)
        except (ValueError, FileNotFoundError):
            rejected += 1
    assert rejected == 4
    changed = root / fonts[0]
    original = changed.read_bytes()
    changed.write_bytes(b"changed")
    try:
        try:
            render_pdf(html, root, root / "bad.pdf", allowed_assets=allowed)
        except (ValueError, FileNotFoundError):
            rejected += 1
        else:
            raise AssertionError("changed font accepted")
    finally:
        changed.write_bytes(original)
    assert not (root / "bad.pdf").exists()
    result = render_pdf(html, root, root / "clean.pdf", allowed_assets=allowed)
    from pypdf import PdfReader
    text = "\n".join(page.extract_text() for page in PdfReader(result).pages)
    assert "Árbol y profesión" in text
    return {"bad_rejected": rejected == 5, "clean_accepted": result.read_bytes().startswith(b"%PDF-"),
            "producer": "LocalOnlyFetcher+render_pdf+pypdf", "rejected_resources": rejected,
            "pdf_sha256": _sha(result)}


def _stale_current(root: Path) -> dict:
    from brujula import pipeline_v2 as pipeline
    output, source = root / "output", root / "source"
    source.mkdir()
    with MonkeyPatch.context() as patch:
        from brujula import analysis_v2
        publics, accepted = synthetic_inputs(patch, complementary=True)
        patch.setattr(analysis_v2, "_required_code_files", lambda: analysis_v2.EXPECTED_CODE_FILES)
        accepted["manifest"]["code_sha256"] = pipeline._code_hashes()
        registry = load_definition_registry(entity_reference_code="02")
        registry["metric_manifest_sha256"] = accepted["manifest"]["metric_manifest_sha256"]
        patch.setattr(findings_v2, "load_definition_registry", lambda **_kwargs: deepcopy(registry))
        candidate = findings_v2._assemble(publics, accepted["manifest"], accepted["audits"], registry)
        frozen = deepcopy(findings_v2._reference_from_packet(candidate))
        patch.setattr(findings_v2, "_load_reference", lambda: deepcopy(frozen))
        packet = findings_v2.build_analysis_packet(publics, accepted["manifest"], accepted["audits"], registry)
        assert findings_v2.validate_analysis_packet(packet) == []
        model = build_publication_model(packet)
        proof = packet["source_manifest"]["acceptance"]
        dependencies = [{"snapshot_id": sid, "acquisition_attempt_id": "synthetic-attempt",
                         "source_url": item["url"], "source_sha256": item["sha256"],
                         "period_id": item["period_id"], "receipt_sha256": "3" * 64}
                        for sid, item in packet["source_manifest"]["sources"].items()]
        dependencies.sort(key=lambda dep: pipeline.SNAPSHOTS.index(dep["snapshot_id"]))
        numerical = {"attempt_id": "a" * 36,
                     "numeric_content_digest": proof["numeric_content_digest"]}
        summary = {"attempt_id": numerical["attempt_id"], "receipt_sha256": "d" * 64,
                   "numeric_content_digest": proof["numeric_content_digest"],
                   "metric_manifest_sha256": proof["metric_manifest_sha256"],
                   "code_sha256": proof["code_sha256"],
                   "resource_sha256": pipeline._numeric_resource_digests(),
                   "source_manifest": packet["source_manifest"]}
        # The tiny one-metric fixture has no drawable figure.  Keep the real
        # manifest validator and resolver; adjust only its production minimum
        # (six base figures) to this fixture's exact derived artifact count.
        schema = pipeline._manifest_schema()
        schema["properties"]["artifact_hashes"]["minProperties"] = len(pipeline._expected(model))
        patch.setattr(pipeline, "_manifest_schema", lambda: deepcopy(schema))
        patch.setattr(pipeline, "_sources", lambda _root: deepcopy(dependencies))
        patch.setattr(pipeline, "_accepted", lambda _audit, selected=None: (numerical, "d" * 64))
        patch.setattr(pipeline, "_summary", lambda *_args: deepcopy(summary))

        def stage(_model, run):
            from brujula.report_v2 import stage_report_fonts
            stage_report_fonts(run)
            names = pipeline._expected(_model)
            for name in names - {"analysis.json"} - set(pipeline.FONT_PATHS):
                path = run / name
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(name.encode("utf-8"))
            return pipeline._inventory(run, names)

        patch.setattr(pipeline, "_render", stage)
        analysis = root / "analysis.json"
        analysis.write_bytes(pipeline.json_bytes(packet))
        built = pipeline.build_publication(source, output, root / "numeric", analysis)
        run = built["run"]
        expected = built["manifest"]["artifact_hashes"]
        first = pipeline.resolve_publication_current(output, source)
        assert first["html"] == run / "report.html"
        (run / "report.html").write_bytes(b"tampered report")
        try:
            pipeline.resolve_publication_current(output, source)
        except ValueError as exc:
            artifact_rejected = "artifact" in str(exc)
        else:
            artifact_rejected = False
        (run / "report.html").write_bytes(b"report.html")
        dependencies[0]["source_sha256"] = "f" * 64
        try:
            pipeline.resolve_publication_current(output, source)
        except ValueError as exc:
            source_rejected = "source dependencies" in str(exc)
        else:
            source_rejected = False
        dependencies[0]["source_sha256"] = packet["source_manifest"]["sources"][dependencies[0]["snapshot_id"]]["sha256"]
        patch.setattr(pipeline, "_sources", lambda _root: (_ for _ in ()).throw(ValueError("failed required acquisition")))
        try:
            pipeline.resolve_publication_current(output, source)
        except ValueError as exc:
            failed_acquisition_rejected = "failed required acquisition" in str(exc)
        else:
            failed_acquisition_rejected = False
        patch.setattr(pipeline, "_sources", lambda _root: deepcopy(dependencies))
        again = pipeline.resolve_publication_current(output, source)
    assert artifact_rejected and source_rejected and failed_acquisition_rejected
    assert again["html"] == first["html"]
    return {"bad_rejected": True, "clean_accepted": True,
            "producer": "pipeline_v2.build_publication+real_verify_sealed+live_source_service_double",
            "artifact": "report.html", "original_sha256": expected["report.html"],
            "failed_acquisition_rejected": failed_acquisition_rejected}


def run_prohibition_case(name: str, fixture: str | Path | None = None) -> dict:
    if name not in CASES:
        raise ValueError("unknown Phase 4 prohibition")
    active_case = "clean"
    if fixture is not None:
        path = Path(fixture)
        if not path.is_absolute():
            path = ROOT / path
        subject = json.loads(path.read_text(encoding="utf-8"))
        if (subject.get("synthetic") is not True or
                subject.get("case") not in (name, "clean") or
                subject.get("mutation") not in (CASES[name], None)):
            raise ValueError("fixture does not describe requested control")
        active_case = subject["case"]
    with TemporaryDirectory(prefix="brujula-phase4-prohibition-") as dirname:
        root = Path(dirname)
        if name == "pdf-fetch":
            result = _pdf_fetch(root)
        elif name == "stale-current":
            result = _stale_current(root)
        else:
            with MonkeyPatch.context() as patch:
                if name == "suppressed":
                    model, safe, canaries = _canary_model(patch)
                    result = _suppressed(model, safe, canaries, root)
                else:
                    result = _complement(_model(patch), root)
    return {"case": name, "synthetic": True, **result,
            "active_subject_valid": result["clean_accepted"] if active_case == "clean"
            else not result["bad_rejected"]}


if __name__ == "__main__":
    print(json.dumps(run_prohibition_case(sys.argv[1], sys.argv[2]),
                     sort_keys=True, ensure_ascii=False))
