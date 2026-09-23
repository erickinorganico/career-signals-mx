"""Evidence-bound static Spanish editorial report from a validated public model."""

from __future__ import annotations

from decimal import Decimal, ROUND_HALF_UP
from html import escape
import hashlib
import io
from pathlib import Path
import re
import shutil
from urllib.parse import quote

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib import font_manager

from .publication_v2 import validate_publication_model
from .resources import font_path

FONT_NAMES = ('DejaVuSans.ttf', 'DejaVuSans-Bold.ttf',
              'DejaVuSerif.ttf', 'DejaVuSerif-Bold.ttf', 'LICENSE_DEJAVU')
FOCAL = (('033100', 'Derecho', 'derecho'),
         ('032100', 'Comunicación y periodismo', 'comunicacion'),
         ('031300', 'Ciencias políticas', 'politicas'))
SECTIONS = (
    ('hallazgos', '¿Qué puede responder la evidencia?'),
    ('lectura', '¿Cómo se debe leer este informe?'),
    ('contexto', '¿Cuál es el contexto nacional?'),
    ('derecho', '¿Qué muestra Derecho?'),
    ('comunicacion', '¿Qué muestra Comunicación y periodismo?'),
    ('politicas', '¿Qué muestra Ciencias políticas?'),
    ('evolucion', '¿Cómo evolucionaron los ocho trimestres?'),
    ('sexo-territorio', '¿Qué permiten describir el sexo registrado y las entidades?'),
    ('otros-campos', '¿Qué muestran los otros campos identificables?'),
    ('cobertura', '¿Qué cobertura y exclusiones limitan las cifras?'),
    ('metodos', '¿Cómo se estimaron y revisaron las cifras?'),
    ('fuentes', '¿Cuáles son las fuentes exactas?'),
    ('evidencia', '¿Dónde está la evidencia completa?'),
)
FIGURE_TITLES = {
    'national-context': '¿Qué muestra el contexto nacional?',
    'focal-latest': '¿Cómo se describen los tres campos en el trimestre más reciente?',
    'eight-quarter-trends': '¿Cómo se movieron las series disponibles?',
    'recorded-sex': '¿Qué se observa por sexo registrado?',
    'state-availability': '¿Qué datos de Derecho están disponibles por entidad?',
    'other-fields': '¿Qué datos hay para otros campos identificables?',
}
COLORS = {'REVIEW': '#145A66', 'MEASURED': '#145A66',
          'UNKNOWN': '#687985', 'BLOCKED': '#687985'}


def _number(value: int | float | None, places: int = 2) -> str:
    if value is None:
        return 'no disponible'
    quant = Decimal('1').scaleb(-places)
    rounded = Decimal(str(value)).quantize(quant, rounding=ROUND_HALF_UP)
    return f'{rounded:,.{places}f}'.replace(',', 'X').replace('.', ',').replace('X', ' ')


def _value(record: dict) -> str:
    value = record['value']
    if value is None:
        return 'No disponible'
    unit = record['unit']
    if unit == 'percent':
        return f'{_number(value)} %'
    if unit == 'MXN/month':
        return f'{_number(value)} MXN/mes nominales'
    if unit == 'people':
        return f'{_number(value, 0)} personas'
    if unit == 'hours/week':
        return f'{_number(value)} horas/semana'
    raise ValueError(f'Unidad no autorizada: {unit}')


def _public_point(record_id: str, item: dict) -> dict:
    record, display = item['record'], item['display']
    precision = record['precision']
    return {
        'record_id': record_id, 'field_code': record['field_of_study_id'],
        'label': display.get('field') or display.get('geography') or display.get('metric'),
        'field': display.get('field', ''), 'metric': display['metric'],
        'geography': display['geography'], 'period': display['period'],
        'population': display['population'], 'recorded_sex': display['recorded_sex'],
        'value': record['value'], 'value_text': _value(record),
        'unit': record['unit'], 'status': record['status'], 'reason': record['reason'],
        'ci90_lower': precision['ci90_lower'], 'ci90_upper': precision['ci90_upper'],
        'cv': precision['coefficient_variation'], 'sample_size': record['sample_size'],
        'source_id': record['source_snapshot_id'], 'evidence_refs': record['evidence_refs'],
        'synthetic': record['synthetic'], 'metric_id': record['metric_id'],
        'geography_id': record['geography_id'], 'recorded_sex_id': record['recorded_sex_id'],
    }


