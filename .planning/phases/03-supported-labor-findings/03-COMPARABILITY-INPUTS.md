# Phase 3 comparability inputs (Plan 03-02)

Status: input audit complete; this document is a read-only map of accepted
Phase 2 evidence. It does not activate a source, approve the ENT/CVE_ENT
bridge, or define an unreviewed equivalence.

## Authority and accepted evidence

The accepted public projections are the eight files under
`.cache/research/phase2-acceptance/enoe_<year>_q<q>-public-v2.json`. The
corresponding `*-aggregate.json` files are aggregate audit packets: their
`public_records`/request-comparison sections audit the public projection and
they are not internal estimate payloads. The accepted replay is
`.cache/research/phase2-acceptance/final-replay-pass.json`:
`status=PASS`, `official.status=PASS`, `oracle.status=PASS`,
`analytic_oracle.status=PASS`, `no_distinct_person_sum=true`,
`no_independent_quarter_significance=true`, and metric manifest SHA
`2ee87c8b7bfae9addcdf224ae93071023b918a5a22012e1355b9378b73e5827e`.

The exact contract grain is `brujula.research_contract.GRAIN`:

```text
(source_snapshot_id, population_id, field_of_study_id, occupation_id,
 industry_id, geography_id, recorded_sex_id, period_id, metric_id, method_id)
```

The public projection also carries non-grain record metadata (`unit`,
`price_basis`, `method_version`, `design_id`, support/precision, status,
value, evidence references, and synthetic flag). Across all eight files, the
actual observed catalog sets are:

| public projection | geography IDs present | recorded-sex IDs present | population IDs present | record count |
|---|---|---|---|---:|
| 2024-Q3, 2024-Q4, 2025-Q1 | `mx` | `all` | `completed_professional_known_age`, `national_15_plus_context` | 115 each |
| 2025-Q2 | `02`, `mx` | `all` | `completed_professional_known_age`, `national_15_plus_context` | 138 |
| 2025-Q3, 2025-Q4, 2026-Q1 | `mx` | `all` | `completed_professional_known_age`, `national_15_plus_context` | 115 each |
| 2026-Q2 | `01`–`32`, `mx` | `1`, `2`, `all` | `completed_professional_known_age`, `national_15_plus_context` | 5911 |

Thus `geography_id=mx` is the national catalog entry, while state IDs and
sex IDs are present only in the later accepted projections shown above. Their
absence from an earlier projection is a missing endpoint/cell constraint, not
permission to infer a value. There is no stored `record_id`, source SHA, source edition,
geography native field/key, population definition version, metric numerator/denominator
version, classification version, estimator version separate from
`method_version`, or suppression-policy version. The executor must derive a
stable record ID from the contract grain and obtain the missing fields from a
reviewed registry; it must not invent them from labels.

## Snapshot and revision provenance

The following values are directly present in `final-replay-pass.json` under
`snapshots` and in `data/catalog/enoe-snapshots.json` (`expected_sha256`).
`public_v2_digest` identifies accepted public-v2 canonical content and
`public_content_sha256` identifies the public canonical content recorded by
the replay. `internal_content_sha256` identifies the internal v2 canonical
content used by the replay; it is not a byte/JSON hash of the corresponding
`*-aggregate.json` audit packet. The aggregate paths below are audit inputs,
not internal estimate payloads.

