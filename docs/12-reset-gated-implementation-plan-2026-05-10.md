# 12 - Reset Gated Implementation Plan

**Status:** Active control document for the May 10 product reset.
**Created:** 2026-05-10.
**Integration branch:** `rebuild/validated-leads-loop`.
**Operator-use branch:** `main`, explicitly promoted from `rebuild/validated-leads-loop` by ADR-010 for Thomas/Lee internal use.
**Current product gate:** Red.
**Current reset gate:** RG4 - Sales-First Operator UI preflight. RG3 advanced on the post-R09L Prompt C audit after the live source-assisted proof reproduced the April New Mexico workbook pattern through the protected API boundary. Product remains red, and production RG4 implementation remains blocked until Matt approves refreshed mockups.
**Next Prompt A feature:** RG4 refreshed mockup/design preflight from `DESIGN.md`, not R10 production UI. R10-R12 remain blocked until Matt approves the refreshed mockups.
**Current Prompt B handoff:** None. RG3 advanced; the next assignment is pre-implementation design/mockup work.
**Current Prompt C handoff:** None. RG4 Prompt C is not valid until the refreshed mockup/design preflight is approved and R10-R12 are implemented and merged.

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
- the source-assisted/manual-oracle replay cannot reproduce the April New Mexico school-district IT workbook structure with verified-contact, manual-lookup, not-found, source URL, and blocker-note rows,
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

## Source-Assisted Research Compiler Pivot

ADR-019 adds the current RG3 remediation pivot. The live autonomous Scout path is not yet producing CRM-ready value, but Lee's April 2026 "NM IT for school districts" package proves a stronger near-term shape: human plus chatbot/Codex plus public sources can produce a useful school-district IT workbook with verified contacts, manual-lookup rows, source URLs, verification notes, and outreach/export artifacts.

The reset now treats that April package as the manual-oracle benchmark. The next remediation slice must prove White Rabbit can reproduce or improve the workbook pattern:

```text
operator target
-> public rosters / staff pages / PDFs / source URLs / seed files
-> structured extraction
-> field validation and blocker labeling
-> verified-contact rows + manual-lookup rows + not-found rows
-> sales-first export
```

This does not weaken validation. Missing, unsupported, inaccessible, guessed, or conflicting contacts still cannot become `high_trust_usable` / `READY`. The difference is that source-supported person rows with missing direct contact are preserved as useful `manual_lookup` or `review` rows instead of disappearing or being treated as total product failure.

R09D-R09H proved the offline workbook path but did not prove live startup. ADR-020 added R09I to prove API liveness and live-harness startup evidence. The post-R09I audit proved `/health` process liveness but not bounded readiness, live-runner completion, or live source-assisted product value. ADR-021 adds R09J-R09L as the ordered same-gate remediation path before the next RG3 Prompt C audit.

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

## Final Product Mockup And Design Preflight Gate

Before reset UI/export implementation starts, Matt must inspect the final product mockup artifacts and approve the active visual direction.

- Visual direction authority: `DESIGN.md`.
- Product-structure reference: `docs/mockups/final-product-2026-05-10/index.html`.
- Existing rendered screenshots: `.gstack/qa-reports/screenshots/final-product-mockups-2026-05-10/`.

`DESIGN.md` is the RG4 visual direction: deep navy instrument chassis, paper-white evidence table, restrained operator copy, and quarantined rabbit/icon handling until an approved vector exists. It is not production code and does not unlock production UI implementation by itself.

The May 10 mockup remains useful for product structure only: one search input, high-volume tier distribution, CRM-first fields, evidence one action away, sales-first export, and no Scout/Full/product-internals ceremony in the operator path.

A refreshed RG4 design preflight artifact exists on `codex/rg4-design-preflight-2026-05-11` at commit `5c5a10f` with six mockup screens. It remains an unmerged inspection artifact and must be reconciled against the post-R09L source-assisted proof before Matt approval. It does not unlock R10, export, or production UI work by itself.

If RG3 Prompt C records `advance`, it must not mark R10 ready directly. Instead, it must assign a refreshed mockup/design preflight using `DESIGN.md`. That mockup pass must produce Empty, Loading, Results, Evidence Review, Low Signal, and Mobile Review artifacts for Matt inspection. R10-R12 remain blocked until Matt approves the refreshed mockups.

Prompt A/B agents must not invent a different final UI direction during R10-R12 without fresh Matt approval. Prompt C for RG4 and RG5 must compare browser screenshots against the approved refreshed mockups and explicitly record any intentional divergence. Live-demo UI copy must not mention internal people, agent prompts, gates, sprint labels, or implementation machinery.

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
| RG2 | Search Coverage And Source Collection | R04-R06 | gate_advanced | `audits/gates/reset-2026-05-10/rg2-search-source-coverage.md` |
| RG3 | Validation, Conflict, And Gate Semantics | R07-R09L | gate_advanced | `audits/gates/reset-2026-05-10/rg3-validation-semantics.md` |
| RG4 | Sales-First Operator UI | R10-R12 | ready | `audits/gates/reset-2026-05-10/rg4-operator-ui.md` |
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
| R06 | Not-found and organization-only coverage writer | merged_to_rebuild_branch | `feat/reset-r06-nonperson-coverage` | core tests |
| R07 | Inclusive extraction prompt and candidate parse salvage | merged_to_rebuild_branch | `feat/reset-r07-inclusive-extraction` | core/API tests |
| R08 | Tiering engine, field validator, and conflict resolver | merged_to_rebuild_branch | `feat/reset-r08-tier-validation-conflicts` | core tests |
| R09 | Tier summary, score semantics, and reason language reset | merged_to_rebuild_branch | `feat/reset-r09-tier-summary-semantics` | core + web tests |
| R09A | Live value recovery and benchmark funnel diagnosis | merged_to_rebuild_branch | `feat/reset-r09a-live-value-recovery` | core/API + live/replay benchmark artifacts |
| R09B | Contact and evidence acquisition pass | merged_to_rebuild_branch | `feat/reset-r09b-contact-evidence-acquisition` | core/API + live/replay contact evidence artifacts |
| R09C | Deep multi-source evidence acquisition and tier calibration | merged_to_rebuild_branch | `feat/reset-r09c-deep-multisource-evidence-tier-calibration` | core/API + live/replay evidence/tier calibration artifacts |
| R09D | April NM evidence fixture and manual-oracle replay | merged_to_rebuild_branch | `feat/reset-r09d-april-nm-manual-oracle` | core tests + sanitized evidence fixtures |
| R09E | K-12 source map and public roster collector | merged_to_rebuild_branch | `feat/reset-r09e-k12-source-map-roster-collector` | core tests + source-map replay |
| R09F | Source-assisted lead compiler | merged_to_rebuild_branch | `feat/reset-r09f-source-assisted-lead-compiler` | core/API tests + replay artifacts |
| R09G | Research-workbook tiering and export semantics | merged_to_rebuild_branch | `feat/reset-r09g-research-workbook-tiering` | core/web or export tests as applicable |
| R09H | Manual-oracle proof replay gate packet | merged_to_rebuild_branch | `feat/reset-r09h-manual-oracle-proof-packet` | replay + live/source-assisted artifacts |
| R09I | API startup and live proof harness | merged_to_rebuild_branch | `feat/reset-r09i-api-startup-live-proof` | API tests + live harness artifacts |
| R09J | Bounded readiness diagnostics | merged_to_rebuild_branch | `feat/reset-r09j-bounded-readiness-diagnostics` | API tests + readiness probe artifacts |
| R09K | Live runner timeout containment | merged_to_rebuild_branch | `feat/reset-r09k-live-runner-timeout-containment` | core/API tests + complete timeout artifacts |
| R09L | Live source-assisted product proof | merged_to_rebuild_branch | `feat/reset-r09l-live-source-assisted-proof` | API/core tests + live source-assisted proof artifacts |
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
- R09A - Live value recovery and benchmark funnel diagnosis.
- R09B - Contact and evidence acquisition pass.
- R09C - Deep multi-source evidence acquisition and tier calibration.
- R09D - April NM evidence fixture and manual-oracle replay.
- R09E - K-12 source map and public roster collector.
- R09F - Source-assisted lead compiler.
- R09G - Research-workbook tiering and export semantics.
- R09H - Manual-oracle proof replay gate packet.
- R09I - API startup and live proof harness.
- R09J - Bounded readiness diagnostics.
- R09K - Live runner timeout containment.
- R09L - Live source-assisted product proof.

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

Accepted hold and R09A remediation:

RG3 Prompt C recorded `hold` on 2026-05-11. Matt accepted the hold state instead of treating it as a queue blocker. R09A is the only valid remediation feature before RG3 can be re-audited. It must not start RG4, mockups, R10, export polish, persistence, dogfood, or a `main` sync.

R09A scope:

- Add or repair benchmark funnel observability so every live/replay case can show the drop-off path: raw vendor hits, deduped sources, source snapshots, extracted candidates, categorized rows, person rows, `high_trust_usable` rows, and contact-quality passes.
- Fix the active broad-query floor semantics in the live quality summary. The report must distinguish the old 10-row escape-velocity floor from the current 50-500+ broad-query target, and privacy-refusal cases must pass as expected refusals instead of failing because they returned no candidates.
- Diagnose and repair the source-to-candidate-to-tier choke point that caused RG3 live runs to return only 7-10 categorized rows despite the high-volume source path. Do not satisfy this by lowering the `high_trust_usable` gate or inventing contacts.
- Improve contact/value recovery only when evidence supports it: verified contact, source-backed domain pattern, or explicit missing/unsupported status. Unsupported, inaccessible, guessed, or missing contacts must remain non-CRM-ready.
- Normalize failed-row and not-found reason language so a row with null name/title cannot imply a hidden usable lead or stale narrative certainty.

