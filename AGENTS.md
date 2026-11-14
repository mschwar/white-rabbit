# AGENTS.md — White Rabbit

Canonical operating guide for agents working in `mschwar/white-rabbit`.

## What This Repo Is

White Rabbit is an internal-first B2B lead prospecting application for Matt, Thomas, and Lee:

- **Web (`apps/web`):** Next.js App Router UI and authenticated `/api/*` server-side proxy routes.
- **API (`apps/api`):** FastAPI + SQLAlchemy + PostgreSQL service enforcing `WR_API_INTERNAL_TOKEN` (`x-white-rabbit-internal-token`).
- **Core (`packages/core`):** Shared Python search, query planner/guardrails, SSRF-safe source validation, contact evidence, and lead scoring (`scout()`).

## Hard Guardrails

1. **Internal-only scope:** No public self-serve signup, multi-tenant orgs, or billing unless explicitly authorized by Matt.
2. **Secrets stay server-side:** Browser/client bundles never hold `OPENAI_API_KEY`, `TAVILY_API_KEY`, `DATABASE_URL`, or `WR_API_INTERNAL_TOKEN`. Never log raw credential-bearing URLs or tokens.
3. **All Web -> API traffic goes through authenticated Next.js route handlers:** Never add unauthenticated `vercel.json` rewrites to the FastAPI backend. Keep `GET /health` lightweight and non-leaking; keep `GET /readiness` and operational routes behind `ProtectedApiAccess`.
4. **Database & external I/O safety:** Never hold open DB transactions or row locks across external network/LLM calls (`scout()`, Tavily, OpenAI, HTTP fetches). Validate external URLs against SSRF and cap response body sizes.
5. **Runtime data belongs in package source:** Runtime data files live under `packages/core/src/core/data/`, never under `tests/fixtures/`.
6. **Worktree & merge hygiene:** Work on feature branches from `origin/main`, commit per logical step, lint touched Python files with `uvx ruff check`, verify locally, and merge only with human authorization per `ops/merge-policy.json` (`GitGuardian Security Checks` required; hosted cloud-VM PR runners retired).

## Key References

- [`README.md`](./README.md) — architecture, environment setup, and commands.
- [`STATUS.md`](./STATUS.md) — concise current repository status.
- [`TESTING.md`](./TESTING.md) — local test commands for `packages/core`, `apps/api`, and `apps/web`.
- [`docs/00-product-northstar.md`](./docs/00-product-northstar.md) — product scope and lead quality bar.
- [`docs/03-decisions.md`](./docs/03-decisions.md) — architectural decision records.
