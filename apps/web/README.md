# White Rabbit Web App

**Status:** Active package reference.

This is the Next.js App Router frontend for White Rabbit. It is not a standalone product; read the root [`README.md`](../../README.md), [`STATUS.md`](../../STATUS.md), and [`docs/00-product-northstar.md`](../../docs/00-product-northstar.md) before working here.

## Current Role

- Shared-password app shell.
- Same-origin API proxy routes.
- Primary lead-search UI for rebuild verification.
- Sends `WR_API_INTERNAL_TOKEN` to the FastAPI backend from server-side route handlers.

Recipe, batch, Friday review, scoreboard, and sandbox reset surfaces are internal/deferred while the product is red.

## Commands

```bash
npm install
npm run dev
npm test -- --run
npm run build
```

Browser QA is required for UI-visible rebuild features.
