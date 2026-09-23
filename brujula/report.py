"""Offline, deterministic static research reports for validated local bundles."""
from __future__ import annotations

from collections import defaultdict
from hashlib import sha256
from html import escape
import os
from pathlib import Path
import tempfile
from textwrap import fill
from typing import Any, Iterable

os.environ.setdefault("MPLCONFIGDIR", str(Path(tempfile.gettempdir()) / "brujula-matplotlib"))

import matplotlib

matplotlib.use("Agg")
from matplotlib import pyplot as plt
from matplotlib import rcParams


SYNTHETIC_WARNING = "DATOS SINTÉTICOS ILUSTRATIVOS"
_UNAVAILABLE = {"BLOCKED", "UNKNOWN"}


def _text(value: Any) -> str:
    """Render payload text without treating missing values as a numeric value."""
    if value is None or value == "":
        return "No disponible"
    return str(value)


def _number(value: Any, unit: str | None = None) -> str:
    if value is None:
        return "No disponible"
    if unit == "percent":
        return f"{float(value):,.1f}%"
    return f"{float(value):,.2f}".rstrip("0").rstrip(".")


def _markdown_text(value: Any) -> str:
    """Keep untrusted payload text literal in Markdown (including URL fields)."""
    return _text(value).replace("\\", "\\\\").replace("://", ":\\//").replace("\n", " ").replace("|", "\\|").replace("!", "\\!").replace("[", "\\[").replace("]", "\\]").replace("(", "\\(").replace(")", "\\)").replace("<", "\\<").replace(">", "\\>")


def _table(headers: Iterable[str], rows: Iterable[Iterable[Any]]) -> str:
    head = list(headers)
    body = [list(row) for row in rows]
    markdown = ["| " + " | ".join(head) + " |", "| " + " | ".join("---" for _ in head) + " |"]
    markdown.extend("| " + " | ".join(_markdown_text(value) for value in row) + " |" for row in body)
    return "\n".join(markdown)


def _html_table(headers: Iterable[str], rows: Iterable[Iterable[Any]]) -> str:
    cells = lambda tag, values: "<tr>" + "".join(f"<{tag}>{escape(_text(value))}</{tag}>" for value in values) + "</tr>"
    return "<table><thead>" + cells("th", headers) + "</thead><tbody>" + "".join(cells("td", row) for row in rows) + "</tbody></table>"


def _maps(dataset: dict[str, Any]) -> dict[str, dict[str, Any]]:
    dimensions = dataset.get("dimensions", {})
    return {
        "concepts": {(concept_type, item["id"]): item.get("label", item["id"]) for concept_type, name in (("field_of_study", "fields"), ("occupation", "occupations")) for item in dimensions.get(name, [])},
        "geographies": {item["id"]: item.get("label", item["id"]) for item in dimensions.get("geographies", [])},
        "periods": {item["id"]: item for item in dimensions.get("periods", [])},
        "metrics": {item["id"]: item for item in dataset.get("metrics", [])},
        "sources": {item["id"]: item for item in dataset.get("sources", [])},
    }


def _usable(row: dict[str, Any]) -> bool:
    return row.get("value") is not None and row.get("status") not in _UNAVAILABLE


def _display_row_value(row: dict[str, Any]) -> str:
    """Status is authoritative: unavailable rows never display supplied numbers."""
    if row.get("status") in _UNAVAILABLE:
        return "No disponible"
    return _number(row.get("value"), row.get("unit"))


def _safe_chart_name(prefix: str, value: Any) -> str:
    """Use a stable opaque token so payload IDs cannot affect output paths."""
    digest = sha256(_text(value).encode("utf-8")).hexdigest()[:16]
    return f"{prefix}-{digest}"


