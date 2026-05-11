# QA Report - R09 Tier Summary, Score Semantics, And Reason Language Reset

**Date:** 2026-05-11  
**QA agent:** prompt-b-r09-qa  
**Branch:** `feat/reset-r09-tier-summary-semantics`  
**Integration branch:** `rebuild/validated-leads-loop`  
**Decision:** pass - ready to merge to `rebuild/validated-leads-loop`

## Current State Proven

- `STATUS.md` names R09 as the only reset feature waiting for Prompt B QA.
- `docs/12-reset-gated-implementation-plan-2026-05-10.md` names R09 as `implemented_pending_qa` and keeps R10-R15 blocked.
- Local and pushed feature branch matched at `46dbde1013109488102c9ba6c99154bfdb515c4a`.
- `git status --short --branch` was clean on `feat/reset-r09-tier-summary-semantics...origin/feat/reset-r09-tier-summary-semantics` before QA changes.

## Commands Run

| Command | Result |
| --- | --- |
| `git fetch origin --prune` | pass |
| `git status --short --branch` | pass, clean feature branch |
| `git diff --check origin/rebuild/validated-leads-loop...HEAD` | pass |
| `cd packages/core && uv run pytest tests/test_source_validation.py tests/test_contact_status.py tests/test_scoring.py tests/test_orchestrator.py -q` | pass, `48 passed in 1.04s` |
| `cd apps/api && WR_API_INTERNAL_TOKEN=test-internal-token uv run pytest tests -q` | pass, `43 passed, 50 warnings in 2.86s` |
| `cd apps/web && npm test -- --run` | pass, `13` files / `30` tests passed |
| `cd apps/web && npm run build` | pass, existing Next.js workspace-root and middleware deprecation warnings |
| Playwright browser QA on `http://localhost:3007/scout?qa=validation-buckets` | pass, desktop and mobile screenshots captured |

## Browser QA

Fresh Prompt B browser QA exercised the deterministic validation-buckets fixture:

1. Started the web app on `http://localhost:3007`.
2. Opened `/scout?qa=validation-buckets`.
3. Logged in through the shared-password gate.
4. Ran the Full fixture query.
5. Confirmed `Tier summary` rendered.
6. Confirmed operator labels rendered: `READY`, `REVIEW`, `ORG-ONLY`, and `NOT FOUND`.
7. Confirmed READY reason language rendered with supported person, organization, source, and usable contact wording.

Screenshots:

- `.gstack/qa-reports/screenshots/r09-prompt-b-desktop.png`
- `.gstack/qa-reports/screenshots/r09-prompt-b-mobile.png`

Note: starting the local API server for browser support was blocked by the existing local `OPENAI_BASE_URL=http://localhost:11434/v1` environment pointing at an Ollama instance without `gpt-4o-mini`. The API verification itself passed through the test suite. Browser QA used the existing front-end fixture and stubbed only `/api/sandbox` usage-card fetches to avoid unrelated local API preflight noise.

## Northstar Drift Check

R09 aligns with `docs/00-product-northstar.md`:

- `high_trust_usable` remains the strict `READY` path.
- Review, organization-only, not-found, and failed rows remain visible instead of disappearing.
- Fit / Evidence / Contact wording now reads as signals, not generic readiness scores.
- Missing, failed, or unsupported contact evidence is capped and cannot retain strong-looking contact readiness.
- Unsupported field/source evidence is capped and cannot retain strong-looking evidence support.
- Reason language now says `READY` or `REVIEW` with the blocker instead of implying old score-pass confidence.

No external self-serve features, signup, billing, account/org model, public landing page, or frontend API-key handling changed.

## Scope Check

The branch stayed inside R09:

- Changed core score semantics, field descriptions, and reason copy.
- Changed web result typing, tier distribution display, and score-label copy.
- Added/updated focused core and web tests.
- Added R09 screenshots and handoff docs.

The branch did not implement adjacent reset features:

- No R10 primary search workspace simplification.
- No R11 compact CRM-first table redesign beyond R09 label/readiness wording.
- No R12 evidence dossier review mode.
- No R13 export rewrite.
- No R14 persistence/DB readback work.
- No RG4 unlock and no `main` sync.

## Result

R09 passes Prompt B QA. Because R09 is the last RG3 feature, RG3 should now move to Prompt C audit after the feature branch is merged into `rebuild/validated-leads-loop`. Downstream RG4 remains blocked until Prompt C records a gate decision.
