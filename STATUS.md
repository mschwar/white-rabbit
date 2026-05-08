# STATUS

**Last updated:** 2026-05-08 by gpt-5.4-mini
**Branch:** feat/buildout-04-vertical-agnostic-prompt
**Current sprint:** BUILDOUT-04 in progress — prompt and model descriptions rewritten, tests passing locally

> Update this file at the end of every session. It is the source of truth for "where we are."

---

## ⚠️ Audit reality (2026-05-07)

A ground-up zero-trust audit landed on this branch. **The product is not deployable as-is.** See [`audits/hard-audit-2026-05-07.md`](audits/hard-audit-2026-05-07.md) for the full report and [`docs/06-audit-action-plan.md`](docs/06-audit-action-plan.md) for the remediation roadmap.

**Top 5 P0 blockers** (full list of 10 in the master report):

1. **`OPENAI_BASE_URL=http://localhost:11434/v1` in `apps/api/.env`** silently routes every chat completion to local Ollama. The current main config has been broken for any environment without a local chat model installed in Ollama. Phase 2 reproduced this as 4-of-4 query failures until forced to api.openai.com.
2. **VoIP/Telecom bias is hardcoded** into `orchestrator.py` SYSTEM_PROMPT and `models.py` Field descriptions. Live testing reproduced the failure at **89% rate** across non-VoIP queries (CISO of NY Fed Reserve Bank pitched VoIP for "regulatory compliance"; hydrogen fuel cell VP pitched VoIP for production efficiency).
3. **`sandbox_state` table has no alembic migration.** Today's dev DB only has it because `init_db()` calls `Base.metadata.create_all()` as a parallel schema path. A clean alembic-only deploy crashes on every user-facing route.
4. **`get_engine()` ignores `DATABASE_URL`** (apps/api/api/models.py:114–116). Production always tries hardcoded localhost.
5. **Session tokens never expire server-side.** `verifySessionToken` decodes `iat` but never compares it to the clock.

**Sprint reconciliation:** Sprints 1, 2, 4 need rework (see action plan). Sprint 3 is mostly clean.

**Recommendation:** Pause new feature work and external-user testing until Phase 1 of the action plan lands (~10 hours of focused work).

---

## What's done

- Repo created at `/Users/mschwar/Documents/white-rabbit/`.
- Directory structure scaffolded (`docs/`, `apps/web/`, `apps/api/`, `packages/core/`).
- Bootstrap documentation written:
  - `AGENTS.md` — agent entry point and rules.
  - `README.md` — human intro pointing at AGENTS.md.
  - `docs/00-context.md` — strategic background.
  - `docs/01-model.md` — operator model, recipes, scores, run model.
  - `docs/02-stack.md` — Next.js + Python + Postgres layout and conventions.
  - `docs/03-decisions.md` — locked decisions (4 ADRs).
  - `docs/04-roadmap.md` — Sprint 1 build slice and 90-day kill/keep gate.
  - `docs/05-reuse.md` — explicit lift list from `/Users/mschwar/Documents/proxy-lead`.
- .gitignore written.
- git initialized and first commit made.
- 'superskills' (v2.5.0) installed and linked in .gemini/skills.
  - Repository cloned to .gemini/superskills-repo.
  - ~150+ skills linked to workspace scope.
  - Workflow rule added to GEMINI.md.
