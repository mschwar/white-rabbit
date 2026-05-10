# 07 - UI / UX / Copy

**Verdict:** visually polished but cognitively noisy.

## Live Screen Findings

Screenshots:

- `audits/raw/zero-trust-2026-05-10/screenshots/desktop-scout-initial.png`
- `audits/raw/zero-trust-2026-05-10/screenshots/desktop-scout-healthcare-results-complete.png`
- `audits/raw/zero-trust-2026-05-10/screenshots/desktop-evidence-drawer.png`
- `audits/raw/zero-trust-2026-05-10/screenshots/desktop-full-export-ready.png`
- `audits/raw/zero-trust-2026-05-10/screenshots/mobile-scout-initial.png`

The first screen says "Find source-backed prospects", then immediately introduces Scout/Full, search usage, query quota, rows remaining, and a location filter. On `/scout`, the default query is Phoenix while default location is New Mexico.

The results screen organizes rows into large bucket sections. This makes internal validation visible, but it pushes the actual CRM fields apart. A salesperson wants organization, location, name, role, email, phone, source, and why-this-person. The current layout asks them to parse implementation state first.

The evidence drawer is useful, but it arrives after the UI has already elevated a bad row. In the live healthcare run, the drawer showed that Mike Mehta's title was unsupported and contact was missing, but the row still carried high Fit/Evidence badges and a large cold-email-style note.

## Copy Problems

- "Find source-backed prospects" overpromises when 0 rows are usable.
- "Evidence 100%" is misleading when title/name/contact are unsupported or missing.
- "Search usage" is internal meter copy and should not dominate the operator screen.
- "Full run saved for internal review" is useful for Matt, not Thomas/Lee.
- Feedback buttons on every row imply the operator is QA-ing the app, not prospecting.

## Required UX Reset

Primary UI should be:

1. Search box.
2. Run button.
3. Compact status: searched, found, usable, needs review.
4. Table with CRM fields first.
5. Evidence/dossier panel for the selected row.
6. Export.

Hide:

- Scout/Full modes.
- quota cards unless nearing cap,
- score sort controls until scores are trusted,
- feedback/correction controls unless in review mode,
- recipes/batch/Friday/scoreboards/operator-minute controls from primary path.
