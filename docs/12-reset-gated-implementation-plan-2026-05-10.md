# 12 - Reset Gated Implementation Plan

**Status:** Active control document for the May 10 product reset.
**Created:** 2026-05-10.
**Integration branch:** `rebuild/validated-leads-loop`.
**Current product gate:** Red.
**Current reset gate:** RG0 - W5 hold and reset control.
**Next Prompt A feature:** `R00 - W5 hold report and reset control docs`.

This document converts the May 10 zero-trust audit into an implementation queue. It overlays `docs/08-agentic-buildout-plan.md` and `docs/09-rebuild-phase-gates.md` until the reset either reaches yellow or is killed. The old F00-F23 history remains useful context, but new implementation work should use the reset feature table below.

## Non-Negotiable Rule

Every reset gate requires a full evaluation and audit before the next gate unlocks.

Feature completion is not enough. Test pass is not enough. Browser render is not enough. Each gate must prove the operator loop with repo-backed evidence:

```text
operator prompt
-> target/account coverage
-> enough categorized results to create sales value
-> field-validated rows
-> evidence review
-> sales-first export
```

Gate reviewers must assume the app, docs, test fixtures, and prior gate claims are untrusted until they are proven against live code, saved artifacts, and the Thomas/Lee evidence set.

## Operator Volume Requirement

Lee and Thomas reported on 2026-05-10 that current Scout/Full output is not useful when Scout returns 3 rows and Full returns 4 rows. For broad targets, White Rabbit must return more than 10 categorized results and should aim for 10-25 results. Quality still wins over filler, but "few clean rows" is not enough product value for the operator workflow.

This requirement applies to:

- benchmark fixtures and live benchmark summaries,
- search coverage planning,
- UI result review,
- CSV export ordering and row counts,
- every reset gate decision from RG1 onward.

Narrow named-account prompts may produce fewer person leads only when every requested account is represented as `person_lead`, `organization_only`, `not_found`, or `failed`. Broad vertical/persona prompts that return fewer than 10 categorized results must be marked `hold` unless the gate report proves the market itself is smaller.

## Branch Workflow

Do not touch `main`.

All reset work branches from and returns to:

```text
rebuild/validated-leads-loop
```

Feature branch pattern:

```text
feat/reset-rNN-short-name
```

Gate review branch pattern:

```text
audit/reset-rgN-short-name
```

Prompt A implements exactly one `ready` reset feature. Prompt B QA's and merges that feature into `rebuild/validated-leads-loop`. A gate-review prompt then runs the full evaluation/audit for that gate. The next gate unlocks only when the gate report records `advance` and `STATUS.md` is updated.

## Prompt A - Build Next Reset Feature

```text
You are working in /Users/mschwar/Documents/white-rabbit.

Work only on rebuild/validated-leads-loop. Do not touch main.

1. Read AGENTS.md, STATUS.md, docs/00-product-northstar.md, docs/12-reset-gated-implementation-plan-2026-05-10.md, docs/03-decisions.md, and docs/02-stack.md.
2. Checkout rebuild/validated-leads-loop and pull latest with fast-forward only.
3. Pick the next reset feature whose status is ready in docs/12-reset-gated-implementation-plan-2026-05-10.md.
4. Create its feature branch from rebuild/validated-leads-loop using the branch name in the feature card.
5. Implement only that feature. No opportunistic refactors. No adjacent reset features.
6. Run the feature's required verification.
7. Update docs/12-reset-gated-implementation-plan-2026-05-10.md and STATUS.md with status, tests, and next handoff.
8. Commit atomically with a conventional commit message.
9. Push the feature branch.
10. Do not merge. Do not target main.

Return:
- reset feature ID/name
- branch
- commits
- tests run
- files changed
- current status
- exact QA instructions for Prompt B
```

## Prompt B - QA And Merge Reset Feature

```text
You are working in /Users/mschwar/Documents/white-rabbit.

QA the current reset feature branch and merge only into rebuild/validated-leads-loop. Never merge to main.

1. Read AGENTS.md, STATUS.md, docs/00-product-northstar.md, docs/12-reset-gated-implementation-plan-2026-05-10.md, and the feature card being QA'd.
2. Checkout the feature branch and pull latest.
3. Run the required tests.
4. If UI-visible, run browser QA, save screenshots under .gstack/qa-reports/screenshots/.
5. If non-UI, run the explicit verification from the feature card and capture output.
6. Check for northstar drift and overbuild. Fix only in-scope issues or mark QA failed.
7. Write a QA report under .gstack/qa-reports/.
8. Update docs/12-reset-gated-implementation-plan-2026-05-10.md and STATUS.md.
9. Commit QA/docs/fixes atomically.
10. Push the feature branch.
11. Merge into rebuild/validated-leads-loop only.
12. Push rebuild/validated-leads-loop.
13. Do not open or target main.

Return:
- QA verdict
- report/screenshots path
- tests run
- commits
- merge target confirmation
- whether the current reset gate is ready for full evaluation/audit
```

