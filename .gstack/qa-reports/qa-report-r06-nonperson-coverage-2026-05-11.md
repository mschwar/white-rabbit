# QA Report - R06 Not-Found And Organization-Only Coverage Writer

**Feature:** R06 - Not-found and organization-only coverage writer
**Branch:** `feat/reset-r06-nonperson-coverage`
**Integration target:** `rebuild/validated-leads-loop`
**Decision:** pass
**UI-visible:** no

## State Provenance

- Read `AGENTS.md`, `STATUS.md`, `docs/03-decisions.md`, `docs/00-product-northstar.md`, `docs/12-reset-gated-implementation-plan-2026-05-10.md`, and `docs/13-pipeline-orchestrator-contract-2026.md`.
- `STATUS.md` and `docs/12-reset-gated-implementation-plan-2026-05-10.md` identified exactly one Prompt B target: `R06 - Not-found and organization-only coverage writer`.
- Pushed branch state identified `origin/feat/reset-r06-nonperson-coverage` at `3db8436`, matching the local feature branch.
- `rebuild/validated-leads-loop` and `origin/rebuild/validated-leads-loop` were at `8ef6624`.
- `git status --short --branch` before QA: `## feat/reset-r06-nonperson-coverage...origin/feat/reset-r06-nonperson-coverage`.

## Required Verification

```bash
git diff --check
```

Result: passed.

```bash
cd packages/core && uv run pytest tests/test_query_planner.py tests/test_search.py tests/test_benchmark_suite.py -q
```

Result: `18 passed in 0.38s`.

Additional focused non-UI regression check:

```bash
cd packages/core && uv run pytest tests/test_coverage.py tests/test_orchestrator.py -q
```

Result: `16 passed in 0.72s`.

## Non-UI Verification

No browser QA or screenshots were required because R06 changes only core coverage writing and orchestrator wiring.

Code review verified:

- `write_nonperson_coverage()` only runs when a `QueryPlan` has named-account obligations.
- Existing person, organization-only, not-found, or failed rows that mention an account alias count as coverage and are not duplicated.
- If a collected source mentions an uncovered named account, the writer appends an `OrganizationOnlyCandidate` with the account name and source URL.
- If no collected source supports the uncovered named account, the writer appends a `NotFoundCandidate` with `searched_target` and organization set to the account.
- The writer does not create person names, titles, emails, phone numbers, fit/evidence/contact scores, tier labels, or CRM-ready gate state.
- `scout()` applies the same source-validation pass to appended non-person rows, preserving existing validation behavior.

## Northstar Drift Check

R06 supports the northstar by making missing or personless named-account obligations visible instead of silently dropping them or inventing people. It preserves the rule that a person row needs a real person, keeps `organization_only` and `not_found` distinct from CRM-ready leads, and does not loosen the strict `high_trust_usable` definition.

R06 does not add external self-serve features, accounts, billing, public landing pages, frontend API-key use, recipe/batch surfaces, operator-minute ceremony, UI changes, or export behavior. The product remains red; RG2 still requires Prompt C live evidence under the `$5` cap before any gate advancement.

## Scope Check

Diff review against `rebuild/validated-leads-loop` showed reset implementation changes only in:

- `packages/core/src/core/coverage.py`
- `packages/core/src/core/orchestrator.py`
- `packages/core/src/core/query_planner.py`
- `packages/core/tests/test_coverage.py`
- `packages/core/tests/test_orchestrator.py`
- reset handoff docs in `STATUS.md` and `docs/12-reset-gated-implementation-plan-2026-05-10.md`

No `apps/web`, `apps/api`, export, database migration, inclusive extraction, tiering engine, conflict resolver, score-language reset, `primary_filter_reason`, or downstream RG3 implementation was present. RG3 remains blocked.

## Result

R06 passes Prompt B QA. Merge only into `rebuild/validated-leads-loop`, mark RG2 ready for Prompt C audit, and do not unlock RG3.
