"""PDF resource isolation and searchable Spanish text."""

from pathlib import Path
import hashlib

import pytest

from brujula.pdf_v2 import LocalOnlyFetcher, render_pdf
from brujula.report_v2 import _print_comparison_table, _style, stage_report_fonts


def inventory(root, names):
    return {name: hashlib.sha256((root / name).read_bytes()).hexdigest() for name in names}


def test_fetcher_rejects_nonlocal_and_unlisted(tmp_path):
    (tmp_path / 'report.html').write_text('<h1>Árbol</h1>', encoding='utf-8')
    fonts = stage_report_fonts(tmp_path)
    fetcher = LocalOnlyFetcher(tmp_path, inventory(tmp_path, {'report.html', *fonts}))
    for url in ('https://example.org/x', 'data:text/plain,a', 'file:///etc/passwd',
                (tmp_path / 'absent.css').as_uri(), '../outside.css'):
        with pytest.raises((ValueError, FileNotFoundError)):
            fetcher(url)


def test_missing_or_changed_font_blocks_pdf(tmp_path):
    (tmp_path / 'report.html').write_text('<h1>Árbol</h1>', encoding='utf-8')
    fonts = stage_report_fonts(tmp_path)
    output = tmp_path / 'report.pdf'
    (tmp_path / fonts[0]).unlink()
    with pytest.raises((ValueError, FileNotFoundError)):
        render_pdf(tmp_path / 'report.html', tmp_path, output,
                   allowed_assets={'report.html': hashlib.sha256((tmp_path / 'report.html').read_bytes()).hexdigest(),
                                   **{name: '0'*64 for name in fonts}})
    assert not output.exists()
    stage_report_fonts(tmp_path)
    (tmp_path / fonts[0]).write_bytes(b'altered')
    with pytest.raises(ValueError):
        render_pdf(tmp_path / 'report.html', tmp_path, output,
                   allowed_assets={'report.html': hashlib.sha256((tmp_path / 'report.html').read_bytes()).hexdigest(),
                                   **{name: '0'*64 for name in fonts}})


def test_pdf_has_searchable_accents(tmp_path):
    from pypdf import PdfReader
    (tmp_path / 'report.html').write_text(
        '<!doctype html><html lang="es"><head><meta charset="utf-8">'
        '<style>@font-face{font-family:LocalSans;src:url("assets/fonts/DejaVuSans.ttf")}'
        'body{font-family:LocalSans}</style></head><body><h1>Árbol y profesión</h1></body></html>',
        encoding='utf-8')
    fonts = stage_report_fonts(tmp_path)
    pdf = render_pdf(tmp_path / 'report.html', tmp_path, tmp_path / 'report.pdf',
                     allowed_assets=inventory(tmp_path, {'report.html', *fonts}))
    reader = PdfReader(pdf)
    text = '\n'.join(page.extract_text() for page in reader.pages)
    assert 'Árbol y profesión' in text
    fonts_used = [font.get_object() for font in reader.pages[0]['/Resources']['/Font'].values()]
    descendants = [child.get_object() for font in fonts_used
                   for child in font.get('/DescendantFonts', [])]
    assert any('/FontFile2' in font['/FontDescriptor'].get_object()
               for font in [*fonts_used, *descendants] if '/FontDescriptor' in font)


def test_all_listed_assets_are_checked_even_when_unused(tmp_path):
    (tmp_path / 'report.html').write_text('<h1>Informe</h1>', encoding='utf-8')
    fonts = stage_report_fonts(tmp_path)
    (tmp_path / 'unused.png').write_bytes(b'public-asset')
    names = {'report.html', 'unused.png', *fonts}
    hashes = inventory(tmp_path, names)
    (tmp_path / 'unused.png').write_bytes(b'changed')
    with pytest.raises(ValueError, match='Altered PDF asset'):
        render_pdf(tmp_path/'report.html', tmp_path, tmp_path/'report.pdf', allowed_assets=hashes)
    assert not (tmp_path/'report.pdf').exists()
    (tmp_path / 'unused.png').unlink()
    with pytest.raises(FileNotFoundError):
        render_pdf(tmp_path/'report.html', tmp_path, tmp_path/'report.pdf', allowed_assets=hashes)