## Gate Evaluation / Audit Prompt

Run this after all features in a reset gate have merged.

```text
You are working in /Users/mschwar/Documents/white-rabbit.

Run a full zero-trust evaluation and audit for the current reset gate. This is review/report work unless the gate doc explicitly requires a small docs/status update. Do not edit product code.

1. Read AGENTS.md, STATUS.md, docs/00-product-northstar.md, docs/12-reset-gated-implementation-plan-2026-05-10.md, audits/zero-trust-codebase-audit-2026-05-10.md, and the relevant reset feature QA reports.
2. Checkout rebuild/validated-leads-loop and pull latest.
3. Create an audit branch using audit/reset-rgN-short-name.
4. Run every required gate command and browser/live check listed in the gate card.
5. Use the true north-star evidence set: Monroe 7/8, Thomas Gmail thread IDs, Lee Gmail thread IDs, saved workbook/PDF artifacts where available, v1 proxy-lead read-only reference, current code, current UI, and current live outputs.
6. Save raw outputs under audits/raw/reset-2026-05-10/rgN/.
7. Write the gate report under audits/gates/reset-2026-05-10/rgN-short-name.md.
8. The gate report must include: Decision, Evidence Used, Commands Run, Live Results, Screenshots/Artifacts, Findings, What Worked, What Did Not Work, New Gaps Found, Recommended Scope Change For Next Gate.
9. Update docs/12-reset-gated-implementation-plan-2026-05-10.md and STATUS.md only if the gate decision is clear.
10. Commit and push the audit branch.

Return:
- gate decision: advance / hold / revise / rollback / kill
- report path
- raw artifact path
- exact next Prompt A assignment if advance
```

## Gate Decision Semantics

| Decision | Meaning |
| --- | --- |
| `advance` | Gate evidence meets criteria; unlock the next gate's first feature. |
| `hold` | Current gate needs remediation; do not unlock downstream work. |
| `revise` | Sequencing or scope is wrong; update the plan before more implementation. |
| `rollback` | A merged feature damaged the reset goal; revert or repair before continuing. |
| `kill` | Evidence says v2 should pause; continue concierge/manual fulfillment outside this app path. |

## Evidence Set

Each gate evaluation must cite which evidence it used.

Required baseline evidence:

- `audits/zero-trust-codebase-audit-2026-05-10.md`
- `audits/raw/zero-trust-2026-05-10/evidence-ledger.md`
- `audits/raw/zero-trust-2026-05-10/operator-feedback-volume-2026-05-10.md`
- `audits/raw/zero-trust-2026-05-10/live/`
- `audits/raw/zero-trust-2026-05-10/screenshots/`
- `docs/00-product-northstar.md`
- `/Users/mschwar/Documents/proxy-lead` as read-only v1 reference
- Monroe 7/8 transcripts and summaries
- Gmail message IDs recorded in the May 10 evidence ledger

Privacy rule: summarize private emails/messages. Do not dump unnecessary private content into repo artifacts.

Spend rule: live verification stays under `$5` unless Matt explicitly raises the cap.

## Reset Gate Overview

| Gate | Name | Feature range | Status | Required report |
| --- | --- | --- | --- | --- |
| RG0 | W5 Hold And Control Reset | R00 | ready | `audits/gates/reset-2026-05-10/rg0-w5-hold.md` |
| RG1 | Operator Benchmark Harness | R01-R03 | blocked | `audits/gates/reset-2026-05-10/rg1-benchmark-harness.md` |
| RG2 | Search Coverage And Source Collection | R04-R06 | blocked | `audits/gates/reset-2026-05-10/rg2-search-source-coverage.md` |
| RG3 | Validation, Conflict, And Gate Semantics | R07-R09 | blocked | `audits/gates/reset-2026-05-10/rg3-validation-semantics.md` |
| RG4 | Sales-First Operator UI | R10-R12 | blocked | `audits/gates/reset-2026-05-10/rg4-operator-ui.md` |
| RG5 | Sales-First Export And Persistence | R13-R14 | blocked | `audits/gates/reset-2026-05-10/rg5-export-persistence.md` |
| RG6 | Dogfood / Kill Decision | R15 | blocked | `audits/gates/reset-2026-05-10/rg6-dogfood-decision.md` |

