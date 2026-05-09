# White Rabbit v2

Internal-first B2B prospecting workbench. Three operators (Matt, Thomas, Lee). Self-serve from day 1. Recipes, not lists.

> **AI agents:** read [`AGENTS.md`](./AGENTS.md) first. Then [`STATUS.md`](./STATUS.md). Do not skip.

> **Humans:** read [`docs/00-context.md`](./docs/00-context.md) for the why and [`docs/04-roadmap.md`](./docs/04-roadmap.md) for the plan.

## What this is

White Rabbit v2 takes a natural-language prospecting query ("Healthcare IT directors in Phoenix"), runs it through web search and LLM extraction, and returns ranked leads with three visible scores (**Fit**, **Evidence**, **Contact**) and an explanation for each rank. The unit of work is a **recipe** — a saved query + filters + source mix + ranking weights + outcome stats, reusable across batches.

## What this is not

- **Not the Scotty demo.** The demo lives at `/Users/mschwar/Documents/proxy-lead`. Frozen.
- **Not a SaaS yet.** No accounts, no billing. One shared password. Three operators.
- **Not a ZoomInfo competitor on volume.** It wins on ranking, provenance, and recipe reusability — or it doesn't ship.

## Stack

Next.js (App Router, TypeScript) + FastAPI (Python) + Postgres. Frontend never holds API keys.

See [`docs/02-stack.md`](./docs/02-stack.md) for layout and conventions.

## Getting started

### Prerequisites

