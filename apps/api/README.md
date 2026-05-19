# White Rabbit API

**Status:** Active package reference.

This is the FastAPI backend for White Rabbit. It owns all OpenAI, Tavily, database, guardrail, and lead-search server behavior.

Read the root [`README.md`](../../README.md), [`STATUS.md`](../../STATUS.md), and [`docs/00-product-northstar.md`](../../docs/00-product-northstar.md) before working here.

## Boundary

`GET /health` is public. Lead/search/sandbox endpoints require the internal header:

```text
x-white-rabbit-internal-token: <WR_API_INTERNAL_TOKEN>
```

The Next.js app proxy is responsible for sending that header. Direct tokenless calls to protected endpoints should fail.

`GET /runs/{run_id}/leads` now returns `404 {"detail":"Run not found"}` when the run ID does not exist, instead of implying a successful empty readback.

## Local Commands

```bash
uv sync
uv run alembic upgrade head
uv run uvicorn api.main:app --reload --port 8000
```

DB-backed tests need a reachable Postgres URL. On this Ubuntu node I verified the suite against an isolated local container on port `55432`:

```bash
DATABASE_URL='postgresql://white_rabbit:white_rabbit_dev@127.0.0.1:55432/white_rabbit' \
WR_API_INTERNAL_TOKEN=test-internal-token \
uv run alembic -c alembic.ini upgrade head

DATABASE_URL='postgresql://white_rabbit:white_rabbit_dev@127.0.0.1:55432/white_rabbit' \
WR_API_INTERNAL_TOKEN=test-internal-token \
uv run pytest tests -q
```