- **Sprint 1: Scaffold `apps/web` (Next.js) completed.**
- **Sprint 1: Scaffold `apps/api` (FastAPI + uv) completed.**
- **Sprint 1: Core primitives (`packages/core`) lifted and adapted.**
- **Testing framework bootstrapped for Web (Vitest/Playwright) and Python (Pytest).**
- **Sprint 1: Scout core smoke harness added.** `packages/core` orchestrator now supports injectable search/client fakes, and the API has a verified `/scout` contract test.
- **Sprint 1: Python import path bootstraps added** so `core` resolves from local package runs and `api.main` can import the shared core package.
- **Sprint 1: Shared-password auth gate added in `apps/web`.** Login/logout routes, session-cookie middleware, a protected home shell, and a protected Scout shell are browser-tested.
- **Sprint 1: Scout UI + Next.js API proxy wired.** The `/scout` page now posts to `POST /api/scout`, proxies to FastAPI `/scout`, and renders returned leads/metrics.
- **Sprint 1: Scout filters now propagate end-to-end.** `apps/web` already forwards the payload, and `apps/api`/`packages/core` now pass request filters into search and prompt context.
- **Sprint 1: Real Tavily search integration.** `packages/core/src/core/search.py` now uses direct HTTP API calls to Tavily (not httpx.AsyncClient, since tavily-python SDK is sync-only; we use `httpx.Client` in a sync wrapper callable from async orchestrator).
- **Sprint 1: Real OpenAI extraction integration.** `packages/core/src/core/orchestrator.py` uses `AsyncOpenAI` with `beta.chat.completions.parse` and structured outputs (`response_format=LeadList`).
- ~~**Sprint 1: Email patterns lifted.**~~ — `packages/core/src/core/email_patterns.py` copied and adapted from `/proxy-lead/email_patterns.py` with relative imports to the new `Lead` model. **⚠️ AUDIT FAILED:** the file was lifted but never imported anywhere; it is dead code. The prompt instructs the LLM to "deduce emails based on common domain patterns" while the module that learns those patterns is unreachable. See audit D1-06 / D4-08 / D5-04.
- **Sprint 1: API error handling improved.** `apps/api/api/main.py` now distinguishes `OrchestratorError` (503 Service Unavailable) from unexpected exceptions (500 Internal Server Error).
- **Sprint 1: Core test coverage expanded.** Added tests for missing-key and Tavily-failure error paths in `packages/core/tests/test_orchestrator.py`.
- ~~**Sprint 1: Scout live validation completed.**~~ — Originally claimed "verified end-to-end with real API keys: FastAPI `/scout` returns 3-4 real leads with three scores and metrics in ~15s." **⚠️ AUDIT REALITY:** this validation used the K-12 Albuquerque query — the only query that aligns with the hidden VoIP bias. Real testing on 3 other verticals (healthcare, finance, manufacturing) showed VoIP language injected into 89% of leads. "Lead cards render" was a UI test, not a data-quality test. See audit D1-01 / Phase 2 F2-01.
- **Sprint 1: Environment template files created.** `.env.example` files for root, `apps/api/`, and `apps/web/` to help future developers configure API keys and secrets.
- **Sprint 2: Postgres persistence added.** Local PostgreSQL 16 is running via Homebrew; SQLAlchemy models and Alembic migration created `recipe`, `recipe_run`, `lead`, and `lead_feedback` tables.
- **Sprint 2: Scout vs Full split implemented.** Scout remains quick/no-storage; Full stores recipe + run metadata and returns saved IDs.
- **Sprint 2: Five-button feedback per lead implemented.** Leads now expose usable / wrong persona / bad source / bad contact / duplicate feedback buttons.
- **Sprint 2: Recipe library page added.** `/recipes` shows saved recipes and run history.
- **Sprint 2: Operator-time logging added.** Full runs now expose a close-run form that records operator minutes through `/api/runs/[run_id]/close`.
- **Sprint 2: Browser QA completed for the new slice.** Verified Full run save UI, operator-minute close flow, and recipe library rendering in the browser.
- **Sprint 2: Tests passing.** `npm run build` and `npm test` pass in `apps/web`; `pytest tests -q` passes in `apps/api`.
- **Sprint 2 merged to `main`.** `main` and `origin/main` are at `feat(sprint2): add recipe library and operator time logging (#6)`.
- **Sprint 3: Recipe scoreboard added and QA verified.** `/recipes` now shows per-recipe scoreboard metrics: leads returned, usable leads, API cost spent, operator minutes, and derived minutes/cost per usable lead. Browser QA on `localhost:3003` confirmed the recipe list, scoreboard tiles, and run history render correctly.
- **Sprint 3: Sort-by-score controls added and QA verified.** `/scout` now lets the operator sort by original rank, Fit, Evidence, Contact, or pass/fail gate. Browser QA on `localhost:3004` confirmed the select control and sorted lead order.
- **Sprint 3: Sort controls re-verified in browser.** Current QA pass confirmed the selector still works on the live workspace and produced `.gstack/qa-reports/qa-report-white-rabbit-2026-05-06-sort-controls.md`.
- **Sprint 3: Friday recipe-review export added and QA verified.** `/recipes` now exposes a Friday export card with CSV download and printable markdown preview. Browser QA on `localhost:3005` confirmed the export builds and the review packet renders.
- **Sprint 3 merged to `main`.** The scoreboard feature, docs updates, and QA report are merged and pushed.
- **Sprint 3: Friday recipe-review export added and QA verified.** `/recipes` now exposes a Friday export card with CSV download and printable markdown preview. Browser QA on `localhost:3005` confirmed the export builds and the review packet renders.
- **Sprint 3 merged to `main`.** The Friday export feature, docs updates, and QA report are merged and pushed.
- **Sprint 4: Batch/bulk workspace and API added.** Batch jobs and runs persist in Postgres, the API exposes `POST /batch`, and the web app now has a batch page, proxy route, and batch helpers/UI.
- **Sprint 4: Batch API tests passing.** `pytest tests -q` passes in `apps/api`.
- **Sprint 4: Browser QA completed.** Logged in to the web app, opened `/batch`, submitted a batch run, and verified the result card and run summaries render correctly.
- **Sprint 4 follow-up: Full-run lead export added.** Scout Full runs now build a downloadable CSV export with query, recipe, run metadata, scores, gate status, explanation, and validation context. Browser QA confirmed the export link renders in the live workspace.
- **Sprint 4 follow-up: Sandbox caps merged.** Query/row caps (10 queries / 1000 rows) with reset and usage tracking. API enforces caps on Scout, Full, and Batch. Web UI shows quota card with reset button. Tests updated for sandbox fetch on mount. **⚠️ AUDIT REALITY:** the `sandbox_state` table has no alembic migration (audit D4-01 / D7-03); the query counter is non-atomic and bypassable under concurrent load (audit D4-04); the spend cap is checked AFTER the API call so money is already spent when the cap fires (audit D4-12).
- **BUILDOUT-01: Config preflight + DATABASE_URL respect + remove Ollama trap.** QA signed off on `feat/buildout-01-config-preflight`. Preflight verifies env vars and OpenAI/Tavily/Postgres connectivity; `DATABASE_URL` is only required in production (hotfix committed); Ollama trap removed.
- **BUILDOUT-01 QA report captured.** Browser QA notes and screenshots are saved at `.gstack/qa-reports/buildout-01-config-preflight.md` with baseline data in `.gstack/qa-reports/baseline.json`.
- **BUILDOUT-02: Add `sandbox_state` alembic migration.** Merged on `feat/buildout-02-sandbox-state-migration`; the `sandbox_state` table now has a real Alembic migration and the `create_all()` fallback is gone.
- **BUILDOUT-03: Server-side session token expiry.** Verified in tests and browser QA on the protected login / Scout flow; session tokens now expire server-side on schedule.

