"""Render original, static charts from the audited public research exports."""

from __future__ import annotations

import csv
import hashlib
from html import escape
import io
import json
import math
from pathlib import Path


TREND_FIGURE = "figure:eight-quarter-trends"
TERRITORY_FIGURE = "figure:state-availability"
FIELDS = (("033100", "Derecho", "#3659d9"),
          ("032100", "Comunicación y periodismo", "#087f75"),
          ("031300", "Ciencias políticas", "#ad5b49"))
METRICS = (("employment_rate", "Tasa de ocupación", "%"),
           ("positive_income_coverage", "Cobertura de ingreso positivo conocido", "%"),
           ("positive_income_mean", "Ingreso mensual medio positivo conocido", "MXN/mes"))
EDITORIAL = {
    "employment_rate": ("empleo", "Alrededor de 3 de cada 4 personas con estos estudios tienen alguna ocupación",
                        "La medida usa como denominador a todas las personas del grupo con situación laboral conocida, incluidas las inactivas. No mide empleo relacionado con la carrera ni calidad laboral; el resto incluye tanto personas desocupadas como inactivas."),
    "positive_income_coverage": ("cobertura-ingreso", "Menos de la mitad de las personas ocupadas tienen ingreso positivo exacto conocido",
                                 "La falta de un ingreso exacto conocido no equivale a ingreso cero."),
    "positive_income_mean": ("ingreso", "El ingreso medio observado ronda 18–20 mil pesos mensuales",
                             "Promedio nominal entre personas ocupadas con ingreso positivo exacto conocido; no es oferta salarial ni resultado de egresados."),
}


def _read_csv(path: Path) -> tuple[list[dict[str, str]], str]:
    content = path.read_bytes()
    rows = list(csv.DictReader(io.StringIO(content.decode("utf-8-sig"))))
    if not rows:
        raise ValueError(f"CSV vacío: {path.name}")
    return rows, hashlib.sha256(content).hexdigest()


def _number(row: dict[str, str], key: str) -> float | None:
    raw = row[key].strip()
    if not raw:
        return None
    value = float(raw)
    if not math.isfinite(value):
        raise ValueError(f"valor no finito en {row['record_id']}: {key}")
    return value


def _fmt(value: float | None, unit: str, digits: int = 1) -> str:
    if value is None:
        return "No disponible"
    if unit == "MXN/mes":
        return f"${value:,.2f} MXN/mes" if digits == 2 else f"${value:,.0f} MXN/mes"
    return f"{value:.{digits}f} %"


def _axes(metric: str, rows: list[dict[str, str]]) -> tuple[float, float]:
    if metric != "positive_income_mean":
        return 0.0, 100.0
    highs = [_number(row, "ci90_upper") for row in rows]
    maximum = max((value for value in highs if value is not None), default=0)
    return 0.0, max(5000.0, math.ceil(maximum / 5000) * 5000.0)


