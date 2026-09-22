# Brújula Laboral MX

**Reproducible research for understanding Mexico's labor market.** A local-first
Analytics repository combining source research, evidence-aware pipelines and
analytical reports. [Español](README.md) · [Documentation](docs/README.md)

> **Current status: accepted planning baseline, with a partial prototype.**
> The full demo is not release-ready. All included observations are synthetic,
> not Mexican labor estimates, vacancies or personal career recommendations.
> See [verified status and blockers](docs/STATUS.md).

## Intended outcome

Trace analytical results through source permissions, immutable captures,
explicit concepts, quality checks and comparable observations. Produce DuckDB
tables, CSV/Parquet/JSON, SVG/PNG figures, static Markdown/HTML reports and
briefs separating observation, interpretation and recommendation. This phase
does not build a frontend, application backend or navigable website.

The pilot design covers three study fields (law, communication and journalism,
political science), three quarters (2025 Q2–Q4), national Mexico and an
illustrative Jalisco segment. Its three measures are employed population,
nominal mean monthly income and women's share of employment. The target is 54
synthetic observations; the prototype's actual coverage is recorded in STATUS.

An ENOE extension is future work, subject to verified redistribution conditions,
official field codes, population filters, weights and complex-survey precision.
No real source ingestion or automatic source activation is implied by inclusion
in the source catalog. LATAM requires separate country-level methodology review.

## Read the design

- [Charter](docs/PROJECT-CHARTER.md), [scope](docs/SCOPE.md) and [PRD](docs/PRD.md).
- [Specification](docs/SPEC.md), [contracts](docs/CONTRACT.md), [methodology](docs/METHODOLOGY.md) and [glossary](docs/GLOSSARY.md).
- [Architecture](docs/ARCHITECTURE.md), [decisions](docs/decisions/README.md) and [source audit](docs/SOURCES.md).
- [Implementation plan](docs/PLAN.md), [roadmap](docs/ROADMAP.md), [risks](docs/RISKS.md) and [validation plan](docs/VALIDATION-PLAN.md).
- [Adversarial planning review](docs/PLANNING-REVIEW.md) and [verified status](docs/STATUS.md).

The detailed design is maintained in Spanish. It distinguishes accepted design
decisions from implemented behavior and verified releases.

## Inspect the development checkpoint

With Git, Python 3.12 and `uv` available:

```sh
git clone https://github.com/erickinorganico/career-signals-mx.git
cd career-signals-mx
uv venv --python 3.12
uv pip install -r requirements.txt
.venv/bin/python scripts/check_docs.py
.venv/bin/python -m pytest tests/test_data.py tests/test_quality.py tests/test_scout.py -q
```

On Windows use `.venv/Scripts/python.exe`. Standard `venv` and `pip install -r
requirements.txt` are alternatives. These commands inspect documentation and
the tested subset, not a completed clean-install or end-to-end release.

The planned CLI entry points are `python -m brujula demo`, `python -m brujula
verify` and opt-in `python -m brujula scout`. **Demo/full verification remain
blocked by missing components.** The metadata scout cannot activate new numeric
sources or publish statistical claims.

## Evidence rules

Study field, occupation and vacancy are different concepts. Missing data remain
null. Synthetic data stay labeled and in REVIEW. Changes in source, population,
method, unit, geography or price basis can block comparisons. Nominal income is
not purchasing power; descriptive changes do not identify causes.

Failed refreshes must invalidate the current release while preserving historical
runs. This is a specified invariant, not a claim that the incomplete E2E already
passes. Current agent code uses deterministic replay; no autonomous LLM service
or paid inference is required or claimed.

See [contributing](CONTRIBUTING.md), [model orchestration](docs/ORCHESTRATION.md)
and [local efficiency assessment](PROJECT-EFFICIENCY.md). Original code,
documentation and fixtures use the [MIT license](LICENSE); external sources
retain their own terms; see [third-party notices](THIRD_PARTY_NOTICES.md).
No restricted datasets, credentials or unrelated
proprietary material are included.
