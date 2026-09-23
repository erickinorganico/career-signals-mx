"""Evidence-bound static Spanish editorial report from a validated public model."""

from __future__ import annotations

from decimal import Decimal, ROUND_HALF_UP
from datetime import datetime, timezone
from html import escape
import hashlib
import io
import json
from pathlib import Path
import re
import shutil
import textwrap
from urllib.parse import quote

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib import font_manager

from .publication_v2 import validate_publication_model
from .resources import font_path

FONT_NAMES = ('DejaVuSans.ttf', 'DejaVuSans-Bold.ttf',
              'DejaVuSerif.ttf', 'DejaVuSerif-Bold.ttf', 'LICENSE_DEJAVU')
FONT_SHA256 = {
    'DejaVuSans.ttf': '3fdf69cabf06049ea70a00b5919340e2ce1e6d02b0cc3c4b44fb6801bd1e0d22',
    'DejaVuSans-Bold.ttf': 'b184b89e3c1075f22f6b71575b6fc20d4972b3cfd3b23322ca6fd596dcaef167',
    'DejaVuSerif.ttf': '107244956e9962b9e96faccdc551825e0ae0898ae13737133e1b921a2fd35ffa',
    'DejaVuSerif-Bold.ttf': 'c3753f2ed6bc673f15846dc45addbeb3b9c872f32fb18fd53a21f1bef1ed7676',
    'LICENSE_DEJAVU': 'd75938dec098f06f0ac3c00853065d94f020be1c3c62ef1dc2975ba15b4d9b0e',
}
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
SERIES_STYLES = {
    '033100': ('#145A66', 'o', 'Derecho'),
    '032100': ('#A34F23', 's', 'Comunicación y periodismo'),
    '031300': ('#4B5F89', '^', 'Ciencias políticas'),
}
UNIT_LABELS = {'percent': '%', 'people': 'personas',
               'MXN/month': 'MXN/mes nominales', 'hours/week': 'horas/semana'}


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
        'population_id': record['population_id'],
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
        comparison_map = {c['comparison_id']: c for c in model['comparisons']}
        figures.append({**link, 'slug': slug, 'title': title, 'points': points,
                        'comparisons': [comparison_map[cid] for cid in link['comparison_ids']],
                        'synthetic': model['profiles']['synthetic'],
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
        expected = FONT_SHA256[name]
        if hashlib.sha256(source.read_bytes()).hexdigest() != expected:
            raise ValueError(f'Packaged font asset changed: {name}')
        target = folder / name
        if target.exists() and hashlib.sha256(target.read_bytes()).hexdigest() != expected:
            raise ValueError(f'Colliding font asset: {name}')
        if not target.exists():
            shutil.copyfile(source, target)
        if hashlib.sha256(target.read_bytes()).hexdigest() != expected:
            raise ValueError(f'Font copy changed: {name}')
        result.append(f'assets/fonts/{name}')
    return result


def _plot_figure(figure: dict, points: list[dict], *, print_mode: bool = False):
    """Draw one declared point set; group units and leave missing points empty."""
    font_manager.fontManager.addfont(str(font_path('DejaVuSans.ttf')))
    plt.rcParams.update({'font.family': 'DejaVu Sans', 'svg.fonttype': 'path',
                         'font.size': 8, 'text.color': '#172B3A',
                         'axes.labelcolor': '#172B3A', 'xtick.color': '#405464',
                         'ytick.color': '#405464'})
    groups = {}
    for p in points:
        groups.setdefault((p['metric_id'], p['unit'], p['population']), []).append(p)
    is_trend = figure['slug'] == 'eight-quarter-trends'
    width = 6.8 if print_mode else 10
    if is_trend:
        fig, axes = plt.subplots(len(groups), 1, figsize=(width, max(4.5, len(groups)*2.6)),
                                 layout='constrained', squeeze=False)
    else:
        fig, axes = plt.subplots(len(groups), 1,
                                 figsize=(width, max(3.4, len(points)*.28 + len(groups)*1.35)),
                                 layout='constrained', squeeze=False,
                                 gridspec_kw={'height_ratios': [max(1,len(rows)*.3) for rows in groups.values()]})
    fig.patch.set_facecolor('white')
    for ax, ((metric, unit, population), rows) in zip(axes.flat, groups.items()):
        if is_trend:
            missing_labels = []
            for code in (c[0] for c in FOCAL if any(p['field_code']==c[0] for p in rows)):
                color, marker, _label = SERIES_STYLES[code]
                series = sorted((p for p in rows if p['field_code']==code),
                                key=lambda p: figure['periods'].index(p['period']))
                for p in series:
                    x = figure['periods'].index(p['period'])
                    if p['value'] is None:
                        missing_labels.append(f"{code} {p['period']}")
                    else:
                        lo, hi = p['ci90_lower'], p['ci90_upper']
                        err = None if lo is None or hi is None else [[p['value']-lo],[hi-p['value']]]
                        ax.errorbar(x, p['value'], yerr=err, fmt=marker,
                                    color=color, markersize=4, capsize=2)
                # A segment is drawn only when its adjacent public comparison is accepted.
                by_period = {p['period']: p for p in series}
                valid_comparisons = {(c['previous_record_id'], c['current_record_id'])
                                     for c in figure.get('comparisons', [])
                                     if c['comparable'] and c['status']=='REVIEW'
                                     and c['comparison_type']=='adjacent_quarter'}
                for a, b in zip(figure['periods'], figure['periods'][1:]):
                    first, second = by_period.get(a), by_period.get(b)
                    if (first and second and first['value'] is not None and second['value'] is not None
                            and (first['record_id'], second['record_id']) in valid_comparisons):
                        ax.plot([figure['periods'].index(a), figure['periods'].index(b)],
                                [first['value'], second['value']], color=color, linewidth=1.2)
            ax.set_xticks(range(len(figure['periods'])), figure['periods'], rotation=30)
            if all(p['value'] is None for p in rows):
                ax.yaxis.set_visible(False)
                ax.text(.5,.5,'Sin valores autorizados; consulte el estado y motivo en la tabla',
                        transform=ax.transAxes,ha='center',va='center',fontsize=8,color='#405464')
            else:
                ax.set_ylabel(UNIT_LABELS[unit])
                ax.grid(axis='y', color='#D5DEE2', linewidth=.5)
            ax.text(.99,.95, '○ Derecho   □ Comunicación   △ Ciencias políticas',
                    transform=ax.transAxes,ha='right',va='top',fontsize=7)
            if missing_labels:
                ax.text(.01,.04, '× No disponible: ' + ', '.join(missing_labels),
                        transform=ax.transAxes,ha='left',va='bottom',fontsize=7,color='#405464')
        else:
            labels = []
            all_missing = all(p['value'] is None for p in rows)
            for i,p in enumerate(rows):
                if figure['slug']=='state-availability':
                    label = f"{p['geography_id']} · {p['geography']}"
                elif figure['slug']=='other-fields':
                    label = p['field_code']
                elif figure['slug']=='recorded-sex':
                    label = f"{p['field_code']} · {p['recorded_sex']} ({p['recorded_sex_id']})"
                else:
                    label = f"{p['field_code']} · {p['period']}"
                labels.append(label)
                if p['value'] is None:
                    ax.text(.02, i, '× No disponible', transform=ax.get_yaxis_transform(),
                            color='#405464', fontsize=7, va='center')
                else:
                    lo, hi = p['ci90_lower'], p['ci90_upper']
                    err = None if lo is None or hi is None else [[p['value']-lo],[hi-p['value']]]
                    ax.errorbar(p['value'], i, xerr=err, fmt='o', color=COLORS[p['status']],
                                markersize=3, capsize=2, linewidth=1)
            ax.set_yticks(range(len(rows)), labels=labels)
            # Include missing rows in the categorical limits even when only
            # later rows have numeric artists; otherwise row zero is drawn
            # outside the axes and can overlap the title.
            ax.set_ylim(len(rows) - .5, -.5)
            if all_missing:
                ax.xaxis.set_visible(False)
                ax.spines['bottom'].set_visible(False)
                ax.text(.5,.5,'Sin valores autorizados; consulte el estado y motivo en la tabla',
                        transform=ax.transAxes,ha='center',va='center',fontsize=8,color='#405464')
            else:
                ax.set_xlabel(UNIT_LABELS[unit] + ' · IC90 del proyecto cuando existe')
                ax.grid(axis='x', color='#D5DEE2', linewidth=.5)
        short_population = ('Profesionales terminados, edad conocida 15+'
                            if population.startswith('personas residentes con estudios profesionales')
                            else 'Contexto nacional 15+')
        subtitle = '\n'.join(textwrap.wrap(
            f'{rows[0]["metric"]} · {short_population}',
            width=46 if print_mode else 76))
        ax.set_title(subtitle, loc='left', fontsize=8)
    title = '\n'.join(textwrap.wrap(figure['title'], width=58 if print_mode else 78))
    fig.suptitle(title, ha='left', x=.01, fontsize=12, fontweight='bold')
    periods = list(dict.fromkeys(p['period'] for p in points))
    sources = list(dict.fromkeys(p['source_id'] for p in points))
    footer_lines = []
    for statement in ('Fuente: INEGI ENOE · ' + ', '.join(sources),
                      'Periodos: ' + ', '.join(periods),
                      'IC90: cálculo aproximado del proyecto; precisión no oficial de INEGI.'):
        footer_lines.extend(textwrap.wrap(statement, width=70 if print_mode else 105,
                                          break_long_words=False))
    if figure.get('synthetic'):
        footer_lines.append('DATOS SINTÉTICOS · no son estimaciones ENOE')
    height = fig.get_figheight()
    footer_inches = .19 * len(footer_lines) + .18
    fig.get_layout_engine().set(rect=(0, footer_inches / height, 1,
                                      1 - footer_inches / height))
    for index, line in enumerate(footer_lines):
        fig.text(.015, (footer_inches - .17 * (index + 1)) / height, line,
                 ha='left', va='top', fontsize=7.2,
                 color='#A34F23' if 'DATOS SINTÉTICOS' in line else '#405464')
    return fig


def _plot(figure: dict, root: Path) -> tuple[str, str]:
    fig = _plot_figure(figure, figure['points'])
    points = figure['points']
    origin_note = ' · DATOS SINTÉTICOS' if figure.get('synthetic') else ''
    manifest = json.dumps([{'record_id': p['record_id'], 'value': p['value'],
                            'ci90_lower': p['ci90_lower'], 'ci90_upper': p['ci90_upper'],
                            'status': p['status'], 'reason': p['reason']}
                           for p in points], ensure_ascii=False, separators=(',', ':'))
    folder = root / 'figures'
    folder.mkdir(parents=True, exist_ok=True)
    svg = f"figures/{figure['slug']}.svg"
    png = f"figures/{figure['slug']}.png"
    fig.savefig(root / svg, format='svg', metadata={'Title': figure['title'],
                'Description': f"{figure['figure_id']}{origin_note}; {manifest}"})
    fig.savefig(root / png, format='png', dpi=145, metadata={'Title': figure['title'],
                'Description': f"{figure['figure_id']}{origin_note}; {manifest}"})
    svg_path = root / svg
    raw_svg = svg_path.read_text(encoding='utf-8')
    raw_svg = re.sub(r'(<svg\b[^>]*>)',
                     lambda m: m.group(1) + f'<title>{escape(figure["title"])}</title><desc>{escape(figure["figure_id"])} · {len(points)} registros públicos</desc>',
                     raw_svg, count=1)
    svg_path.write_text(raw_svg, encoding='utf-8')
    plt.close(fig)
    return svg, png


def _print_panels(figure: dict) -> str:
    points = figure['points']
    blocks = []
    for n, start in enumerate(range(0, len(points), 16), 1):
        panel = _plot_figure(figure, points[start:start+16], print_mode=True)
        output = io.StringIO()
        panel.savefig(output, format='svg', metadata={'Title': figure['title']})
        plt.close(panel)
        svg = output.getvalue()
        svg = re.sub(r'^<\?xml[^>]*>\s*', '', svg)
        svg = re.sub(r'<!DOCTYPE svg[^>]*>\s*', '', svg)
        # Matplotlib IDs are local to each SVG; add a panel namespace to every
        # referenced ID so repeated clip paths cannot collide in print HTML.
        prefix = f"p-{figure['slug']}-{n}-"
        svg = re.sub(r'\bid="([^"]+)"', lambda m: f'id="{prefix}{m.group(1)}"', svg)
        svg = re.sub(r'url\(#([^)]*)\)', lambda m: f'url(#{prefix}{m.group(1)})', svg)
        svg = re.sub(r'(?:href|xlink:href)="#([^"]+)"', lambda m: m.group(0).replace('#',f'#{prefix}',1), svg)
        panel_ids = '|'.join(p['record_id'] for p in points[start:start+16])
        blocks.append(f'<div class="print-panel" data-figure-id="{escape(figure["figure_id"])}" data-record-ids="{escape(panel_ids)}"><p>{escape(figure["figure_id"])} · panel {n} · fuente: {escape(", ".join(figure["source_ids"]))}</p>{svg}</div>')
    return '<div class="print-panels">' + ''.join(blocks) + '</div>'


def _figure_alt(figure: dict) -> str:
    """Describe only public supported points, scope and visible missingness."""
    points = figure['points']
    supported = [p for p in points if p['value'] is not None]
    missing = len(points) - len(supported)
    populations = list(dict.fromkeys(
        'profesionales terminados, edad conocida 15+' if p['population_id']=='completed_professional_known_age'
        else 'contexto nacional 15+' for p in points))
    periods = list(dict.fromkeys(p['period'] for p in points))
    unit_labels = {'percent':'%', 'people':'personas', 'MXN/month':'MXN/mes nominales',
                   'hours/week':'horas/semana'}
    units = list(dict.fromkeys(unit_labels[p['unit']] for p in points))
    scope = (f"Universo: {', '.join(populations)}. Periodos: {', '.join(periods)}. "
             f"Unidades: {', '.join(units)}. Fuentes: {', '.join(figure['source_ids'])}.")
    if supported:
        # First and last are existing values in each comparable display group.
        # Their complete recorded scopes prevent two states or sexes from being
        # announced as the same observation. No change or rank is inferred.
        groups: dict[tuple[str, str, str, str], list[dict]] = {}
        for point in supported:
            key = (point['metric_id'], point['unit'], point['population_id'],
                   point['field_code'] if figure.get('slug') == 'eight-quarter-trends' else '')
            groups.setdefault(key, []).append(point)
        selected = []
        for group in groups.values():
            selected.append(group[0])
            if len(group) > 1:
                selected.append(group[-1])
        examples = '; '.join(
            f"{p['field']} ({p['field_code']}), {p['population']} "
            f"({p['population_id']}), {p['geography']} ({p['geography_id']}), "
            f"sexo registrado {p['recorded_sex']} ({p['recorded_sex_id']}), "
            f"{p['period']}, {p['metric']} ({p['metric_id']}), "
            f"{p['value_text']}, fuente {p['source_id']}"
            for p in selected)
        evidence = f"Primer y último valor público de cada grupo en el orden declarado: {examples}."
    else:
        evidence = 'Sin valores autorizados; no hay escala cuantitativa.'
    synthetic = 'DATOS SINTÉTICOS. ' if figure.get('synthetic') else ''
    return (f"{synthetic}{figure['title']} {scope} {evidence} "
            f"{missing} puntos sin valor; estado y motivo en la tabla {figure['table_id']}.")


def _record_rows(model: dict, predicate) -> list[dict]:
    rows = [_public_point(rid, item) for rid, item in model['records'].items()
            if predicate(item['record'])]
    rows.sort(key=lambda p: (p['period'], p['field_code'], p['metric_id'],
                             p['geography_id'], p['recorded_sex_id'], p['record_id']))
    return rows


def _print_comparison_table(comparisons: list[dict], model: dict,
                            comp_refs: dict[str, str]) -> str:
    parts = ['<table class="print-table print-comparisons"><caption>Comparaciones descriptivas aceptadas para las series focales; sin intervalo ni prueba de significancia de la diferencia</caption><thead><tr>']
    parts.extend(f'<th scope="col">{escape(head)}</th>' for head in
                 ('Campo / medida', 'Periodos / tipo', 'Cambio absoluto', 'Estado', 'Fuentes / ref.'))
    parts.append('</tr></thead><tbody>')
    for comparison in comparisons:
        current = model['records'][comparison['current_record_id']]
        previous = model['records'][comparison['previous_record_id']]
        comparison_type = {'adjacent_quarter':'trimestre adyacente',
                           'like_quarter_annual':'mismo trimestre anual'}[comparison['comparison_type']]
        display_unit = {'percentage points':'puntos porcentuales',
                        'nominal MXN/month':'MXN/mes nominales',
                        'people':'personas', 'hours/week':'horas/semana'}.get(
                            comparison['display_unit'], comparison['display_unit'])
        sources = ', '.join(dict.fromkeys((previous['record']['source_snapshot_id'],
                                           current['record']['source_snapshot_id'])))
        cells = (f"{current['display']['field']} · {current['display']['metric']}",
                 f"{' → '.join(comparison['slot_periods'])} · {comparison_type}",
                 f"{_number(comparison['absolute_change'])} {display_unit}",
                 comparison['status'],
                 f"{sources} · {comp_refs[comparison['comparison_id']]}")
        parts.append('<tr>' + ''.join(f'<td>{escape(str(value))}</td>' for value in cells) + '</tr>')
    parts.append('</tbody></table>')
    return ''.join(parts)


def _html_table(rows: list[dict], caption: str, table_id: str, refs: dict[str, str]) -> str:
    heads = ('Campo / código', 'Alcance', 'Geografía', 'Periodo', 'Medida', 'Valor / unidad',
             'IC90 / CV', 'Estado y motivo', 'n observado', 'Fuente', 'Evidencia')
    parts = [f'<div class="table-scroll" role="region" aria-label="Tabla desplazable: {escape(caption)}" tabindex="0">',
             f'<table class="screen-table" id="{escape(table_id)}"><caption>{escape(caption)}</caption><thead><tr>']
    parts += [f'<th scope="col">{escape(h)}</th>' for h in heads]
    parts.append('</tr></thead><tbody>')
    for p in rows:
        ci = ('No disponible' if p['ci90_lower'] is None else
              f"{_number(p['ci90_lower'])}–{_number(p['ci90_upper'])}")
        cv = 'No disponible' if p['cv'] is None else f"{_number(p['cv'])} %"
        status = p['status'] + (f" · {p['reason']}" if p['reason'] else '')
        universe = ('Profesional 15+ edad conocida' if p['population_id']=='completed_professional_known_age'
                    else 'Nacional 15+') + ' · ' + p['recorded_sex']
        vals = (f"{p['field_code']} · {p['field']}", universe, p['geography'], p['period'], p['metric'],
                p['value_text'], f'{ci} / {cv}', status, str(p['sample_size']), p['source_id'], refs[p['record_id']])
        parts.append('<tr>')
        parts += [f'<td>{escape(str(v))}</td>' for v in vals]
        parts.append('</tr>')
    parts.append('</tbody></table></div>')
    sources = ', '.join(sorted({p['source_id'] for p in rows}))
    print_caption = caption.split('. Fuentes:')[0]
    parts.append(f'<table class="print-table"><caption>{escape(print_caption)}. Fuentes: {escape(sources)}.</caption><thead><tr>')
    for heading in ('Campo / universo / lugar / periodo', 'Medida', 'Valor / IC90 / CV',
                    'Estado / n', 'Fuente / ref.'):
        parts.append(f'<th scope="col">{escape(heading)}</th>')
    parts.append('</tr></thead><tbody>')
    for p in rows:
        universe = 'Profesional 15+ edad conocida' if p['population_id']=='completed_professional_known_age' else 'Nacional 15+'
        ci = 'No disponible' if p['ci90_lower'] is None else f"{_number(p['ci90_lower'])}–{_number(p['ci90_upper'])}"
        cv = 'No disponible' if p['cv'] is None else f"{_number(p['cv'])} %"
        reason_es = {'project_singleton_adjustment':'ajuste singleton del proyecto',
                     'precision_suppressed':'precisión insuficiente',
                     'complementary_suppression':'supresión complementaria',
                     'unknown':'sin estimación', 'review_required':'revisión requerida',
                     'unsupported':'sin soporte', 'blocked':'bloqueado',
                     'synthetic_fixture':'muestra sintética'}.get(p['reason'], p['reason'] or 'sin motivo')
        context = f"{p['field_code']} · {p['field']} · {universe} · {p['recorded_sex']} · {p['geography']} · {p['period']}"
        lo = 'No disponible' if p['ci90_lower'] is None else _number(p['ci90_lower'])
        hi = 'No disponible' if p['ci90_upper'] is None else _number(p['ci90_upper'])
        if p['value'] is None:
            value_cell = '<span class="num">No disponible</span>'
        else:
            value_cell = ('<span class="num">'
                          + escape(_number(p['value'], 0 if p['unit']=='people' else 2))
                          + '</span> <span class="unit">' + escape(UNIT_LABELS[p['unit']]) + '</span>')
        numeric = (value_cell + '<br>IC90: '
                   + '<span class="num">' + escape(lo) + '</span> – <span class="num">'
                   + escape(hi) + '</span><br>CV: <span class="num">' + escape(cv) + '</span>')
        parts.append('<tr><td>' + escape(context) + '</td><td>' + escape(p['metric'])
                     + '</td><td>' + numeric + '</td><td>' + escape(f"{p['status']} · {reason_es} · n={p['sample_size']}")
                     + '</td><td>' + escape(p['source_id']) + '<br>'
                     + escape(refs[p['record_id']]) + '</td></tr>')
    parts.append('</tbody></table>')
    return ''.join(parts)


def _md_table(rows: list[dict], caption: str, refs: dict[str, str]) -> str:
    lines = [f'**{caption}**', '', '| Campo / código | Alcance | Geografía | Periodo | Medida | Valor / unidad | IC90 / CV | Estado y motivo | n observado | Fuente | Evidencia |',
             '| --- | --- | --- | --- | --- | --- | --- | --- | ---: | --- | --- |']
    for p in rows:
        ci = 'No disponible' if p['ci90_lower'] is None else f"{_number(p['ci90_lower'])}–{_number(p['ci90_upper'])}"
        cv = 'No disponible' if p['cv'] is None else f"{_number(p['cv'])} %"
        status = p['status'] + (f" · {p['reason']}" if p['reason'] else '')
        universe = ('Profesional 15+ edad conocida' if p['population_id']=='completed_professional_known_age'
                    else 'Nacional 15+') + ' · ' + p['recorded_sex']
        vals = (f"{p['field_code']} · {p['field']}", universe, p['geography'], p['period'], p['metric'],
                p['value_text'], f'{ci} / {cv}', status, str(p['sample_size']), p['source_id'], refs[p['record_id']])
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
table {border-collapse:collapse;min-width:900px;font-size:.78rem;line-height:1.38} .print-table {display:none} .compact-scroll{max-width:100%;overflow:auto} caption {text-align:left;font-weight:700;font-size:1rem;padding:.5rem 0}
th,td {text-align:left;vertical-align:top;border-bottom:1px solid #D5DEE2;padding:.4rem .55rem} th {background:#EDF2F4;color:#172B3A} td:last-child {overflow-wrap:anywhere;font-size:.72rem}
.evidence-id {overflow-wrap:anywhere;word-break:break-all;font-size:.74rem;margin:.16rem 0} .source-note,.small {font-size:.83rem;color:#405464} a {color:#145A66;text-decoration:underline}
article a,#fuentes p,figcaption {overflow-wrap:anywhere}
figure {margin:0} figcaption {font-size:.84rem;color:#405464;margin:.45rem 0} .print-panels {display:none}
@media(max-width:600px) {main {padding:1.4rem .9rem} h2 {font-size:1.45rem} .plot-scroll img {width:720px}}
@page {size:A4;margin:19mm 18mm 20mm 18mm;@bottom-left {content:"Brújula Laboral MX · v1.0.0";font:8pt LocalSans;color:#405464}@bottom-right {content:counter(page);font:8pt LocalSans;color:#405464}}
@media print {body{font:10.5pt/1.4 LocalSans,sans-serif}main{max-width:none;padding:0}h1{font-size:25pt}h2{font-size:16pt;break-after:avoid}h3{font-size:12pt;break-after:avoid}
.plot-scroll{display:none}.print-panels{display:block}.print-panel{break-inside:avoid;margin:5mm 0}.print-panel svg{width:100%;height:auto;max-height:225mm}
.table-scroll{display:none}.compact-scroll{overflow:visible}.print-table{display:table}table{min-width:0;width:100%;font-size:8.2pt;line-height:1.3;table-layout:fixed}thead{display:table-header-group}tr{break-inside:avoid}
th,td{padding:3pt;overflow-wrap:break-word}.num{white-space:nowrap}.print-table caption{font:700 9pt/1.25 LocalSans}.print-table th:nth-child(1){width:28%}.print-table th:nth-child(2){width:25%}.print-table th:nth-child(3){width:25%}.print-table th:nth-child(4){width:12%}.print-table th:nth-child(5){width:10%}
.print-comparisons th:nth-child(1){width:23%}.print-comparisons th:nth-child(2){width:24%}.print-comparisons th:nth-child(3){width:21%}.print-comparisons th:nth-child(4){width:10%}.print-comparisons th:nth-child(5){width:22%}
.evidence-id{font-size:8.5pt;word-break:normal;white-space:nowrap}
article{break-inside:avoid}.figure h3{break-after:avoid}figcaption{break-after:avoid}.screen-only{display:none}}
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
    build_date = datetime.now(timezone.utc).date().isoformat()
    intro = f"Ventana de observación: {periods[0]} a {periods[-1]}. Edición generada: {build_date} (UTC). Versión de publicación: v1.0.0. La fecha exacta de edición de la fuente no está disponible."
    html += ['<header><p class="eyebrow">Investigación laboral · México</p><h1>Brújula Laboral MX</h1>', f'<p class="lede">{escape(intro)}</p></header>']
    md += [intro, '']
    if warning:
        html.append(f'<p class="warning">{escape(warning)}</p>')
        md += [f'**{warning}**', '']
    claims = document['claims']
    refs = {rid: f'R{i:04d}' for i, rid in enumerate(sorted(model['records']), 1)}
    comp_refs = {c['comparison_id']: f'C{i:04d}'
                 for i,c in enumerate(sorted(model['comparisons'],key=lambda c:c['comparison_id']),1)}
    used_records = set()
    used_comparisons = set()

    def html_table(rows, caption, table_id):
        used_records.update(p['record_id'] for p in rows)
        return _html_table(rows, caption, table_id, refs)

    def md_table(rows, caption):
        return _md_table(rows, caption, refs)
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
        alt = _figure_alt(fig)
        source_line = 'Fuentes: ' + ', '.join(fig['source_ids']) + '. IC90 y CV son aproximaciones del proyecto, no precisión oficial del INEGI.'
        html.append(f'<div class="figure" id="{escape(fig["figure_id"])}"><h3>{escape(fig["title"])}</h3><figure>')
        html.append(f'<div class="plot-scroll" role="region" aria-label="Gráfica desplazable: {escape(fig["title"])}" tabindex="0"><img src="{result["svg"]}" alt="{escape(alt)}"></div>')
        html.append(_print_panels(fig))
        html.append(f'<figcaption>{escape(source_line)} Código de figura: {escape(fig["figure_id"])}.</figcaption></figure>')
        html.append(html_table(pts, fig['title'] + '. ' + source_line, fig['table_id']))
        html.append('</div>')
        md.extend([f'### {fig["title"]}', '', f'![{alt}]({result["svg"]})', '', source_line,
                   f'Figura: {fig["figure_id"]}. Tabla: {fig["table_id"]}.', '',
                   md_table(pts, fig['title']), ''])

    section('hallazgos')
    if not document['opening_claim_ids']:
        para('No hay hallazgos de apertura respaldados para esta edición; las celdas no disponibles conservan su motivo en las tablas.')
    for i, cid in enumerate(document['opening_claim_ids'], 1):
        c = claims[cid]
        html.append(f'<article id="claim-{i}"><h3>Hallazgo {i}: {escape(c["title"])}</h3>')
        md.extend([f'### Hallazgo {i}: {c["title"]}', ''])
        for field in ('observation', 'interpretation', 'limitation'):
            para(c[field])
        record_keys = ', '.join(refs[rid] for rid in c['record_ids'])
        html.append(f'<p class="small">Evidencia [{i}]: <a href="#evidencia">{escape(cid)}</a>; registros {escape(record_keys)}.</p></article>')
        md += [f'Evidencia [{i}]: {cid}; registros {record_keys}.', '']
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
    html.append(html_table(national, f'Detalle nacional y profesional · {latest} · 23 medidas por universo', 'table:national-detail'))
    md.extend([md_table(national, f'Detalle nacional y profesional · {latest}'), ''])
    end()

    for code, label, key in FOCAL:
        section(key)
        para(f'{label} ({code}) se refiere al campo de estudio reportado, no a una ocupación ni a una industria. Las 23 medidas del trimestre {latest} mantienen valor, unidad, IC90, CV, estado, motivo y evidencia propios.')
        rows = _record_rows(model, lambda r, code=code: r['field_of_study_id']==code and r['geography_id']=='mx' and r['recorded_sex_id']=='all' and r['period_id']==latest)
        html.append(html_table(rows, f'Perfil completo de {label} · {latest}', f'table:profile-{key}'))
        md.extend([md_table(rows, f'Perfil completo de {label} · {latest}'), ''])
        if key == 'politicas':
            figure_block('focal-latest')
        end()

    section('evolucion')
    para('Se presentan los ocho trimestres en orden cronológico. Las diferencias trimestrales adyacentes pueden reflejar estacionalidad; las comparaciones anuales usan el mismo trimestre. Las muestras pueden solaparse y no se estima significancia de la diferencia. Una celda no disponible interrumpe la serie.')
    figure_block('eight-quarter-trends')
    trend = figure_by_slug.get('eight-quarter-trends')
    if trend:
        accepted_comparisons = sorted(trend[0]['comparisons'],
                                      key=lambda c:(c['slot_periods'],c['comparison_type'],c['comparison_id']))
        html.append('<div class="table-scroll" role="region" aria-label="Comparaciones trimestrales desplazables" tabindex="0"><table id="table:trend-comparisons"><caption>Comparaciones descriptivas aceptadas para las series focales; sin intervalo ni prueba de significancia de la diferencia</caption><thead><tr>')
        comp_heads = ('Campo', 'Medida', 'Periodos', 'Tipo', 'Cambio absoluto', 'Estado', 'Evidencia')
        html.extend(f'<th scope="col">{escape(head)}</th>' for head in comp_heads)
        html.append('</tr></thead><tbody>')
        md.extend(['**Comparaciones descriptivas aceptadas de las series focales**', '',
                   '| Campo | Medida | Periodos | Tipo | Cambio absoluto | Estado | Evidencia |',
                   '| --- | --- | --- | --- | --- | --- | --- |'])
        for c in accepted_comparisons:
            record = model['records'][c['current_record_id']]
            comparison_type = {'adjacent_quarter':'trimestre adyacente',
                               'like_quarter_annual':'mismo trimestre anual'}[c['comparison_type']]
            display_unit = {'percentage points':'puntos porcentuales',
                            'nominal MXN/month':'MXN/mes nominales',
                            'people':'personas', 'hours/week':'horas/semana'}.get(
                                c['display_unit'], c['display_unit'])
            fields = (record['display']['field'], record['display']['metric'],
                      ' → '.join(c['slot_periods']), comparison_type,
                      f"{_number(c['absolute_change'])} {display_unit}",
                      c['status'], comp_refs[c['comparison_id']])
            html.append('<tr>' + ''.join(f'<td>{escape(str(value))}</td>' for value in fields) + '</tr>')
            md.append('| ' + ' | '.join(str(value).replace('|','\\|') for value in fields) + ' |')
            used_comparisons.add(c['comparison_id'])
        html.append('</tbody></table></div>')
        html.append(_print_comparison_table(accepted_comparisons, model, comp_refs))
        md.append('')
    for period in periods:
        html.append(f'<h3>{escape(period)}</h3>')
        md.extend([f'### {period}', ''])
        rows = _record_rows(model, lambda r, period=period: r['period_id']==period and r['field_of_study_id'] in {c[0] for c in FOCAL} and r['geography_id']=='mx' and r['recorded_sex_id']=='all' and r['metric_id'] in ('employment_rate','positive_income_mean','positive_income_coverage'))
        html.append(html_table(rows, f'Series focales · {period}', f'table:quarter-{period}'))
        md.extend([md_table(rows, f'Series focales · {period}'), ''])
    end()

    section('sexo-territorio')
    para(f'Los contrastes por sexo registrado y entidad son descriptivos en {latest}. Baja California (02) es referencia descriptiva declarada, no patrón de éxito; una celda suprimida impide ese contraste.')
    figure_block('recorded-sex')
    figure_block('state-availability')
    state_rows = _record_rows(model, lambda r: r['period_id']==latest and r['geography_id']!='mx' and r['metric_id']=='employment_rate' and r['field_of_study_id'] in ({'all'} | {c[0] for c in FOCAL}) and r['recorded_sex_id']=='all')
    html.append(html_table(state_rows, 'Disponibilidad por 32 entidades y cuatro grupos de campo', 'table:state-32x4'))
    md.extend([md_table(state_rows, 'Disponibilidad por 32 entidades y cuatro grupos de campo'), ''])
    end()

    section('otros-campos')
    para('Los campos identificables adicionales aparecen por código oficial de clasificación. El orden no constituye una clasificación de resultados; las celdas suprimidas siguen visibles.')
    figure_block('other-fields')
    end()

    section('cobertura')
    para('Cobertura y exclusiones se informan como conteos observados que pueden solaparse; no se suman como grupos excluyentes. Las cifras de ingreso positivo requieren respuesta conocida y denominador propio.')
    expected = model['coverage']['expected_cells']
    reasons = model['coverage']['missing_reasons']
    html.append('<div class="compact-scroll" role="region" aria-label="Tabla desplazable de celdas esperadas" tabindex="0"><table class="compact"><caption>Celdas esperadas por aparición de perfil; una celda puede aparecer en más de una vista</caption><thead><tr><th scope="col">Vista</th><th scope="col">Celdas esperadas</th></tr></thead><tbody>')
    md.extend(['| Vista | Celdas esperadas |', '| --- | ---: |'])
    for view, count in sorted(expected.items()):
        html.append(f'<tr><td>{escape(view)}</td><td>{_number(count,0)}</td></tr>')
        md.append(f'| {view} | {_number(count,0)} |')
    html.append('</tbody></table></div>')
    md.append('')
    html.append('<div class="compact-scroll" role="region" aria-label="Tabla desplazable de motivos sin valor" tabindex="0"><table class="compact"><caption>Motivos de celdas sin valor autorizado en el registro público</caption><thead><tr><th scope="col">Motivo</th><th scope="col">Celdas</th></tr></thead><tbody>')
    md.extend(['| Motivo | Celdas |', '| --- | ---: |'])
    for reason, count in sorted(reasons.items()):
        html.append(f'<tr><td>{escape(reason)}</td><td>{_number(count,0)}</td></tr>')
        md.append(f'| {reason} | {_number(count,0)} |')
    html.append('</tbody></table></div>')
    md.append('')
    para(f"Celdas públicas sin valor autorizado: {_number(model['coverage']['suppressed_cells'],0)}. Los conteos por vista son apariciones y no registros independientes.")
    coverage_cells = [c for c in model['profiles']['national'] if c['period_id']==latest and c['metric_id']=='employment_rate']
    coverage_cells += [c for c in model['profiles']['latest_fields'] if c['field_of_study_id'] in {x[0] for x in FOCAL} and c['metric_id']=='employment_rate']
    html.append('<div class="compact-scroll" role="region" aria-label="Tabla desplazable de cobertura y exclusiones" tabindex="0"><table class="compact"><caption>Cobertura observada, respuesta de ingreso positivo y exclusiones por perfil en el trimestre reciente</caption><thead><tr>')
    for heading in ('Perfil / universo', 'n observado', 'n elegible', 'Respuesta de ingreso conocido', 'Exclusiones observadas'):
        html.append(f'<th scope="col">{escape(heading)}</th>')
    html.append('</tr></thead><tbody>')
    md.extend(['| Perfil / universo | n observado | n elegible | Respuesta de ingreso conocido | Exclusiones observadas |', '| --- | ---: | ---: | --- | --- |'])
    for c in coverage_cells:
        cov = c['coverage']
        response = cov.get('exact_income_response') or {}
        response_text = (f"{_number(response.get('responding_n'),0)} de {_number(response.get('denominator_n'),0)}"
                         if response.get('responding_n') is not None else 'No disponible')
        exclusions = ', '.join(f"{key}: {_number(value,0)}" for key,value in sorted(cov.get('metric_exclusions',{}).items())) or 'Ninguna declarada'
        label = c.get('field_label') or ('Profesionales terminados, edad conocida' if c['population_id']=='completed_professional_known_age' else 'Contexto nacional 15+')
        vals = (label, _number(cov['observed_n'],0), _number(cov['metric_eligible_n'],0), response_text, exclusions)
        html.append('<tr>' + ''.join(f'<td>{escape(str(v))}</td>' for v in vals) + '</tr>')
        md.append('| ' + ' | '.join(str(v).replace('|','\\|') for v in vals) + ' |')
    html.append('</tbody></table></div>')
    md.append('')
    for limitation in model['limitations']:
        para(limitation)
    end()

    section('metodos')
    para('Fuente: INEGI, Encuesta Nacional de Ocupación y Empleo. Selección, estimación y transformación: Brújula Laboral MX; INEGI no avala esta precisión. La varianza se aproxima mediante el método Taylor del proyecto y el ajuste singleton documentado; los intervalos de 90 % no son intervalos oficiales. Las comparaciones son descriptivas y solo se publican cuando la definición aceptada es comparable.')
    para('Los identificadores v2r corresponden a registros públicos de diez dimensiones; v2c a comparaciones validadas; v2k a afirmaciones aceptadas. Los archivos de datos públicos mantienen precisión numérica distinta del redondeo de lectura de esta página.')
    end()

    section('fuentes')
    for sid, source in sorted(model['source_manifest']['sources'].items()):
        html.append(f'<p id="source-{escape(sid)}">INEGI ENOE, {escape(sid)} · periodo {escape(source["period_id"])} · SHA-256 {escape(source["sha256"])} · <a href="{escape(source["url"], quote=True)}">Archivo oficial</a></p>')
        md.extend([f'INEGI ENOE, {sid} · periodo {source["period_id"]} · SHA-256 {source["sha256"]} · [Archivo oficial]({source["url"]})', ''])
    terms = 'https://www.inegi.org.mx/inegi/terminos.html'
    html.append(f'<p>Fuente: INEGI, Encuesta Nacional de Ocupación y Empleo (ENOE). <a href="{terms}">Términos de libre uso de INEGI</a>. Selección, estimación y transformación: Brújula Laboral MX; no implica aval de INEGI.</p>')
    md.extend([f'Fuente: INEGI, Encuesta Nacional de Ocupación y Empleo (ENOE). [Términos de libre uso de INEGI]({terms}). Selección, estimación y transformación: Brújula Laboral MX; no implica aval de INEGI.', ''])
    end()

    section('evidencia')
    para('Índice exacto de afirmaciones, comparaciones y registros citados. Cada identificador permanece completo para su unión con las tablas y los datos públicos.')
    for f in document['figures']:
        used_records.update(f['record_ids'])
        used_comparisons.update(f['comparison_ids'])
    for c in model['claims']:
        used_records.update(c['record_ids'])
        if c['comparison_id']:
            used_comparisons.add(c['comparison_id'])
    for kind, ids in (('Afirmaciones v2k', sorted(claims)), ('Comparaciones v2c', sorted(used_comparisons)), ('Registros v2r', sorted(used_records))):
        html.append(f'<h3>{escape(kind)}</h3><div class="evidence-list">')
        md.extend([f'### {kind}', ''])
        for item_id in ids:
            label = ((refs[item_id] if kind.startswith('Registros') else comp_refs[item_id]) + ' · '
                     if not kind.startswith('Afirmaciones') else '')
            html.append(f'<p class="evidence-id">{escape(label + item_id)}</p>')
            md.append(f'- {label}{item_id}')
        html.append('</div>')
        md.append('')
    end()
    html.append('</main></body></html>')
    (root / 'report.html').write_text(''.join(html), encoding='utf-8')
    (root / 'report.md').write_text('\n'.join(md), encoding='utf-8')
    inventory = ['report.html', 'report.md', *fonts]
    for figure in figure_results:
        inventory.extend((figure['svg'], figure['png']))
    artifact_hashes = {name: hashlib.sha256((root / name).read_bytes()).hexdigest()
                       for name in sorted(inventory)}
    return {'html': 'report.html', 'markdown': 'report.md', 'figures': figure_results,
            'fonts': fonts, 'sections': [s['id'] for s in document['sections']],
            'claim_ids': document['opening_claim_ids'],
            'record_ids': sorted(used_records), 'comparison_ids': sorted(used_comparisons),
            'artifact_hashes': artifact_hashes}
