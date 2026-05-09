# White Rabbit Core

**Status:** Active package reference.

This package contains shared Python primitives for guardrails, search, models, scoring/extraction support, and rebuild validation work.

Read the root [`README.md`](../../README.md), [`STATUS.md`](../../STATUS.md), [`docs/00-product-northstar.md`](../../docs/00-product-northstar.md), and [`docs/08-agentic-buildout-plan.md`](../../docs/08-agentic-buildout-plan.md) before working here.

## Commands

```bash
uv sync
uv run pytest tests -q
```

Live integration tests may call external APIs and incur cost:

```bash
uv run pytest tests -m integration -q
```

Run live tests only when a feature card, QA rubric, or gate report requires them.