def _figure_order(point: dict, periods: list[str]) -> tuple:
    period = point['period']
    return (point['field_code'], point['metric_id'], periods.index(period) if period in periods else 99,
            point['geography_id'], point['recorded_sex_id'], point['record_id'])


def build_editorial_document(model: dict) -> dict:
    """Validate and bind every visible datum to canonical public evidence."""
    errors = validate_publication_model(model)
    if errors:
        raise ValueError(f'Invalid public publication model: {errors[:3]}')
    opening = model['opening_claim_ids']
    if len(opening) > 3 or len(opening) != len(set(opening)):
        raise ValueError('Opening claims must be unique and at most three')
    claims = {c['claim_id']: c for c in model['claims']}
    if any(cid not in claims for cid in opening):
        raise ValueError('Opening claim missing')
    periods = model['profiles']['periods']
    if len(periods) != 8 or periods != sorted(periods):
        raise ValueError('Eight ordered quarters required')
    figures = []
    slugs = set()
    for link in model['figure_links']:
        figure_id = link['figure_id']
        if not figure_id.startswith('figure:'):
            raise ValueError('Invalid figure ID')
        slug = figure_id[len('figure:'):]
        if not re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*', slug) or slug in slugs:
            raise ValueError('Invalid or colliding portable figure slug')
        slugs.add(slug)
        points = [_public_point(rid, model['records'][rid]) for rid in link['record_ids']]
        points.sort(key=lambda p: _figure_order(p, periods))
        title = FIGURE_TITLES.get(slug, claims[link['claim_ids'][0]]['title'] if link['claim_ids'] else slug)
        figures.append({**link, 'slug': slug, 'title': title, 'points': points,
                        'source_ids': list(link['source_ids']),
                        'periods': list(periods)})
    return {'sections': [{'id': key, 'title': title} for key, title in SECTIONS],
            'opening_claim_ids': list(opening), 'claims': claims, 'figures': figures,
            'periods': list(periods), 'model': model,
            'synthetic': model['profiles']['synthetic']}


def stage_report_fonts(output_dir: str | Path) -> list[str]:
    """Copy the five reviewed package assets and verify exact source bytes."""
    root = Path(output_dir)
    folder = root / 'assets' / 'fonts'
    folder.mkdir(parents=True, exist_ok=True)
    result = []
    for name in FONT_NAMES:
        source = font_path(name)
        expected = hashlib.sha256(source.read_bytes()).hexdigest()
        target = folder / name
        if target.exists() and hashlib.sha256(target.read_bytes()).hexdigest() != expected:
            raise ValueError(f'Colliding font asset: {name}')
        if not target.exists():
            shutil.copyfile(source, target)
        if hashlib.sha256(target.read_bytes()).hexdigest() != expected:
            raise ValueError(f'Font copy changed: {name}')
        result.append(f'assets/fonts/{name}')
    return result


