# Phase 4 plan check — verification passed

**Phase:** Offline Publication and Reproducible Operation  
**Plans verified:** `04-01` through `04-06` (six plans, four waves)  
**Status:** PASS — 0 blockers, 1 nonblocking scope warning after the supplemental CI review. Initial bounded revision closed with 0 warnings; see the dated addendum.

The six plans now describe a path to the roadmap goal: one validated Phase 3 public projection feeds consistent offline reports, figures and exports; an installed eight-snapshot run can be replayed; sealed artifacts precede atomic current promotion; and every current read rechecks source acquisition and artifact integrity. This is pre-execution verification. Planned tests and real-data acceptance are not credited as passed.

| Roadmap requirement | Covering plans | Outcome planned |
|---|---|---|
| PUB-01 | 04-04, 04-06 | Full Spanish question-led editorial report and accepted claims |
| PUB-02 | 04-04–06 | Same-run offline HTML, Markdown and searchable printable PDF |
| PUB-03 | 04-04, 04-06 | SVG/PNG, semantic tables, mobile/zoom/print visual gate |
| PUB-04 | 04-03, 04-06 | Joined CSV, Parquet, DuckDB and data dictionary |
| PUB-05 | 04-03–06 | One sanitized projection; suppressed diagnostics and complement reconstruction blocked across outputs |
| OPS-01 | 04-01–02, 04-05–06 | Installed refresh, fresh numerical acceptance, offline replay and explicit CLI roots |
| OPS-02 | 04-05–06 | Exact receipt/manifest/artifact seal before current; failure receipt and immutable history |
| OPS-03 | 04-05–06 | Eight live acquisition currents plus complete artifact hashes verified on each open |

The 45 exact edge resolutions are represented in owning plan truths and the integrated 04-06 behavioral gate. Four structured prohibitions have current-output bad/clean controls. All tasks have concrete files, actions, automated verification and done criteria; 04-01/03, 04-02/04, 04-05 and 04-06 form an acyclic four-wave graph with separate same-wave file ownership. Plan sizes remain within the checker thresholds. The Nyquist strategy and `04-VALIDATION.md` exist; the local batch responsibility map, project rules, accepted Phase 3 handoff and deferred Phase 5 release are respected. No conflicting cross-plan data transformation or unaddressed research Open Question remains.

## Revision history and closure

1. **Installed numerical/analysis guard (earlier B1): closed.** `04-02` specifies a fixed inventory of executing package modules and packaged R oracle, package-owned paths and golden, CRLF-normalized hashes, historical-manifest and tamper negatives, fresh real eight-ZIP acceptance and unchanged replay. The final source/packet reference is rebound only from independent proof (`04-02-PLAN.md:66-67,101-103`).
2. **Offline font custody (earlier B2): closed.** `04-04` stages four audited DejaVu TTFs and complete notice at fixed relative paths for HTML/PDF and restricts PDF fetches to the staged allowlist; `04-05` hashes/verifies all five in the exact sealed inventory; `04-06` checks real assets, glyphs, embedding and failure controls on Windows and Ubuntu (`04-04-PLAN.md:68-71,96,102`; `04-05-PLAN.md:70-71,98,106`; `04-06-PLAN.md:152`).
3. **Packet rebind order (revision-2 blocker): closed.** Before rebind, the plan requires a positive installed `index_public_estimates` with `_check_codes` and independent golden active. A private test-only `_assemble` candidate must fail validation at exactly `trusted_reference`, and production `build_analysis_packet` must reject it. After unchanged numerical acceptance/replay, the plan deliberately rebinds the independent hash-only reference; only then must the installed production builder and persisted JSON validator pass (`04-02-PLAN.md:67,100-103,119-120`; `04-VALIDATION.md:27-29`). This matches the actual calls: `index_public_estimates` invokes `_check_codes` (`brujula/analysis_v2.py:168-190`); `build_analysis_packet` assembles then validates; `validate_analysis_packet` compares `_reference_from_packet` to `_load_reference` and emits `trusted_reference` on mismatch (`brujula/findings_v2.py:208-226,265-272`). No validator bypass is planned.

**Recommendation:** The revision gate can release these plans to `$gsd-execute-phase 4`. Execution must still produce the fresh installed numerical proof, real cross-format output, 45 edge results, four prohibition results and visual/current-failure evidence required by `04-VALIDATION.md`; any failed gate keeps Phase 4 blocked.

## Supplemental review — 04-06 installed-runtime CI addition

**Current scoped verdict:** 0 BLOCKER, 1 WARNING. The prior PASS on goal coverage and the closed B1/B2/rebind findings stands; this addendum reviews only the later 04-06 CI preparation. `04-CI-PREFLIGHT.md` identifies two concrete gaps in the current workflow: no installed outside-checkout PDF/resource lane and a Node glob that misses `phase4_prohibitions.test.cjs`. The revised 04-06 Task 2 owns `.github/workflows/verify.yml` and `scripts/check_installed_runtime.py`, requires current-wheel build/install from a separate directory on Windows and Ubuntu, explicit prohibition collection, reviewed native PDF prerequisites, actual installed import/resource/font/PDF checks and aggregate-only evidence (`04-06-PLAN.md:7-18,127,148,161-165`). It does not substitute fixture CI for designated-environment real eight-ZIP/R acceptance, or treat preflight registry/doc findings as successful runtime checks. The official onedir asset URL/SHA and Ubuntu Pango procedure are prepared in `04-CI-PREFLIGHT.md`; actual download/install/render and statuses remain execution gates. No new research source, hosted API, credential, paid service, or publication destination is introduced. Wave ordering and other plan ownership are unchanged.

**WARNING — scope_sanity (`04-06`):** Adding the workflow and helper raises `files_modified` from 9 to 11, above the checker's 10-file warning threshold. Five of the 11 paths are small negative/clean fixture JSON files and the plan still has two tasks, so this is a context-management warning, not a delivery blocker. Keep Task 2's CI/helper changes and runtime receipts narrowly scoped; if the executor cannot complete both platform lanes plus real acceptance within its context, split the CI lane into a dependent plan without dropping either platform or the Node control.

```yaml
issues:
  - plan: "04-06"
    task: 2
    dimension: scope_sanity
    severity: WARNING
    description: "The CI/helper addition raises files_modified to 11 paths, crossing the 10-file warning threshold."
    fix_hint: "Keep CI/helper work bounded; split into a dependent plan if execution context cannot cover both platform lanes and real acceptance."
```
