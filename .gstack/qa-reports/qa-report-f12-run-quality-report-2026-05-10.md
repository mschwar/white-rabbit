# QA Report - F12 Per-Run Quality Report

**Feature ID:** F12  
**Feature name:** Per-run quality report  
**Branch:** feat/f12-run-quality-report  
**PR target:** rebuild/validated-leads-loop  
**Date:** 2026-05-10  
**Agent:** Codex  
**Required verification type:** non-UI verification  
**Buildout plan:** docs/08-agentic-buildout-plan.md  
**Northstar:** docs/00-product-northstar.md  

## Scope Checked

- Feature card read: yes (`## F12 - Per-Run Quality Report`)  
- Files changed: `packages/core/src/core/quality_report.py`, `packages/core/tests/test_quality_report.py`  
- Explicit anti-goals reviewed: no scoreboard UI, no analytics/dashboarding, no self-grading model calls  
- Confirmed `main` untouched: yes  
- Confirmed PR/merge target is `rebuild/validated-leads-loop`: yes  

## Non-UI Verification Steps

**Command(s):**

```bash
cd packages/core && uv run pytest tests/test_quality_report.py -q
```

**Expected output:**

```text
2 passed
```

**Actual output summary:**

```text
2 passed in 0.08s
```

**Fixture/test file(s):**

- `packages/core/tests/test_quality_report.py`  

## Screenshots Required

List required screenshots from the feature card and save them under `.gstack/qa-reports/screenshots/`.

| Required screenshot | Saved path | Pass/fail |
| --- | --- | --- |
| n/a (non-UI feature) | n/a | n/a |

## Tests Run

| Command | Result | Notes |
| --- | --- | --- |
| `cd packages/core && uv run pytest tests/test_quality_report.py -q` | Passed | `2 passed` |

## Northstar Reflection Result

Answer each before merge.

| Question | Yes/No | Notes |
| --- | --- | --- |
| Does this directly improve natural-language query -> high-quality validated leads -> export? | Yes | It provides per-run quality telemetry on precision, persona match, contact quality, source support, and fake/unsupported signal coverage. |
| Does it reduce false confidence, bad contacts, wrong personas, or unsupported source claims? | Yes | It makes those failure modes explicit instead of implicit. |
| Does it avoid organizing or beautifying untrusted data? | Yes | This change is read-only quality telemetry and does not add UI/operator-facing surfaces. |
| Does it keep main untouched and target only rebuild/validated-leads-loop? | Yes | No `main` changes; current flow is for rebuild QA branch. |
| Is the feature independently mergeable? | Yes | It adds a self-contained module + tests. |
| Can the next agent discover state from docs without chat context? | Yes | Status docs updated with QA result and handoff pointer. |
| Is there browser QA or explicit non-UI verification? | Yes | Explicit non-UI test command run and passed. |
| Is the scope small enough for GPT-5.3 Spark or GPT-5.4 Mini? | Yes | Self-contained quality module and tests. |

## Findings

### Blocking

- None.

### Non-Blocking

- No non-blocking findings.

## Merge Decision

**Decision:** merge

**Reason:**

- Required command passes with expected assertions for all listed quality metrics and serialization shape.

**Merged into:** rebuild/validated-leads-loop

## Follow-Up Issues

- None.

## Handoff

```text
Feature: F12 Per-Run Quality Report
Branch: feat/f12-run-quality-report
Status: qa_passed
What changed: Added quality report serialization and metrics builder plus targeted unit tests for candidate-category counts, persona/contact/source metrics, and fake/unsupported email signals.
Tests or QA run: `cd packages/core && uv run pytest tests/test_quality_report.py -q` (2 passed)
Screenshots or report: `.gstack/qa-reports/qa-report-f12-run-quality-report-2026-05-10.md`
Northstar reflection: Supports objective quality feedback before UI surfaces expose validated leads.
Next pointer: F13 Single Search-Bar UI
Open questions: none.
```
