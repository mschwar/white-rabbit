# White Rabbit Final Product Mockups - 2026-05-10

**Status:** Live-demo inspection artifact before reset implementation.
**Source of truth:** `docs/00-product-northstar.md`, `docs/12-reset-gated-implementation-plan-2026-05-10.md`, and `docs/13-pipeline-orchestrator-contract-2026.md`.
**Product code changed:** No.

Open `index.html` in a browser to inspect the proposed final operator experience before Prompt A starts implementation. Demo-facing copy intentionally avoids internal people, agent prompts, gate labels, sprint labels, and implementation machinery.

## What This Mockup Locks

- One primary search input. No Scout/Full mode switch in the operator path.
- Broad runs show high-volume tier distribution: 50-500+ categorized candidates where the market supports it, with the strict usable tier separated from everything else.
- Visible operator buckets are `READY`, `REVIEW`, `ORG-ONLY`, and `NOT FOUND`.
- CRM-useful result fields come first: organization, location, lead, title, email, phone, source, and row status.
- Evidence is always one action away and shows field-level support for name, title, organization, contact, source, and contradictions.
- Export is a sales artifact first and an audit artifact second.
- Review, organization-only, not-found, and failed rows stay visible with concise reasons instead of masquerading as `READY` leads.
- Recipe, batch, scoreboard, quota, and implementation-detail surfaces are absent from the primary path.
- Low-signal runs still show returned rows, but clearly warn that the result set is below the expected broad-query coverage.

## Screens Included

- `Search`: simplified first screen with pipeline flow.
- `Results + Evidence`: high-volume distribution, filters, compact table, and evidence dossier.
- `Export`: sales-first CSV preview with audit columns later.
- `Mobile`: compact row-card treatment for phone-width review.
- `Low Signal`: below-threshold run state with broadening guidance.

Rendered screenshots are stored in `.gstack/qa-reports/screenshots/final-product-mockups-2026-05-10/` for quick inspection without running the HTML locally.

## Inspection Questions

- Does this feel like a live demo screen a buyer can understand without internal context?
- Is the tier distribution glanceable enough for hundreds of surfaced candidates without becoming noisy?
- Are the CRM fields front-loaded enough?
- Is the evidence panel visible enough without stealing the whole screen?
- Are the non-actionable blockers obvious enough to understand in seconds?
- Does the low-signal state make it clear whether to broaden the search or inspect the few returned rows?
- Should the final product keep this dark terminal-like feel, or get a quieter light/neutral treatment?

## Implementation Boundary

This is not production code. It is a visual contract for R10-R13 and a gate artifact for Prompt C review. Any implementation agent changing the operator UI should compare against this mockup before merging.