R09A required verification:

```bash
cd packages/core && uv run pytest tests/test_query_planner.py tests/test_search.py tests/test_coverage.py tests/test_source_validation.py tests/test_contact_status.py tests/test_scoring.py tests/test_orchestrator.py tests/test_live_benchmark_runner.py tests/test_quality_report.py -q
cd apps/api && WR_API_INTERNAL_TOKEN=test-internal-token uv run pytest tests -q
git diff --check
```

R09A expected evidence:

- Saved replay or live benchmark artifacts showing the new funnel fields.
- A short QA note explaining the identified choke point and why the fix increases value without relaxing READY/high-trust precision.
- Explicit proof that missing/unsupported contacts are still not marked CRM-ready.
- Explicit proof that the B2C/privacy guardrail case is handled as an expected refusal.

R09A Prompt B QA handoff:

- Branch: `feat/reset-r09a-live-value-recovery`.
- Status: `merged_to_rebuild_branch`.
- Prompt A change summary: broad Scout/Full now use high-volume breadth; run metrics and benchmark summaries expose funnel counts/notes; unmatched broad source hits become explicit failed source-gap rows; active broad-volume summaries distinguish the 10-row escape floor from the 50+ target; expected privacy refusals produce `quality_status=expected_privacy_refusal`; failed/org-only/not-found reasons no longer imply hidden usable leads.
- Prompt A verification: `cd packages/core && uv run pytest tests/test_query_planner.py tests/test_search.py tests/test_coverage.py tests/test_source_validation.py tests/test_contact_status.py tests/test_scoring.py tests/test_orchestrator.py tests/test_live_benchmark_runner.py tests/test_quality_report.py -q` (`70 passed`); `cd apps/api && WR_API_INTERNAL_TOKEN=test-internal-token uv run pytest tests -q` (`45 passed`, existing datetime deprecation warnings); `cd packages/core && uv run pytest -m integration -q` (`6 skipped`, no live integration credentials used).
- Evidence artifacts: `.gstack/qa-reports/r09a-live-value-recovery-note-2026-05-11.md` and `audits/raw/reset-2026-05-10/r09a/replay/`.
- Prompt B QA: passed. Report: `.gstack/qa-reports/qa-report-r09a-live-value-recovery-2026-05-11.md`.
- Prompt B verification: required core R09A suite (`70 passed`), API suite (`45 passed`, existing datetime warnings), `git diff --check`, replay artifact inspection, and live Scout artifacts for all six benchmark cases under `audits/raw/reset-2026-05-10/r09a/live-prompt-b/`.
- Prompt B evidence summary: broad live cases now return 50 categorized rows and privacy refusal is handled as expected, but high-trust usable rows and contact-quality passes remain `0` across the live suite. This is enough to merge R09A as a remediation/diagnostic slice, not enough to advance RG3 without Prompt C.
- Exact Prompt C handoff: Audit RG3 - Validation, Conflict, And Gate Semantics on `rebuild/validated-leads-loop`. Confirm R07-R09A are merged, run the RG3 full evaluation/audit below, and write/update `audits/gates/reset-2026-05-10/rg3-validation-semantics.md`. Do not unlock RG4, refreshed mockups, export work, dogfood, `main`, or downstream readiness unless Prompt C records an `advance`.

Post-R09A Prompt C result:

- Branch: `audit/reset-rg3-r09a-value-audit`.
- Decision: `hold`.
- Report: `audits/gates/reset-2026-05-10/rg3-validation-semantics.md`.
- Raw notes: `audits/raw/reset-2026-05-10/rg3/command-output-r09a-reaudit.md` and `audits/raw/reset-2026-05-10/rg3/evidence-notes-r09a-reaudit.md`.
- Reason: R09A recovered broad categorized volume and funnel observability, but every evaluated live benchmark still has `0` high-trust usable rows and `0` contact-quality passes. The current Prompt C re-run also timed out after the first live case, so RG3 cannot claim fresh full-suite runtime reliability.
- Matt accepted the hold and requested R09B as the next remediation. RG4, refreshed mockups, R10-R12, export, dogfood, and `main` sync remain blocked.

Accepted post-R09A hold and R09B remediation:

R09A recovered broad row volume for most broad prompts, but the product still did not produce operator value: the complete live suite had `0` high-trust usable rows and `0` contact-quality passes. R09B is therefore about contact/evidence acquisition, not more volume, UI polish, export, or design.

R09B scope:

- Add a second targeted public-web evidence pass for promising `review` person rows and organization rows where the first pass found plausible target fit but no CRM-ready contact evidence.
- Search only for source-backed contact evidence: direct staff pages, leadership/team pages, department pages, board/agenda PDFs, contact pages, source snippets, and explicit organization-domain email pattern evidence. Do not invent email addresses, infer contacts from generic domains, or mark blocked/inaccessible sources as support.
- Preserve the strict `high_trust_usable` definition. Promote a row to `high_trust_usable` only when name, title, organization, and contact status are evidence-backed or the contact is deduced from a validated domain pattern.
- If contact remains missing, unsupported, inaccessible, or failed, keep the row non-CRM-ready and explain the exact blocker.
- Add READY-blocker reporting in benchmark summaries so each candidate can show why it failed to become high trust: no contact source, no validated domain pattern, source inaccessible, title unsupported, persona mismatch, organization-only, conflicting evidence, or privacy refusal.
- Improve live benchmark runner reliability enough that timeouts produce complete partial-failure artifacts and do not silently mask the verdict.

R09B non-goals:

- No UI redesign, RG4 work, mockup implementation, export polish, persistence, dogfood packet, recipe/batch work, or `main` sync.
- No lowering of the high-trust gate.
- No paid contact-source integration unless Matt separately approves a product-positioning or vendor change.

R09B required verification:

```bash
cd packages/core && uv run pytest tests/test_query_planner.py tests/test_search.py tests/test_coverage.py tests/test_source_validation.py tests/test_contact_status.py tests/test_scoring.py tests/test_orchestrator.py tests/test_live_benchmark_runner.py tests/test_quality_report.py -q
cd apps/api && WR_API_INTERNAL_TOKEN=test-internal-token uv run pytest tests -q
git diff --check
```

R09B expected evidence:

- Saved replay or live benchmark artifacts under `audits/raw/reset-2026-05-10/r09b/`.
- A QA note explaining which evidence-acquisition path was added, which READY blockers remain, and why the change does not relax high-trust precision.
- Explicit proof that missing, unsupported, inaccessible, guessed, or failed contacts are still not marked CRM-ready.
- Explicit proof that at least one benchmark has nonzero contact-quality passes, or a source-backed explanation that public evidence was unavailable.

R09B Prompt A implementation handoff:

- Branch: `feat/reset-r09b-contact-evidence-acquisition`.
- Status: `waiting_prompt_b_qa`.
- Prompt A change summary: added a bounded targeted contact-evidence pass after first validation and before tiering; it searches up to 8 promising review/person or organization-only rows, promotes direct person emails only from source-backed public snippets, allows `deduced_with_pattern_evidence` only from explicit organization-domain pattern evidence, keeps organization-only rows non-CRM-ready, adds READY-blocker reporting to quality payloads, and makes live benchmark timeouts write partial artifacts instead of aborting the suite.
- Prompt A verification: required R09B core suite (`74 passed`); API suite (`45 passed`, existing datetime deprecation warnings).
- Evidence artifacts: `.gstack/qa-reports/r09b-contact-evidence-acquisition-note-2026-05-11.md`; `audits/raw/reset-2026-05-10/r09b/replay/contact-evidence-pass.json`; `audits/raw/reset-2026-05-10/r09b/replay/quality-summary.json`; `audits/raw/reset-2026-05-10/r09b/replay/runner-timeout-partial.json`.
- Exact Prompt B handoff: QA `feat/reset-r09b-contact-evidence-acquisition`; verify the branch contains only R09B scope, rerun the required R09B core/API suites plus `git diff --check`, inspect `audits/raw/reset-2026-05-10/r09b/replay/quality-summary.json`, confirm no unsupported/missing/inaccessible/guessed contacts become CRM-ready, confirm direct email and explicit domain-pattern evidence are the only promotion paths, confirm READY blockers are reported for missing-contact and organization-only rows, confirm runner timeouts produce partial artifacts, and confirm no RG4/UI/export/main-sync scope creep landed. If QA passes, merge only to `rebuild/validated-leads-loop` and hand off Prompt C for RG3 re-audit; do not unlock RG4 from feature QA alone.

Accepted post-R09B hold extension and R09C remediation:

R09B completed the first contact/evidence remediation pass, but Matt directed that RG3 must remain `in_progress / gate_hold` and must not run Prompt C yet. R09B + R09C together now define the accepted RG3 remediation slice. R09C exists to materially improve contact quality and tier usefulness on promising review rows without relaxing the `high_trust_usable` definition.

R09C scope:

- Deepen evidence acquisition for promising `review` rows using multiple public-web source types and corroboration paths, while preserving strict source support and explicit failure labeling.
- Improve contact-quality recovery only when multiple grounded sources or stronger field support justify it. Missing, unsupported, inaccessible, conflicting, or guessed contacts must remain non-CRM-ready.
- Recalibrate tier usefulness for promising rows so `review` becomes more operationally useful without letting weak evidence masquerade as `high_trust_usable`.
- Preserve explicit READY blockers and evidence traceability for every promising row touched by the deeper pass.
- Produce live/replay artifacts that show whether the deeper pass materially improves contact quality and tier usefulness on promising rows.