## What's in flight

- BUILDOUT-04 is in flight on `feat/buildout-04-vertical-agnostic-prompt`; prompt/model-description rewrite is implemented and tests pass locally. Awaiting QA + merge.

## Next concrete task

- QA BUILDOUT-04 in the browser, then mark `docs/07-buildout-plan.md` and merge on Prompt B.

## Open questions for Matt

- Commercial arrangement with Lee and Thomas (free seats / revenue share / equity / content rights). Blocks the design-partner motion. **Not blocking Sprint 1 build, but blocks public usage.**
- Cost-tracking source of truth: should live API cost figures be pulled from OpenAI/Tavily dashboards, or computed locally from token/call counts? Recommendation: compute locally per-run, reconcile weekly. See `docs/05-reuse.md` note on stale 2025 prices.
- Access boundary for the Friday guarded version: local handoff, deployed internal URL, or Matt-run sessions?
- Whether any external customer gets direct sandbox access before the 90-day kill/keep gate. If yes, customer-data isolation needs an explicit boundary first.
- Sandbox cap semantics: is the 10-query / 1,000-row cap per operator, per customer, per shared app, or per reset window?
- Export target: raw CSV, Excel-style CSV, HubSpot-ready CSV, or multiple formats?

## Known issues / risks

**⚠️ This section was incomplete prior to the 2026-05-07 audit.** The following items were listed as "known issues" but have since been fixed; they are kept here strikethrough so the regression history is visible:

