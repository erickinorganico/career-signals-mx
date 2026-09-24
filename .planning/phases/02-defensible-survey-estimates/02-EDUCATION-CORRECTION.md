# Education and age coverage correction

Status: implemented and locally verified on 2026-09-22.

The exact `CS_P13_1` catalogs from all eight approved snapshots were read from
the ZIPs resolved by `brujula.acquisition.resolve_snapshot`. The aggregate
evidence is recorded in `docs/evidence/education-catalog-review.json`; no
person rows were decoded or exported. Every catalog labels code `0` as
`Ninguno` and `99` as `No sabe`.

`classify_eligibility` now treats catalog levels `0` through `5` as
`other_education`. Blank, `-1`, and `99` remain `unknown_education`; completion
`-1` is likewise `unknown_completion`, matching adapter normalization. The
professional cohort selector is unchanged (`CS_P13_1=07` and `CS_P16=1`).
`_population_coverage` reports education exclusions only for that cohort, keeps
national EDA 98 operationally included, and counts missing/`-1` age as unknown
rather than under 15. Its under-15 mask is limited to `0 <= EDA < 15`.

Observations that do not exclude all-field membership, including missing study
field and national EDA 98, are retained in `observed_category_counts`; actual
population/domain exclusions remain under `exclusions`.

The prior audit classification is retained as history in the evidence JSON;
this correction does not erase the earlier finding. Focused regressions cover
known zero, missing/`-1`/`99` education, EDA 14/15/98/99, national versus
professional EDA 98, and coverage/classifier parity. Metric masks and numerical
formulas are unchanged.
