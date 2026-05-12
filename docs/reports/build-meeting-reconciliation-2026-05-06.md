# Build / Meeting Reconciliation Report — 2026-05-06

> **Status:** Historical Record. This document preserves evidence from the date it was written. Do not use it as the current work queue. Current product truth: `docs/00-product-northstar.md`; current state: `STATUS.md`; current reset execution: `docs/12-reset-gated-implementation-plan-2026-05-10.md`.


## Scope

This report checks the current `/Users/mschwar/Documents/white-rabbit` build against the Monroe St NE 8 meeting artifacts before turning the discussion into a new plan or sprint.

Evidence reviewed:

- `STATUS.md`
- `docs/00-context.md`
- `docs/01-model.md`
- `docs/02-stack.md`
- `docs/03-decisions.md`
- `docs/04-roadmap.md`
- `docs/05-reuse.md`
- `docs/meeting-notes/monroe-st-ne-8-transcript.md`
- `docs/meeting-notes/monroe-st-ne-8-minutes.md`
- `docs/meeting-notes/monroe-st-ne-8-executive-summary.md`
- Current git branch, diff, app/API/core code, and test/build output

This is intentionally a reconciliation report, not a sprint plan.

## Executive readout

The build is ahead of `STATUS.md` but behind the meeting expectation.

Code reality: Sprint 2 is already merged to `main`, and the active branch is `feature/sprint3-recipe-scoreboard`. There is uncommitted Sprint 3 scoreboard work that adds per-recipe aggregate metrics to the API and recipe library. Web tests, web production build, and API tests pass. Core tests currently have one environment-sensitive failure.

Product reality: the repo is still shaped as an internal operator workbench for Matt, Thomas, and Lee. That remains strategically correct, but the meeting introduced a more concrete Friday deliverable: a guarded lead-generation sandbox with 10 queries, 100 rows per query, 1,000 total rows, out-of-scope prompt redirects, practical export, and no lateral customer-data connection.

The main tension is that the roadmap says "no external self-serve product yet," while the meeting language drifts toward a customer/demo sandbox. The safest interpretation is: build the guarded sandbox mechanics for internal Lee/Thomas/Matt usage first, and do not give customers direct access until data isolation and access boundaries are explicit.

## Current build state

### What is merged

`main` points at `feat(sprint2): add recipe library and operator time logging (#6)`.

Merged product surface:

- Shared-password protected Next.js app.
- Scout mode: query UI, Next API proxy, FastAPI `/scout`, Tavily + OpenAI extraction, three scores, explanations, and metrics.
- Full mode: `POST /full` runs a larger query, stores recipe/run/lead records, returns saved IDs, and exposes a close-run operator-minute flow.
- Postgres-backed persistence with `recipe`, `recipe_run`, `lead`, and `lead_feedback` tables.
- Recipe library page with saved recipes and run history.
- Five feedback labels exist in the UI/API contract: `usable`, `wrong_persona`, `bad_source`, `bad_contact`, `duplicate`.
- Operator minutes are captured when a Full run is closed.

### What is in flight

The active branch is `feature/sprint3-recipe-scoreboard`.

Uncommitted Sprint 3 work currently adds:

- API aggregate helper `get_recipe_scoreboard(...)`.
- FastAPI endpoint `GET /recipes/{recipe_id}/scoreboard`.
- Next.js proxy route `GET /api/recipes/[recipe_id]/scoreboard`.
- Recipe library scoreboard UI for:
  - API cost spent.
  - Leads returned.
  - Usable leads.
  - Operator minutes.
  - Minutes per usable lead.
  - API cost per usable lead.
  - Feedback counts.
- Tests for the API endpoint and recipe library scoreboard rendering.

### Status doc drift

`STATUS.md` was stale at session start:

- It said the branch was `feature/sprint2-persistence-recipes`.
- It said Sprint 2 push/merge was still in flight.
- Actual state is `feature/sprint3-recipe-scoreboard`, with `main` already at the Sprint 2 merge commit.

This matters because future agents would otherwise pick up the wrong next task.

## Verification performed

Commands run:

- `npm test` in `apps/web`: passed, 8 test files / 16 tests.
- `npm run build` in `apps/web`: passed. Warnings remain for workspace-root inference and Next.js middleware deprecation.
- `uv run pytest tests -q` in `apps/api`: passed, 4 tests.
- `uv run pytest tests -q` in `packages/core`: failed, 1 failed / 4 passed.

