# 02 - Stack

**Status:** Active reference.
**Authority:** For product truth, defer to `docs/00-product-northstar.md`. For current rebuild execution, defer to `docs/08-agentic-buildout-plan.md` and `docs/09-rebuild-phase-gates.md`.

## Runtime Choices

- **Web:** Next.js 16.2.4 App Router, React 19.2.4, TypeScript 5.9, Tailwind 4.
- **API:** Python 3.12+, FastAPI 0.136+, Pydantic 2.13+, SQLAlchemy 2.0+, Alembic 1.18+.
- **Core:** Python package under `packages/core`.
- **Storage:** Postgres. Local development uses Docker compose; deployed environments use managed Postgres.
- **Package management:** `npm` for web, `uv` for Python.
- **Auth/boundary:** shared app password plus internal web-to-API token. See ADR-003 and ADR-005.

## Current Repo Layout

```text
white-rabbit/
├── AGENTS.md
├── README.md
├── STATUS.md
├── docs/
│   ├── 00-product-northstar.md      # current product truth
│   ├── 03-decisions.md              # locked ADRs
│   ├── 08-agentic-buildout-plan.md  # active rebuild queue
│   ├── 09-rebuild-phase-gates.md    # active gate process
│   └── historical/reference docs
├── apps/
│   ├── web/                         # Next.js app
│   │   └── src/
│   │       ├── app/                 # pages and route handlers
│   │       ├── components/
│   │       └── lib/
│   └── api/                         # FastAPI app
│       ├── api/
│       ├── alembic/
│       └── tests/
└── packages/
    └── core/                        # shared Python primitives
        ├── src/core/
        └── tests/
```

## Branch Workflow

Current rebuild work runs on `rebuild/validated-leads-loop`.

- Feature branches branch from `rebuild/validated-leads-loop`.
- Feature PRs target `rebuild/validated-leads-loop`.
- Do not merge rebuild feature work to `main`.
- Use `docs/08-agentic-buildout-plan.md` for feature status and branch names.
- Use `docs/09-rebuild-phase-gates.md` for wave transitions.

Legacy `main`-targeted BUILDOUT docs are historical records, not the current work queue.

## Web/API Boundary

The browser talks to same-origin Next.js route handlers. Those route handlers call FastAPI with the internal token.

FastAPI:

```text
GET /health                         public
POST /scout                         protected
POST /full                          protected
GET/POST /sandbox, /sandbox/reset   protected
GET/POST /batch                     protected
recipe/run/feedback endpoints       protected or internal depending on route
```

Protected API requests require:

```text
x-white-rabbit-internal-token: <WR_API_INTERNAL_TOKEN>
```

Frontend code never holds OpenAI or Tavily keys. All vendor calls happen in the Python service.

## Environment Variables

### Root / API

```text
OPENAI_API_KEY=...
TAVILY_API_KEY=...
DATABASE_URL=postgresql://white_rabbit:white_rabbit_dev@localhost:5432/white_rabbit
WR_SHARED_PASSWORD=...
WR_SESSION_SECRET=...
WR_API_INTERNAL_TOKEN=...
WR_ENV=development
```

`OPENAI_BASE_URL` is optional and should be unset unless using a local OpenAI-compatible endpoint.

### Web

```text
WR_API_BASE_URL=http://localhost:8000
WR_SHARED_PASSWORD=...
WR_SESSION_SECRET=...
WR_API_INTERNAL_TOKEN=...
```

`WR_API_INTERNAL_TOKEN` must match the API value.

## Local Development

```bash
docker compose up -d
```

```bash
cd apps/api
uv sync
uv run alembic upgrade head
uv run uvicorn api.main:app --reload --port 8000
```

```bash
cd apps/web
npm install
npm run dev
```

Open `http://localhost:3000`.

## Testing

See `TESTING.md` for command details.

Common checks:

```bash
cd apps/web && npm test -- --run
cd apps/api && $env:DATABASE_URL='postgresql://white_rabbit:white_rabbit_dev@localhost:5432/white_rabbit'; uv run pytest tests -q
cd packages/core && uv run pytest tests -q
```

On macOS/Linux, use shell environment syntax instead of PowerShell.

## Deployment

Deployment config exists for:

- **Web:** Vercel.
- **API:** Fly.io.
- **DB:** managed Postgres, typically Neon for deploys.

Deployment readiness is not the same as product readiness. The red/yellow/green launch gate in `docs/00-product-northstar.md` controls who may use the product.

## Conventions

- App Router only; no `pages/`.
- Server Components by default; use client components only for interaction.
- Tailwind for styling.
- Python inputs/outputs use Pydantic models.
- Database schema changes go through Alembic.
- Tests mirror source boundaries.
- Conventional commit prefixes: `feat:`, `fix:`, `docs:`, `chore:`, `refactor:`, `test:`, `qa:`.
