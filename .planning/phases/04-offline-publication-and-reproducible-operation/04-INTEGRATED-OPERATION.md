# Phase 4 integrated installed recovery and metadata evidence

Source freeze `c222f69` includes interrupted-run recovery (`98e2fc8`) and
public figure context (`c222f69`). This evidence supplements 04-WAVE3-CHECKS;
it does not designate Phase 4, cross-platform CI or the public release complete.

## Executed operation

The wheel SHA-256 is
`77e6a0e36aa897a3e7f054b49b6259837be3ccb83b5200adec9e63e0fb61e983`.
It ran outside the checkout in an isolated Python 3.12 environment with the same
35 pinned dependencies. Installed identity checks matched all 24 authored
resources, 11 numerical implementation/oracle hashes and seven numerical
resource hashes to accepted numerical evidence. No numerical acceptance was
regenerated or weakened.

A Python audit hook terminated the actual installed CLI with `os._exit(17)`
before its first journal atomic replace, after the current pointer and OS lock
record existed. The hook did not replace a production function or validation
guard. The interrupted attempt was `20260924T010245-fdd01aefc560`.

The next unmodified installed `research-build` recovered that attempt under
the exclusive OS lock. It retained a bounded immutable `BLOCKED`/`FAILED`
receipt at stage `interrupted_recovery`, SHA-256
`db3d5a5ff07dddf9a3da38dea8e6dfbbae72f44833dfea134ee661147058c605`.
It then built run `20260924T010247-81cfb71ea5f1` from the new installed analysis
packet already accepted in 04-WAVE3-CHECKS. Build exited zero in 300.984 seconds;
the subsequent actual installed `research-open --format pdf` exited zero in
164.609 seconds. Both ran with socket network operations denied; no network
attempt occurred. These timings describe these checks, not a service guarantee.

The new manifest SHA-256 is
`38c3dfc21d816f32d7e4a21d7efd89418fc198fd80e94577783706f00d7fb023`;
the successful receipt SHA-256 is
`1b2e2c228700c8491ea7ee2c1d489fb7af5cc603e1da40ba610d7144dcf5cbe1`.
All 73 declared content artifacts match their hashes. All 87 tracked original
publication, numerical acceptance and acquisition-current anchors remain
byte-identical. The original successful publication was not overwritten.

## Container and visual continuity

- All 22 tables have matching typed rows and headers across CSV, Parquet and
  DuckDB. Public exports retain 6,739 record IDs, 4,209 comparison IDs and 38
  claim IDs.
- HTML, Markdown and the 97-page PDF contain the same selected 446 record,
  141 comparison and 38 claim IDs, with all eight quarter labels.
- All nine PNG pixel buffers are exactly identical to the accepted real
  publication. SVG/PNG numeric manifests match the old public values exactly;
  added context includes title, universe, units, period, geography, field,
  recorded sex, metric and source. The plot layout function is AST-identical.
- PDF pages 2–97 have identical content streams and extracted text. Page 1
  differs only in the generation date, from 2026-09-23 to 2026-09-24 UTC.
  The orchestrator rendered and inspected the new page 1 at 1400 pixels:
  title, date, opening claim, limitations, evidence link and footer fit without
  clipping or overlap; Spanish accents remain legible. Its PNG SHA-256 is
  `8723ac4574063e6b42e345e5f0ea59219a9f3d9ecee9727b196e63a3b1fb33ac`.

Only `pipeline_v2.py`, `report_v2.py` and wheel RECORD differ from the prior
`26c9864` wheel. The analysis and replay implementations remain AST-identical.
The earlier complete installed reconstruction replay is retained as bounded
evidence for those unchanged methods; changed recovery, successful resolution
and rendering were directly exercised above. This is not a claim that a new
full reconstruction replay ran on `c222f69`.

## Receipts and regression checks

Local detailed receipts reside in `.cache/research/phase4-integrated-operation`;
they are deliberately excluded from public assets because command envelopes
contain workstation paths. Public-safe identifiers and hashes are recorded here.

| Receipt | SHA-256 |
|---|---|
| recovery-proof.json | `8f59cb54a828b30808618d793ec00d253bf2183d8a1ce53bdfe5f10e5e52056a` |
| metadata-continuity.json | `6796df323f669624ec735a879cccbeecc9d1088f45027a1902861ce0b43d8c82` |
| build-command.json | `129a39947b5a6e3d0cbac92ac3e3577fe98a5cafea5c059326824a7e25de4386` |
| open-command.json | `cb044c64e1b67db7db8a5fc40f97fc76405d640b21366286cf32400a466df848` |

Recovery regression: 52 passed across pipeline-v2, CLI-v2, CLI and installed
runtime tests, including real subprocess exit 17, five interruption positions,
idempotent recovery and malformed/reparse-path rejection. Metadata regression:
20 passed across report-v2 and PDF-v2 tests after the RED regression commit
`b6de4c3`. Independent metadata review is in 04-METADATA-REVIEW.md. Integrated
disclosure controls, native Windows/Ubuntu CI and final phase reviews remain
separate gates.