Core test failure:

`tests/test_orchestrator.py::test_scout_raises_on_missing_openai_key` expects `OPENAI_API_KEY not found`, but this environment has an OpenAI key present, so the test goes through to OpenAI and fails with a model 404 for `gpt-4o-mini`. This is a test isolation issue more than a product behavior conclusion: the missing-key test must explicitly clear the env var.

## Meeting signal

The Monroe St NE 8 meeting turned the product discussion from broad possibility into a concrete sandbox shape.

Decisions and strong signals from the meeting:

- The initial experience should be a constrained lead-generation sandbox, not an unrestricted AI assistant.
- Start with 10 queries, 100 leads/rows per query, and 1,000 total output rows.
- Reject or redirect prompts outside lead generation.
- Steer users toward lead-list criteria: job title, vertical, industry, geography, and related search constraints.
- Current UI can stay mostly as-is if the guardrails are in place.
- Exports need to work for real sales workflows, including CSV/Excel-style output and validation/context fields.
- Customer data must not laterally connect across clients.
- The immediate focus is B2B lead generation and the Scotty/demo path.
- B2C ideas are real but phase two.
- Lee and Thomas need hands-on access by end of day Friday.
- Cost/pricing should be learned empirically from early capped runs.

## Reconciliation

| Area | Current build / roadmap | Meeting direction | Reconciliation |
|---|---|---|---|
| Product boundary | Internal-first operator workbench; no external self-serve. | Guarded sandbox usable for demo/trial. | Keep internal-first as the operating boundary. Build sandbox mechanics now, but do not assume direct customer access until access/data boundaries are explicit. |
| Run size | Scout 10-20, Full up to 100 leads. | 10 queries, 100 rows/query, 1,000 total rows. | Full already matches the per-query row cap. Missing: query-count ledger, total-row ledger, and reset/admin flow. |
| Prompt scope | Query field accepts any non-empty text. Orchestrator prompt is B2B telecom-oriented. | Reject or redirect non-lead-gen prompts. | Need server-side preflight guardrails before vendor calls. UI copy alone is not enough. |
| Output scope | Lead schema is strongly structured. | Output must remain lead-generation output. | Schema helps, but the API should still return explicit out-of-scope messages rather than spending on irrelevant prompts. |
| Export | HubSpot CSV export is deferred in roadmap. | CSV/Excel-style output with validation/context columns is near-term. | Export is now a real workflow requirement for Lee/Thomas/Scotty, even if it stays internal. This conflicts with the old defer-until-asked note. |
| Data isolation | One shared internal app; global recipe/run/lead tables. | No lateral connection across customer data. | Current schema is acceptable for three internal operators, but not for multiple customer sandboxes. Avoid customer direct access or add an explicit customer/session boundary. |
| Cost learning | Scoreboard and metrics measure cost/minutes. | Let capped runs reveal real cost. | Strong alignment. Scoreboard work supports this, but only after caps/guardrails prevent runaway usage. |
| B2C | Lee tests generalization, but roadmap stays B2B-first. | B2C/refinance/social targeting is phase two. | Aligned. Do not add B2C now. Capture as future strategy only. |
| Deployment/access | Deploy is deferred in docs. | Lee and Thomas need access by Friday. | If they need remote access, deployment is no longer deferred. If local access is acceptable, document the handoff path precisely. |

## High-impact gaps

### 1. Guardrails are now P0

Current validation only checks that the query is non-empty. The meeting asks for "not Jarvis" behavior: if someone asks for supply-chain advice or general AI help, White Rabbit should redirect them to lead-list criteria.

Minimum viable guardrail should live server-side, before Tavily/OpenAI spend:

- Accept lead-generation queries that include or imply target people/orgs.
- Encourage missing criteria such as title, vertical, industry, location, and company type.
- Reject/redirect broad advice, writing, strategy, code, general research, and non-lead-list outputs.
- Return a friendly structured message that the UI can show.

### 2. Sandbox caps are missing

The product has a Full run max of 100 leads, but it does not have the meeting's sandbox ledger:

- 10 query cap.
- 100 rows/query cap enforced as a hard response limit.
- 1,000 total rows cap.
- Reset/admin mechanism for Lee/Thomas.
- Cost/result summary per capped batch.

Without this, the app may be technically functional but not demo-safe.

### 3. Export moved from "later" to "near-term"

