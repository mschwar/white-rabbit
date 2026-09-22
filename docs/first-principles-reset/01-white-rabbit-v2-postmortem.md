# White Rabbit v2 Postmortem

Created: 2026-06-03

## Bottom Line

White Rabbit v2 did not fail because the north star was wrong. The current north star says the near-term launch wedge is source-assisted research, not fully autonomous broad search, and that White Rabbit's first job is to beat the manual public-source workbook workflow. That thesis still matches the evidence.

The failure was second-system layering: a simple v1 lead-generation demo became a Next.js/FastAPI/Postgres rebuild with gates, prompt loops, tiers, audits, assignment locks, and remediation branches before the product consistently produced useful checked lead workbooks.

Sources: `docs/00-product-northstar.md`, `docs/12-reset-gated-implementation-plan-2026-05-10.md`, `STATUS.md`, `docs/02-stack.md`, `audits/raw/zero-trust-2026-05-10/evidence-ledger.md`.

## What Still Holds

- The product should turn a sales target plus public-source evidence into an exportable research workbook of validated leads, manual-lookup rows, not-found rows, and transparent evidence. Source: `docs/00-product-northstar.md`.
- The core loop is target -> source-assisted public-web research -> field-validated rows -> evidence review -> export. Source: `docs/00-product-northstar.md`.
- Missing contact information can still be useful when name, title, organization, source, and next action are clear, but it must not be marked CRM-ready. Source: `docs/00-product-northstar.md`.
- The pipeline contract already points away from generic autonomous search and toward accepted or gathered public-source evidence, source maps, rosters, staff pages, PDFs, and sales-first exports. Source: `docs/13-pipeline-orchestrator-contract-2026.md`.

## What Failed

The reset machinery grew faster than the product truth.

- `STATUS.md` and `docs/12-reset-gated-implementation-plan-2026-05-10.md` record waves, reset gates, R-features, subfeatures, Prompt A/B/C loops, assignment locks, and audit branches. That structure made coordination possible, but it also made the product hard to reason about.
- The current gate remains product-red. The latest tracked state says Arizona produced a valid timed run/export/close with 2 READY contact-supported rows, but did not prove 6-of-8 named-account quality; sampled precision remained below the gate floor at persona `0.158`, organization `0.421`, source `0.447`, and contact `0.184`; and manufacturing still lacked a valid current product artifact. Sources: `STATUS.md`, `docs/reset-current-assignment.json`.
- The documented RG6 state blocks yellow/green claims, public SaaS work, account/org/billing work, and Thomas/Lee dogfood expansion. Sources: `STATUS.md`, `docs/reset-current-assignment.json`.
- The stack itself is larger than the current proof demands: Next.js 16, React 19, Tailwind 4, FastAPI, SQLAlchemy, Alembic, Postgres, Vercel, Fly, managed Postgres, internal tokens, and shared-password auth. Source: `docs/02-stack.md`.
- `docs/02-stack.md` still contains stale branch-workflow language saying reset work runs on `rebuild/validated-leads-loop`, while ADR-024 and `docs/12` say `main` is the integration branch. That is a small example of documentation authority drift. Sources: `docs/02-stack.md`, `docs/03-decisions.md`, `docs/12-reset-gated-implementation-plan-2026-05-10.md`.

## What Worked Despite the Mess

Source-assisted proof kept showing up as the useful path.

- ADR-019 pivoted toward the April New Mexico school-district IT package as a manual-oracle benchmark: public rosters, staff pages, source URLs, verified rows, manual-lookup rows, blocker notes, and sales-first export. Source: `docs/03-decisions.md`.
- R09D-R09H proved the offline workbook pattern; later work proved a live source-assisted route, but not enough to clear the broader dogfood gate. Sources: `STATUS.md`, `docs/12-reset-gated-implementation-plan-2026-05-10.md`.
- Lee and Thomas's Gmail evidence says the same thing in plain operator language: direct person contacts matter, company-only output is weak, a GPT-style list can be a useful seed, and the product must outperform the seed by checking and exporting it honestly. Sources: `GMAIL-LEE-01`, `GMAIL-THOMAS-01/02/03` in `audits/raw/zero-trust-2026-05-10/evidence-ledger.md`; private index at `/Users/mschwar/Documents/white-rabbit-private/lee-reset/index.md`.

## Decision Forced by the Evidence

The next product should not be another autonomous-lead-finder rebuild.

The next product should be a source-assisted concierge automation tool for Lee-style work:

1. Accept a customer bucket, seed list, source pack, rough GPT output, or operator prompt.
2. Gather public sources and show the search/work trail.
3. Extract rows into a workbook shape.
4. Verify every CRM-ready claim.
5. Preserve manual-lookup and not-found rows instead of hiding them.
6. Export a sales-first CSV/workbook.
7. Help the operator continue, correct, and deliver the artifact.

That is smaller than v2 and closer to what the evidence says works.

## Non-Goals for the Reset

- No new gate system.
- No account/org/billing/public SaaS work.
- No new autonomous broad-search benchmark suite.
- No revival of the v2 Prompt A/B/C loop as the planning interface.
- No edits to `/Users/mschwar/Documents/proxy-lead`.
