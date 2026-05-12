# Reset Gate Review - RG4 Sales-First Operator UI

**Branch:** `audit/reset-rg4-operator-ui`
**Integration branch:** `rebuild/validated-leads-loop`
**Date:** 2026-05-12
**Decision:** advance
**Current product gate:** red

## Evidence Used

- Required control docs: `AGENTS.md`, `STATUS.md`, `docs/00-product-northstar.md`, `docs/12-reset-gated-implementation-plan-2026-05-10.md`, `docs/13-pipeline-orchestrator-contract-2026.md`, and `docs/03-decisions.md`.
- Baseline audit: `audits/zero-trust-codebase-audit-2026-05-10.md`.
- Approved RG4 reference: `DESIGN.md` and `docs/mockups/rg4-refreshed-preflight-2026-05-12/`.
- R10-R12 QA reports: `.gstack/qa-reports/qa-report-r10-primary-search-ui-2026-05-12.md`, `.gstack/qa-reports/qa-report-r11-crm-results-table-2026-05-12.md`, and `.gstack/qa-reports/qa-report-r12-evidence-dossier-review-2026-05-12.md`.
- Prior RG3 source-assisted proof: `audits/gates/reset-2026-05-10/rg3-validation-semantics.md` and `audits/raw/reset-2026-05-10/rg3/post-r09l-source-assisted-proof/source-assisted-proof-live-response.json`.
- Current RG4 raw evidence: `audits/raw/reset-2026-05-10/rg4/`.

## State Proof

| Check | Result | Evidence |
| --- | --- | --- |
| Current in-progress gate | RG4 - Sales-First Operator UI | `docs/12-reset-gated-implementation-plan-2026-05-10.md` |
| Gate not already advanced | No RG4 report existed before this audit; existing reports stopped at RG3 | `audits/raw/reset-2026-05-10/rg4/commands/existing-gate-reports.txt` |
| R10 merged | yes | `audits/raw/reset-2026-05-10/rg4/commands/r10-merge-proof.txt` |
| R11 merged | yes | `audits/raw/reset-2026-05-10/rg4/commands/r11-merge-proof.txt` |
| R12 merged | yes | `audits/raw/reset-2026-05-10/rg4/commands/r12-merge-proof.txt` |
| Branch state | `audit/reset-rg4-operator-ui...origin/rebuild/validated-leads-loop` | `audits/raw/reset-2026-05-10/rg4/commands/git-status-short-branch.txt` |

## Commands Run

```bash
git fetch origin --prune
git switch -c audit/reset-rg4-operator-ui origin/rebuild/validated-leads-loop
git status --short --branch
git merge-base --is-ancestor origin/feat/reset-r10-primary-search-ui origin/rebuild/validated-leads-loop
git merge-base --is-ancestor origin/feat/reset-r11-crm-results-table origin/rebuild/validated-leads-loop
git merge-base --is-ancestor origin/feat/reset-r12-evidence-dossier-review origin/rebuild/validated-leads-loop
find audits/gates/reset-2026-05-10 -maxdepth 1 -type f -print | sort
cd apps/web && npm test -- --run
cd apps/web && npm run build
git diff --check
cd apps/web && WR_SHARED_PASSWORD=codex-test-password WR_SESSION_SECRET=codex-test-session-secret WR_API_INTERNAL_TOKEN=test-internal-token npm run start -- -p 3010
curl -s -D - 'http://127.0.0.1:3010/login?next=/'
curl -s -D - 'http://127.0.0.1:3010/'
cd apps/web && WR_SHARED_PASSWORD=codex-test-password WR_SESSION_SECRET=codex-test-session-secret WR_API_INTERNAL_TOKEN=test-internal-token npm run dev -- -p 3011
WR_BROWSER_BASE_URL=http://localhost:3011 WR_SESSION_SECRET=codex-test-session-secret node audits/raw/reset-2026-05-10/rg4/evidence/browser-audit.mjs
```

Command outputs are saved under `audits/raw/reset-2026-05-10/rg4/commands/`.

## Verification Results

| Check | Result |
| --- | --- |
| Web unit tests | Passed: `13` files, `30` tests |
| Web production build | Passed, with existing workspace-root and `middleware` deprecation warnings |
| Diff hygiene before report/status edits | Passed |
| Production `next start` smoke | Blocked locally: `/` and `/login` returned 404 and server logged `ERR_HTTP_HEADERS_SENT` |
| Dev browser audit | Completed with screenshots and summary JSON |

The `next start` failure is a residual runtime risk. It was not treated as a gate blocker because R10-R12 Prompt B reports recorded production browser passes, the production build passed in this audit, and the independent dev browser run was sufficient to inspect integrated RG4 behavior. Recheck `next start` in R13 Prompt B.

## Browser Findings

Screenshots:

