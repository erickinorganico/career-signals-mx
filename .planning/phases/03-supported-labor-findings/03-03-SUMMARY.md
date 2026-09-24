---
phase: 03-supported-labor-findings
plan: 03
subsystem: public-aggregate-findings
tags: [enoe, typed-claims, public-v2, evidence, offline-research]
requires:
  - phase: 03-supported-labor-findings
    plan: 01
    provides: accepted eight-quarter public index, complete profiles and sanitized record_index
  - phase: 03-supported-labor-findings
    plan: 02
    provides: reviewed definition registry and fail-closed descriptive comparison ledger
provides:
  - deterministic Spanish claim construction and exact text/evidence regeneration
  - independently pinned public-only analytical packet for Phase 4
  - executable claim, advice and activation prohibition controls
affects: [04-offline-publication-and-reproducible-operation]
tech-stack:
  added: []
  patterns: [safe display metadata on sanitized records, hash-only accepted reference, canonical claim regeneration, exact derived packet validation]
key-files:
  created:
    - brujula/claims_v2.py
    - brujula/findings_v2.py
    - contracts/analysis-v2.schema.json
    - data/fixtures/enoe-analysis-reference.json
    - tests/test_claims_v2.py
    - tests/test_analysis_integration.py
    - tests/phase3_prohibitions_03.py
    - tests/phase3_prohibitions_03.test.cjs
    - tests/fixtures/phase3_prohibitions/03.clean.json
    - tests/fixtures/phase3_prohibitions/03-p5.bad.json
    - tests/fixtures/phase3_prohibitions/03-p6.bad.json
    - tests/fixtures/phase3_prohibitions/03-p7.bad.json
  modified: []
key-decisions:
  - "Derive safe field labels from accepted per-snapshot catalogs and geography names from the reviewed registry; attach them only to sanitized record_index items."
  - "Pin source_manifest, enriched sanitized record_index, profiles and coverage independently; a caller-recomputed packet digest never establishes acceptance."
  - "Recompute comparison, claim, opening and limitation outputs during standalone validation instead of trusting caller-supplied publication text."
  - "Select opening findings by fixed measure relevance and observed support, never by the highest estimated outcome."
patterns-established:
  - "Canonical claim text is regenerated from exact record/comparison IDs and compared in full, including Spanish accents, units and qualifiers."
  - "Public analytical packet carries no raw person rows or private estimates; suppressed parent records remain null in the common downstream index."
requirements-completed: [ANA-01, ANA-02, ANA-03, ANA-04, ANA-05, ANA-06]
coverage:
  - id: typed-claims
    description: Exact observation and descriptive-comparison claims bind labels, amounts, unit, universe, method, evidence and limitations
    requirement: ANA-06
    verification:
      - kind: unit
        ref: tests/test_claims_v2.py
        status: pass
    human_judgment: false
  - id: accepted-packet
    description: Strict public-only packet contains all accepted eight-quarter records, profile slots, comparison slots and supported findings
    requirement: ANA-01
    verification:
      - kind: integration
        ref: tests/test_analysis_integration.py#test_real_accepted_aggregate_packet
        status: pass
    human_judgment: false
  - id: independent-pins
    description: Standalone validator rejects coherent source, record, label, coverage, comparison, claim, opening and limitation repinning
    requirement: ANA-06
    verification:
      - kind: unit
        ref: tests/test_analysis_integration.py#test_coherently_rehashed_packet_tampering_fails
        status: pass
    human_judgment: false
  - id: prohibitions
    description: Causal profession substitution, unsupported numbers/advice and source or suppressed-value activation fail current-output controls
    requirement: ANA-06
    verification:
      - kind: integration
        ref: tests/phase3_prohibitions_03.test.cjs
        status: pass
    human_judgment: false
duration: 48min
completed: 2026-09-23
status: complete
---

# Phase 3 Plan 03: Evidence-Bound Findings Summary

**The accepted ENOE aggregates now produce one pinned analytical packet with exact Spanish claims and three supported opening findings.**

## Performance

- **Duration:** approximately 48 minutes, including accepted-real packet validation and full regression.
- **Completed:** 2026-09-23.
- **Tasks:** 3/3.
- **Files created:** 12 implementation, schema, fixture and control files.

## Accomplishments

- The accepted aggregate-only run produced **6,739** sanitized records, **6,762** profile appearances (920 national, 2,714 latest named field, 2,944 state and 184 recorded-sex), **4,209** descriptive comparison slots, **38** exact typed claims and **three** supported opening findings. Opening themes are exact-income coverage, employment rate and positive-known nominal income; their field IDs are distinct. There is no outcome-value ranking.
- Claims regenerate an exact Spanish title, observation, interpretation and limitation from stable `v2r:` or passing `v2c:` IDs. They bind source snapshot IDs and SHA-256 hashes, evidence refs, method IDs/versions, population, metric, typed amounts and precision status. A suppressed or incompatible endpoint, changed label/unit/number, causal effect, personal advice, invented significance or altered Unicode fails validation.
- The packet contains only sanitized public-v2 records. The hash-only `enoe-analysis-reference.json` independently binds source acceptance, sanitized/enriched records, profiles and coverage to the accepted real Phase 2 aggregate inputs. Standalone validation checks those pins, a strict schema, exact profile references, regenerated comparisons/claims/openings/limitations and a deterministic content digest. It does not treat a caller-recomputed digest as trusted provenance.
- The final accepted artifact and compact receipt are in `.cache/research/phase3-analysis/analysis.json` and `receipt.json`. Their shared content digest is `d2f28f26f993d052fb5f246db3262ad00b776081a663d608e0427962745a0c79`. The cache is local diagnostic output for Phase 4, not a promoted current publication.