## Reset Feature Table

| ID | Feature | Status | Branch | Verification |
| --- | --- | --- | --- | --- |
| R00 | W5 hold report and reset control docs | ready | `feat/reset-r00-w5-hold-control` | non-UI docs + gate evidence |
| R01 | Operator evidence fixture pack | blocked | `feat/reset-r01-operator-evidence-fixtures` | non-UI fixture audit |
| R02 | Golden benchmark replay harness | blocked | `feat/reset-r02-benchmark-replay-harness` | core tests |
| R03 | Live benchmark runner and quality summary | blocked | `feat/reset-r03-live-benchmark-runner` | core/API + saved raw outputs |
| R04 | Target-account coverage planner | blocked | `feat/reset-r04-target-account-coverage` | core tests |
| R05 | Source collection and snapshot store | blocked | `feat/reset-r05-source-collection-store` | core tests + raw source fixtures |
| R06 | Not-found and organization-only coverage writer | blocked | `feat/reset-r06-nonperson-coverage` | core tests |
| R07 | Candidate parse salvage and failed-row recovery | blocked | `feat/reset-r07-parse-salvage` | core/API tests |
| R08 | Field validator and duplicate/conflict resolver | blocked | `feat/reset-r08-validation-conflicts` | core tests |
| R09 | Score semantics and gate language reset | blocked | `feat/reset-r09-score-semantics` | core + web tests |
| R10 | Primary search workspace simplification | blocked | `feat/reset-r10-primary-search-ui` | browser |
| R11 | Compact CRM-first results table | blocked | `feat/reset-r11-crm-results-table` | browser |
| R12 | Evidence dossier review mode | blocked | `feat/reset-r12-evidence-dossier-review` | browser |
| R13 | Sales-first CSV export | blocked | `feat/reset-r13-sales-first-export` | browser + CSV |
| R14 | Persistence, DB readback, and quality report tie-out | blocked | `feat/reset-r14-persistence-quality-tieout` | API + DB |
| R15 | Internal correction review and dogfood decision packet | blocked | `feat/reset-r15-dogfood-decision-packet` | browser + docs |

## RG0 - W5 Hold And Control Reset

Features:

- R00 - W5 hold report and reset control docs.

Goal:
Stop the current rebuild line from treating F13-F19 as proof that the operator loop works.

R00 scope:

- Create `.gstack/qa-reports/gate-w5-operator-loop-export.md` with decision `hold`.
- Cite the May 10 audit, live benchmark JSON, screenshots, and Full-mode CSV sample.
- Update `docs/08-agentic-buildout-plan.md` so future agents defer active reset work to this plan.
- Update `STATUS.md` so W6 is blocked and R01 remains blocked until RG0 audit advances.
- Do not edit product code.

Required R00 verification:

```bash
git diff --check
rg -n "RG0|R00|W5 hold|reset-gated|gate-w5-operator-loop-export" docs STATUS.md .gstack/qa-reports
```

RG0 full evaluation/audit:

- Confirm W5 report exists and decision is `hold`.
- Confirm W6/deferred work is blocked in `STATUS.md`.
- Confirm `docs/08-agentic-buildout-plan.md` points to this reset plan.
- Confirm no product code changed.
- Re-read May 10 live evidence and summarize why W5 cannot advance.

Advance criteria:

- The repo has a clear active reset plan.
- The first implementation gate is blocked from accidental downstream work.
- R01 is ready only after the gate audit records `advance`.

## RG1 - Operator Benchmark Harness

Features:

- R01 - Operator evidence fixture pack.
- R02 - Golden benchmark replay harness.
- R03 - Live benchmark runner and quality summary.

Goal:
Make Thomas/Lee prompts executable as evidence, not anecdotes.

Implementation requirements:

- Preserve source IDs and private-evidence summaries without dumping private content.
- Add replay fixtures for Thomas Arizona K-12, Lee commodity buyers, healthcare IT Phoenix, finance CISOs New York, manufacturing ops Detroit, and B2C/private refusal.
- Benchmark output must classify every expected target as `person_lead`, `organization_only`, `not_found`, or `failed`.
- Broad benchmark output must track categorized row count, person-lead count, usable-row count, and whether the run met the 10-25 target range.
- Live runner must save JSON, HTTP status, elapsed time, estimated cost, and quality summary.

Required feature verification:

```bash
cd packages/core && uv run pytest tests/test_arizona_k12_benchmark.py tests/test_benchmark_suite.py tests/test_quality_report.py -q
git diff --check
```

