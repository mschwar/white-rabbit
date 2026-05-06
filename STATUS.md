# STATUS

**Last updated:** 2026-05-05 by api-scaffold session
**Branch:** feat/sprint-1-scaffold-api
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

### 3. Wire shared-password auth

Next.js middleware (`apps/web/src/middleware.ts`) intercepts every request, checks a session cookie set by a single `POST /login` route. Password is read from env var `WR_SHARED_PASSWORD`. Compare with `crypto.timingSafeEqual` to avoid timing attacks. See `docs/02-stack.md` for the full pattern.

### 4. End-to-end smoke

Next.js form → `POST /api/scout` → forwards to FastAPI `POST /scout` → calls `core.orchestrator.scout(query)` → returns 10–20 leads with three scores → Next.js renders.

Definition of done for Sprint 1:
- Thomas can log in with the shared password from his laptop.
- Thomas types "K-12 IT directors in Albuquerque" and sees a Scout result with Fit/Evidence/Contact per lead within 30 seconds.
- The result includes the per-lead explanation string.
- API and web both run with `npm run dev` and `uv run uvicorn …`. No deploy yet.

## Open questions for Matt

- Commercial arrangement with Lee and Thomas (free seats / revenue share / equity / content rights). Blocks the design-partner motion. **Not blocking Sprint 1 build, but blocks public usage.**
- Postgres host for Sprint 2 (Supabase / Neon / local Docker). Recommendation in `docs/02-stack.md` is Supabase for Sprint 2 since the demo already uses it.
- Cost-tracking source of truth: should live API cost figures be pulled from OpenAI/Tavily dashboards, or computed locally from token/call counts? Recommendation: compute locally per-run, reconcile weekly. See `docs/05-reuse.md` note on stale 2025 prices.

## Known issues / risks

- Pricing constants in `packages/core/core/cost.py` updated to 2026-05 estimates. Verify with real dashboard data after first few runs.
- No tests yet for orchestrator (requires real keys). Sprint 1 should land at least smoke tests for the orchestrator and the auth middleware before Sprint 2.

## Session log

| Date | Agent | Summary |
|------|-------|---------|
| 2026-05-05 | bootstrap (Opus 4.7) | Repo bootstrapped. All 10 priority docs written. git init + first commit. Next: Sprint 1 scaffold. |
| 2026-05-05 | api-scaffold (Opus 4.7) | Scaffolded apps/api and packages/core. Lifted and adapted code from proxy-lead. Passed health check tests. |
