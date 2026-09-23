# Geography comparability: `ENT` to `CVE_ENT`

**Status:** REVIEW / planning evidence only  
**Scope:** ENOE SDEM snapshots 2024-Q3 through 2026-Q2; state and national comparisons  
**Reviewed:** 2026-09-22 local  

## Decision

The 2025-Q3 change from `ENT` to `CVE_ENT` is representation-compatible for a
candidate bridge, but it is not proof that the geography concept or survey
state changed. The local metadata supports a deterministic code normalization:
trim ASCII padding, validate a two-digit state key in `01`–`32`, and map the
2024–Q2 `ENT` values `1`–`32` to their zero-filled equivalents. Preserve the
period's source field and raw lexeme in provenance. Keep the bridge in `REVIEW`
until ANA-03 records the source and concept signature.

Accordingly, the reviewed rule is:

* Comparisons within the `ENT` regime (2024-Q3 through 2025-Q2) may use the
  period's native field after the normal state-code validation.
* Comparisons within the `CVE_ENT` regime (2025-Q3 through 2026-Q2) may use the
  period's native field after the same validation.
* A state-level descriptive delta crossing 2025-Q3 may pass the geography gate
  after ANA-03 verifies the candidate signature below, even though the native
  column name changes. A normalized key alone is insufficient.
* A national aggregate does not require a state-code join, so it may be
  computed within each snapshot. A national delta crossing 2025-Q3 may pass
  when the same signature and metric contract are verified; the alias itself
  cannot certify national comparability.

This is a routing rule for planning. It does not activate a source or bridge and
does not authorize person-row publication.

## Direct local evidence

The resolver-backed inventory contains eight successful current snapshots in
chronological order. The SDEM headers have 114 columns through 2025-Q2 and 115
from 2025-Q3. The observed geography transition is `ent` → `cve_ent`, with
`ageb`, `loc`, and `mun` changing to `cve_ageb`, `cve_loc`, and `cve_mun`; the
2025-Q3 header also introduces `cvegeo`. No duplicate headers were reported.

The exact SDEM dictionary rows are:

| Regime | Dictionary SHA-256 | Geography row | Declared range |
|---|---|---|---|
| 2024-Q3..2025-Q2 | `ce67f37024a4a60767b0b140ad249e9eca98bf900459117cf82f63c3649d251b` (2024-Q3/Q4 and 2025-Q2); `410dff0ef72908a275e01be116e1bce949d79a38e17a403427840680c64cd51d` (2025-Q1) | `Entidad` / `ent` | `[01-32]` |
| 2025-Q3..2026-Q2 | `43dd74055f8d4c934c5101b68f70065517f4a4b538d8230592e273b4c0ec6cbe` | `Entidad federativa` / `cve_ent` | `[01-32]` |

The dictionary hash change proves that the dictionary bytes changed, and the
added column proves an observed schema difference. Together they require
period-aware parsing. They do not by themselves establish a conceptual,
frame, boundary, or universe change, and they do not certify semantic
continuity.

The exact SDEM state catalogs provide stronger code-set evidence:

| Periods | Member | Member SHA-256 | Rows | Key form | Names |
|---|---|---|---:|---|---|
| 2024-Q3..2025-Q2 | `.../catalogos/ent.csv` | `ea2e8198df208d0b662c00766739eb39c5a6b9a198821903d1a9416cdf9c7c1a` | 32 | `1`..`32` | 32 unique names, Aguascalientes through Zacatecas |
| 2025-Q3..2026-Q2 | `.../catalogos/cve_ent.csv` | `f297f6856885a3da13f754749000e0a35d8c1745e7f2cf474a1e2adc01e07ddf` | 32 | `01`..`32` | 32 unique names, Aguascalientes through Zacatecas |

The full member paths represented by those grouped rows are
`conjunto_de_datos_sdem_enoe_2024_3t/catalogos/ent.csv`,
`conjunto_de_datos_sdem_enoe_2024_4t/catalogos/ent.csv`,
`conjunto_de_datos_sdem_enoe_2025_1t/catalogos/ent.csv`,
`conjunto_de_datos_sdem_enoe_2025_2t/catalogos/ent.csv`,
`conjunto_de_datos_sdem_enoe_2025_3t/catalogos/cve_ent.csv`,
`conjunto_de_datos_sdem_enoe_2025_4t/catalogos/cve_ent.csv`,
`conjunto_de_datos_sdem_enoe_2026_1t/catalogos/cve_ent.csv`, and
`conjunto_de_datos_sdem_enoe_2026_2t/catalogos/cve_ent.csv`.

After zero-filling the first catalog's keys, the two key/name sets are equal
for all 32 states. This establishes a safe mechanical normalization for joins;
it does not establish boundary or universe equivalence.

The bundled CMPE study catalog is stable across all eight snapshots:
`b521d2b5a07e3471da1bd6792183bb2c6864a38e022f74a6a919990c49f4a871`.
That identity is relevant to field-of-study comparisons, but it is independent
of the geography bridge and cannot waive the geography review. The focus CMPE
keys remain normalized to six digits (`031300`, `032100`, `033100`), with
`999999` and absent values unknown.

