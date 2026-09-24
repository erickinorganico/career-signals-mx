# Report layout preflight

Prepared 2026-09-23 by an independent read-only review for Plan 04-04. These are implementation recommendations, not rendered visual acceptance. Cardinalities below were read from the accepted historical Phase 3 packet only to size layout; Plan 04-04 must consume the newly accepted installed packet after 04-02.

## Figure and profile coverage

The current nine declared figure groups have 6, 9, 72, 12, 32, 115, 1, 1 and 1 records. The other-fields group has 115 additional official field codes, or 118 including the three focal fields. Its historical cells include 84 REVIEW and 31 UNKNOWN. The state figure links 32 Derecho employment records. Separately, latest state profiles contain 32 entities × four field groups × 23 metrics = 2,944 cells. Do not treat the other 96 field/entity availability cells as extra points in the 32-record figure.

## Preserve full content at readable size

Generate all plots, their semantic tables and print panels from one ordered typed figure specification. Keep all nine declared figure keys and the exact paired canonical SVG/PNG files. A 115-row point plot must not be squeezed onto one A4 page. Order by official classification code, place codes on the axis, and keep full official names, nulls, status and reasons in the semantic table.

For screen HTML, place the full-height canonical plot in a labeled bounded scroll container. For print, emit inline SVG panel views from the same point specification, approximately 14–16 rows per panel, with repeated figure key, panel number, axis/unit and source caption. These are representations of the existing figure, not new analytical keys or additional external asset files. Keep panels together at page breaks; determine actual row height from rendered glyph bounds. Give each inline SVG its own deterministic internal IDs to prevent clip-path collisions. The union of panel point IDs, values and states must equal the canonical SVG/PNG point set exactly, with no duplicates or omissions.

The 32 linked state points can use two 16-row print panels. Render the full 32×4 availability/status table separately with repeated headers and explicit unavailable reasons. Keep the 23 metrics and full focal profiles in joined detail/appendix tables and all public exports. Full machine-readable records need not become thousands of narrative rows.

Use short numbered evidence links in the narrative and a keyed evidence appendix with exact full v2r/v2c/v2k identifiers, one unbroken identifier per line at approximately 8.5–9 pt Sans across the available A4 content width. Do not hide required evidence in closed details or print-hidden elements. Compare extracted PDF full identifiers, public quantities and states with the shared HTML/Markdown document. Screen-only canonical graphics and print-only panel views must not create duplicate evidence counts.

## Required actual checks

This approach remains conditional on actual WeasyPrint rendering. Inspect mobile, desktop, 200% enlargement and A4 pages for plot label size, page transitions, repeated captions/headers, evidence tokens, full official names and whole-page overflow. Verify paired asset/panel/table value parity, source links and readable null reasons. The existing 04-EDITORIAL-SPEC and 04-04-PLAN remain authority; this preflight does not reduce scope or certify accessibility.
