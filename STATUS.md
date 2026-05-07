     1|# STATUS
     2|
**Last updated:** 2026-05-07 by Codex
**Branch:** feature/full-lead-export
**Current sprint:** Sprint 4 follow-up — Full-run lead export on the Scout workspace
     6|
     7|> Update this file at the end of every session. It is the source of truth for "where we are."
     8|
     9|## What's done
    10|
    11|- Repo created at `/Users/mschwar/Documents/white-rabbit/`.
    12|- Directory structure scaffolded (`docs/`, `apps/web/`, `apps/api/`, `packages/core/`).
    13|- Bootstrap documentation written:
    14|  - `AGENTS.md` — agent entry point and rules.
    15|  - `README.md` — human intro pointing at AGENTS.md.
    16|  - `docs/00-context.md` — strategic background.
    17|  - `docs/01-model.md` — operator model, recipes, scores, run model.
    18|  - `docs/02-stack.md` — Next.js + Python + Postgres layout and conventions.
    19|  - `docs/03-decisions.md` — locked decisions (4 ADRs).
    20|  - `docs/04-roadmap.md` — Sprint 1 build slice and 90-day kill/keep gate.
    21|  - `docs/05-reuse.md` — explicit lift list from `/Users/mschwar/Documents/proxy-lead`.
    22|- .gitignore written.
    23|- git initialized and first commit made.
    24|- 'superskills' (v2.5.0) installed and linked in .gemini/skills.
    25|  - Repository cloned to .gemini/superskills-repo.
    26|  - ~150+ skills linked to workspace scope.
    27|  - Workflow rule added to GEMINI.md.
    28|- **Sprint 1: Scaffold `apps/web` (Next.js) completed.**
    29|- **Sprint 1: Scaffold `apps/api` (FastAPI + uv) completed.**
    30|- **Sprint 1: Core primitives (`packages/core`) lifted and adapted.**
    31|- **Testing framework bootstrapped for Web (Vitest/Playwright) and Python (Pytest).**
    32|- **Sprint 1: Scout core smoke harness added.** `packages/core` orchestrator now supports injectable search/client fakes, and the API has a verified `/scout` contract test.
    33|- **Sprint 1: Python import path bootstraps added** so `core` resolves from local package runs and `api.main` can import the shared core package.
    34|- **Sprint 1: Shared-password auth gate added in `apps/web`.** Login/logout routes, session-cookie middleware, a protected home shell, and a protected Scout shell are browser-tested.
    35|- **Sprint 1: Scout UI + Next.js API proxy wired.** The `/scout` page now posts to `POST /api/scout`, proxies to FastAPI `/scout`, and renders returned leads/metrics.
    36|- **Sprint 1: Scout filters now propagate end-to-end.** `apps/web` already forwards the payload, and `apps/api`/`packages/core` now pass request filters into search and prompt context.
    37|- **Sprint 1: Real Tavily search integration.** `packages/core/src/core/search.py` now uses direct HTTP API calls to Tavily (not httpx.AsyncClient, since tavily-python SDK is sync-only; we use `httpx.Client` in a sync wrapper callable from async orchestrator).
    38|- **Sprint 1: Real OpenAI extraction integration.** `packages/core/src/core/orchestrator.py` uses `AsyncOpenAI` with `beta.chat.completions.parse` and structured outputs (`response_format=LeadList`).
    39|- **Sprint 1: Email patterns lifted.** `packages/core/src/core/email_patterns.py` copied and adapted from `/proxy-lead/email_patterns.py` with relative imports to the new `Lead` model.
    40|- **Sprint 1: API error handling improved.** `apps/api/api/main.py` now distinguishes `OrchestratorError` (503 Service Unavailable) from unexpected exceptions (500 Internal Server Error).
    41|- **Sprint 1: Core test coverage expanded.** Added tests for missing-key and Tavily-failure error paths in `packages/core/tests/test_orchestrator.py`.
    42|- **Sprint 1: Scout live validation completed.** Verified end-to-end with real API keys: FastAPI `/scout` returns 3-4 real leads with three scores and metrics in ~15s. Browser QA confirmed the Scout workspace renders ranked lead cards with Fit/Evidence/Contact scores, gate status, explanations, and icebreakers.
    43|- **Sprint 1: Environment template files created.** `.env.example` files for root, `apps/api/`, and `apps/web/` to help future developers configure API keys and secrets.
    44|- **Sprint 2: Postgres persistence added.** Local PostgreSQL 16 is running via Homebrew; SQLAlchemy models and Alembic migration created `recipe`, `recipe_run`, `lead`, and `lead_feedback` tables.
    45|- **Sprint 2: Scout vs Full split implemented.** Scout remains quick/no-storage; Full stores recipe + run metadata and returns saved IDs.
    46|- **Sprint 2: Five-button feedback per lead implemented.** Leads now expose usable / wrong persona / bad source / bad contact / duplicate feedback buttons.
    47|- **Sprint 2: Recipe library page added.** `/recipes` shows saved recipes and run history.
    48|- **Sprint 2: Operator-time logging added.** Full runs now expose a close-run form that records operator minutes through `/api/runs/[run_id]/close`.
    49|- **Sprint 2: Browser QA completed for the new slice.** Verified Full run save UI, operator-minute close flow, and recipe library rendering in the browser.
    50|- **Sprint 2: Tests passing.** `npm run build` and `npm test` pass in `apps/web`; `pytest tests -q` passes in `apps/api`.
    51|- **Sprint 2 merged to `main`.** `main` and `origin/main` are at `feat(sprint2): add recipe library and operator time logging (#6)`.
    52|- **Sprint 3: Recipe scoreboard added and QA verified.** `/recipes` now shows per-recipe scoreboard metrics: leads returned, usable leads, API cost spent, operator minutes, and derived minutes/cost per usable lead. Browser QA on `localhost:3003` confirmed the recipe list, scoreboard tiles, and run history render correctly.
    53|- **Sprint 3: Sort-by-score controls added and QA verified.** `/scout` now lets the operator sort by original rank, Fit, Evidence, Contact, or pass/fail gate. Browser QA on `localhost:3004` confirmed the select control and sorted lead order.
    54|- **Sprint 3: Sort controls re-verified in browser.** Current QA pass confirmed the selector still works on the live workspace and produced `.gstack/qa-reports/qa-report-white-rabbit-2026-05-06-sort-controls.md`.
    55|- **Sprint 3: Friday recipe-review export added and QA verified.** `/recipes` now exposes a Friday export card with CSV download and printable markdown preview. Browser QA on `localhost:3005` confirmed the export builds and the review packet renders.
    56|- **Sprint 3 merged to `main`.** The scoreboard feature, docs updates, and QA report are merged and pushed.
    57|- **Sprint 3: Friday recipe-review export added and QA verified.** `/recipes` now exposes a Friday export card with CSV download and printable markdown preview. Browser QA on `localhost:3005` confirmed the export builds and the review packet renders.
    58|- **Sprint 3 merged to `main`.** The Friday export feature, docs updates, and QA report are merged and pushed.