## Validation Results

- Final full Python suite: **435 passed**, one existing duplicate-ZIP-member warning in `tests/test_acquisition.py`, in **143.91 seconds**. This includes the accepted eight-snapshot aggregate-only integration. No ENOE ZIP decoding, R computation or survey estimation was rerun.
- Focused synthetic claim/packet controls: **20 passed**, with the accepted-real test excluded in that focused run. Successful qoq, yoy, recorded-sex and entity claim kinds; 0–3 opening boundary; label, amount, method/source/unit and Unicode changes; coherent packet repinning; cyclic/nonfinite JSON; complementary parent redaction are covered.
- Node claim prohibitions: **3 passed** on the clean fixture. Each bad fixture made only its matching named test red. Canonical GSD proof files `p5-proof.json`, `p6-proof.json` and `p7-proof.json` under `.cache/research/phase3-final-controls/` report `status=green`, `located=true`, `failFirst=true`, `passed=true` and `flagged=false`. The p7 control also checks source-only and restored-suppressed-claim-only mutations independently through `validate_analysis_packet`.
- The earlier four Phase 3 prohibition proofs are in the same cache directory and remained green after the unchanged Plan 01/02 controls. The parent phase gate owns the final seven-descriptor rollup.

## Task Commits

1. **Task 1 — typed claims:** `0e0e67c` RED and `3eabfc1` GREEN.
2. **Task 2 — pinned analytical packet:** `84bb024` RED and `d9f17e5` GREEN. `67fa85f` corrected the canonical age and metric wording after output readback and refreshed the trusted record-index pin.
3. **Task 3 — executable prohibitions:** `7c3b999` RED, `f7ed896` GREEN and `35e22bb` strengthened independent p7 negative controls.

## Decisions Made

- Safe display metadata stays attached to each sanitized record item. The common index has no fake IDs, private roots or restored complementary parent values.
- The official field label comes from the accepted quarter catalog. Reviewed state names, metric meanings and population labels are controlled definitions; the professional age label explicitly states that EDA code 97 means 97 years or more.
- Temporal claim limitations mention possible rotating-sample overlap. Same-period sex/entity limitations describe a group difference and no change significance.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Corrected public claim grammar and age semantics**
- **Found during:** Accepted packet readback after Tasks 1 and 2.
- **Issue:** A generic feminine article produced incorrect income prose, and the initial age label could imply an upper bound of 97 rather than the EDA top code.
- **Fix:** Use a gender-neutral metric phrase and explicitly describe code 97 as 97 years or more; add direct income/plural and age semantic tests; refresh the trusted sanitized-index pin.
- **Files modified:** `brujula/claims_v2.py`, `tests/test_claims_v2.py`, `data/fixtures/enoe-analysis-reference.json`.
- **Commit:** `67fa85f`.

**2. [Rule 2 - Missing critical negative control] Tested source and suppressed-value promotion independently**
- **Found during:** Task 3 review.
- **Issue:** A combined p7 mutation could fail its first source assertion before proving the suppressed claim path.
- **Fix:** Independently mutate a source status and a redacted record plus claim, coherently recompute each caller digest, and require the strict packet validator to reject both.
- **Files modified:** `tests/phase3_prohibitions_03.py`.
- **Commit:** `35e22bb`.

## Known Stubs

None. Empty dictionaries/lists are input accumulation, no-finding output or negative-control expected results; no placeholder finding is released.

## Next Phase Readiness

Phase 4 can consume the validated analytical packet and its exact claim IDs. Publication/current promotion, report formatting and release audit remain Phase 4 work. The parent phase gate owns STATE.md, ROADMAP.md and final cross-plan verification.

## Final persisted handoff correction

Independent final review found that `metric_dictionary_refs` was emitted as a Python tuple, while persisted JSON reload produced a list. The packet validated in memory but the reloaded comparison ledger failed. RED `159cbcb` adds a synthetic save/load/validate regression and makes the real integration validate after JSON round trip. GREEN `a6696a1` emits a JSON-native list. Integration/comparison checks pass 41/41; root and independent reviewer both validate the original saved file successfully. Its file SHA-256 `9bbb5af3091c4cb02bec98d499ac522d77715f3a1316a30f906364fcc4c6537d` and content digest above are unchanged. No numerical recomputation, reference repinning or validation bypass was used.

## Self-Check: PASSED

All 12 created plan files, the cached accepted packet and its receipt exist. All eight task/fix commit hashes resolve to Git commits. The final full regression, real aggregate integration, clean/bad Node controls and three canonical p5–p7 proof files support the results above.
