# QA Report — BUILDOUT-17: Production verification

> **Status:** Historical QA Record. This report is retained as evidence for the gate it evaluated, not as current instructions. Current product truth: `docs/00-product-northstar.md`; current state: `STATUS.md`; current rebuild execution: `docs/08-agentic-buildout-plan.md` and `docs/09-rebuild-phase-gates.md`.


**Date:** 2026-05-09
**Branch:** main
**Repo:** /Users/mschwar/Documents/white-rabbit
**Target web:** https://white-rabbit-ten.vercel.app
**Target API:** https://white-rabbit-api.fly.dev/health
**Sources:** live Vercel/Fly checks, browser QA, repo docs
**Screenshots:** `.gstack/qa-reports/screenshots/buildout-17-*.png`
**Rubric:** `docs/qa-rubric.md` (Tier 6 browser smoke; plus Full-flow smoke coverage)

## Summary

Production is working end-to-end.

- Vercel production deployment for commit `f3b6a45` is `READY`.
- Fly health returns `200 {"status":"ok"}`.
- Anonymous protected-route access redirects to `/login?next=%2Fscout`.
- Wrong-password login is rejected with the friendly error state.
- Correct-password login succeeds and returns to the protected app.
- Scout queries return live leads and render cards correctly.
- Full flow works, including saved recipe creation, export building, feedback submission, and run closeout.
- Logout works and protected routes redirect again after sign-out.

Remaining risk: Fly trial auto-stop behavior can still stop one machine when idle; that is an infrastructure policy issue, not an app bug.

## Deployment verification

### Vercel
- Latest production deployment: `READY`
- Deployment URL: `https://white-rabbit-ofgtyr3sx-matts-projects-06539e54.vercel.app`
- Alias: `https://white-rabbit-ten.vercel.app`
- Commit SHA: `f3b6a4595af816f1981fea69a093e69072165b01`
- Commit message: `fix(prod): repair Vercel auth routing and verify live deploy`

### Fly
- Health endpoint: `200 {"status":"ok"}`
- `flyctl status` shows `deployed` version `3`
- Machine state snapshot during QA: one machine `started`, one machine `stopped`, both on image tag `deployment-01KR6YFANYBYX58ZNFZHW6C4YY`
- Interpretation: healthy service with trial auto-stop behavior present, not a deploy failure

## Browser QA walkthrough

### 1) Anonymous protected-route redirect
- Navigated to `/scout` while signed out.
- Browser redirected to `/login?next=%2Fscout`.
- Screenshot: `buildout-17-01-anon-scout-redirect.png`

### 2) Wrong-password login
- Submitted an incorrect password.
- Login page showed the friendly error state: `That password did not work. Try again.`
- Screenshot: `buildout-17-02-wrong-password.png`

### 3) Correct login
- Submitted the shared password.
- Redirected back into the protected app at `/scout`.
- Screenshot: `buildout-17-03-scout-after-login.png`

### 4) Scout query
- Query used: `Healthcare IT directors in Phoenix`
- Location filter: `Arizona`
- Live `/api/scout` response status: `200`
- First two leads rendered: `Mary Fox`, `Jim Hall`
- A non-blocking guardrail hint appeared: the query could be tighter by adding a company type or vertical.
- Screenshot: `buildout-17-04-scout-results.png`

### 5) Full flow: save, export, and feedback
I exercised the Full flow in two passes so both persistence branches were covered.

#### Pass A — save + export + feedback
- Full run saved successfully.
- Export built successfully.
- Clicked `usable` on the first lead.
- Recipes page showed the saved recipe and feedback summary updating to `Usable: 1`.
- Live `/api/full` response status: `200`
- Example recipe name: `QA prod smoke 2026-05-09 18-46-53`
- Screenshot(s):
  - `buildout-17-05-full-saved.png`
  - `buildout-17-06-full-export-ready.png`
  - `buildout-17-07-feedback-submitted.png`
  - `buildout-17-08-recipes-updated.png`

#### Pass B — close run and verify operator minutes
- Started a second Full run to confirm the closeout path.
- Closed the run with `12.5` operator minutes.
- Recipes page updated to show `Operator minutes: 12.5` and the scoreboard reflected the closed run.
- Live `/api/full` response status: `200`
- Example recipe name: `QA prod closed 2026-05-09 18-49-06`
- Screenshot(s):
  - `buildout-17-05b-full-closed.png`
  - `buildout-17-08b-recipes-closed.png`

### 6) Logout
- Signed out from the app.
- Browser returned to the login page.
- Re-checking `/scout` after logout redirected back to `/login?next=%2Fscout`.
- Screenshot: `buildout-17-09-logout.png`

## Console / network health

- JavaScript errors: `0`
- Page errors: `0`
- Warning count: `0`
- Non-blocking network noise: only expected Next.js `_rsc` navigation requests that aborted during route changes

## Result

BUILDOUT-17 is fully complete from a production-verification standpoint.

What passed:
- Vercel READY deployment on the expected commit
- Fly health check
- Login gate
- Protected-route redirect behavior
- Scout query rendering
- Full save/export/feedback flow
- Full closeout/operator-minutes flow
- Recipes page update
- Logout

What failed:
- Nothing functionally failed in production QA

## Screenshot inventory

- `.gstack/qa-reports/screenshots/buildout-17-01-anon-scout-redirect.png`
- `.gstack/qa-reports/screenshots/buildout-17-02-wrong-password.png`
- `.gstack/qa-reports/screenshots/buildout-17-03-scout-after-login.png`
- `.gstack/qa-reports/screenshots/buildout-17-04-scout-results.png`
- `.gstack/qa-reports/screenshots/buildout-17-05-full-saved.png`
- `.gstack/qa-reports/screenshots/buildout-17-06-full-export-ready.png`
- `.gstack/qa-reports/screenshots/buildout-17-07-feedback-submitted.png`
- `.gstack/qa-reports/screenshots/buildout-17-08-recipes-updated.png`
- `.gstack/qa-reports/screenshots/buildout-17-05b-full-closed.png`
- `.gstack/qa-reports/screenshots/buildout-17-08b-recipes-closed.png`
- `.gstack/qa-reports/screenshots/buildout-17-09-logout.png`