R09C non-goals:

- No Prompt C gate advance work, RG4 work, refreshed mockup unlock, R10-R12, export work, persistence work, dogfood packet work, or `main` promotion.
- No relaxation of the `high_trust_usable` definition.
- No UI-only compensation for weak contact evidence.
- No paid contact-source integration unless Matt explicitly changes product strategy later.

R09C required verification:

```bash
cd packages/core && uv run pytest tests/test_query_planner.py tests/test_search.py tests/test_coverage.py tests/test_source_validation.py tests/test_contact_status.py tests/test_scoring.py tests/test_orchestrator.py tests/test_live_benchmark_runner.py tests/test_quality_report.py -q
cd apps/api && WR_API_INTERNAL_TOKEN=test-internal-token uv run pytest tests -q
git diff --check
```

R09C expected evidence:

- Saved replay or live benchmark artifacts under `audits/raw/reset-2026-05-10/r09c/`.
- A QA note explaining which deeper multi-source evidence paths were added, which promising rows improved, which blockers remain, and why the change does not relax READY/high-trust precision.
- Explicit proof that missing, unsupported, inaccessible, conflicting, or guessed contacts are still not marked CRM-ready.
- Explicit proof that tier changes on promising rows are evidence-backed and do not overstate confidence.

R09C Prompt A implementation handoff:

- Branch: `feat/reset-r09c-deep-multisource-evidence-tier-calibration`.
- Status: `waiting_prompt_b_qa`.
- Prompt A change summary: Extended the R09B pass into a bounded multi-hop public-web contact/evidence pass across exact person/org, source-domain, staff/directory/team, department, board/agenda/PDF, contact/email-format, and news/press paths. Added page-type detection, lightweight cross-source corroboration/conflict tracking, stricter contact-quality counting so failed/non-person rows do not inflate contact passes, sharper review reasons for deep-contact misses, and benchmark observability for contact-evidence searches, contacts acquired, conflicts, and review-to-high-trust movement by case/theme.
- Prompt A verification: required R09C core suite (`76 passed`); API suite (`45 passed`, existing datetime deprecation warnings); integration marker run (`6 skipped`, no live integration credentials used); `git diff --check` passed.
- Evidence artifacts: `.gstack/qa-reports/r09c-deep-multisource-evidence-tier-calibration-note-2026-05-11.md`; `audits/raw/reset-2026-05-10/r09c/replay/deep-contact-evidence-pass.json`; `audits/raw/reset-2026-05-10/r09c/replay/quality-summary.json`.
- Exact Prompt B handoff: QA `feat/reset-r09c-deep-multisource-evidence-tier-calibration`; verify the branch contains only R09C scope, rerun the required R09C core/API suites plus `git diff --check`, inspect the R09C replay artifacts, confirm missing/unsupported/inaccessible/conflicting/guessed contacts do not become CRM-ready, confirm contact-quality counts do not include failed/non-person rows, confirm theme-level benchmark summaries expose contact acquisition success and high-trust yield, and confirm no RG4/UI/export/persistence/dogfood/main-sync scope landed. If QA passes, merge only to `rebuild/validated-leads-loop`; keep RG3 in `in_progress / gate_hold` and hand off a future RG3 Prompt C only after confirming both R09B and R09C are merged. Do not unlock RG4, refreshed mockups, R10-R12, R13-R15, export work, or `main` from feature QA alone.
- Prompt B QA: passed. Report: `.gstack/qa-reports/qa-report-r09c-deep-multisource-evidence-tier-calibration-2026-05-11.md`.
- Prompt B verification: required R09C core suite (`76 passed`), API suite (`45 passed`, existing datetime warnings), `git diff --check`, and replay artifact inspection for `audits/raw/reset-2026-05-10/r09c/replay/deep-contact-evidence-pass.json` plus `quality-summary.json`.
- Prompt B evidence summary: deeper multi-source evidence can promote promising rows only when public-web corroboration finds a direct person contact, keeps missing-contact rows in `review`, downgrades stale/conflicting rows to `failed`, and exposes contact acquisition plus high-trust yield in theme summaries without relaxing READY/high-trust precision.
- Exact Prompt C handoff: Superseded by ADR-019. Do not run Prompt C from this R09C handoff. The post-R09C live re-run recorded `hold`, and Matt accepted the source-assisted remediation pivot below.

Post-R09C source-assisted remediation:

- Branch: `audit/reset-rg3-tavily-rerun`.
- Decision: `hold`.
- Report: `audits/gates/reset-2026-05-10/rg3-validation-semantics.md`.
- Raw evidence note: `audits/raw/reset-2026-05-10/april-nm-school-district-it-evidence-note.md`.
- Reason: R09C improved deep evidence semantics, but live value still did not meet the operator loop. The product still produced `0` high-trust usable rows and `0` contact-quality passes in the Tavily-credit RG3 run. Lee's April New Mexico school-district IT package shows the stronger product path: source-assisted public research compiled into verified-contact, manual-lookup, not-found, and exportable rows.
- Queue consequence: RG3 remains `in_progress / gate_hold`. R09E is the single next ready feature. R09F-R09H remain blocked. RG4, refreshed mockups, R10-R12, export work, dogfood, and `main` promotion remain blocked.

R09D scope:

- Create sanitized April New Mexico school-district IT fixtures from the evidence note, not from private email bodies.
- Represent the manual-oracle benchmark with at least:
  - 10 verified-contact rows from the April public-email CSV shape.
  - 7 manual-lookup rows from the April missing-email CSV shape.
  - source URL, title, organization, contact status, verification note, and expected tier for every row.
- Add an offline replay comparator that can measure whether current/future output reproduces the useful workbook structure: verified contacts, manual-lookup rows, source URLs, blocker notes, and sales-first fields.
- Make current product failure measurable without requiring live services.
- Do not alter product behavior, search, extraction, tiering, API, UI, export, persistence, or `main`.

R09D non-goals:

- No live benchmark remediation.
- No source collector implementation beyond fixture/replay harness setup.
- No UI/mockup/export changes.
- No relaxation of high-trust / READY semantics.
- No dumping private email or message bodies into repo artifacts.

R09D required verification:

- Targeted core replay/fixture tests added for the manual-oracle comparator.
- `git diff --check`.
- Privacy/scope review confirming no full private email bodies or unrelated product-code changes landed.

R09D Prompt A result:

- Branch: `feat/reset-r09d-april-nm-manual-oracle`.
- Status: `merged_to_rebuild_branch`.
- Implemented only the fixture/replay harness slice: `packages/core/src/core/manual_oracle.py`, `packages/core/tests/fixtures/april_nm_manual_oracle.json`, `packages/core/tests/test_manual_oracle.py`, and `audits/raw/reset-2026-05-10/r09d/manual-oracle-current-failure-replay.json`.
- Verification run by Prompt A: `cd packages/core && uv run pytest tests/test_manual_oracle.py -q` (`5 passed`).
- Prompt B QA: `git diff --check 31a2b6518ec85babb20e2e73b933c30274fe13d2^ 31a2b6518ec85babb20e2e73b933c30274fe13d2` (clean), `cd packages/core && uv run pytest tests/test_manual_oracle.py -q` (`5 passed`), northstar drift review, and privacy/scope review passed.
- Prompt A scope note: no product behavior, search, extraction, tiering, API, UI, export, persistence, dogfood, Prompt C, RG4, or `main` changes.

R09D Prompt B result:

- Status: `merged_to_rebuild_branch`.
- QA report: `.gstack/qa-reports/qa-report-r09d-april-nm-manual-oracle-2026-05-11.md`.
- Checks passed: `git diff --check 31a2b6518ec85babb20e2e73b933c30274fe13d2^ 31a2b6518ec85babb20e2e73b933c30274fe13d2`; `cd packages/core && uv run pytest tests/test_manual_oracle.py -q` (`5 passed`); northstar drift review; privacy/scope review.
- Merge: `feat/reset-r09d-april-nm-manual-oracle` was fast-forwarded into `rebuild/validated-leads-loop`.
- Queue consequence: R09E is now ready; R09F-R09H remain blocked until their predecessors pass; RG4/R10-R12/export/dogfood/main remain blocked.

R09D Prompt A assignment:

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
- confirm it is `R09D - April NM evidence fixture and manual-oracle replay`
- use branch `feat/reset-r09d-april-nm-manual-oracle`
- if zero or multiple features are ready, stop and report the ambiguity
- if the selected feature branch already exists with unmerged work, resume that branch instead of recreating or duplicating it

Implement only R09D:
- create sanitized April New Mexico school-district IT manual-oracle fixtures
- add replay/comparison coverage that measures whether White Rabbit can reproduce the useful workbook structure
- preserve privacy by summarizing private evidence and storing only sanitized fixture data
- keep this as a non-behavior fixture/harness slice unless the codebase requires a tiny parser/helper to support the replay
- do not touch RG4, mockups, R10-R12, export work, persistence, dogfood, or main promotion

Required verification:
- targeted core replay/fixture tests added for R09D
- `git diff --check`

Required output:
- feature ID/name selected and why it was valid
- branch used
- implementation matching only R09D
- saved sanitized fixtures/artifacts under `audits/raw/reset-2026-05-10/r09d/` or `packages/core/tests/fixtures/`
- STATUS.md and docs/12 updated with the feature status and exact Prompt B handoff
- atomic conventional commit
- pushed feature branch

