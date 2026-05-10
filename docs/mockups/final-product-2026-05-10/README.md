# White Rabbit Final Product Mockups - 2026-05-10

**Status:** Inspection artifact before reset implementation.
**Source of truth:** `docs/00-product-northstar.md` and `docs/12-reset-gated-implementation-plan-2026-05-10.md`.
**Product code changed:** No.

Open `index.html` in a browser to inspect the proposed final operator experience before Prompt A starts implementation.

## What This Mockup Locks

- One primary search input. No Scout/Full mode switch in the operator path.
- Broad runs show high-volume tier distribution: 50-300+ categorized candidates where the market supports it, with the strict usable tier separated from everything else.
- CRM-useful result fields come first: organization, location, lead, title, email, phone, source, and row status.
- Evidence is always one action away and shows field-level support for name, title, organization, contact, and source.
- Export is a sales artifact first and an audit artifact second.
- Review, organization-only, not-found, and failed rows stay visible with concise reasons instead of masquerading as high-trust usable leads.
- Recipe, batch, scoreboard, quota, and implementation-detail surfaces are absent from the primary path.

## Screens Included

- `Search`: final first screen and product bar.
- `Results + Evidence`: compact 18-row table with evidence dossier.
- `Export`: sales-first CSV preview with audit columns later.
- `Mobile`: compact row-card treatment for phone-width review.

Rendered screenshots are stored in `.gstack/qa-reports/screenshots/final-product-mockups-2026-05-10/` for quick inspection without running the HTML locally.

## Inspection Questions

- Does this feel like something Thomas or Lee would understand without Matt explaining the product?
- Is the tier distribution glanceable enough for hundreds of surfaced candidates without becoming noisy?
- Are the CRM fields front-loaded enough?
- Is the evidence panel visible enough without stealing the whole screen?
- Are the non-actionable blockers obvious enough to understand in seconds?
- Should the final product keep this dark terminal-like feel, or get a quieter light/neutral treatment?

## Implementation Boundary

This is not production code. It is a visual contract for R10-R13 and a gate artifact for Prompt C review. Any implementation agent changing the operator UI should compare against this mockup before merging.
