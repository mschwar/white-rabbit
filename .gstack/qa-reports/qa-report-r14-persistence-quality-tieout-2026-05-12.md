# QA Report - R14 Persistence, DB readback, and quality report tie-out

Date: 2026-05-12
Prompt: B
Feature: R14 - Persistence, DB readback, and quality report tie-out
Branch under QA: `feat/reset-r14-persistence-quality-tieout`
Integration target: `main`
Decision: PASS - merge to `main`

## Summary

R14 passes Prompt B QA. The branch is limited to API/DB persistence, DB readback, and typed web readback proxy support. It does not include R14A image work, R14B UI/UX consistency work, R14C deployment smoke work, RG6 dogfood work, source/compiler changes, benchmark changes, or deployment promotion.

## State proof

- Fetched origin and pulled latest `main` before QA.
- `origin/main`: `e626052 docs(reset): refresh r14 prompt b branch tip [skip ci]`.
- `origin/feat/reset-r14-persistence-quality-tieout`: `b07aab7 Merge remote-tracking branch 'origin/main' into feat/reset-r14-persistence-quality-tieout`.
- Assignment lock: `docs/reset-current-assignment.json` allowed only Prompt B QA for R14 on `feat/reset-r14-persistence-quality-tieout`.
- Current worktree note: untracked local file `WhiteRabbit_brand_design_pack.zip` existed before QA and was not touched.

## Required verification

| Check | Result | Evidence |
| --- | --- | --- |
| `git diff --check origin/main...HEAD` | PASS | Exit 0, no output. |
| `cd apps/api && WR_API_INTERNAL_TOKEN=test-internal-token uv run pytest -q` | PASS | `53 passed, 82 warnings in 1.22s`; warnings are existing datetime deprecations. |
| `cd apps/web && npm test` | PASS | `13 passed (13)`, `30 passed (30)`. |
| `cd apps/web && npm run build` | PASS | Build completed successfully; existing warnings about workspace-root inference and deprecated `middleware` naming. |
| Targeted persistence/readback smoke | PASS | `test_scout_endpoint_returns_scoped_payload`, `test_run_leads_endpoint_returns_persisted_rows_and_readback`, and `test_full_endpoint_returns_persisted_lead_ids` all passed. |

## Persistence/readback findings

Confirmed by tests and diff inspection:

- `/scout` now persists recipe/run/lead rows and returns `run_id`, `recipe_id`, persisted lead IDs, and `persistence_readback`.
- `/full` now shares the same persistence/readback helper and returns `persistence_readback`.
- `persistence_readback` includes response, persisted, DB readback, and exportable row counts plus `row_count_matches`.
- Protected `GET /runs/{run_id}/leads` returns stored lead rows, row count, tier distribution, and candidate-category distribution.
- Web proxy `apps/web/src/app/api/runs/[run_id]/leads/route.ts` forwards persisted-run readback requests through the internal API boundary.
- Web types in `apps/web/src/lib/scout.ts` model `PersistenceReadback` and persisted run lead readback responses.

## Scope check

Diff versus `origin/main` touched only:

- `apps/api/api/main.py`
- `apps/api/tests/test_api.py`
- `apps/web/src/app/api/runs/[run_id]/leads/route.ts`
- `apps/web/src/lib/scout.ts`

No product UI component, visual asset, image, deployment, benchmark, source-assisted compiler, dogfood, or gate-audit files changed.

A scoped grep for adjacent work found no R14A/R14B/R14C/RG6 implementation terms beyond pre-existing `source_assisted_proof` test context. The actual changed files are API persistence/readback, API tests, web proxy, and web types only.

## Northstar drift check

R14 aligns with `docs/00-product-northstar.md`:

- It improves the core loop by making run/lead persistence and DB readback auditable.
- It preserves export validation context by reporting row-count tie-out instead of flattening data.
- It does not relax READY/high-trust semantics, invent contacts, change scoring, or hide uncertain rows.
- It does not add public SaaS/account/billing scope or expose frontend API keys.
- Product remains red; R14 is feature QA evidence, not a gate advance.

## Browser/visual QA

Not applicable for R14. The selected feature card is `API + DB`, and this branch does not touch user-facing UI components. R14A/R14B/R14C browser, screenshot, and deployment-smoke checks remain blocked until those features are individually ready.

## Queue consequence

Because QA passed:

- Mark R14 `merged_to_mainline` after merge.
- Mark R14A `ready` after merge.
- Keep R14B, R14C, R15/RG6, dogfood, and RG5 Prompt C blocked.
- Do not unlock the next gate.