Do not merge. Do not trigger Prompt C. Do not change queue readiness beyond R09D's own status and Prompt B handoff. Do not sync main.
```

R09E scope:

- Build a K-12 source map and roster-first collector, starting with New Mexico.
- Prefer official education-agency rosters, district websites, staff directories, technology pages, board/agenda PDFs, contact pages, and public source families that can be audited.
- Record source family, access status, source reputation signal, crawl/extraction method, and source coverage gaps.
- Do not depend on generic Tavily breadth as the first discovery move for known public-sector verticals.

R09E Prompt A result:

- Branch: `feat/reset-r09e-k12-source-map-roster-collector`.
- Status: `passed_prompt_b_qa`.
- Implemented only the R09E source-map/collector slice: `packages/core/src/core/k12_source_map.py`, `packages/core/tests/fixtures/nm_k12_source_map.json`, `packages/core/tests/test_k12_source_map.py`, and `audits/raw/reset-2026-05-10/r09e/source-map-replay.json`.
- Change summary: added a New Mexico K-12 source-map fixture with official state education-agency directory seeds, official district homepage/staff/contact seeds, and privacy-safe R09D manual-oracle seed gaps; added a roster-first collector that emits auditable source seeds with source family, access status, reputation signal, crawl method, extraction method, supports fields, and deterministic seed IDs; added a replay summary that proves the source map avoids generic search families and records coverage gaps.
- Verification run by Prompt A: `packages/core/.venv/bin/python -m py_compile packages/core/src/core/k12_source_map.py packages/core/tests/test_k12_source_map.py` (passed); direct execution of the three targeted R09E test functions from `packages/core/tests/test_k12_source_map.py` (passed); replay-artifact tie-out confirmed `audits/raw/reset-2026-05-10/r09e/source-map-replay.json` matches `replay_k12_source_map().to_payload()`.
- Prompt B verification: `cd packages/core && uv run pytest tests/test_k12_source_map.py -q` (`3 passed`); `git diff --check b5d1013 626fb36 -- STATUS.md audits/raw/reset-2026-05-10/r09e/source-map-replay.json docs/12-reset-gated-implementation-plan-2026-05-10.md packages/core/src/core/k12_source_map.py packages/core/tests/fixtures/nm_k12_source_map.json packages/core/tests/test_k12_source_map.py` (passed); replay-artifact tie-out confirmed `audits/raw/reset-2026-05-10/r09e/source-map-replay.json` matches `replay_k12_source_map().to_payload()`; fixture metadata/privacy audit confirmed 13 source seeds, all required metadata present, zero generic search sources, and no email-like private values in the source map fixture.
- Prompt A scope note: no R09F compiler, extraction, tiering, API, UI, export, persistence, dogfood, Prompt C, RG4, or `main` changes.
- Prompt B QA report: `.gstack/qa-reports/qa-report-r09e-k12-source-map-roster-collector-2026-05-11.md`.
- Prompt B result: QA passed. Merge only to `rebuild/validated-leads-loop`, mark R09F `ready`, and keep R09G-R09H/RG4/R10-R12/export/dogfood/main blocked.

R09F expected scope after R09E passes:

- Add a source-assisted compiler path that can accept source URLs, source packs, pasted search/chatbot output, or seed CSV rows.
- Convert those inputs into canonical candidate rows with field-level evidence, dedupe, source IDs, contact status, and blocker notes.
- Preserve the strict READY/high-trust contract while making `review` and `manual_lookup` rows useful.

R09F Prompt A result:

- Branch: `feat/reset-r09f-source-assisted-lead-compiler`.
- Status: `merged_to_rebuild_branch`.
- Implemented only the R09F source-assisted compiler slice: `packages/core/src/core/source_assisted_compiler.py`, `packages/core/tests/test_source_assisted_compiler.py`, a small `ManualOracleRow` metadata extension in `packages/core/src/core/manual_oracle.py`, and `audits/raw/reset-2026-05-10/r09f/source-assisted-compiler-replay.json`.
- Change summary: added a compiler path for source URLs, source packs, pasted search/chatbot output, seed CSV rows, the R09D manual-oracle fixture, and the R09E source map. The compiler emits canonical candidate rows with deterministic source/candidate IDs, source family/reputation metadata, field evidence for name/title/organization/email/source, contact status, blocker notes, next action, dedupe reporting, and strict downgrades so missing/unsupported contacts cannot remain `high_trust_usable`.
- Verification run by Prompt A: `cd packages/core && uv run pytest tests/test_source_assisted_compiler.py tests/test_manual_oracle.py tests/test_k12_source_map.py -q` (`12 passed`); `cd packages/core && uv run pytest tests/test_source_validation.py -q` (`6 passed`); `cd packages/core && uv run pytest tests/test_contact_status.py -vv -s` (`15 passed`); `cd apps/api && WR_API_INTERNAL_TOKEN=test-internal-token uv run pytest tests -q` (`45 passed`, existing datetime deprecation warnings); `git diff --check -- STATUS.md docs/12-reset-gated-implementation-plan-2026-05-10.md packages/core/src/core/manual_oracle.py` (passed); `git diff --cached --check` (passed after staging the R09F files); replay artifact generated and validated as JSON.
- Evidence artifact: `audits/raw/reset-2026-05-10/r09f/source-assisted-compiler-replay.json`, reporting 17 compiled rows, 10 `high_trust_usable` verified-contact rows, 7 `manual_lookup` rows, no unsupported READY contacts, no generic search source URLs, source IDs on every row, and manual-oracle structure reproduced.
- Prompt A scope note: no R09G workbook/export tier semantics, UI, API endpoint, persistence, dogfood, Prompt C, RG4, R10-R12, or `main` changes.
- Exact Prompt B handoff: QA `feat/reset-r09f-source-assisted-lead-compiler`; verify the branch contains only R09F scope; rerun the R09F core tests plus API suite and staged/full diff hygiene as the checkout allows; inspect `audits/raw/reset-2026-05-10/r09f/source-assisted-compiler-replay.json`; confirm it reports 17 compiled rows, 10 `high_trust_usable` verified-contact rows, 7 `manual_lookup` rows, no unsupported READY contacts, no generic search source URLs, source IDs on every row, field evidence on name/title/organization/email/source, duplicate handling for source packs/seed rows, and no R09G export semantics, UI, persistence, dogfood, Prompt C, RG4, or `main` sync scope. If QA passes, merge only to `rebuild/validated-leads-loop`; keep R09G-R09H/RG4/R10-R12/export/dogfood/main blocked.
- Prompt B QA: passed. Report: `.gstack/qa-reports/qa-report-r09f-source-assisted-lead-compiler-2026-05-11.md`.
- Prompt B verification: `git diff --check` (passed); `git diff --cached --check` (passed); `cd packages/core && uv run pytest tests/test_source_assisted_compiler.py tests/test_manual_oracle.py tests/test_k12_source_map.py -q` (`12 passed`); `cd packages/core && uv run pytest tests/test_source_validation.py -q` (`6 passed`); `cd packages/core && uv run pytest tests/test_contact_status.py -q` (`15 passed`); `cd apps/api && WR_API_INTERNAL_TOKEN=test-internal-token uv run pytest tests -q` (`45 passed`, existing datetime deprecation warnings).
- Prompt B blocker fix: API QA initially reproduced a slow import/startup stall. Prompt B made API import safer by lazy-loading the OpenAI-backed orchestrator, moving DB initialization out of module import, disabling unused Pydantic plugin and SQLAlchemy optional C-extension loading, and replacing the PostgreSQL UUID dialect import with SQLAlchemy's generic `Uuid`.
- Prompt B evidence summary: the R09F replay artifact reports 17 compiled rows, 10 `high_trust_usable` verified-contact rows, 7 `manual_lookup` rows, no unsupported READY contacts, no generic search source URLs, source IDs on every row, field evidence on name/title/organization/email/source, duplicate handling for source packs/seed rows, and manual-oracle structure reproduced.
- Prompt B result: QA passed. Merge only to `rebuild/validated-leads-loop`, mark R09G `ready`, and keep R09H/RG4/R10-R12/export/dogfood/main blocked.

R09G expected scope after R09F passes:

- Align research-workbook tiers with operator value: `READY_WITH_CONTACT`, `REVIEW`, `MANUAL_LOOKUP`, `ORG_ONLY`, `NOT_FOUND`, and `FAILED` as appropriate for UI/export labels.
- Keep internal compatibility with existing tier models where possible, but stop treating source-supported missing-contact rows as total failure.
- Ensure sales-first export semantics can preserve usable rows, manual-lookup rows, not-found rows, source URLs, and validation/audit columns without false confidence.

R09G Prompt A result:

- Branch: `feat/reset-r09g-research-workbook-tiering`.
- Status: `implemented_pending_qa`.
- Implemented only the R09G research-workbook tier/export semantics slice: `packages/core/src/core/research_workbook.py`, `packages/core/tests/test_research_workbook.py`, and `audits/raw/reset-2026-05-10/r09g/research-workbook-replay.json`.
- Change summary: added a workbook semantics layer on top of R09F compiler rows. It maps source-assisted rows into `READY_WITH_CONTACT`, `REVIEW`, `MANUAL_LOOKUP`, `ORG_ONLY`, `NOT_FOUND`, and `FAILED`; builds sales-first CSV-ready rows with query/run/rank, CRM-ready flag, person/account/contact fields, source URL columns, validation notes, blocker notes, next action, source IDs/family/reputation, input method, and checked timestamp; preserves manual-lookup and not-found rows without marking them CRM-ready; and tracks/downgrades any claimed-ready row that lacks supported contact evidence.
- Verification run by Prompt A: `cd packages/core && uv run pytest tests/test_research_workbook.py -q` (`3 passed`); `cd packages/core && uv run pytest tests/test_research_workbook.py tests/test_source_assisted_compiler.py tests/test_manual_oracle.py tests/test_k12_source_map.py -q` (`15 passed`); `cd packages/core && uv run pytest tests/test_source_validation.py tests/test_contact_status.py -q` (`21 passed`); R09G replay artifact generated and validated as JSON.
- Evidence artifact: `audits/raw/reset-2026-05-10/r09g/research-workbook-replay.json`, reporting 17 workbook rows, 10 `READY_WITH_CONTACT` rows, 7 `MANUAL_LOOKUP` rows, no downgraded ready rows for the April replay, export headers with sales-first fields and validation/audit/source columns, source URLs preserved, and `passes=true`.
- Prompt A scope note: no UI, API endpoint, persistence, R09H proof packet, Prompt C, RG4, R10-R12, dogfood, or `main` changes.
- Exact Prompt B handoff: QA `feat/reset-r09g-research-workbook-tiering`; verify the branch contains only R09G scope; rerun `cd packages/core && uv run pytest tests/test_research_workbook.py tests/test_source_assisted_compiler.py tests/test_manual_oracle.py tests/test_k12_source_map.py -q`, `cd packages/core && uv run pytest tests/test_source_validation.py tests/test_contact_status.py -q`, and `git diff --check`; inspect `audits/raw/reset-2026-05-10/r09g/research-workbook-replay.json`; confirm it reports 17 workbook rows, 10 `READY_WITH_CONTACT` rows, 7 `MANUAL_LOOKUP` rows, zero downgraded ready rows for the April replay, export headers with sales-first fields plus validation/audit/source columns, source URLs preserved for name/title/organization/email where available, manual-lookup rows kept non-CRM-ready with next actions, and synthetic claimed-ready rows without contact support downgraded by tests. Confirm no UI, API endpoint, persistence, R09H proof packet, Prompt C, RG4, R10-R12, dogfood, or `main` sync scope landed. If QA passes, merge only to `rebuild/validated-leads-loop`, mark R09H `ready`, and keep RG4/R10-R12/export/dogfood/main blocked.
- Prompt B QA: passed. Report: `.gstack/qa-reports/qa-report-r09g-research-workbook-tiering-2026-05-11.md`.
- Prompt B verification: `git diff --check` (passed); `cd packages/core && uv run pytest tests/test_research_workbook.py tests/test_source_assisted_compiler.py tests/test_manual_oracle.py tests/test_k12_source_map.py -q` (`15 passed`); `cd packages/core && uv run pytest tests/test_source_validation.py tests/test_contact_status.py -q` (`21 passed`); replay artifact tie-out confirmed `audits/raw/reset-2026-05-10/r09g/research-workbook-replay.json` matches `build_april_nm_research_workbook_replay().to_payload()`.
- Prompt B evidence summary: the R09G replay artifact reports 17 workbook rows, 10 `READY_WITH_CONTACT` rows, 7 `MANUAL_LOOKUP` rows, zero downgraded ready rows for the April replay, sales-first export headers with validation/audit/source columns, preserved source URLs, `passes=true`, and all manual-lookup rows non-CRM-ready with next actions.
- Prompt B result: QA passed. Merge only to `rebuild/validated-leads-loop`, mark R09H `ready`, and keep RG4/R10-R12/export/dogfood/main blocked.

R09H expected scope after R09G passes:

- Produce the manual-oracle proof replay gate packet.
- Run offline replay against the April New Mexico fixture.
- Run live/source-assisted checks if services and keys are available; money/credits are not the limiting factor, but every claim must stay source-backed.
- Recommend `advance`, `hold`, `revise`, or `kill` for RG3 based on whether White Rabbit beats the human+chatbot workbook baseline.

R09H Prompt A result:

- Branch: `feat/reset-r09h-manual-oracle-proof-packet`.
- Status: `merged_to_rebuild_branch`.
- Implemented only the R09H manual-oracle proof replay gate packet: `packages/core/src/core/manual_oracle_proof_packet.py`, `packages/core/tests/test_manual_oracle_proof_packet.py`, and `audits/raw/reset-2026-05-10/r09h/manual-oracle-proof-packet.{json,md}`.
- Change summary: added a proof-packet builder that composes the R09D manual-oracle replay, R09F source-assisted compiler, and R09G research workbook into a single gate packet. The packet records manual-oracle structure reproduction, source-assisted compiler counts, workbook tier counts, unsupported CRM-ready safety checks, manual-lookup non-CRM-ready checks, private-contact redaction, latest saved live evidence counts, and Prompt C handoff constraints.
- Verification run by Prompt A: `cd packages/core && uv run pytest tests/test_manual_oracle_proof_packet.py -q` (`3 passed`); `cd packages/core && uv run pytest tests/test_manual_oracle_proof_packet.py tests/test_research_workbook.py tests/test_source_assisted_compiler.py tests/test_manual_oracle.py tests/test_k12_source_map.py -q` (`18 passed`); `cd packages/core && uv run pytest tests/test_source_validation.py tests/test_contact_status.py -q` (`21 passed`); `curl --max-time 5 -s -o /tmp/white-rabbit-api-health-r09h.json -w "%{http_code}\n" http://127.0.0.1:8000/health` returned `000`.
- Evidence artifacts: `audits/raw/reset-2026-05-10/r09h/manual-oracle-proof-packet.json`; `audits/raw/reset-2026-05-10/r09h/manual-oracle-proof-packet.md`.
- Packet evidence summary: the R09H packet reports 17 observed manual-oracle rows, 10 verified-contact rows, 7 manual-lookup rows, 17 source-assisted compiler rows, zero generic blocked source URLs, 17 workbook rows, 10 `READY_WITH_CONTACT` rows, 7 `MANUAL_LOOKUP` rows, zero unsupported CRM-ready rows, zero manual-lookup CRM-ready rows, and private contact values redacted. Credentials are present in `apps/api/.env`, but no local API responded on `/health` during R09H artifact generation; the packet therefore preserves latest saved live evidence as zero high-trust/contact-quality output and leaves fresh full-suite live evidence to Prompt C after QA/merge.
- Prompt A scope note: no product API, UI, persistence, export surface, Prompt C, RG4, refreshed mockups, R10-R12, dogfood, or `main` changes.
- Exact Prompt B handoff: QA `feat/reset-r09h-manual-oracle-proof-packet`; verify the branch contains only R09H scope; rerun `cd packages/core && uv run pytest tests/test_manual_oracle_proof_packet.py tests/test_research_workbook.py tests/test_source_assisted_compiler.py tests/test_manual_oracle.py tests/test_k12_source_map.py -q`, `cd packages/core && uv run pytest tests/test_source_validation.py tests/test_contact_status.py -q`, and `git diff --check`; inspect `audits/raw/reset-2026-05-10/r09h/manual-oracle-proof-packet.json` and `.md`; confirm the packet reports 17 observed rows, 10 verified-contact rows, 7 manual-lookup rows, 17 source-assisted compiler rows, zero generic blocked source URLs, 17 workbook rows, 10 `READY_WITH_CONTACT` rows, 7 `MANUAL_LOOKUP` rows, zero unsupported CRM-ready rows, zero manual-lookup CRM-ready rows, private contact values redacted, and Prompt C handoff constraints that keep RG4/refreshed mockups/R10-R12/export/dogfood/main blocked. Confirm live/source-assisted status records credentials present, API health `000`, no fresh live benchmark run, and latest saved live evidence still at zero high-trust/contact-quality output; do not treat R09H as a Prompt C gate advance. If QA passes, merge only to `rebuild/validated-leads-loop`, mark R09H `merged_to_rebuild_branch`, and hand off Prompt C for RG3 audit from current integration state while keeping downstream blocked unless Prompt C records `advance`.
- Prompt B QA: passed. Report: `.gstack/qa-reports/qa-report-r09h-manual-oracle-proof-packet-2026-05-11.md`.
- Prompt B verification: `git diff --check` (passed); `cd packages/core && uv run pytest tests/test_manual_oracle_proof_packet.py tests/test_research_workbook.py tests/test_source_assisted_compiler.py tests/test_manual_oracle.py tests/test_k12_source_map.py -q` (`18 passed`); `cd packages/core && uv run pytest tests/test_source_validation.py tests/test_contact_status.py -q` (`21 passed`); regenerated proof-packet payload matched `audits/raw/reset-2026-05-10/r09h/manual-oracle-proof-packet.json`.
- Prompt B evidence summary: the R09H packet reports 17 observed manual-oracle rows, 10 verified-contact rows, 7 manual-lookup rows, 17 source-assisted compiler rows, zero generic blocked source URLs, 17 workbook rows, 10 `READY_WITH_CONTACT` rows, 7 `MANUAL_LOOKUP` rows, zero unsupported CRM-ready rows, zero manual-lookup CRM-ready rows, private contact values redacted, credentials present, API health `000`, no fresh live benchmark run, and latest saved live evidence still at zero high-trust/contact-quality output.
- Prompt B result: QA passed. R09H is the last same-gate feature; merge only to `rebuild/validated-leads-loop`, mark RG3 `ready_for_prompt_c_audit / gate_hold`, and keep RG4/refreshed mockups/R10-R12/export/dogfood/main blocked unless Prompt C records `advance`.

