# STATUS

**Last updated:** 2026-05-09 by Codex feat/docs-hard-audit-remediation
**Branch:** feat/docs-hard-audit-remediation
**Current sprint:** Documentation authority remediation on the validated-leads rebuild branch; F04 query compiler/planner remains next after this docs-only branch merges

> Update this file at the end of every session. It is the source of truth for "where we are."

---

## Current rebuild status (2026-05-09)

**Integration branch:** `rebuild/validated-leads-loop`

**Current gate:** Red. Do not ship. Do not daily-dogfood with Thomas or Lee.

**Next feature pointer:** F04 Query compiler / planner (ready).

**Control docs:**

- `docs/00-product-northstar.md` is the anti-drift product source of truth for the rebuild.
- `docs/08-agentic-buildout-plan.md` is the agentic missing-feature list and two-prompt loop control document.
- `docs/09-rebuild-phase-gates.md` is the gated wave plan for milestone reviews before downstream work unlocks.
- `docs/10-documentation-audit-2026-05-09.md` records the repo-wide documentation audit and remediation performed on this branch.
- `.gstack/qa-reports/qa-template-agentic-buildout.md` is the QA report template for rebuild features.

**Main is intentionally untouched:** the validated-leads rebuild runs on `rebuild/validated-leads-loop` so product-risky reconstruction can proceed without implying `main` is shippable or merging unvalidated feature work into the production line.

**Latest handoff:**

```text
Feature: Repo-wide documentation authority audit and remediation
Branch: feat/docs-hard-audit-remediation
Status: verification_passed_ready_to_merge
What changed: Added ADR-006 and `docs/10-documentation-audit-2026-05-09.md`; rewrote README/TESTING/USER_GUIDE/package READMEs for red-gate rebuild reality; updated AGENTS read order; corrected docs/08 F04 pointer; added the W1 containment gate report; marked legacy planning docs, audits, QA reports, and meeting notes with explicit status banners; refreshed the QA report index.
Tests or QA run: `cd apps/web && npm test -- --run` (25 passed); `cd packages/core && uv run pytest tests/test_query_guardrails.py -q` (9 passed); `cd apps/api && $env:DATABASE_URL='postgresql://white_rabbit:white_rabbit_dev@localhost:5432/white_rabbit'; uv run pytest tests/test_api.py -q -k "guardrail or sandbox or scout or full or batch"` (22 passed, 12 deselected); `git diff --check`; doc stale-string hygiene check.
Screenshots or report: Documentation-only; W1 gate evidence recorded in `.gstack/qa-reports/gate-w1-red-state-containment.md`.
Northstar reflection: This branch removes stale docs as an excuse for building off the wrong product truth. White Rabbit remains red-gated until lead validation quality passes the phase gates.
Next pointer: Merge this docs branch to `rebuild/validated-leads-loop`, then begin F04 Query compiler / planner on `feat/f04-query-compiler`.
Open questions: None blocking docs remediation.
```

---

## 🚨 Zero-trust product audit reality (2026-05-09)

A ruthless product audit against Thomas/Lee's actual core loop found White Rabbit v2 is **not useful enough for a real sales operator yet**. Full report: [`audits/zero-trust-product-audit-2026-05-09.md`](audits/zero-trust-product-audit-2026-05-09.md). Raw live outputs: [`audits/raw/zero-trust-2026-05-09/`](audits/raw/zero-trust-2026-05-09/).

**Verdict:** Do not ship. Do not put Thomas or Lee on this as a daily tool. Rebuild search validation before more feature work.

**Scores:** features/functions **2/10**, UI/UX/design **3/10**, actual search **1/10**.

**Fatal findings:**

1. The Arizona K-12 VoIP benchmark failed twice: the full Thomas-style prompt crashed Tavily at the 400-character query limit; a compressed version returned zero leads.
2. Across 18 returned sampled leads, **0 were CRM-usable** under the standard "salesperson can act without doing most of the research again."
3. The shared-password UI is not the true boundary: the Fly backend endpoints were publicly callable during the audit, including `/scout`, `/full`, `/batch`, and `/sandbox/reset`.
4. Guardrails block simple off-topic prompts but fail B2C/privacy boundary prompts, which run and return zero leads instead of refusing.
5. Recipe library, scoreboard, Friday export, and bulk workspace are premature and should be hidden or killed until single-query search quality passes a benchmark.

