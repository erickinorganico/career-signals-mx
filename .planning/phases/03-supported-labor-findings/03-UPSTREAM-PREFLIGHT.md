# Phase 3 upstream interface readback

Status: preparatory readback; Phase 2 final review, post-fix numerical replay and goal verification are required before execution.

The frozen pre-core-review aggregate output has 6,739 records: six quarters with 115, 2025-Q2 with 138, and 2026-Q2 with 5,911. The two extra 23-metric national-context Baja California domains support the official/R benchmarks; they are not additional professional-cohort slices and must not be mistaken for incomplete research inventory.

- Every public payload is a complete strict `research-v2` root, with sources, populations, fields_of_study, occupations, industries, geographies, recorded_sexes, periods, metrics, methods, evidence and records. Records have the ten `GRAIN` dimensions and no preexisting record ID.
- The manifest `snapshots` maps exact snapshot IDs to `public_v2_path`, `public_v2_digest`, `numeric_digest`, aggregate audit `path`, requested_count and elapsed_seconds. It binds code hashes and metric manifest SHA separately. Re-read the final accepted manifest because review hardening may add metadata.
- Each aggregate ledger has requested_cells and evaluated_cells keyed by the pipe-joined ten-field grain. An evaluation carries status, has_estimate, reason, coverage, exclusions, dictionary_binding, metric_version, method_version and synthetic. Population coverage is keyed separately by population, field, geography and recorded sex.
- Latest-quarter payload contains 118 actually observed, verified named professional fields plus all; 32 entities plus national; sex 1 and 2 plus all. Field coverage is not all 185 possible official catalog entries. Research requirements request all identifiable observed fields, and sparse state/sex cells remain explicit.
- The latest record states at this checkpoint are 3,175 REVIEW and 2,736 UNKNOWN. REVIEW does not necessarily mean a visible number: precision suppression must follow null value and its reason, not status alone.
- Population coverage separates exclusions from observed_category_counts. Counts are nonexclusive and must not be summed as unique excluded people. Unweighted observed coverage is distinct from weighted estimates.
- Method IDs recur across quarters while each method catalog entry binds that quarter's source_snapshot_ids. Keep per-snapshot catalog context when validating or merging; differing source-reference lists are not competing numerical method definitions.

The final Phase 2 result and 02-VERIFICATION.md must replace this preliminary evidence at the Phase 3 execution preflight. No ANA requirement is accepted by this document.
