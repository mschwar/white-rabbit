# BUILDOUT-03 QA Report

> **Status:** Historical QA Record. This report is retained as evidence for the gate it evaluated, not as current instructions. Current product truth: `docs/00-product-northstar.md`; current state: `STATUS.md`; current reset execution: `docs/12-reset-gated-implementation-plan-2026-05-10.md`.


Date: 2026-05-08
Branch: feat/buildout-03-session-expiry
Feature: BUILDOUT-03 — Server-side session token expiry

## Summary
Pass. Browser QA confirmed the shared-password login gate still works, the protected Scout workspace loads after login, and sign-out returns to the login screen. The new server-side session-expiry behavior is covered by unit tests and matched the browser flow.

## Changes verified
- Logged in successfully at http://localhost:3000/login with the shared password from `apps/web/.env.local`.
- Confirmed the app redirected to the protected workspace after login.
- Opened the protected Scout workspace and verified the query form and reset control rendered correctly.
- Signed out and confirmed the app returned to the login screen.
- Ran the web test suite; `apps/web/src/lib/__tests__/auth.test.ts` now covers max-age expiry and clock-skew rejection.

## Why this matters
This feature closes the hole where a stolen session cookie could stay valid forever. The browser path still behaves normally, while the server now rejects stale or future-dated tokens.

## Findings
- No browser-visible app bugs were confirmed in this QA pass.
- Browser-expiry forging was not practical in the browser, so the expiry behavior was verified through the new unit tests instead. That is acceptable for this slice because the login/logout flow and protected-page access were both exercised in-browser.
- Tooling note: browser vision analysis returned a 401 from the external vision service, but screenshots were still captured successfully.

## Evidence
Screenshots captured:
- /Users/mschwar/.hermes/cache/screenshots/browser_screenshot_2d1fd0463f5b476f8fc26cf7d9eded6d.png
- /Users/mschwar/.hermes/cache/screenshots/browser_screenshot_6a0024f04e9a45cca3e6ca8fdffa3de5.png
- /Users/mschwar/.hermes/cache/screenshots/browser_screenshot_b772acc39534433d93354c94164a0533.png

Checks run:
- `npm test` in `apps/web` — passed
- `npm run build` in `apps/web` — passed
- Browser QA on `/login` and `/scout` — passed

Console: clean on the tested pages.

## Recommended actions
- Merge `feat/buildout-03-session-expiry`.
- Next buildout task is BUILDOUT-04 (strip VoIP bias; restore lost proxy-lead prompt instructions).