def _trend_points(series: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Each usable observation remains visible even when no segment is allowed."""
    return [row for row in series if _usable(row)]


def _trend_segments(series: list[dict[str, Any]], comparable: set[tuple[Any, Any]]) -> list[tuple[dict[str, Any], dict[str, Any]]]:
    """A segment exists only for an explicitly declared compatible adjacent pair."""
    return [(previous, current) for previous, current in zip(series, series[1:])
            if _usable(previous) and _usable(current) and (previous["id"], current["id"]) in comparable]


def _period_x_positions(periods: dict[str, dict[str, Any]]) -> tuple[list[dict[str, Any]], dict[str, int]]:
    ordered = sorted(periods.values(), key=lambda period: (period.get("start", ""), period.get("end", ""), period.get("id", "")))
    return ordered, {period["id"]: index for index, period in enumerate(ordered)}


def _chart_save(fig: Any, target: Path) -> list[str]:
    target.parent.mkdir(parents=True, exist_ok=True)
    rcParams["svg.hashsalt"] = "brujula-laboral-mx-v1"
    rcParams["svg.fonttype"] = "none"
    metadata = {"Creator": "Brujula Laboral MX", "Date": None}
    svg = target.with_suffix(".svg")
    png = target.with_suffix(".png")
    fig.savefig(svg, format="svg", metadata=metadata, bbox_inches="tight")
    fig.savefig(png, format="png", metadata=metadata, dpi=144, bbox_inches="tight")
    plt.close(fig)
    return [svg, png]


def _figure_metadata(rows: list[dict[str, Any]], maps: dict[str, dict[str, Any]]) -> str:
    periods = maps["periods"]
    sources = maps["sources"]
    names = lambda values: ", ".join(sorted({_text(value) for value in values}))
    dates = [periods.get(row.get("period_id"), {}) for row in rows]
    starts = [period.get("start") for period in dates if period.get("start")]
    ends = [period.get("end") for period in dates if period.get("end")]
    period_range = f"{min(starts)} a {max(ends)}" if starts and ends else "No disponible"
    return (f"Fuente: {names(sources.get(row.get('source_id'), {}).get('name') for row in rows)}; "
            f"periodo: {period_range}; geografia: {names(maps['geographies'].get(row.get('geography_id')) for row in rows)}; "
            f"unidad: {names(row.get('unit') for row in rows)}; poblacion: {names(row.get('population') for row in rows)}; "
            f"base de precio: {names(row.get('price_basis') for row in rows)}; precision: {names(row.get('precision_note') for row in rows)}")


def _decorate(fig: Any, ax: Any, metadata: str, bottom: float = 0.33) -> None:
    ax.grid(axis="y", alpha=0.25)
    fig.subplots_adjust(bottom=bottom)
    fig.text(0.5, 0.035, fill(f"{SYNTHETIC_WARNING} | {metadata}", width=130),
             ha="center", va="bottom", fontsize=7.5)


def _latest_metric_charts(dataset: dict[str, Any], maps: dict[str, dict[str, Any]], output: Path) -> tuple[list[Path], list[dict[str, Any]]]:
    periods = maps["periods"]
    national = next((ident for ident, label in maps["geographies"].items() if "nacional" in str(label).lower()), None)
    charts: list[Path] = []
    descriptions: list[dict[str, Any]] = []
    if national is None:
        return charts, descriptions
    for metric_id, metric in sorted(maps["metrics"].items()):
        rows = [row for row in dataset.get("observations", []) if row.get("concept_type") == "field_of_study" and row.get("geography_id") == national and row.get("metric_id") == metric_id]
        if not rows:
            continue
        latest_end = max(periods.get(row["period_id"], {}).get("end", "") for row in rows)
        selected_by_field = {row["concept_id"]: row for row in rows if periods.get(row["period_id"], {}).get("end") == latest_end}
        field_ids = sorted((item["id"] for item in dataset.get("dimensions", {}).get("fields", [])), key=lambda ident: maps["concepts"].get(("field_of_study", ident), ident))
        selected = [selected_by_field.get(field_id) for field_id in field_ids]
        usable = [row for row in selected if row is not None and _usable(row)]
        if not usable:
            continue
        labels = [maps["concepts"].get(("field_of_study", field_id), field_id) for field_id in field_ids]
        values = [float(row["value"]) for row in usable]
        fig, ax = plt.subplots(figsize=(8, 4.8))
        available_positions = [index for index, row in enumerate(selected) if row is not None and _usable(row)]
        bars = ax.bar(available_positions, values, color="#1d4e89")
        ax.set_title(f"{metric.get('label', metric_id)}: ultimo periodo nacional disponible")
        ax.set_ylabel(metric.get("unit", ""))
        ax.set_xticks(range(len(field_ids)), labels, rotation=18)
        for bar, value in zip(bars, values):
            ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height(), _number(value, metric.get("unit")), ha="center", va="bottom", fontsize=8)
        label_height = max(values) * 0.035
        for index, row in enumerate(selected):
            if row is None or not _usable(row):
                ax.text(index, label_height, "Sin dato", ha="center", va="bottom", fontsize=8, color="#555555")
        _decorate(fig, ax, _figure_metadata([row for row in selected if row is not None], maps))
        name = _safe_chart_name("latest-national", metric_id)
        files = _chart_save(fig, output / "charts" / name)
        charts.extend(files)
        descriptions.append({"name": name, "title": f"{metric.get('label', metric_id)}: ultimo periodo nacional disponible", "files": files, "headers": ["Campo de estudio", "Valor", "Periodo", "Geografia", "Unidad", "Fuente", "Poblacion", "Base de precio", "Precision", "Advertencia"], "rows": [[maps["concepts"].get(("field_of_study", field_id)), _display_row_value(row or {"status": "UNKNOWN"}), periods.get((row or {}).get("period_id"), {}).get("label"), maps["geographies"].get((row or {}).get("geography_id")), metric.get("unit"), maps["sources"].get((row or {}).get("source_id"), {}).get("name"), (row or {}).get("population"), (row or {}).get("price_basis"), (row or {}).get("precision_note"), SYNTHETIC_WARNING] for field_id, row in zip(field_ids, selected)]})
    return charts, descriptions


def _income_trend(dataset: dict[str, Any], maps: dict[str, dict[str, Any]], comparisons: list[dict[str, Any]], output: Path) -> tuple[list[Path], dict[str, Any] | None]:
    periods = maps["periods"]
    rows = [row for row in dataset.get("observations", []) if row.get("concept_type") == "field_of_study" and row.get("metric_id") == "mean_monthly_income"]
    usable = [row for row in rows if _usable(row)]
    if not usable:
        return [], None
    comparable = {(item.get("previous_id"), item.get("current_id")) for item in comparisons if item.get("comparable") is True}
    chronological_periods, x_positions = _period_x_positions(periods)
    grouped: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        grouped[(row.get("concept_id"), row.get("geography_id"))].append(row)
    fig, ax = plt.subplots(figsize=(9, 5))
    table_rows: list[list[Any]] = []
    plotted = False
    colors = plt.rcParams["axes.prop_cycle"].by_key()["color"]
    for series_index, ((concept_id, geography_id), series) in enumerate(sorted(grouped.items())):
        series.sort(key=lambda row: periods.get(row.get("period_id"), {}).get("start", ""))
        label = f"{maps['concepts'].get(('field_of_study', concept_id), concept_id)} — {maps['geographies'].get(geography_id)}"
        color = colors[series_index % len(colors)]
        visible = _trend_points(series)
        if visible:
            ax.scatter([x_positions.get(row.get("period_id")) for row in visible],
                       [float(row["value"]) for row in visible], label=label, color=color)
            plotted = True
        for previous, current in _trend_segments(series, comparable):
            ax.plot([x_positions.get(previous.get("period_id")), x_positions.get(current.get("period_id"))], [float(previous["value"]), float(current["value"])], color=color)
        for index, row in enumerate(series):
            connected = index > 0 and _usable(series[index - 1]) and _usable(row) and (series[index - 1]["id"], row["id"]) in comparable
            table_rows.append([maps["concepts"].get(("field_of_study", concept_id)), maps["geographies"].get(geography_id), periods.get(row.get("period_id"), {}).get("label"), _display_row_value(row), "Disponible" if _usable(row) else "No disponible", "Conectado con comparacion declarada" if connected else ("Punto aislado; no hay par comparable declarado" if _usable(row) else "Brecha por valor o estado no disponible"), row.get("population"), row.get("price_basis"), row.get("precision_note"), SYNTHETIC_WARNING])
    if not plotted:
        plt.close(fig)
        return [], None
    ax.set_title("Ingreso mensual medio por campo y geografia")
    ax.set_ylabel("MXN/month")
    ax.set_xticks(range(len(chronological_periods)), [period.get("label", period["id"]) for period in chronological_periods])
    ax.legend(fontsize=7, loc="upper center", bbox_to_anchor=(0.5, -0.14), ncol=2)
    _decorate(fig, ax, _figure_metadata(rows, maps), bottom=0.5)
    files = _chart_save(fig, output / "charts" / "income-trends")
    return files, {"name": "income-trends", "title": "Ingreso mensual medio por campo y geografia", "files": files, "headers": ["Campo de estudio", "Geografia", "Periodo", "Valor", "Disponibilidad", "Tratamiento de linea", "Poblacion", "Base de precio", "Precision", "Advertencia"], "rows": table_rows}


def _blocked_report(payload: dict[str, Any], output: Path) -> dict[str, Any]:
    diagnostic = _text(payload.get("error") or payload.get("quality", {}).get("checks", [{}])[0].get("message"))
    markdown = f"# Brújula Laboral MX — BLOQUEADO\n\n## Diagnóstico\n\nEstado: `BLOCKED`. No se publican cifras, tablas de datos ni gráficas.\n\nMotivo: {_markdown_text(diagnostic)}\n"
    html = "<!doctype html><html lang=\"es\"><meta charset=\"utf-8\"><title>Brújula Laboral MX — BLOQUEADO</title><body><main><h1>Brújula Laboral MX — BLOQUEADO</h1><h2>Diagnóstico</h2><p>Estado: <code>BLOCKED</code>. No se publican cifras, tablas de datos ni gráficas.</p><p>Motivo: " + escape(diagnostic) + "</p></main></body></html>"
    (output / "report.md").write_text(markdown, encoding="utf-8")
    (output / "report.html").write_text(html, encoding="utf-8")
    return {"markdown": "report.md", "html": "report.html", "charts": []}


def render_report(payload: dict[str, Any], output_dir: Path | str) -> dict[str, Any]:
    """Render local Markdown, escaped HTML, and paired SVG/PNG chart artifacts."""
    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)
    if payload.get("status") == "BLOCKED" or not payload.get("publishable") or not isinstance(payload.get("dataset"), dict):
        return _blocked_report(payload, output)
    dataset = payload["dataset"]
    maps = _maps(dataset)
    chart_paths, figures = _latest_metric_charts(dataset, maps, output)
    trend_paths, trend = _income_trend(dataset, maps, payload.get("comparisons", []), output)
    chart_paths.extend(trend_paths)
    if trend:
        figures.append(trend)
    relative = [str(path.relative_to(output)).replace("\\", "/") for path in chart_paths]
    freshness = payload.get("quality", {}).get("freshness", {})
    source_rows = [[source.get("name"), source.get("access_status"), source.get("license"), source.get("terms_url"), source.get("url"), source.get("population"), source.get("notes")] for source in dataset.get("sources", [])]
    observation_rows = [[maps["concepts"].get((row.get("concept_type"), row.get("concept_id"))), row.get("concept_type"), maps["geographies"].get(row.get("geography_id")), maps["periods"].get(row.get("period_id"), {}).get("label"), maps["metrics"].get(row.get("metric_id"), {}).get("label"), _display_row_value(row), row.get("status"), row.get("unit"), row.get("price_basis"), row.get("population"), row.get("precision_note"), SYNTHETIC_WARNING] for row in dataset.get("observations", []) if row.get("status") != "BLOCKED"]
    markdown = [f"# {_markdown_text(dataset.get('label'))}", "", f"> **{SYNTHETIC_WARNING}**. Este reporte no representa estimaciones del mercado laboral real.", "", "## Alcance y frescura", "", f"- Estado del bundle: `{_markdown_text(payload.get('status'))}`", f"- Ejecutado: `{_markdown_text(payload.get('generated_at'))}`", f"- Frescura por periodo de negocio: `{_markdown_text(freshness.get('latest_period_end'))}` (estado: `{_markdown_text(freshness.get('status'))}`; edad: `{_markdown_text(freshness.get('age_days'))}` días)", "- Campo y ocupación son conceptos distintos; los bridges editoriales no crean equivalencia.", "", "## Fuentes y condiciones", "", _table(["Fuente", "Acceso", "Licencia", "Términos", "URL", "Población", "Notas"], source_rows), "", "## Observaciones disponibles y brechas", "", _table(["Concepto", "Tipo", "Geografía", "Periodo", "Métrica", "Valor", "Estado", "Unidad", "Base", "Población", "Precisión", "Advertencia"], observation_rows)]
    for figure in figures:
        svg = next(path for path in figure["files"] if path.suffix == ".svg")
        markdown.extend(["", f"## {_markdown_text(figure['title'])}", "", f"> **{SYNTHETIC_WARNING}**. La tabla conserva fuente, periodo, geografía, unidad, población, base y precisión.", "", f"![{_markdown_text(figure['title'])}]({svg.relative_to(output).as_posix()})", "", _table(figure["headers"], figure["rows"])])
    insights = payload.get("insights", [])
    if insights:
        markdown.extend(["", "## Paquetes de insight", ""])
        for insight in insights:
            markdown.extend([f"### {_markdown_text(insight.get('title'))}", "", f"- Observación: {_markdown_text(insight.get('observation'))}", f"- Interpretación: {_markdown_text(insight.get('interpretation'))}", f"- Recomendación: {_markdown_text(insight.get('recommendation'))}", f"- Incertidumbres: {_markdown_text('; '.join(insight.get('unknowns', [])))}", f"- Evidencia: {_markdown_text(', '.join(insight.get('evidence_refs', [])))}", ""])
    markdown_text = "\n".join(markdown) + "\n"
    html_parts = ["<!doctype html><html lang=\"es\"><meta charset=\"utf-8\"><title>" + escape(_text(dataset.get("label"))) + "</title><body><main>", "<h1>" + escape(_text(dataset.get("label"))) + "</h1>", "<p><strong>" + escape(SYNTHETIC_WARNING) + "</strong>. Este reporte no representa estimaciones del mercado laboral real.</p>", "<h2>Alcance y frescura</h2><ul><li>Estado del bundle: <code>" + escape(_text(payload.get("status"))) + "</code></li><li>Frescura por periodo de negocio: " + escape(_text(freshness.get("latest_period_end"))) + "</li><li>Campo y ocupación son conceptos distintos; los bridges editoriales no crean equivalencia.</li></ul>", "<h2>Fuentes y condiciones</h2>" + _html_table(["Fuente", "Acceso", "Licencia", "Términos", "URL", "Población", "Notas"], source_rows), "<h2>Observaciones disponibles y brechas</h2>" + _html_table(["Concepto", "Tipo", "Geografía", "Periodo", "Métrica", "Valor", "Estado", "Unidad", "Base", "Población", "Precisión", "Advertencia"], observation_rows)]
    for figure in figures:
        svg = next(path for path in figure["files"] if path.suffix == ".svg")
        html_parts.extend(["<section><h2>" + escape(figure["title"]) + "</h2><p><strong>" + escape(SYNTHETIC_WARNING) + "</strong>. La tabla alternativa conserva los metadatos de la figura.</p><img src=\"" + escape(svg.relative_to(output).as_posix(), quote=True) + "\" alt=\"" + escape(figure["title"], quote=True) + "\">" + _html_table(figure["headers"], figure["rows"]) + "</section>"])
    if insights:
        html_parts.append("<section><h2>Paquetes de insight</h2>")
        for insight in insights:
            html_parts.append("<article><h3>" + escape(_text(insight.get("title"))) + "</h3><p>Observación: " + escape(_text(insight.get("observation"))) + "</p><p>Interpretación: " + escape(_text(insight.get("interpretation"))) + "</p><p>Recomendación: " + escape(_text(insight.get("recommendation"))) + "</p><p>Incertidumbres: " + escape(_text("; ".join(insight.get("unknowns", [])))) + "</p><p>Evidencia: " + escape(_text(", ".join(insight.get("evidence_refs", [])))) + "</p></article>")
        html_parts.append("</section>")
    html_text = "".join(html_parts) + "</main></body></html>"
    (output / "report.md").write_text(markdown_text, encoding="utf-8")
    (output / "report.html").write_text(html_text, encoding="utf-8")
    return {"markdown": "report.md", "html": "report.html", "charts": relative}
