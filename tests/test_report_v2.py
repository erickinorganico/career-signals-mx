"""Public editorial rendering preserves accepted identities and missingness."""

import json
from pathlib import Path

import pytest

from brujula.publication_v2 import build_publication_model
from brujula.report_v2 import build_editorial_document, render_publication


@pytest.fixture(scope="module")
def model():
    packet = json.loads(Path('.cache/research/phase4-analysis/analysis.json').read_text(encoding='utf-8'))
    return build_publication_model(packet)


def test_editorial_scope_and_identity(model):
    document = build_editorial_document(model)
    assert [section['id'] for section in document['sections']] == [
        'hallazgos', 'lectura', 'contexto', 'derecho', 'comunicacion',
        'politicas', 'evolucion', 'sexo-territorio', 'otros-campos',
        'cobertura', 'metodos', 'fuentes', 'evidencia']
    assert document['opening_claim_ids'] == model['opening_claim_ids']
    assert len(document['figures']) == len(model['figure_links']) == 9
    assert {f['figure_id'] for f in document['figures']} == {f['figure_id'] for f in model['figure_links']}
    for figure in document['figures']:
        assert set(figure['record_ids']) == {p['record_id'] for p in figure['points']}
        assert all(p['value'] == model['records'][p['record_id']]['record']['value'] for p in figure['points'])


def test_real_render_has_all_figures_and_staged_fonts(model, tmp_path):
    result = render_publication(model, tmp_path)
    assert (tmp_path / result['html']).is_file()
    assert (tmp_path / result['markdown']).is_file()
    assert len(result['figures']) == 9
    assert len(result['fonts']) == 5
    html = (tmp_path / result['html']).read_text(encoding='utf-8')
    assert 'SYNTHETIC' not in html
    for figure in result['figures']:
        assert (tmp_path / figure['svg']).is_file()
        assert (tmp_path / figure['png']).is_file()
        assert figure['figure_id'] in html
        assert figure['table_id'] in html
    assert 'Ciencias políticas' in html
    assert 'Baja California' in html