**Next product move:** freeze feature work, hide recipe/batch operator surfaces, put auth on the backend or restrict ingress, build a golden Arizona K-12 benchmark harness, and rebuild field-level source/contact validation.

---

## ⚠️ Audit reality (2026-05-07)

A ground-up zero-trust audit landed on this branch. **The product is not deployable as-is.** See [`audits/hard-audit-2026-05-07.md`](audits/hard-audit-2026-05-07.md) for the full report and [`docs/06-audit-action-plan.md`](docs/06-audit-action-plan.md) for the remediation roadmap.

**Top 5 P0 blockers** (full list of 10 in the master report):

1. **`OPENAI_BASE_URL=http://localhost:11434/v1` in `apps/api/.env`** silently routes every chat completion to local Ollama. The current main config has been broken for any environment without a local chat model installed in Ollama. Phase 2 reproduced this as 4-of-4 query failures until forced to api.openai.com.
2. **Former P0 — VoIP/Telecom bias was hardcoded** into `orchestrator.py` SYSTEM_PROMPT and `models.py` Field descriptions. BUILDOUT-04 removed the bias and browser QA re-verified the fix on 2026-05-08.
3. **Former P0 — sandbox_state alembic migration was missing.** Today's dev DB only had it because `init_db()` called `Base.metadata.create_all()` as a parallel schema path. BUILDOUT-02 added the real Alembic migration and removed the fallback.
4. **Former P0 — `get_engine()` ignored `DATABASE_URL`.** Production always tried hardcoded localhost. BUILDOUT-01 fixed this.
5. **Former P0 — server-side session expiry was missing.** `verifySessionToken` decoded `iat` but did not compare it to the clock. BUILDOUT-03 fixed this.

**Sprint reconciliation:** Sprints 1, 2, 4 need rework (see action plan). Sprint 3 is mostly clean.

**Recommendation:** Pause new feature work and external-user testing until Phase 1 of the action plan lands (~10 hours of focused work).

---

## 🚨 Production deploy reality (2026-05-09 — /qa run)

A browser QA run against `https://white-rabbit-ten.vercel.app/` found the deployed app is **fully broken end-to-end**. Health score: **18 / 100**. Full report: [`.gstack/qa-reports/qa-report-white-rabbit-ten-vercel-app-2026-05-09.md`](.gstack/qa-reports/qa-report-white-rabbit-ten-vercel-app-2026-05-09.md).

**Three critical issues:**

1. **`vercel.json` legacy `routes[]` shadows local Next.js auth routes.** The current `vercel.json` (restored in commit `534aee4` from BUILDOUT-16) uses Vercel v2 `builds[]` + `routes[]` which proxies *every* `/api/*` to fly, including `/api/login` and `/api/logout`. Submitting the login form lands users on a raw JSON 404 page (`{"detail":"Not Found"}`) returned by FastAPI. **No user can authenticate in production.**
2. **fly.io backend `white-rabbit-api.fly.dev` is down.** Direct hits to `/health` and every `/api/*` path time out or return 502/503. Likely needs `flyctl status -a white-rabbit-api` + scale-up + redeploy.
3. **Auth bypass on protected pages.** `/scout`, `/recipes`, `/batch` render fully to anonymous users. Two compounding causes: legacy `routes[]` skips Next.js middleware, and the pages are statically prerendered + edge-cached (`age: 22029` ≈ 6h on `/scout`).

**Visual / mobile:** Clean. Typography, dark theme, responsive layout all good. The break is structural, not visual.

**Recommended fix path** (see report appendix for full JSON):
- Replace `vercel.json` with `framework: "nextjs"` + `rewrites[]` allowlist of fly endpoints (excludes `/api/login`, `/api/logout` so local Next routes execute).
- Add `export const dynamic = 'force-dynamic'` to `apps/web/src/app/scout/page.tsx`, `recipes/page.tsx`, `batch/page.tsx` so middleware runs per-request.
- Bring the fly backend back up.

`vercel.json` has been edited 5× in the last 7 days (`534aee4`, `b7dbfd5`, `68d82da`, `d96cc60`, `62ec795`) chasing the SPA-fallback-vs-API-proxy tradeoff. The QA fix was deferred — choose a path before the next vercel.json edit.

---

## What's done

