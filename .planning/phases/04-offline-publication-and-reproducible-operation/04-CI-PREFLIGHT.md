---
phase: 04-offline-publication-and-reproducible-operation
plan: 06
prepared: 2026-09-23
scope: read_only_ci_preflight
status: implementation_ready_pending_runtime_checks
files_reviewed:
  - .github/workflows/verify.yml
  - requirements.txt
  - pyproject.toml
  - .planning/phases/04-offline-publication-and-reproducible-operation/04-06-PLAN.md
  - .planning/phases/04-offline-publication-and-reproducible-operation/04-01-SUMMARY.md
  - .planning/phases/04-offline-publication-and-reproducible-operation/04-PACKAGING-READBACK.md
  - .planning/research/PDF-PROBE.md
  - .planning/phases/04-offline-publication-and-reproducible-operation/04-RESEARCH.md
findings:
  blockers: 0
  required_inputs: 0
  total: 0
---

# Plan 04-06 CI preflight

This is preparation for Plan 04-06, not a workflow change or acceptance result. No cross-platform PASS is claimed. The existing workflow already runs a two-OS Python 3.12 matrix and `python -m brujula verify`; the following gaps must be closed by the Plan 04-06 owner.

## Current workflow gaps

`.github/workflows/verify.yml:25-34` installs `requirements.txt`, runs the checkout-bound verification command, runs a Node glob, and builds the synthetic v1 demo. It does not build a wheel, install that wheel into an environment outside the checkout, prove package resource lookup from the installed import, or run the optional PDF capability check.

The Node command at line 30 is `node --test tests/phase*_prohibitions_*.test.cjs`. It matches the existing phase files with a suffix underscore, but it does not match the Plan 04-06 target `tests/phase4_prohibitions.test.cjs`. The minimal correction is an explicit list or the broader reviewed pattern `tests/phase*_prohibitions*.test.cjs`, followed by a readback of the collected file list so the new phase-4 test is demonstrably executed.

`requirements.txt` contains the base and test dependencies but not WeasyPrint. The reviewed declaration is the optional `pdf` extra in `pyproject.toml`: `weasyprint==70.0`. The CI job must install that extra in the PDF-capable environment and record the resolved version; it must not silently treat the base requirements install as PDF coverage.

## Minimal Plan 04-06 job proposal

Keep the existing `verify` matrix for checkout regression and add a bounded `installed-runtime` job on the same `ubuntu-latest` / `windows-latest` matrix. The job should:

1. Check out the pinned action revisions already used by `verify`, set up Python `3.12`, and install the project’s pinned base/test dependencies plus the reviewed `pdf` extra. Record `python --version`, `pip freeze` or an equivalent resolved-package receipt, and the WeasyPrint version.
2. Build a fresh project wheel from the checkout into a disposable staging directory. Compute and record its SHA-256; do not hard-code the historical Plan 04-01 wheel hash (`4c782b5d…7060ac7e`) as a current source identity after implementation changes.
3. Create a clean virtual environment in the runner temporary directory, outside the repository. Install the fresh project wheel and its approved dependencies there. Run the installed-resource test from an outside working directory, or an equivalent script with the installed site-packages as the only package import path, and record `brujula.__file__`, the current authored-resource digest count (22 at the 04-01 freeze; extended as new schemas are implemented), the missing-resource failure, and the exact font/oracle hashes. The current Plan 04-01 wheel evidence and hashes are the comparison baseline, not a new CI PASS.
4. Run a small offline Spanish PDF render through `resources.require_pdf_capability()` and the later restricted renderer when available. Assert WeasyPrint `70.0`, a `%PDF-` result, Spanish accent text, and explicit failure for missing dependency/native loader or missing/altered local asset. Keep output and receipts under the runner temporary directory; do not use checkout `.cache` as installed authority.
5. Run the current full checkout regression through `python -m brujula verify`, the explicit phase-4 Python edge test when present, and the corrected Node prohibition command. The phase-4 producer must prove clean output, targeted bad failure, and clean pass before evidence is recorded.
6. Upload only aggregate-safe receipts, test logs, wheel/resource inventory, and PDF capability evidence. Never upload source ZIPs, person rows, credentials, native caches, or local R/Pango installations.

The job should use the existing project interpreter consistently. If the wheel builder requires an additional build tool beyond the repository pins, Plan 04-06 must pin and review that tool before editing the workflow; this preflight does not invent a version.

## Native PDF preparation and subsequent resolution