RG1 full evaluation/audit:

- Run replay benchmarks.
- Run live benchmarks if local keys/services are available and spend cap allows.
- Confirm Thomas prompt covers all 8 target accounts.
- Confirm broad Lee/Thomas-style prompts do not pass the gate with only 3-4 returned rows.
- Confirm manufacturing role-as-name is represented as failed, not a 503.
- Confirm B2C/private query blocks before search.
- Save raw outputs under `audits/raw/reset-2026-05-10/rg1/`.

Advance criteria:

- Harness can fail bad output.
- Benchmarks are reproducible without live keys.
- Live path is documented when keys are available.

## RG2 - Search Coverage And Source Collection

Features:

- R04 - Target-account coverage planner.
- R05 - Source collection and snapshot store.
- R06 - Not-found and organization-only coverage writer.

Goal:
Stop dropping named accounts and stop forcing unknown targets into person rows.

Implementation requirements:

- Named-account prompts preserve each account as a coverage obligation.
- Simple vertical prompts still produce enough bounded vendor queries to support 10-25 categorized results where the market supports it.
- Source collection stores enough evidence for replay and audit.
- Missing or personless targets become explicit `not_found` or `organization_only` rows.

Required feature verification:

```bash
cd packages/core && uv run pytest tests/test_query_planner.py tests/test_search.py tests/test_benchmark_suite.py -q
git diff --check
```

RG2 full evaluation/audit:

- Re-run Thomas Arizona prompt and verify 8 account coverage.
- Re-run broad Scout/Full benchmark prompts and verify the planner does not artificially starve result volume below 10.
- Inspect raw collected sources for at least 3 target accounts.
- Confirm no vendor query exceeds Tavily's limit.
- Confirm adjacent/filler accounts are flagged or excluded.

Advance criteria:

- All Thomas target accounts appear in output categories.
- Source artifacts are sufficient for a reviewer to reproduce why each target passed, failed, or was not found.

## RG3 - Validation, Conflict, And Gate Semantics

Features:

- R07 - Candidate parse salvage and failed-row recovery.
- R08 - Field validator and duplicate/conflict resolver.
- R09 - Score semantics and gate language reset.

Goal:
Make false confidence hard to display.

Implementation requirements:

- One invalid LLM candidate cannot crash the whole query.
- Conflicting person/organization claims are flagged.
- Contact status cannot be verified from inaccessible or unsupported sources.
- Fit/Evidence/Contact language is hidden, renamed, or recalibrated so non-usable rows do not look strong.

Required feature verification:

```bash
cd packages/core && uv run pytest tests/test_source_validation.py tests/test_contact_status.py tests/test_scoring.py tests/test_orchestrator.py -q
cd apps/api && WR_API_INTERNAL_TOKEN=test-internal-token uv run pytest tests -q
git diff --check
```

RG3 full evaluation/audit:

- Re-run manufacturing benchmark and confirm no 503 parse crash.
- Sample 10 returned person rows across benchmarks and inspect validation field support.
- Confirm duplicate/conflict cases fail or are downgraded.
- Confirm no row with missing/unsupported contact is labeled CRM-ready.

Advance criteria:

- Bad candidates degrade into explicit failed/noisy rows.
- Gate language and UI score semantics no longer create false confidence.

## RG4 - Sales-First Operator UI

Features:

- R10 - Primary search workspace simplification.
- R11 - Compact CRM-first results table.
- R12 - Evidence dossier review mode.

Goal:
Restore the calm v1 operator shape without restoring v1 implementation.

Implementation requirements:

- Primary screen is one search input and one command.
- No Scout/Full toggle in the operator path.
- No quota card unless near cap or blocked.
- Results review comfortably handles 10-25 categorized rows without turning into a noisy dashboard.
- Results table starts with organization, location, lead name, title, email, phone, source, and why target.
- Evidence/dossier panel is available without burying CRM fields.
- Feedback/correction controls move behind review mode.

Required feature verification:

```bash
cd apps/web && npm test -- --run
cd apps/web && npm run build
git diff --check
```

RG4 full evaluation/audit:

- Browser QA on desktop and mobile.
- Screenshot empty, loading, results, evidence dossier, and blocked query states.
- Verify the results page remains usable with 10-25 categorized rows.
- Compare against v1 proxy-lead reference read-only.
- Check current UI against Lee/Thomas workflow notes.

Advance criteria:

- A reviewer can run query -> inspect rows -> open evidence without seeing implementation modes.
- UI is simpler than the May 10 screenshots and does not hide critical CRM fields.