def _chart_svg(rows: list[dict[str, str]], *, title: str, metric: str,
               color: str, limits: tuple[float, float]) -> str:
    width, height = 420, 280
    left, right, top, bottom = 48, 398, 20, 224
    low, high = limits
    x = lambda index: left + index * (right - left) / 7
    y = lambda value: bottom - (value - low) * (bottom - top) / (high - low)
    parts = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" role="img" aria-label="{escape(title, quote=True)}">',
             f"<title>{escape(title)}</title><desc>México, cohorte profesional terminada, edad conocida 15+, todos los sexos registrados. ENOE 2024-T3 a 2026-T2. Intervalos del 90%, precisión no oficial REVIEW. Una cruz señala un dato no disponible.</desc>",
             '<rect width="420" height="280" fill="#fff"/>']
    for tick in range(5):
        value = low + (high - low) * tick / 4
        pos = y(value)
        label = f"{value:,.0f}"
        parts.append(f'<path d="M{left} {pos:.1f}H{right}" stroke="#e0e7ef" stroke-width="1"/>')
        parts.append(f'<text x="40" y="{pos + 4:.1f}" text-anchor="end" fill="#55647a" font-size="14" font-family="system-ui">{label}</text>')
    unit_label = "MXN/mes nominales" if metric == "positive_income_mean" else "%"
    parts.append(f'<text x="48" y="12" fill="#55647a" font-size="12" font-family="system-ui">{unit_label}</text>')
    previous: tuple[float, float] | None = None
    for index, row in enumerate(rows):
        point, ci_low, ci_high = (_number(row, key) for key in ("value", "ci90_lower", "ci90_upper"))
        xpos = x(index)
        period = row["period_id"]
        short = "T" + period[-1]
        parts.append(f'<text x="{xpos:.1f}" y="246" text-anchor="middle" fill="#55647a" font-size="16" font-family="system-ui">{escape(short)}</text>')
        if point is None:
            previous = None
            parts.append(f'<text x="{xpos:.1f}" y="{bottom-8}" text-anchor="middle" fill="#55647a" font-size="15" font-family="system-ui">×</text>')
            continue
        ypos = y(point)
        if previous is not None:
            parts.append(f'<path d="M{previous[0]:.1f} {previous[1]:.1f}L{xpos:.1f} {ypos:.1f}" fill="none" stroke="{color}" stroke-width="2.5"/>')
        if ci_low is not None and ci_high is not None:
            a, b = y(ci_high), y(ci_low)
            parts.append(f'<path d="M{xpos:.1f} {a:.1f}V{b:.1f}M{xpos-4:.1f} {a:.1f}h8M{xpos-4:.1f} {b:.1f}h8" stroke="{color}" stroke-opacity=".53" stroke-width="2" fill="none"/>')
        parts.append(f'<circle cx="{xpos:.1f}" cy="{ypos:.1f}" r="4.2" fill="{color}" stroke="#fff" stroke-width="1.5"/>')
        previous = (xpos, ypos)
    years = sorted({row["period_id"][:4] for row in rows})
    for year in years:
        indices = [i for i, row in enumerate(rows) if row["period_id"].startswith(year)]
        center = sum(x(i) for i in indices) / len(indices)
        parts.append(f'<text x="{center:.1f}" y="270" text-anchor="middle" fill="#55647a" font-size="15" font-family="system-ui">{year}</text>')
    parts.append('</svg>')
    return "".join(parts)


def _table(rows: list[dict[str, str]], *, unit: str, caption: str,
           territory: bool = False) -> str:
    columns = (("geography_id", "Código"), ("geography_label", "Entidad")) if territory else (("field_label", "Campo"), ("period_id", "Periodo"))
    head = "".join(f"<th scope=\"col\">{label}</th>" for _, label in columns)
    head += "<th scope=\"col\">Valor</th><th scope=\"col\">IC 90 %</th><th scope=\"col\">Estado</th><th scope=\"col\">Registro</th>"
    body = []
    for row in rows:
        value, lower, upper = (_number(row, key) for key in ("value", "ci90_lower", "ci90_upper"))
        interval = f"{_fmt(lower, unit, 2)}–{_fmt(upper, unit, 2)}" if lower is not None and upper is not None else "No disponible"
        cells = "".join(f"<td>{escape(row[key])}</td>" for key, _ in columns)
        cells += f"<td>{escape(_fmt(value, unit, 2))}</td><td>{escape(interval)}</td><td>{escape(row['status'])}</td><td><code>{escape(row['record_id'])}</code></td>"
        body.append(f"<tr>{cells}</tr>")
    return f'<div class="data-table-scroll" tabindex="0" role="region" aria-label="Tabla de datos con desplazamiento horizontal"><table><caption>{escape(caption)}</caption><thead><tr>{head}</tr></thead><tbody>{"".join(body)}</tbody></table></div>'


