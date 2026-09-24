# Phase 4 wave 3 verification

2026-09-24 UTC. Scope: Plan 04-05. Phase 4 integration and the final v1.0.0 release remain separate gates.

The frozen operation implementation at `26c9864` passed 38 focused tests and independent review with zero open findings. `04-OPERATION-REVIEW.md` preserves all five resolved findings, including Windows junction containment, sparse exact inventories, CSV/Parquet replay coverage, failed analysis receipts and tied-row ordering. The root review also caught and corrected a misplaced test tail that could mask the independent Parquet negative.

## Actual installed operation

- Installed outside-checkout `research-analyze` produced a fresh packet from immutable numerical acceptance `ee11f305-8113-4ff4-855c-bb8727fe89ab`; operation ID `20260923T235440-f1d9120e3656`, exit 0, zero network attempts. Packet SHA-256: `4b35ce4d67f9b0372aa6e418e88ed8aa90f630b36814a1295cbf79481e25b638`.
- `research-build` consumed that exact new packet and sealed run `20260923T235530-ad828dbe6e56`, exit 0, zero network attempts. Its manifest SHA-256 is `d1de4187b32bcd8311242caa3a4187bca8a093074947e9f37f1d472aacb28136`; receipt SHA-256 is `e39fcd3742a83bde29413cf1f713d13c0bab8ce380d276cba8efc7f65de981d7`. Exact inventory: 73 content artifacts plus manifest and receipt; the operational journal is excluded from the seal.
- Those two commands and four actual `research-open` commands (HTML, Markdown, PDF, CSV) used the `b778eee` wheel, SHA-256 `a49612912c0197d03c75dc58719a2fbee49064bbaaa35f333bdb9f9a405e4b82`. Independent readback verified all 22 typed tables across CSV, Parquet and DuckDB, all manifest hashes, 23 metric definitions and 625 report evidence keys across HTML, Markdown and the 97-page PDF (446 records, 141 comparisons, 38 claims). Parquet and DuckDB also have physical container readback and CLI mapping tests; no additional actual CLI-open invocation is claimed for those two formats.
- The first full reconstruction replay passed at `b778eee`, attempt `20260924T000110-084e6d8e9436`. After an independently reproduced tied-row false mismatch, the final `26c9864` wheel was rebuilt and installed in a separate environment: SHA-256 `709b62ffeaa0153005b088a148d5a1edd37462135f3410792fe2c4b451c83e8e`.
- The final actual installed reconstruction passed: attempt `20260924T001001-c9ecddaaee71`, receipt SHA-256 `825d9d1122b953578b49ce40a9b7cf1b179444149aa69798b701106fcddaa2e8`, exit 0, zero network attempts. It rebuilt reports and all exports, compared typed row multisets and ordered CSV, and reverified the original sealed run and all eight live sources before success.

The canonical digests remain numerical `8db575e9d664864d1513e3b9658bd9b060c4cb3bed8b51561f208adeb97b9a00`, analysis `15f5bdc0fb366f9b3ae75c1c0b096aed1f7b1f4e7f8b71b514f62133ea8dddca` and publication `ff4f7ef1c34927812c15488d46220edd2cebb55378c264827c15b378970a385e`. Public statistical status remains nonofficial `REVIEW`; successful operation does not change that limitation.

## Controlled failure and evidence continuity

A separate eight-ZIP source copy first resolved successfully. The reviewer verified containment and a distinct file identity, removed only one copied ZIP, then called the actual installed offline acquisition API. It created immutable FAILED attempt `20260924T002741769026Z-1ee9bcb4edf2`, SHA-256 `7ad86b0a71a412e26385f815bde5d517e8a6553d57d5edae94c5196d2c5c0b1e`. The subsequent installed open against that copied source exited 1 with a bounded acquisition error and zero network attempts. Original raw/current files, numerical current and immutable receipt, publication current/manifest/receipt and all 73 content artifacts remained hash-identical.

Reusing the successful analysis/build/open/fault checks is bounded by a mechanical continuity proof, SHA-256 `ea5f510cde1f59241ce93fc55ae252d57d9acc848e31f69f1696119cca88e1f6`. The two wheels differ only in `pipeline_v2.py` and its wheel RECORD entry; AST comparison finds only `_logical_exports` and the added Counter import changed. The other 26 definitions, all 24 authored resources and all 36 installed distribution versions match. The changed replay comparator received fresh installed reconstruction above. The fixed 11 numerical code/oracle entries, seven numerical resources, eight source identities, R/library and benchmark hashes remain accepted; no numerical authority or guard was bypassed.

## Evidence and remaining gates

Ignored machine receipts are under `.cache/research/phase4-installed-chain/`, `.cache/research/phase4-installed-readback-20260923/` and `.cache/research/phase4-final-installed-publication-replay/`. The initial readback's underscore-prefix key probe is superseded by `container-keys.json`, which checks actual colon-prefixed canonical IDs. Command receipts use the installed package entry point under a Python audit hook denying socket operations; the envelope is verification tooling, not a runtime dependency.

Canonical wave hooks returned schema drift `block=false/drift_detected=false`, codebase drift `block=false/action_required=false`, and UI safety `hasUiFiles=false/block=false`. Plan 04-06 still owns deliberate all-container canaries, all 45 edge controls, canonical bad/clean prohibition proof, full regression, Windows/Ubuntu installed PDF CI and the aggregate-only public acceptance receipt. No new CI success or release publication follows from this wave.
