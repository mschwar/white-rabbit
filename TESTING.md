# Testing - White Rabbit

**Status:** Active testing reference.

Use this file for command syntax. Use [`docs/qa-rubric.md`](./docs/qa-rubric.md) and [`docs/09-rebuild-phase-gates.md`](./docs/09-rebuild-phase-gates.md) for ship-gate requirements.

## Current Baseline

White Rabbit is in the red-gate validated-leads rebuild. Passing tests means a change is mechanically safe; it does not mean the product is ready for Thomas/Lee dogfood.

For rebuild features:

- UI-visible changes require browser QA and screenshots.
- Non-UI changes require explicit command verification.
- Wave transitions require a gate report under `.gstack/qa-reports/`.

## Web

```bash
cd apps/web
npm test -- --run
npm run build
```

End-to-end/browser checks use Playwright or the Codex Browser skill when the feature card requires it:

```bash
cd apps/web
npm run test:e2e
```

## API

Most API tests use FastAPI `TestClient` with mocks. Some sandbox/migration tests touch the local Postgres database.

PowerShell:

```powershell
cd apps/api
$env:DATABASE_URL='postgresql://white_rabbit:white_rabbit_dev@localhost:5432/white_rabbit'
uv run pytest tests -q
```

macOS/Linux:

```bash
cd apps/api
DATABASE_URL=postgresql://white_rabbit:white_rabbit_dev@localhost:5432/white_rabbit uv run pytest tests -q
```

If DB-backed tests fail with password/authentication errors, confirm Docker Postgres is running:

```bash
docker compose up -d
docker ps
```

## Core

```bash
cd packages/core
uv run pytest tests -q
```

Integration tests hit live external APIs and may incur cost:

```bash
cd packages/core
uv run pytest tests -m integration -q
```

Run live integration only when the feature card or QA rubric requires it and API keys are configured.

## W1 Gate Verification

For red-state containment, the current required commands are:

```bash
cd apps/web && npm test -- --run
cd apps/api && $env:DATABASE_URL='postgresql://white_rabbit:white_rabbit_dev@localhost:5432/white_rabbit'; uv run pytest tests/test_api.py -q -k "guardrail or sandbox or scout or full or batch"
cd packages/core && uv run pytest tests/test_query_guardrails.py -q
```

On macOS/Linux, use shell env syntax for the API command.

## Reporting

QA and gate reports live in `.gstack/qa-reports/`.

Every report should include:

- Branch and date.
- Required tiers or gate.
- Commands run and result.
- Browser screenshots if UI-visible.
- Any skipped check with a concrete reason.

Do not treat old QA reports as current product proof unless the active gate docs explicitly reference them.