Post-R09H Prompt C result:

- Branch: `audit/reset-rg3-manual-oracle`.
- Decision: `hold`.
- Report: `audits/gates/reset-2026-05-10/rg3-validation-semantics.md`.
- Raw notes: `audits/raw/reset-2026-05-10/rg3/evidence-notes-r09h-reaudit.md`; command outputs and health checks under `audits/raw/reset-2026-05-10/rg3/commands/`; replay packet under `audits/raw/reset-2026-05-10/rg3/replay-r09h-reaudit/`.
- Reason: The source-assisted manual-oracle replay now passes offline with 17 workbook rows, 10 `READY_WITH_CONTACT`, 7 `MANUAL_LOOKUP`, sales-first export fields, and zero unsupported CRM-ready rows. RG3 still cannot advance because current live evidence is unavailable: the local API stayed in application startup, `/health` returned `000`, and no fresh live benchmark suite completed. The latest complete saved live suite still has zero high-trust usable rows and zero contact-quality passes.
- Queue consequence: RG3 remains `gate_hold`. No Prompt A, Prompt B, or Prompt C assignment is valid until Matt accepts the hold and assigns another same-gate remediation or revises the plan. RG4, refreshed mockups, R10-R12, export, dogfood, and `main` promotion remain blocked.

Accepted post-R09H hold and R09I remediation:

