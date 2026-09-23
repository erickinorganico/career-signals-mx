# Font and contrast asset audit

Checked 2026-09-23 against project Matplotlib 3.10.8. This verifies local candidates for the Phase 4 editorial contract; final HTML/PDF rendering and asset sealing remain pending.

## Exact local candidates

Source directory: `.venv/Lib/site-packages/matplotlib/mpl-data/fonts/ttf/`. All four files contain every tested Spanish character, punctuation and numeric glyph. FontTools reports OS/2 fsType=0 for each; the complete license remains authoritative.

| File / PostScript name | SHA-256 | Bytes |
|---|---|---:|
| DejaVuSans.ttf / DejaVuSans | `3fdf69cabf06049ea70a00b5919340e2ce1e6d02b0cc3c4b44fb6801bd1e0d22` | 756072 |
| DejaVuSans-Bold.ttf / DejaVuSans-Bold | `b184b89e3c1075f22f6b71575b6fc20d4972b3cfd3b23322ca6fd596dcaef167` | 704128 |
| DejaVuSerif.ttf / DejaVuSerif | `107244956e9962b9e96faccdc551825e0ae0898ae13737133e1b921a2fd35ffa` | 379740 |
| DejaVuSerif-Bold.ttf / DejaVuSerif-Bold | `c3753f2ed6bc673f15846dc45addbeb3b9c872f32fb18fd53a21f1bef1ed7676` | 355692 |

Font name-table version: Version 2.35. Tested characters: `áéíóúüñÁÉÍÓÚÜÑ¿¡.,:;%–−0123456789`. The local notice `LICENSE_DEJAVU` has SHA-256 `d75938dec098f06f0ac3c00853065d94f020be1c3c62ef1dc2975ba15b4d9b0e`.

## Redistribution and use

The packaged Bitstream/Arev notice permits use and redistribution with its complete copyright, trademark and permission notices retained. Modified fonts have reserved-name restrictions; font files cannot be sold alone. DejaVu changes are identified as public domain. Retain the original four files and the entire `LICENSE_DEJAVU` in the package and report assets; do not relicense them as repository MIT. Primary reference: [DejaVu license](https://dejavu-fonts.github.io/License.html).

Use DejaVu Sans regular/bold for prose, tables and plots, and DejaVu Serif regular/bold for editorial headings. Bind local @font-face resources explicitly. No system Arial or network font is required. PDF subsetting and actual embedding must be inspected in the final PDF; an fsType value alone does not prove renderer behavior.

## Computed contrast on white

| Foreground | Ratio against #FFFFFF | Normal-text 4.5 threshold |
|---|---:|---|
| #172B3A | 14.552207:1 | PASS |
| #405464 | 7.864735:1 | PASS |
| #145A66 | 7.823933:1 | PASS |
| #A34F23 | 5.675724:1 | PASS |

Calculation: sRGB channels are linearized with the 0.04045 threshold; luminance weights are 0.2126/0.7152/0.0722; contrast is (lighter+0.05)/(darker+0.05). Threshold comparisons use unrounded values. [W3C contrast minimum](https://www.w3.org/WAI/WCAG22/Understanding/contrast-minimum.html) specifies 4.5:1 for normal text and 3:1 for large text.

These four color pairs pass the normal-text threshold. This does not establish whole-document WCAG conformance. Verify actual CSS foreground/background pairs, links, gray unavailable states, focus outlines, figure lines and print rendering. Different series also need labels/shapes; color contrast against white does not prove the two series are distinguishable from each other.

## Final acceptance still required

Seal copied asset hashes and notice inventory; verify Spanish glyphs and font embedding in actual PDF; inspect chart labels at print size, long tables, mobile HTML and 200% zoom. Configure MPLCONFIGDIR inside the writable project/output cache, not the user profile, for reproducible local/CI operation.
