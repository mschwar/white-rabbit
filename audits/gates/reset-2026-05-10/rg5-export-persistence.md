# Reset Gate Review - RG5 Sales-First Export And Persistence

**Branch:** `audit/reset-rg5-export-persistence`
**Integration branch:** `main`
**Date:** 2026-05-22
**Decision:** advance
**Current product gate:** red

## Evidence Used

- Control docs: `AGENTS.md`, `STATUS.md`, `docs/reset-current-assignment.json`, `docs/00-product-northstar.md`, `docs/12-reset-gated-implementation-plan-2026-05-10.md`, `docs/13-pipeline-orchestrator-contract-2026.md`, and `docs/03-decisions.md`.
- Baseline product reality: `audits/zero-trust-codebase-audit-2026-05-10.md`.
- Design authority: `DESIGN.md` and approved RG4 mockups under `docs/mockups/rg4-refreshed-preflight-2026-05-12/`.
- Feature QA reports:
  - `.gstack/qa-reports/qa-report-r13-sales-first-export-2026-05-12.md`
  - `.gstack/qa-reports/qa-report-r14-persistence-quality-tieout-2026-05-12.md`
  - `.gstack/qa-reports/qa-report-r14a-image-overhaul-brand-cleanup-2026-05-12.md`
  - `.gstack/qa-reports/qa-report-r14b-ui-ux-consistency-2026-05-12.md`
  - `.gstack/qa-reports/qa-report-r14c-deployment-readiness-2026-05-19.md`
- Saved export and smoke artifacts:
  - `.gstack/qa-reports/csv/r13-sales-first-export-2026-05-12/primary-sales-first-export.csv`
  - `.gstack/qa-reports/csv/r13-sales-first-export-2026-05-12/browser-qa-summary.json`
  - `.gstack/qa-reports/screenshots/r14c-prod-smoke/browser-qa-summary.json`
  - `.gstack/qa-reports/screenshots/r14c-prod-smoke/01-login-gate.png`
  - `.gstack/qa-reports/screenshots/r14c-prod-smoke/03-results-overview.png`
  - `.gstack/qa-reports/screenshots/r14c-prod-smoke/04-evidence-drawer.png`
  - `.gstack/qa-reports/screenshots/r14c-prod-smoke/05-export-ready.png`
- Current RG5 raw evidence: `audits/raw/reset-2026-05-10/rg5/`.

## State Proof

| Check | Result | Evidence |
| --- | --- | --- |
| Current assignment | Prompt C, RG5 | `docs/reset-current-assignment.json` |
| R13 status | merged to mainline | `.gstack/qa-reports/qa-report-r13-sales-first-export-2026-05-12.md`; reset plan feature table |
| R14 status | merged to mainline | `.gstack/qa-reports/qa-report-r14-persistence-quality-tieout-2026-05-12.md`; reset plan feature table |
| R14A status | merged to mainline | `.gstack/qa-reports/qa-report-r14a-image-overhaul-brand-cleanup-2026-05-12.md`; reset plan feature table |
| R14B status | merged to mainline | `.gstack/qa-reports/qa-report-r14b-ui-ux-consistency-2026-05-12.md`; reset plan feature table |
| R14C status | merged to mainline | `.gstack/qa-reports/qa-report-r14c-deployment-readiness-2026-05-19.md`; reset plan feature table |
| Product gate | red | `docs/00-product-northstar.md`; baseline zero-trust audit |

## Commands Run

```bash
git status --short --branch && git branch --show-current
git fetch origin
git checkout main
git pull --ff-only origin main
git checkout -b audit/reset-rg5-export-persistence
git diff --check
python3 - <<'PY'
# redacted environment/config presence check
PY
# attempted direct production curl of stable Vercel/Fly endpoints; blocked by execution environment
cd apps/web && npm test -- --run src/lib/__tests__/full-export.test.ts src/components/__tests__/scout-workspace.test.tsx src/app/api/runs/[run_id]/leads/route.test.ts
cd apps/web && npm test -- --run src/lib/__tests__/full-export.test.ts
cd apps/web && npx vitest run --pool=threads src/lib/__tests__/full-export.test.ts
cd apps/api && WR_API_INTERNAL_TOKEN=test-internal-token uv run pytest tests/test_api.py -q -k 'persistence_readback or run_leads or full_endpoint_returns_persisted or scout_endpoint_returns_scoped_payload'
```

