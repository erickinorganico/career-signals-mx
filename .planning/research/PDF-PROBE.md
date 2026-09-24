# Offline PDF feasibility probe

Verified on Windows 11, 2026-09-22 local. This is a synthetic format test, not the final publication or a release gate pass.

- Official [WeasyPrint 70.0 Windows onedir release](https://github.com/Kozea/WeasyPrint/releases/tag/v70.0), ZIP 32,271,073 bytes; GitHub-declared and locally verified SHA-256 `ab1151f210b4e6bb7aa7a79e91a67e8ddb760094c107bfda55241b6aaefe7d53`.
- Standalone CLI reports WeasyPrint 70.0, Python 3.14.7, Pydyf 0.12.1, Pango 15802. Synthetic local HTML converted successfully without stderr using a project-local Fontconfig cache.
- Separately installed official PyPI `weasyprint==70.0` in ignored `.cache/pdf-env` under Python 3.12.13. With `WEASYPRINT_DLL_DIRECTORIES` pointing to the verified release's `_internal` directory and `FONTCONFIG_FILE` pointing to a local configuration, the Python library CLI also produced the PDF successfully. The project runtime dependencies were not changed by this spike.
- Canonical test: Spanish accents, inline SVG, 80 table rows, repeating headers, A4 and page numbering. Reader check: 5 pages, all 80 row labels, accents retained. First and last page visually inspected: no clipping, intact figure, readable table and page counters.
- Evidence retained locally: `.cache/research/pdf_smoke.py`, `pdf-smoke-receipt.json`, `pdf-smoke.html`, `pdf-smoke.pdf`, `pdf-library-smoke.pdf`, `pdf-smoke-contact.png`. Software/env/font caches stay ignored and are not redistributed.

## Phase 4 implications

Keep the recommended WeasyPrint 70.0 approach. Use the Python API with a project-owned URL fetcher restricted to validated local artifacts; do not permit renderer network fetches. Windows can use documented MSYS2/Pango installation or the verified official binary distribution as a bounded local DLL source. Document explicit environment setup, never silently change machine-wide PATH or font settings. Linux clean CI still needs its own Pango install/render check. Final report parity, suppression, tables/figures and visual review remain required; this synthetic proof does not satisfy them.

Official guidance: [installation and Windows/Pango settings](https://doc.courtbouillon.org/weasyprint/latest/first_steps.html). The portable product must not depend on Codex's bundled PDF inspection interpreter.