def _territory_svg(rows: list[dict[str, str]], part: int) -> str:
    title = f"Tasa de ocupación en Derecho, entidades {part*16+1} a {part*16+len(rows)}"
    pieces = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 600 650" role="img" aria-label="{escape(title, quote=True)}">',
              f'<title>{escape(title)}</title><rect width="600" height="650" fill="#fff"/>']
    for tick in (0, 25, 50, 75, 100):
        xpos = 220 + tick * 2.65
        pieces.append(f'<path d="M{xpos:.1f} 34V622" stroke="#e0e7ef"/>')
        pieces.append(f'<text x="{xpos:.1f}" y="24" text-anchor="middle" fill="#55647a" font-size="12" font-family="system-ui">{tick}%</text>')
    for index, row in enumerate(rows):
        ypos = 56 + index * 36
        label = f"{row['geography_id']} · {row['geography_label']}"
        pieces.append(f'<text x="210" y="{ypos+4}" text-anchor="end" fill="#172235" font-size="13" font-family="system-ui">{escape(label)}</text>')
        value, lower, upper = (_number(row, key) for key in ("value", "ci90_lower", "ci90_upper"))
        if value is None:
            pieces.append(f'<text x="226" y="{ypos+4}" fill="#55647a" font-size="12" font-family="system-ui">No disponible</text>')
            continue
        center = 220 + value * 2.65
        if lower is not None and upper is not None:
            a, b = 220 + lower * 2.65, 220 + upper * 2.65
            pieces.append(f'<path d="M{a:.1f} {ypos}H{b:.1f}M{a:.1f} {ypos-5}v10M{b:.1f} {ypos-5}v10" stroke="#087f75" stroke-opacity=".75" stroke-width="2"/>')
        pieces.append(f'<circle cx="{center:.1f}" cy="{ypos}" r="4" fill="#087f75"/>')
        pieces.append(f'<text x="500" y="{ypos+4}" fill="#172235" font-size="12" font-family="system-ui">{value:.1f}%</text>')
    pieces.append('</svg>')
    return "".join(pieces)


def _select(records: list[dict[str, str]], links: list[dict[str, str]], figure: str,
            expected: int) -> list[dict[str, str]]:
    all_ids = [row["record_id"] for row in records]
    if len(all_ids) != len(set(all_ids)):
        raise ValueError("public-records.csv contiene record_id duplicados")
    ids = [link["record_id"] for link in links if link["figure_id"] == figure]
    if len(ids) != expected or len(ids) != len(set(ids)):
        raise ValueError(f"vínculos incompletos o duplicados: {figure}")
    index = {row["record_id"]: row for row in records}
    missing = set(ids) - index.keys()
    if missing:
        raise ValueError(f"registro de figura no publicado: {figure}: {sorted(missing)[0]}")
    return [index[record_id] for record_id in ids]


def _editorial_insights(trend: list[dict[str, str]]) -> tuple[list[dict], str]:
    """Derive the three editorial statements only from linked 2026-Q2 rows."""
    insights = []
    markup = []
    for number, (metric, _, unit) in enumerate(METRICS, 1):
        section_id, title, interpretation = EDITORIAL[metric]
        rows = [row for row in trend if row["metric_id"] == metric and row["period_id"] == "2026-Q2"]
        by_field = {row["field_of_study_id"]: row for row in rows}
        if len(rows) != len(FIELDS) or set(by_field) != {field for field, _, _ in FIELDS}:
            raise ValueError(f"faltan filas editoriales 2026-Q2: {metric}")
        fields = []
        for field, name, _ in FIELDS:
            row = by_field[field]
            value = _number(row, "value")
            if value is None or row["status"] != "REVIEW":
                raise ValueError(f"valor editorial no publicable: {metric}: {field}")
            fields.append({"field_of_study_id": field, "field_label": name,
                           "value": value, "record_id": row["record_id"]})
        values = [field["value"] for field in fields]
        if metric == "employment_rate" and not all(70 <= value <= 80 for value in values):
            raise ValueError("la afirmación ocupación ronda 75 % no se sostiene")
        if metric == "positive_income_coverage" and not all(0 <= value < 50 for value in values):
            raise ValueError("la afirmación cobertura menor a la mitad no se sostiene")
        if metric == "positive_income_mean" and not all(0 < value < 100000 for value in values):
            raise ValueError("ingreso editorial fuera del rango válido")
        if metric == "positive_income_mean" and not all(18000 <= value < 20000 for value in values):
            raise ValueError("la afirmación ingreso ronda 18–20 mil no se sostiene")
        if unit == "MXN/mes":
            range_text = f"${min(values):,.0f}–${max(values):,.0f} MXN/mes"
            point = lambda value: f"${value:,.0f}"
        else:
            range_text = f"{min(values):.1f}–{max(values):.1f} %"
            point = lambda value: f"{value:.1f} %"
        detail = "; ".join(f"{field['field_label']}: {point(field['value'])}" for field in fields)
        insights.append({"metric_id": metric, "section_id": section_id, "period_id": "2026-Q2",
                         "unit": unit, "range": {"minimum": min(values), "maximum": max(values),
                                                "display": range_text}, "fields": fields})
        markup.append(f'<article class="takeaway"><span class="takeaway-number">{number:02d}</span>'
                      f'<h3>{escape(title)}</h3><p class="takeaway-value">{escape(range_text)}</p>'
                      f'<p>{escape(detail)}. {escape(interpretation)}</p>'
                      f'<a href="#{section_id}">Ver datos y método</a></article>')
    return insights, '<div class="takeaways">' + "".join(markup) + '</div>'


