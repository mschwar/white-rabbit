# 12 - Reset Gated Implementation Plan

**Status:** Active control document for the May 10 product reset.
**Created:** 2026-05-10.
**Integration branch:** `rebuild/validated-leads-loop`.
**Operator-use branch:** `main`, explicitly promoted from `rebuild/validated-leads-loop` by ADR-010 for Thomas/Lee internal use.
**Current product gate:** Red.
**Current reset gate:** RG2 - Search Coverage And Source Collection, ready for Prompt C audit after the R06 merge to `rebuild/validated-leads-loop`.
**Next Prompt A feature:** None. R06 passed Prompt B QA; RG3 remains blocked.
**Current Prompt B handoff:** None. R06 passed Prompt B QA on `feat/reset-r06-nonperson-coverage`; after merge to `rebuild/validated-leads-loop`, run Prompt C for RG2 and do not unlock RG3 unless the gate audit records and merges an accepted advance decision.

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

## 24-Hour Product Bar

The next 24 hours are not for building a cleaner-looking version of the same failed product. The only value proposition that matters is:

```text
Thomas or Lee enters a real sales target
-> White Rabbit surfaces the realistic public-web candidate universe
-> every row is categorized honestly
-> source evidence explains why the row is safe or unsafe
-> the useful rows export in a sales-first format
```

Hard fail conditions:

- broad Scout/Full prompts return fewer than 50 categorized candidates after high-volume mode lands, or fewer than 10 before it lands, without proving the market is smaller,
- person rows cannot show source-supported name, title, organization, and contact status,
- the UI or export makes noisy/failed rows look CRM-ready,
- an agent advances a gate from tests, mocks, screenshots, or docs without current live/replay evidence tied to operator prompts.

Do not start UI simplification, export polish, correction review, recipe, batch, scoreboard, or dogfood work until Prompt C has advanced the preceding data-quality gates. If a feature does not move the product toward result volume, provenance, validation honesty, or sales-first export, it is out of scope for this reset.

## High-Volume Transparency Requirement

Lee and Thomas reported on 2026-05-10 that current Scout/Full output is not useful when Scout returns 3 rows and Full returns 4 rows. ADR-011 set 10-25 categorized rows as the first escape from that failure. ADR-013 supersedes that as the live-demo and pipeline target: for broad vertical + geography prompts, White Rabbit should surface 50-500+ categorized candidates where the market supports it.

High volume is acceptable only because the product must make the distribution instantly understandable:

- `high_trust_usable` rows remain strict and high precision.
- `review` rows are plausible but limited.
- `organization_only`, `not_found`, and `failed` rows explain the blocker instead of disappearing.
- Every row gets a grounded `primary_filter_reason`.
- The operator can answer in seconds: how many real decision-makers are findable, and what blocks the rest?

This requirement applies to:

- benchmark fixtures and live benchmark summaries,
- search coverage planning,
- UI result review,
- CSV export ordering and row counts,
- every reset gate decision from RG1 onward.

Narrow named-account prompts may produce fewer person leads only when every requested account is represented as `high_trust_usable`, `review`, `organization_only`, `not_found`, or `failed`. Broad vertical/persona prompts that return fewer than 50 categorized candidates after the high-volume path lands must be marked `hold` unless the gate report proves the market itself is smaller.

## Branch Workflow

Do not merge feature branches directly to `main`.

All reset work branches from and returns to:

```text
rebuild/validated-leads-loop
```

`main` is the operator-use deployment line because Thomas and Lee asked to use the most recent internal version. A push to `main` is an explicit operator-use promotion from `rebuild/validated-leads-loop`; it is not evidence that a reset gate passed or that the product is yellow/green. Keep feature QA and gate advancement on `rebuild/validated-leads-loop`, then sync `main` only when Matt or the active gate plan explicitly asks for that promotion.

Feature branch pattern:

```text
feat/reset-rNN-short-name
```

Gate review branch pattern:

```text
audit/reset-rgN-short-name
```

## Kickoff Workflow - Only Prompt A, Prompt B, Prompt C

Use only this loop:

```text
Prompt A: implement exactly one ready reset feature on a feature branch
Prompt B: QA that feature, write the QA report, and merge only to rebuild/validated-leads-loop
Prompt C: run the gate evaluation/audit after every feature in that gate has merged
```

Prompt A never merges. Prompt B never unlocks the next gate. Prompt B may unlock the next feature inside the same in-progress gate after QA passes and the prior feature is merged. Prompt C is the only prompt that can record a gate-level `advance` or recommend an operator-use sync to `main`. A Prompt C `advance` is not active for the next Prompt A until the audit branch has been merged back into `rebuild/validated-leads-loop` and pushed.

Current kickoff order is resolved dynamically from `STATUS.md` and the reset feature/gate tables below.

Do not use a hard-coded feature prompt from an earlier chat turn. Before every assignment, the agent must prove the current state from the repo:

```text
1. Prompt A -> the single feature currently marked ready
2. Prompt B -> the single feature branch currently waiting for QA
3. If the current gate has another feature -> Prompt A on that next same-gate feature
4. If all features in the current gate are merged -> Prompt C on the current gate
5. If and only if Prompt C records advance and merges the audit branch to the integration branch -> the next gate's first feature becomes ready
```

If Prompt C records `hold`, `revise`, `rollback`, or `kill`, no downstream Prompt A assignment is valid until that decision is resolved.

If there are zero ready features, multiple ready features, a dirty working tree on the integration branch, or an already-started feature branch for the same feature, the agent must stop and report the ambiguity instead of starting duplicate work. Ignored local editor files such as `.obsidian/` do not count as dirty state.

## Final Product Mockup Inspection Gate

Before reset UI/export implementation starts, Matt must inspect the final product mockup artifact:

- Mockup: `docs/mockups/final-product-2026-05-10/index.html`
- Rendered screenshots: `.gstack/qa-reports/screenshots/final-product-mockups-2026-05-10/`

This mockup is not production code. It is the visual contract for R10-R13: one search input, high-volume tier distribution, CRM-first fields, evidence one action away, sales-first export, and no Scout/Full/product-internals ceremony in the operator path.

Prompt A/B agents must not invent a different final UI direction during R10-R13 without a fresh Matt approval. Prompt C for RG4 and RG5 must compare browser screenshots against this mockup and explicitly record any intentional divergence. Live-demo UI copy must not mention internal people, agent prompts, gates, sprint labels, or implementation machinery.

## Copy-Paste Prompt Authority

The only active Prompt A/B/C text is in the reusable copy-paste section below. Do not copy older chat prompts or historical F00-F23 prompt blocks.

## Live-Evidence Rule

RG0 may advance on repo evidence because it is a control-plane hold gate. RG1 may advance on replay evidence only if the live runner is created and the report documents exactly why live runs were or were not executed.

From RG2 onward, no product gate may advance without current live evidence under the `$5` cap. If API keys, services, auth, or deployment are unavailable, Prompt C must record `hold` with the exact blocker instead of advancing from mocks, fixtures, screenshots, or intentions.

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
| RG0 | W5 Hold And Control Reset | R00 | gate_advanced | `audits/gates/reset-2026-05-10/rg0-w5-hold.md` |
| RG1 | Operator Benchmark Harness | R01-R03 | gate_advanced | `audits/gates/reset-2026-05-10/rg1-benchmark-harness.md` |
| RG2 | Search Coverage And Source Collection | R04-R06 | ready_for_prompt_c_audit | `audits/gates/reset-2026-05-10/rg2-search-source-coverage.md` |
| RG3 | Validation, Conflict, And Gate Semantics | R07-R09 | blocked | `audits/gates/reset-2026-05-10/rg3-validation-semantics.md` |
| RG4 | Sales-First Operator UI | R10-R12 | blocked | `audits/gates/reset-2026-05-10/rg4-operator-ui.md` |
| RG5 | Sales-First Export And Persistence | R13-R14 | blocked | `audits/gates/reset-2026-05-10/rg5-export-persistence.md` |
| RG6 | Dogfood / Kill Decision | R15 | blocked | `audits/gates/reset-2026-05-10/rg6-dogfood-decision.md` |