| period / snapshot | approved raw ZIP SHA-256 | public-v2 digest | internal canonical digest | native geography | dictionary SHA-256 | SDEM correction evidence |
|---|---|---|---|---|---|---|
| 2024-Q3 / `enoe_2024_q3` | `f384a1b8872e051856ed2241289400302b13a8701489b1c596390452c183cd01` | `6089c67ad241d6d61b554efc7b9612807d5859abfbad961a2e542ec5c71b3741` | `02578f359c6a309e7fb5d854dff6b008da6b713fb9d0930e99a4a654a176722b` | `ENT` | `ce67f37024a4a60767b0b140ad249e9eca98bf900459117cf82f63c3649d251b` | bitácora present, 4 changes, 2025-05-27; SHA `cc3101c01a94cd7e9e810f82bc1cd2d49f3cf867d4ee5fc9e0761f6e283d565e` |
| 2024-Q4 / `enoe_2024_q4` | `bb6d958c9bca11672d367d2c051cd08bf1654c471c2f32c8e21992c126a3b426` | `328e9876a51f4f219fbcff329dc8e73cb424b1538f2b473cef4dda443030a7a7` | `f779e8b0e1ce74f1cfb9eea2c65b7dfc10de2589a2ef8d5f93429aa4e88c41f9` | `ENT` | `ce67f37024a4a60767b0b140ad249e9eca98bf900459117cf82f63c3649d251b` | bitácora present, 9 changes, 2025-05-27; SHA `4716ded92c64ae5053e1f20c6d5df188eed8bf14e503ae88a86e7321cf4062e5` |
| 2025-Q1 / `enoe_2025_q1` | `3931e7c9242147da6ebf9badb1e2b9a59d43d95a9811e077232be406c4ce6691` | `f10c3653eee54c2bf4a3810943ebc78f89f84ce37049380c98f6481bdbe94ba8` | `65b7711346680fbda38adccc1139e1c0c1f8fa7f13f95ab5718bfe34227253a2` | `ENT` | `410dff0ef72908a275e01be116e1bce949d79a38e17a403427840680c64cd51d` | no SDEM bitácora member found |
| 2025-Q2 / `enoe_2025_q2` | `9530a017e3defb0658418b73a47a6039eeb54abf11342fa10693374736515127` | `34abb675c23f098e3972dfa08da26a906a8660eb1a1fcb2b01bb75661d02ce48` | `ea70ad4faa070433df8570b222c35c1a01c3958b4ef661adb82b9fdf6ac8a9b4` | `ENT` | `ce67f37024a4a60767b0b140ad249e9eca98bf900459117cf82f63c3649d251b` | no SDEM bitácora member found |
| 2025-Q3 / `enoe_2025_q3` | `7138b2bfabc740a9805b83b3fd0dae28287fc2aab3781a596a741b8fc7861566` | `79616bc60dc6dfdddc82c82dee4ce29acb1cb68758f8ff89566503ab71bac1ec` | `8cf5e178803b7cefec7fbfae83832055c6d13728eb243ea812950c8d7604ece7` | `CVE_ENT` | `43dd74055f8d4c934c5101b68f70065517f4a4b538d8230592e273b4c0ec6cbe` | no SDEM bitácora member found |
| 2025-Q4 / `enoe_2025_q4` | `e4d4284cc9924a40c39544a5530715f320a5627cd81997214c0430827616d9d6` | `7557e86e8f9f9747d45c5c4115416cf01224371a552c117a63db99a9ea9d2626` | `e575e2d4b6e91461d23da1d065d3d16c667c00a4c2beeb0429a15c984ceb8aa2` | `CVE_ENT` | `43dd74055f8d4c934c5101b68f70065517f4a4b538d8230592e273b4c0ec6cbe` | no SDEM bitácora member found |
| 2026-Q1 / `enoe_2026_q1` | `429c288af46e408de743e5dfb92750f668df7e42789be5824f7cdf1c5ff56580` | `c32d1f01e4f49a95079ce4e65b14f1c02ef5fd85cb65551beaadc81fb5aa07ce` | `df28270b9990d4c96b259877bbbebd109c50dfc8299b13e4ee03f8ad617dad77` | `CVE_ENT` | `43dd74055f8d4c934c5101b68f70065517f4a4b538d8230592e273b4c0ec6cbe` | no SDEM bitácora member found |
| 2026-Q2 / `enoe_2026_q2` | `9ef8877c363f6097da1a04b2077cbda96300cc474b38f835c4963d1dd8f953df` | `bd915277dcb5fcae851c23e33979ce63386811a6b0803808f3f4973a90422eff` | `27c9747bcd3fc0b1bd0d1b65c91d6b2f27970e2e97a81ee7ed78d11912d3c5f5` | `CVE_ENT` | `43dd74055f8d4c934c5101b68f70065517f4a4b538d8230592e273b4c0ec6cbe` | no SDEM bitácora member found |

All eight source inventory records have `catalog_title` matching the period,
`cmpe_catalog_version=CMPE 2016 (bundled cs_p14_c)`, `catalog_member` SHA
`b521d2b5a07e3471da1bd6792183bb2c6864a38e022f74a6a919990c49f4a871`, and
`concept_equivalence_review=REVIEW`. The raw source identity and ZIP hashes are
endpoint provenance. For longitudinal pairs they are retained and expected to
differ across distinct snapshots; they are not equality-required comparability
fields. Same-period cross-slice pairs require exact snapshot identity/hash
equality. An unapproved hash or revision is blocked. An unknown edition date
is a visible limitation; comparison may pass when the exact approved snapshot
and reviewed edition/correction compatibility are otherwise present. An absent
or unreviewed edition/signature remains blocked.

## Signature input matrix

