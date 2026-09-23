"""PDF resource isolation and searchable Spanish text."""

from pathlib import Path
import hashlib

import pytest

from brujula.pdf_v2 import LocalOnlyFetcher, render_pdf
from brujula.report_v2 import stage_report_fonts


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
    text = '\n'.join(page.extract_text() for page in PdfReader(pdf).pages)
    assert 'Árbol y profesión' in text


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
