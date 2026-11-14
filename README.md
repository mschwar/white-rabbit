# White Rabbit

Internal-first B2B lead research tool for Matt, Thomas, and Lee.

> **Current state:** Internal operator evaluation (`main`). Not a public SaaS — no self-serve signup, orgs, or billing.

## Core Loop

```text
natural-language B2B target
  -> query guardrails & source planning
  -> candidate discovery & source validation
  -> field-level evidence & quality scoring
  -> ranked leads + CSV export
```

White Rabbit prioritizes verified people, persona fit, source-backed organization/contact evidence, and explicit missing/blocker states over raw unverified lead volume.

## Authority Docs

1. [`AGENTS.md`](./AGENTS.md) — operating rules and verification policy.
2. [`docs/03-decisions.md`](./docs/03-decisions.md) — architectural decision records (ADRs).
3. [`docs/00-product-northstar.md`](./docs/00-product-northstar.md) — product scope and quality bar.
4. [`STATUS.md`](./STATUS.md) — concise current repository status.
5. [`TESTING.md`](./TESTING.md) — local verification commands.

## Stack

- **Web (`apps/web`):** Next.js 16 App Router, React 19, TypeScript, Tailwind 4 (deployed on Vercel).
- **API (`apps/api`):** FastAPI, Python 3.12+, SQLAlchemy 2.0, Alembic (deployed on Fly.io).
- **Core (`packages/core`):** Shared Python search, query planning/guardrails, source validation, contact evidence, and scoring primitives.
- **Database:** PostgreSQL.
- **Auth boundary:** Shared operator password + signed session cookie on Web; `x-white-rabbit-internal-token` (`WR_API_INTERNAL_TOKEN`) on all server-to-server Web -> API proxy calls. Frontend code never holds OpenAI or Tavily keys.

## Local Setup

### 1. Environment

```bash
cp .env.example .env
cp apps/api/.env.example apps/api/.env
cp apps/web/.env.example apps/web/.env.local
```

Required variables:

| Variable | Files | Purpose |
| --- | --- | --- |
| `OPENAI_API_KEY` | `.env`, `apps/api/.env` | OpenAI extraction |
| `TAVILY_API_KEY` | `.env`, `apps/api/.env` | Web search |
| `DATABASE_URL` | `.env`, `apps/api/.env` | PostgreSQL connection |
| `WR_SHARED_PASSWORD` | `.env`, `apps/api/.env`, `apps/web/.env.local` | Shared operator password |
| `WR_SESSION_SECRET` | `.env`, `apps/api/.env`, `apps/web/.env.local` | Cookie signing secret (32+ chars) |
| `WR_API_INTERNAL_TOKEN` | `.env`, `apps/api/.env`, `apps/web/.env.local` | Internal Web -> API token |

### 2. Start Postgres & Migrate

```bash
docker compose up -d
cd apps/api
uv sync --dev
uv run alembic upgrade head
uv run uvicorn api.main:app --reload --port 8000
```

`GET /health` is public for container healthchecks. `GET /readiness` and all lead/search/batch/recipe/sandbox endpoints require `x-white-rabbit-internal-token`.

### 3. Start Web

```bash
cd apps/web
npm install
npm run dev
```

## Verification & Merge Policy

Hosted cloud-VM PR runners are retired (`workflow_dispatch` only in [`.github/workflows/deploy.yml`](./.github/workflows/deploy.yml)); merge policy lives in [`ops/merge-policy.json`](./ops/merge-policy.json) (`GitGuardian Security Checks` required, local verification before merge).

```bash
cd packages/core && uv run pytest tests -q
cd apps/api && DATABASE_URL=postgresql://white_rabbit:white_rabbit_dev@localhost:5432/white_rabbit uv run pytest tests -q
cd apps/web && npm test -- --run && npm run build
```

## Project Layout

```text
white-rabbit/
├── apps/
│   ├── api/           FastAPI + SQLAlchemy + Alembic service
│   └── web/           Next.js App Router frontend & authenticated API proxy routes
├── packages/
│   └── core/          Shared Python search, guardrails, validation, and scoring
├── docs/              Product, architecture, and historical design docs
└── ops/               Fleet merge policy (`ops/merge-policy.json`)
```

## License

Private. Not for distribution.