- **Documentation authority audit/remediation completed on `feat/docs-hard-audit-remediation`.** Added ADR-006, created `docs/10-documentation-audit-2026-05-09.md`, rewrote active setup/testing/operator docs for red-gate rebuild reality, bannered historical planning/audit/QA/meeting docs, fixed the QA index, and recorded the W1 containment gate.
- **W1 red-state containment gate advanced.** `.gstack/qa-reports/gate-w1-red-state-containment.md` records F01-F03 evidence plus fresh W1 verification commands, so F04 remains ready.
- **F01 QA complete and merged on `rebuild/validated-leads-loop` via `feat/f01-hide-premature-surfaces`.** Home primary navigation now links only to lead search, and Scout hides recipe-library links, raw endpoint/FastAPI/storage copy, and the sandbox reset button. `npm test`, `npm run build`, and browser screenshots (with QA report `qa-report-f01-hide-premature-surfaces-2026-05-09.md`) were captured.
- **F02 QA complete and merged on `rebuild/validated-leads-loop` via `feat/f02-backend-api-boundary`.** FastAPI lead/sandbox endpoints now require the internal boundary token. Next.js proxy calls to `/api/scout` are verified with auth flow and expected local-service error payload; direct POSTs to `/scout`, `/full`, `/batch`, and `/sandbox/reset` return 401 when no token is supplied. QA report: `qa-report-f02-backend-api-boundary-2026-05-09.md`.
- **F03 QA complete and merged on `rebuild/validated-leads-loop` via `feat/f03-b2b-guardrails`.** Guardrails now allow normal B2B sales queries while blocking consumer/privacy-sensitive, weapon, and off-topic prompts before search. `uv run pytest tests/test_query_guardrails.py -q` and API guardrail regression tests pass (`2 passed`).
- **Rebuild phase gates merged.** `docs/09-rebuild-phase-gates.md` groups F00-F23 into gated waves W0-W6 and requires gate review reports before downstream waves unlock.
- **F00 rebuild planning docs landed on `rebuild/validated-leads-loop`.** Added `docs/00-product-northstar.md`, `docs/08-agentic-buildout-plan.md`, AGENTS rebuild branch protocol, STATUS rebuild handoff, and `.gstack/qa-reports/qa-template-agentic-buildout.md`.
- **BUILDOUT-12: Atomic sandbox cap counter added.** `_sandbox_reserve_query_or_429` now uses `get_sandbox_state_for_update()` to lock the sandbox row during cap checks, and API tests cover the concurrent 12-request cap path.
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
- **BUILDOUT-04 merged to `main`.** The prompt/model-description rewrite is on main, the old VoIP bias is removed, and browser QA re-verified finance results no longer leak VoIP/telecom language.
- **Sprint 4 follow-up: Sandbox caps merged.** Query/row caps (10 queries / 1000 rows) with reset and usage tracking. API enforces caps on Scout, Full, and Batch. Web UI shows quota card with reset button. Tests updated for sandbox fetch on mount. **⚠️ AUDIT REALITY:** the `sandbox_state` table has no alembic migration (audit D4-01 / D7-03); the query counter is non-atomic and bypassable under concurrent load (audit D4-04); the spend cap is checked AFTER the API call so money is already spent when the cap fires (audit D4-12).
- **BUILDOUT-01: Config preflight + DATABASE_URL respect + remove Ollama trap.** QA signed off on `feat/buildout-01-config-preflight`. Preflight verifies env vars and OpenAI/Tavily/Postgres connectivity; `DATABASE_URL` is only required in production (hotfix committed); Ollama trap removed.
- **BUILDOUT-01 QA report captured.** Browser QA notes and screenshots are saved at `.gstack/qa-reports/buildout-01-config-preflight.md` with baseline data in `.gstack/qa-reports/baseline.json`.
- **BUILDOUT-02: Add `sandbox_state` alembic migration.** Merged on `feat/buildout-02-sandbox-state-migration`; the `sandbox_state` table now has a real Alembic migration and the `create_all()` fallback is gone.
- **BUILDOUT-03: Server-side session token expiry.** Verified in tests and browser QA on the protected login / Scout flow; session tokens now expire server-side on schedule.
- **BUILDOUT-08: Delete `email_patterns.py` dead code.** Browser QA on 2026-05-08 verified the login gate, Scout results page, recipe library scoreboard, bulk workspace, and sign-out flow with clean console output; report saved at `.gstack/qa-reports/qa-report-white-rabbit-2026-05-08.md`.
- **BUILDOUT-09: UI de-bias branch completed and browser-verified.** Scout now opens with the neutral placeholder defaults, Batch uses the debiased starter rows, and the lead-export description matches the CSV columns. Vitest, Next.js build, and live browser QA all passed.
- **BUILDOUT-13: Specific API error codes for UI.** API returns structured `{error_code, message, request_id}` on 503/500; Scout workspace maps codes to user-friendly messages (e.g., `tavily_failed` → "Search engine is rate-limited; try again in ~60s"). Verified by 24 passing API tests and live browser QA on Scout/recipes/batch. QA report at `.gstack/qa-reports/buildout-13-error-codes.md`.
- **BUILDOUT-14: README setup walkthrough verified end-to-end.** Followed README.md steps on the live workspace: confirmed web (localhost:3000) and API (localhost:8000) running, login gate functional, Scout query returns leads with score cards, recipe library and batch workspace render correctly, sign-out clears session. QA report at `.gstack/qa-reports/buildout-14-readme-verified.md`.
- **BUILDOUT-15: QA rubric document + multi-vertical gate shipped.** Added `docs/qa-rubric.md` with the 6-tier ship-gate (Tiers 1–4 mandatory for extraction/scoring changes, Tier 5 weekly, Tier 6 every run). Updated `.gstack/qa-reports/index.md` to reference the rubric. Added `.gstack/qa-reports/qa-template.md` as a skeleton for future QA reports. Updated `AGENTS.md` read order to include the rubric. Browser QA verified login, Scout, recipes, and batch pages render correctly with zero console errors. QA report at `.gstack/qa-reports/qa-report-buildout-15-qa-rubric.md`.
- **BUILDOUT-16: Deploy config for Vercel + Fly.io + Neon shipped.** Created `apps/api/Dockerfile`, `apps/api/fly.toml`, `vercel.json`, and `.github/workflows/deploy.yml`. Updated `apps/web/next.config.ts` with production rewrites and image config. Added "Deployment" section to README with platform setup, CI/CD, and manual deploy instructions. All tests pass (24 API, 23 web). Browser QA verified Scout workspace renders correctly. Branch `feat/buildout-16-deploy-config` pushed and ready for QA+merge.
- **BUILDOUT-16 QA verified and merged.** Health score 95/100. All 24 API tests and 23 web tests pass. Next.js build succeeds. Deploy config files validated. Only cosmetic issue: favicon 404s (deferred). Ready for BUILDOUT-17.
- **BUILDOUT-17: Live deploy verified in production.** Fly API `https://white-rabbit-api.fly.dev/health` returns `200 {"status":"ok"}` after the OpenAI secret fix. Vercel project config was corrected (`rootDirectory=apps/web`, framework `nextjs`, runtime env vars added) and a fresh production deploy now serves the local Next auth routes. Verified with authenticated `vercel curl`: anonymous `/scout` redirects to `/login?next=%2Fscout`, wrong-password `POST /api/login` redirects to `/login?error=1`, and correct-password `POST /api/login` sets `wr_session` and redirects to `/`. Remaining platform risk: Fly trial machines auto-stop after ~5 minutes unless billing is enabled.
- **BUILDOUT-17: Final production browser QA completed.** Verified the live Vercel deployment at commit `f3b6a45`, confirmed Fly health and deploy status, exercised login / Scout / Full / export / feedback / closeout / logout in the browser, and saved evidence at `.gstack/qa-reports/buildout-17-production-verification.md` plus screenshots under `.gstack/qa-reports/screenshots/`.
- **BUILDOUT-17 follow-up: fixed the POST-login redirect crash and unblocked CI.** Root cause of the production auth bug was `NextResponse.redirect()` returning a 307 from `POST /api/login`, which caused the browser to replay the POST against `/` and hit `405` until a manual reload. The login/logout routes now use `303` redirects, a regression test covers the login route, and `.github/workflows/deploy.yml` now starts Postgres + runs Alembic before API tests so the sandbox migration tests pass in GitHub Actions.