- `audits/raw/reset-2026-05-10/rg4/screenshots/01-primary-empty.png`
- `audits/raw/reset-2026-05-10/rg4/screenshots/02-primary-results.png`
- `audits/raw/reset-2026-05-10/rg4/screenshots/03-evidence-dossier.png`
- `audits/raw/reset-2026-05-10/rg4/screenshots/04-mobile-results.png`
- `audits/raw/reset-2026-05-10/rg4/screenshots/05-mobile-evidence-dossier.png`

Browser audit summary:

| Check | Result |
| --- | --- |
| 51-row mocked result set | passed |
| Target input visible | passed |
| Source-context input absent | intentional per ADR-023 |
| Scout/Full controls hidden | passed |
| Always-visible quota/search-usage chrome hidden | passed |
| Export controls hidden | expected until RG5 |
| Results overview visible | passed |
| READY/REVIEW/ORG-ONLY/NOT FOUND labels visible | passed |
| Evidence dossier visible | passed |
| Source trail visible | passed |
| Mobile evidence visible | passed |

Residual mobile caveat: the 390px run reported `scrollWidth=407` against `clientWidth=390`. The screenshot remained usable, but R13/R14 browser QA should recheck this while adding export/persistence controls.

## Product Scope Clarification

During this audit, Matt clarified that the user-entered source-context field was intentionally removed because it added noise for daily operators. Source context can still exist on the backend/orchestrator side, but it should not be exposed as an extra daily-operator control.

This is recorded in ADR-023. The absence of a source-context input is therefore not a gate blocker.

## Value Prop Verdict

The current product gives enough result volume and evidence value to advance RG4, but it does **not** yet give enough export value for the full operator loop.

Result volume: sufficient for RG4. The browser audit exercised a 51-row categorized result set, which meets the RG4 high-volume UI check. The UI preserved tier distribution, filters, CRM-first fields, and evidence access without collapsing into a noisy dashboard.

Evidence: sufficient for RG4. READY/REVIEW/ORG-ONLY/NOT FOUND remain visible, evidence is one action away, and the dossier shows status, primary blocker, rationale, source trail, checked timestamps, and source links. Uncertain rows are not presented as CRM-ready.

Export: not sufficient yet. That is the reason RG5 exists. The current primary path correctly does not expose final sales-first export/persistence controls, so the next gate must prove export value before dogfood or any `main` promotion.

## Decision

`advance`

RG4 meets its formal advance criteria:

- A reviewer can run query -> inspect rows -> open evidence without seeing Scout/Full implementation modes.
- The UI is materially simpler than the May 10 audit screen and does not hide critical CRM fields.
- It is clear at a glance why most surfaced candidates are READY, REVIEW, ORG-ONLY, or NOT FOUND.

The product remains red because export/persistence is not yet proven.

## Next Main Promotion Recommendation

Do not sync `main`.

RG4 advances only to RG5 on the integration branch. The product remains red, export/persistence is not implemented, dogfood is not approved, and Matt has not explicitly requested another operator-use promotion.

## Next Prompt A Assignment

```text
You are Prompt A for the White Rabbit reset queue.

Work in /Users/mschwar/Documents/white-rabbit. Implement R13 - Sales-first CSV export on feat/reset-r13-sales-first-export. Branch from rebuild/validated-leads-loop and target only rebuild/validated-leads-loop. Do not edit main or the frozen proxy-lead demo.

First prove current state:
- read AGENTS.md
- read STATUS.md
- read docs/00-product-northstar.md
- read docs/12-reset-gated-implementation-plan-2026-05-10.md
- read docs/13-pipeline-orchestrator-contract-2026.md
- read audits/gates/reset-2026-05-10/rg4-operator-ui.md
- run git status --short --branch

Scope:
- Add sales-first CSV export to the primary operator path after rows exist.
- Usable/READY rows must sort first by default.
- CRM-facing columns must come before audit/run metadata.
- Validation context, tier, primary_filter_reason, source URLs, checked timestamps, and evidence status must remain in the export.
- Include all tiers by default only if uncertain rows remain clearly marked and cannot masquerade as CRM-ready.
- Preserve the one-target-input daily operator UI from ADR-023; do not add a user-facing source-context field.

Non-goals:
- No persistence/DB readback work; that is R14.
- No backend/core/search/tiering changes unless strictly required to export fields already returned by the current API.
- No dogfood packet, correction workflow expansion, recipes, batch, scoreboards, or main promotion.

Required verification:
- cd apps/web && npm test -- --run
- cd apps/web && npm run build
- browser QA on desktop and mobile proving query -> results -> export download/CSV content
- inspect the first 5 CSV lines and save them as raw evidence
- git diff --check

Required outputs:
- implementation changes for R13 only
- raw export/browser evidence under audits/raw/reset-2026-05-10/r13/
- STATUS.md and docs/12 handoff updates for Prompt B

Do not merge. Do not unlock R14/RG6/main. Commit the feature branch when complete.
```