- Date: 2026-05-11.
- Decision: Matt accepted the RG3 hold and authorized a narrow same-gate remediation.
- New feature: `R09I - API startup and live proof harness`.
- Branch: `feat/reset-r09i-api-startup-live-proof`.
- Status: `merged_to_rebuild_branch` after Prompt B QA; this historical section is superseded by the post-R09I hold and R09J-R09L remediation below.
- Why it exists: The offline source-assisted workbook proof passes, but future RG3 audits cannot distinguish product-value failure from runtime failure while the local API can stay in startup and `/health` can return `000` without actionable diagnostics.
- Scope:
  - Split process liveness from dependency readiness so `/health` proves the API process can answer without blocking on vendor, DB, or long preflight work.
  - Add a readiness/preflight endpoint or equivalent diagnostic payload that reports DB/config/vendor readiness with actionable fields and bounded timeouts.
  - Make local/live benchmark startup deterministic: start API, wait for `/health`, collect readiness diagnostics, and only then run live benchmarks.
  - Capture startup failure artifacts under `audits/raw/reset-2026-05-10/r09i/` and future RG3 raw folders, including command output, health/readiness responses, ports, env-key presence without secret values, and timeout reason.
  - Preserve existing internal auth semantics for protected product endpoints.
- Non-goals:
  - No lead-quality tuning, source compiler changes, prompt/model changes, tier/export semantics, UI, persistence, dogfood packet, RG4, R10-R12, or `main` promotion.
  - Do not make `/health` call OpenAI, Tavily, Postgres, or any long import/preflight path.
  - Do not hide runtime failures by returning success for readiness when required dependencies are unavailable.
- Required verification:
  - `cd apps/api && WR_API_INTERNAL_TOKEN=test-internal-token uv run pytest tests -q`
  - Add focused API tests proving `/health` responds without DB/vendor readiness and readiness diagnostics stay bounded/actionable.
  - Add or update harness tests proving startup failure writes artifacts instead of ambiguous `000`-only evidence.
  - `git diff --check`
- Exact Prompt A assignment:

```text
Implement R09I - API startup and live proof harness on feat/reset-r09i-api-startup-live-proof.

Keep scope to API startup/readiness diagnostics and live benchmark harness reliability. Do not change lead-quality logic, prompts, source-assisted compiler behavior, workbook/export semantics, UI, persistence, dogfood, RG4/R10-R12, or main promotion.

The output must make future Prompt C audits able to answer:
- did the API process start and answer /health?
- are DB/config/vendor dependencies ready, degraded, or unavailable?
- did the live benchmark suite actually run, or did startup fail?
- where are the raw startup and readiness artifacts?

Before ending, update STATUS.md and docs/12 with the Prompt B handoff, write any R09I raw artifacts under audits/raw/reset-2026-05-10/r09i/, commit, and push the feature branch only.
```

R09I Prompt B QA handoff:

- Branch: `feat/reset-r09i-api-startup-live-proof`.
- Status: `merged_to_rebuild_branch`.
- Prompt A change summary: API startup no longer runs DB/vendor preflight before `/health`; `/health` is process liveness only; `/readiness` reports config, database, OpenAI, and Tavily readiness with redacted env presence and actionable status; the live benchmark runner waits for `/health`, captures readiness diagnostics, writes startup artifacts, and emits per-case `api_startup_failed` / HTTP 599 artifacts when health never answers.
- Prompt A verification:
  - `cd apps/api && WR_API_INTERNAL_TOKEN=test-internal-token uv run pytest tests -q` (`48 passed`, existing datetime deprecation warnings)
  - `cd packages/core && uv run pytest tests/test_live_benchmark_runner.py -q` (`5 passed`)
  - `cd packages/core && WR_API_INTERNAL_TOKEN=test-internal-token uv run python -m core.live_benchmark_runner --api-base-url http://127.0.0.1:8999 --api-token test-internal-token --output-dir ../../audits/raw/reset-2026-05-10/r09i/startup-failure-probe --startup-timeout-seconds 0.2` (wrote startup-failure and per-case artifacts)
- Artifacts: `audits/raw/reset-2026-05-10/r09i/startup-failure-probe/`.
- Exact Prompt B handoff: QA `feat/reset-r09i-api-startup-live-proof`; verify the branch contains only R09I startup/readiness diagnostics and live-harness reliability scope; rerun `cd apps/api && WR_API_INTERNAL_TOKEN=test-internal-token uv run pytest tests -q`, `cd packages/core && uv run pytest tests/test_live_benchmark_runner.py -q`, and `git diff --check`; inspect `audits/raw/reset-2026-05-10/r09i/startup-failure-probe/startup/startup-failure.json`, `startup/startup-diagnostics.json`, `startup/health.http`, per-case `*.http`/`*.json`, and `quality-summary.json`; confirm `/health` responds without DB/vendor readiness, `/readiness` reports DB/config/vendor readiness without secret values, startup failures write actionable artifacts with port/env-presence/timeout details, and failed startup marks every case `api_startup_failed` with HTTP 599 instead of ambiguous `000`-only evidence. Confirm no lead-quality logic, prompts, source-assisted compiler behavior, workbook/export semantics, UI, persistence, dogfood, RG4/R10-R12, or `main` promotion landed. If QA passes, merge only to `rebuild/validated-leads-loop`, mark R09I `merged_to_rebuild_branch`, and hand off Prompt C for RG3 from current integration state while keeping downstream blocked unless Prompt C records `advance`.

Post-R09I Prompt C result:

- Branch: `audit/reset-rg3-live-proof`.
- Decision: `hold`.
- Report: `audits/gates/reset-2026-05-10/rg3-validation-semantics.md`.
- Raw notes: `audits/raw/reset-2026-05-10/rg3/post-r09i-live-proof/evidence-notes.md`; command outputs, live attempts, startup artifacts, and replay artifacts under `audits/raw/reset-2026-05-10/rg3/post-r09i-live-proof/`.
- Reason: R09I improved process-liveness proof: a clean API process answered `/health` and the startup probe captured `health_ok=true`. RG3 still cannot advance because `/readiness` timed out, the live runner timed out on sandbox reset with an unhandled `httpx.ReadTimeout`, and the direct `/scout` attempt timed out on the first Thomas Arizona K-12 benchmark with zero returned rows. The current live product path therefore does not prove result volume, evidence quality, contact-quality passes, or export value. The April New Mexico source-assisted replay still passes offline with 17 workbook rows, 10 `READY_WITH_CONTACT`, 7 `MANUAL_LOOKUP`, sales-first export fields, and zero unsupported CRM-ready rows.
- Queue consequence: RG3 remains `gate_hold`. Matt accepted this hold on 2026-05-11 and authorized ordered same-gate remediation slices R09J-R09L. RG4, refreshed mockups, R10-R12, export, dogfood, and `main` promotion remain blocked.

Accepted post-R09I hold and R09J-R09L remediation:

- Date accepted: 2026-05-11.
- Decision: keep RG3 in `gate_hold` and add three ordered same-gate remediation slices. R09J and R09K are merged to `rebuild/validated-leads-loop`; R09L has now passed Prompt B QA and merged to `rebuild/validated-leads-loop`. RG3 is ready for Prompt C audit.
- Why this split exists: the post-R09I hold exposed three different failure modes that should not be bundled into one oversized feature. `/readiness` must become bounded and diagnostic; the live runner must complete and preserve artifacts even when reset/product calls time out; and the source-assisted workbook value path must be proven through the live service boundary instead of only through offline replay.

R09J scope - Bounded readiness diagnostics:

- Branch: `feat/reset-r09j-bounded-readiness-diagnostics`.
- Status: `merged_to_rebuild_branch`.
- Goal: make `/readiness` fast, bounded, and actionable without weakening `/health` process liveness or pretending unavailable dependencies are healthy.
- Requirements:
  - `/readiness` must not block behind OpenAI, Tavily, Postgres, sandbox reset, or long application startup work.
  - Dependency checks must use explicit short timeouts, cancellation/containment, and a total response budget.
  - The readiness payload must report process, config, database, OpenAI, Tavily, and any sandbox/dependency readiness separately with redacted env presence and actionable status/reason fields.
  - `/health` remains process-only liveness and must not call vendors or the database.
  - If a dependency is unavailable, readiness reports `degraded` or `unavailable` with reason; it must not hide the failure as success.
  - Write R09J probe artifacts under `audits/raw/reset-2026-05-10/r09j/`, including health/readiness HTTP captures, timing, env-key presence without values, and timeout/dependency status.
- Non-goals:
  - No lead-quality logic, prompt/model changes, source-assisted compiler changes, Scout/search tuning, workbook/export semantics, UI, persistence, dogfood, RG4/R10-R12, Prompt C audit, or `main` promotion.
