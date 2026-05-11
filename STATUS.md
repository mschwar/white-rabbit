# STATUS

**Last updated:** 2026-05-11 by Codex prompt-b-r09-qa
**Branch:** rebuild/validated-leads-loop
**Current sprint:** The validated-leads rebuild is on `main` for Thomas/Lee internal use. Product remains red. Lee/Thomas operator feedback now makes low-volume broad runs a hard failure: Scout returning 3 rows and Full returning 4 rows is not useful. Matt has clarified that 10-25 was only the first escape from that failure; the reset now targets live-demo-safe high-volume transparent tiering for broad queries. Production web now has the required internal API token after the post-promotion Vercel env fix.

> Update this file at the end of every session. It is the source of truth for "where we are."

**Latest non-reset handoff:** Split `/Users/mschwar/Downloads/Generated Image May 10, 2026 - 10_17PM.jpg` into three 2048x2048 PNG logo assets under `apps/web/public/brand/`: light search mark, dark search mark, and standalone rabbit mark. Added a corrected top-half brand template crop at `docs/brand/assets/white-rabbit-top-half-template-2026-05-10.png` plus a draft design/brand schema at `docs/brand/white-rabbit-draft-design-brand-schema-2026-05-10.md` and `docs/brand/white-rabbit-brand-tokens.draft.json`. No product code, reset gate, or active feature status changed.

**Next pointer:** Prompt C should audit RG3 - Validation, Conflict, And Gate Semantics. R09 is merged to `rebuild/validated-leads-loop`. Do not unlock RG4 or sync `main` unless Prompt C records an advance and Matt explicitly asks for an operator-use promotion.

**Open question:** If these become production brand assets, replace the upscaled raster crops with a clean vector or native high-resolution source when available.

---

## Current rebuild status (2026-05-10)

**Operator-use branch:** `main`, promoted from `rebuild/validated-leads-loop` by ADR-010.

**Current gate:** Red with Matt-directed Thomas/Lee internal-use exception. Do not treat the promotion as a public launch or as evidence that the reset gates passed.

**Latest operator feedback:** On 2026-05-10, Matt reported that Lee and Thomas need Scout/Full to return more than 10 categorized results for broad targets because 3-4 rows provide no sales value. Matt then clarified that 10-25 is minimum escape velocity, not the ideal end state. The current direction is live-demo-safe high-volume transparent tiering: broad vertical + geography prompts should surface 50-500+ categorized candidates where the market supports it, while preserving a strict ready tier and explaining every non-actionable row.

**Next feature pointer:** None. R09 is the final RG3 feature and is merged; RG3 is ready for Prompt C audit. Do not unlock RG4 or sync `main`.

**Kickoff workflow:** Use only the reusable Prompt A/B/C loop in `docs/12-reset-gated-implementation-plan-2026-05-10.md`: Prompt A resolves and implements the single ready feature from current repo state, Prompt B resolves and QA/merges the single feature branch waiting for QA, and Prompt C resolves the current gate only after all features in that gate have merged. Prompt B may unlock the next feature inside the same in-progress gate after QA passes; Prompt C is the only prompt that can unlock the next gate or recommend a `main` operator-use sync. Do not use hard-coded R00/RG0 prompts from older chat turns or from stale docs.

**Final product mockup gate:** Inspect `docs/mockups/final-product-2026-05-10/index.html` before assigning Prompt A implementation. R10-R13 must treat it as the visual contract for live-demo high-volume tier distribution unless Matt approves a different direction; RG4/RG5 Prompt C audits must compare live screenshots against it.

**Current feature branch QA status:** R07, R08, and R09 are merged to `rebuild/validated-leads-loop`. RG3 is ready for Prompt C audit.

**Latest historical orchestrator review:** `.gstack/qa-reports/orchestrator-review-w1-f04-2026-05-10.md` accepted the W1 gate and F04 merge after rerunning W1/F04 verification. It also records the root cause of the earlier gate bypass: the old gate docs required reports but did not require an orchestrator acceptance checkpoint before agents unlocked downstream waves. Current reset advancement is governed by ADR-014 and `docs/12-reset-gated-implementation-plan-2026-05-10.md`.

**Latest gate acceptance:** W4 accepted on 2026-05-10. W5 remains explicitly held on `rebuild/validated-leads-loop`; RG0 advanced on 2026-05-10 as a control-plane reset audit; RG1 advanced on 2026-05-10 as a benchmark-harness audit; RG2 advanced on 2026-05-11 as a search/source coverage audit; and W6 remains blocked until the visible operator loop is proven:

- W4 benchmarks and quality reporting: `.gstack/qa-reports/gate-w4-benchmarks-quality.md`
- W5 operator loop export hold report: `.gstack/qa-reports/gate-w5-operator-loop-export.md`
- RG0 control reset gate report: `audits/gates/reset-2026-05-10/rg0-w5-hold.md`
- RG1 benchmark harness gate report: `audits/gates/reset-2026-05-10/rg1-benchmark-harness.md`
- RG2 search/source coverage gate report: `audits/gates/reset-2026-05-10/rg2-search-source-coverage.md`

**Latest reset control doc:** `docs/12-reset-gated-implementation-plan-2026-05-10.md` defines reset gates RG0-RG6. Every gate requires a full evaluation/audit report before downstream gate work unlocks. RG0 is advanced via `audits/gates/reset-2026-05-10/rg0-w5-hold.md`; RG1 is advanced via `audits/gates/reset-2026-05-10/rg1-benchmark-harness.md`; RG2 is advanced via `audits/gates/reset-2026-05-10/rg2-search-source-coverage.md`; RG3 is ready for Prompt C audit; and RG4 remains blocked.

Prior accepted gates:

- W2 search contract: `.gstack/qa-reports/gate-w2-search-contract.md`
- W3 validation engine: `.gstack/qa-reports/gate-w3-validation-engine.md`

**Control docs:**

- `docs/00-product-northstar.md` is the anti-drift product source of truth for the rebuild.
- `docs/12-reset-gated-implementation-plan-2026-05-10.md` is the active reset implementation queue, reusable Prompt A/B/C authority, and gate-audit contract.
- `docs/08-agentic-buildout-plan.md` is historical F00-F23 context overlaid by the reset plan.
- `docs/09-rebuild-phase-gates.md` is historical W0-W6 context overlaid by the reset plan.
- `docs/13-pipeline-orchestrator-contract-2026.md` is the live-demo pipeline/output contract sourced from Matt's spreadsheet artifacts.
- `docs/10-documentation-audit-2026-05-09.md` records the repo-wide documentation audit and remediation performed on this branch.
- `.gstack/qa-reports/qa-template-agentic-buildout.md` is a historical F00-F23 QA template; current reset QA follows Prompt B in `docs/12-reset-gated-implementation-plan-2026-05-10.md`.

**Main promotion override:** ADR-010 explicitly supersedes the prior "main untouched" operating rule for this promotion. `main` is now the operator-use deployment line, but the repo must still preserve the red-gate caveats, evidence requirements, and internal-only scope. Feature branches still merge to `rebuild/validated-leads-loop` first; `main` is synced only by explicit operator-use promotion.

**Production ops item resolved:** Vercel Production now has `WR_API_INTERNAL_TOKEN`; production was redeployed, and authenticated `/api/scout` no longer returns the missing-token 502.

**Production URL note:** Use the stable production alias `https://white-rabbit-ten.vercel.app/`, not one-off deployment URLs like `https://white-rabbit-7kw7lh6ri-matts-projects-06539e54.vercel.app/`. Vercel deployment URLs are immutable snapshots; `7kw7lh6ri` was created before `WR_API_INTERNAL_TOKEN` existed in Production and can continue to show the old missing-token error even after the alias is fixed.

**Latest handoff:**