## Official cross-boundary review

INEGI's official [ENOE Bulletin 636/25 (26 November 2025)](https://www.inegi.org.mx/contenidos/saladeprensa/boletines/2025/enoe/enoe2025_11.pdf),
page 3 (Cuadro 1), explicitly compares the third quarters of 2024 and 2025 at
the national level. It reports total population `101,620,868` and `103,068,355`,
PEA `61,370,334` and `61,303,255`, occupied `59,528,249` and `59,533,449`,
and unemployed `1,842,085` and `1,769,806`, respectively. The same table also
reports women and men. This is primary evidence that INEGI publishes selected
descriptive national comparisons across the period boundary; it is not a
claim that every microdata field, state bridge, estimate, or precision property
is interchangeable.

The official [ENOE executive presentation for 2025-Q3](https://www.inegi.org.mx/contenidos/programas/enoe/15ymas/doc/enoe_presentacion_ejecutiva_trim3_2025.pdf),
pages 3–4, states the population target as people aged 15 and over, identifies
households and usual residents of private dwellings as observation units, and
states national and 32-entity coverage. It also identifies face-to-face and
telephone interviewing. These statements support the candidate signature's
population, geography coverage, and method fields for the official ENOE
publication, subject to matching the local metric and period records.

The [INEGI ENOE program page](https://www.inegi.org.mx/programas/enoe/) is the
official program landing page used for source identity. The page and the two
official documents support a candidate source signature; they do not activate a
local source or bridge.

### Candidate ANA-03 concept signature

Treat a cross-boundary descriptive delta as eligible for review when all of the
following fields match between periods and are recorded in the evidence packet:

1. source identity is INEGI ENOE, with the approved snapshot and official
   publication references;
2. population/universe is the same explicitly defined population (for example,
   ENOE people aged 15 and over, with the local response/residence rules);
3. geography is national or one of the same 32 entities, with native keys
   normalized to the two-digit ID and catalog names checked equal;
4. concept and measure are the same (for example, PEA, occupied, unemployed,
   or a specified field-of-study measure), with units and denominator stated;
5. method and design metadata match, including the applicable survey method,
   weight, variance/precision treatment, and any suppression rule; and
6. period is the intended quarter and the result is labeled descriptive, with
   no added causal, significance, or official-precision claim.

The official bulletin directly satisfies the evidence pattern for its listed
national counts, but does not substitute for checks 2–6 on a locally derived
state or field-of-study estimate. A state-level delta therefore changes from
an unconditional block to `REVIEW`/eligible only after the signature is
complete. Any failed, missing, or contradictory field remains `BLOCKED`.

## What can and cannot compare automatically

Automatic comparison is permitted only when the normal comparison contract also
passes source, universe, measure, price basis, method, concept, and period
checks. Within one alias regime, state values can be keyed by the native
catalog key and national values can be aggregated without a geography join.
Across the alias boundary, the candidate signature above must additionally be
complete. A passing signature permits a descriptive delta to retain its value;
it does not authorize inferential claims or publication by itself.

Across the 2025-Q3 boundary, the following remain blocked unless the candidate
signature and full comparison contract pass:

* any state-level temporal delta that has only the `ENT` → `CVE_ENT`
  normalization as evidence;
* any national temporal delta for a locally derived metric whose population,
  measure, method, or precision metadata are not matched;
* claims that the four renamed geography variables are interchangeable at
  municipality, locality, AGEB, or `CVEGEO` grain;
* any bridge that maps codes by position, label similarity, or the field-name
  change alone.

Missing, malformed, out-of-range, duplicate, or unmapped keys remain unknown or
blocked; they are never recoded to zero or silently dropped. The raw field and
the normalized key must remain separate dimensions in downstream evidence.

## Evidence paths and limits

Primary evidence is the local resolver inventory
`.cache/research/enoe-source-inventory.json`, whose records retain each raw ZIP
SHA, exact SDEM member path/hash/size, dictionary member/hash, catalog member
hash, native geography header, and `concept_equivalence_review: REVIEW`.
The exact ZIP members were checked under `artifacts/enoe/raw/<raw_sha256>.zip`
through the existing resolver; no person rows are included in this note.

Supporting package metadata and prior routing are in
`.planning/phases/01-official-sources-and-research-contract/01-RESEARCH.md`
(SRC-03 and the resolved-but-unactivated geography question). The local
inventory records the 2024-Q3 and 2024-Q4 SDEM correction logs, but no correction
log exists in the later packages; those revision differences are another reason
to retain the cross-boundary `REVIEW` state and require the candidate signature
before an automatic delta.

The full survey-frame and boundary semantics associated with the 2025-Q3
metadata change remain unverified in the local evidence. This document
intentionally makes no official claim of conceptual equivalence and performs no
numeric comparison.