- Prompt A change summary: Added a process-first readiness response that reports process, config, database, OpenAI, Tavily, and sandbox checks separately; moved `/readiness` onto a worker thread; bounded dependency checks with concurrent time-boxed execution; surfaced redacted env presence plus actionable `ready`/`degraded`/`misconfigured`/`unavailable` status and reason fields; and increased timing precision so the raw probe shows nonzero elapsed time instead of collapsing fast reads to `0.0`.
- Verification run by Prompt A:
- `cd apps/api && WR_API_INTERNAL_TOKEN=test-internal-token uv run pytest tests -q` (`49 passed`, existing datetime deprecation warnings)
- `cd apps/api && python -m py_compile api/main.py tests/test_preflight.py` (passed)
- `git diff --check` (passed)
- Manual readiness probe against a local API process with empty env values under `audits/raw/reset-2026-05-10/r09j/missing-config-probe/`
    - `health.http`: `200 0.001685`
    - `readiness.http`: `200 0.001600`
    - `readiness.json`: `process=ready`, `config/database/openai/tavily/sandbox=misconfigured`, redacted env presence, `budget_seconds=2.0`, and `elapsed_seconds=0.000381`
- Artifacts: `audits/raw/reset-2026-05-10/r09j/missing-config-probe/`.
- Exact Prompt B handoff:

```text
QA `feat/reset-r09j-bounded-readiness-diagnostics`; verify the branch contains only R09J scope; rerun `cd apps/api && WR_API_INTERNAL_TOKEN=test-internal-token uv run pytest tests -q`, `git diff --check`, and inspect `audits/raw/reset-2026-05-10/r09j/missing-config-probe/health.http`, `health.json`, `readiness.http`, and `readiness.json`; confirm `/health` remains process-only, `/readiness` returns within the configured budget with process/config/database/OpenAI/Tavily/sandbox checks reported separately, missing envs surface as `misconfigured` with redacted env presence, dependency slowness becomes bounded `unavailable` instead of hanging, and no lead-quality, prompt/model, search, workbook/export, UI, persistence, dogfood, RG4/R10-R12, Prompt C, or `main` promotion landed. If QA passes, merge only to `rebuild/validated-leads-loop`, mark R09J `merged_to_rebuild_branch`, and hand off Prompt A for R09K only.
```
R09K Prompt B QA passed; R09L Prompt B QA passed and merged to `rebuild/validated-leads-loop`. Prompt C is now the active step.

R09K scope - Live runner timeout containment:

- Branch: `feat/reset-r09k-live-runner-timeout-containment`.
- Status: `merged_to_rebuild_branch`.
- Goal: make the live benchmark runner finish with complete artifacts even when sandbox reset, readiness, health-after-timeout, or product-path requests time out.
- Requirements:
  - Wrap sandbox reset, startup checks, readiness checks, benchmark requests, and health-after-timeout probes in explicit timeouts with structured error handling.
  - No unhandled `httpx.ReadTimeout` or equivalent exception may abort the suite without writing a quality summary.
  - Every benchmark case must get an artifact row even when the runner cannot call the product path.
  - Timeout artifacts must distinguish `readiness_timeout`, `sandbox_reset_timeout`, `runner_timeout`, `api_startup_failed`, `product_request_timeout`, and `privacy_refusal_expected` where applicable.
  - The quality summary must include enough data to tell runtime failure from product-value failure.
- Non-goals:
  - No search/result-quality tuning, no source-assisted product endpoint, no UI/export/persistence/dogfood/RG4/R10-R12/main work.
- Required verification:
  - `cd packages/core && uv run pytest tests/test_live_benchmark_runner.py -q`
  - `cd apps/api && WR_API_INTERNAL_TOKEN=test-internal-token uv run pytest tests -q`
  - Add or update tests that simulate sandbox reset timeout, product request timeout, and readiness timeout while still producing complete artifacts.
  - Save timeout-containment artifacts under `audits/raw/reset-2026-05-10/r09k/`.
  - `git diff --check`

Prompt A change summary:

- Added explicit timeout containment for startup readiness, sandbox reset, product requests, and health-after-timeout probes so the live runner always writes a quality summary and case artifacts instead of aborting on `httpx.ReadTimeout`.
- Labeled readiness request timeouts as `readiness_timeout`, sandbox reset timeouts as `sandbox_reset_timeout`, product request timeouts as `product_request_timeout`, and failed post-timeout health recovery probes as `runner_timeout`.
- Kept runtime failures separate from product-value failures by writing partial artifacts with empty leads plus structured startup/sandbox-reset/post-timeout probe payloads, while preserving the existing quality report semantics for successful or privacy-refusal cases.

Verification run by Prompt A:

- `cd packages/core && uv run pytest tests/test_live_benchmark_runner.py -q` (`8 passed`)
- `cd apps/api && WR_API_INTERNAL_TOKEN=test-internal-token uv run pytest tests -q` (`49 passed`, existing datetime deprecation warnings)
- `git diff --check` (passed)
- Timeout-containment artifacts saved under `audits/raw/reset-2026-05-10/r09k/` in the `api-startup-failed`, `readiness-timeout`, `sandbox-reset-timeout`, `product-request-timeout`, and `runner-timeout-probe` subdirectories.

Prompt B QA result: pass. See `.gstack/qa-reports/qa-report-r09k-live-runner-timeout-containment-2026-05-11.md`. The branch stayed inside R09K scope, verified the required core/API tests and `git diff --check`, and produced complete timeout-containment artifacts under `audits/raw/reset-2026-05-10/r09k/`.

R09L scope - Live source-assisted product proof:

- Branch: `feat/reset-r09l-live-source-assisted-proof`.
- Status: `merged_to_rebuild_branch`.
- Implemented only the R09L live source-assisted proof slice: `packages/core/src/core/live_source_assisted_proof.py`, `packages/core/tests/test_live_source_assisted_proof.py`, `apps/api/api/main.py`, `apps/api/tests/test_api.py`, and `audits/raw/reset-2026-05-10/r09l/live-source-assisted-proof.{json,md}`.
- Goal: prove the April New Mexico source-assisted workbook path through a live API/service boundary, not just offline module replay.
- Requirements:
  - Add the smallest internal API or service-boundary harness needed to run the source-assisted compiler/research-workbook path from sanitized target/source-map inputs.
  - The path must be protected by existing internal token semantics if exposed over HTTP.
  - It must produce live artifacts showing workbook rows, tier counts, source URLs, blocker notes, sales-first fields, and zero unsupported CRM-ready rows.
  - It must preserve the offline manual-oracle replay contract: 17 observed workbook rows, 10 `READY_WITH_CONTACT`, 7 `MANUAL_LOOKUP`, source URLs/provenance, and no private contact values beyond sanitized fixture data.
  - If the live service cannot reproduce the offline proof, it must fail with actionable artifacts rather than silently passing.
- Non-goals:
  - No public UI, no production export surface, no design/RG4/R10-R12 work, no autonomous Scout quality tuning beyond what is needed to prove the source-assisted path, no dogfood packet, and no `main` promotion.
- Required verification:
  - `cd packages/core && uv run pytest tests/test_manual_oracle_proof_packet.py tests/test_research_workbook.py tests/test_source_assisted_compiler.py tests/test_manual_oracle.py tests/test_k12_source_map.py -q`
  - `cd apps/api && WR_API_INTERNAL_TOKEN=test-internal-token uv run pytest tests -q`
  - Add focused tests for the live/service-boundary source-assisted path.
  - Save live proof artifacts under `audits/raw/reset-2026-05-10/r09l/`.
  - `git diff --check`

- Prompt A change summary: added a protected `/source-assisted-proof` API proof route that composes the April NM source-map replay, source-assisted compiler replay, and research workbook replay into one live artifact; added a core proof packet/writer with request summary, service-boundary details, safety checks, and Prompt B handoff metadata; and preserved the offline workbook contract while proving the internal-token boundary.
- Verification run by Prompt A: `uv run pytest tests/test_live_source_assisted_proof.py -q` (`2 passed`); `cd apps/api && uv run pytest tests/test_api.py -k "source_assisted_proof or protected_api_endpoints_require_internal_token" -q` (`16 passed, 28 deselected`); `WR_API_INTERNAL_TOKEN=test-internal-token uv run python - <<'PY' ...` against the protected `/source-assisted-proof` route, which wrote `audits/raw/reset-2026-05-10/r09l/live-source-assisted-proof.json` and `.md`.
- Evidence artifacts: `audits/raw/reset-2026-05-10/r09l/live-source-assisted-proof.json`; `audits/raw/reset-2026-05-10/r09l/live-source-assisted-proof.md`.
- Exact Prompt B handoff: QA `feat/reset-r09l-live-source-assisted-proof`; verify the branch contains only R09L scope; rerun `cd packages/core && uv run pytest tests/test_live_source_assisted_proof.py tests/test_manual_oracle_proof_packet.py tests/test_research_workbook.py tests/test_source_assisted_compiler.py tests/test_manual_oracle.py tests/test_k12_source_map.py -q`, `cd apps/api && WR_API_INTERNAL_TOKEN=test-internal-token uv run pytest tests -q`, and `git diff --check`; inspect `audits/raw/reset-2026-05-10/r09l/live-source-assisted-proof.json` and `.md`; confirm the protected `/source-assisted-proof` route returns the April New Mexico source-map replay, source-assisted compiler replay, workbook proof, sales-first export headers, blocker notes, and zero unsupported CRM-ready rows; confirm the response reports 17 workbook rows, 10 `READY_WITH_CONTACT` rows, 7 `MANUAL_LOOKUP` rows, source URLs, blocker notes, and redacted private contact values; confirm the route is internal-token protected and no public UI, production export surface, design/RG4/R10-R12, dogfood packet, or `main` promotion landed. If QA passes, merge only to `rebuild/validated-leads-loop`, mark R09L `merged_to_rebuild_branch`, and hand off Prompt C for RG3 from current integration-branch state once R09J-R09L are all merged, while keeping downstream blocked unless Prompt C records `advance`.