Feature: R09 - Tier summary, score semantics, and reason language reset
Branch: `feat/reset-r09-tier-summary-semantics`
Status: `passed_prompt_b_qa`
What changed: Prompt A implemented R09 only, and Prompt B verified it. Core score semantics now cap evidence/contact signals after validation so unsupported fields and missing/failed contacts cannot retain strong-looking evidence/contact values. The reason language now starts with READY/REVIEW operator states and avoids old score-pass phrasing. Web result types now include `tier`, `primary_filter_reason`, and `metrics.tier_distribution`; the results view shows a tier summary and uses readiness/signal labels instead of score/gate-centric copy.
Tests or QA run:
- `git diff --check` (passed)
- `cd packages/core && uv run pytest tests/test_source_validation.py tests/test_contact_status.py tests/test_scoring.py tests/test_orchestrator.py -q` (`48 passed in 1.04s`)
- `cd apps/api && WR_API_INTERNAL_TOKEN=test-internal-token uv run pytest tests -q` (`43 passed in 2.86s`, 50 existing datetime deprecation warnings)
- `cd apps/web && npm test -- --run` (`13 test files / 30 tests passed`)
- `cd apps/web && npm run build` (passed; existing Next.js workspace-root and middleware deprecation warnings)
- Playwright browser QA on `http://localhost:3007/scout?qa=validation-buckets` (desktop and mobile fixture tier summary rendered with READY, REVIEW, ORG-ONLY, and NOT FOUND rows)
Screenshots or report: `.gstack/qa-reports/qa-report-r09-tier-summary-semantics-2026-05-11.md`, `.gstack/qa-reports/screenshots/r09-prompt-b-desktop.png`, and `.gstack/qa-reports/screenshots/r09-prompt-b-mobile.png`. No UI redesign, RG4 work, export rewrite, or `main` sync was done.
Northstar reflection: R09 reduces false confidence by making READY depend on validation-backed tiering while keeping review, organization-only, not-found, and failed rows visible with explicit reasons and tier counts.
Exact Prompt C handoff: Audit RG3 - Validation, Conflict, And Gate Semantics on `rebuild/validated-leads-loop`. Confirm R07-R09 are merged, run the RG3 full evaluation/audit from `docs/12-reset-gated-implementation-plan-2026-05-10.md`, and write `audits/gates/reset-2026-05-10/rg3-validation-semantics.md`. Do not unlock RG4 unless Prompt C records an `advance`; do not sync `main`.
Next pointer: Prompt C for RG3.
Open questions: Local browser API startup is still affected by an existing Ollama-routed OpenAI env mismatch (`gpt-4o-mini` not available at `http://localhost:11434/v1`); this did not block API tests or fixture browser QA, but Prompt C should use the intended live/replay environment for gate evidence.

Previous handoff:

Feature: R08 - Tiering engine, field validator, and conflict resolver
Branch: `feat/reset-r08-tier-validation-conflicts`
Status: `passed_prompt_b_qa`
What changed: Prompt A implemented R08 only, and Prompt B verified it. Candidates now carry server-computed `tier` and `primary_filter_reason`; person rows can become `high_trust_usable`, `review`, or explicit `failed` rows after validation; inaccessible sources and failed core field validation downgrade unsafe person rows to `FailedCandidate`; person/account conflicts are flagged and downgraded; validated contact status is synchronized back onto person rows so unsupported, missing, or failed contact evidence cannot remain CRM-ready; and run metrics now expose `tier_distribution`.
Tests or QA run:
- `git diff --check` (passed)
- `cd packages/core && uv run pytest tests/test_source_validation.py tests/test_contact_status.py tests/test_scoring.py tests/test_orchestrator.py -q` (`46 passed in 0.37s`)
- `cd apps/api && WR_API_INTERNAL_TOKEN=test-internal-token uv run pytest tests -q` (`43 passed in 0.85s`, 50 existing datetime deprecation warnings)
Screenshots or report: non-UI implementation; no browser screenshots required. Prompt B QA report saved at `.gstack/qa-reports/qa-report-r08-tier-validation-conflicts-2026-05-11.md`.
Northstar reflection: R08 keeps the binary evidence gate as the only `high_trust_usable` path while keeping review/org-only/not-found/failed rows visible with grounded primary reasons. It reduces false confidence by preventing unsupported contact evidence and inaccessible sources from appearing CRM-ready.
Exact Prompt A handoff: Implement R09 on `feat/reset-r09-tier-summary-semantics`. Keep scope to tier summary, score semantics, and reason language reset; do not start RG4, do not unlock the next gate, and do not touch `main`.
Next pointer: Prompt A for R09.
Open questions: None for R09 kickoff; RG3 still requires R09 and Prompt C audit before any gate advancement.


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
- **F13 QA complete on `feat/f13-single-search-ui`.** The root route now renders the primary lead-search workspace with one natural-language input, Scout/Full mode toggles hidden from the primary screen, and the shared workspace component can render in primary mode. Browser QA on `/` captured empty, loading, and validation-error states.
- **F15 is merged to `rebuild/validated-leads-loop` from `feat/f15-evidence-drawer`.** The results table now exposes a right-side evidence drawer per row with field-level status, source URL, checked_at, notes, and evidence snippet for usable and failed/noisy rows. Vitest, Next.js build, and browser QA on the local validation fixture all passed; screenshot pair saved at:
  - `.gstack/qa-reports/screenshots/f15-01-usable-evidence-drawer.png`
  - `.gstack/qa-reports/screenshots/f15-02-failed-evidence-drawer.png`
  - QA report: `.gstack/qa-reports/qa-report-f15-evidence-drawer-2026-05-10.md`
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

