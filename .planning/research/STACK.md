# Stack Research

**Domain:** Reproducible ENOE survey research and offline editorial publication for Mexico
**Researched:** 2026-09-22
**Confidence:** HIGH for the retained stack; MEDIUM for the proposed PDF converter pending a clean Windows/Linux render

## Recommended Stack

### Core Technologies

| Technology | Version | Purpose | Why Recommended |
|------------|---------|---------|-----------------|
| CPython | 3.12 baseline (`>=3.12` project range) | Local CLI, acquisition, survey estimates and publication | Already runs the code and CI; retain one implementation language. |
| NumPy | 2.5.3, **declare directly** | Vectorized weighted arrays and design-based variance | `brujula/survey.py` imports it; the current exact requirements pin is only transitive through Matplotlib. A direct project dependency makes clean installs honest. |
| DuckDB | 1.4.4 | Validated aggregate tables, SQL checks and Parquet export | Existing embedded warehouse and export code already use it; DuckDB documents direct Parquet `COPY`. |
| jsonschema | 4.26.0 | Versioned source, estimate, receipt and report contracts | Existing Draft 2020-12 validation is the release gate for traceable numbers. Extend the contracts to v2 before integrating ENOE. |
| Matplotlib | 3.10.8 | Offline SVG and PNG charts | Existing renderer and noninteractive backend; official documentation supports both hardcopy formats. |
| WeasyPrint | 70.0 **proposed** | Render the canonical offline HTML report as PDF | One HTML content path for web/print, with CSS paged media and SVG figures. Requires a proved Pango installation on Windows and CI before pinning in the release environment. |

### Supporting Libraries and Tools

| Library or tool | Version | Purpose | When to Use |
|-----------------|---------|---------|-------------|
| pytest | 9.0.3 | Statistical, contract, pipeline and publication regression checks | Existing test extra; add official-snapshot acceptance cases and PDF smoke checks. |
| R + `survey` | Host observed R 4.6.1, `survey` 4.5 | Independent design-based totals/ratios/SE oracle | Validation fixture or isolated comparison run only; no Python runtime or reader installation dependency. Pin options, input hash and version in comparison receipts. |
| Python standard library | Python 3.12 | `argparse`, `csv`, `hashlib`, `zipfile`, `urllib`, file locking and receipts | Keep approved-source acquisition and content-addressed raw artifacts local; no new download framework is needed. |
| `uv` or `pip` | Existing documented installer | Recreate the Python environment | Keep `pyproject.toml` direct requirements and exact `requirements.txt` closure synchronized. Rebuild from a clean environment in CI. |

### Development and Release Gates

| Gate | Build impact |
|------|--------------|
| Source snapshots | Catalog each of eight official quarters with URL, terms, ZIP members, SHA-256, dictionary and schema signature; only approved snapshots enter estimation. |
| Survey oracle | Compare Python with R `survey` on full-design domains, then reconcile point estimates and precision against matching INEGI tabulations. A point-total match alone does not validate SE/CV. |
| Static artifact gate | Generate Markdown, HTML, PDF, SVG/PNG, CSV, Parquet and DuckDB from the same validated estimates. Verify PDF pages/text, offline resource resolution, figure/table correspondence and visible suppression. |
| Reproduction | Run install, refresh/replay, tests and document checks on Python 3.12 Ubuntu and Windows. Failure must leave a receipt and invalidate `current`; no prior report may appear fresh. |

## Installation and Compatibility

Current product dependencies are pinned in `pyproject.toml`; `requirements.txt` pins their resolved closure. Add `numpy==2.5.3` to direct dependencies, retaining its existing exact requirements pin. Once a PDF proof passes, add a **pin for WeasyPrint 70.0 and its resolved closure**, plus documented Pango setup to CI/clean-install instructions. WeasyPrint 70 requires Python >=3.10 and Pango >=1.44; the present Python baseline is compatible, but the native Pango dependency is a real Windows setup gate. Use its local-file input and restrict external resource fetching so PDF generation remains offline.

Do not treat the ignored `.cache/R-4.6.1` and `.cache/R-library/survey` copies as portable installation artifacts. The shipped Python package should run without R; the independent numerical audit records the R environment separately. Do not add a web service, frontend, cloud database, paid API or external inference service for this milestone.

## Alternatives Considered

| Recommended | Alternative | When the alternative makes sense |
|-------------|-------------|----------------------------------|
| Existing Python estimator, cross-checked with R | Replace it with R `survey` as the product engine | Only if the Python variance method cannot be validated; this would change the release contract and install story. |
| WeasyPrint from canonical HTML | Matplotlib `PdfPages` | For chart-only appendices. A long editorial report with tables, references and print typography would need a second layout path. |
| DuckDB SQL and Parquet | Pandas/Arrow data-frame layer | Only if a demonstrated transform cannot be expressed clearly in existing Python/SQL; avoid an extra large dependency for routine exports. |
| Exact requirements pins | New package manager/lock migration | Reconsider only if clean-install drift is observed; first align direct declarations, closure and CI. |

## What Not to Add

| Avoid | Reason | Use instead |
|-------|--------|-------------|
| `renoe` or `joinENOE` as release dependencies | Domain code and licensing need separate review; the current acquisition and join contracts already need source-specific evidence. | Own allowlisted ENOE adapter with tested keys, cardinality and catalog. |
| `samplics`/`svy` as a shortcut to publishable precision | A library does not certify ENOE coding, singleton handling or official comparability. | Existing estimator + independent R and INEGI checks. |
| Browser app/BI dashboard | Project release is a static research publication. | Offline HTML/PDF and reusable aggregate tables. |
| Synthetic fallback after real-data failure | Would misrepresent the final release. | BLOCKED receipt and invalidated current pointer. |

## Sources and Confidence

- **HIGH, repository evidence:** `pyproject.toml`, `requirements.txt`, `.planning/codebase/STACK.md`, `docs/FINAL-RELEASE-PLAN.md`, `docs/research/ENOE-METHOD-REVIEW.md`, `docs/CONTRACT.md` (observed 2026-09-22).
- **HIGH, official:** [DuckDB Parquet export](https://duckdb.org/docs/stable/data/parquet/overview), [Matplotlib static backends](https://matplotlib.org/stable/users/explain/figure/backends.html), [R survey design](https://r-survey.r-forge.r-project.org/survey/html/svydesign.html).
- **HIGH for capability, MEDIUM for local suitability:** [WeasyPrint 70 API](https://doc.courtbouillon.org/weasyprint/stable/api_reference.html) and [installation requirements](https://doc.courtbouillon.org/weasyprint/latest/first_steps.html). Native dependency and Spanish report rendering still need a release proof.
- **MEDIUM, comparative design evidence:** `docs/research/COMPARABLE-REPOSITORIES.md`; useful patterns, not a license to copy code or activate ENOE.

---
*Stack research for Brújula Laboral MX v1.0.0.*
