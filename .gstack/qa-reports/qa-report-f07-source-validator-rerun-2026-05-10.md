# QA Report - F07 Source Validator (Re-run)

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
- No UI changes in scope.
- Confirmed `main` untouched: no `main` branch target.
- Confirmed PR/merge target is `rebuild/validated-leads-loop`: yes.

## Non-UI Verification Steps

### Command(s)

```bash
cd packages/core && uv run pytest tests/test_source_validation.py -q
```

```bash
$env:OPENAI_API_KEY='' ; cd packages/core ; uv run pytest tests/test_source_validation.py tests/test_orchestrator.py -q
```

### Expected output

- `test_source_validation.py` passes.
- Source-validation and orchestrator regression pass when `OPENAI_API_KEY` is intentionally cleared to keep the negative-key branch deterministic.

### Actual output summary

- `tests/test_source_validation.py`: `6 passed`  
- `tests/test_source_validation.py tests/test_orchestrator.py`: `16 passed` with `OPENAI_API_KEY=''`
- Initial run of `tests/test_source_validation.py tests/test_orchestrator.py` in ambient shell failed because a non-empty `OPENAI_API_KEY` in environment was hitting external auth; rerun with explicit empty key removed the coupling.

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
| `cd packages/core && uv run pytest tests/test_source_validation.py -q` | Pass | `6 passed` |
| `$env:OPENAI_API_KEY='' ; cd packages/core ; uv run pytest tests/test_source_validation.py tests/test_orchestrator.py -q` | Pass | `16 passed` |

## Northstar Reflection Result

| Question | Yes/No | Notes |
| --- | --- | --- |
| Does this directly improve natural-language query -> high-quality validated leads -> export? | Yes | It adds source-evidence support/failed metadata needed for false-confidence control. |
| Does it reduce false confidence, bad contacts, wrong personas, or unsupported source claims? | Yes | URL support is checked before fields are considered validated. |
| Does it keep main untouched and target only rebuild/validated-leads-loop? | Yes | Reproducible non-UI core/test change path only. |
| Is the feature independently mergeable? | Yes | Focused backend validator and tests. |
| Can the next agent discover the state from docs without chat context? | Yes | Handoff in `STATUS.md` and feature card remain current. |
| Is there browser QA or explicit non-UI verification? | Yes | Required non-UI verification executed and passed. |
| Is the scope small enough for GPT-5.3 Spark or GPT-5.4 Mini? | Yes | Limited feature scope. |

## Findings

### Blocking

- None.

### Non-Blocking

- Environment variable contamination in the shell can make `test_scout_raises_on_missing_openai_key` non-deterministic unless `OPENAI_API_KEY` is forced empty.

## Merge Decision

**Decision:** merge

**Reason:**

- Required non-UI verification passes under controlled test env.
- Feature directly supports W3 false-confidence controls and remains aligned to current northstar.

**Merged into:** `rebuild/validated-leads-loop`

## Handoff

```text
Feature: F07 Source validator
Branch: feat/f07-source-validator
Status: merged_to_rebuild_branch
What changed: Source-evidence validation now resolves URLs and records field support/unsupported/failed status, plus resolved URL metadata, before those fields are treated as evidence.
Tests or QA run:
- `cd packages/core && uv run pytest tests/test_source_validation.py -q` (6 passed)
- `$env:OPENAI_API_KEY='' ; cd packages/core ; uv run pytest tests/test_source_validation.py tests/test_orchestrator.py -q` (16 passed)
Screenshots or report: `.gstack/qa-reports/qa-report-f07-source-validator-rerun-2026-05-10.md`
Northstar reflection: Source evidence is now validated and downgraded when inaccessible/unsupported, preventing URL-only confidence from propagating.
Next pointer: F08 Contact status model.
Open questions: Should `test_scout_raises_on_missing_openai_key` continue to set `OPENAI_API_KEY=''` centrally to avoid host-environment leaks?
```
