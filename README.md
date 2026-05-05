# White Rabbit v2

Internal-first B2B prospecting workbench. Three operators (Matt, Thomas, Lee). Self-serve from day 1. Recipes, not lists.

> **AI agents:** read [`AGENTS.md`](./AGENTS.md) first. Then [`STATUS.md`](./STATUS.md). Do not skip.

> **Humans:** read [`docs/00-context.md`](./docs/00-context.md) for the why and [`docs/04-roadmap.md`](./docs/04-roadmap.md) for the plan.

## What this is

White Rabbit v2 takes a natural-language prospecting query ("K-12 IT directors in Albuquerque"), runs it through web search and LLM extraction, and returns ranked leads with three visible scores (**Fit**, **Evidence**, **Contact**) and an explanation for each rank. The unit of work is a **recipe** — a saved query + filters + source mix + ranking weights + outcome stats, reusable across batches.

## What this is not

- **Not the Scotty demo.** The demo lives at `/Users/mschwar/Documents/proxy-lead`. Frozen.
- **Not a SaaS yet.** No accounts, no billing. One shared password. Three operators.
- **Not a ZoomInfo competitor on volume.** It wins on ranking, provenance, and recipe reusability — or it doesn't ship.

## Stack

Next.js (App Router, TypeScript) + FastAPI (Python) + Postgres. Frontend never holds API keys.

See [`docs/02-stack.md`](./docs/02-stack.md) for layout and conventions.

## Getting started

Repo is documented but not yet scaffolded. See [`STATUS.md`](./STATUS.md) for the next concrete task (Sprint 1: scaffold).

## License

Private. Not for distribution.
