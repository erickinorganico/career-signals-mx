# Dependency, license, and source inventory

Status: preparation evidence for the v1.0.0 Phase 5 release review; this
document is not a release approval. Checked 2026-09-22 in the local checkout of
`career-signals-mx`.

## Scope and evidence

The project source, documentation, schemas, catalog metadata, and synthetic
fixtures are covered by the repository [MIT license](../../LICENSE). The wheel
does not bundle the Python environments or execution artifacts. Current package
evidence is from installed distribution metadata in the ignored local `.venv` with
Python 3.12.13, cross-checked against the exact pins in
[`pyproject.toml`](../../pyproject.toml) and [`requirements.txt`](../../requirements.txt).
The existing machine-readable snapshot is
[`docs/evidence/dependency-licenses.json`](../evidence/dependency-licenses.json);
package notices remain with their distributions.

The current v1.0.0 runtime closure contains the 23 pinned packages below. A package
license value shown as `metadata/classifier` means the installed metadata did
not expose a normalized SPDX expression; the distribution's license file and
notice remain authoritative for any future binary/environment redistribution.

| Package | Version | Current role | Observed license evidence |
|---|---:|---|---|
| attrs | 26.1.0 | jsonschema closure | `LICENSE` file; no normalized field |
| colorama | 0.4.6 | pytest/Windows console closure | BSD classifier; `LICENSE.txt` |
| contourpy | 1.4.0 | Matplotlib closure | `LICENSE` file |
| cycler | 0.12.1 | Matplotlib closure | BSD license text and `LICENSE` |
| duckdb | 1.4.4 | declared runtime storage/query | MIT classifier |
| fonttools | 4.65.0 | Matplotlib/PDF font handling | MIT field; `LICENSE`, `LICENSE.external` |
| iniconfig | 2.3.0 | pytest closure | `LICENSE` file |
| jsonschema | 4.26.0 | declared contract validation | `COPYING` file |
| jsonschema-specifications | 2025.9.1 | jsonschema closure | `COPYING` file |
| kiwisolver | 1.5.1 | Matplotlib closure | Modified BSD text and `LICENSE` |
| matplotlib | 3.10.8 | declared charts/rendering | Matplotlib license agreement in metadata; bundled component notices are included in the distribution |
| numpy | 2.5.3 | runtime numerical dependency in requirements | `LICENSE.txt` plus component notices (BSD-3-Clause/0BSD/MIT/Zlib/CC0 evidence in snapshot) |
| packaging | 26.3 | Python tooling closure | `LICENSE`, `LICENSE.APACHE`, `LICENSE.BSD` |
| pillow | 12.3.0 | Matplotlib/image closure | `LICENSE` file; metadata does not normalize expression |
| pluggy | 1.6.0 | pytest closure | MIT field/classifier; `LICENSE` |
| pygments | 2.21.0 | pytest/reporting closure | BSD-2-Clause evidence; `LICENSE` |
| pyparsing | 3.3.3 | Matplotlib closure | MIT evidence; `LICENSE` |
| pytest | 9.0.3 | test extra / verification only | MIT evidence; `LICENSE` |
| python-dateutil | 2.9.0.post0 | Matplotlib closure | dual BSD/Apache classifiers; `LICENSE` |
| referencing | 0.37.0 | jsonschema closure | `COPYING` file |
| rpds-py | 2026.6.3 | jsonschema closure | MIT evidence; `LICENSE` |
| six | 1.17.0 | python-dateutil closure | MIT field/classifier; `LICENSE` |
| typing-extensions | 4.16.0 | jsonschema closure | PSF-2.0 evidence; `LICENSE` |

The project declares DuckDB, jsonschema, Matplotlib, and NumPy as runtime
dependencies and pytest as a test extra. `requirements.txt` carries the exact
resolved closure. No package is copied into the source distribution by this
inventory.

## Planned PDF stack (separate from current runtime)

WeasyPrint 70.0 is planned, not a current project dependency. The ignored
`.cache/pdf-env` was independently inspected with Python 3.12.13 and contains:

| Component | Version | Observed license evidence | State |
|---|---:|---|---|
| WeasyPrint | 70.0 | BSD classifier and `LICENSE` file | planned PDF environment |
| pydyf | 0.12.1 | BSD classifier and `LICENSE` file | planned closure |
| tinyhtml5 | 2.1.0 | MIT classifier and `LICENSE` file | planned closure |
| cssselect2 | 0.10.1 | BSD classifier and `LICENSE` file | planned closure |
| cffi | 2.1.1 | `LICENSE` file; normalized expression not exposed | planned closure |
| fonttools | 4.65.0 | MIT plus `LICENSE.external` | shared planned closure |
| Pillow | 12.3.0 | `LICENSE` file; normalized expression not exposed | shared planned closure |
| brotli | 1.2.0 | MIT field; `LICENSE` | planned closure |
| pycparser | 3.0 | `LICENSE` file; normalized expression not exposed | planned closure |
| pyphen | 0.18.1 | GPLv2+/LGPLv2+/MPL 1.1 classifiers; `COPYING.*`, `LICENSE` | planned closure |
| tinycss2 | 1.5.1 | BSD classifier; `LICENSE` | planned closure |
| webencodings | 0.6.1 | BSD classifier; `LICENSE` | planned closure |
| zopfli | 0.4.3 | Apache-2.0 field/classifier; `COPYING` | planned closure |
| career-signals-mx | 0.1.0 | local editable project, repository MIT | environment install |