- Product is in audit-red state. Documentation authority remediation is complete; F01-F19 are merged to `rebuild/validated-leads-loop`, but the May 10 audit found the visible loop still fails live operator benchmarks. W2, W3, and W4 are orchestrator-accepted. R00-R09 are merged; RG2 advanced as a search/source coverage gate; RG3 is ready for Prompt C audit; W5 remains held; W6 remains blocked.

## Next concrete task

- Run Prompt C for RG3 - Validation, Conflict, And Gate Semantics on `rebuild/validated-leads-loop`. Do not unlock RG4 or sync `main`.

## Open questions for Matt

- Commercial arrangement with Lee and Thomas (free seats / revenue share / equity / content rights). Blocks the design-partner motion. **Not blocking Sprint 1 build, but blocks public usage.**
	- Answer: not relevant.
- Cost-tracking source of truth: should live API cost figures be pulled from OpenAI/Tavily dashboards, or computed locally from token/call counts? Recommendation: compute locally per-run, reconcile weekly. See `docs/05-reuse.md` note on stale 2025 prices.
	- Both. Only should be viewable internally.
- Access boundary for the Friday guarded version: local handoff, deployed internal URL, or Matt-run sessions?
	- answer: deployed internal URL
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
| 2026-05-11 | prompt-b-r09-qa (Codex) | QA-passed `R09 - Tier summary, score semantics, and reason language reset` on `feat/reset-r09-tier-summary-semantics`: verified `git diff --check`, the required core/API suite, web tests/build, browser fixture screenshots, northstar drift, and that no R10-R14, RG4, export, persistence, or `main` work landed. Report saved at `.gstack/qa-reports/qa-report-r09-tier-summary-semantics-2026-05-11.md`. R09 is the last RG3 feature, so RG3 is ready for Prompt C audit after merge; RG4 remains blocked. |
| 2026-05-11 | prompt-a-r09-implementation (Codex) | Implemented `R09 - Tier summary, score semantics, and reason language reset` on `feat/reset-r09-tier-summary-semantics`: capped evidence/contact signals from field validation, reset READY/REVIEW primary reason language, typed web tier metadata, and added tier distribution summary/copy updates without starting RG4 UI work. Verified required core/API/web tests and `git diff --check`; branch is pending Prompt B QA and merge. |
| 2026-05-11 | prompt-b-r08-qa (Codex) | QA-passed `R08 - Tiering engine, field validator, and conflict resolver` on `feat/reset-r08-tier-validation-conflicts`: verified `git diff --check`, the required core validation/contact/scoring/orchestrator suite, full API tests, non-UI scope, northstar drift, and that no R09 score-language, UI, export, persistence, or gate-audit work landed. Report saved at `.gstack/qa-reports/qa-report-r08-tier-validation-conflicts-2026-05-11.md`. R09 is the next same-gate feature; RG4 remains blocked. |
| 2026-05-11 | prompt-a-r08 (Codex) | Implemented `R08 - Tiering engine, field validator, and conflict resolver` on `feat/reset-r08-tier-validation-conflicts`: added server-computed candidate tiers and primary filter reasons, synchronized contact status from field validation, downgraded inaccessible-source and person/account conflict rows to explicit failed candidates, and exposed run-level tier distribution metrics. Verified the required R08 core suite, full API tests, and `git diff --check`; branch is pending Prompt B QA and merge. |
| 2026-05-11 | prompt-b-r07-qa (Codex) | QA-passed `R07 - Inclusive extraction prompt and candidate parse salvage` on `feat/reset-r07-inclusive-extraction`: verified `git diff --check`, the required core extraction/scoring/source-validation suite, full API tests, non-UI scope, northstar drift, and that no R08/R09 tier/conflict/score-language work landed. Report saved at `.gstack/qa-reports/qa-report-r07-inclusive-extraction-2026-05-11.md`. R08 is the next same-gate feature after the R07 merge lands; RG4 remains blocked. |
| 2026-05-11 | prompt-c-rg2-audit (Codex) | Ran the RG2 search/source coverage gate audit on `audit/reset-rg2-search-source-coverage`: live Scout/Full benchmarks plus direct source snapshots showed all 8 Thomas Arizona K-12 accounts represented and 73-90 deduped raw sources for broad prompts, while final product output remains low-volume with 0 high-trust usable rows. RG2 advanced as a source-coverage gate, product remains red, and R07 is now the next ready Prompt A feature. |
| 2026-05-11 | prompt-b-r06-qa (Codex) | QA-passed `R06 - Not-found and organization-only coverage writer` on `feat/reset-r06-nonperson-coverage`: verified the required RG2 core suite, `git diff --check`, focused coverage/orchestrator regressions, northstar drift, and scope boundaries. Report saved at `.gstack/qa-reports/qa-report-r06-nonperson-coverage-2026-05-11.md`. R06 is the last RG2 feature, so RG2 is ready for Prompt C audit after merge; RG3 remains blocked. |
| 2026-05-11 | prompt-a-r06-nonperson-coverage (Codex) | Implemented `R06 - Not-found and organization-only coverage writer` on `feat/reset-r06-nonperson-coverage`: added a core coverage writer that appends explicit `organization_only` rows for uncovered named-account obligations with collected source support and `not_found` rows when no source coverage exists, without duplicating existing account rows or changing person-lead scoring/gating. Verified core coverage/orchestrator tests plus the required RG2 core suite; branch is pending Prompt B QA and merge. |
| 2026-05-11 | prompt-b-r05-qa (Codex) | QA-passed `R05 - Source collection and snapshot store` on `feat/reset-r05-source-collection-store`: verified the required core test suite, `git diff --check`, raw source fixture integrity, northstar drift, and scope boundaries. Report saved at `.gstack/qa-reports/qa-report-r05-source-collection-store-2026-05-11.md`. R06 is the next same-gate feature after the R05 merge lands; RG3 remains blocked. |
| 2026-05-11 | prompt-a-r05-source-collection (Codex) | Implemented `R05 - Source collection and snapshot store` on `feat/reset-r05-source-collection-store`: added structured `source_collection.v1` snapshots for deduped search sources, stable source IDs, content hashes, query-plan payloads, vendor-query provenance, an optional snapshot-store interface, and the canonical raw source fixture at `packages/core/tests/fixtures/raw_source_collection_snapshot.json`. Verified the required R05 core tests; branch is pending Prompt B QA and merge. |
| 2026-05-10 | prompt-a-r04-high-volume-search (Codex) | Implemented `R04 - High-volume query planner and search aggregation` on `feat/reset-r04-high-volume-search`: full Arizona K-12 account coverage planning, broad-query vendor-query fanout, normal/aggressive breadth controls, Tavily per-call cap handling, client-side aggregation/dedupe with matched-query provenance, and `scout()` raw-result controls. Verified required R04 tests plus adjacent/all core tests; branch is pending Prompt B QA and merge. |
| 2026-05-10 | rg1-audit-merge-fix (Codex) | Fast-forward merged `audit/reset-rg1-benchmark-harness` into `rebuild/validated-leads-loop` so the RG1 advance and R04-ready state are visible to Prompt A. Updated Prompt C instructions to require merging accepted gate-advance audit branches back into the integration branch before the next Prompt A. |
| 2026-05-10 | prompt-b-r03-live-benchmark-runner (Codex) | QA-passed and merged `R03 - Live benchmark runner and quality summary` into `rebuild/validated-leads-loop`, wrote `.gstack/qa-reports/qa-report-r03-live-benchmark-runner-2026-05-10.md`, reran the protected local API benchmark suite, refreshed `audits/raw/reset-2026-05-10/rg1/` to current live evidence, and marked RG1 as gate-pending-audit with Prompt C as the next pointer. |
| 2026-05-10 | prompt-a-r03-live-benchmark-runner (Codex) | Implemented `R03 - Live benchmark runner and quality summary` on `feat/reset-r03-live-benchmark-runner`: added the executable runner plus CLI path, saved-artifact observation parsing, automatic sandbox reset before suite execution, targeted runner tests, and live RG1 artifacts under `audits/raw/reset-2026-05-10/rg1/`. |
| 2026-05-10 | prompt-b-r02-benchmark-replay-harness (Codex) | QA-passed and merged `R02 - Golden benchmark replay harness` into `rebuild/validated-leads-loop`, wrote `.gstack/qa-reports/qa-report-r02-benchmark-replay-harness-2026-05-10.md`, confirmed replay-harness scope stayed inside `packages/core` plus reset control docs, and marked `R03 - Live benchmark runner and quality summary` as the next same-gate ready feature. |
| 2026-05-10 | prompt-a-r02-benchmark-replay-harness (Codex) | Implemented `R02 - Golden benchmark replay harness` on `feat/reset-r02-benchmark-replay-harness`: added offline replay observations over the saved May 10 RG1 artifacts, reused canonical candidate parsing plus quality-report logic, tracked target coverage and broad-query volume failures, preserved Detroit `503 openai_failed` evidence and B2C refusal replay, and added tests proving the replay suite fails current bad outputs offline. |
| 2026-05-10 | reset-queue-unblock (Codex) | Fixed the post-R01 queue state: Prompt B may unlock the next feature inside the same gate, R02 is ready, R03 remains blocked, and `.obsidian/` is ignored so local editor metadata does not dirty the integration branch. |
| 2026-05-10 | prompt-loop-fix (Codex) | Replaced stale hard-coded R00/RG0 copy-paste prompts with reusable A/B/C prompts that resolve the next feature, QA branch, and gate from current repo state, with stop rules for duplicate or ambiguous assignments. |
| 2026-05-10 | frontier-control-plane-audit (Codex) | Audited and hardened the remaining authority surfaces: AGENTS, ADRs, docs/08, docs/09, docs/12 prompt authority, archived doc banners, tracked QA-log supersession notes, and the control-plane audit report. R02 remains the next Prompt A feature. |
| 2026-05-10 | mockup-copy-tightening (Codex) | Tightened only the final mockup copy: removed top tagline, pipeline-stage row, and principle list from the first screen; rewrote low-signal guidance into a concrete diagnosis plus exact broadening suggestions. |
| 2026-05-10 | live-demo-pipeline-mockups (Codex) | Read Matt's CSV/XLSX pipeline artifacts, added ADR-013 and `docs/13-pipeline-orchestrator-contract-2026.md`, updated the orchestrator brief/reset docs, and rebuilt the mockups for live-demo copy, 50-500+ transparent tiering, filters, evidence actions, mobile review, and low-signal state. |
| 2026-05-10 | high-volume-reset-contract (Codex) | Superseded the 10-25 ideal with ADR-012 high-volume transparent tiering, added `docs/Orchestrator_Agent_Implementation_Brief.md`, updated the northstar/reset plan, and revised the final product mockups to show 186 categorized candidates with high-trust/review/org-only/not-found/failed distribution. |
| 2026-05-10 | final-product-mockups (Codex) | Added `docs/mockups/final-product-2026-05-10/index.html` and rendered screenshots so Matt can inspect the final intended operator product before kickoff. Wired the mockup into the reset plan as the R10-R13 visual contract and RG4/RG5 Prompt C comparison artifact. |
| 2026-05-10 | pre-kickoff-review (Codex) | Ran a ruthless final review of the reset plan against the northstar and true value prop. Tightened `docs/12-reset-gated-implementation-plan-2026-05-10.md` to a strict Prompt A/B/C kickoff loop, added a 24-hour product bar, made Prompt C the only gate unlock/main-promotion recommender, added live-evidence rules, and wrote first Prompt B/C assignments so R00 cannot drift into another ambiguous gate bypass. |
| 2026-05-10 | stale-deployment-url-check (Codex) | Checked Matt's reported `white-rabbit-7kw7lh6ri...` URL and confirmed it is an old immutable production deployment created before the env fix. Verified the stable production alias points at the newer `white-rabbit-jcrn58h0c...` deployment and that authenticated `/api/scout` on `https://white-rabbit-ten.vercel.app/` returns 200 instead of the missing-token 502. |
| 2026-05-10 | branch-policy-reconcile (Codex) | Reconciled the docs after Matt confirmed Thomas/Lee asked to use the latest version and `rebuild/validated-leads-loop` was pushed to `main`: `main` is now the operator-use deployment line, while feature work still targets `rebuild/validated-leads-loop` first and only syncs to `main` by explicit promotion. |
| 2026-05-10 | prod-env-fix-verified (Codex) | Completed the post-promotion Vercel env fix: confirmed Production has `WR_API_INTERNAL_TOKEN`, redeployed with `vercel deploy --prod --yes`, and verified an authenticated live `POST /api/scout` reaches the protected API instead of returning "Missing WR_API_INTERNAL_TOKEN." |
| 2026-05-10 | prod-env-fix (Codex) | Investigated the live Scout error "Missing WR_API_INTERNAL_TOKEN", confirmed Vercel production lacked the web-side server env var while local API/web envs matched, added `WR_API_INTERNAL_TOKEN` to Vercel Production, and started redeploy/verification. |
| 2026-05-10 | main-promotion (Codex) | Recorded ADR-010 for Matt-directed Thomas/Lee internal operator use, updated the northstar red-gate exception, fixed API/core tests that leaked local env vars, verified web/API/core suites, fast-forwarded `main` to `rebuild/validated-leads-loop`, pushed `main`, confirmed the GitHub production workflow passed, and smoke-checked Fly health plus the Vercel login/Scout boundary. |
| 2026-05-10 | f19-qa (Codex) | QA'd `feat/f19-batch-internal-only` with `cd apps/web && npm test -- --run src/app/__tests__/page.test.tsx src/components/__tests__/batch-workspace.test.tsx`, `cd apps/web && npm run build`, and browser verification on `http://localhost:3000/` plus `http://localhost:3000/batch`; found that `/` already hid batch but `/batch` needed explicit internal-only framing, added that warning copy, captured `.gstack/qa-reports/screenshots/f19-01-home-no-batch-nav.png` and `.gstack/qa-reports/screenshots/f19-02-batch-internal-only.png`, wrote `.gstack/qa-reports/qa-report-f19-batch-internal-only-2026-05-10.md`, and prepared the branch for merge into `rebuild/validated-leads-loop`. |
| 2026-05-10 | f19-build (Codex) | After promoting F19 on `rebuild/validated-leads-loop`, created and pushed `feat/f19-batch-internal-only`. No product code changes were required because batch was already hidden by F01, so the branch now carries the isolated F19 QA handoff: Prompt B should verify `/` still omits batch from primary nav and record the screenshot evidence from the card. |
| 2026-05-10 | f19-promotion (Codex) | Matt explicitly promoted F19 only. Updated `docs/08-agentic-buildout-plan.md` and `STATUS.md` so `F19` is the sole `ready` deferred follow-on feature, with explicit instructions that Prompt A should create `feat/f19-batch-internal-only` next and Prompt B should QA only that card verification afterward. |
| 2026-05-10 | build-loop-blocked-no-ready-feature (Codex) | Re-read AGENTS plus the active rebuild docs, fast-forward checked `rebuild/validated-leads-loop` against `origin/rebuild/validated-leads-loop`, and revalidated that no feature card is currently `ready`. F19-F23 remain intentionally `deferred`, so no feature branch was created and the next build prompt needs Matt to explicitly promote one deferred internal-only feature or change the red-gate policy first. |
| 2026-05-10 | f18-qa (Codex) | QA'd `feat/f18-recipes-internal-only` with `cd apps/web && npm test -- --run src/components/__tests__/recipes-library.test.tsx src/app/__tests__/page.test.tsx`, `cd apps/web && npm run build`, and browser verification on `http://localhost:3000/` plus `http://localhost:3000/recipes`; confirmed `/` still has no recipe navigation, confirmed `/recipes` is explicitly labeled internal evaluation only, captured `.gstack/qa-reports/screenshots/f18-01-home-no-recipe-nav.png` and `.gstack/qa-reports/screenshots/f18-02-recipes-internal-only.png`, wrote `.gstack/qa-reports/qa-report-f18-recipes-internal-only-2026-05-10.md`, and prepared the branch for merge into `rebuild/validated-leads-loop`. |
| 2026-05-10 | f16-export (Codex) | Built `feat/f16-validation-export` with validation-aware CSV export rows, updated the Scout workspace export flow, and added a QA-only fixture hook for `qa=validation-buckets`. Verified with `cd apps/web && npm test -- --run src/lib/__tests__/full-export.test.ts src/components/__tests__/scout-workspace.test.tsx` (`9` passed) and browser QA on `http://localhost:3000/scout?qa=validation-buckets`; screenshots saved at `.gstack/qa-reports/screenshots/f16-01-export-control.png`, `.gstack/qa-reports/screenshots/f16-02-export-ready.png`, and `.gstack/qa-reports/screenshots/f16-03-csv-content.png`. |
| 2026-05-10 | f15-qa (Codex) | QA'd `feat/f15-evidence-drawer` with `cd apps/web && npm test -- --run` (`13` passed), `cd apps/web && npm run build`, and browser verification on `http://localhost:3000/scout?qa=validation-buckets`; captured `.gstack/qa-reports/screenshots/f15-01-usable-evidence-drawer.png` and `.gstack/qa-reports/screenshots/f15-02-failed-evidence-drawer.png`; wrote `.gstack/qa-reports/qa-report-f15-evidence-drawer-2026-05-10.md`; updated `docs/08-agentic-buildout-plan.md` and `STATUS.md`; merged the branch into `rebuild/validated-leads-loop`. |
| 2026-05-10 | f14-qa (Codex) | QA'd `feat/f14-validation-results-table` with `cd apps/web && npm test -- --run` (`28` passed), `cd apps/web && npm run build`, and browser verification on `http://localhost:3000/?qa=validation-buckets`; captured usable, noisy/failed, and organization-only/not-found screenshots; wrote `.gstack/qa-reports/qa-report-f14-validation-results-table-2026-05-10.md`; updated `docs/08-agentic-buildout-plan.md` and `STATUS.md`; merged the branch into `rebuild/validated-leads-loop`. |
| 2026-05-10 | orchestrator-gate-check (Codex) | Checked W4 after F10-F12, found the feature agents had merged F13 before formal W4 acceptance, added explicit quality-report threshold failures for zero-usable/high-noise runs, passed W4 verification (`11 passed, 1 skipped`), wrote `.gstack/qa-reports/gate-w4-benchmarks-quality.md`, accepted W4, and unlocked F14 while keeping the product red. |
| 2026-05-10 | f13-qa (Codex) | QA'd `feat/f13-single-search-ui` with `cd apps/web && npm test -- src/app/__tests__/page.test.tsx src/components/__tests__/scout-workspace.test.tsx` and browser verification on `http://localhost:3000/`; captured empty, loading, and error-state screenshots; wrote `.gstack/qa-reports/qa-report-f13-single-search-ui-2026-05-10.md`; updated `docs/08-agentic-buildout-plan.md` and `STATUS.md`; merged the branch into `rebuild/validated-leads-loop`. |
| 2026-05-09 | f11-qa (Codex) | QA'd `feat/f11-required-benchmark-suite` with offline suite verification (`3 passed`), wrote `.gstack/qa-reports/qa-report-f11-required-benchmark-suite-2026-05-09.md`, updated `docs/08-agentic-buildout-plan.md` and `STATUS.md`, and merged the feature branch into `rebuild/validated-leads-loop`. |
| 2026-05-10 | orchestrator-gate-check (Codex) | Checked the next gates after F09, accepted W2 and W3 with reports, added missing `packages/core/tests/test_scoring.py` so W3's documented command passes, and unlocked F10 while keeping the product red. |
| 2026-05-10 | f06-qa (Codex) | QA'd `feat/f06-field-validation-schema` with required non-UI verification and merged it into `rebuild/validated-leads-loop`; wrote `.gstack/qa-reports/qa-report-f06-field-validation-schema-2026-05-10.md` and updated docs handoff/status. |
| 2026-05-10 | f06-build (Codex) | Implemented field-level validation schema on `feat/f06-field-validation-schema`: added explicit per-field validation records to all candidate types, defaulted untouched rows to unsupported validation, and verified core model tests plus Scout/Full API serialization. |
| 2026-05-10 | f05-qa (Codex) | QA'd and merged `feat/f05-candidate-types` into `rebuild/validated-leads-loop` after required non-UI checks passed (`25` model tests, `10` scout API tests); wrote `.gstack/qa-reports/qa-report-f05-candidate-model-separation-2026-05-10.md` and updated `docs/08-agentic-buildout-plan.md` + `STATUS.md`. |
| 2026-05-10 | f05-build (Codex) | Implemented candidate model separation on `feat/f05-candidate-types`: split person_lead from organization_only/not_found/failed rows, added company-as-person and role-only rejection, preserved candidate_category through core/API responses, and passed the required non-UI tests. Branch is pending QA/merge; W3 remains blocked. |
| 2026-05-10 | orchestrator-review (Codex) | Reviewed F01-F04 against the northstar and gate docs, accepted W1/F04 evidence while keeping the product red, fixed F04 Tavily-search metrics, reconciled F04/F05 doc status drift, added ADR-007, and updated gate mechanics so downstream waves require orchestrator acceptance before unlock. |
| 2026-05-10 | f04-qa (Codex) | QA'd `feat/f04-query-compiler` with required tests (`5 passed`) and long-Arizona bounded-query verification (`8` named-account queries, max length `86/380`), wrote `.gstack/qa-reports/qa-report-f04-query-compiler-2026-05-10.md`, and updated `docs/08-agentic-buildout-plan.md` plus `STATUS.md` for merge handoff. |
| 2026-05-09 | f04-build (Codex) | Implemented F04 query compiler/planner on `feat/f04-query-compiler`: added `packages/core/src/core/query_planner.py`, rewired Tavily search to compile bounded vendor queries, added planner and long-AZ decomposition tests, and verified `cd packages/core && uv run pytest tests/test_query_planner.py tests/test_search.py -q` (5 passed). |
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