def _plot(figure: dict, root: Path) -> tuple[str, str]:
    """One public point set drives both vector and raster figure files."""
    font_manager.fontManager.addfont(str(font_path('DejaVuSans.ttf')))
    plt.rcParams.update({'font.family': 'DejaVu Sans', 'svg.fonttype': 'path',
                         'font.size': 8, 'text.color': '#172B3A',
                         'axes.labelcolor': '#172B3A', 'xtick.color': '#405464',
                         'ytick.color': '#405464'})
    points = figure['points']
    n = len(points)
    height = max(3.4, min(40.0, n * 0.22 + 1.8))
    fig, ax = plt.subplots(figsize=(10, height), layout='constrained')
    fig.patch.set_facecolor('white')
    y = list(range(n))
    labels = []
    for i, p in enumerate(points):
        label = f"{p['field_code']} · {p['period']} · {p['metric']}"
        if figure['slug'] == 'state-availability':
            label = f"{p['geography_id']} · {p['geography']}"
        elif figure['slug'] == 'other-fields':
            label = p['field_code']
        elif figure['slug'] == 'recorded-sex':
            label = f"{p['field_code']} · {p['recorded_sex']} · {p['metric']}"
        labels.append(label)
        if p['value'] is None:
            ax.scatter(0, i, marker='x', color=COLORS[p['status']], s=25)
        else:
            lo, hi = p['ci90_lower'], p['ci90_upper']
            xerr = None if lo is None or hi is None else [[p['value']-lo], [hi-p['value']]]
            ax.errorbar(p['value'], i, xerr=xerr, fmt='o', color=COLORS[p['status']],
                        markersize=3, capsize=2, linewidth=1)
    ax.set_yticks(y, labels=labels)
    ax.invert_yaxis()
    ax.set_xlabel('Valor según unidad de la fila; × = no disponible. IC90 del proyecto cuando existe')
    ax.grid(axis='x', color='#D5DEE2', linewidth=.5)
    ax.set_title(figure['title'], loc='left', fontsize=12, fontweight='bold')
    folder = root / 'figures'
    folder.mkdir(parents=True, exist_ok=True)
    svg = f"figures/{figure['slug']}.svg"
    png = f"figures/{figure['slug']}.png"
    fig.savefig(root / svg, format='svg', metadata={'Title': figure['title'],
                'Description': f"{figure['figure_id']}; {len(points)} registros públicos"})
    fig.savefig(root / png, format='png', dpi=145, metadata={'Title': figure['title'],
                'Description': f"{figure['figure_id']}; {len(points)} registros públicos"})
    plt.close(fig)
    return svg, png


def _record_rows(model: dict, predicate) -> list[dict]:
    rows = [_public_point(rid, item) for rid, item in model['records'].items()
            if predicate(item['record'])]
    rows.sort(key=lambda p: (p['period'], p['field_code'], p['metric_id'],
                             p['geography_id'], p['recorded_sex_id'], p['record_id']))
    return rows


def _html_table(rows: list[dict], caption: str, table_id: str, *, compact: bool = False) -> str:
    heads = ('Campo / código', 'Geografía', 'Periodo', 'Medida', 'Valor / unidad',
             'IC90', 'CV', 'Estado y motivo', 'n observado', 'Fuente', 'Registro')
    parts = [f'<div class="table-scroll" role="region" aria-label="Tabla desplazable: {escape(caption)}" tabindex="0">',
             f'<table id="{escape(table_id)}"><caption>{escape(caption)}</caption><thead><tr>']
    parts += [f'<th scope="col">{escape(h)}</th>' for h in heads]
    parts.append('</tr></thead><tbody>')
    for p in rows:
        ci = ('No disponible' if p['ci90_lower'] is None else
              f"{_number(p['ci90_lower'])}–{_number(p['ci90_upper'])}")
        cv = 'No disponible' if p['cv'] is None else f"{_number(p['cv'])} %"
        status = p['status'] + (f" · {p['reason']}" if p['reason'] else '')
        vals = (f"{p['field_code']} · {p['field']}", p['geography'], p['period'], p['metric'],
                p['value_text'], ci, cv, status, str(p['sample_size']), p['source_id'], p['record_id'])
        parts.append('<tr>')
        parts += [f'<td>{escape(str(v))}</td>' for v in vals]
        parts.append('</tr>')
    parts.append('</tbody></table></div>')
    return ''.join(parts)


