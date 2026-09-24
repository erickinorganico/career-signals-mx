---
phase: 04-offline-publication-and-reproducible-operation
plan: 06
subsystem: integrated-publication-acceptance
tags: [edge-controls, disclosure, installed-wheel, native-pdf, hosted-ci]
requires:
  - phase: 04-05
    provides: sealed real publication, installed CLI and fail-closed current
provides:
  - exact 45-criterion integrated behavioral mapping
  - four executable publication prohibition controls with bad-red and clean-green proof
  - public-safe acceptance receipt for real publication and clean Windows/Ubuntu installed fixtures
affects: [phase-04-verification, phase-05-release]
key-files:
  created:
    - tests/test_phase4_edge_acceptance.py
    - tests/phase4_prohibitions.py
    - tests/phase4_prohibitions.test.cjs
    - scripts/check_installed_runtime.py
    - docs/evidence/phase-04-publication-acceptance.json
  modified:
    - .github/workflows/verify.yml
    - requirements-pdf.txt
requirements-completed: [PUB-01, PUB-02, PUB-03, PUB-04, PUB-05, OPS-01, OPS-02, OPS-03]
completed: 2026-09-24
---

# Phase 04 Plan 06: Integrated Publication Acceptance

**The real offline publication passed the integrated local controls and the clean installed-wheel fixture/PDF lane on hosted Windows and Ubuntu.** This plan's evidence does not grant Phase 5 release acceptance or change the public statistical `REVIEW` precision designation.

## Executed evidence

- The installed `c222f69` publication run `20260924T010247-81cfb71ea5f1` sealed 73 content artifacts under manifest SHA-256 `38c3dfc21d816f32d7e4a21d7efd89418fc198fd80e94577783706f00d7fb023`: 22 public tables, nine figure groups and a 97-page PDF. Its fresh analysis/build/open, interrupted-run recovery, live-source failure and unchanged historical anchors are recorded in `04-INTEGRATED-OPERATION.md` and `04-WAVE3-CHECKS.md`.
- Local full verification passed 592 Python tests with one duplicate-ZIP warning. The exact 45 edge criteria mapped to 46 passing tests; all 30 Node controls passed. Four GSD prohibition producers located the suppressed-value, complement, PDF-fetch and stale-current controls and observed deliberate bad output fail before clean output passed. The same suppressed-record canary was checked through emitted text, figure metadata and typed exports. The local and real permutation limits are specified in `04-VALIDATION.md` and the public-safe acceptance receipt.
- Hosted run [36050222714](https://github.com/erickinorganico/career-signals-mx/actions/runs/36050222714) on commit `3b8b2d4e603d69f9d94f5ac45f6446156a17d14f` completed successfully on Windows and Ubuntu. Each host built the current wheel, installed it outside checkout, passed the repository verification and Node controls, then ran the installed helper. Both downloaded helper receipts report `PASS`, 33 installed code modules, 24 authored resources, 63 wheel members, altered-font rejection, local URL rejection, and a searchable Spanish PDF with embedded DejaVu. The Ubuntu and Windows receipt SHA-256 values are `06296f3691aabb2be7b6bf421442f59d10f94862f1873fcd0f747f4e1a0c3f0d` and `a5e39dd08df523d0fd863a1a3dc8f87ff6d98d70908e396bc10eb7e54fe93d3c`, respectively. Both report installed code/resource digest `263b9900eb45604f9b3a10ef949cf6512eb6478c222c70cd2c402853afffe065`.
- The preceding hosted runs failed only at the Windows native asset layout check: the SHA-verified archive expands into `onedir/weasyprint/_internal`. Commit `3b8b2d4` corrected that lookup; the next run passed both hosts. No numerical or report implementation changed in this fix.

## Scope and decisions

The accepted full real eight-quarter R/official numerical acceptance and offline reconstruction replay were run in the designated research environment. This plan reused them only under the unchanged numerical code, resources, input, benchmark and method identities documented in `04-WAVE3-CHECKS.md` and `04-INTEGRATED-OPERATION.md`. Hosted fixture/PDF checks establish package portability; they do not assert a second real numerical experiment on each host. The fresh installed real analysis/build/open and actual visual inspection provide the separately required publication proof.

The reviewed local wheel and sealed bundle had no identified raw ZIP, person-row export, credential or workstation-path marker; `04-SECURITY.md` and the acceptance receipt retain the bounded local audit. Final license, attribution, secret/microdata and exact release-asset approval belong to Phase 5. An independent Phase 4 verifier must read this summary and the completed hosted receipt before Phase 4 is marked accepted in the roadmap.
