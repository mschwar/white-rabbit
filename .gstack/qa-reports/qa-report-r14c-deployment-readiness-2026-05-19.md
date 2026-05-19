# QA Report — R14C deployment readiness and operator-use smoke

- Date: 2026-05-19
- Branch under test: `feat/reset-r14c-deployment-readiness-smoke`
- Base branch: `main`
- Target URL: `http://127.0.0.1:3000`
- Mode: diff-aware / standard
- Framework: Next.js
- Scope: shared-password login gate, protected home redirect, operator results review, evidence drawer, CSV export readiness under `next start`
- Browser evidence: `.gstack/qa-reports/screenshots/r14c-prod-smoke/`
- Duration: focused QA + fix loop in-session

## Baseline

Health score before fixes: 97/100

Category scores before fixes:
- Console: 100
- Links: 100
- Visual: 100
- Functional: 85
- UX: 100
- Performance: 100
- Content: 100
- Accessibility: 100

Top issue before fixes:
1. ISSUE-001 — High — functional
   - Symptom: successful shared-password login on local production smoke redirected the browser from `127.0.0.1` to `localhost`, so the session cookie stayed on the wrong host and browser automation could not reach the protected workspace.
   - Repro: open `/login`, submit valid password, observe redirect host mismatch.
   - Evidence: Playwright failure notes plus local browser/network reproduction during QA.

## Fixes applied

### ISSUE-001 — shared-password login redirected to the wrong host in production smoke
- Status: verified
- Fix: login redirects now derive origin from forwarded/host headers instead of trusting the local Next request URL.
- Files changed:
  - `apps/web/src/app/api/login/route.ts`
  - `apps/web/src/app/api/login/route.regression-1.test.ts`
  - `apps/web/e2e/operator-smoke.spec.ts`
- Regression coverage:
  - `src/app/api/login/route.regression-1.test.ts`
  - existing auth/login tests still pass

## Browser verification

Verified in a real browser flow via Playwright production smoke against `next start`:
- login gate renders correctly
- unauthenticated `/` redirects to `/login?next=%2F`
- shared-password login reaches the protected workspace
- mocked operator run renders categorized results
- evidence drawer opens on READY row
- CSV export becomes ready and downloads successfully

Key screenshots:
- `.gstack/qa-reports/screenshots/r14c-prod-smoke/01-login-gate.png`
- `.gstack/qa-reports/screenshots/r14c-prod-smoke/03-results-overview.png`
- `.gstack/qa-reports/screenshots/r14c-prod-smoke/04-evidence-drawer.png`
- `.gstack/qa-reports/screenshots/r14c-prod-smoke/05-export-ready.png`
- `.gstack/qa-reports/screenshots/r14c-prod-smoke/browser-qa-summary.json`

Visual notes:
- Login gate looks coherent: centered card, consistent wordmark, clear field hierarchy, and no obvious spacing or contrast problems.
- Results overview looks coherent: approved navy/paper shell, clear summary counts, visible low-signal warning, and readable CRM-first table.
- Evidence drawer looks coherent: overlay focus works, structure is readable, and status/blocker cards remain legible.
- Export-ready state looks coherent: rebuild/download actions are visible without crowding the review surface.

## Validation commands

Executed successfully:
- `cd apps/web && npm test -- --run src/app/api/login/route.regression-1.test.ts src/lib/__tests__/auth.test.ts src/app/api/login/route.test.ts`
- `cd apps/web && npm run test:e2e:prod`

Artifact summary from browser smoke:
- downloaded file: `white-rabbit-lead-export-2026-05-19.csv`
- exported rows: 3 data rows
- first CSV header begins with sales-first fields (`lead_name,title,organization,email,...`)

## Deferred / not proven here

- Live Fly `/health` and `/readiness` could not be directly re-verified in this session because direct API curl access had been blocked earlier.
- This QA run used mocked `/api/scout` browser data for deterministic operator-path verification.

## Final result

Health score after fixes: 100/100

Summary:
- Total issues found: 1
- Fixes applied: 1 verified, 0 best-effort, 0 reverted
- Deferred issues: 0 product issues in the browser flow; live remote API smoke remains an external verification gap
- Health score delta: 97 → 100

PR summary:
> QA found 1 issue, fixed 1, health score 97 → 100.
