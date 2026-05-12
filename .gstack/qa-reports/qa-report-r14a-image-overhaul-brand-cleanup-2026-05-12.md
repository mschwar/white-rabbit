# QA Report - R14A Image Overhaul And Approved Brand Asset Cleanup

**Date:** 2026-05-12
**Prompt:** Prompt B
**Feature:** R14A - Image overhaul and approved brand asset cleanup
**Branch:** `feat/reset-r14a-image-overhaul-brand-cleanup`
**Base:** `origin/main`
**Decision:** Pass

## State Proof

- At QA time, `STATUS.md` and `docs/reset-current-assignment.json` both pointed at R14A Prompt B on the correct feature branch.
- `git status --short --branch` showed the feature branch plus one unrelated untracked file, `WhiteRabbit_brand_design_pack.zip`; it was left untouched.
- `git diff --name-only main...HEAD` stayed inside the brand cleanup slice plus the expected reset handoff docs and QA artifacts.

## Scope Reviewed

R14A imports the approved design-pack favicon, touch, manifest, and social assets; removes the old generated rabbit/lens/rabbit-mark rasters; replaces the primary shell's placeholder brand mark with the approved wordmark-first identity; and refreshes login/metadata branding without touching backend, export, persistence, or dogfood behavior.

The branch diff remained confined to:

- `apps/web/public/android-chrome-192x192.png`
- `apps/web/public/android-chrome-512x512.png`
- `apps/web/public/apple-touch-icon.png`
- `apps/web/public/brand/white-rabbit-og-light.png`
- `apps/web/public/brand/white-rabbit-og-navy.png`
- `apps/web/public/brand/white-rabbit-rabbit-mark.png` removed
- `apps/web/public/brand/white-rabbit-search-dark.png` removed
- `apps/web/public/brand/white-rabbit-search-light.png` removed
- `apps/web/public/site.webmanifest`
- `apps/web/src/app/favicon.ico`
- `apps/web/src/app/globals.css`
- `apps/web/src/app/layout.tsx`
- `apps/web/src/app/login/page.tsx`
- `apps/web/src/components/brand-identity.tsx`
- `apps/web/src/components/scout-workspace.tsx`
- `apps/web/src/middleware.ts`
- `docs/brand/white-rabbit-brand-tokens.draft.json`
- `docs/brand/white-rabbit-draft-design-brand-schema-2026-05-10.md`
- `docs/reset-current-assignment.json`
- `docs/12-reset-gated-implementation-plan-2026-05-10.md`
- `STATUS.md`
- `.gstack/qa-reports/r14a-brand-cleanup-prompt-a-browser-qa-2026-05-12.md`
- `.gstack/qa-reports/screenshots/r14a-brand-cleanup-2026-05-12/*`

No backend/API/core/search/export/persistence/source-assisted compiler/benchmark/dogfood/deployment-promotion behavior changed.

## Verification

| Check | Result |
| --- | --- |
| `git diff --check` | Passed |
| `cd apps/web && npm test -- --run` | Passed, `13` files and `30` tests |
| `cd apps/web && npm run build` | Passed, with the existing Next.js workspace-root inference and `middleware` deprecation warnings |
| `cd apps/api && WR_API_INTERNAL_TOKEN=test-internal-token uv run pytest tests -q` | Passed, `53 passed`, with the existing datetime deprecation warnings |

## Browser And Asset Evidence

Reviewed the saved browser QA artifacts:

- `.gstack/qa-reports/screenshots/r14a-brand-cleanup-2026-05-12/desktop-login.png`
- `.gstack/qa-reports/screenshots/r14a-brand-cleanup-2026-05-12/desktop-empty.png`
- `.gstack/qa-reports/screenshots/r14a-brand-cleanup-2026-05-12/desktop-results.png`
- `.gstack/qa-reports/screenshots/r14a-brand-cleanup-2026-05-12/mobile-login.png`
- `.gstack/qa-reports/screenshots/r14a-brand-cleanup-2026-05-12/mobile-empty.png`
- `.gstack/qa-reports/screenshots/r14a-brand-cleanup-2026-05-12/mobile-results.png`

Observed:

- Login, empty, and results states stay usable on desktop and mobile.
- The UI reads as wordmark-first; no standalone rabbit/mascot/ad hoc CSS logo appears in the product surface.
- Desktop browser metrics from the Prompt A QA artifact remain `scrollWidth=1440` at `1440` width.
- Mobile browser metrics from the Prompt A QA artifact remain `scrollWidth=390` at `390` width.

Live asset reachability was verified against a temporary local Next dev server at `http://127.0.0.1:3014`:

- `apple-touch-icon.png` returned `200`.
- `site.webmanifest` returned `200`.
- `brand/white-rabbit-og-light.png` returned `200`.
- `favicon.ico` returned `200`.
- `brand/white-rabbit-rabbit-mark.png` returned `404`.
- `brand/white-rabbit-search-dark.png` returned `404`.
- `brand/white-rabbit-search-light.png` returned `404`.

## Northstar Check

Pass. R14A stays inside the product northstar: approved browser/social branding only, no backend or export changes, no new operator chrome, and no relaxation of the strict usable-lead or evidence rules.

## Result

QA passed. Merge only to `main`.

Queue update after merge:

- Mark R14A `merged_to_mainline`.
- Mark R14B `ready`.
- Keep R14C, RG6, and dogfood blocked.