Command outputs and notes are saved under `audits/raw/reset-2026-05-10/rg5/`.

## Live Results

No new remote live result was captured during this audit.

The attempted direct production curl to the stable operator/API endpoints was blocked by the execution environment with `BLOCKED: User denied. Do NOT retry.` This audit therefore uses the existing R14C deployment-readiness smoke evidence and explicitly carries forward the R14C caveat that live Fly `/health` and `/readiness` were not directly re-proven during that session.

Saved R14C browser-smoke evidence still proves the local production-like `next start` operator path:

- unauthenticated `/` redirects to `/login?next=%2F`;
- shared-password login reaches the protected workspace;
- mocked operator run renders categorized rows;
- evidence drawer opens;
- CSV export builds and downloads;
- primary mode has no visible Scout/Full chrome (`scoutVisible=0`, `fullVisible=0`).

## Screenshots And Artifacts

- R13 51-row export artifact: `.gstack/qa-reports/csv/r13-sales-first-export-2026-05-12/primary-sales-first-export.csv`
- R13 browser/CSV summary: `.gstack/qa-reports/csv/r13-sales-first-export-2026-05-12/browser-qa-summary.json`
- R14C screenshots:
  - `.gstack/qa-reports/screenshots/r14c-prod-smoke/01-login-gate.png`
  - `.gstack/qa-reports/screenshots/r14c-prod-smoke/03-results-overview.png`
  - `.gstack/qa-reports/screenshots/r14c-prod-smoke/04-evidence-drawer.png`
  - `.gstack/qa-reports/screenshots/r14c-prod-smoke/05-export-ready.png`
- R14C browser summary: `.gstack/qa-reports/screenshots/r14c-prod-smoke/browser-qa-summary.json`
- RG5 audit artifact summary: `audits/raw/reset-2026-05-10/rg5/artifact-summary.md`

## Value Prop Verdict

RG5 is sufficient to advance to the dogfood/kill decision packet, but not sufficient to change the product launch color.

The export/persistence loop now satisfies the RG5 implementation value proposition:

- export is available from the primary operator path after rows exist;
- the first ten CSV headers are sales-useful fields: `lead_name`, `title`, `organization`, `email`, `email_status`, `phone`, `phone_status`, `usable_candidate`, `operator_label`, `candidate_category`;
- READY/high-trust usable rows sort first in saved export evidence;
- uncertain rows retain `operator_label`, `candidate_category`, `usable_candidate`, source URLs, validation notes, field/contact statuses, checked timestamps, and run/query context;
- R14 persistence/readback QA verifies `/scout`, `/full`, protected run-lead readback, row-count tie-out, tier distribution, and candidate-category distribution;
- R14A/R14B/R14C closed the brand, visual consistency, mobile overflow, and local production-smoke slices enough for a decision packet.

The product remains red because live data quality, broad autonomous result quality, production endpoint proof, and Thomas/Lee no-research dogfood criteria are not proven by RG5. Those belong to RG6 and the product red/yellow/green launch gate, not to the export/persistence implementation gate.

## Findings

1. **Sales-first CSV ordering is proven in saved artifacts.** The R13 51-row export starts with CRM-facing fields and pushes run/audit metadata later.
2. **Uncertain rows keep safety context.** Export rows preserve tier/category/operator labels and validation notes, so REVIEW/ORG-ONLY/NOT FOUND rows cannot silently masquerade as READY rows.
3. **Persistence/readback is proven at test and API-contract level.** R14 Prompt B verified response, persistence, DB readback, and exportable row counts match in the API test suite.
4. **Primary path deployment smoke is mechanically proven locally.** R14C verified login, protected workspace, results, evidence drawer, and CSV export under `next start` with deterministic data.
5. **Fresh local test reruns were environment-blocked.** Vitest worker startup timed out before tests executed, and targeted API pytest timed out during setup/collection in this shell. The failure mode is recorded as audit-environment instability rather than a product regression because the same checks passed in Prompt B reports and no code changed before the failed reruns.
6. **Fresh remote endpoint proof is still missing.** Direct production curl was blocked in this execution environment; R14C also recorded that live Fly `/health` and `/readiness` were not directly re-verified.

## What Worked