def render_charts(stage: Path) -> dict[str, str]:
    """Write static SVG/trace files and return safe HTML fragments for the site."""
    exports = stage / "research" / "exports"
    records, records_hash = _read_csv(exports / "public-records.csv")
    links, links_hash = _read_csv(exports / "figure-record-links.csv")
    trend = _select(records, links, TREND_FIGURE, 72)
    territory = _select(records, links, TERRITORY_FIGURE, 32)
    periods = sorted({row["period_id"] for row in trend})
    if len(periods) != 8:
        raise ValueError("tendencias requieren ocho periodos")
    expected_pairs = {(metric, field, period) for metric, _, _ in METRICS for field, _, _ in FIELDS for period in periods}
    actual_pairs = [(r["metric_id"], r["field_of_study_id"], r["period_id"]) for r in trend]
    if set(actual_pairs) != expected_pairs or len(actual_pairs) != len(set(actual_pairs)):
        raise ValueError("registros de tendencia no forman nueve series completas")
    for row in trend:
        if row["geography_id"] != "mx" or row["population_id"] != "completed_professional_known_age" or row["recorded_sex_id"] != "all":
            raise ValueError("universo o geografía inesperados en tendencias")
    territory.sort(key=lambda row: row["geography_id"])
    if [row["geography_id"] for row in territory] != [f"{i:02d}" for i in range(1, 33)]:
        raise ValueError("la figura territorial no contiene las 32 entidades")
    if any(row["metric_id"] != "employment_rate" or row["field_of_study_id"] != "033100" or row["period_id"] != "2026-Q2" for row in territory):
        raise ValueError("dimensiones inesperadas en figura territorial")
    insights, summary_markup = _editorial_insights(trend)
    charts = stage / "charts"
    charts.mkdir(exist_ok=True)
    trace = {"schema_version": "1.0", "figures": {TREND_FIGURE: trend, TERRITORY_FIGURE: territory},
             "editorial_insights": insights,
             "source_sha256": {"public-records.csv": records_hash, "figure-record-links.csv": links_hash}}
    (charts / "chart-data.json").write_text(json.dumps(trace, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    groups = []
    for metric, title, unit in METRICS:
        metric_rows = [r for r in trend if r["metric_id"] == metric]
        limits = _axes(metric, metric_rows)
        cards = []
        for field, name, color in FIELDS:
            series = sorted((r for r in metric_rows if r["field_of_study_id"] == field), key=lambda r: r["period_id"])
            filename = f"trend-{metric}-{field}.svg"
            (charts / filename).write_text(_chart_svg(series, title=f"{title} · {name}", metric=metric, color=color, limits=limits), encoding="utf-8")
            last = series[-1]
            value, lower, upper = (_number(last, key) for key in ("value", "ci90_lower", "ci90_upper"))
            interval = f"IC 90 %: {_fmt(lower, unit)} a {_fmt(upper, unit)}" if lower is not None and upper is not None else "IC 90 % no disponible"
            cards.append(f'<article class="chart-card"><h4>{escape(name)}</h4><p class="chart-latest"><strong>{escape(_fmt(value, unit))}</strong><span>{escape(last["period_id"])} · {escape(interval)}</span></p><img src="charts/{filename}" alt="Serie trimestral de {escape(title)} para {escape(name)}; datos completos en la tabla siguiente" width="420" height="280" loading="lazy"><p class="chart-open"><a href="charts/{filename}">Abrir gráfica en tamaño completo</a></p></article>')
        metric_rows.sort(key=lambda r: (r["field_of_study_id"], r["period_id"]))
        table = _table(metric_rows, unit=unit, caption=f"{title}: ocho trimestres y tres campos de estudio")
        section_id, takeaway_title, interpretation = EDITORIAL[metric]
        groups.append(f'<section class="chart-group" id="{section_id}"><h3>{escape(takeaway_title)}</h3>'
                      f'<p class="chart-group-metric">{escape(title)}</p>'
                      f'<p class="chart-group-note">{escape(interpretation)}</p>'
                      f'<div class="chart-card-grid">{"".join(cards)}</div>'
                      f'<details><summary>Ver los 24 registros e intervalos</summary>{table}</details></section>')
    territory_cards = []
    for part in range(2):
        filename = f"territory-{part+1}.svg"
        (charts / filename).write_text(_territory_svg(territory[part*16:(part+1)*16], part), encoding="utf-8")
        territory_cards.append(f'<figure class="territory-panel"><img src="charts/{filename}" alt="Tasa de ocupación en Derecho, entidades {part*16+1} a {(part+1)*16}; datos completos en la tabla" width="600" height="650" loading="lazy"><figcaption>Entidades {part*16+1}–{(part+1)*16} · <a href="charts/{filename}">Abrir gráfica en tamaño completo</a></figcaption></figure>')
    hero_rows = sorted((r for r in trend if r["metric_id"] == "employment_rate" and r["field_of_study_id"] == "033100"), key=lambda r: r["period_id"])
    hero = hero_rows[-1]
    value, lower, upper = (_number(hero, key) for key in ("value", "ci90_lower", "ci90_upper"))
    if hero["period_id"] != "2026-Q2" or value is None:
        raise ValueError("registro destacado de Derecho ausente")
    hero_markup = (f'<div class="hero-stat"><p class="eyebrow">Dato destacado · Derecho · 2026-Q2</p>'
                   f'<strong>{escape(_fmt(value, "%", 2))}</strong><p>Tasa de ocupación · IC 90 % del proyecto: {escape(_fmt(lower, "%"))} a {escape(_fmt(upper, "%"))}</p>'
                   f'<img src="charts/trend-employment_rate-033100.svg" alt="Tasa de ocupación trimestral de Derecho; datos completos en la sección de tendencias" width="420" height="280">'
                   f'<p class="chart-note">Estimación en revisión; precisión no oficial. Personas con estudios profesionales terminados y edad conocida de 15 años o más. <a href="research/report.html#{TREND_FIGURE}">Ver investigación y método</a>.</p></div>')
    trend_markup = ('<div class="chart-section-intro"><p>ENOE · México · personas con estudios profesionales terminados · ocho trimestres. '
                    'IC 90 % del proyecto, en revisión y no oficial.</p>'
                    '<p><a href="research/report.html#figure:eight-quarter-trends">Ver figura del informe</a> · '
                    '<a href="charts/chart-data.json" download>Descargar registros públicos usados</a></p></div>' + ''.join(groups))
    available = sum(_number(row, "value") is not None and row["status"] == "REVIEW"
                    for row in territory)
    territory_markup = (f'<h3>{available} de 32 entidades tienen cifra publicable</h3>'
                        '<p>Derecho · 2026-Q2 · tasa de ocupación por entidad. Códigos oficiales en orden. '
                        'IC 90 % del proyecto; precisión no oficial. Las ausencias se muestran como no disponibles; '
                        'las diferencias descriptivas no establecen causas.</p>'
                        '<p class="territory-mobile-note">En pantalla pequeña, desplaza cada gráfica horizontalmente para leer las entidades.</p>'
                        f'<div class="territory-grid">{"".join(territory_cards)}</div>'
                        '<details><summary>Ver los 32 registros estatales e intervalos</summary>'
                        + _table(territory, unit="%", caption="Tasa de ocupación de Derecho, 2026-Q2, por entidad", territory=True) + '</details>'
                        '<p><a href="research/report.html#figure:state-availability">Ver figura del informe</a></p>')
    return {"hero_markup": hero_markup, "summary_markup": summary_markup,
            "trend_markup": trend_markup, "territory_markup": territory_markup}
