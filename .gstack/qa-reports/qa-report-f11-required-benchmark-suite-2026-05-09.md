# QA Report - Agentic Buildout Feature

**Feature ID:** F11
**Feature name:** Required Benchmark Suite
**Branch:** feat/f11-required-benchmark-suite
**PR target:** rebuild/validated-leads-loop
**Date:** 2026-05-09
**Agent:** Codex
**Required verification type:** non-UI verification
**Buildout plan:** docs/08-agentic-buildout-plan.md
**Northstar:** docs/00-product-northstar.md

## Scope Checked

- Feature card read: `docs/08-agentic-buildout-plan.md` section for F11.
- Files changed: `packages/core/src/core/benchmark_suite.py`, `packages/core/tests/fixtures/benchmark_suite.json`, `packages/core/tests/test_benchmark_suite.py`.
- Explicit anti-goals reviewed:
  - no UI or live-api substitution for data-quality checks
  - keep product scope in red state
  - no live API dependency in default tests
- Confirmed `main` untouched: yes
- Confirmed PR/merge target is `rebuild/validated-leads-loop`: yes

## Non-UI Verification Steps

**Command(s):**

```bash
cd packages/core && uv run pytest tests/test_benchmark_suite.py -q
```

**Expected output:**

```text
3 passed
```

**Actual output summary:**

```text
... [100%]
3 passed in 0.08s
```

**Fixture/test file(s):**

- `packages/core/tests/fixtures/benchmark_suite.json`
- `packages/core/tests/test_benchmark_suite.py`

## Tests Run

| Command | Result | Notes |
| --- | --- | --- |
| `cd packages/core && uv run pytest tests/test_benchmark_suite.py -q` | passed | 3 passed |

## Northstar Reflection Result

Answer each before merge.

| Question | Yes/No | Notes |
| --- | --- | --- |
| Does this directly improve natural-language query -> high-quality validated leads -> export? | Yes | It makes QA coverage deterministic for these stages and prevents silent regression on key quality thresholds. |
| Does it reduce false confidence, bad contacts, wrong personas, or unsupported source claims? | Yes | Adds offline validation contracts for persona/contact/source pass dimensions and privacy refusal behavior. |
| Does it avoid organizing or beautifying untrusted data? | Yes | No UI changes; verification-only feature. |
| Does it keep main untouched and target only rebuild/validated-leads-loop? | Yes | Branch and merge target are rebuild-only. |
| Is the feature independently mergeable? | Yes | Self-contained benchmark fixture and tests. |
| Can the next agent discover state from docs without chat context? | Yes | Status updates captured in `docs/08-agentic-buildout-plan.md` and `STATUS.md`. |
| Is there browser QA or explicit non-UI verification? | Yes | Explicit non-UI verification executed and passing. |
| Is the scope small enough for GPT-5.3 Spark or GPT-5.4 Mini? | Yes | Small, isolated test/model fixture change set. |

## Findings

### Blocking

- None.

### Non-Blocking

- None.

## Merge Decision

**Decision:** merge

**Reason:**

- Required benchmark suite passes offline contract and pass/fail dimension checks using canonical fixture payloads with no live dependencies.

**Merged into:** pending

## Handoff

```text
Feature: F11 - Required Benchmark Suite
Branch: feat/f11-required-benchmark-suite
Status: qa_passed
What changed: Added a canonical required benchmark suite fixture and contract tests for simple B2B and guardrail/privacy scenarios in `packages/core/tests/fixtures/benchmark_suite.json` and `packages/core/tests/test_benchmark_suite.py`.
Tests or QA run:
 - `cd packages/core && uv run pytest tests/test_benchmark_suite.py -q` (3 passed)
Screenshots or report: `.gstack/qa-reports/qa-report-f11-required-benchmark-suite-2026-05-09.md`
Northstar reflection: Suite enforces required audit-query breadth and pass/fail dimensions without external services and directly supports the quality rebuild before UI work.
Next pointer: F12 per-run quality report (`feat/f12-run-quality-report`).
Open questions: none
```
