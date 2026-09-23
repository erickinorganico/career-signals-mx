"""PDF resource isolation and searchable Spanish text."""

from pathlib import Path

import pytest

from brujula.pdf_v2 import LocalOnlyFetcher, render_pdf
from brujula.report_v2 import stage_report_fonts


def test_fetcher_rejects_nonlocal_and_unlisted(tmp_path):
    (tmp_path / 'report.html').write_text('<h1>Árbol</h1>', encoding='utf-8')
    fonts = stage_report_fonts(tmp_path)
    fetcher = LocalOnlyFetcher(tmp_path, {'report.html', *fonts})
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
        render_pdf(tmp_path / 'report.html', tmp_path, output, allowed_assets={'report.html', *fonts})
    assert not output.exists()
    stage_report_fonts(tmp_path)
    (tmp_path / fonts[0]).write_bytes(b'altered')
    with pytest.raises(ValueError):
        render_pdf(tmp_path / 'report.html', tmp_path, output, allowed_assets={'report.html', *fonts})


def test_pdf_has_searchable_accents(tmp_path):
    from pypdf import PdfReader
    (tmp_path / 'report.html').write_text(
        '<!doctype html><html lang="es"><head><meta charset="utf-8">'
        '<style>@font-face{font-family:LocalSans;src:url("assets/fonts/DejaVuSans.ttf")}'
        'body{font-family:LocalSans}</style></head><body><h1>Árbol y profesión</h1></body></html>',
        encoding='utf-8')
    fonts = stage_report_fonts(tmp_path)
    pdf = render_pdf(tmp_path / 'report.html', tmp_path, tmp_path / 'report.pdf',
                     allowed_assets={'report.html', *fonts})
    text = '\n'.join(page.extract_text() for page in PdfReader(pdf).pages)
    assert 'Árbol y profesión' in text