def _md_table(rows: list[dict], caption: str) -> str:
    lines = [f'**{caption}**', '', '| Campo / código | Geografía | Periodo | Medida | Valor / unidad | IC90 | CV | Estado y motivo | n observado | Fuente | Registro |',
             '| --- | --- | --- | --- | --- | --- | --- | ---: | --- | --- | --- |']
    for p in rows:
        ci = 'No disponible' if p['ci90_lower'] is None else f"{_number(p['ci90_lower'])}–{_number(p['ci90_upper'])}"
        cv = 'No disponible' if p['cv'] is None else f"{_number(p['cv'])} %"
        status = p['status'] + (f" · {p['reason']}" if p['reason'] else '')
        vals = (f"{p['field_code']} · {p['field']}", p['geography'], p['period'], p['metric'],
                p['value_text'], ci, cv, status, str(p['sample_size']), p['source_id'], p['record_id'])
        lines.append('| ' + ' | '.join(str(v).replace('|', '\\|').replace('\n', ' ') for v in vals) + ' |')
    return '\n'.join(lines)


def _style() -> str:
    return '''
@font-face {font-family: LocalSans; src: url("assets/fonts/DejaVuSans.ttf")} 
@font-face {font-family: LocalSans; src: url("assets/fonts/DejaVuSans-Bold.ttf"); font-weight:700}
@font-face {font-family: LocalSerif; src: url("assets/fonts/DejaVuSerif.ttf")}
@font-face {font-family: LocalSerif; src: url("assets/fonts/DejaVuSerif-Bold.ttf"); font-weight:700}
* {box-sizing:border-box} html {background:#fff; color:#172B3A} body {margin:0; font:17px/1.55 LocalSans,sans-serif}
main {max-width:920px; margin:auto; padding:2.6rem 1.4rem 5rem} h1,h2,h3 {font-family:LocalSerif,serif;line-height:1.23;color:#172B3A}
h1 {font-size:clamp(2rem,5vw,3.2rem);margin:.3rem 0} h2 {font-size:1.8rem;margin:2.7rem 0 .8rem} h3 {font-size:1.25rem;margin:1.5rem 0 .5rem}
p,li {max-width:72ch} .eyebrow,.meta {color:#405464} .lede {font-size:1.16rem} .warning {border-left:4px solid #A34F23;padding:.5rem 1rem;background:#F7F3F0}
.figure {margin:1.8rem 0 2.6rem} .plot-scroll,.table-scroll {max-width:100%;overflow-x:auto;overflow-y:auto;border:1px solid #CCD7DC;padding:.5rem}
.plot-scroll {max-height:680px} .plot-scroll img {max-width:none;width:100%;min-width:720px;height:auto;display:block}
table {border-collapse:collapse;min-width:900px;font-size:.78rem;line-height:1.38} caption {text-align:left;font-weight:700;font-size:1rem;padding:.5rem 0}
th,td {text-align:left;vertical-align:top;border-bottom:1px solid #D5DEE2;padding:.4rem .55rem} th {background:#EDF2F4;color:#172B3A} td:last-child {overflow-wrap:anywhere;font-size:.72rem}
.evidence-id {overflow-wrap:anywhere;word-break:break-all;font-size:.74rem} .source-note,.small {font-size:.83rem;color:#405464} a {color:#145A66;text-decoration:underline}
figure {margin:0} figcaption {font-size:.84rem;color:#405464;margin:.45rem 0} .print-panels {display:none}
@media(max-width:600px) {main {padding:1.4rem .9rem} h2 {font-size:1.45rem} .plot-scroll img {width:720px}}
@page {size:A4;margin:19mm 18mm 20mm 18mm;@bottom-left {content:"Brújula Laboral MX · v1.0.0";font:8pt LocalSans;color:#405464}@bottom-right {content:counter(page);font:8pt LocalSans;color:#405464}}
@media print {body{font:10.5pt/1.4 LocalSans,sans-serif}main{max-width:none;padding:0}h1{font-size:25pt}h2{font-size:16pt;break-after:avoid}h3{font-size:12pt;break-after:avoid}
.plot-scroll{display:none}.print-panels{display:block}.print-panel{break-inside:avoid;margin:5mm 0}.print-panel svg{width:100%;height:auto;max-height:225mm}
.table-scroll{overflow:visible;border:0;padding:0}table{min-width:0;width:100%;font-size:6.7pt;table-layout:fixed}thead{display:table-header-group}tr{break-inside:avoid}
th,td{padding:2pt;overflow-wrap:anywhere}td:last-child{font-size:5.6pt}.evidence-id{font-size:8.5pt;word-break:break-all}
.figure{break-before:page}.figure h3{break-after:avoid}figcaption{break-after:avoid}.screen-only{display:none}}
'''


