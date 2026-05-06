# STATUS

**Last updated:** 2026-05-05 by bootstrap session
**Branch:** main
**Current sprint:** Bootstrap → Sprint 1 (scaffold)

> Update this file at the end of every session. It is the source of truth for "where we are."

## What's done

- Repo created at `/Users/mschwar/Documents/white-rabbit/`.
- Directory structure scaffolded (`docs/`, `apps/web/`, `apps/api/`, `packages/core/` with `.gitkeep` placeholders).
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


## What's in flight

Nothing. Bootstrap session ended cleanly.

## Next concrete task — Sprint 1 (scaffold)

Pick up here. Read `docs/04-roadmap.md` for full sprint scope, then:

### 1. Scaffold `apps/web` (Next.js)

```bash
cd /Users/mschwar/Documents/white-rabbit/apps
rm -rf web && npx create-next-app@latest web --typescript --app --tailwind --eslint --src-dir --import-alias "@/*" --no-turbopack
```

Verify: `cd web && npm run dev` serves at http://localhost:3000.

### 2. Scaffold `apps/api` (FastAPI + uv)

```bash
cd /Users/mschwar/Documents/white-rabbit/apps
rm -rf api && uv init --package api && cd api && uv add fastapi uvicorn pydantic python-dotenv httpx openai tavily-python
```

Verify: minimal `uv run uvicorn api:app --reload` starts on http://localhost:8000.

If `uv` is not installed, install it: `curl -LsSf https://astral.sh/uv/install.sh | sh`. Poetry is acceptable as fallback (see `docs/02-stack.md`).

### 3. Lift code into `packages/core`

Per `docs/05-reuse.md`, copy and adapt these files from `/Users/mschwar/Documents/proxy-lead/`:

- `models.py` → `packages/core/models.py` (add `fit_score`, `evidence_score`, `contact_score`, `gate_passed`, `explanation` fields)
- `tavily_validation.py` → `packages/core/search.py` (extract just the search primitive; drop validation-suite scaffolding)
- `email_patterns.py` → `packages/core/email_patterns.py` (lift cleanly)
- `history_store.py` → `packages/core/cost.py` (lift the pricing constants and cost calculation; **update prices to current 2026 rates** — see reuse doc)
- `agent.py` → reference only; rewrite the orchestration in `packages/core/orchestrator.py` without LangChain (use `openai` SDK direct + `tavily-python`)

Do **not** lift: `app.py`, `demo_data.py`, `results_summary.py`, `config.py`, anything Streamlit-coupled, anything PDF-related.

### 4. Wire shared-password auth

Next.js middleware (`apps/web/src/middleware.ts`) intercepts every request, checks a session cookie set by a single `POST /login` route. Password is read from env var `WR_SHARED_PASSWORD`. Compare with `crypto.timingSafeEqual` to avoid timing attacks. See `docs/02-stack.md` for the full pattern.

### 5. End-to-end smoke

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

- Pricing constants in `proxy-lead/history_store.py` are dated "as of 2025-04". Today is 2026-05. Update to current OpenAI and Tavily rates before they're used in any cost-per-usable-lead calculations. Tavily moved to credit-based pricing; OpenAI added `web_search_preview` at $10/1k calls. See `docs/05-reuse.md`.
- No tests yet. Sprint 1 should land at least smoke tests for the orchestrator and the auth middleware before Sprint 2.

## Session log

| Date | Agent | Summary |
|------|-------|---------|
| 2026-05-05 | bootstrap (Opus 4.7) | Repo bootstrapped. All 10 priority docs written. git init + first commit. Next: Sprint 1 scaffold. |
