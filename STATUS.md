# STATUS

**Branch:** `main`

## Current State

- **Product posture:** Internal operator evaluation for Matt, Thomas, and Lee (shared-password web login + `WR_API_INTERNAL_TOKEN` backend boundary). Public SaaS, self-serve accounts, and billing remain out of scope.
- **Active runtime surfaces:**
  - `packages/core`: `scout()` lead discovery, B2B word-boundary query guardrails, 50-state + DC query planner, K-12 official-domain source map (`core/data/`), SSRF-hardened source validation, and evidence-backed scoring.
  - `apps/api`: FastAPI + PostgreSQL persistence (`/scout`, `/full`, `/batch`, `/recipes`, `/runs`, `/leads`, `/sandbox`, authenticated `/readiness`, lightweight public `/health`).
  - `apps/web`: Next.js 16 operator workspace with authenticated server-side proxy routes under `src/app/api/*`.
- **CI & merge policy:** Automatic cloud-VM push workflows are retired (`workflow_dispatch` only in `.github/workflows/deploy.yml`). Local verification + `GitGuardian Security Checks` govern PR merges per `ops/merge-policy.json`.
- **Historical artifacts:** Pre-product brainstorm/audio media (`archive/`, `Monroe St NE 8.m4a`) and historical audit/QA bundles (`audits/`, `.gstack/`) are archived offline under `/central/archive/`.