## What’s in flight

- Product is in audit-red state. Documentation authority remediation is ready to merge; F01-F03 are merged; F04 query compiler/planner is next on `feat/f04-query-compiler`.

## Next concrete task

- After merging `feat/docs-hard-audit-remediation` into `rebuild/validated-leads-loop`, start QA and implementation handoff for **F04 - Query compiler / planner** on branch `feat/f04-query-compiler`:
  - read AGENTS.md, STATUS.md, docs/00-product-northstar.md, docs/08-agentic-buildout-plan.md, and F04 feature card
  - implement and run the F04 verification commands from the feature card
  - update docs/08-agentic-buildout-plan.md and STATUS.md after handoff
  - merge only into `rebuild/validated-leads-loop` after QA

## Open questions for Matt

- Commercial arrangement with Lee and Thomas (free seats / revenue share / equity / content rights). Blocks the design-partner motion. **Not blocking Sprint 1 build, but blocks public usage.**
- Cost-tracking source of truth: should live API cost figures be pulled from OpenAI/Tavily dashboards, or computed locally from token/call counts? Recommendation: compute locally per-run, reconcile weekly. See `docs/05-reuse.md` note on stale 2025 prices.
- Access boundary for the Friday guarded version: local handoff, deployed internal URL, or Matt-run sessions?
- Whether any external customer gets direct sandbox access before the 90-day kill/keep gate. If yes, customer-data isolation needs an explicit boundary first.
- Sandbox cap semantics: is the 10-query / 1,000-row cap per operator, per customer, per shared app, or per reset window?
	- answer: it is per reset window for now.