## Reset Feature Table

| ID | Feature | Status | Branch | Verification |
| --- | --- | --- | --- | --- |
| R00 | W5 hold report and reset control docs | merged | `feat/reset-r00-w5-hold-control` | non-UI docs + gate evidence |
| R01 | Operator evidence fixture pack | merged | `feat/reset-r01-operator-evidence-fixtures` | non-UI fixture audit |
| R02 | Golden benchmark replay harness | merged | `feat/reset-r02-benchmark-replay-harness` | core tests |
| R03 | Live benchmark runner and quality summary | merged_to_rebuild_branch | `feat/reset-r03-live-benchmark-runner` | core/API + saved raw outputs |
| R04 | High-volume query planner and search aggregation | merged_to_rebuild_branch | `feat/reset-r04-high-volume-search` | core tests |
| R05 | Source collection and snapshot store | merged_to_rebuild_branch | `feat/reset-r05-source-collection-store` | core tests + raw source fixtures |
| R06 | Not-found and organization-only coverage writer | qa_passed_pending_merge | `feat/reset-r06-nonperson-coverage` | core tests |
| R07 | Inclusive extraction prompt and candidate parse salvage | blocked | `feat/reset-r07-inclusive-extraction` | core/API tests |
| R08 | Tiering engine, field validator, and conflict resolver | blocked | `feat/reset-r08-tier-validation-conflicts` | core tests |
| R09 | Tier summary, score semantics, and reason language reset | blocked | `feat/reset-r09-tier-summary-semantics` | core + web tests |
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
- Benchmark output must classify every expected target into `high_trust_usable`, `review`, `organization_only`, `not_found`, or `failed`, while preserving candidate category where needed.
- Broad benchmark output must track total categorized candidate count, tier distribution, person-lead count, high-trust usable count, review count, and whether the run met the high-volume floor.
- Live runner must save JSON, HTTP status, elapsed time, estimated cost, and quality summary.

Required feature verification:

```bash
cd packages/core && uv run pytest tests/test_arizona_k12_benchmark.py tests/test_benchmark_suite.py tests/test_quality_report.py -q
git diff --check
```

RG1 full evaluation/audit:

- Run replay benchmarks.
- Run live benchmarks if local keys/services are available and spend cap allows.
- If live benchmarks are not run, record the exact blocker and do not unlock RG2 unless the live runner itself is proven executable once credentials/services are restored.
- Confirm Thomas prompt covers all 8 target accounts.
- Confirm broad Lee/Thomas-style prompts do not pass the gate with only 3-4 returned rows and are ready to measure high-volume tier distribution.
- Confirm manufacturing role-as-name is represented as failed, not a 503.
- Confirm B2C/private query blocks before search.
- Save raw outputs under `audits/raw/reset-2026-05-10/rg1/`.

Advance criteria:

- Harness can fail bad output.
- Benchmarks are reproducible without live keys.
- Live runner is executable, or the only blocker is documented environment/service access outside product code.
- Prompt C can identify which exact broad prompts will be used to prove RG2 result volume.

## RG2 - Search Coverage And Source Collection

Features:

- R04 - Target-account coverage planner.
- R05 - Source collection and snapshot store.
- R06 - Not-found and organization-only coverage writer.

Goal:
Increase raw search/source coverage without turning unsupported candidates into false confidence.

Implementation requirements:

- Follow `docs/Orchestrator_Agent_Implementation_Brief.md`.
- Named-account prompts preserve each account as a coverage obligation.
- Simple vertical prompts produce enough bounded vendor queries and client-side aggregation to support 50-500+ categorized candidates where the market supports it.
- `scout()` exposes safe volume controls such as `max_results` and optional `aggressive_breadth`.
- Tavily's per-call cap is handled with multi-query planning, aggregation, and deduplication.
- Role synonyms and light geographic/vertical expansion are used only when the query is broad.
- Source collection stores enough evidence for replay and audit.
- Missing or personless targets become explicit `not_found` or `organization_only` rows.

