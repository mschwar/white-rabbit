# Testing - White Rabbit

Local verification reference (proportional verification per `ops/merge-policy.json`).

## Core (`packages/core`)

```bash
cd packages/core
uv run pytest tests -q
```

Live external API tests (`-m integration`) are opt-in only when keys are configured.

## API (`apps/api`)

```bash
cd apps/api
DATABASE_URL=postgresql://white_rabbit:white_rabbit_dev@localhost:5432/white_rabbit uv run pytest tests -q
```

## Web (`apps/web`)

```bash
cd apps/web
npm test -- --run
npm run build
```

## Python Lint

```bash
uvx ruff check apps/api packages/core
```
