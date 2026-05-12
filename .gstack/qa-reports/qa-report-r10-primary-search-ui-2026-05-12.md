# QA Report - R10 Primary Search Workspace Simplification

**Date:** 2026-05-12
**Prompt:** Prompt B
**Feature:** R10 - Primary search workspace simplification
**Branch:** `feat/reset-r10-primary-search-ui`
**Base:** `origin/rebuild/validated-leads-loop`
**Decision:** Pass

## State Proof

- `STATUS.md` identifies R10 on `feat/reset-r10-primary-search-ui` as implemented and waiting for Prompt B QA.
- `docs/12-reset-gated-implementation-plan-2026-05-10.md` identifies the same single Prompt B handoff and marks R11/R12 blocked before R10 QA.
- `origin/feat/reset-r10-primary-search-ui` exists at `b98ac92` and is one commit ahead of `origin/rebuild/validated-leads-loop` at `beb0db9`.
- `git branch -r --contains origin/feat/reset-r10-primary-search-ui` returns only `origin/feat/reset-r10-primary-search-ui`, so the feature was not already merged before QA.
- `git status --short --branch` returned clean on `feat/reset-r10-primary-search-ui...origin/feat/reset-r10-primary-search-ui` before QA doc updates.

## Required Verification

| Check | Result |
| --- | --- |
| `git diff --check` | Passed |
| `cd apps/web && npm test -- --run` | Passed, `13` files and `30` tests |
| `cd apps/web && npm run build` | Passed, with existing Next.js workspace-root and `middleware` deprecation warnings |
| Production browser QA | Passed on `http://localhost:3000/` using `next start` and local test auth |

## Browser QA

Screenshots:

- `.gstack/qa-reports/screenshots/r10-primary-search-ui-prompt-b-2026-05-12/01-desktop-empty.png`
- `.gstack/qa-reports/screenshots/r10-primary-search-ui-prompt-b-2026-05-12/02-desktop-loading.png`
- `.gstack/qa-reports/screenshots/r10-primary-search-ui-prompt-b-2026-05-12/03-mobile-empty.png`
- `.gstack/qa-reports/screenshots/r10-primary-search-ui-prompt-b-2026-05-12/04-mobile-loading.png`

Verified desktop `1440x1000` and mobile `390x844` states:

- One visible Target input, one Source context input, and one candidate-search command.
- Empty state matches the approved RG4 direction: deep navy chassis, paper command surface, neutral `WR` placeholder, and source-assisted operator language.
- Loading state appears from a real form submit while `/api/scout` is held by Playwright, with visible evidence-forming copy and stage labels.
- No visible Scout/Full controls.
- No always-visible Search usage quota or sandbox card.
- No prompt, gate, sprint, R10/RG4, or implementation-copy leak.
- No horizontal overflow on desktop or mobile.
- Console had no errors in the final production run. The only request failures were benign aborted Next RSC prefetches for login links during navigation.

## Northstar Drift Check

R10 stays aligned with `docs/00-product-northstar.md`:

- Keeps the app internal and red-gate scoped; no public landing, signup, accounts, billing, or `main` promotion.
- Keeps the primary operator path focused on target plus source context, not recipes, batch, scoreboards, sandbox reset, or implementation machinery.
- Does not claim CRM-ready results, relax validation semantics, invent contacts, or alter score semantics.
- Does not move vendor/API keys into the frontend.
- Preserves the source-assisted research direction without presenting untrusted result rows as proven value.

## Scope Check

The branch diff against `origin/rebuild/validated-leads-loop` is limited to:

- `apps/web/src/components/scout-workspace.tsx`
- `apps/web/src/app/__tests__/page.test.tsx`
- `apps/web/src/components/__tests__/scout-workspace.test.tsx`
- `STATUS.md`
- `docs/12-reset-gated-implementation-plan-2026-05-10.md`
- R10 screenshots under `.gstack/qa-reports/screenshots/`

No `apps/api`, `packages/core`, source-assisted compiler, benchmark, persistence, export, dogfood, RG5/RG6, or `main` scope landed. The existing results table and evidence drawer were not expanded into the R11 compact CRM-first results table or R12 dossier mode.

## Result

R10 passes Prompt B. Merge only into `rebuild/validated-leads-loop`. Mark R10 `merged_to_rebuild_branch`, mark R11 `ready`, keep R12/RG5/RG6/export/dogfood/main blocked, and do not run Prompt C until R10-R12 have all passed Prompt B and merged.
