# QA Report - F05 Candidate Model Separation

**Feature ID:** F05
**Feature name:** Candidate model separation
**Branch:** feat/f05-candidate-types
**PR target:** rebuild/validated-leads-loop
**Date:** 2026-05-10
**Agent:** Codex
**Required verification type:** non-UI verification
**Buildout plan:** docs/08-agentic-buildout-plan.md
**Northstar:** docs/00-product-northstar.md

## Scope Checked

- Feature card read: F05 card in `docs/08-agentic-buildout-plan.md`
- Files changed: `packages/core/src/core/models.py`, `apps/api/api/main.py` compatibility responses, `apps/api/tests/test_api.py` (already on branch prior to this QA prompt)
- Explicit anti-goals reviewed: final results table, source validation, existing persistence removal
- Confirmed `main` untouched: yes
- Confirmed PR/merge target is `rebuild/validated-leads-loop`: yes

## Non-UI Verification Steps

**Command(s):**

```bash
cd packages/core && uv run pytest tests/test_models.py -q
cd apps/api && uv run pytest tests/test_api.py -q -k scout
```

**Expected output:**

```text
model and API tests pass; candidate-category fixtures validate/reject as expected.
```

**Actual output summary:**

```text
25 passed in packages/core/test_models.py.
10 passed, 25 deselected in apps/api/test_api.py with 6 non-blocking warnings.
```

**Fixture/test file(s):**

- `packages/core/tests/test_models.py`
- `apps/api/tests/test_api.py`

## Screenshots Required

No browser screenshot required; non-UI verification only.

| Required screenshot | Saved path | Pass/fail |
| --- | --- | --- |
| N/A (non-UI feature) | N/A | N/A |

## Tests Run

| Command | Result | Notes |
| --- | --- | --- |
| `cd packages/core && uv run pytest tests/test_models.py -q` | Pass | `25 passed` |
| `cd apps/api && uv run pytest tests/test_api.py -q -k scout` | Pass | `10 passed, 25 deselected`; 6 warnings about deprecated `datetime.utcnow()` |

## Northstar Reflection Result

Answer each before merge.

| Question | Yes/No | Notes |
| --- | --- | --- |
| Does this directly improve natural-language query -> high-quality validated leads -> export? | Yes | It removes false-confidence person rows and creates explicit candidate state categories needed for later filtering/export quality. |
| Does it reduce false confidence, bad contacts, wrong personas, or unsupported source claims? | Yes | Company/role-only names are rejected from person_lead and represented as non-person categories. |
| Does it avoid organizing or beautifying untrusted data? | Yes | No UI changes; schema/serialization hardening only. |
| Does it keep main untouched and target only rebuild/validated-leads-loop? | Yes | Per merge plan, only rebuild branch target. |
| Is the feature independently mergeable? | Yes | API and model changes are scoped and compatible with current contracts. |
| Can the next agent discover state from docs without chat context? | Yes | `docs/08-agentic-buildout-plan.md` and `STATUS.md` updated with handoff. |
| Is there browser QA or explicit non-UI verification? | Yes | Explicit non-UI test command set executed. |
| Is the scope small enough for GPT-5.3 Spark or GPT-5.4 Mini? | Yes | Scope limited to candidate contract/schema changes. |

## Findings

### Blocking

- None.

### Non-Blocking

- Non-blocking pytest warning in `apps/api/tests/test_api.py` for `datetime.utcnow()` deprecation.

## Merge Decision

**Decision:** merge

**Reason:**

- F05 passes required command-level verification and aligns with the rebuild northstar by preventing company-like rows from being presented as person leads.

**Merged into:** `rebuild/validated-leads-loop`

## Follow-Up Issues

- None.

## Handoff

```text
Feature: F05 Candidate model separation
Branch: feat/f05-candidate-types
Status: merged_to_rebuild_branch
What changed: Added candidate_category-first contract for person/organization/not_found/failed cases and strict person-lead name validation for company-like and role-only strings.
Tests or QA run:
- `cd packages/core && uv run pytest tests/test_models.py -q` (25 passed)
- `cd apps/api && uv run pytest tests/test_api.py -q -k scout` (10 passed, 25 deselected)
Screenshots or report: `.gstack/qa-reports/qa-report-f05-candidate-model-separation-2026-05-10.md`
Northstar reflection: Candidate separation protects against false-confidence rows in the lead list and preserves downstream ranking/export semantics.
Next pointer: F06 Field-level validation schema (blocked).
Open questions: None blocking F05.
```