Required feature verification:

```bash
cd packages/core && uv run pytest tests/test_query_planner.py tests/test_search.py tests/test_benchmark_suite.py -q
git diff --check
```

RG2 full evaluation/audit:

- Re-run Thomas Arizona prompt and verify 8 account coverage.
- Re-run broad Scout/Full benchmark prompts and verify the planner does not artificially starve raw source volume.
- Inspect raw collected sources for at least 3 target accounts.
- Confirm no vendor query exceeds Tavily's limit.
- Confirm adjacent/filler accounts are flagged or excluded.

Advance criteria:

- All Thomas target accounts appear in output categories.
- Source artifacts are sufficient for a reviewer to reproduce why each target passed, failed, or was not found.
- Broad prompts produce enough unique raw hits to support high-volume tiering, or the report proves the public web/source universe is smaller.

## RG3 - Validation, Conflict, And Gate Semantics

Features:

- R07 - Inclusive extraction prompt and candidate parse salvage.
- R08 - Tiering engine, field validator, and conflict resolver.
- R09 - Tier summary, score semantics, and reason language reset.

Goal:
Make false confidence hard to display.

Implementation requirements:

- One invalid LLM candidate cannot crash the whole query.
- LLM extraction is inclusive; it does not pre-filter plausible candidates simply because evidence is incomplete.
- The old evidence gate remains the definition of `high_trust_usable`, not the only return path.
- Every candidate receives `tier`, `primary_filter_reason`, and detailed grounded reasons where available.
- Conflicting person/organization claims are flagged.
- Contact status cannot be verified from inaccessible or unsupported sources.
- Fit/Evidence/Contact language is hidden, renamed, or recalibrated so non-usable rows do not look strong.
- Run metrics or response metadata expose tier distribution.

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
- High-trust usable precision is preserved while review/org-only/not-found/failed candidates remain visible and explained.

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
- Results review comfortably handles 50-500+ categorized candidates through tier distribution, filtering, and dense CRM-first review without turning into a noisy dashboard.
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
- Verify the results page remains usable with high-volume tier distribution and at least a 50+ row fixture or live run.
- Compare against v1 proxy-lead reference read-only.
- Check current UI against Lee/Thomas workflow notes.

Advance criteria:

- A reviewer can run query -> inspect rows -> open evidence without seeing implementation modes.
- UI is simpler than the May 10 screenshots and does not hide critical CRM fields.
- It is clear at a glance why most surfaced candidates are not immediately actionable.

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
- Export can include all tiers while sorting high-trust usable rows first and keeping non-actionable reasons visible.

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
- Confirm high-volume exports preserve tier and `primary_filter_reason`.
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
- Confirm broad Thomas/Lee-style prompts consistently return high-volume categorized output where the market supports it, not 3-4 row trickles.
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
## Value Prop Verdict
## Findings
## What Worked
## What Did Not Work
## New Gaps Found
## Recommended Scope Change For Next Gate
## Next Main Promotion Recommendation
## Next Prompt A Assignment
```

## Reusable Copy-Paste Prompt A

Use this exact prompt for every implementation feature. The agent must resolve the next feature from the current repo state instead of receiving a hard-coded feature ID.

```text
You are Prompt A for the White Rabbit reset queue.

Work in /Users/mschwar/Documents/white-rabbit. Use rebuild/validated-leads-loop as the integration branch. Do not merge or target main.

First prove current state:
- read AGENTS.md
- read STATUS.md
- read docs/00-product-northstar.md
- read docs/12-reset-gated-implementation-plan-2026-05-10.md
- read docs/03-decisions.md
- read docs/02-stack.md
- run git status --short --branch

Resolve the next feature from STATUS.md and the reset feature table:
- choose exactly one feature marked ready
- do not choose any feature already marked merged
- do not choose any feature in a blocked gate
- if zero or multiple features are ready, stop and report the ambiguity
- if the selected feature branch already exists with unmerged work, resume that branch instead of recreating or duplicating it

Implement only that selected feature on the branch named in its feature card.

