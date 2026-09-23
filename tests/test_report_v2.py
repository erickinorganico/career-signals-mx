"""Public editorial rendering preserves accepted identities and missingness."""

import pytest

from brujula.publication_v2 import build_publication_model
from brujula.report_v2 import (SERIES_STYLES, _figure_alt, _html_table, _plot, _plot_figure,
                               _print_panels, _style,
                               build_editorial_document, render_publication)
from tests.publication_v2_support import pinned_synthetic_packet


@pytest.fixture(scope="module")
def model(monkeypatch_module):
    packet = pinned_synthetic_packet(monkeypatch_module)
    return build_publication_model(packet)


@pytest.fixture(scope="module")
def monkeypatch_module():
    with pytest.MonkeyPatch.context() as patch:
        yield patch


def test_editorial_scope_and_identity(model):
    document = build_editorial_document(model)
    assert [section['id'] for section in document['sections']] == [
        'hallazgos', 'lectura', 'contexto', 'derecho', 'comunicacion',
        'politicas', 'evolucion', 'sexo-territorio', 'otros-campos',
        'cobertura', 'metodos', 'fuentes', 'evidencia']
    assert document['opening_claim_ids'] == model['opening_claim_ids']
    assert len(document['figures']) == len(model['figure_links'])
    assert {f['figure_id'] for f in document['figures']} == {f['figure_id'] for f in model['figure_links']}
    for figure in document['figures']:
        assert set(figure['record_ids']) == {p['record_id'] for p in figure['points']}
        assert all(p['value'] == model['records'][p['record_id']]['record']['value'] for p in figure['points'])


def test_real_render_has_all_figures_and_staged_fonts(model, tmp_path):
    result = render_publication(model, tmp_path)
    assert (tmp_path / result['html']).is_file()
    assert (tmp_path / result['markdown']).is_file()
    assert len(result['figures']) == len(model['figure_links'])
    assert len(result['fonts']) == 5
    html = (tmp_path / result['html']).read_text(encoding='utf-8')
    assert 'DATOS SINTÉTICOS' in html
    for figure in result['figures']:
        assert (tmp_path / figure['svg']).is_file()
        assert (tmp_path / figure['png']).is_file()
        assert figure['figure_id'] in html
        assert figure['table_id'] in html
    assert 'Ciencias políticas' in html
    assert 'Baja California' in html


def _point(record_id, *, metric='employment_rate', unit='percent', value=71.0,
           period='2026-Q1', field='033100'):
    return {'record_id': record_id, 'field_code': field, 'metric_id': metric,
            'metric': metric, 'unit': unit, 'population': 'personas profesionales',
            'period': period, 'value': value, 'ci90_lower': None if value is None else value-1,
            'ci90_upper': None if value is None else value+1, 'status': 'UNKNOWN' if value is None else 'REVIEW',
            'reason': 'unknown' if value is None else None, 'geography_id': 'mx',
            'geography': 'México', 'recorded_sex_id': 'all', 'recorded_sex': 'todos',
            'source_id': 'enoe_2026_q1', 'field': 'Derecho'}


def test_plot_separates_units_and_null_is_not_zero(tmp_path):
    points = [_point('v2r:a', value=70), _point('v2r:b', value=None),
              _point('v2r:c', metric='positive_income_mean', unit='MXN/month', value=18000)]
    figure = {'slug':'focal-latest','figure_id':'figure:focal-latest',
              'title':'¿Qué muestran los valores?', 'points':points,
              'periods':['2026-Q1'],'synthetic':True,'source_ids':['enoe_2026_q1']}
    chart = _plot_figure(figure, points)
    assert len(chart.axes) == 2
    assert any('No disponible' in text.get_text() for text in chart.axes[0].texts)
    assert not any(list(line.get_xdata()) == [0] for line in chart.axes[0].lines)
    import matplotlib.pyplot as plt
    plt.close(chart)
    svg, png = _plot(figure, tmp_path)
    svg_text = (tmp_path / svg).read_text(encoding='utf-8')
    from PIL import Image
    png_meta = Image.open(tmp_path / png).info['Description']
    assert '<title>' in svg_text and '<desc>' in svg_text
    assert 'v2r:b' in svg_text and '"value":null' in svg_text
    assert 'v2r:b' in png_meta and '"value":null' in png_meta
    assert 'DATOS SINTÉTICOS' in svg_text and 'DATOS SINTÉTICOS' in png_meta