- macOS or Linux (Windows via WSL2 should work but is not actively tested)
- Node.js 22+ and `npm`
- Python 3.13+ and `uv` (https://docs.astral.sh/uv/)
- Docker Desktop or `docker` CLI (for Postgres)
- Git
- API keys: [OpenAI](https://platform.openai.com/api-keys) and [Tavily](https://app.tavily.com/home)

### 1. Clone and configure

```bash
git clone https://github.com/mschwar/homelab.git white-rabbit   # or your fork
cd white-rabbit
```

Copy the example env files and fill in your real API keys:

```bash
cp .env.example .env
cp apps/api/.env.example apps/api/.env
cp apps/web/.env.example apps/web/.env.local
```

Edit the three files and set at least these values:

| Variable | File | What |
|----------|------|------|
| `OPENAI_API_KEY` | `.env`, `apps/api/.env` | OpenAI API key |
| `TAVILY_API_KEY` | `.env`, `apps/api/.env` | Tavily search API key |
| `WR_SHARED_PASSWORD` | `.env`, `apps/api/.env`, `apps/web/.env.local` | One password all operators share |
| `WR_SESSION_SECRET` | `.env`, `apps/api/.env`, `apps/web/.env.local` | Min 32 random chars for cookie signing |
| `WR_API_INTERNAL_TOKEN` | `.env`, `apps/api/.env`, `apps/web/.env.local` | Shared server-to-server token forwarded by the Next.js proxy |
| `DATABASE_URL` | `.env`, `apps/api/.env` | Postgres URL (see step 2) |

> **Important:** Do not commit `.env` or `.env.local` files to git. They are already in `.gitignore`.

> **Optional:** `OPENAI_BASE_URL` is only needed if you use a local OpenAI-compatible endpoint (e.g. Ollama at `http://localhost:11434/v1`). Leave it empty or commented out to use the real OpenAI API.

### 2. Start Postgres

```bash
docker compose up -d
```

This starts PostgreSQL 16 on port `5432` with user `white_rabbit` / password `white_rabbit_dev` / database `white_rabbit`.

If you use your own Postgres, set `DATABASE_URL` accordingly, e.g.:
```bash
export DATABASE_URL="postgresql://white_rabbit:white_rabbit_dev@localhost:5432/white_rabbit"
```

### 3. Install API dependencies and run migrations

```bash
cd apps/api
uv sync
uv run alembic upgrade head
```

This creates all tables (`recipe`, `recipe_run`, `lead`, `lead_feedback`, `sandbox_state`, etc.).

### 4. Start the API

```bash
uv run uvicorn api.main:app --reload --port 8000
```

You should see startup logs including:
```
OpenAI: gpt-4o-mini @ https://api.openai.com/v1
Postgres: postgresql://...
```

If you see a `RuntimeError` about missing env vars or an unreachable model, check your `.env` file and API key validity.

### 5. Install web dependencies and start the dev server

In a **new terminal**:

```bash
cd apps/web
npm install
npm run dev
```

The web app will be available at `http://localhost:3000`.

### 6. Open the app and run a Scout query

1. Open `http://localhost:3000` in your browser.
2. Log in with the `WR_SHARED_PASSWORD` you configured.
3. Click **Scout** in the nav.
4. Enter a query like `Healthcare IT directors in Phoenix` and click **Run Scout**.
5. After ~15 seconds you should see lead cards with Fit / Evidence / Contact scores.

## Common issues

| Symptom | Likely cause | Fix |
|---------|-------------|-----|
| `RuntimeError: Missing required env: OPENAI_API_KEY` | `.env` file not copied or key not filled in | Copy `.env.example` → `.env` and set the key |
| `OpenAI model unreachable: gpt-4o-mini @ http://localhost:11434/v1` | `OPENAI_BASE_URL` points to Ollama but Ollama is not running or does not have the model | Comment out `OPENAI_BASE_URL` in `.env` to use the real OpenAI API |
| `connection refused` on port `5432` | Postgres is not running | Run `docker compose up -d` |
| `alembic upgrade head` fails with `relation does not exist` | You skipped the migration step | Run `uv run alembic upgrade head` in `apps/api` |
| Web app shows "API Error" with no leads | The API is not running on `:8000` or `WR_API_BASE_URL` in `apps/web/.env.local` is wrong | Start the API (`uvicorn api.main:app --port 8000`) and check the env var |
| Login page loops back to itself | `WR_SESSION_SECRET` differs between `apps/api/.env` and `apps/web/.env.local` | Set the same 32+ char secret in both files and restart both servers |

## Deployment

White Rabbit is configured for **Vercel** (frontend) + **Fly.io** (API) + **Neon** (Postgres). All three offer generous free tiers.

### Platform setup

1. **Neon Postgres**
   - Create a project at https://neon.tech
   - Copy the connection string (looks like `postgresql://user:pass@ep-...us-east-1.aws.neon.tech/dbname`)
   - Set it as `DATABASE_URL` in both Fly.io and local `.env` files

2. **Fly.io (API)**
   - Install `flyctl`: https://fly.io/docs/hands-on/install-flyctl/
   - `cd apps/api && flyctl launch` (use the existing `fly.toml`)
   - Set secrets:
     ```bash
     flyctl secrets set OPENAI_API_KEY=sk-... TAVILY_API_KEY=tvly-... \
       WR_SHARED_PASSWORD=... WR_SESSION_SECRET=... WR_API_INTERNAL_TOKEN=... DATABASE_URL=postgresql://... \
       --app white-rabbit-api
     ```

3. **Vercel (Web)**
   - Import the repo at https://vercel.com/new
   - Set environment variables in the Vercel dashboard:
     - `WR_API_BASE_URL=https://white-rabbit-api.fly.dev`
     - `WR_SHARED_PASSWORD` (same as API)
     - `WR_SESSION_SECRET` (same as API, min 32 chars)
     - `WR_API_INTERNAL_TOKEN` (same as API)
   - Vercel will auto-detect the Next.js app in `apps/web`

### CI/CD

Pushes to `main` trigger the GitHub Actions workflow at `.github/workflows/deploy.yml`:
1. Runs API, core, and web tests
2. Deploys API to Fly.io
3. Deploys web to Vercel

Required repository secrets:
- `FLY_API_TOKEN` — from `flyctl tokens create deploy`
- `VERCEL_TOKEN`, `VERCEL_ORG_ID`, `VERCEL_PROJECT_ID` — from Vercel dashboard

### Manual deploy (without CI)

```bash
# API
cd apps/api
flyctl deploy --remote-only

# Web
# Vercel deploys automatically on git push if linked, or:
vercel --prod
```

---

## Testing

### Python (API + Core)

```bash
cd apps/api
uv run pytest tests -q
```

```bash
cd packages/core
uv run pytest tests -q
```

Integration tests (requires real API keys, costs ~$0.05 per run):
```bash
cd packages/core
uv run pytest tests -m integration -q
```

### Web (Next.js)

```bash
cd apps/web
npm test
npm run build
```

## Project layout

```
white-rabbit/
├── apps/
│   ├── api/           FastAPI + SQLAlchemy + Alembic
│   └── web/           Next.js App Router + TypeScript
├── packages/
│   └── core/          Shared Python: models, orchestrator, search, cost, guardrails
├── docs/              Architecture decisions, roadmap, context
├── audits/            Audit reports and action plans
└── .gstack/           QA reports and screenshots
```

## License

Private. Not for distribution.
