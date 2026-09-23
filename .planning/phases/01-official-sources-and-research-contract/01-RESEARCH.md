# Phase 1: Official Sources and Research Contract — Research

**Researched:** 2026-09-22 local / 2026-09-23 UTC · **Confidence:** HIGH for pinned package metadata and code; MEDIUM for concept semantics from official-method review.

<user_constraints>
## User Constraints (from CONTEXT.md)
### Locked Decisions
#### Fuente y reproducción
- Usar exclusivamente las ocho URLs exactas del catálogo aprobado, con sus SHA ya adquiridos y fijados. Validar también miembro SDEM, diccionario y catálogos, sin inventar URLs ni elegir el primer CSV por substring.
- Conservar intentos fallidos y éxitos posteriores; resolver current mediante el recibo inmutable y su hash. No volver a descargar archivos para cubrir una falla de validación que puede resolverse offline.
- Inventariar correcciones incluidas en los paquetes 2024 y el cambio ENT→CVE_ENT desde 2025-Q3; un alias compatible no implica automáticamente ruptura de concepto, pero debe quedar verificado.
- Publicar metadatos y agregados; ZIP y filas de personas permanecen en carpetas ignoradas. Términos y atribución INEGI acompañan los outputs.
#### Universos y conceptos
- Contexto nacional: respuesta válida R_DEF=0 y residentes C_RES∈{1,3}; reproducir la convención oficial operativa 15<=EDA<=98 para benchmarks, declarando 98 como edad no especificada y nunca como 98 años.
- Cohorte principal de perfiles: respuesta/residencia válidas, edad conocida 15–97, CS_P13_1=7 y CS_P16=1; excluye técnicos, estudios incompletos y posgrados. Reportar las exclusiones. No llamarla el total de personas que alguna vez cursaron una licenciatura.
- Campos CS_P14_C se vinculan al catálogo incluido en cada paquete mediante normalización comprobada a seis dígitos. Foco: 033100, 032100 y 031300. 999999 y códigos ausentes tienen cobertura desconocida, sin inventar un campo.
- Campo de estudios, ocupación, industria, entidad, sexo registrado y periodo mantienen dimensiones distintas. No crear bridges automáticos.
#### Contrato y valores públicos
- Mantener contrato v1 y pruebas sintéticas. Definir contrato v2 separado para investigación real, con grain único y registros estrictos.
- Incluir el método, diseño, precisión, soporte, unidad/base de precios y evidencia en cada estimación. `sample_size` significa n observado; no es tamaño efectivo.
- Separar el diagnóstico interno `estimate` de `value` público. La proyección pública omite estimación e intervalos que revelarían valores suprimidos.
- Definir denominadores y sentinelas con los diccionarios de los ocho paquetes. INGOCUP cero no es salario cero por sí solo; ingreso positivo conocido no describe a todos los ocupados.
- La política singleton permanece explícita y su aceptación numérica corresponde a fase 2. El contrato debe admitirla sin etiquetarla como precisión oficial ni activar publicación automáticamente.
### the agent's Discretion
- Nombres internos, distribución de archivos y pruebas acotadas compatibles con las convenciones existentes.
- Reutilizar código correcto ya escrito y verificarlo; no reimplementar para que parezca nuevo trabajo GSD.
### Deferred Ideas (OUT OF SCOPE)
Estimación y oráculos (fase 2), perfiles/comparaciones/claims (fase 3), informe y pipeline final (fase 4), release (fase 5). Son dependencias posteriores comprometidas, no funciones descartadas. No se agrega un frontend.
</user_constraints>