- Export target: raw CSV, Excel-style CSV, HubSpot-ready CSV, or multiple formats?
	- answer: multiple formats.

## Known issues / risks

**⚠️ This section was incomplete prior to the 2026-05-07 audit.** The following items were listed as "known issues" but have since been fixed; they are kept here strikethrough so the regression history is visible:

- ~~Feedback buttons may not be fully usable after Full runs until persisted lead IDs are returned to the web UI; current core `Lead` objects do not include the database `lead.id`.~~ → Fixed in commit 76c0987 (`feat: return persisted lead IDs in Full runs`). See audit D8-01.
- ~~Current app has no server-side lead-generation prompt guardrail and no query/row usage ledger for the meeting's sandbox cap.~~ → Both shipped: `_query_guardrail_or_422()` in apps/api/api/main.py:195/222/419 and sandbox caps in #11. See audit D8-01.

Resolved audit blockers retained for regression history:

- ~~**P0 — `OPENAI_BASE_URL` Ollama trap** (audit F2-05).~~ → Fixed in BUILDOUT-01.
- ~~**P0 — Hardcoded VoIP bias** in prompt and schema (audit D1-01, D1-02).~~ → Fixed in BUILDOUT-04 and re-verified in browser on 2026-05-08.
- ~~**P0 — `sandbox_state` migration missing** (audit D4-01, D7-03).~~ → Fixed in BUILDOUT-02.
- ~~**P0 — `get_engine()` ignores `DATABASE_URL`** (audit D4-03).~~ → Fixed in BUILDOUT-01.
- ~~**P0 — server-side session expiry missing** (audit D4-02).~~ → Fixed in BUILDOUT-03.

