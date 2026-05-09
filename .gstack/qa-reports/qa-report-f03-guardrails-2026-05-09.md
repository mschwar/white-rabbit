# QA Report — F03 Guardrail Rewrite for B2B Scope and Privacy Blocking

**Feature ID:** F03
**Feature name:** Guardrail rewrite for B2B scope and privacy blocking
**Branch:** feat/f03-b2b-guardrails
**PR target:** rebuild/validated-leads-loop
**Date:** 2026-05-09
**Agent:** Codex
**Required verification type:** Non-UI
**Buildout plan:** docs/08-agentic-buildout-plan.md
**Northstar:** docs/00-product-northstar.md

## Scope Checked

- Feature card reviewed in docs/08-agentic-buildout-plan.md (F03).
- Runtime verification focused on guardrail behavior in packages/core and API-level regressions in pps/api.
- Merge target remains ebuild/validated-leads-loop.

## Browser Test Steps

Not applicable (feature is non-UI). No browser-required QA for F03.

## Non-UI Verification Steps

**Command(s):**

`ash
cd packages/core && uv run pytest tests/test_query_guardrails.py -q
cd apps/api && uv run pytest tests/test_api.py -q -k "blocks_broad_advice_queries or blocks_privacy_sensitive_queries"
`

**Expected output:**

- Guardrail tests pass.
- Explicitly blocked privacy/off-topic examples remain blocked.
- Blocked queries do not invoke scout().

**Actual output summary:**

- cd packages/core && uv run pytest tests/test_query_guardrails.py -q => 9 passed in 0.08s
- cd apps/api && uv run pytest tests/test_api.py -q -k "blocks_broad_advice_queries or blocks_privacy_sensitive_queries" => 2 passed, 32 deselected in 1.01s

**Fixture/test file(s):**

- packages/core/tests/test_query_guardrails.py
- pps/api/tests/test_api.py

## Screenshots Required

Not applicable (non-UI verification only). No screenshots required.

## Tests Run

| Command | Result | Notes |
| --- | --- | --- |
| cd packages/core && uv run pytest tests/test_query_guardrails.py -q | Pass | 9 passed |
| cd apps/api && uv run pytest tests/test_api.py -q -k "blocks_broad_advice_queries or blocks_privacy_sensitive_queries" | Pass | 2 passed, 32 deselected |

## Northstar Reflection Result

| Question | Yes/No | Notes |
| --- | --- | --- |
| Does this directly improve natural-language query -> high-quality validated leads -> export? | Yes | It preserves the real-use query surface for B2B sales language while preventing unsafe/irrelevant prompts. |
| Does it reduce false confidence, bad contacts, wrong personas, or unsupported source claims? | Yes | It prevents non-B2B/privacy-unsafe prompts from entering search at all, reducing off-scope/unsafe outputs. |
| Does it avoid organizing or beautifying untrusted data? | Yes | No UI/data formatting changes; boundary enforcement only. |
| Does it keep main untouched and target only rebuild/validated-leads-loop? | Yes | QA and changes target this feature branch with rebuild merge only. |
| Is the feature independently mergeable? | Yes | Isolated changes in core guardrail + API regression tests. |
| Can the next agent discover state from docs without chat context? | Yes | Feature card and status/docs are updated with QA outcome and pointers. |
| Is there browser QA or explicit non-UI verification? | Yes | Explicit non-UI verification completed. |
| Is the scope small enough for GPT-5.3 Spark or GPT-5.4 Mini? | Yes | Single boundary rule rewrite + tests. |

## Findings

### Blocking

- None.

### Non-Blocking

- No functional regressions observed in the tested guardrail paths.

## Merge Decision

**Decision:** merge

**Reason:** Required guardrail test paths pass and feature behavior matches the F03 acceptance criteria in the buildout plan.

**Merged into:** rebuild/validated-leads-loop (pending merge completion in this QA run)

## Follow-Up Issues

- None.

## Handoff

`	ext
Feature: F03 Guardrail Rewrite for B2B Scope and Privacy Blocking
Branch: feat/f03-b2b-guardrails
Status: qa_passed (pending merge completion)
What changed: Guardrail logic allows normal B2B sales phrasing, blocks privacy-sensitive/off-topic prompts, and ensures blocked prompts do not call scout().
Tests or QA run: uv run pytest tests/test_query_guardrails.py -q; uv run pytest tests/test_api.py -q -k "blocks_broad_advice_queries or blocks_privacy_sensitive_queries"
Screenshots or report: .gstack/qa-reports/qa-report-f03-guardrails-2026-05-09.md
Northstar reflection: pass
Next pointer: F04 Query compiler / planner
Open questions: None
` 