<phase_requirements>
## Phase Requirements
| ID | Description | Research support |
|---|---|---|
| SRC-01 | Eight approved SHA-pinned ENOE ZIPs resolve offline. | Eight successful `resolve_snapshot` probes; existing acquisition module. [VERIFIED: local resolver and receipts] |
| SRC-02 | Attempts are receipted; failure invalidates current. | Existing immutable attempts/current checks and acquisition tests. [VERIFIED: `brujula/acquisition.py`; `tests/test_acquisition.py`] |
| SRC-03 | Per-period member, dictionary, catalog, revision, codes, geography aliases. | Eight-package table and correction inventory below. [VERIFIED: pinned ZIP probe] |
| SRC-04 | Terms, attribution, acquisition date, transformation; person rows local. | Receipt timestamps and INEGI terms. [VERIFIED: receipts] [CITED: https://www.inegi.org.mx/inegi/terminos.html] |
| CTR-01 | Strict separate v2 record and intact v1 synthetic gates. | Grain and projection proposal below. [VERIFIED: `docs/CONTRACT.md`; existing schema/tests] |
| CTR-02 | Explicit national and completed-professional universes and denominators. | Population table below. [VERIFIED: CONTEXT.md; eight SDEM dictionaries] |
</phase_requirements>

## Summary
All eight registry-approved ENOE ZIPs are cached at pinned SHA-256 and resolved successfully on 2026-09-22 local (receipts complete 2026-09-23 UTC). `resolve_snapshot` checks current against immutable attempt, registry URL/SHA, raw bytes and ZIP safety; plan to reuse it. The remaining Phase 1 work is a per-snapshot metadata inventory, explicit universe/denominator rules, and a separate strict v2 contract. Estimation and official numerical reconciliation belong to Phase 2. [VERIFIED: `data/catalog/enoe-snapshots.json`; `brujula/acquisition.py`; eight offline resolutions; ROADMAP.md]

**Primary recommendation:** Have one inventory read only through the resolver, pin every required member and revision, then validate named populations and v2 research records without exporting person rows. [VERIFIED: repository contract; ZIP probe]

## Architectural Responsibility Map
| Capability | Primary tier | Secondary tier | Rationale |
|---|---|---|---|
| Approved bytes and receipts | Local acquisition/storage | Official INEGI host | Existing resolver is the integrity/current authority. [VERIFIED: acquisition code] |
| Package inventory and code mapping | Local metadata pipeline | Pinned ZIP | Period-specific bytes, not generic file names, define inputs. [VERIFIED: ZIP probe] |
| Populations/denominators | Research contract | Future survey adapter | Phase 1 defines rules; Phase 2 estimates. [VERIFIED: CONTEXT.md] |
| V2 validation/public view | Contract/quality layer | Future publisher | One strict grain and projection prevent dimension collapse/leakage. [VERIFIED: CONTEXT.md; v1 contract] |

## Project Constraints (from AGENTS.md)
Read `docs/CONTRACT.md` before interface edits; preserve v1 synthetic gates. Local scripts, docs, fixtures and isolated tests are authorized. No paid API, external inference, credentials, third-party messages, frontend, backend service or app. Read public sources only through the approved catalog; keep raw rows local and publish only validated synthetic or redistributable public data after secret/license review. Keep field, occupation, industry, geography, period and source distinct; missing remains null. Claims need exact evidence; agent proposals do not activate sources or bridges. Failed refresh invalidates current; comparability includes source, universe, geography, measure, price basis, method, concept and period. Preserve others' edits and exclude unrelated proprietary data. [VERIFIED: `AGENTS.md`]

## Standard Stack
| Component | Version | Use |
|---|---|---|
| Python and stdlib `zipfile/csv/json/hashlib/pathlib` | local 3.12.13, project >=3.12 | Inspect metadata and hash members; no extraction or new dependency. [VERIFIED: local CLI; pyproject] |
| `jsonschema` | pinned/installed 4.26.0 | Separate strict v2 schema using current v1 pattern. [VERIFIED: pyproject; local metadata] |
| `pytest` | pinned/installed 9.0.3 | Focused fixture tests and unchanged v1 regression. [VERIFIED: pyproject; local CLI] |

No new package installation is recommended; Package Legitimacy Audit does not apply. [VERIFIED: existing dependencies; phase requirements]

## Source and Package Inventory
The registry owns exact URL and full expected raw SHA; code must not duplicate them. Every ZIP has exactly one main `conjunto_de_datos_sdem_enoe_YYYY_Nt/conjunto_de_datos/conjunto_de_datos_sdem_enoe_YYYY_Nt.csv`, one sibling `diccionario_de_datos/diccionario_datos_sdem_enoe_YYYY_Nt.csv`, and one sibling `catalogos/cs_p14_c.csv`. Require exact path and unique match; the 2024 SDEM bitácoras are separate CSVs. Store full member path, member hash/size, dictionary/catalog hash, header, review date and acquisition receipt reference. [VERIFIED: eight ZIP listings]

| Quarter | Raw SHA prefix | SDEM columns | Geography | Dictionary SHA-256 | Revision |
|---|---|---:|---|---|---|
| 2024-Q3 | `f384a1b8872e` | 114 | ENT | `ce67f37024a4a60767b0b140ad249e9eca98bf900459117cf82f63c3649d251b` | 4 `cs_p14_c` corrections. [VERIFIED: pinned ZIP] |
| 2024-Q4 | `bb6d958c9bca` | 114 | ENT | `ce67f37024a4a60767b0b140ad249e9eca98bf900459117cf82f63c3649d251b` | 9 corrections. [VERIFIED: pinned ZIP] |
| 2025-Q1 | `3931e7c92421` | 114 | ENT | `410dff0ef72908a275e01be116e1bce949d79a38e17a403427840680c64cd51d` | No SDEM bitácora member found. [VERIFIED: ZIP listing] |
| 2025-Q2 | `9530a017e3de` | 114 | ENT | `ce67f37024a4a60767b0b140ad249e9eca98bf900459117cf82f63c3649d251b` | No SDEM bitácora member found. [VERIFIED: ZIP listing] |
| 2025-Q3 | `7138b2bfabc7` | 115 | CVE_ENT | `43dd74055f8d4c934c5101b68f70065517f4a4b538d8230592e273b4c0ec6cbe` | No SDEM bitácora member found. [VERIFIED: ZIP listing] |
| 2025-Q4 | `e4d4284cc992` | 115 | CVE_ENT | `43dd74055f8d4c934c5101b68f70065517f4a4b538d8230592e273b4c0ec6cbe` | No SDEM bitácora member found. [VERIFIED: ZIP listing] |
| 2026-Q1 | `429c288af46e` | 115 | CVE_ENT | `43dd74055f8d4c934c5101b68f70065517f4a4b538d8230592e273b4c0ec6cbe` | No SDEM bitácora member found. [VERIFIED: ZIP listing] |
| 2026-Q2 | `9ef8877c363f` | 115 | CVE_ENT | `43dd74055f8d4c934c5101b68f70065517f4a4b538d8230592e273b4c0ec6cbe` | No SDEM bitácora member found. [VERIFIED: ZIP listing] |

All eight bundled `cs_p14_c.csv` members have SHA `b521d2b5a07e3471da1bd6792183bb2c6864a38e022f74a6a919990c49f4a871`. Catalog numeric keys `31300/32100/33100` map to Ciencias políticas/Comunicación y periodismo/Derecho; the SDEM dictionaries declare `CS_P14_C` length 6. Validate digit-only and unique mapping, then `zfill(6)` to `031300/032100/033100`; `999999` means unspecified. Do not silently map absent codes. [VERIFIED: eight bundled catalogs and dictionaries]

At 2025-Q3, `AGEB/ENT/LOC/MUN` are replaced by `CVE_AGEB/CVE_ENT/CVE_LOC/CVE_MUN`, and `CVEGEO` appears; all eight headers had no duplicates. Validate geography alias per period and review conceptual equivalence separately. [VERIFIED: eight header diffs] The 2024-Q3 SDEM bitácora has four `cs_p14_c` corrections (SHA `cc3101c01a94cd7e9e810f82bc1cd2d49f3cf867d4ee5fc9e0761f6e283d565e`); Q4 has five `cs_p14_c`, one `par_c`, one `cs_p20a_c`, two `cs_p20b_c` (SHA `4716ded92c64ae5053e1f20c6d5df188eed8bf14e503ae88a86e7321cf4062e5`). Both logs date changes 2025-05-27 and state the dataset was replaced. [VERIFIED: bundled bitácoras]

Metadata catalog/dictionary decoded as UTF-8 without replacements; the first 1 MB of 2026-Q2 person CSV did not decode as UTF-8, although the ASCII header did. The exact person-row encoding was not established across full files; Phase 2 must audit it and preserve raw bytes. [VERIFIED: bounded byte probe] [ASSUMED: exact person-row encoding]

## Architecture Patterns
Flow: approved registry → verified current ZIP/receipt → exact metadata members → validated codes/revisions/aliases → versioned source inventory → population/denominator rules → strict v2 contract → Phase 2. A failed current or ambiguous member blocks downstream inventory. [VERIFIED: acquisition code; CONTEXT.md]

**Named populations:** `national_15_plus_context` uses normalized `R_DEF=00`, `C_RES∈{1,3}`, `15<=EDA<=98`, with 98 explicitly “age unspecified,” for official-context benchmarks. `completed_professional_known_age` uses same response/residence, `15<=EDA<=97`, `CS_P13_1=07`, `CS_P16=1`; report exclusions for technical/incomplete/postgraduate, unknown age/completion and unknown field. [VERIFIED: CONTEXT.md; SDEM dictionaries] [CITED: https://www.inegi.org.mx/rnm/index.php/catalog/1121/variable/F42/V5657?name=EDA]

**Denominators:** For each period keep observed eligible n, valid-response n, unknown/excluded n by reason, and weighted denominator as distinct fields. `sample_size` is observed n of the relevant valid denominator, never `sum(FAC_TRI)` or effective n. `ING7C=6` means no income; `ING7C=7` is unspecified; `INGOCUP=0` alone cannot establish zero wage. Income-positive-known denominators exclude no-income/unspecified states and must never describe all occupied persons. Numeric estimators remain Phase 2. [VERIFIED: CONTEXT.md; eight dictionaries; ENOE-METHOD-REVIEW.md]

**Strict v2 grain proposal:** `(source_snapshot_id,population_id,field_of_study_id,occupation_id,industry_id,geography_id,recorded_sex_id,period_id,metric_id,method_id)`; use explicit `all` aggregation IDs and `unknown` categories, reserving JSON null for unavailable values. Require unique grain, resolvable refs, `additionalProperties:false`, and method/design/version, `sample_size`, weighted denominator, support, SE/CV/CI method/level, singleton policy, status/reason, unit/price basis and evidence. Keep `estimate` diagnostic and `value` public separate; public allowlist strips estimate and revealing intervals/SE when suppressed. Preserve v1 schema/tests unchanged; Phase 2 accepts numerical precision. [VERIFIED: CONTEXT.md; docs/CONTRACT.md] [ASSUMED: discretionary ID spellings/property grouping]

## Don't Hand-Roll
Use `resolve_snapshot` for byte/receipt verification and `jsonschema` plus semantic checks for v2. Do not build a second downloader, guess classification bridges from text, or let renderers fall back to diagnostic `estimate`. [VERIFIED: acquisition/quality code; AGENTS.md]

## Common Pitfalls
| Pitfall | Planner gate |
|---|---|
| First CSV matching `sdem` can select 2024 bitácora. [VERIFIED: ZIP listing] | Exact canonical path, unique match, negative extra-CSV fixture. |
| A universal `ENT` parser fails at 2025-Q3; header alias is not automatically concept equivalence. [VERIFIED: header diff] | Per-period header manifest and explicit review. |
| Unchecked integer code conversion loses leading zero or invents field. [VERIFIED: catalogs] | Six-digit normalized key, catalog membership and unknown coverage tests. |
| `EDA=98` described as 98 years or `INGOCUP=0` as zero wage. [VERIFIED: dictionaries; method review] | Sentinel/denominator tests and visible unknown states. |
| Historical success or suppressed estimate leaks as current/public. [VERIFIED: acquisition code; CONTEXT.md] | Fail-closed eight-current check and central public projection tests. |

## Code Examples
```python
# Source: brujula/acquisition.py; eight offline resolutions.
from pathlib import Path
from brujula.acquisition import resolve_snapshot
raw_zip, receipt = resolve_snapshot("enoe_2026_q2", Path("artifacts/enoe"))
assert receipt["status"] == "SUCCEEDED"
# Read exact declared member paths from raw_zip; never extract or publish rows.
```
```python
# Source: eight bundled study catalogs and SDEM dictionaries.
def cmpe_key(raw: str) -> str:
    if not raw.isascii() or not raw.isdigit() or not 1 <= len(raw) <= 6:
        raise ValueError("invalid CMPE catalog key")
    return raw.zfill(6)
assert cmpe_key("31300") == "031300"
```

## State of the Art
Current package bytes show `ENT` through 2025-Q2 and `CVE_ENT` from 2025-Q3; a period-aware manifest is required. V1's ENOE extension is marked inactive, so v2 is a separate researched interface, not a loosening of v1. [VERIFIED: ZIP headers; docs/CONTRACT.md]

## Assumptions Log
| # | Assumption | Risk |
|---|---|---|
| A1 | Exact v2 ID names and property grouping above are discretionary. [ASSUMED] | Low; preserve grain and semantics. |
| A2 | Person-row encoding beyond bounded probe is unknown. [ASSUMED] | Medium; Phase 2 loader must audit before numeric reads. |

## Open Questions
1. **RESOLVED for Phase 1 by explicit routing, not by asserting equivalence:** inventory records the verified `ENT`/`CVE_ENT` alias and `concept_equivalence_review=REVIEW`; Phase 3 ANA-03 must establish the source/concept signature before allowing a temporal delta. Metadata equivalence alone never opens that gate. [VERIFIED: eight dictionaries/header diff; ROADMAP.md]
2. **RESOLVED for Phase 1 by explicit routing, not by asserting decoding correctness:** Phase 1 reads metadata as verified UTF-8 and records person encoding as unverified; Phase 2 STAT-01/06 must audit selected numeric bytes and every income state over the full pinned files before numerical acceptance. Phase 1 does not ingest person observations. [VERIFIED: byte probe; ROADMAP.md]

## Environment Availability
Python 3.12.13, pytest 9.0.3, jsonschema 4.26.0 and all eight cached ZIPs were available locally. No new service, runtime, package or network call is required for the Phase 1 inventory. [VERIFIED: local CLI; eight offline resolutions]

## Validation Architecture
`nyquist_validation=true`; `pytest` is configured in `pyproject.toml`. Quick existing command: `.venv/Scripts/python.exe -m pytest tests/test_acquisition.py tests/test_quality.py -q`; full command: `.venv/Scripts/python.exe -m pytest -q`. Existing acquisition and quality tests were inspected, not rerun for this research-only document. [VERIFIED: config; tests; pyproject]

| Requirement | Needed test / command |
|---|---|
| SRC-01/02 | Existing `tests/test_acquisition.py`; add inventory integration that resolves all eight offline and fails closed if one current is FAILED. |
| SRC-03/04 | New `tests/test_source_inventory.py`: exact member/header/hash/correction metadata, extra-CSV rejection, public metadata excludes person rows and has terms/receipt dates. |
| CTR-01 | New `tests/test_research_contract.py`: strict grain/refs/states/public projection and unchanged `tests/test_quality.py` v1 regression. |
| CTR-02 | New `tests/test_population_rules.py`: response/residence, 07/08/09, 97/98/99, `999999`, `ING7C` states and observed denominators. |

Wave 0: create the three focused test files with synthetic fixtures. Per-task run affected tests; per-wave and phase gate run the full suite. Do not full-scan person files to verify the metadata contract. [VERIFIED: AGENTS.md; phase scope]

## Security Domain
`security_enforcement=true` (ASVS level 1). V2 authentication and V3 sessions do not apply because there is no service; V4 is local raw/public boundary; V5 input validation covers approved host/URL, SHA, ZIP paths/size, exact members, codes, schemas and refs; V6 uses stdlib SHA-256 integrity, without custom cryptography. Threats: ZIP traversal/decompression bomb, off-host redirect/HTML response, stale current, raw person publication and suppressed-value leakage. Use existing ZIP/redirect checks plus metadata/public-projection gates. [VERIFIED: config; AGENTS.md; acquisition code]

## Sources
Primary: eight pinned ZIPs/receipts and `data/catalog/enoe-snapshots.json`; `brujula/acquisition.py`, `brujula/resources.py`, `brujula/quality.py`, v1 schemas/tests and `docs/CONTRACT.md`. [VERIFIED: local inspection]
Official: [INEGI terms](https://www.inegi.org.mx/inegi/terminos.html) consulted this session; [ENOE 2025 RNM](https://www.inegi.org.mx/rnm/index.php/catalog/1121) and [2024 dictionary](https://www.inegi.org.mx/rnm/index.php/catalog/1016/data-dictionary/F37) appeared in official search; `docs/research/ENOE-METHOD-REVIEW.md` links further official variable/method documents. [CITED: https://www.inegi.org.mx/inegi/terminos.html] [CITED: https://www.inegi.org.mx/rnm/index.php/catalog/1121]
Low-confidence gap: exact person-row encoding; no unverified package name or compliance claim is needed. [ASSUMED]

## Metadata
**Confidence:** stack HIGH; architecture HIGH; eight-package inventory HIGH; concept semantics MEDIUM; person encoding LOW. **Valid until:** recheck if registry, official edition or pinned hashes change; otherwise 2026-10-22 for this immutable inventory. [VERIFIED: local registry/receipts]