Open residual risks:

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
| 2026-05-09 | docs-hard-audit-remediation (Codex) | Ran repo-wide documentation authority remediation on `feat/docs-hard-audit-remediation`: ADR-006, documentation audit report, active setup/testing/operator doc rewrites, historical banners, QA index repair, W1 gate report, and W1 verification commands. Next pointer remains F04 query compiler/planner after this docs branch merges. |
| 2026-05-09 | f03-build (Codex) | Implemented and QA-verified F03 guardrail rewrite on `feat/f03-b2b-guardrails`: B2B sales language now clears guardrails, privacy-sensitive and weapon/off-topic prompts are blocked before search, core and API regression tests pass, and feature is merged to `rebuild/validated-leads-loop`. QA report: `qa-report-f03-guardrails-2026-05-09.md`. |
| 2026-05-09 | f02-build (Codex) | Implemented and QA-verified backend API boundary on `feat/f02-backend-api-boundary`: FastAPI now requires `WR_API_INTERNAL_TOKEN` on `scout/full/batch/sandbox/reset` paths, Next.js proxies forward that token, API tests and web tests pass, browser proxy flow `/scout` is captured, and tokenless `POST` to all four protected endpoints returns 401. |
| 2026-05-09 | f01-build (Codex) | Implemented F01 on `feat/f01-hide-premature-surfaces`: home now links only to lead search; Scout hides premature recipe/batch/admin copy, raw endpoint/FastAPI/storage text, recipe-library links, and sandbox reset. Verified with web tests/build and localhost browser smoke screenshots; ready for Prompt B QA/merge to `rebuild/validated-leads-loop`. |
| 2026-05-09 | buildout-architect (Codex) | Added a gated W0-W6 implementation plan in `docs/09-rebuild-phase-gates.md` so downstream waves require evidence-backed gate review before unlocking. Used a separate worktree/branch to avoid touching in-flight F01 UI edits. |
| 2026-05-09 | buildout-architect (Codex) | Created `rebuild/validated-leads-loop` as the rebuild integration branch; added the product northstar, agentic buildout plan, rebuild branch protocol, QA template, and STATUS handoff. Next pointer: F01 hide premature operator surfaces. |
| 2026-05-09 | zero-trust-product-audit (Codex) | Audited White Rabbit against Thomas/Lee's core lead-quality loop using Gmail benchmark attachments, Monroe transcripts, live Fly API search runs, source URL validation, Vercel/GitHub/code inspection, and Browser screenshots. Wrote `audits/zero-trust-product-audit-2026-05-09.md` plus raw outputs. Verdict: do not ship; actual search scored 1/10 with 0/18 sampled leads CRM-usable and the Arizona K-12 VoIP benchmark failing. |
| 2026-05-09 | prod-hotfix (GPT-5.4) | Reproduced the production auth crash after password submit, traced it to 307 POST redirect semantics on `/api/login`, changed login/logout to `303`, added a login route regression test, and fixed GitHub Actions by provisioning Postgres + Alembic before API tests so the DB-backed sandbox tests pass in CI. |
| 2026-05-09 | deploy-fix (GPT-5.4) | Fixed production auth routing by removing the web app's catch-all `/api/*` rewrite, repaired the Vercel project (`rootDirectory=apps/web`, framework set, runtime env vars added), forced a successful prod deploy, verified `/api/login` now hits Next instead of Fly, and documented that the remaining production issue is Fly trial auto-stop. |
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
| 2026-05-09 | qa (gpt-5.4-mini) | Browser-checked login, Scout, recipes, and batch on localhost:3000; captured screenshots; ran core and API tests; updated STATUS and BUILDOUT-10 roadmap state; QA report saved at `.gstack/qa-reports/qa-report-white-rabbit-2026-05-09.md`. |
| 2026-05-08 | buildout-04 (gpt-5.4-mini) | Removed the hardcoded VoIP/telecom bias from the Scout prompt and Lead schema descriptions, updated tests, marked BUILDOUT-04 complete in the buildout plan, pushed PR #13, and merged it to main after browser QA re-verified finance queries no longer leak VoIP language. |
| 2026-05-08 | docs-sync (gpt-5.4-mini) | Reconciled `docs/07-buildout-plan.md` with git history, marked BUILDOUT-02 complete, updated STATUS to point at BUILDOUT-03, and tightened AGENTS so future BUILDOUT sessions must update the checklist before finishing. |
| 2026-05-08 | qa (gpt-5.4-mini) | Browser QA for BUILDOUT-07 verified the protected shell, Scout workspace, recipe library, and bulk run workspace on localhost:3000; captured screenshots; ran `pytest -m integration -q` in `packages/core` and confirmed the marker skips cleanly without real API keys. |
| 2026-05-08 | qa (gpt-5.4-mini) | Browser QA for BUILDOUT-05 verified Scout and recipe-library flows on localhost:3000, captured screenshots, confirmed clean console, and updated docs/report artifacts. |
| 2026-05-08 | qa (gpt-5.4-mini) | Browser QA for BUILDOUT-06 verified the shared-password login, Scout results page, and Gate pass/fail sort control on localhost:3000; captured screenshots and kept the console clean. |
| 2026-05-07 | hard-audit (Claude Opus 4.7) | Ground-up zero-trust audit. 8 parallel sub-agents, 4 live scout queries against real OpenAI ($0.045 spent), 65 findings across 8 dimensions plus Phase 2. 2 agent errors caught and corrected. Master report at `audits/hard-audit-2026-05-07.md`; action plan at `docs/06-audit-action-plan.md`. **Conclusion: not deployable as-is. 5 confirmed P0 blockers including `OPENAI_BASE_URL` routing to local Ollama and 89% VoIP leak rate in real leads.** |