def test_external_destination_does_not_create_directory(tmp_path):
    (tmp_path / 'report.html').write_text('<h1>Informe</h1>', encoding='utf-8')
    fonts = stage_report_fonts(tmp_path)
    outside = tmp_path.parent / 'no-such-pdf-folder'
    with pytest.raises(ValueError):
        render_pdf(tmp_path/'report.html', tmp_path, outside/'report.pdf',
                   allowed_assets=inventory(tmp_path, {'report.html', *fonts}))
    assert not outside.exists()


def test_fetcher_hashes_exact_returned_bytes_after_path_check(tmp_path, monkeypatch):
    asset = tmp_path / 'a.txt'
    asset.write_bytes(b'authorized')
    fetcher = LocalOnlyFetcher(tmp_path, inventory(tmp_path, {'a.txt'}))
    original_resolve = fetcher.resolve
    def switched(url):
        path = original_resolve(url)
        path.write_bytes(b'other-bytes')
        return path
    monkeypatch.setattr(fetcher, 'resolve', switched)
    with pytest.raises(ValueError, match='changed during read'):
        fetcher(asset.as_uri())


def test_html_is_passed_as_verified_bytes_not_reopened(tmp_path, monkeypatch):
    import weasyprint
    (tmp_path / 'report.html').write_text('<h1>Verificado</h1>', encoding='utf-8')
    fonts = stage_report_fonts(tmp_path)
    called = {}
    class FakeHTML:
        def __init__(self, **kwargs):
            called.update(kwargs)
        def write_pdf(self):
            return b'%PDF-fake'
    monkeypatch.setattr(weasyprint, 'HTML', FakeHTML)
    render_pdf(tmp_path/'report.html', tmp_path, tmp_path/'report.pdf',
               allowed_assets=inventory(tmp_path, {'report.html', *fonts}))
    assert called['string'] == '<h1>Verificado</h1>'
    assert 'filename' not in called and called['base_url'] == (tmp_path/'report.html').as_uri()


def test_accepted_trend_change_and_context_survive_print_pdf(tmp_path):
    from pypdf import PdfReader
    comparison = {'comparison_id':'v2c:accepted', 'previous_record_id':'v2r:first',
                  'current_record_id':'v2r:second', 'slot_periods':['2025-Q1','2026-Q1'],
                  'comparison_type':'like_quarter_annual', 'display_unit':'percentage points',
                  'absolute_change':2.5, 'status':'REVIEW'}
    model = {'records':{
        'v2r:first':{'record':{'source_snapshot_id':'enoe_2025_q1'}},
        'v2r:second':{'record':{'source_snapshot_id':'enoe_2026_q1'},
                      'display':{'field':'Derecho','metric':'Tasa de empleo'}}}}
    table = _print_comparison_table([comparison], model, {'v2c:accepted':'C0001'})
    (tmp_path/'report.html').write_text('<!doctype html><html lang="es"><head><meta charset="utf-8"><style>'
                                        + _style() + '</style></head><body>' + table + '</body></html>',
                                        encoding='utf-8')
    fonts = stage_report_fonts(tmp_path)
    pdf = render_pdf(tmp_path/'report.html', tmp_path, tmp_path/'report.pdf',
                     allowed_assets=inventory(tmp_path, {'report.html', *fonts}))
    extracted = '\n'.join(page.extract_text() for page in PdfReader(pdf).pages)
    flattened = ' '.join(extracted.split())
    assert 'Comparaciones descriptivas aceptadas para las series focales' in flattened
    assert 'Cambio absoluto' in flattened and '2,50 puntos porcentuales' in flattened
    assert '2025-Q1' in flattened and '2026-Q1' in flattened
    assert 'mismo trimestre anual' in flattened
    assert 'enoe_2025_q1' in flattened and 'enoe_2026_q1' in flattened
    assert 'C0001' in flattened
