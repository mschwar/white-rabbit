# QA Report - F06 Field-Level Validation Schema

**Feature ID:** F06  
**Feature name:** Field-level validation schema  
**Branch:** feat/f06-field-validation-schema  
**PR target:** rebuild/validated-leads-loop  
**Date:** 2026-05-10  
**Agent:** Codex  
**Required verification type:** non-UI verification  
**Buildout plan:** docs/08-agentic-buildout-plan.md  
**Northstar:** docs/00-product-northstar.md  

## Scope Checked

- Feature card read: `docs/08-agentic-buildout-plan.md` (F06).
- Files changed since last handoff: `packages/core/src/core/models.py`, `packages/core/tests/test_models.py`, `apps/api/tests/test_api.py`, `docs/08-agentic-buildout-plan.md`, `STATUS.md`.
- Confirmed `main` untouched: no changes outside `rebuild/validated-leads-loop` lineage and feature branch path.
- Confirmed PR/merge target is `rebuild/validated-leads-loop`: yes.

## Non-UI Verification Steps

### Command(s)

```bash
cd packages/core && uv run pytest tests/test_models.py -q
cd apps/api && uv run pytest tests/test_api.py -q -k full
cd apps/api && uv run pytest tests/test_api.py -q -k "scout or full"
```

### Expected output

- `test_models.py` passes.
- Scout/Full API serialization verification passes.

### Actual output summary

```text
packages/core/test_models.py: 30 passed in 0.59s
apps/api/test_api.py -k full: 2 passed, 33 deselected
apps/api/test_api.py -k "scout or full": 12 passed, 23 deselected
```

Non-blocking warnings observed in `apps/api/tests/test_api.py` and `apps/api/api/main.py` for deprecated `datetime.utcnow()` usage.

### Fixture/test file(s)

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
| `cd packages/core && uv run pytest tests/test_models.py -q` | Pass | `30 passed` |
| `cd apps/api && uv run pytest tests/test_api.py -q -k full` | Pass | `2 passed, 33 deselected` |
| `cd apps/api && uv run pytest tests/test_api.py -q -k "scout or full"` | Pass | `12 passed, 23 deselected`; deprecation warnings only |

## Northstar Reflection Result

| Question | Yes/No | Notes |
| --- | --- | --- |
| Does this directly improve natural-language query -> high-quality validated leads -> export? | Yes | It creates explicit per-field validation records, a prerequisite for trustworthy export and ranking changes. |
| Does it reduce false confidence, bad contacts, wrong personas, or unsupported source claims? | Yes | It replaces implicit trust with explicit `unsupported` default states for untouched validation fields. |
| Does it keep main untouched and target only rebuild/validated-leads-loop? | Yes | Merge target is `rebuild/validated-leads-loop`; no main changes. |
| Is the feature independently mergeable? | Yes | Scoped model/API serialization updates with gated tests and no UI coupling. |
| Can the next agent discover the state from docs without chat context? | Yes | `docs/08-agentic-buildout-plan.md` and `STATUS.md` now reflect merged status and next pointer. |
| Is there browser QA or explicit non-UI verification? | Yes | Required non-UI commands were executed and passed. |
| Is the scope small enough for the requested model sizes? | Yes | Schema-only changes plus verification; no adjacent refactors. |

## Findings

### Blocking

- None.

### Non-blocking

- Deprecation warnings from `datetime.utcnow()` in existing API paths (`datetime.datetime.utcnow()`); not introduced by this feature.

## Merge Decision

**Decision:** merge

**Reason:**

- Required non-UI checks passed.
- Feature improves the core northstar contract by preserving explicit validation state instead of implicit trust.
- Scope matches the feature card and W2 contract.

**Merged into:** `rebuild/validated-leads-loop`

## Handoff

```text
Feature: F06 Field-level validation schema
Branch: feat/f06-field-validation-schema
Status: merged_to_rebuild_branch
What changed: Added explicit field-level validation records for name, title, organization, email, phone, and source with explicit status/source/checked_at/notes fields; preserved API compatibility.
Tests or QA run:
- `cd packages/core && uv run pytest tests/test_models.py -q` (30 passed)
- `cd apps/api && uv run pytest tests/test_api.py -q -k full` (2 passed, 33 deselected)
- `cd apps/api && uv run pytest tests/test_api.py -q -k "scout or full"` (12 passed, 23 deselected)
Screenshots or report: `.gstack/qa-reports/qa-report-f06-field-validation-schema-2026-05-10.md`
Northstar reflection: Explicit field validation records reduce implicit trust and prevent pretending unsupported rows are usable until validators run.
Next pointer: F07 Source validator (blocked) after F06 merge.
Open questions: none blocking
```