Required output:
- feature ID/name selected and why it was valid
- branch used
- implementation matching only that feature card
- required verification from the feature card
- git diff --check passing
- STATUS.md and docs/12 updated with the feature status and exact Prompt B handoff
- atomic conventional commit
- pushed feature branch

Do not merge. Do not change queue readiness beyond the selected feature's own status and Prompt B handoff. Do not sync main.
```

## Reusable Copy-Paste Prompt B

Use this exact prompt after Prompt A has pushed the current feature branch. The QA agent must resolve the feature branch from repo state and must not QA an already-merged feature.

```text
You are Prompt B for the White Rabbit reset queue.

Work in /Users/mschwar/Documents/white-rabbit. QA the current reset feature branch and merge only into rebuild/validated-leads-loop. Do not merge or target main.

First prove current state:
- read AGENTS.md
- read STATUS.md
- read docs/00-product-northstar.md
- read docs/12-reset-gated-implementation-plan-2026-05-10.md
- identify the single feature branch currently waiting for QA from STATUS.md, docs/12, and the pushed branch state
- run git status --short --branch

If there is no feature branch waiting for QA, more than one plausible feature branch, or the feature is already marked merged, stop and report the ambiguity.

Required checks:
- git diff --check
- every verification command in the selected feature card
- if UI-visible, browser QA plus screenshots under .gstack/qa-reports/screenshots/
- if non-UI, explicit non-UI verification output
- northstar drift check against docs/00-product-northstar.md
- scope check proving no adjacent reset feature was implemented

If QA passes:
- write the QA report under .gstack/qa-reports/
- update STATUS.md and docs/12
- if this was not the last feature in the current gate, mark the next same-gate feature `ready`
- if this was the last feature in the current gate, mark the gate ready for Prompt C audit and leave downstream gates blocked
- commit QA/docs/fixes atomically if needed
- push the feature branch
- merge the feature branch into rebuild/validated-leads-loop only
- push rebuild/validated-leads-loop
- stop

Do not unlock the next gate. Do not sync main.
```

## Reusable Copy-Paste Prompt C

Use this exact prompt only after Prompt B has merged every feature in the current gate into `rebuild/validated-leads-loop`.

```text
You are Prompt C for the White Rabbit reset queue.

Work in /Users/mschwar/Documents/white-rabbit. Run the current reset gate evaluation and audit. This is review/report work unless the gate decision requires small docs/status updates. Do not edit product code.

First prove current state:
- read AGENTS.md
- read STATUS.md
- read docs/00-product-northstar.md
- read docs/12-reset-gated-implementation-plan-2026-05-10.md
- read docs/13-pipeline-orchestrator-contract-2026.md
- read audits/zero-trust-codebase-audit-2026-05-10.md
- identify the current in_progress reset gate from the gate table
- confirm every feature in that gate is merged before auditing the gate
- confirm the gate has not already advanced
- run git status --short --branch

If the current gate is not ready for audit, or if it has already advanced, stop and report the exact blocker. Do not rerun a completed gate.

Create an audit branch from rebuild/validated-leads-loop using audit/reset-rgN-short-name.

Required output:
- audits/gates/reset-2026-05-10/rgN-short-name.md
- audits/raw/reset-2026-05-10/rgN/ with command output and cited evidence notes
- decision: advance / hold / revise / rollback / kill
- Value Prop Verdict that explicitly says whether the current product gives enough result volume, evidence, and export value for the operator loop
- Next Main Promotion Recommendation
- if and only if advance: mark the next gate's first feature ready and provide the exact next Prompt A assignment

Commit and push the audit branch.

If and only if the gate decision is `advance`:
- checkout rebuild/validated-leads-loop
- fast-forward merge the audit branch into rebuild/validated-leads-loop
- push rebuild/validated-leads-loop
- verify Prompt A can now resolve the next ready feature from the integration branch

If the gate decision is `hold`, `revise`, `rollback`, or `kill`, do not merge the audit branch into rebuild/validated-leads-loop unless Matt explicitly accepts that decision state afterward.

Do not sync main unless Matt explicitly asks after seeing the gate decision.
```
