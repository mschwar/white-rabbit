# QA Report - F15 Evidence Drawer Or Dossier

**Feature ID:** F15  
**Feature name:** Evidence Drawer Or Dossier  
**Branch:** feat/f15-evidence-drawer  
**PR target:** rebuild/validated-leads-loop  
**Date:** 2026-05-10  
**Agent:** Codex f15-qa  
**Required verification type:** Browser QA  
**Buildout plan:** docs/08-agentic-buildout-plan.md  
**Northstar:** docs/00-product-northstar.md  

## Scope Checked

- Feature card read: `docs/08-agentic-buildout-plan.md` (F15)  
- Files changed: No code changes on this QA pass; docs + screenshots + report only.  
- Explicit anti-goals reviewed: no source validation redesign, no page redesign, no CRM profile view.  
- Confirmed `main` untouched: yes  
- Confirmed merge target is `rebuild/validated-leads-loop`: yes  

## Browser Test Steps

**Route(s):**

- `http://localhost:3000/scout?qa=validation-buckets`

**Steps:**

1. Open `/scout?qa=validation-buckets` and log in using `apps/web/.env.local` shared password.
2. Keep host as `localhost` and run one Scout search to load the QA fixture response.
3. Open evidence for `Jane Smith` and confirm the drawer fields.
4. Open evidence for `Broken District` and confirm the drawer fields.
5. Capture required screenshots.

**Expected result:**

- Drawer opens from both usable and failed/noisy rows.
- Drawer shows field-level: status, source URL, checked_at, notes, and evidence snippet.

**Actual result:**

- Passed. Fixture data is present for `Jane Smith` and `Broken District`.
- Usable/failed drawers opened and displayed all required field evidence details.
- Screenshots captured and saved under `.gstack/qa-reports/screenshots/`.

## Screenshots Required

| Required screenshot | Saved path | Pass/fail |
| --- | --- | --- |
| Evidence drawer for usable row | `.gstack/qa-reports/screenshots/f15-01-usable-evidence-drawer.png` | pass |
| Evidence drawer for failed/noisy row | `.gstack/qa-reports/screenshots/f15-02-failed-evidence-drawer.png` | pass |

## Tests Run

| Command | Result | Notes |
| --- | --- | --- |
| `cd apps/web && npm test -- --run` | pass | 13 files, 28 tests passed |
| `cd apps/web && npm run build` | pass | Next.js build completed |
| `Playwright fixture login + evidence drawer capture` | pass | Logged in with shared password; loaded fixture via `qa=validation-buckets`; captured both screenshots |

## Northstar Reflection Result

Answer each before merge.

| Question | Yes/No | Notes |
| --- | --- | --- |
| Does this directly improve natural-language query -> high-quality validated leads -> export? | Yes | Improves operator trust-check step without changing query/export flow. |
| Does it reduce false confidence, bad contacts, wrong personas, or unsupported source claims? | Yes | Makes evidence states explicit per field. |
| Does it avoid organizing or beautifying untrusted data? | Yes | No new data source or ranking logic added; visibility only. |
| Does it keep main untouched and target only `rebuild/validated-leads-loop`? | Yes | QA only touched docs/reports; merge target remains rebuild branch. |
| Is the feature independently mergeable? | Yes | UI-only, no core validation changes required. |
| Can the next agent discover state from docs without chat context? | Yes | `STATUS.md` and `docs/08-agentic-buildout-plan.md` updated with merge status and next pointer. |
| Is there browser QA or explicit non-UI verification? | Yes | Browser QA completed on fixture route. |
| Is the scope small enough for GPT-5.3 Spark or GPT-5.4 Mini? | Yes | Single component-level feature. |

## Findings

### Blocking

- None.

### Non-Blocking

- `next dev` requires `NEXT_DISABLE_TURBOPACK=1` locally in this environment due a turbopack panic; `npm run build` and browser screenshot flow were otherwise successful.

## Merge Decision

**Decision:** merge  

**Reason:**

- All required implementation and verification criteria passed.

**Merged into:** rebuild/validated-leads-loop

## Follow-Up Issues

- None.

## Handoff

```text
Feature: F15 - Evidence Drawer Or Dossier
Branch: feat/f15-evidence-drawer
Status: merged_to_rebuild_branch
What changed: Evidence drawer visibility and per-field support details from validation rows.
Tests or QA run:
 - cd apps/web && npm test -- --run (13 files, 28 tests passed)
 - cd apps/web && npm run build
 - Browser QA on http://localhost:3000/scout?qa=validation-buckets
Screenshots or report: .gstack/qa-reports/screenshots/f15-01-usable-evidence-drawer.png, .gstack/qa-reports/screenshots/f15-02-failed-evidence-drawer.png
Northstar reflection: Pass; drawer adds field-level confidence transparency without widening operator surfaces.
Next pointer: F16 remains blocked; prepare for export evidence fields once gate/reopen conditions are defined.
Open questions: none blocking
```
