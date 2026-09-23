---
last_mapped_commit: 20b935e
last_mapped_at: 2026-09-22
---
# Codebase Concerns

**Analysis Date:** 2026-09-22

Scope: current checkout and the real-data release required by `docs/FINAL-RELEASE-PLAN.md`. This map uses code, tests and existing local research; it does not rerun the full suite, download sources or inspect individual microdata records. No project-local `.codex/skills/` or `.agents/skills/` directory is present.

## Tech Debt

**Official-data contract stops at the synthetic release boundary — high:**

- Issue: `validate_dataset()` unconditionally fails `official_snapshot` with `source_activation`; acquisition approval does not supply the missing numerical-publication contract.
- Files: `brujula/quality.py`, `contracts/dataset.schema.json`, `docs/CONTRACT.md`, `data/catalog/enoe-snapshots.json`, `docs/decisions/0006-real-research-scope-and-acquisition.md`.
- Impact: a downloaded, statistically reviewed ENOE dataset cannot pass the current publication pipeline.
- Fix approach: implement versioned source activation and contract migration together with the reviewed adapter. Retain fail-closed behavior until numerical acceptance passes; do not remove the gate merely because acquisition is approved.

**Precision metadata cannot survive the complete output path — high:**

- Issue: `SurveyDesign` produces SE, intervals, design degrees of freedom, denominator and suppression reasons; the observation schema, warehouse columns and export field list only support sample size, CV and a prose precision note.
- Files: `brujula/survey.py`, `contracts/dataset.schema.json`, `brujula/warehouse.py`, `brujula/export.py`, `docs/research/ENOE-METHOD-REVIEW.md`.
- Impact: the final release cannot preserve machine-readable uncertainty and suppression provenance across JSON, DuckDB, CSV and Parquet.
- Fix approach: extend schema, validation, warehouse, exports and renderer as one versioned interface change; test null and suppressed values across every format.

**Documentation gives different completion and authority boundaries — medium:**

- Issue: the completed synthetic scope in `docs/STATUS.md` and inactive ENOE extension in `docs/CONTRACT.md` need reconciliation with acquisition approval and the real final-release requirement.
- Files: `docs/STATUS.md`, `docs/CONTRACT.md`, `docs/FINAL-RELEASE-PLAN.md`, `docs/decisions/0006-real-research-scope-and-acquisition.md`.
- Impact: readers can mistake synthetic acceptance for completion of the requested research, or acquisition permission for numerical-publication permission.
- Fix approach: make the active release target and separate acquisition, estimation and publication gates explicit; retain evidence labels for the synthetic release.

## Known Bugs

**Acquisition request advertises an incompatible ZIP media type — high:**

- Symptoms: the integrator's official-host probe reports HTTP 406 with `Accept: application/zip`; the same approved URL accepts `*/*` and serves `application/x-zip-compressed`.
- Files: `brujula/acquisition.py` (`_download`), `tests/test_acquisition.py`, `data/catalog/enoe-snapshots.json`.
- Trigger: downloading a catalogued package through the request header currently set by `_download()`.
- Workaround: update content negotiation and verify it through an injected transport regression test while retaining ZIP-content, size and redirect checks. The mapper verified the header in code; the live response is integrator-provided evidence.

**Acquisition preflight failures bypass attempt receipts — medium:**

- Symptoms: `_read_registry()`, `_snapshot()` and limit conversion run before the guarded attempt; malformed, revoked or unknown registry input raises without sealing a failed receipt or invalidating an existing per-snapshot pointer.
- Files: `brujula/acquisition.py` (`acquire_snapshot`), `tests/test_acquisition.py`, `docs/CONTRACT.md`.
- Trigger: an acquisition invocation fails registry validation before entering `BuildLock` and the receipt-producing exception handler.
- Workaround: put refresh-level preflight under an attempt journal that can record a safe requested identifier and failed publication state. Test failure after a successful refresh; do not mutate the pointer of a different active lock owner.

## Security Considerations

**Raw survey data must remain outside the editorial release:**

- Risk: acquisition makes real records available locally, while the authorized deliverable contains aggregate outputs only.
- Files: `AGENTS.md`, `docs/decisions/0006-real-research-scope-and-acquisition.md`, `data/catalog/enoe-snapshots.json`, `.gitignore`, `brujula/acquisition.py`.
- Current mitigation: approved host and HTTPS checks, redirect checks, bounded downloads, ZIP path/symlink checks, content hashes, ignored `.cache/` and `artifacts/`, and `publication_approved: false`.
- Recommendations: use an explicit aggregate-asset allowlist and privacy/license review when assembling the final release; ignoring raw files in Git does not validate manually packaged assets. No additional confirmed security vulnerability is asserted by this map.

## Performance Bottlenecks

**ZIP download and verification materialize full archives in memory:**

- Problem: `_download()` accumulates chunks then joins them; cached ZIP verification uses `read_bytes()` and `BytesIO`.
- Files: `brujula/acquisition.py`, `data/catalog/enoe-snapshots.json`.
- Cause: validation and immutable writing accept complete byte strings. Peak memory includes multiple copies of a compressed archive; no measured slowdown is established.
- Improvement path: if measured memory pressure warrants it, stream into a bounded temporary file while hashing, then validate and atomically publish the content-addressed archive. Preserve the same receipt and corruption checks.

## Fragile Areas

**Singleton-stratum policy and independent statistical acceptance — high:**