- R13 export artifacts show 51 data rows, not a 3-4-row trickle, for the high-volume browser export fixture.
- First five CSV lines show READY rows first with source URLs, validation notes, checked timestamps, and query/run context preserved.
- R14 persistence contracts add `persistence_readback`, persisted lead IDs, protected run-lead readback, tier distribution, and candidate-category distribution.
- R14B/R14C keep the primary operator path free of Scout/Full implementation chrome and audit-first export ordering.
- R14B mobile evidence reports `scrollWidth=390` at `innerWidth=390`, closing the RG4 mobile overflow caveat for the current UI slice.

## What Did Not Work

- This audit could not independently query production Vercel/Fly endpoints.
- This audit could not produce a fresh live Postgres row-count query from a live UI run.
- Fresh local test commands were not reliable in this shell because worker/process startup timed out.
- The R14C browser smoke uses deterministic mocked `/api/scout` rows; it proves the operator path and export mechanics, not live lead quality.

## New Gaps Found

- Add a repeatable RG6/live-ops smoke path that can run production `/health`, `/readiness`, protected login, query, export, and DB readback from an environment with network permission and the needed secrets.
- Preserve a workaround or documented command for local Vitest/pytest timeout conditions if they recur; current logs show process startup timeout, not assertion failure.
- RG6 must separate export/persistence readiness from data-quality readiness so the product does not accidentally move from red to yellow on UI/export evidence alone.

## Recommended Scope Change For Next Gate

Do not expand RG6 into new product implementation.

RG6 should produce the dogfood/kill decision packet using existing functionality and evidence:

- rerun live endpoint and production-smoke checks where network/secrets are available;
- rerun or collect existing benchmark output;
- inspect CSV exports and DB readbacks;
- evaluate red/yellow/green criteria line by line;
- recommend Matt-only yellow evaluation, continued red hold, or pause/concierge fallback.

Any new implementation found necessary during RG6 should be recorded as a follow-up feature only after the decision packet, not shipped opportunistically inside RG6 Prompt C.

## Next Deployment Recommendation

Do not perform a new deployment promotion from this audit branch.

R13-R14C are already merged to `main`. RG5 advancement only unlocks the decision-packet gate; it does not make the product yellow or green, and it does not authorize public SaaS scope, Thomas/Lee dogfood, accounts, billing, or any new deployment beyond the existing operator-use line.

## Next Prompt A Assignment

```text
You are Prompt A for the White Rabbit reset queue.

Work in /Users/mschwar/Documents/white-rabbit. Use main as the integration branch.

First prove current state:
- fetch origin
- read AGENTS.md
- read STATUS.md
- read docs/reset-current-assignment.json
- read docs/00-product-northstar.md
- read docs/12-reset-gated-implementation-plan-2026-05-10.md
- read audits/gates/reset-2026-05-10/rg5-export-persistence.md
- read docs/13-pipeline-orchestrator-contract-2026.md
- run git status --short --branch

Resolve the next feature from STATUS.md and the reset feature table. The expected next feature after RG5 advancement is R15 - Internal correction review and dogfood decision packet.

Implement only R15 on `feat/reset-r15-dogfood-decision-packet`.

Scope:
- compile benchmark results, screenshots, CSV samples, DB readback evidence, correction/review evidence, and operator-minute notes into a dogfood/kill decision packet;
- evaluate the red/yellow/green criteria from `docs/00-product-northstar.md` line by line;
- prove whether Matt-only yellow evaluation, Thomas/Lee dogfood, continued red hold, or pause/manual-concierge fallback is warranted;
- preserve the current internal-only shared-password product boundary.

Non-goals:
- no public SaaS/accounts/orgs/billing;
- no new search/export/persistence/source-assisted compiler implementation unless a small docs-only/reporting change is required for the packet;
- no production promotion beyond evidence gathering unless Matt explicitly authorizes it;
- do not mark yellow or green unless the northstar criteria are actually met.

Required verification:
- run the applicable docs/report checks and any available non-destructive live smoke checks;
- run `git diff --check`;
- if code changes are made, run the relevant web/API/core tests for those touched areas;
- save raw evidence under `audits/raw/reset-2026-05-10/rg6/` or `.gstack/qa-reports/`.

Required outputs:
- R15 decision packet/report;
- updated `STATUS.md`, `docs/12-reset-gated-implementation-plan-2026-05-10.md`, and `docs/reset-current-assignment.json` handoff;
- commit and push the feature branch only. Do not merge; Prompt B must QA it.
```