R09L Prompt B QA handoff:

- Branch: `feat/reset-r09l-live-source-assisted-proof`.
- Status: `merged_to_rebuild_branch`.
- Prompt A change summary: added a protected `/source-assisted-proof` API proof route that composes the April NM source-map replay, source-assisted compiler replay, and research workbook replay into one live artifact; added a core proof packet/writer with request summary, service-boundary details, safety checks, and Prompt B handoff metadata; and preserved the offline workbook contract while proving the internal-token boundary.
- Prompt B verification: `git diff --check` (passed); `cd packages/core && uv run pytest tests/test_live_source_assisted_proof.py tests/test_manual_oracle_proof_packet.py tests/test_research_workbook.py tests/test_source_assisted_compiler.py tests/test_manual_oracle.py tests/test_k12_source_map.py -q` (`20 passed`); `cd apps/api && WR_API_INTERNAL_TOKEN=test-internal-token uv run pytest tests -q` (`51 passed`, existing datetime deprecation warnings).
- Prompt B evidence summary: protected `/source-assisted-proof` route returned the April New Mexico source-map replay, source-assisted compiler replay, workbook proof, sales-first export headers, blocker notes, and zero unsupported CRM-ready rows; response reported 17 workbook rows, 10 `READY_WITH_CONTACT` rows, 7 `MANUAL_LOOKUP` rows, source URLs, blocker notes, redacted private contact values, `source_map_reproduced=true`, `internal_token_required=true`, and `protected_route_ok=true`.
- Prompt B result: QA passed. Merge only to `rebuild/validated-leads-loop`, mark `R09L` `merged_to_rebuild_branch`, and hand off Prompt C for RG3 from `rebuild/validated-leads-loop` now that R09J-R09L are merged, while keeping downstream blocked unless Prompt C records `advance`.

Prompt C audit queue:

- None. RG3 advanced on the post-R09L Prompt C audit. The next valid assignment is the RG4 refreshed mockup/design preflight from `DESIGN.md`; R10-R12 remain blocked until Matt approves the refreshed mockups.

Post-R09L Prompt C result:

- Branch: `audit/reset-rg3-validation-semantics`.
- Decision: `advance`.
- Report: `audits/gates/reset-2026-05-10/rg3-validation-semantics.md`.
- Raw evidence: `audits/raw/reset-2026-05-10/rg3/post-r09l-source-assisted-proof/`.
- Reason: R07-R09L are merged to `origin/rebuild/validated-leads-loop`; the current RG3 regression suite passed (`87 passed`); the API suite passed (`51 passed`); `/health` returned 200; `/readiness` returned a bounded diagnostic payload; tokenless `/source-assisted-proof` returned 401; and tokened `/source-assisted-proof` returned 200 with `passes=true`.
- Value proof: the protected live source-assisted route reproduced the April New Mexico workbook pattern with 17 workbook rows, 10 `READY_WITH_CONTACT`, 7 `MANUAL_LOOKUP`, 18 source-assisted sources, source URLs on every row, blocker/next-action notes for manual lookup rows, sales-first export headers, zero unsupported CRM-ready rows, zero manual-lookup CRM-ready rows, and private contact values redacted.
- Scope caveat: this advances RG3 for the source-assisted validation/runtime path. It does not prove autonomous broad Scout as the operator value path, does not make the product yellow/green, does not unlock export/dogfood, and does not justify a `main` promotion without Matt's explicit request.
- Queue consequence: RG4 is ready for refreshed mockup/design preflight only. Per ADR-015, do not mark R10 ready and do not edit production UI code until Matt approves the refreshed mockups.

Exact next assignment:

```text
You are Prompt A for the White Rabbit reset queue.

Work in /Users/mschwar/Documents/white-rabbit. Use rebuild/validated-leads-loop as the integration branch. This is a refreshed RG4 mockup/design preflight, not production UI implementation. Do not edit production UI code. Do not merge or target main.

First prove current state:
- read AGENTS.md
- read STATUS.md
- read DESIGN.md
- read docs/00-product-northstar.md
- read docs/12-reset-gated-implementation-plan-2026-05-10.md
- read docs/13-pipeline-orchestrator-contract-2026.md
- read audits/gates/reset-2026-05-10/rg3-validation-semantics.md
- run git status --short --branch

Create a branch from rebuild/validated-leads-loop using codex/rg4-design-preflight-2026-05-12.

Produce refreshed RG4 mockup/design preflight artifacts under docs/mockups/rg4-design-preflight-2026-05-12/ for:
- Empty
- Loading
- Results
- Evidence Review
- Low Signal
- Mobile Review

Use DESIGN.md as the visual direction authority and docs/mockups/final-product-2026-05-10/index.html as the product-structure reference. Reconcile the preflight against the post-R09L source-assisted evidence: 17 source-assisted workbook rows, READY/REVIEW/manual-lookup semantics, evidence one action away, blocker/next-action notes, and sales-first export framing. Keep public/demo copy free of internal people, sprint IDs, gate IDs, and implementation machinery.

Required output:
- static mockup artifacts and rendered screenshots for all six states
- a short preflight report explaining how the mockups align with DESIGN.md, the product northstar, and the post-R09L source-assisted proof
- STATUS.md and docs/12 update with the handoff for Matt approval

Do not mark R10 ready. Do not start R10-R12 production UI implementation. Do not start export, persistence, dogfood, or main promotion.
```

RG3 full evaluation/audit:

- Re-run manufacturing benchmark and confirm no 503 parse crash.
- Sample 10 returned person rows across benchmarks and inspect validation field support.
- Confirm duplicate/conflict cases fail or are downgraded.
- Confirm no row with missing/unsupported contact is labeled CRM-ready.
- Confirm broad live benchmarks no longer produce only 7-10 categorized rows unless source evidence proves the market itself is smaller.
- Confirm the live quality summary reports benchmark funnel drop-offs and treats privacy refusals separately from no-candidate product failures.
- Confirm contact/evidence acquisition produces source-backed contact status or explicit READY blockers for promising person/review rows.
- Confirm live runner timeout behavior records partial-failure artifacts cleanly.
- Confirm R09D-R09L are merged before any RG3 Prompt C re-audit begins.
- Replay the April New Mexico manual-oracle benchmark and confirm the product can reproduce or improve the workbook structure: verified contacts, manual-lookup rows, source URLs, blocker notes, and sales-first fields.

Advance criteria:

- Bad candidates degrade into explicit failed/noisy rows.
- Gate language and UI score semantics no longer create false confidence.
- High-trust usable precision is preserved while review/org-only/not-found/failed candidates remain visible and explained.
- At least one required live benchmark produces nonzero `high_trust_usable` output without unsupported contacts.
- Broad-query categorized output materially improves from the RG3 hold baseline or the gate report proves the public-web market is smaller.
- At least one required live benchmark produces nonzero contact-quality passes, or the gate report proves source-backed public contact evidence is unavailable for the benchmark set and recommends a product-positioning/vendor decision instead of pretending the current loop is CRM-ready.
- April New Mexico manual-oracle replay reproduces or improves the source-assisted workbook pattern with zero unsupported contacts marked CRM-ready.
- RG4, refreshed mockups, R10-R12, export work, and any `main` promotion remain blocked until R09D-R09L are complete and a future RG3 Prompt C records `advance`.

## RG4 - Sales-First Operator UI

Features:

- R10 - Primary search workspace simplification.
- R11 - Compact CRM-first results table.
- R12 - Evidence dossier review mode.

Goal:
Restore the calm v1 operator shape without restoring v1 implementation.

Design preflight:

- `DESIGN.md` is the visual direction authority for RG4.
- The May 10 mockup remains the product-structure reference, not the final visual direction.
- Before R10 starts, a design/mockup agent must produce refreshed Empty, Loading, Results, Evidence Review, Low Signal, and Mobile Review mockups from `DESIGN.md`.
- Matt must approve the refreshed mockups before R10 can be marked `ready`.
- The rabbit/icon problem stays quarantined: use a placeholder or approved existing asset only until an approved vector mark exists; do not create an ad hoc CSS rabbit, generated mascot, or competing mark in production UI.

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
- read DESIGN.md if present; treat it as future RG4 visual direction only, not as evidence that the current data-quality gate passed
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
- if and only if advance: unlock the next valid assignment from the integration branch and state whether that assignment is a Prompt A feature or a design/mockup preflight
- if the current gate is RG3 and the decision is advance: do not mark R10 ready; assign the refreshed mockup/design preflight from DESIGN.md and leave R10-R12 blocked until Matt approves the refreshed mockups

Commit and push the audit branch.

If and only if the gate decision is `advance`:
- checkout rebuild/validated-leads-loop
- fast-forward merge the audit branch into rebuild/validated-leads-loop
- push rebuild/validated-leads-loop
- verify Prompt A can now resolve the next ready feature from the integration branch

If the gate decision is `hold`, `revise`, `rollback`, or `kill`, do not merge the audit branch into rebuild/validated-leads-loop unless Matt explicitly accepts that decision state afterward.

Do not sync main unless Matt explicitly asks after seeing the gate decision.
```
