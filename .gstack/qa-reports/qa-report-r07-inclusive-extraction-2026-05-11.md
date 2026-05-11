# QA Report - R07 Inclusive Extraction Prompt And Candidate Parse Salvage

**Feature:** R07 - Inclusive extraction prompt and candidate parse salvage
**Branch:** `feat/reset-r07-inclusive-extraction`
**Integration target:** `rebuild/validated-leads-loop`
**Decision:** pass
**UI-visible:** no

## State Provenance

- Read `AGENTS.md`, `STATUS.md`, `docs/03-decisions.md`, `docs/00-product-northstar.md`, `docs/12-reset-gated-implementation-plan-2026-05-10.md`, and `docs/13-pipeline-orchestrator-contract-2026.md`.
- `STATUS.md` and `docs/12-reset-gated-implementation-plan-2026-05-10.md` identified exactly one Prompt B target: `R07 - Inclusive extraction prompt and candidate parse salvage`.
- Pushed branch state identified `origin/feat/reset-r07-inclusive-extraction` at `2de0301`, matching the local feature branch.
- `rebuild/validated-leads-loop` and `origin/rebuild/validated-leads-loop` were at `1de2602`.
- `git status --short --branch` before QA: `## feat/reset-r07-inclusive-extraction...origin/feat/reset-r07-inclusive-extraction`.

## Required Verification

```bash
git diff --check
```

Result: passed.

```bash
cd packages/core && uv run pytest tests/test_source_validation.py tests/test_contact_status.py tests/test_scoring.py tests/test_orchestrator.py -q
```

Result: `43 passed in 0.70s`.

```bash
cd apps/api && WR_API_INTERNAL_TOKEN=test-internal-token uv run pytest tests -q
```

Result: `43 passed, 50 warnings in 0.75s`. Warnings were existing `datetime.utcnow()` deprecations in API and test code.

## Non-UI Verification

No browser QA or screenshots were required because R07 changes only core extraction parsing, strict model coercion, and non-UI tests.

Code review verified:

- The OpenAI structured output response format now asks for `ExtractedLeadList`, a deliberately looser Pydantic model with optional candidate fields and strict `extra="forbid"` shape, then the server coerces rows into existing strict White Rabbit candidate models.
- A malformed `person_lead` row no longer crashes the whole query. If strict `Lead` validation fails, the candidate is retried with invalid contact stripped; if it still fails, it becomes a `FailedCandidate`.
- Missing emails normalize to `email_status="missing"` and cannot pass the evidence gate.
- Invalid or generic emails are stripped to blank contact with `email_status="failed"`, `contact_score=0.0`, and `gate_passed=False`.
- The existing server-side source validation and evidence gate remain the final authority for `gate_passed`.

## Northstar Drift Check

R07 supports the northstar by making plausible but incomplete candidates visible without letting unsupported data look CRM-ready. It preserves the rule that a person row needs a real person, strips unsupported contacts, keeps the binary evidence gate strict, and downgrades unsafe extraction output into explicit failed rows.

R07 does not add external self-serve features, accounts, billing, public landing pages, frontend API-key use, recipe/batch surfaces, operator-minute ceremony, UI changes, export behavior, tier distribution UI, or persistence behavior. The product remains red; RG3 still needs R08, R09, and Prompt C audit before any gate advancement.

## Scope Check

Diff review against `rebuild/validated-leads-loop` showed reset implementation changes only in:

- `packages/core/src/core/orchestrator.py`
- `packages/core/tests/test_orchestrator.py`
- reset handoff docs in `STATUS.md` and `docs/12-reset-gated-implementation-plan-2026-05-10.md`

No `apps/web`, API route, export, database migration, benchmark harness, query planner, source collection, non-person coverage writer, tiering engine, field-validator rewrite, conflict resolver, score-language reset, `tier`, or `primary_filter_reason` implementation was present. R08 and R09 remain downstream RG3 work.

## Result

R07 passes Prompt B QA. Merge only into `rebuild/validated-leads-loop`, mark R08 ready inside RG3, and do not unlock RG4.