The exact `.cache/pdf-env` distribution listing is:
`brotli==1.2.0`, `career-signals-mx==0.1.0`, `cffi==2.1.1`,
`cssselect2==0.10.1`, `fonttools==4.65.0`, `pillow==12.3.0`,
`pycparser==3.0`, `pydyf==0.12.1`, `pyphen==0.18.1`, `tinycss2==1.5.1`,
`tinyhtml5==2.1.0`, `weasyprint==70.0`, `webencodings==0.6.1`, and
`zopfli==0.4.3`. The seven detailed rows above are the packages directly
relevant to the renderer; the remaining seven are transitive closure and must
have their complete notices captured if that environment is ever distributed.

The PDF probe records the official WeasyPrint 70.0 Windows onedir archive URL,
SHA-256 `ab1151f210b4e6bb7aa7a79e91a67e8ddb760094c107bfda55241b6aaefe7d53`,
and a successful synthetic five-page render in
[`PDF-PROBE.md`](../../.planning/research/PDF-PROBE.md). That receipt proves
local execution only. The portable archive, DLLs, caches, and PDF smoke files
remain ignored and are not release assets. The planned setup also needs native
Pango/DLL provenance and a clean CI proof before pinning it into a release
environment; the official installation guidance is linked from the probe.

The probe used `C:/Windows/Fonts` (Arial) through a project-local Fontconfig
cache. The exact font files, font licenses, embedding/subsetting behavior, and
whether a final PDF embeds or references them are not yet recorded. Phase 5
must choose a documented redistributable font set or prove that system fonts are
not shipped, retain the applicable notices, and verify offline PDF output.

### Local Matplotlib font candidate

The current `.venv` Matplotlib installation contains DejaVu Sans/Serif TTFs
(font name table version 2.35) at
`.venv/Lib/site-packages/matplotlib/mpl-data/fonts/ttf/`, including
`DejaVuSans.ttf`, `DejaVuSans-Bold.ttf`, `DejaVuSerif.ttf`, and their italic,
bold, display, and mono variants. The exact local notice is
`.venv/Lib/site-packages/matplotlib/mpl-data/fonts/ttf/LICENSE_DEJAVU`.
It grants reproduction and distribution with the Bitstream/Arev notices and
requires renamed modified fonts to avoid the reserved names; DejaVu changes are
identified there as public domain. This is stronger local evidence than the
unverified Windows Arial path used by the smoke probe.

Recommendation for the future HTML/PDF implementation: evaluate DejaVu Sans
as the single bundled font family for charts and report text, with the complete
`LICENSE_DEJAVU` notice retained if font files are shipped. This is a candidate
recommendation only: no font files were copied into the repository, and Phase 5
still must verify Spanish glyph coverage, PDF embedding/subsetting, visual
fidelity, and the final asset manifest before adoption.

## Current v1.0.0 source and asset conditions

The v1.0.0 project is building a real ENOE publication. All eight official
snapshots (2024-Q3 through 2026-Q2) are catalogued with
`acquisition_approved: true`, exact URLs, expected SHA-256 values, and local
acquisition receipts. `brujula/acquisition.py` authorizes and verifies the raw
ZIP acquisition only; it does not authorize estimates or publication.
`data/catalog/enoe-snapshots.json` explicitly sets `publication_approved: false`.
Design-based estimation, precision/suppression, aggregate projection, and the
public release gate remain pending. Any local ENOE microdata or person-level
frames remain ignored research inputs and are never public assets.

INEGI's published terms permit copying, extraction, adaptation, and publication
when attribution, metadata, update date, transformation notice, and
no-endorsement statement are retained. A v1.0.0 public release still requires
the exact accepted snapshots, validated aggregates, SHA-256 receipts,
dictionary/parameters, and attribution from [`SOURCES.md`](../SOURCES.md).

OLA/STPS is benchmark-only: the audit found informational conditions but no
explicit redistribution license. Data México has an ambiguous license scope
across integrated datasets, and IMCO states all rights reserved. Their figures
must not enter a public bundle without source-specific permission and evidence.
The source catalog and terms evidence are [`SOURCES.md`](../SOURCES.md) and
[`source-research.json`](../source-research.json).

## Phase 5 unknowns / required evidence

- Repeat metadata capture from the exact clean-install target and preserve the
  full PDF transitive closure if PDF tooling is shipped.
- Preserve complete notices for all 23 current packages if an environment or
  binary distribution is ever published; the source wheel currently does not
  redistribute them.
- Decide and document the WeasyPrint 70.0 delivery form, native Pango source,
  and all transitive notices before shipping PDF tooling.
- Identify the exact final PDF fonts and their redistribution/embedding terms;
  the local Arial smoke proof is insufficient for that decision.
- Recheck current INEGI, OLA, Data México, and IMCO terms at the point of any
  real-data or third-party-asset publication. Historical metadata and a green
  local render do not establish current redistribution permission.
- Keep raw ZIPs, person-level data, software caches, DLLs, and temporary smoke
  outputs outside the public release manifest; release review must verify that
  boundary directly.