## RG5 - Sales-First Export And Persistence

Features:

- R13 - Sales-first CSV export.
- R14 - Persistence, DB readback, and quality report tie-out.

Goal:
Make export a sales artifact first and audit artifact second.

Implementation requirements:

- Export is available from the primary operator path after rows exist.
- Usable rows sort first by default.
- CRM-facing columns come before audit/run metadata.
- Validation context remains in the export.
- DB readback matches UI rows and CSV rows.

Required feature verification:

```bash
cd apps/web && npm test -- --run
cd apps/web && npm run build
cd apps/api && WR_API_INTERNAL_TOKEN=test-internal-token uv run pytest tests -q
git diff --check
```

RG5 full evaluation/audit:

- Run Full/persisted query path through the UI.
- Download CSV and inspect first 5 lines.
- Query Postgres for run and lead rows.
- Confirm row counts match UI, CSV, and DB.
- Confirm broad benchmark exports do not contain only 3-4 rows unless the gate report proves the market is smaller.
- Confirm first 10 CSV columns are sales-useful without audit metadata.

Advance criteria:

- Export can be handed to Thomas/Lee without explaining validation internals first.
- Uncertain rows remain clearly marked and cannot masquerade as CRM-ready.

## RG6 - Dogfood / Kill Decision

Features:

- R15 - Internal correction review and dogfood decision packet.

Goal:
Decide whether White Rabbit v2 earns Matt-only yellow evaluation, Thomas/Lee dogfood, or a pause.

Implementation requirements:

- Compile benchmark results, screenshots, CSV samples, DB readbacks, correction review output, and operator-minute notes into a decision packet.
- Do not mark yellow/green unless `docs/00-product-northstar.md` criteria are met.
- If criteria are not met, recommend kill/hold/manual concierge path.

Required feature verification:

```bash
cd packages/core && uv run pytest -q
cd apps/api && WR_API_INTERNAL_TOKEN=test-internal-token uv run pytest tests -q
cd apps/web && npm test -- --run
cd apps/web && npm run build
git diff --check
```

RG6 full evaluation/audit:

- Re-run the full live benchmark suite if services/keys are available.
- Re-run browser query-to-export on desktop and mobile.
- Inspect generated CSV and DB readback.
- Confirm broad Thomas/Lee-style prompts consistently return 10-25 categorized results, not 3-4 row trickles.
- Evaluate red/yellow/green criteria line by line.
- Write final decision report.

Advance criteria:

- Yellow only if Matt can evaluate with benchmark evidence and sales-first export.
- Green only if Thomas/Lee can dogfood without re-researching most rows.
- Otherwise hold or kill.

## Status Rules

Use these statuses only:

- `blocked`
- `ready`
- `in_progress`
- `implemented_pending_qa`
- `qa_failed`
- `merged_to_rebuild_branch`
- `gate_pending_audit`
- `gate_hold`
- `gate_advanced`
- `deferred`
- `killed`

## Gate Report Required Sections

Every gate report must include:

```markdown
# Reset Gate Review - RGN Name

**Branch:**
**Integration branch:** rebuild/validated-leads-loop
**Date:**
**Decision:** advance / hold / revise / rollback / kill
**Current product gate:** red / yellow / green

## Evidence Used
## Commands Run
## Live Results
## Screenshots And Artifacts
## Findings
## What Worked
## What Did Not Work
## New Gaps Found
## Recommended Scope Change For Next Gate
## Next Prompt A Assignment
```

## First Prompt A Assignment

Assign the first implementation agent:

```text
You are Prompt A for White Rabbit reset feature R00.

Work in /Users/mschwar/Documents/white-rabbit on rebuild/validated-leads-loop only. Do not touch main.

Read AGENTS.md, STATUS.md, docs/00-product-northstar.md, docs/12-reset-gated-implementation-plan-2026-05-10.md, docs/03-decisions.md, and audits/zero-trust-codebase-audit-2026-05-10.md.

Implement only R00 - W5 hold report and reset control docs on branch feat/reset-r00-w5-hold-control.

Required output:
- .gstack/qa-reports/gate-w5-operator-loop-export.md with decision hold
- report cites 2026-05-10 Lee/Thomas feedback: Scout returned 3 rows, Full returned 4 rows, and the operator target is more than 10 results with 10-25 preferred
- docs/08-agentic-buildout-plan.md pointer to docs/12 as active reset queue
- STATUS.md updated to show W5 held, W6 blocked, and RG0 pending audit
- git diff --check passing
- rg verification from the R00 card

Commit and push the feature branch. Do not merge.
```
