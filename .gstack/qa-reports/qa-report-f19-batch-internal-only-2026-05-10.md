# QA Report - F19 Batch Workspace Internal-Only Policy

- Date: 2026-05-10
- Branch: `feat/f19-batch-internal-only`
- Feature: F19 - Batch Workspace Internal-Only Policy
- Verdict: Pass

## Scope

Verify that the red-gate operator home path at `/` still exposes no batch navigation, and that any remaining batch route is clearly framed as an internal-only evaluation surface rather than an operator-facing workflow.

## Findings And Fix

- Initial QA found that `/` already hid batch from the primary operator path, but `/batch` still rendered as a normal bulk-run workspace with no internal-only warning language.
- Fixed on the feature branch by adding an internal evaluation warning block to the batch workspace and extending the component test to assert the warning copy.

## Tests Run

1. `cd apps/web && npm test -- --run src/app/__tests__/page.test.tsx src/components/__tests__/batch-workspace.test.tsx`
   - Result: 2 files passed, 2 tests passed.
2. `cd apps/web && npm run build`
   - Result: production build passed.
   - Non-blocking warnings: Next.js workspace-root warning remains open; `middleware.ts` deprecation warning remains open from prior work.

## Browser QA

Local target: `http://localhost:3000`

Login:

- Used the shared-password login flow against the local Next app.
- Confirmed successful redirect to `/` after `POST /api/login`.

Assertions:

1. `/`
   - Confirmed the page loads the primary lead-search workspace.
   - Confirmed there are zero role-based links matching `batch` or `bulk`.
   - Confirmed there are zero visible buttons matching `batch` or `bulk`.
2. `/batch`
   - Loaded the route after login with `GET /api/batch` stubbed to an empty list so the page could render deterministically during browser QA.
   - Confirmed the page shows `Internal evaluation only`.
   - Confirmed the warning copy says the route is for Matt-run internal evaluation and not for Thomas or Lee daily prospecting.

## Screenshots

- `/Users/mschwar/Documents/white-rabbit/.gstack/qa-reports/screenshots/f19-01-home-no-batch-nav.png`
- `/Users/mschwar/Documents/white-rabbit/.gstack/qa-reports/screenshots/f19-02-batch-internal-only.png`

## Northstar Reflection

Pass. The feature keeps batch out of the primary red-gate operator loop and now explicitly marks the remaining route as internal evaluation only. It does not revive bulk workflow adoption, does not widen batch capabilities, and does not touch the search, validation, or scoring core.

## Merge Decision

Merge `feat/f19-batch-internal-only` into `rebuild/validated-leads-loop` only. Do not merge to `main`.
