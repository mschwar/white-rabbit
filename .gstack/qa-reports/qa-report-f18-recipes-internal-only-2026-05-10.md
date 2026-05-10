# QA Report - F18 Recipe Library Internal-Only Policy

- Date: 2026-05-10
- Branch: `feat/f18-recipes-internal-only`
- Feature: F18 - Recipe Library Internal-Only Policy
- Verdict: Pass

## Scope

Verify that the red-gate operator home path at `/` still exposes no recipe navigation, and that `/recipes` is clearly framed as an internal-only evaluation surface rather than an operator-facing workflow.

## Tests Run

1. `cd apps/web && npm test -- --run src/components/__tests__/recipes-library.test.tsx src/app/__tests__/page.test.tsx`
   - Result: 2 files passed, 3 tests passed.
2. `cd apps/web && npm run build`
   - Result: production build passed.
   - Non-blocking warnings: Next.js inferred the workspace root from `/Users/mschwar/package-lock.json`; `middleware.ts` deprecation warning remains open from prior work.

## Browser QA

Local target: `http://localhost:3000`

Login:

- Used the shared-password login flow against the local Next app.
- Confirmed successful redirect to `/` after `POST /api/login`.

Assertions:

1. `/`
   - Confirmed the page loads the primary lead-search workspace.
   - Confirmed there are zero `a[href="/recipes"]` links on the page.
   - Confirmed there are zero visible role-based links matching `recipe`.
2. `/recipes`
   - Loaded the route after login with API responses stubbed for recipe list, runs, and scoreboard so the page could render the intended internal review state during browser QA.
   - Confirmed the page shows `Recipe library`.
   - Confirmed the warning block reads `Internal evaluation only`.
   - Confirmed the warning copy says the route is for Matt-run internal evaluation and not for Thomas or Lee daily prospecting.

## Screenshots

- `/Users/mschwar/Documents/white-rabbit/.gstack/qa-reports/screenshots/f18-01-home-no-recipe-nav.png`
- `/Users/mschwar/Documents/white-rabbit/.gstack/qa-reports/screenshots/f18-02-recipes-internal-only.png`

## Northstar Reflection

Pass. The feature keeps recipes out of the primary red-gate operator loop while allowing internal review access with explicit warning language. It does not reintroduce recipes into navigation, does not expand recipe workflows, and does not touch search, extraction, or scoring behavior.

## Merge Decision

Merge `feat/f18-recipes-internal-only` into `rebuild/validated-leads-loop` only. Do not merge to `main`.
