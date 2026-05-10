# Orchestrator Review - W1 Gate And F04 Merge

**Branch:** `rebuild/validated-leads-loop`
**Date:** 2026-05-10
**Reviewer:** Codex orchestrator
**Current product gate:** red

## Decision

**W1 gate:** accepted after review.
**F04 merge:** accepted as valid W2 in-wave work.
**Next pointer:** F05 Candidate model separation remains ready.
**W2 gate:** not yet due; W2 requires F04-F06 plus the W2 gate report before W3 can unlock.

## Work Reviewed

| Item | Status | Evidence |
| --- | --- | --- |
| F01 Hide premature operator surfaces | merged_to_rebuild_branch | `.gstack/qa-reports/qa-report-f01-hide-premature-surfaces-2026-05-09.md` |
| F02 Backend API boundary | merged_to_rebuild_branch | `.gstack/qa-reports/qa-report-f02-backend-api-boundary-2026-05-09.md`; ADR-005 |
| F03 B2B/privacy guardrails | merged_to_rebuild_branch | `.gstack/qa-reports/qa-report-f03-guardrails-2026-05-09.md` |
| W1 red-state containment gate | advance accepted | `.gstack/qa-reports/gate-w1-red-state-containment.md` |
| F04 Query compiler / planner | merged_to_rebuild_branch | `.gstack/qa-reports/qa-report-f04-query-compiler-2026-05-10.md` |

## Verification Run

| Check | Result | Evidence |
| --- | --- | --- |
| Core F04/F03/orchestrator tests | pass | `uv run pytest tests/test_query_planner.py tests/test_search.py tests/test_query_guardrails.py tests/test_orchestrator.py -q` in `packages/core` -> 22 passed |
| Web containment tests | pass | `npm test -- --run` in `apps/web` -> 13 files, 25 tests passed |
| API W1 subset | pass | `uv run pytest tests/test_api.py -q -k "guardrail or sandbox or scout or full or batch"` in `apps/api` with local `DATABASE_URL` -> 22 passed, 12 deselected |
| Whitespace check | pass | `git diff --check` -> no whitespace errors; Windows CRLF warnings only |

## Northstar Assessment

- Query: F04 reduces the Arizona query-length failure by compiling bounded named-account searches.
- Validated leads: still red; F05-F09 are required before rows can represent candidate category, field validation, contact status, and evidence-backed ranking.
- Field-level evidence: not implemented yet.
- Ranking: still score/gate based on existing fields; evidence-backed ranking is F09.
- Export: still lacks the northstar validation-by-field columns.
- False-confidence risk: W1 reduces trust leaks; F04 removes one search-crash path, but it does not make outputs CRM-ready.

## Findings And Resolutions

1. `docs/08-agentic-buildout-plan.md` had stale status drift: the header said F04 was merged and F05 was ready, while the feature table still listed F04 as `implemented_pending_qa` and the F05 feature card still said `blocked`.
   - Resolved by updating the table and F05 card to match the actual rebuild state.

2. The phase-gate process allowed agents to self-advance wave gates. `docs/09-rebuild-phase-gates.md` said a gate branch should update next-wave statuses and push the decision, while only reserving final yellow/green product readiness for Matt.
   - Resolved by adding ADR-007 and updating the gate process so downstream waves require an orchestrator acceptance record in the gate report and `STATUS.md`.

3. F04 introduced multi-query Tavily planning, but run metrics still counted one Tavily search.
   - Resolved by preserving `tavily_searches` metadata on search results and using it in orchestrator metrics.

## Root Cause Of Gate Bypass

The agents did not have an explicit "stop and consult the orchestrator" rule. The written gate mechanics required evidence, but then instructed the gate branch to update unlock statuses and push the result. In other words, the docs created a report requirement, not an approval checkpoint.

ADR-007 changes the authority model: feature agents can recommend a gate decision, but cannot unlock a downstream wave without orchestrator acceptance.
