# Gate Review - W2 Search Contract

**Branch:** `rebuild/validated-leads-loop`
**Integration branch:** `rebuild/validated-leads-loop`
**Date:** 2026-05-10
**Prepared recommendation:** advance
**Orchestrator decision:** advance
**Orchestrator acceptance:** Codex orchestrator / 2026-05-10
**Current product gate:** red

## Features Included

| Feature | Status | Commit/PR | QA report |
| --- | --- | --- | --- |
| F04 Query compiler / planner | merged_to_rebuild_branch | `feat/f04-query-compiler` | `.gstack/qa-reports/qa-report-f04-query-compiler-2026-05-10.md` |
| F05 Candidate model separation | merged_to_rebuild_branch | `feat/f05-candidate-types` | `.gstack/qa-reports/qa-report-f05-candidate-model-separation-2026-05-10.md` |
| F06 Field-level validation schema | merged_to_rebuild_branch | `feat/f06-field-validation-schema` | `.gstack/qa-reports/qa-report-f06-field-validation-schema-2026-05-10.md` |

## Required Verification

| Check | Result | Evidence |
| --- | --- | --- |
| Core query planner and model contract | pass | `$env:OPENAI_API_KEY=''; cd packages/core && uv run pytest tests/test_query_planner.py tests/test_models.py -q` -> 32 passed |
| API Scout/Full serialization | pass | `cd apps/api && uv run pytest tests/test_api.py -q -k "scout or full"` with local Docker `DATABASE_URL` -> 12 passed, 23 deselected |

## Northstar Assessment

- Query: Bounded query planning exists and preserves the Arizona named-account prompt under Tavily limits.
- Validated leads: Candidate categories now distinguish `person_lead`, `organization_only`, `not_found`, and `failed`.
- Field-level evidence: Validation records exist for name, title, organization, email, phone, and source.
- Ranking: Not part of W2; W3 owns ranking.
- Export: Not part of W2.
- False-confidence risk: Reduced because company-as-person and role-as-person cases can be represented without pretending they are usable leads.

## Decision Rationale

Advance accepted retroactively because W2 feature evidence is present and the W2 required verification passed. The sequencing was not ideal: W3 feature work had already merged before this formal gate acceptance existed. ADR-007 remains the rule going forward.

## Next Pointer

W3 validation and ranking gate review.

## Follow-Ups

- Keep the product red until benchmark and export gates prove usable lead quality.