- Files: `brujula/survey.py`, `tests/test_survey.py`, `docs/research/ENOE-METHOD-REVIEW.md`, `.cache/research/oracle-adjust.R`, `.cache/research/r-survey-oracle.json`.
- Why fragile: `SurveyDesign` rejects any true singleton stratum. The integrator reports 13 in the full responding/resident 2026Q2 design and records the aggregate diagnostic in `.cache/research/design-probe.json`; this mapper did not repeat the record-level calculation. Domain singletons and true design singletons require different handling.
- Safe modification: preserve the complete design before domain masks, default to rejection, and introduce any reviewed singleton option with an explicit method identifier and provenance. Do not silently drop strata, treat them as certainty PSUs or filter the design to one education field.
- Test coverage: the documented 24 isolated survey tests cover arithmetic, support, boundaries and metamorphic checks. The local R 4.6.1 / `survey` 4.5 oracle succeeds for four quantities using `survey.lonely.psu='adjust'`; Python agreement and acceptance of that policy are not established by the oracle output alone. R is an optional local validation tool.

**Period-specific schema, universe and classification mapping — high:**

- Files: `docs/research/ENOE-METHOD-REVIEW.md`, `data/catalog/enoe-snapshots.json`, `brujula/quality.py`.
- Why fragile: geographic field names change from 2025Q3; CMPE storage can omit leading zeros; unknown age and income codes are not ordinary numbers. The method review corroborates 2026Q2 metadata without proving equivalence across all eight periods.
- Safe modification: validate each snapshot's members, header, dictionary and classification crosswalk before aggregation; keep missingness, confirmed zero and out-of-universe states distinct. Compare only matched universe/method/source/price/concept signatures.
- Test coverage: adapter fixtures for these real-package variations and official benchmark reconciliation are still required by `docs/FINAL-RELEASE-PLAN.md`.

## Scaling Limits

**Bounded acquisition and in-memory survey design:**

- Current capacity: `data/catalog/enoe-snapshots.json` permits 100,000,000 compressed bytes and 1,500,000,000 declared expanded bytes per package; it enumerates eight quarterly snapshots.
- Limit: `brujula/acquisition.py` rejects packages over those limits, and `brujula/survey.py` builds arrays for the complete design. No end-to-end memory or throughput ceiling is measured.
- Scaling path: process each quarter independently and retain full-design domain semantics. Profile before increasing limits or parallelizing downloads; quarterly samples overlap and must not be pooled as independent people (`docs/FINAL-RELEASE-PLAN.md`).

## Dependencies at Risk

**NumPy is directly imported but declared only transitively in project metadata:**

- Risk: `brujula/survey.py` imports NumPy, while `pyproject.toml` declares DuckDB, jsonschema and Matplotlib only. `requirements.txt` pins NumPy, and Matplotlib currently supplies it transitively.
- Impact: the wheel's dependency contract does not explicitly describe the statistical module's runtime requirement; installation behavior depends on another library's dependency graph.
- Migration plan: declare the compatible NumPy version directly in `pyproject.toml`, reconcile `requirements.txt`, and check the wheel outside the checkout. This is dependency declaration debt, not a claim of a known vulnerability.

## Missing Critical Features

**Integrated ENOE refresh, adapter and offline replay:**

- Problem: acquisition and statistical modules exist, but `brujula/cli.py` exposes build/demo/report/scout/verify without an ENOE refresh command; `brujula/pipeline.py` consumes the dataset contract rather than assembling reviewed ENOE snapshots.
- Files: `brujula/cli.py`, `brujula/pipeline.py`, `brujula/acquisition.py`, `brujula/survey.py`, `docs/FINAL-RELEASE-PLAN.md`.
- Blocks: the required eight-period real research release, official benchmarks, and one reproducible refresh/replay workflow.

**Real-data editorial report and printable distribution:**

- Problem: `render_report()` inserts `SYNTHETIC_WARNING` in every successful report, observation table and figure regardless of dataset mode; its return contract supplies Markdown/HTML/charts without PDF.
- Files: `brujula/report.py`, `tests/test_report.py`, `docs/research/PRODUCT-GAP-AUDIT.md`, `docs/FINAL-RELEASE-PLAN.md`.
- Blocks: accurate real-data labeling, the required contextual and field profiles, explicit uncertainty displays, and the final printable research package. Preserve the synthetic path while adding reviewed official-data presentation.

## Test Coverage Gaps

**Actual acquisition transport behavior — high:**

- What's not tested: most acquisition tests replace `_download()` itself; redirect and HTML cases inject its exception rather than exercising the opener, response headers, body limits and media negotiation.
- Files: `tests/test_acquisition.py`, `brujula/acquisition.py`.
- Risk: orchestration tests pass while approved-host downloads fail, as the `Accept` mismatch demonstrates.
- Priority: high; inject a fake opener/response below `_download()` and cover successful alternate ZIP content type, hostile redirect, HTML body, size limits and transport failure.

**Real statistical and publication acceptance — high:**

- What's not tested: cross-period adapter equivalence, reviewed singleton handling against R, official estimate/precision benchmarks, and end-to-end preservation of structured precision and suppressed nulls.
- Files: `tests/test_survey.py`, `tests/test_pipeline.py`, `tests/test_export.py`, `tests/test_report.py`, `docs/research/ENOE-METHOD-REVIEW.md`, `docs/FINAL-RELEASE-PLAN.md`.
- Risk: local software success can be mistaken for valid real labor findings. The synthetic release's passing checks do not establish these real-data gates.
- Priority: high; retain small deterministic fixtures, add independent oracle comparisons and explicit benchmark receipts, then review the aggregate report and clean replay before release.

---

*Concerns audit: 2026-09-22*
