"""A4 PDF rendering with an exact local staged-asset allowlist."""

from __future__ import annotations

import hashlib
import logging
import mimetypes
import os
from pathlib import Path, PurePosixPath
import tempfile
from urllib.parse import unquote, urlsplit
import re

from .report_v2 import FONT_NAMES, FONT_SHA256


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class LocalOnlyFetcher:
    """Allow exact existing regular files below one staged publication root."""

    def __init__(self, asset_root: str | Path, allowed_assets):
        self._fail_on_errors = True
        original_root = Path(asset_root)
        if original_root.is_symlink():
            raise ValueError('Symlink PDF stage root')
        self.root = original_root.resolve(strict=True)
        if not isinstance(allowed_assets, dict) or not allowed_assets:
            raise ValueError('PDF requires exact path-to-SHA inventory')
        self.allowed = {}
        for name, digest in allowed_assets.items():
            if not isinstance(name, str) or not name or '\\' in name:
                raise ValueError('Invalid asset inventory path')
            path = PurePosixPath(name)
            if path.is_absolute() or any(part in ('', '.', '..') for part in path.parts) or path.as_posix() != name:
                raise ValueError(f'Unsafe asset inventory path: {name}')
            if not isinstance(digest, str) or not re.fullmatch(r'[0-9a-f]{64}', digest):
                raise ValueError(f'Invalid asset SHA-256: {name}')
            self.allowed[name] = digest
        self.verify_inventory()

    def resolve(self, url: str) -> Path:
        parsed = urlsplit(url)
        if parsed.scheme not in ('', 'file') or parsed.netloc not in ('', 'localhost') or parsed.query or parsed.fragment:
            raise ValueError(f'External or ambiguous PDF asset URL: {url}')
        raw = unquote(parsed.path)
        if '%' in raw or '\\' in raw or '\x00' in raw:
            raise ValueError(f'Unsafe encoded PDF path: {url}')
        if parsed.scheme == 'file':
            candidate = Path(raw)
            # Windows file URLs encode drive letters as /C:/...
            if os.name == 'nt' and raw.startswith('/') and len(raw) > 2 and raw[2] == ':':
                candidate = Path(raw[1:])
            if not candidate.is_absolute():
                raise ValueError(f'Nonabsolute file URL: {url}')
            try:
                rel = candidate.relative_to(self.root)
            except ValueError as exc:
                raise ValueError(f'PDF asset outside stage: {url}') from exc
        else:
            rel = Path(raw)
            if rel.is_absolute():
                raise ValueError(f'Absolute PDF asset path: {url}')
        if any(part in ('', '.', '..') for part in rel.parts):
            raise ValueError(f'PDF path traversal: {url}')
        key = rel.as_posix()
        if key not in self.allowed:
            raise ValueError(f'Unlisted PDF asset: {key}')
        candidate = self.root / rel
        if candidate.is_symlink() or any(parent.is_symlink() for parent in candidate.parents if parent != self.root):
            raise ValueError(f'Symlink PDF asset: {key}')
        resolved = candidate.resolve(strict=True)
        if not resolved.is_relative_to(self.root) or not resolved.is_file():
            raise ValueError(f'Escaped or nonfile PDF asset: {key}')
        if _sha(resolved) != self.allowed[key]:
            raise ValueError(f'Altered PDF asset: {key}')
        return resolved

    def verify_inventory(self):
        for name in self.allowed:
            self.resolve((self.root / name).as_uri())

    def __call__(self, url: str, *args, **kwargs):
        from weasyprint.urls import URLFetcherResponse
        path = self.resolve(url)
        content = path.read_bytes()
        key = path.relative_to(self.root).as_posix()
        if hashlib.sha256(content).hexdigest() != self.allowed[key]:
            raise ValueError(f'PDF asset changed during read: {key}')
        return URLFetcherResponse(path.as_uri(), content,
                                  {'Content-Type': mimetypes.guess_type(path.name)[0] or 'application/octet-stream'})


class _ResourceErrors(logging.Handler):
    def __init__(self):
        super().__init__(level=logging.WARNING)
        self.messages = []

    def emit(self, record):
        if record.levelno >= logging.ERROR:
            self.messages.append(record.getMessage())
        elif record.levelno >= logging.WARNING:
            message = record.getMessage()
            if any(token in message.lower() for token in
                   ('font-face', 'failed to load', 'failed to fetch', 'image at', 'resource')):
                self.messages.append(message)


def render_pdf(html_path: str | Path, asset_root: str | Path, pdf_path: str | Path, *, allowed_assets) -> Path:
    """Render only a complete staged report; fail on any missing/altered resource."""
    root_candidate = Path(asset_root)
    if root_candidate.is_symlink():
        raise ValueError('Symlink PDF stage root')
    root = root_candidate.resolve(strict=True)
    fetcher = LocalOnlyFetcher(root_candidate, allowed_assets)
    html_candidate = Path(html_path)
    if html_candidate.is_symlink():
        raise ValueError('Symlink PDF HTML')
    html = html_candidate.resolve(strict=True)
    if html != fetcher.resolve(html.as_uri()):
        raise ValueError('HTML outside declared PDF asset inventory')
    for name in FONT_NAMES:
        rel = f'assets/fonts/{name}'
        path = fetcher.resolve((root / rel).as_uri())
        if _sha(path) != FONT_SHA256[name]:
            raise ValueError(f'Altered staged font asset: {name}')
    try:
        import weasyprint
    except (ImportError, OSError) as exc:
        raise RuntimeError('WeasyPrint 70.0 and native Pango/Fontconfig are required') from exc
    if weasyprint.__version__ != '70.0':
        raise RuntimeError('WeasyPrint 70.0 required')
    HTML = weasyprint.HTML
    response = fetcher(html.as_uri())
    try:
        verified_html = response.read().decode('utf-8')
    finally:
        response.close()
    logger = logging.getLogger('weasyprint')
    errors = _ResourceErrors()
    logger.addHandler(errors)
    try:
        result = HTML(string=verified_html, base_url=html.as_uri(), url_fetcher=fetcher).write_pdf()
    finally:
        logger.removeHandler(errors)
    if errors.messages:
        raise RuntimeError('PDF rendering warnings/errors: ' + '; '.join(errors.messages[:3]))
    if not result.startswith(b'%PDF-'):
        raise RuntimeError('PDF rendering produced no valid PDF header')
    fetcher.verify_inventory()
    target = Path(pdf_path)
    if target.exists() and target.is_symlink():
        raise ValueError('Symlink PDF destination')
    if any(parent.is_symlink() for parent in target.parents if parent != root):
        raise ValueError('Symlink PDF destination parent')
    if not target.parent.exists() or not target.parent.resolve(strict=True).is_relative_to(root):
        raise ValueError('PDF destination outside stage')
    fd, temp_name = tempfile.mkstemp(prefix='.report-', suffix='.pdf', dir=target.parent)
    try:
        with os.fdopen(fd, 'wb') as stream:
            stream.write(result)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temp_name, target)
    finally:
        if os.path.exists(temp_name):
            os.unlink(temp_name)
    return target