- ~~Feedback buttons may not be fully usable after Full runs until persisted lead IDs are returned to the web UI; current core `Lead` objects do not include the database `lead.id`.~~ → Fixed in commit 76c0987 (`feat: return persisted lead IDs in Full runs`). See audit D8-01.
- ~~Current app has no server-side lead-generation prompt guardrail and no query/row usage ledger for the meeting's sandbox cap.~~ → Both shipped: `_query_guardrail_or_422()` in apps/api/api/main.py:195/222/419 and sandbox caps in #11. See audit D8-01.

Real known issues (post-audit):

- **P0 — `OPENAI_BASE_URL` Ollama trap** (audit F2-05). `apps/api/.env` routes all OpenAI SDK calls to local Ollama; main config has been broken for any non-local-Ollama environment.
- **P0 — Hardcoded VoIP bias** in prompt and schema (audit D1-01, D1-02). Live testing reproduced 89% leak rate.
- **P0 — `sandbox_state` migration missing** (audit D4-01, D7-03). Fresh deploys don't work without `Base.metadata.create_all()` fallback.
- **P0 — `get_engine()` ignores `DATABASE_URL`** (audit D4-03). Wrong DB in production.
- **P0 — Session tokens never expire server-side** (audit D4-02).
- **P0 — Zero tests verify real LLM extraction** (audit D2-01). All 46 tests use "Jane Smith" mock.
- **P1 — Lost prompt instructions** vs proxy-lead reference (audit D5-01, D5-02).
- **P1 — `gate_passed` LLM-controlled, not server-validated** (audit D4-07). One inconsistency observed in 9 real leads.
- Pricing constants in `packages/core/core/cost.py` updated to 2026-05 estimates. Verify with real dashboard data after first few runs.
- Next.js 16 warns that `middleware.ts` is deprecated in favor of `proxy.ts`; auth currently works, but a rename is a follow-up if we want to eliminate the warning.
- `packages/core` test isolation issue: `test_scout_raises_on_missing_openai_key` fails when `OPENAI_API_KEY` is present in the environment because it reaches OpenAI instead of exercising the missing-key branch.
- See [`docs/06-audit-action-plan.md`](docs/06-audit-action-plan.md) for the full prioritized remediation roadmap (Phases 1, 2, 3).

## Session log

