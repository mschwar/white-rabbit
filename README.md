# White Rabbit v2

Internal-first B2B lead research tool for Matt, Thomas, and Lee.

> **Current state:** Red-gate validated-leads rebuild. Do not ship and do not use for Thomas/Lee daily dogfood until the benchmark gates say otherwise.

AI agents must read [`AGENTS.md`](./AGENTS.md), [`STATUS.md`](./STATUS.md), [`docs/00-product-northstar.md`](./docs/00-product-northstar.md), [`docs/08-agentic-buildout-plan.md`](./docs/08-agentic-buildout-plan.md), and [`docs/09-rebuild-phase-gates.md`](./docs/09-rebuild-phase-gates.md) before working.

Humans should start with [`docs/00-product-northstar.md`](./docs/00-product-northstar.md) for current product truth and [`STATUS.md`](./STATUS.md) for current branch/state.

## What This Is

White Rabbit is being rebuilt around one core loop:

```text
natural-language B2B target
  -> checked candidates
  -> field-level evidence
  -> ranked validated rows
  -> export with validation context
```

It does not win by returning the most leads. It wins only if it returns better, more trustworthy lead data than ZoomInfo/DiscoverOrg-style lists: real people, right persona, source-backed title/org/contact data, and explicit missing/failed states.

## What This Is Not

- Not the frozen Scotty demo. That reference app lives outside this repo (`C:\Users\Matty\Documents\proxy-lead` in this workspace; older docs may mention `/Users/mschwar/Documents/proxy-lead`) and must not be edited.
- Not a public SaaS. No signup, orgs, billing, or customer self-serve access.
- Not green for Thomas/Lee daily use. The product remains red until benchmark and browser gate evidence says otherwise.
- Not currently a recipe/batch-first workbench. Recipes, batch, scoreboards, Friday review, and sandbox reset are internal/deferred while the product is red.

## Current Authority Docs

When docs conflict, use this order:

1. [`docs/03-decisions.md`](./docs/03-decisions.md) for locked ADR history.
2. [`docs/00-product-northstar.md`](./docs/00-product-northstar.md) for current product truth and launch gates.
3. [`STATUS.md`](./STATUS.md) for current repo state and next pointer.
4. [`docs/08-agentic-buildout-plan.md`](./docs/08-agentic-buildout-plan.md) for rebuild feature sequencing.
5. [`docs/09-rebuild-phase-gates.md`](./docs/09-rebuild-phase-gates.md) for wave-gate rules.
6. [`docs/qa-rubric.md`](./docs/qa-rubric.md) for QA tiers.

Older roadmap, BUILDOUT, audit, QA, and meeting docs are historical unless their status banner says `Active`.

## Stack

- Web: Next.js 16.2.4 App Router, React 19.2.4, TypeScript, Tailwind 4.
- API: FastAPI 0.136+, Python 3.12+, SQLAlchemy 2.0+, Alembic 1.18+.
- Core: shared Python package for search, guardrails, scoring, and extraction primitives.
- DB: Postgres.
- Boundary: shared password for the app plus `WR_API_INTERNAL_TOKEN` for web-to-API calls.

Frontend code never holds OpenAI/Tavily keys. Third-party search/extraction calls happen in the Python service.

## Local Setup

### Prerequisites

- Node.js 22+ and `npm`
- Python 3.12+ and `uv`
- Docker Desktop or compatible Docker CLI
- OpenAI and Tavily API keys if running live search paths

### 1. Configure Environment

Copy env examples:

```bash
cp .env.example .env
cp apps/api/.env.example apps/api/.env
cp apps/web/.env.example apps/web/.env.local
```

Set these values:

| Variable | Files | Purpose |
| --- | --- | --- |
| `OPENAI_API_KEY` | `.env`, `apps/api/.env` | OpenAI extraction |
| `TAVILY_API_KEY` | `.env`, `apps/api/.env` | Web search |
| `DATABASE_URL` | `.env`, `apps/api/.env` | Postgres connection |
| `WR_SHARED_PASSWORD` | `.env`, `apps/api/.env`, `apps/web/.env.local` | Shared app password |
| `WR_SESSION_SECRET` | `.env`, `apps/api/.env`, `apps/web/.env.local` | Cookie signing secret, 32+ chars |
| `WR_API_INTERNAL_TOKEN` | `.env`, `apps/api/.env`, `apps/web/.env.local` | Server-to-server API boundary token |

For Docker compose Postgres, use:

```text
DATABASE_URL=postgresql://white_rabbit:white_rabbit_dev@localhost:5432/white_rabbit
```

`OPENAI_BASE_URL` is optional. Leave it unset unless deliberately using a local OpenAI-compatible endpoint.

### 2. Start Postgres

```bash
docker compose up -d
```

### 3. Install API Dependencies And Migrate

```bash
cd apps/api
uv sync
uv run alembic upgrade head
```

### 4. Start API

```bash
cd apps/api
uv run uvicorn api.main:app --reload --port 8000
```

`GET /health` remains public. Lead/search/sandbox endpoints require `x-white-rabbit-internal-token`.

### 5. Start Web

```bash
cd apps/web
npm install
npm run dev
```

Open `http://localhost:3000` and log in with `WR_SHARED_PASSWORD`.

## Running Tests

See [`TESTING.md`](./TESTING.md) for the current command set.

Common checks:

```bash
cd apps/web && npm test -- --run
cd apps/api && $env:DATABASE_URL='postgresql://white_rabbit:white_rabbit_dev@localhost:5432/white_rabbit'; uv run pytest tests/test_api.py -q
cd packages/core && uv run pytest tests -q
```

On macOS/Linux, use `DATABASE_URL=... uv run pytest ...` instead of the PowerShell env assignment.

## Deployment

Deployment config exists for Vercel (web), Fly.io (API), and Neon/Postgres. The rebuild branch is not a launch signal. Production or preview deploys must still respect the red/yellow/green launch gate in `docs/00-product-northstar.md`.

## Project Layout

```text
white-rabbit/
├── apps/
│   ├── api/           FastAPI + SQLAlchemy + Alembic
│   └── web/           Next.js App Router + TypeScript
├── packages/
│   └── core/          Shared Python primitives
├── docs/              Current control docs plus historical records
├── audits/            Audit evidence and raw outputs
└── .gstack/           QA and gate reports
```

## License

Private. Not for distribution.