- **Sprint 4: Batch/bulk workspace and API added.** Batch jobs and runs persist in Postgres, the API exposes `POST /batch`, and the web app now has a batch page, proxy route, and batch helpers/UI.
- **Sprint 4: Batch API tests passing.** `pytest tests -q` passes in `apps/api`.
- **Sprint 4: Browser QA completed.** Logged in to the web app, opened `/batch`, submitted a batch run, and verified the result card and run summaries render correctly.
- **Sprint 4 follow-up: Full-run lead export added.** Scout Full runs now build a downloadable CSV export with query, recipe, run metadata, scores, gate status, explanation, and validation context. Browser QA confirmed the export link renders in the live workspace.
## What's in flight

- `feature/full-lead-export` is pushed and ready for review/merge.

## Next concrete task

- Merge `feature/full-lead-export` to `main` after review, then pick up the next sprint slice from `docs/04-roadmap.md`.

## Open questions for Matt
    72|
    73|- Commercial arrangement with Lee and Thomas (free seats / revenue share / equity / content rights). Blocks the design-partner motion. **Not blocking Sprint 1 build, but blocks public usage.**
    74|- Cost-tracking source of truth: should live API cost figures be pulled from OpenAI/Tavily dashboards, or computed locally from token/call counts? Recommendation: compute locally per-run, reconcile weekly. See `docs/05-reuse.md` note on stale 2025 prices.
    75|- Access boundary for the Friday guarded version: local handoff, deployed internal URL, or Matt-run sessions?
    76|- Whether any external customer gets direct sandbox access before the 90-day kill/keep gate. If yes, customer-data isolation needs an explicit boundary first.
    77|- Sandbox cap semantics: is the 10-query / 1,000-row cap per operator, per customer, per shared app, or per reset window?
    78|- Export target: raw CSV, Excel-style CSV, HubSpot-ready CSV, or multiple formats?
    79|
    80|## Known issues / risks
    81|
    82|- Pricing constants in `packages/core/core/cost.py` updated to 2026-05 estimates. Verify with real dashboard data after first few runs.
    83|- Next.js 16 warns that `middleware.ts` is deprecated in favor of `proxy.ts`; auth currently works, but a rename is a follow-up if we want to eliminate the warning.
    84|- `packages/core` test isolation issue: `test_scout_raises_on_missing_openai_key` fails when `OPENAI_API_KEY` is present in the environment because it reaches OpenAI instead of exercising the missing-key branch.
    85|- Feedback buttons may not be fully usable after Full runs until persisted lead IDs are returned to the web UI; current core `Lead` objects do not include the database `lead.id`.
    86|- Current app has no server-side lead-generation prompt guardrail and no query/row usage ledger for the meeting's sandbox cap.
    87|
    88|## Session log
    89|
    90|| Date | Agent | Summary |
    91||------|-------|---------|
    92|| 2026-05-05 | bootstrap (Opus 4.7) | Repo bootstrapped. All 10 priority docs written. git init + first commit. Next: Sprint 1 scaffold. |
    93|| 2026-05-05 | api-scaffold (Opus 4.7) | Scaffolded apps/api and packages/core. Lifted and adapted code from proxy-lead. Passed health check tests. |
    94|| 2026-05-06 | scout-harness (gpt-5.4-mini) | Added injectable Scout smoke harnesses in core and API, fixed local import bootstraps, and verified core/API/web tests plus runtime imports. |
    95|| 2026-05-06 | qa (gpt-5.4-mini) | Browser-checked the homepage and docs path, captured screenshots, and found no browser-visible issues. |
    96|| 2026-05-06 | shared-password-auth (gpt-5.4-mini) | Added shared-password auth middleware, login/logout routes, and protected home/Scout shells. Browser-checked login, invalid-password, home, and Scout flows with screenshots. |
    97|| 2026-05-06 | qa (gpt-5.4-mini) | Browser-checked the shared-password login, sign-out, and Scout pages; tightened Scout query label spacing; updated QA docs and screenshots. |
    98|| 2026-05-06 | merge (gpt-5.4-mini) | Merged feature/shared-password-auth into main after QA verification and pushed the merge commit. |
    99|| 2026-05-06 | scout-api-proxy (gpt-5.4-mini) | Added the Scout Next.js query UI, `/api/scout` proxy route, and browser-backed error-path checks. Verified with Vitest and Next.js production build; live Scout browser QA remains blocked by the unknown shared password secret. |
   100|| 2026-05-06 | qa (gpt-5.4-mini) | Attempted browser QA on the Scout feature branch, captured the login gate state, and updated STATUS.md to note that successful end-to-end Scout verification is still pending valid shared-password access. |
   101|| 2026-05-06 | scout-core-real-integration (gpt-5.4-mini) | Threaded Scout request filters through the FastAPI layer into core search/prompt context, added tests for filter propagation, and verified Python/Web test suites pass. |
   102|| 2026-05-06 | scout-live-validation (kimi-for-coding) | Completed live end-to-end Scout validation with real API keys. FastAPI returns 3-4 real leads with three scores in ~15s. Browser QA confirmed lead cards render correctly. Created `.env.example` templates. Sprint 1 complete. |
   103|| 2026-05-06 | qa (kimi-for-coding) | Full browser QA on Scout workspace with gstack browse. Verified login, search form, live results rendering, lead cards with three scores, and no console errors. Health score 100/100. No issues found. |
   104|| 2026-05-06 | qa (kimi-for-coding) | Browser-QA'd login, home, Scout, and logout flows. Auth works end-to-end. Scout form submits correctly and displays the expected missing-API-key error. Health score 95/100. QA report written to `.gstack/qa-reports/qa-report-white-rabbit-2026-05-06.md`. |
   105|| 2026-05-06 | build-meeting-reconciliation (Codex) | Checked current build and uncommitted Sprint 3 scoreboard work against Monroe St NE 8 meeting notes. Wrote `docs/reports/build-meeting-reconciliation-2026-05-06.md`, updated STATUS, and verified web/API checks. Core test suite has one env-isolation failure. |
   106|| 2026-05-06 | qa (gpt-5.4-mini) | Browser-checked the recipe library scoreboard on `localhost:3003`, verified the recipe list, KPI tiles, and run history, captured a screenshot, and confirmed no console errors. |
| 2026-05-06 | merge (gpt-5.4-mini) | Merged feature/sprint3-recipe-scoreboard into `main` after browser QA, updated STATUS, and pushed `origin/main`. |
| 2026-05-07 | sprint4-batch-bulk (gpt-5.4-mini) | Added batch jobs/runs, POST /batch, batch UI/proxy/helpers, and tests. Fixed the cap test by making the mock job reflect requested caps. Verified API tests, Next.js build, and browser QA on /batch. |
| 2026-05-07 | qa (gpt-5.4-mini) | Re-verified the batch workspace in the browser, confirmed batch submission renders the result card and updated history, captured screenshots, and wrote the QA report. |
| 2026-05-07 | qa (gpt-5.4-mini) | Browser-validated the lead query guardrails slice on a clean next start, confirmed valid, vague, and blank queries behave correctly, and added a regression test for plain-text API failures. |
| 2026-05-07 | full-lead-export (gpt-5.4-mini) | Added Full-run CSV lead export helpers, wired the Scout workspace export button and download link, added tests, verified with Next.js build, Vitest, and browser QA, and pushed the feature branch. |
