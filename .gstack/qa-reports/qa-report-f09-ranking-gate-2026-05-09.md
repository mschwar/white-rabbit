# QA Report - F09 Ranking Gate Based On Evidence

**Feature ID:** F09
**Feature name:** Ranking Gate Based On Evidence
**Branch:** feat/f09-ranking-gate
**PR target:** rebuild/validated-leads-loop
**Date:** 2026-05-09
**Agent:** Codex
**Required verification type:** non-UI verification
**Buildout plan:** docs/08-agentic-buildout-plan.md
**Northstar:** docs/00-product-northstar.md
**Rubric:** docs/qa-rubric.md (Tiers 1–4 apply because orchestrator/validation logic changed)

## Scope Checked

- Feature card read: yes
- Files changed:
  - `packages/core/src/core/orchestrator.py`
  - `packages/core/src/core/models.py`
  - `packages/core/tests/test_orchestrator.py`
  - `packages/core/tests/test_orchestrator_integration.py`
- Explicit anti-goals reviewed:
  - No UI redesign or additional surfaces were introduced.
  - No opaque composite-rank UI changes were introduced.
  - Core scope only.
- Confirmed `main` untouched: yes
- Confirmed PR/merge target is `rebuild/validated-leads-loop`: yes

## Non-UI Verification Steps

### Command(s)

```bash
$env:OPENAI_API_KEY=''
cd packages/core && uv run pytest tests/test_source_validation.py tests/test_contact_status.py tests/test_orchestrator.py tests/test_orchestrator_integration.py -q

$env:OPENAI_API_KEY=''
cd packages/core && uv run pytest -q
```

### Expected output

- 32 passed, 5 skipped (target verification command)
- 76 passed, 5 skipped (full packages/core suite)

### Actual output summary

```text
32 passed, 5 skipped

76 passed, 5 skipped
```

### Fixture/test file(s)

- `packages/core/tests/test_source_validation.py`
- `packages/core/tests/test_contact_status.py`
- `packages/core/tests/test_orchestrator.py`
- `packages/core/tests/test_orchestrator_integration.py`

### Screenshots Required

Not applicable (non-UI feature).

## Tests Run

| Command | Result | Notes |
| --- | --- | --- |
| `$env:OPENAI_API_KEY=''; cd packages/core && uv run pytest tests/test_source_validation.py tests/test_contact_status.py tests/test_orchestrator.py tests/test_orchestrator_integration.py -q` | pass | 32 passed, 5 skipped |
| `$env:OPENAI_API_KEY=''; cd packages/core && uv run pytest -q` | pass | 76 passed, 5 skipped |

## Northstar Reflection Result

| Question | Yes/No | Notes |
| --- | --- | --- |
| Does this directly improve natural-language query -> high-quality validated leads -> export? | Yes | It makes gate passability depend on evidence records, not only raw scores. |
| Does it reduce false confidence, bad contacts, wrong personas, or unsupported source claims? | Yes | Unsupported/unsupported-source candidate rows are correctly blocked from gate-pass. |
| Does it avoid organizing or beautifying untrusted data? | Yes | No UI change; core scoring behavior only. |
| Does it keep main untouched and target only `rebuild/validated-leads-loop`? | Yes | Merge target remained `rebuild/validated-leads-loop`. |
| Is the feature independently mergeable? | Yes | Scoped to core scoring + tests and docs. |
| Can the next agent discover the state from docs without this chat? | Yes | STATUS and docs feature card updated with handoff. |
| Is there browser QA or explicit non-UI verification? | Yes | Explicit non-UI verification completed with core suites. |
| Is the scope small enough for GPT-5.3 Spark / GPT-5.4 Mini? | Yes | Core scoring patch plus tests within existing module boundaries. |

## Findings

### Blocking

- None.

### Non-Blocking

- Initial run of the feature card command failed when `OPENAI_API_KEY` was inherited as an invalid key from env; reran with explicit `OPENAI_API_KEY=''` to make the test expectation deterministic.

## Merge Decision

**Decision:** merge

**Reason:**

- Evidence-backed gate computation now blocks unsupported rows and still allows verified/ deduced-with-pattern evidence to pass when scores clear threshold.
- Required non-UI verification passed and no regressions were observed in the core suite.

**Merged into:** rebuild/validated-leads-loop / not merged yet in report

## Handoff

```text
Feature: F09 Ranking gate based on evidence
Branch: feat/f09-ranking-gate
Status: merged_to_rebuild_branch
What changed: evidence-backed gate now requires supported name/title/organization/source and valid contact status in addition to score thresholds.
Tests or QA run:
  - `$env:OPENAI_API_KEY=''; cd packages/core && uv run pytest tests/test_source_validation.py tests/test_contact_status.py tests/test_orchestrator.py tests/test_orchestrator_integration.py -q` (32 passed, 5 skipped)
  - `$env:OPENAI_API_KEY=''; cd packages/core && uv run pytest -q` (76 passed, 5 skipped)
Screenshots or report: .gstack/qa-reports/qa-report-f09-ranking-gate-2026-05-09.md
Northstar reflection: reduces false confidence by requiring evidence support and usable contact statuses.
Next pointer: keep F10 blocked at wave level until orchestrator acceptance decision is recorded.
Open questions: whether W3 orchestrator acceptance should be marked accepted now or held pending additional benchmark evidence.
```