def test_trend_lines_require_accepted_adjacent_pair():
    assert SERIES_STYLES['033100'][1:] == ('o', 'Derecho')
    assert SERIES_STYLES['032100'][1:] == ('s', 'Comunicación y periodismo')
    assert SERIES_STYLES['031300'][1:] == ('^', 'Ciencias políticas')
    points = [_point('a', value=70, period='2026-Q1'),
              _point('b', value=None, period='2026-Q2'),
              _point('c', value=72, period='2026-Q3')]
    figure = {'slug':'eight-quarter-trends','title':'¿Cómo cambió?',
              'points':points,'periods':['2026-Q1','2026-Q2','2026-Q3'],
              'comparisons':[], 'synthetic':True}
    chart = _plot_figure(figure, points)
    assert not any(len(line.get_xdata()) == 2 for line in chart.axes[0].lines)
    assert any('No disponible' in text.get_text() for text in chart.axes[0].texts)
    import matplotlib.pyplot as plt
    plt.close(chart)
    points[1] = _point('b', value=71, period='2026-Q2')
    figure['comparisons'] = [{'previous_record_id':'a','current_record_id':'b',
                              'comparable':True,'status':'REVIEW','comparison_type':'adjacent_quarter'}]
    chart = _plot_figure(figure, points)
    segments = [line for line in chart.axes[0].lines if len(line.get_xdata()) == 2]
    assert len(segments) == 1 and list(segments[0].get_ydata()) == [70,71]
    plt.close(chart)


def test_print_panels_preserve_exact_record_union():
    points = [_point(f'v2r:{i:03d}', value=70+i) for i in range(17)]
    figure = {'slug':'state-availability','figure_id':'figure:state-availability',
              'title':'¿Dónde?', 'points':points, 'periods':['2026-Q1'],
              'source_ids':['enoe_2026_q1'], 'synthetic':True}
    html = _print_panels(figure)
    import re
    groups = re.findall(r'data-record-ids="([^"]+)"', html)
    assert len(groups) == 2
    assert [rid for group in groups for rid in group.split('|')] == [p['record_id'] for p in points]
    ids = re.findall(r'(?<![\w-])id="([^"]+)"', html)
    assert len(ids) == len(set(ids))
    widths = [float(item) for item in re.findall(r'<svg[^>]*\bwidth="([0-9.]+)pt"', html)]
    assert len(widths) == 2 and all(480 <= width <= 500 for width in widths)


def test_fully_unavailable_panel_has_no_quantitative_scale():
    point = _point('v2r:null', value=None)
    point['population_id'] = 'completed_professional_known_age'
    figure = {'slug':'other-fields','figure_id':'figure:other-fields',
              'table_id':'table:other-fields','title':'¿Hay datos?',
              'points':[point], 'periods':['2026-Q1'],
              'source_ids':['enoe_2026_q1'], 'synthetic':False}
    chart = _plot_figure(figure, [point])
    ax = chart.axes[0]
    assert not ax.xaxis.get_visible()
    assert not ax.lines
    assert any('Sin valores autorizados' in item.get_text() for item in ax.texts)
    assert 'sin valores autorizados' in _figure_alt(figure).lower()
    import matplotlib.pyplot as plt
    plt.close(chart)


def test_alt_uses_public_value_scope_source_and_missingness():
    visible = _point('v2r:visible', value=71)
    missing = _point('v2r:missing', value=None)
    for p in (visible, missing):
        p['population_id'] = 'completed_professional_known_age'
        p['value_text'] = '71,00 %' if p['value'] is not None else 'No disponible'
    figure = {'title':'¿Qué muestra Derecho?', 'points':[visible, missing],
              'source_ids':['enoe_2026_q1'], 'table_id':'table:test', 'synthetic':False}
    alt = _figure_alt(figure)
    assert '71,00 %' in alt and 'profesionales terminados' in alt
    assert '2026-Q1' in alt and 'enoe_2026_q1' in alt
    assert '1 puntos sin valor' in alt
    assert 'No disponible: 71' not in alt