The meeting made export practical, not optional. Thomas wants to get lists into outreach tooling and see how the data was validated.

Minimum useful export should include:

- Contact/person fields.
- Organization fields.
- Email and email status.
- Source URL.
- Fit/Evidence/Contact scores.
- Gate status.
- Explanation / validation context.
- Query/recipe/run metadata.

This can remain an internal export. It does not need HubSpot polish yet.

### 4. Customer-data isolation is not designed

The current schema has no `customer_id`, `workspace_id`, `sandbox_id`, or tenant boundary. That matches the locked internal-first decision, but it does not satisfy customer sandbox separation if customers get direct access.

Until this is designed, customer access should be handled one of three ways:

- Matt runs customer work internally and exports deliverables.
- Separate database/environment per customer sandbox.
- Add a minimal explicit customer/sandbox boundary before any direct customer use.

The first option is most consistent with the current ADRs.

### 5. Feedback buttons likely need a wiring fix

The API saves leads to Postgres, but `FullResponse` returns the original core `Lead` objects. The core `Lead` model has no persisted database `id`, while the UI feedback buttons need `lead.id` to post to `/leads/{lead_id}/feedback`.

Observed consequence: after a Full run, the rendered feedback buttons can lack the database ID needed to submit feedback. This should be verified/fixed before claiming the feedback loop is fully usable.

### 6. Scoreboard is useful but should not outrank the Friday guardrails

The in-flight scoreboard work aligns with the empirical-learning direction from the meeting. It is not wasted.

However, if "Lee and Thomas access by end of day Friday" is the forcing function, the order should be:

1. Guardrails.
2. Caps / ledger / reset.
3. Export.
4. Scoreboard polish.
5. Sort controls.

That is a priority read, not a final sprint plan.

## Trajectory read

The strategic trajectory is still basically right:

- Do not turn the Scotty demo repo into the product.
- Keep White Rabbit v2 as the internal operator workbench.
- Keep Thomas as the primary usage signal.
- Keep recipes, provenance, and three visible scores as the product's differentiation.
- Keep public/customer self-serve out of scope until the kill/keep gate.

The meeting sharpens the near-term product from "operator workbench" into "guarded operator sandbox." That is a good constraint. It makes the product safer, easier to demo, and easier to price empirically.

The risky interpretation would be: "we now need a customer-facing sandbox." That would collide with ADR-003 and the roadmap's no-external-self-serve rule. The less risky interpretation is: "we need sandbox behavior inside the internal tool so Lee/Thomas can use it like a customer and report high-signal feedback."

## Recommended planning posture

Do not start the next sprint by expanding the product. Start by deciding the access boundary:

- Internal guarded sandbox only.
- Direct customer sandbox.
- Matt-fulfilled customer workflow with internal tool plus export.

Given the ADRs and current code, the strongest answer is: internal guarded sandbox plus Matt-fulfilled customer workflow. That preserves momentum without creating multi-tenant/auth/data-isolation debt.

Once that boundary is explicit, the next implementation slice should be small and operational:

- Server-side lead-gen prompt guard.
- Sandbox usage ledger.
- 100-row response cap.
- Reset/admin path for Lee/Thomas.
- CSV export with validation/context columns.
- Fix feedback IDs if needed.

Scoreboard can either land immediately after those or be completed if it is already nearly done, but it should not substitute for the meeting's guardrail/cap/export requirements.

## Open decisions before sprinting

1. Are Lee and Thomas accessing this locally, over a deployed internal URL, or through Matt-run sessions?
2. Is any external customer getting direct access before the kill/keep gate?
3. If yes, what is the minimal customer-data isolation boundary?
4. Is "10 queries / 100 rows / 1,000 rows" per customer, per shared app, per operator, or per reset window?
5. Who can reset a sandbox cap, and should resets be logged?
6. What export destination matters first: raw CSV, Excel, HubSpot-ready CSV, or all of the above?
7. What should count as a "query" for the cap: Scout only, Full only, both, failed guardrail attempts, or successful lead-producing runs?

## Bottom line

The build is not off-track, but the next useful slice is not generic Sprint 3 polish. The meeting creates a narrower operating requirement: make the current internal workbench behave like a safe, capped, lead-generation-only sandbox that Lee and Thomas can actually use.

That should be treated as a product-control layer over the existing Scout/Full/recipe foundation, not as a pivot into external self-serve SaaS.
