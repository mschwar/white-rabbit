# STATUS

**Last updated:** 2026-05-06 by scout-harness QA session
**Branch:** feature/scout-harness
**Current sprint:** Sprint 1 (scaffold)

> Update this file at the end of every session. It is the source of truth for "where we are."

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

## What's in flight

Nothing.


## Next concrete task — Sprint 1 (scaffold)

Pick up here. Read `docs/04-roadmap.md` for full sprint scope, then:

### 1. Populate `packages/core` logic (Scout slice)
- Implement `orchestrator.py` logic (already scaffolded, needs verification with real keys).
- Implement `search.py` (Tavily integration).
- Verify with a smoke test.

### 2. Frontend implementation (Scout UI)
- Create `/scout` page in Next.js.
- Implement API proxy in `app/api/scout/route.ts`.
- Add shared-password auth middleware.

## Open questions for Matt

- Commercial arrangement with Lee and Thomas (free seats / revenue share / equity / content rights). Blocks the design-partner motion. **Not blocking Sprint 1 build, but blocks public usage.**
- Postgres host for Sprint 2 (Supabase / Neon / local Docker). Recommendation in `docs/02-stack.md` is Supabase for Sprint 2 since the demo already uses it.
- Cost-tracking source of truth: should live API cost figures be pulled from OpenAI/Tavily dashboards, or computed locally from token/call counts? Recommendation: compute locally per-run, reconcile weekly. See `docs/05-reuse.md` note on stale 2025 prices.

## Known issues / risks

- Pricing constants in `packages/core/core/cost.py` updated to 2026-05 estimates. Verify with real dashboard data after first few runs.
- Core smoke harness is in place; next Sprint 1 gap is shared-password auth middleware plus the Scout UI path.

## Session log

| Date | Agent | Summary |
|------|-------|---------|
| 2026-05-05 | bootstrap (Opus 4.7) | Repo bootstrapped. All 10 priority docs written. git init + first commit. Next: Sprint 1 scaffold. |
| 2026-05-05 | api-scaffold (Opus 4.7) | Scaffolded apps/api and packages/core. Lifted and adapted code from proxy-lead. Passed health check tests. |
| 2026-05-06 | scout-harness (gpt-5.4-mini) | Added injectable Scout smoke harnesses in core and API, fixed local import bootstraps, and verified core/API/web tests plus runtime imports. |
| 2026-05-06 | qa (gpt-5.4-mini) | Browser-checked the homepage and docs path, captured screenshots, and found no browser-visible issues. |
