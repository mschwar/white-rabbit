# QA Report — F01 Hide premature operator surfaces from primary navigation

> **Status:** Historical QA Record. This report is retained as evidence for the gate it evaluated, not as current instructions. Current product truth: `docs/00-product-northstar.md`; current state: `STATUS.md`; current rebuild execution: `docs/08-agentic-buildout-plan.md` and `docs/09-rebuild-phase-gates.md`.


**Branch:** feat/f01-hide-premature-surfaces  
**Date:** 2026-05-09  
**Required verification type:** Browser test (UI-visible feature)  
**Buildout plan:** docs/08-agentic-buildout-plan.md  
**Northstar:** docs/00-product-northstar.md  
**PR target:** rebuild/validated-leads-loop  

## Scope Checked

- Feature card read from `docs/08-agentic-buildout-plan.md` (F01).
- Verified on `/` and `/scout` in a browser session after shared-password login.
- Confirmed no source files outside the current feature intent were modified in this QA pass.
- Confirmed merge target remains `rebuild/validated-leads-loop`.

## Browser Test Steps

### Route: `/`

1. Start web on `localhost:3000` with:
   - `WR_SHARED_PASSWORD`
   - `WR_SESSION_SECRET`
   - `WR_API_BASE_URL`
2. Navigate to `/login`.
3. Submit shared password.
4. Confirm authenticated home route renders.
5. Verify home route has exactly one primary operator link and no recipe/batch/premature-management copy.
6. Capture screenshot.

### Route: `/scout`

1. Navigate from the authenticated session to `/scout`.
2. Verify Scout empty state header/content is visible.
3. Confirm no links to `recipe`, `batch`, and no copy mentioning:
   - FastAPI / raw endpoint
   - recipe storage
   - sandbox reset
4. Capture screenshot.

## Actual result

- Home has one primary operator path: **Open lead search**.
- `/scout` has no recipe/batch links and no banned implementation detail copy.
- Sandbox usage card appears with usage placeholder/loading state.
- One non-blocking console error observed: backend quota fetch returned `502` (expected in this environment because API backend was not intentionally started for this UI-only QA pass).

## Screenshots Required

| Required screenshot | Saved path | Pass/fail |
| --- | --- | --- |
| Home after login (`/`) | `.gstack/qa-reports/screenshots/f01-home-after-login.png` | Pass |
| Scout empty state (`/scout`) | `.gstack/qa-reports/screenshots/f01-scout-empty-state.png` | Pass |

## Tests Run

| Command | Result | Notes |
| --- | --- | --- |
| `npm test` (in `apps/web`) | Pass | 25 tests passed |
| `npm run build` (in `apps/web`) | Pass | Completed successfully |
| Playwright browser script (manual /home + /scout assertions + screenshots) | Pass | No banned link/copy on `/` or `/scout` |

## Northstar Reflection Result

| Question | Yes/No | Notes |
| --- | --- | --- |
| Does this directly improve natural-language query -> high-quality validated leads -> export? | Yes | It narrows the operator path to the lead-search flow, removing noisy admin surfaces. |
| Does it reduce false confidence, bad contacts, wrong personas, or unsupported source claims? | Yes | Removes premature organization of potentially untrusted output and backend-implementation signaling. |
| Does it avoid organizing or beautifying untrusted data? | Yes | Feature is focused on reducing surfaced surfaces, not post-collection framing. |
| Does it keep main untouched and target only `rebuild/validated-leads-loop`? | Yes | No `main` changes. |
| Is the feature independently mergeable? | Yes | UI and copy changes are isolated. |
| Can the next agent discover the state from docs without this chat? | Yes | Updated feature card + status docs and QA report. |
| Is there browser QA or explicit non-UI verification? | Yes | Browser QA completed on `/` and `/scout`. |
| Is the scope small enough for GPT-5.3 Spark or GPT-5.4 Mini? | Yes | Single-surface UI/presentation scope. |

## Findings

### Blocking

- None

### Non-Blocking

- `GET /api/sandbox` returns 502 while API backend is not running locally; this only affects usage card and is expected for this QA pass.

## Merge Decision

**Decision:** merge  
**Reason:** Feature behavior matches F01 acceptance criteria and did not introduce blockers; merge into `rebuild/validated-leads-loop`.

## Follow-Up Issues

- None

## Handoff

```text
Feature: F01 Hide premature operator surfaces from primary navigation
Branch: feat/f01-hide-premature-surfaces
Status: qa_passed (merged to rebuild_ branch)
What changed: QA verification and reporting only; runtime behavior unchanged from implementation.
Tests or QA run: npm test, npm run build, browser QA / and /scout
Screenshots or report: .gstack/qa-reports/qa-report-f01-hide-premature-surfaces-2026-05-09.md
Northstar reflection: pass
Next pointer: F02
Open questions: None
```