def test_alt_distinguishes_state_and_recorded_sex_values():
    points = [_point('v2r:state-a', value=71), _point('v2r:state-b', value=69)]
    for point, geography, geography_id, sex, sex_id, value in (
        (points[0], 'Baja California', '02', 'mujeres', 'female', '71,00 %'),
        (points[1], 'Sonora', '26', 'hombres', 'male', '69,00 %'),
    ):
        point.update(population_id='completed_professional_known_age',
                     geography=geography, geography_id=geography_id,
                     recorded_sex=sex, recorded_sex_id=sex_id, value_text=value)
    figure = {'slug':'state-availability', 'title':'¿Dónde?', 'points':points,
              'source_ids':['enoe_2026_q1'], 'table_id':'table:states', 'synthetic':False}
    alt = _figure_alt(figure)
    assert 'Baja California (02), sexo registrado mujeres (female)' in alt
    assert 'Sonora (26), sexo registrado hombres (male)' in alt
    assert '71,00 %' in alt and '69,00 %' in alt
    assert alt.index('Baja California') < alt.index('Sonora')


def test_standalone_figure_has_readable_sex_units_period_and_source():
    point = _point('v2r:sex', metric='income', unit='MXN/month', value=12000)
    point.update(recorded_sex='mujeres', recorded_sex_id='female')
    figure = {'slug':'recorded-sex', 'title':'¿Qué se observa?', 'points':[point],
              'periods':['2026-Q1'], 'source_ids':['enoe_2026_q1'], 'synthetic':True}
    chart = _plot_figure(figure, [point])
    axis = chart.axes[0]
    assert 'mujeres (female)' in axis.get_yticklabels()[0].get_text()
    assert 'MXN/mes nominales' in axis.get_xlabel()
    footer = '\n'.join(artist.get_text() for artist in chart.texts)
    assert 'INEGI ENOE' in footer and 'enoe_2026_q1' in footer
    assert '2026-Q1' in footer and 'precisión no oficial' in footer
    assert 'DATOS SINTÉTICOS' in footer
    import matplotlib.pyplot as plt
    plt.close(chart)


def test_print_layout_contains_first_missing_row_and_wraps_long_titles():
    points = [_point('v2r:missing-first', value=None), _point('v2r:visible-second', value=70)]
    for point in points:
        point['metric'] = 'cobertura de ingreso positivo conocido entre personas ocupadas'
    figure = {'slug':'other-fields', 'title':'¿Qué datos hay?', 'points':points,
              'periods':['2026-Q1'], 'source_ids':['enoe_2026_q1'], 'synthetic':False}
    chart = _plot_figure(figure, points, print_mode=True)
    axis = chart.axes[0]
    assert axis.get_ylim()[1] < 0 < axis.get_ylim()[0]
    assert '\n' in axis.get_title(loc='left')
    css = _style()
    assert 'article a,#fuentes p,figcaption {overflow-wrap:anywhere}' in css
    assert '.figure{break-before:page}' not in css
    import matplotlib.pyplot as plt
    plt.close(chart)


def test_print_income_keeps_number_intact_and_wraps_nominal_unit():
    point = _point('v2r:income', metric='positive_income_mean', unit='MXN/month',
                   value=17231.75)
    point.update(value_text='17\u00a0231,75\u00a0MXN/mes nominales',
                 population_id='completed_professional_known_age', sample_size=1704,
                 cv=None, reason=None, source_id='enoe_2026_q2')
    html = _html_table([point], 'Ingreso', 'table:income', {'v2r:income':'R0001'})
    assert '<span class="num">17\u00a0231,75</span> <span class="unit">MXN/mes nominales</span>' in html
    assert '<span class="num">17\u00a0231,75\u00a0MXN/mes nominales</span>' not in html
