# QA Report - R08 Tiering Engine, Field Validator, And Conflict Resolver

**Feature:** R08 - Tiering engine, field validator, and conflict resolver
**Branch:** `feat/reset-r08-tier-validation-conflicts`
**Integration target:** `rebuild/validated-leads-loop`
**Decision:** pass
**UI-visible:** no

## State Provenance

- Read `AGENTS.md`, `STATUS.md`, `docs/03-decisions.md`, `docs/00-product-northstar.md`, `docs/12-reset-gated-implementation-plan-2026-05-10.md`, and `docs/13-pipeline-orchestrator-contract-2026.md`.
- `STATUS.md` and `docs/12-reset-gated-implementation-plan-2026-05-10.md` identified exactly one Prompt B target: `R08 - Tiering engine, field validator, and conflict resolver`.
- Pushed branch state identified `origin/feat/reset-r08-tier-validation-conflicts` at `48e8459`, matching the local feature branch.
- `rebuild/validated-leads-loop` and `origin/rebuild/validated-leads-loop` were at `fec952f`.
- `git status --short --branch` before QA: `## feat/reset-r08-tier-validation-conflicts...origin/feat/reset-r08-tier-validation-conflicts`.

## Required Verification

```bash
git diff --check
```

Result: passed.

```bash
cd packages/core && uv run pytest tests/test_source_validation.py tests/test_contact_status.py tests/test_scoring.py tests/test_orchestrator.py -q
```

Result: `46 passed in 0.37s`.

```bash
cd apps/api && WR_API_INTERNAL_TOKEN=test-internal-token uv run pytest tests -q
```

Result: `43 passed, 50 warnings in 0.85s`. Warnings were existing `datetime.utcnow()` deprecations in API and test code.

## Non-UI Verification

No browser QA or screenshots were required because R08 changes only core tiering, validation semantics, metrics, and non-UI tests.

Code review verified:

- Candidate models now carry server-computed `tier` and `primary_filter_reason`.
- Person rows become `high_trust_usable` only when the existing binary evidence gate passes with supported person, organization, source, and usable contact evidence.
- Person rows with missing, unsupported, or failed contact evidence are kept visible as `review`, not CRM-ready, and contact fields are synchronized from validation results.
- Inaccessible sources and failed core field validation downgrade unsafe person rows into explicit `FailedCandidate` rows.
- Person/account conflicts are detected and downgraded to `failed` rows.
- Non-person rows keep explicit `organization_only`, `not_found`, and `failed` tiers.
- Run metrics expose `tier_distribution` across all output tiers.

## Northstar Drift Check

R08 supports the northstar by making false confidence harder to display. It preserves the binary evidence gate as the only `high_trust_usable` path while keeping review, organization-only, not-found, and failed rows visible with grounded reasons.

R08 does not add external self-serve features, accounts, billing, public landing pages, frontend API-key use, recipe/batch surfaces, operator-minute ceremony, UI changes, export behavior, persistence behavior, or gate advancement. The product remains red; RG3 still needs R09 and Prompt C audit before any gate advancement.

## Scope Check

Diff review against `rebuild/validated-leads-loop` showed implementation changes only in:

- `packages/core/src/core/cost.py`
- `packages/core/src/core/models.py`
- `packages/core/src/core/orchestrator.py`
- `packages/core/tests/test_orchestrator.py`
- `packages/core/tests/test_scoring.py`
- reset handoff docs in `STATUS.md` and `docs/12-reset-gated-implementation-plan-2026-05-10.md`

No `apps/web`, API route, export, database migration, benchmark harness, query planner, source collection, non-person coverage writer, score-language reset UI, final mockup, or gate-audit work was present. R09 remains the next same-gate feature.

## Result

R08 passes Prompt B QA. Merge only into `rebuild/validated-leads-loop`, mark R09 ready inside RG3, and do not unlock RG4 or sync `main`.