def render_publication(model: dict, output_dir: str | Path) -> dict:
    """Render HTML, Markdown, paired figures and semantic tables from one model."""
    document = build_editorial_document(model)
    root = Path(output_dir)
    root.mkdir(parents=True, exist_ok=True)
    fonts = stage_report_fonts(root)
    synthetic = document['synthetic']
    warning = 'DATOS SINTÉTICOS · Uso ilustrativo; no son estimaciones ENOE.' if synthetic else None
    html = ['<!doctype html><html lang="es"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">',
            '<title>Brújula Laboral MX · Informe v1.0.0</title><style>', _style(), '</style></head><body><main>']
    md = ['# Brújula Laboral MX', '', 'Informe de investigación · v1.0.0', '']
    periods = document['periods']
    intro = f"Ventana de observación: {periods[0]} a {periods[-1]}. Versión de publicación: v1.0.0. La fecha de edición exacta no está disponible."
    html += ['<header><p class="eyebrow">Investigación laboral · México</p><h1>Brújula Laboral MX</h1>', f'<p class="lede">{escape(intro)}</p></header>']
    md += [intro, '']
    if warning:
        html.append(f'<p class="warning">{escape(warning)}</p>')
        md += [f'**{warning}**', '']
    claims = document['claims']
    figure_results = []
    figure_by_slug = {}
    for figure in document['figures']:
        svg, png = _plot(figure, root)
        entry = {'figure_id': figure['figure_id'], 'table_id': figure['table_id'],
                 'svg': svg, 'png': png, 'record_ids': figure['record_ids'],
                 'comparison_ids': figure['comparison_ids'], 'claim_ids': figure['claim_ids'],
                 'source_ids': figure['source_ids']}
        figure_results.append(entry)
        figure_by_slug[figure['slug']] = (figure, entry)

    def section(key: str):
        title = next(s['title'] for s in document['sections'] if s['id'] == key)
        html.append(f'<section id="{key}"><h2>{escape(title)}</h2>')
        md.extend([f'## {title}', ''])

    def end():
        html.append('</section>')

    def para(text: str):
        html.append(f'<p>{escape(text)}</p>')
        md.extend([text, ''])

    def figure_block(slug: str):
        if slug not in figure_by_slug:
            return
        fig, result = figure_by_slug[slug]
        pts = fig['points']
        alt = f"{fig['title']} {len(pts)} registros públicos; {sum(p['value'] is None for p in pts)} sin valor disponible. Tabla {fig['table_id']} con estado y motivo."
        source_line = 'Fuentes: ' + ', '.join(fig['source_ids']) + '. IC90 y CV son aproximaciones del proyecto, no precisión oficial del INEGI.'
        html.append(f'<div class="figure" id="{escape(fig["figure_id"])}"><h3>{escape(fig["title"])}</h3><figure>')
        html.append(f'<div class="plot-scroll" role="region" aria-label="Gráfica desplazable: {escape(fig["title"])}" tabindex="0"><img src="{result["svg"]}" alt="{escape(alt)}"></div>')
        html.append(f'<figcaption>{escape(source_line)} Código de figura: {escape(fig["figure_id"])}.</figcaption></figure>')
        html.append(_html_table(pts, fig['title'] + '. ' + source_line, fig['table_id']))
        html.append('</div>')
        md.extend([f'### {fig["title"]}', '', f'![{alt}]({result["svg"]})', '', source_line,
                   f'Figura: {fig["figure_id"]}. Tabla: {fig["table_id"]}.', '',
                   _md_table(pts, fig['title']), ''])

    section('hallazgos')
    if not document['opening_claim_ids']:
        para('No hay hallazgos de apertura respaldados para esta edición; las celdas no disponibles conservan su motivo en las tablas.')
    for i, cid in enumerate(document['opening_claim_ids'], 1):
        c = claims[cid]
        html.append(f'<article id="claim-{i}"><h3>Hallazgo {i}: {escape(c["title"])}</h3>')
        md.extend([f'### Hallazgo {i}: {c["title"]}', ''])
        for field in ('observation', 'interpretation', 'limitation'):
            para(c[field])
        refs = ', '.join(c['record_ids'])
        html.append(f'<p class="small">Evidencia [{i}]: <a href="#evidencia">{escape(cid)}</a>; registros {escape(refs)}.</p></article>')
        md += [f'Evidencia [{i}]: {cid}; registros {refs}.', '']
        figure_block('opening-' + cid[4:])
    end()

    section('lectura')
    para('El campo de estudio identifica la carrera reportada; ocupación e industria son dimensiones distintas. La cohorte profesional exige estudios profesionales terminados y edad conocida de 15 años o más. El contexto nacional de 15 años o más tiene otro universo y se muestra por separado.')
    para('No disponible no significa cero. n observado es tamaño de muestra, no población ponderada. El ingreso se presenta en MXN mensuales nominales entre quienes tienen ingreso positivo conocido; su cobertura de respuesta acompaña la media. IC90 y CV son aproximaciones del proyecto y no precisión oficial del INEGI.')
    end()

    latest = periods[-1]
    section('contexto')
    para(f'El contexto nacional de 15 años o más y la cohorte profesional se separan incluso cuando comparten trimestre ({latest}). Las tablas identifican su universo exacto.')
    figure_block('national-context')
    national = _record_rows(model, lambda r: r['period_id']==latest and r['field_of_study_id']=='all' and r['geography_id']=='mx' and r['recorded_sex_id']=='all')
    html.append(_html_table(national, f'Detalle nacional y profesional · {latest} · 23 medidas por universo', 'table:national-detail'))
    md.extend([_md_table(national, f'Detalle nacional y profesional · {latest}'), ''])
    end()

    for code, label, key in FOCAL:
        section(key)
        para(f'{label} ({code}) se refiere al campo de estudio reportado, no a una ocupación ni a una industria. Las 23 medidas del trimestre {latest} mantienen valor, unidad, IC90, CV, estado, motivo y evidencia propios.')
        rows = _record_rows(model, lambda r, code=code: r['field_of_study_id']==code and r['geography_id']=='mx' and r['recorded_sex_id']=='all' and r['period_id']==latest)
        html.append(_html_table(rows, f'Perfil completo de {label} · {latest}', f'table:profile-{key}'))
        md.extend([_md_table(rows, f'Perfil completo de {label} · {latest}'), ''])
        if key == 'politicas':
            figure_block('focal-latest')
        end()

    section('evolucion')
    para('Se presentan los ocho trimestres en orden cronológico. Las diferencias trimestrales adyacentes pueden reflejar estacionalidad; las comparaciones anuales usan el mismo trimestre. Las muestras pueden solaparse y no se estima significancia de la diferencia. Una celda no disponible interrumpe la serie.')
    figure_block('eight-quarter-trends')
    for period in periods:
        html.append(f'<h3>{escape(period)}</h3>')
        md.extend([f'### {period}', ''])
        rows = _record_rows(model, lambda r, period=period: r['period_id']==period and r['field_of_study_id'] in {c[0] for c in FOCAL} and r['geography_id']=='mx' and r['recorded_sex_id']=='all' and r['metric_id'] in ('employment_rate','positive_income_mean','positive_income_coverage'))
        html.append(_html_table(rows, f'Series focales · {period}', f'table:quarter-{period}'))
        md.extend([_md_table(rows, f'Series focales · {period}'), ''])
    end()

    section('sexo-territorio')
    para(f'Los contrastes por sexo registrado y entidad son descriptivos en {latest}. Baja California (02) es referencia descriptiva declarada, no patrón de éxito; una celda suprimida impide ese contraste.')
    figure_block('recorded-sex')
    figure_block('state-availability')
    state_rows = _record_rows(model, lambda r: r['period_id']==latest and r['geography_id']!='mx' and r['metric_id']=='employment_rate' and r['field_of_study_id'] in ({'all'} | {c[0] for c in FOCAL}) and r['recorded_sex_id']=='all')
    html.append(_html_table(state_rows, 'Disponibilidad por 32 entidades y cuatro grupos de campo', 'table:state-32x4'))
    md.extend([_md_table(state_rows, 'Disponibilidad por 32 entidades y cuatro grupos de campo'), ''])
    end()

    section('otros-campos')
    para('Los campos identificables adicionales aparecen por código oficial de clasificación. El orden no constituye una clasificación de resultados; las celdas suprimidas siguen visibles.')
    figure_block('other-fields')
    end()

    section('cobertura')
    para('Cobertura y exclusiones se informan como conteos observados que pueden solaparse; no se suman como grupos excluyentes. Las cifras de ingreso positivo requieren respuesta conocida y denominador propio.')
    for limitation in model['limitations']:
        para(limitation)
    end()

    section('metodos')
    para('Fuente: INEGI, Encuesta Nacional de Ocupación y Empleo. Selección, estimación y transformación: Brújula Laboral MX; INEGI no avala esta precisión. La varianza se aproxima mediante el método Taylor del proyecto y el ajuste singleton documentado; los intervalos de 90 % no son intervalos oficiales. Las comparaciones son descriptivas y solo se publican cuando la definición aceptada es comparable.')
    para('Los identificadores v2r corresponden a registros públicos de diez dimensiones; v2c a comparaciones validadas; v2k a afirmaciones aceptadas. Los archivos de datos públicos mantienen precisión numérica distinta del redondeo de lectura de esta página.')
    end()

    section('fuentes')
    for sid, source in sorted(model['source_manifest']['sources'].items()):
        text = f"{sid} · periodo {source['period_id']} · SHA-256 {source['sha256']} · {source['url']}"
        para(text)
    end()

    section('evidencia')
    para('Índice exacto de afirmaciones, comparaciones y registros citados. Cada identificador permanece completo para su unión con las tablas y los datos públicos.')
    used_records = set()
    used_comparisons = set()
    for f in document['figures']:
        used_records.update(f['record_ids'])
        used_comparisons.update(f['comparison_ids'])
    for c in model['claims']:
        used_records.update(c['record_ids'])
        if c['comparison_id']:
            used_comparisons.add(c['comparison_id'])
    for kind, ids in (('Afirmaciones v2k', sorted(claims)), ('Comparaciones v2c', sorted(used_comparisons)), ('Registros v2r', sorted(used_records))):
        html.append(f'<h3>{escape(kind)}</h3><ol>')
        md.extend([f'### {kind}', ''])
        for item_id in ids:
            html.append(f'<li class="evidence-id">{escape(item_id)}</li>')
            md.append(f'- {item_id}')
        html.append('</ol>')
        md.append('')
    end()
    html.append('</main></body></html>')
    (root / 'report.html').write_text(''.join(html), encoding='utf-8')
    (root / 'report.md').write_text('\n'.join(md), encoding='utf-8')
    return {'html': 'report.html', 'markdown': 'report.md', 'figures': figure_results,
            'fonts': fonts, 'sections': [s['id'] for s in document['sections']],
            'claim_ids': document['opening_claim_ids'],
            'record_ids': sorted(used_records), 'comparison_ids': sorted(used_comparisons)}