| Date | Agent | Summary |
|------|-------|---------|
| 2026-05-05 | bootstrap (Opus 4.7) | Repo bootstrapped. All 10 priority docs written. git init + first commit. Next: Sprint 1 scaffold. |
| 2026-05-05 | api-scaffold (Opus 4.7) | Scaffolded apps/api and packages/core. Lifted and adapted code from proxy-lead. Passed health check tests. |
| 2026-05-06 | scout-harness (gpt-5.4-mini) | Added injectable Scout smoke harnesses in core and API, fixed local import bootstraps, and verified core/API/web tests plus runtime imports. |
| 2026-05-06 | qa (gpt-5.4-mini) | Browser-checked the homepage and docs path, captured screenshots, and found no browser-visible issues. |
| 2026-05-06 | shared-password-auth (gpt-5.4-mini) | Added shared-password auth middleware, login/logout routes, and protected home/Scout shells. Browser-checked login, invalid-password, home, and Scout flows with screenshots. |
| 2026-05-06 | qa (gpt-5.4-mini) | Browser-checked the shared-password login, sign-out, and Scout pages; tightened Scout query label spacing; updated QA docs and screenshots. |
| 2026-05-06 | merge (gpt-5.4-mini) | Merged feature/shared-password-auth into main after QA verification and pushed the merge commit. |
| 2026-05-06 | scout-api-proxy (gpt-5.4-mini) | Added the Scout Next.js query UI, `/api/scout` proxy route, and browser-backed error-path checks. Verified with Vitest and Next.js production build; live Scout browser QA remains blocked by the unknown shared password secret. |
| 2026-05-06 | qa (gpt-5.4-mini) | Attempted browser QA on the Scout feature branch, captured the login gate state, and updated STATUS.md to note that successful end-to-end Scout verification is still pending valid shared-password access. |
| 2026-05-06 | scout-core-real-integration (gpt-5.4-mini) | Threaded Scout request filters through the FastAPI layer into core search/prompt context, added tests for filter propagation, and verified Python/Web test suites pass. |
| 2026-05-06 | scout-live-validation (kimi-for-coding) | Completed live end-to-end Scout validation with real API keys. FastAPI returns 3-4 real leads with three scores in ~15s. Browser QA confirmed lead cards render correctly. Created `.env.example` templates. Sprint 1 complete. |
| 2026-05-06 | qa (kimi-for-coding) | Full browser QA on Scout workspace with gstack browse. Verified login, search form, live results rendering, lead cards with three scores, and no console errors. Health score 100/100. No issues found. |
| 2026-05-06 | qa (kimi-for-coding) | Browser-QA'd login, home, Scout, and logout flows. Auth works end-to-end. Scout form submits correctly and displays the expected missing-API-key error. Health score 95/100. QA report written to `.gstack/qa-reports/qa-report-white-rabbit-2026-05-06.md`. |
| 2026-05-06 | build-meeting-reconciliation (Codex) | Checked current build and uncommitted Sprint 3 scoreboard work against Monroe St NE 8 meeting notes. Wrote `docs/reports/build-meeting-reconciliation-2026-05-06.md`, updated STATUS, and verified web/API checks. Core test suite has one env-isolation failure. |
| 2026-05-06 | qa (gpt-5.4-mini) | Browser-checked the recipe library scoreboard on `localhost:3003`, verified the recipe list, KPI tiles, and run history, captured a screenshot, and confirmed no console errors. |
| 2026-05-06 | merge (gpt-5.4-mini) | Merged feature/sprint3-recipe-scoreboard into `main` after browser QA, updated STATUS, and pushed `origin/main`. |
| 2026-05-07 | sprint4-batch-bulk (gpt-5.4-mini) | Added batch jobs/runs, POST /batch, batch UI/proxy/helpers, and tests. Fixed the cap test by making the mock job reflect requested caps. Verified API tests, Next.js build, and browser QA on /batch. |
| 2026-05-07 | qa (gpt-5.4-mini) | Re-verified the batch workspace in the browser, confirmed batch submission renders the result card and updated history, captured screenshots, and wrote the QA report. |
| 2026-05-07 | qa (gpt-5.4-mini) | Browser-validated the lead query guardrails slice on a clean next start, confirmed valid, vague, and blank queries behave correctly, and added a regression test for plain-text API failures. |
| 2026-05-07 | full-lead-export (gpt-5.4-mini) | Added Full-run CSV lead export helpers, wired the Scout workspace export button and download link, added tests, verified with Next.js build, Vitest, and browser QA, and pushed the feature branch. |
| 2026-05-07 | qa (gpt-5.4-mini) | Browser-verified the full lead export flow on the feature branch: Scout search, Full search, export generation, run closeout, and recipe library scoreboard all rendered correctly. Captured browser screenshots and checked for console errors. |
| 2026-05-08 | qa (gpt-5.4-mini) | Browser QA covered login, Scout, Full, recipes, and batch on http://localhost:3000; captured screenshots; confirmed clean console; wrote `.gstack/qa-reports/buildout-01-config-preflight.md` and `.gstack/qa-reports/baseline.json`. |
| 2026-05-08 | docs-sync (gpt-5.4-mini) | Reconciled `docs/07-buildout-plan.md` with git history, marked BUILDOUT-02 complete, updated STATUS to point at BUILDOUT-03, and tightened AGENTS so future BUILDOUT sessions must update the checklist before finishing. |
| 2026-05-07 | hard-audit (Claude Opus 4.7) | Ground-up zero-trust audit. 8 parallel sub-agents, 4 live scout queries against real OpenAI ($0.045 spent), 65 findings across 8 dimensions plus Phase 2. 2 agent errors caught and corrected. Master report at `audits/hard-audit-2026-05-07.md`; action plan at `docs/06-audit-action-plan.md`. **Conclusion: not deployable as-is. 5 confirmed P0 blockers including `OPENAI_BASE_URL` routing to local Ollama and 89% VoIP leak rate in real leads.** |
