# Gate Review - W1 Red-State Containment

**Branch:** `feat/docs-hard-audit-remediation`
**Integration branch:** `rebuild/validated-leads-loop`
**Date:** 2026-05-09
**Decision:** advance
**Current product gate:** red

## Features Included

| Feature | Status | Evidence |
| --- | --- | --- |
| F01 - Hide premature operator surfaces | merged_to_rebuild_branch | `.gstack/qa-reports/qa-report-f01-hide-premature-surfaces-2026-05-09.md` |
| F02 - Backend API boundary | merged_to_rebuild_branch | `.gstack/qa-reports/qa-report-f02-backend-api-boundary-2026-05-09.md` |
| F03 - Guardrail rewrite | merged_to_rebuild_branch | `.gstack/qa-reports/qa-report-f03-guardrails-2026-05-09.md` |

## Required Verification

| Check | Result | Evidence |
| --- | --- | --- |
| Web containment tests | pass | `cd apps/web && npm test -- --run` -> 13 files, 25 tests passed |
| API boundary/guardrail/sandbox/search tests | pass after explicit local DB URL | First run failed on two real-DB sandbox tests because local `.env`/process DB credentials did not match the running Docker Postgres. Rerun with `DATABASE_URL=postgresql://white_rabbit:white_rabbit_dev@localhost:5432/white_rabbit` passed: 22 passed, 12 deselected. |
| Core guardrail tests | pass | `cd packages/core && uv run pytest tests/test_query_guardrails.py -q` -> 9 passed |

## Northstar Assessment

- Query: W1 does not improve query planning yet; F04 remains the next feature for that.
- Validated leads: Still red. W1 contains trust leaks before validation work.
- Field-level evidence: Not implemented yet; W2/W3 own the contract and validators.
- Ranking: Not addressed by W1.
- Export: Not addressed by W1.
- False-confidence risk: Reduced by hiding premature recipe/batch/admin surfaces, protecting backend endpoints, and blocking privacy/off-topic prompts before search.

## Decision Rationale

Advance to W2 because the product is still red but contained:

- Primary operator UI no longer promotes premature recipe/batch/reset implementation surfaces via F01.
- Direct tokenless backend calls to protected lead/sandbox endpoints are covered by F02 verification.
- Consumer/privacy-sensitive and off-topic prompts are blocked before search by F03.
- Fresh W1 verification commands pass when the documented local database URL is used.

The initial API verification failure is recorded as local environment drift, not a product gate failure: the running Docker Postgres accepted `white_rabbit_dev`, but the pytest process picked up a different DB credential until `DATABASE_URL` was set explicitly.

## Next Pointer

Keep `F04 - Query compiler / planner` ready on branch `feat/f04-query-compiler`.

## Follow-Ups

- The docs remediation branch should make local setup docs explicit about using the Docker compose `DATABASE_URL` when running DB-backed API tests.
- W2 must not start UI work. It should build the typed bounded search contract: query compiler, candidate categories, and field validation schema.
