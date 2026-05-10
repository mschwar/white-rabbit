# QA Report - F07 Source Validator

**Feature ID:** F07  
**Feature name:** Source validator  
**Branch:** feat/f07-source-validator  
**PR target:** rebuild/validated-leads-loop  
**Date:** 2026-05-10  
**Agent:** Codex  
**Required verification type:** non-UI verification  
**Buildout plan:** docs/08-agentic-buildout-plan.md  
**Northstar:** docs/00-product-northstar.md  

## Scope Checked

- Feature card read: `docs/08-agentic-buildout-plan.md` (F07).
- Files changed since last handoff: `packages/core/src/core/orchestrator.py`, `packages/core/src/core/source_validation.py`, `packages/core/tests/test_orchestrator.py`, `packages/core/tests/test_source_validation.py`, `docs/08-agentic-buildout-plan.md`, `STATUS.md`.
- Confirmed `main` untouched: no changes outside rebuild-line feature files and docs.
- Confirmed PR/merge target is `rebuild/validated-leads-loop`: yes.

## Non-UI Verification Steps

### Command(s)

```bash
cd packages/core && $env:OPENAI_API_KEY='' ; uv run pytest tests/test_source_validation.py -q
cd packages/core && $env:OPENAI_API_KEY='' ; uv run pytest tests/test_source_validation.py tests/test_orchestrator.py -q
```

### Expected output

- Source validator fixture cases pass.
- Source validation integration through orchestrator also passes when OpenAI key is intentionally cleared for the negative-key test path.

### Actual output summary

```text
tests/test_source_validation.py: 6 passed
tests/test_source_validation.py tests/test_orchestrator.py: 16 passed
```

### Fixture/test file(s)

- `packages/core/tests/test_source_validation.py`
- `packages/core/tests/test_orchestrator.py`

## Screenshots Required

No browser QA required; non-UI verification only.

| Required screenshot | Saved path | Pass/fail |
| --- | --- | --- |
| N/A | N/A | N/A |

## Tests Run

| Command | Result | Notes |
| --- | --- | --- |
| `cd packages/core && $env:OPENAI_API_KEY='' ; uv run pytest tests/test_source_validation.py -q` | Pass | `6 passed` |
| `cd packages/core && $env:OPENAI_API_KEY='' ; uv run pytest tests/test_orchestrator.py -q` | Pass | `16 passed` across source validator + orchestrator regression |

## Northstar Reflection Result

| Question | Yes/No | Notes |
| --- | --- | --- |
| Does this directly improve natural-language query -> high-quality validated leads -> export? | Yes | It adds source-evidence support/failure metadata required for trustworthy lead ranking and future validation-aware export. |
| Does it reduce false confidence, bad contacts, wrong personas, or unsupported source claims? | Yes | Source URL presence alone is no longer treated as evidence; unsupported/inaccessible sources now downgrade field validation. |
| Does it keep main untouched and target only rebuild/validated-leads-loop? | Yes | Scope is core package + handoff docs; no main-targeted merge action. |
| Is the feature independently mergeable? | Yes | One feature branch, focused files, and verification complete. |
| Can the next agent discover the state from docs without chat context? | Yes | `docs/08-agentic-buildout-plan.md` and `STATUS.md` now reflect merged status and next pointer. |
| Is there browser QA or explicit non-UI verification? | Yes | Required non-UI verification command(s) executed and passed. |
| Is the scope small enough for the requested model sizes? | Yes | Source validation logic and model updates only; no UI. |

## Findings

### Blocking

- None.

### Non-Blocking

- Running `tests/test_orchestrator.py` directly in a session with a preconfigured invalid `OPENAI_API_KEY` triggers the wrong external-call path in the `test_scout_raises_on_missing_openai_key` fixture. Clearing `OPENAI_API_KEY` as shown in the command above keeps the negative-key branch deterministic.

## Merge Decision

**Decision:** merge

**Reason:**

- Required verification passed.
- The feature is within scope and aligns to W3 false-confidence prevention goals.
- No browser QA needed (non-UI feature).

**Merged into:** `rebuild/validated-leads-loop`

## Handoff

```text
Feature: F07 Source validator
Branch: feat/f07-source-validator
Status: merged_to_rebuild_branch
What changed: Added source URL resolution and field-level support/unsupported/failed validation for name, title, organization, email, phone, and source metadata.
Tests or QA run:
- `cd packages/core && $env:OPENAI_API_KEY='' ; uv run pytest tests/test_source_validation.py -q` (6 passed)
- `cd packages/core && $env:OPENAI_API_KEY='' ; uv run pytest tests/test_source_validation.py tests/test_orchestrator.py -q` (16 passed)
Screenshots or report: `.gstack/qa-reports/qa-report-f07-source-validator-2026-05-10.md`
Northstar reflection: Source links are now checked against direct content; inaccessible/unsupported sources are downgraded and no longer treated as evidence.
Next pointer: F08 Contact status model.
Open questions: none blocking
```
