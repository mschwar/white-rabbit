# QA Report - R14B UI/UX Consistency Pass

**Date:** 2026-05-12
**Prompt:** Prompt B
**Feature:** R14B - UI/UX consistency pass
**Branch:** `feat/reset-r14b-ui-ux-consistency-pass`
**Base:** `main`
**Decision:** Pass

## State Proof

- `docs/reset-current-assignment.json` named Prompt B, R14B, and `feat/reset-r14b-ui-ux-consistency-pass`; the current branch matched.
- `git fetch origin` completed before QA. Local `main` already contained the R14A mainline merge/QA commits while `origin/main` was behind; QA therefore compared R14B against local `main`, the active integration branch in this checkout.
- `git status --short --branch` showed only the R14B branch plus the unrelated untracked `WhiteRabbit_brand_design_pack.zip`, which was left untouched.
- `git diff --name-status main...HEAD` stayed inside the R14B UI slice, reset handoff docs, assignment lock, and saved R14B screenshot artifacts.

## Scope Reviewed

R14B aligns the primary operator surface with the approved RG4 navy chassis and paper evidence direction:

- CSV export moved into the results summary/control strip.
- Low-public-signal guidance appears when returned rows or READY rows are below useful signal.
- The CRM-first desktop table is denser, keeps blockers next to status, and removes duplicate READY-row rationale.
- The evidence drawer now reads as a light paper dossier with status, primary blocker, field support, source trail, and existing correction controls preserved.
- Primary empty/results/export/evidence/low-signal/mobile surfaces remain aligned with `DESIGN.md` and `docs/mockups/rg4-refreshed-preflight-2026-05-12/`.

No backend/API/core/search/export logic/persistence/source-assisted compiler/benchmark/dogfood/R14C deployment-smoke/public SaaS scope landed.

Prompt B made one narrow UI-copy fix before passing QA: shared evidence-drawer correction copy said "Full run" / "Full search" in strings reachable from the primary operator path. Those strings now say "saved run" / "saved search" so primary mode does not leak Scout/Full mode chrome.

## Verification

| Check | Result |
| --- | --- |
| `git diff --check` | Passed |
| `git diff --check main...HEAD` | Passed |
| `cd apps/web && npm test -- --run` | Passed, `13` files and `30` tests |
| `cd apps/web && npm run build` | Passed, with the existing Next.js workspace-root inference and `middleware` deprecation warnings |
| `cd apps/api && WR_API_INTERNAL_TOKEN=test-internal-token uv run pytest tests -q` | Passed, `53 passed`, with the existing datetime deprecation warnings |
| Targeted primary-copy scan | Passed: no `Run Full`, `Full run`, `Full search`, or `Run a Full` remains in the changed shared evidence-drawer copy; remaining Scout/Full labels are in the legacy non-primary mode controls |

## Browser Evidence Reviewed

Reviewed the saved R14B browser QA artifacts:

- `.gstack/qa-reports/screenshots/r14b-ui-ux-consistency-2026-05-12/01-desktop-empty.png`
- `.gstack/qa-reports/screenshots/r14b-ui-ux-consistency-2026-05-12/02-desktop-results.png`
- `.gstack/qa-reports/screenshots/r14b-ui-ux-consistency-2026-05-12/03-desktop-export-ready.png`
- `.gstack/qa-reports/screenshots/r14b-ui-ux-consistency-2026-05-12/04-desktop-evidence-dossier.png`
- `.gstack/qa-reports/screenshots/r14b-ui-ux-consistency-2026-05-12/05-desktop-low-signal.png`
- `.gstack/qa-reports/screenshots/r14b-ui-ux-consistency-2026-05-12/06-mobile-empty.png`
- `.gstack/qa-reports/screenshots/r14b-ui-ux-consistency-2026-05-12/07-mobile-results.png`
- `.gstack/qa-reports/screenshots/r14b-ui-ux-consistency-2026-05-12/browser-qa-summary.json`

Observed:

- Empty state uses the approved wordmark-first identity, navy chassis, single target input, and one `Find Candidates` command.
- Results state keeps the table as the hero, preserves READY/REVIEW/ORG-ONLY/NOT FOUND visibility, places CSV export in the summary strip, and keeps uncertain rows visibly non-CRM-ready.
- Export-ready state preserves the secondary `Download CSV` action without creating an audit-first export panel.
- Evidence dossier uses the light paper treatment and exposes primary blocker, field support, and source trail without unapproved mascot imagery.
- Low-signal state shows returned rows and explains the low public data footprint without hiding blockers.
- Mobile empty/results screenshots render inside the viewport. The saved summary reports `scrollWidth=390` and `innerWidth=390`.

## Northstar Check

Pass. The branch improves the operator's command, categorize, prove loop without changing data semantics or making weak rows look CRM-ready. Export remains sales-first and secondary to row review. Product remains red; this feature does not advance RG5 by itself.

## Result

QA passed. Merge only to `main`.

Queue update after merge:

- Mark R14B `merged_to_mainline`.
- Mark R14C `ready`.
- Keep RG5 Prompt C blocked until R14C passes Prompt B and merges.
- Keep RG6 and dogfood blocked.