| signature member | exact accepted path / value | comparison rule |
|---|---|---|
| source family | `data/catalog/enoe-snapshots.json`: `source_id=inegi_enoe`, authority INEGI; public `evidence[].source_snapshot_id` resolves to the snapshot | equal-required family; source URL, raw ZIP SHA, public digest and snapshot ID are endpoint provenance for longitudinal, exact snapshot identity/hash equality for cross-slice |
| edition / correction | source inventory `catalog_title`, dictionary member/hash, `revisions`; 2024-Q3/Q4 have change logs, later six have none | reviewed registry must pin approved snapshot/hash plus edition/correction compatibility; absent/unreviewed or contradictory state blocks; unknown edition date alone remains a visible limitation |
| period | public `periods[0].id`, `start`, `end`, and each record `period_id` | equal only for cross-slice; longitudinal must be ordered and distinct, with q→q+1 or q→q+4 only |
| population / universe | public record `population_id`; definitions in `brujula/populations.py::POPULATION_DEFINITIONS` | equal-required ID and reviewed definition version; `national_15_plus_context` and `completed_professional_known_age` never compare to each other |
| field, occupation, industry | public record IDs; labels in public catalogs; focus CMPE keys `031300`, `032100`, `033100`, `all` | equal-required concept and classification version; no field/occupation/industry substitution |
| geography | public projections expose `mx`, `02` in 2025-Q2, and `01..32` plus `mx` in 2026-Q2; native state field and raw lexeme are absent from public projection; source inventory gives `ENT` through 2025-Q2 and `CVE_ENT` from 2025-Q3 | registry must supply geography type/concept, normalized key/name, native field and catalog hash. ENT `1..32`→`01..32`, CVE_ENT `01..32`; name equality and reviewed concept evidence are all required |
| recorded sex | public projections expose `all` through 2026-Q1 and `1`, `2`, `all` in 2026-Q2 | equal-required longitudinal; cross-slice sex axis may compare 1 vs 2 only with national geography and all other fields fixed |
| metric / denominator | `data/catalog/enoe-metrics.json`, version `enoe-metrics-2026-09-22`, content SHA `2ee87c8b...e5827e`; public record `metric_id`, `unit`, `price_basis` | equal-required metric ID plus numerator, denominator, dictionary refs and definition version from registry; labels/units alone are insufficient |
| unit / price basis | public record and metric catalog. `positive_income_mean` is `MXN/month` + `nominal`; all other listed units use `not_applicable` | equal-required; income deltas are nominal MXN/month only, never purchasing-power change or stable real-price bands |
| estimator / design / method | public `method_id`, `method_version`, `design_id`; precision has `method`, `ci_method`, `singleton_policy`, `official_precision` | equal-required method/design and reviewed estimator/version; `singleton_policy=adjust` and `official_precision=false` remain visible |
| suppression / support | public `status`, `reason`, `value`, `sample_size`, support and precision fields | equal-required suppression/precision policy. Unsupported, UNKNOWN, BLOCKED, null endpoint or missing registry input yields null deltas |
| sample dependence | replay flags above; no public field identifies respondent overlap | descriptive only; never sum quarterly people or derive SE/CI/p/value/significance from marginal intervals |

The public metric catalog has 23 metric IDs. The income rule is exact:
`positive_income_mean` uses `INGOCUP` positive `1..999998`, consistent with
`ING7C=1..5`, and is nominal `MXN/month`; `ING7C=6` is no income, `ING7C=7`
is unspecified, and `INGOCUP=0` or `999999` is not a zero salary. These rules
come from `data/catalog/enoe-metrics.json` and
`brujula/populations.py::classify_income_state`; they do not supply a real
price index.

## Missing-data constraints for the executor

1. Keep every expected quarter pair slot, including a missing/suppressed
   endpoint. Emit null absolute and relative deltas with stable reasons.
2. Longitudinal endpoint signatures may have different snapshot IDs and hashes
   as provenance. They still require equality of source family/edition state,
   population definition, geography concept/key, sex, concepts/classifications,
   metric numerator/denominator/version, unit/basis, method/design, and
   precision/suppression policy.
3. A 2025-Q2 `ENT` and 2025-Q3 `CVE_ENT` state comparison is only eligible when
   the reviewed registry confirms normalized two-digit code, exact official
   name, and concept evidence. The alias or equal names alone cannot pass it.
4. Same-period sex/entity slices require exact period, snapshot ID, snapshot
   hash, source/edition, and every signature member fixed except the declared
   axis. Entity contrast also requires the mandatory reviewed registry entity
   reference; sex contrast requires national geography and recorded sex 1 vs 2.
5. Missing definition/version/edition/revision evidence, absent or unreviewed
   edition/signature, incompatible correction evidence, wrong alias,
   malformed/out-of-range key, or a suppressed endpoint is `BLOCKED`, not
   equivalent and not zero. An unknown edition date alone is a visible
   limitation and may pass only with approved exact snapshot plus reviewed
   edition/correction compatibility.
6. Do not add comparison SE, CI, p-value, significance, combined quarterly
   sample/person counts, purchasing-power wording, or cross-year minimum-wage
   bands to the comparison ledger.

## Evidence paths

- Contract authority: `docs/CONTRACT-V2.md`.
- Geography review and official cross-boundary evidence: `.planning/research/GEOGRAPHY-COMPARABILITY.md`.
- Source and revision inventory: `.cache/research/enoe-source-inventory.json`.
- Snapshot catalog: `data/catalog/enoe-snapshots.json`.
- Metric definitions/version: `data/catalog/enoe-metrics.json`.
- Population definitions and income sentinels: `brujula/populations.py`.
- Accepted replay receipt and all eight canonical projection/internal digests: `.cache/research/phase2-acceptance/final-replay-pass.json`.
- Aggregate audit packets (public-record audit, not internal estimate payload): `.cache/research/phase2-acceptance/enoe_<year>_q<q>-aggregate.json`.