The local Windows probe in `.planning/research/PDF-PROBE.md` is valid synthetic evidence only. It used WeasyPrint `70.0` with the verified official Windows onedir DLL source, whose recorded SHA-256 is `ab1151f210b4e6bb7aa7a79e91a67e8ddb760094c107bfda55241b6aaefe7d53`, plus an explicit `WEASYPRINT_DLL_DIRECTORIES` and local `FONTCONFIG_FILE`. The Python WeasyPrint wheel identity recorded in `04-RESEARCH.md` is `5043e55e38d2a2af2b2b871e869697b1f65dad5f8b4a3677961d04ceacf9c5fe`.

Before adding an unattended Windows download step, the owner must resolve the exact approved official asset URL and verify the onedir SHA-256 before extraction. The repository currently records the release page and hash but does not provide a pinned asset URL or a checked-in binary. Do not guess one, use machine-wide `PATH`, or claim Windows PDF CI from the local probe alone.

Before adding an Ubuntu setup step, the owner must resolve the exact Pango/Fontconfig package procedure against the selected runner image and the primary WeasyPrint installation guidance, then run and record the same offline Spanish PDF probe. The repository currently requires that clean Ubuntu render but does not record a verified package list/version receipt. Do not guess package versions or claim Ubuntu PDF capability from Windows evidence.

## Evidence and completion boundary

Plan 04-01 recorded `12 passed` installed-runtime tests, 54 wheel members with exactly 22 authored resources, the wheel SHA above, and matching audited font/oracle bytes. Those checks are reusable only for unchanged resource functions and unchanged wheel inputs; a fresh Plan 04-06 wheel and installed import proof are still required after later implementation changes.

The existing `.github/workflows/verify.yml` is therefore a useful regression base, not a complete Plan 04-06 gate. Plan 04-06 remains incomplete until the installed outside-checkout checks, corrected phase-4 Node control, full regression, actual Windows/Ubuntu PDF probes, and real publication evidence run successfully. This preflight does not mark Phase 4, security, or publication complete.

_Prepared by independent CI preflight review; no workflow or source implementation files modified._


## Primary-source resolution — 2026-09-23

The two preparation questions above are resolved; actual CI execution remains pending.

- Official GitHub release API `repos/Kozea/WeasyPrint/releases/tags/v70.0` returns asset `weasyprint-windows-onedir.zip`, 32,271,073 bytes, SHA-256 `ab1151f210b4e6bb7aa7a79e91a67e8ddb760094c107bfda55241b6aaefe7d53`. Exact [official asset URL](https://github.com/Kozea/WeasyPrint/releases/download/v70.0/weasyprint-windows-onedir.zip); [release metadata](https://api.github.com/repos/Kozea/WeasyPrint/releases/tags/v70.0). Download to runner temporary storage, verify bytes/hash before extraction and use its `weasyprint/_internal` DLL directory only through process/job environment. This matches the already exercised local native source.
- [WeasyPrint 70 installation guidance](https://doc.courtbouillon.org/weasyprint/stable/first_steps.html#ubuntu-20-04) specifies Ubuntu >=20.04 wheel dependencies: `python3-pip libpango-1.0-0 libharfbuzz0b libpangoft2-1.0-0 libharfbuzz-subset0`. Use the configured Python 3.12 interpreter for the Python environment; install the four native libraries from the runner distribution's package manager. Record the runner image and installed native package versions. [Version-pinned source](https://raw.githubusercontent.com/Kozea/WeasyPrint/v70.0/docs/first_steps.rst) confirms this list.
- Configure local Fontconfig against installed bundled DejaVu faces, then run real Spanish PDF generation and text/font readback on both systems. Registry/docs verification is preparation evidence; it cannot be recorded as a successful Ubuntu or CI render.

Plan04-06 requires a small explicit scope addition for these existing acceptance requirements: `.github/workflows/verify.yml` and a portable installed-runtime verification script under `scripts/`. It must update the prohibition collection, build/install the current wheel, use only reviewed dependency versions, and retain actual result artifacts. Do not freeze the intermediate 04-01 wheel or resource count as the final package inventory.

## Portable PDF readback dependency

Real PDF text/font inspection must not depend on the Codex bundled interpreter. The bounded test-only candidate is `pypdf==6.19.0`, verified from its official PyPI registry with BSD-3-Clause license, Python>=3.9 and wheel SHA-256 `7e5d6e730e7dae87d560a2cee218b852f6498c8be61966f3cd02ead971e48d14`; the existing slopcheck name/registry scan returns OK with no flags. The downloaded wheel matches that SHA and is installed in the ignored project-local PDF audit environment. Reading the historical five-page synthetic probe preserved the tested Spanish accents, first/last table labels and embedded-font descriptors. See docs/evidence/phase-04-pdf-audit-dependency.json. Declare it in the appropriate test/audit dependency set when implementing PDF checks and test the final emitted report text/fonts. This is bounded reader preparation, with no vulnerability, final-report or clean-CI certification inferred.
