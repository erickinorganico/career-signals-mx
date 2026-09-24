---
phase: 04-offline-publication-and-reproducible-operation
reviewed: 2026-09-24T00:28:42Z
depth: deep
source_commit: 26c9864
files_reviewed: 7
files_reviewed_list:
  - brujula/pipeline_v2.py
  - brujula/cli.py
  - brujula/resources.py
  - contracts/publication-manifest-v2.schema.json
  - tests/test_pipeline_v2.py
  - tests/test_cli_v2.py
  - tests/test_installed_runtime.py
findings:
  critical: 0
  warning: 0
  info: 0
  total: 0
status: clean
---

# Plan 04-05: Operation code review

This bounded review covers the sealed publication builder, current resolver, installed CLI wiring, manifest schema, packaged resource registration, focused tests, and their acquisition/numerical/publication call boundaries. The final source delta is pinned to commit `26c9864` and these SHA-256 values:

| File | SHA-256 |
|---|---|
| `brujula/pipeline_v2.py` | `63b341060c76a6a4b5b9441b5186b513c54aae43eb3f810e9d8143e3b58e3613` |
| `brujula/cli.py` | `303524fb3203dfd037a00c8b299763a56711a0ee2c99915af2f800aff1c42c26` |
| `brujula/resources.py` | `1eea5cf7391430b7eb3640049ab97db8a0245ac35affb2e25d7cdf8150f2d9cd` |
| `contracts/publication-manifest-v2.schema.json` | `ab543f5f3361f7065a0dceadc7a66eebc9c547382b423b152907a6c946924bc2` |
| `tests/test_pipeline_v2.py` | `b65741e17269e36212ba3ecc3711b5f53dca8fd4113e30568f51a7f5ae793221` |
| `tests/test_cli_v2.py` | `758409f8b6532bfab7cbc530a2bf6837ebbe4710124e1cf6e69f2307072a10be` |
| `tests/test_installed_runtime.py` | `90a27aa6f4f2c42b14ae6b2e74e0b2792e6fe839c3069c44ac88a1c65b64fb20` |

I independently ran `tests/test_pipeline_v2.py tests/test_cli_v2.py tests/test_installed_runtime.py -q` under the reviewed local WeasyPrint DLL/font configuration at `b778eee`: **35 passed in 6.71s**. For the final replay comparator delta at `26c9864`, I read both source and test diffs and reran its two direct focused tests: **2 passed, 20 deselected**. The executor reported **38 focused passes** on that delta. These checks do not substitute for the fresh installed eight-source chain and real output readback underway with the root reviewer.

## Narrative Findings (AI reviewer)

No open code, security or material contract finding remains in this bounded scope at the recorded hashes. The defects identified during this review are retained below with closure evidence.

## Resolved findings

- **CR-01 · BLOCKER · RESOLVED — Windows junction redirected run writes outside the declared output root.** On the initial `5e1446c` implementation, a real disposable `<output_root>/runs` Windows junction had `Path.is_symlink() == False` and `Path.is_junction() == True`. A controlled `build_publication` call created an immutable failure receipt under the junction's external target before any source processing. At `b778eee`, `_strict_roots`, `_guard_children`, `_safe_file`, `_disk_files`, authority checks and replay/analysis paths reject symlinks and junctions before writes (`brujula/pipeline_v2.py:48-84,280-293,472-501,576-589`). I reran the actual planted-junction build on this commit: `ValueError: symlink or junction publication path`; zero outside run directories, no outside receipt and no output current. An `analysis_output` junction-parent negative similarly raises before a packet or operation receipt is written. Focused tests cover both paths.
- **CR-02 · BLOCKER · RESOLVED — fixed 73-file cardinality rejected valid sparse opening sets.** The initial schema and resolver required exactly 73 files even though zero to three accepted opening claims generate 67, 69, 71 or 73 exact files. The schema now permits that bounded range, while `_verify_sealed` enforces equality with the model-derived `_expected(model)` set (`contracts/publication-manifest-v2.schema.json`; `brujula/pipeline_v2.py:184-203,399-405`). The focused test builds and validates all four inventory sizes. My separate six-base-figure probe yields 67 expected paths within the schema's 67–73 range.
- **CR-03 · BLOCKER · RESOLVED — reconstruction replay could pass with changed CSV/Parquet values.** Initially `_logical_exports` checked only DuckDB tables; identical DuckDB rows and a changed `public-records.csv` returned `True` in a disposable reproduction. The final function compares table names/types/typed-row multisets in DuckDB and Parquet plus parsed CSV rows for every declared table (`brujula/pipeline_v2.py:540-574`). Repeating the CSV-only alteration now returns `False`; a separate focused test mutates Parquet after restoring CSV, so each negative is independently exercised. `replay_publication` still rebuilds reports/exports into a separate attempt and rechecks the sealed baseline and eight live sources before success.
- **CR-04 · BLOCKER · RESOLVED — missing immutable numerical acceptance bypassed analysis failure receipt.** `_accepted` originally ran before `analyze_acceptance`'s operational `try`; a missing selected receipt could raise without the promised separate BLOCKED operation receipt. The call now runs after safe root validation inside the guarded operation (`brujula/pipeline_v2.py:481-537`), and `test_missing_accepted_receipt_seals_analysis_failure` verifies an immutable failure receipt plus BLOCKED analysis current. The numerical acceptance audit remains read-only.
- **CR-05 · BLOCKER · RESOLVED — replay falsely rejected equal typed exports with tied first-column values.** At `b778eee`, `_logical_exports` sorted DuckDB and Parquet by the first column only. A disposable pair of identical row multisets with duplicate first-column keys but reversed insertion order returned `False`; SQL does not define tie order for `ORDER BY 1`. Commit `84abac8` compares full typed rows with `Counter` for DuckDB and Parquet while retaining ordered CSV comparison. The positive tied-row regression passes; the independent CSV and Parquet corruption negatives also pass after test isolation in `26c9864`. This is a bounded source/test verdict; an installed replay of the corrected wheel is a separate runtime gate.

The builder binds the packet's canonical numerical/source summary to the selected immutable acceptance, validates and reloads sealed `analysis.json`, derives its exact report/figure/font/export inventory from the public model, seals receipt then manifest before current promotion, and hashes the five audited font assets on resolution. The resolver checks the manifest, receipt, all artifacts and all eight current acquisition identities twice before returning paths. The sealed real run was built with the earlier `b778eee` installed wheel. The corrected wheel's installed replay has since produced a separate PASS attempt `20260924T001001-c9ecddaaee71` in `.cache/research/phase4-final-installed-publication-replay/attempts/`, with 73 artifacts and the same numerical, analysis and publication digests. This is runtime evidence for reconstruction of that run; the review remains bounded to Plan 04-05 source and contract paths.

_Reviewer: independent Plan 04-05 code/security review. Only this review artifact was written; no source or Git state changed by the reviewer._
