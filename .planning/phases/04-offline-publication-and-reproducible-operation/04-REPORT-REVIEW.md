# Report implementation review

2026-09-23. Root review of the first renderer draft at `c602556`, before PDF and
visual acceptance. This is a working review, not a verdict on the eventual
Plan 04-04 implementation. The executor has received the findings and is
correcting them in its owned files. Closure requires source/test and actual
artifact readback; a promised fix does not close a finding.

| ID | Initial finding | Required evidence for closure | State |
|---|---|---|---|
| R01 | National, focal, sex and trend plots share one numeric scale across percent and nominal MXN. Null points are placed at data coordinate zero. | Separate metric/unit axes or panels within the same canonical figure; unavailable marks outside numeric coordinates; gap-aware ordered trends; exact figure point membership/value tests. | Open |
| R02 | Mandatory report tests read the ignored real packet directly. | Portable independently pinned synthetic fixtures with explicit synthetic labels; separate real acceptance; clean-source run without `.cache` data. | Open |
| R03 | Mixed-population and recorded-sex tables omit those dimensions. | Explicit population/sex row labels or clearly separated homogeneous tables; exact universe and evidence keys retained. | Open |
| R04 | Coverage section contains generic prose only; evidence appendix does not include all profile/detail rows printed elsewhere. | Accepted coverage counts/reasons with overlapping profile appearances identified; full cited-row/key union and complete 23-metric profiles. No invented exclusion count. | Open |
| R05 | Print CSS hides canonical plots before print panels exist and uses 6.7/5.6 pt dense tables. Long identifiers break across lines. | Complete canonical/print-panel point union, readable compact tables, short evidence links and full unbroken appendix identifiers; actual A4/mobile/native-zoom inspection. | Open |
| R06 | Font staging compares against a freshly computed source hash only. | Independent reviewed font/notice hashes enforced on both package and copied bytes; changed package/staged file negatives and actual PDF embedding. | Open |
| R07 | Standalone synthetic figures lack a synthetic notice; the cover says build date is unavailable. | Explicit synthetic notice in every applicable standalone figure; actual build date separate from observation window and excluded from canonical reproducibility identity. | Open |

The real expected readback was derived independently from the accepted packet
at `.cache/research/phase4-report-review/expected-report.json` (ignored
preparation, not publication acceptance). The source packet SHA-256 is
`71d9fb7d6ceb20cff39a1a10f8428bcb239629e2e723b6e001816bd6d564bce3`;
its analytical digest is
`15f5bdc0fb366f9b3ae75c1c0b096aed1f7b1f4e7f8b71b514f62133ea8dddca`.
The validated publication model digest is
`ff4f7ef1c34927812c15488d46220edd2cebb55378c264827c15b378970a385e`.
Nine figure groups contain 6, 9, 72, 12, 32, 115, 1, 1 and 1 records;
the trend group has one unavailable point and the other-fields group has 31.
Those missing values must remain unavailable throughout every representation.
