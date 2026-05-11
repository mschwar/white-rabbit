# RG3 command output

## Initial status
## audit/reset-rg3-validation-semantics
?? audits/raw/reset-2026-05-10/rg3/

## Current gate proof
docs/12-reset-gated-implementation-plan-2026-05-10.md:8:**Current reset gate:** RG3 - Validation, Conflict, And Gate Semantics, ready for Prompt C audit.
docs/12-reset-gated-implementation-plan-2026-05-10.md:9:**Next Prompt A feature:** None. RG4 remains blocked until Prompt C records an RG3 `advance`, a refreshed mockup pass is produced from `DESIGN.md`, and Matt approves that refreshed mockup.
docs/12-reset-gated-implementation-plan-2026-05-10.md:10:**Current Prompt B handoff:** None. R09 passed Prompt B QA on `feat/reset-r09-tier-summary-semantics` and is merged to `rebuild/validated-leads-loop`; Prompt C should audit RG3. Do not unlock RG4 or touch `main`.
docs/12-reset-gated-implementation-plan-2026-05-10.md:130:- Visual direction authority: `DESIGN.md`.
docs/12-reset-gated-implementation-plan-2026-05-10.md:134:`DESIGN.md` is the future RG4 visual direction: deep navy instrument chassis, paper-white evidence table, restrained operator copy, and quarantined rabbit/icon handling until an approved vector exists. It is not production code and does not unlock RG4 by itself.
docs/12-reset-gated-implementation-plan-2026-05-10.md:138:If RG3 Prompt C records `advance`, it must not mark R10 ready directly. Instead, it must assign a refreshed mockup/design preflight using `DESIGN.md`. That mockup pass must produce Empty, Loading, Results, Evidence Review, Low Signal, and Mobile Review artifacts for Matt inspection. R10-R12 remain blocked until Matt approves the refreshed mockups.
docs/12-reset-gated-implementation-plan-2026-05-10.md:140:Prompt A/B agents must not invent a different final UI direction during R10-R12 without fresh Matt approval. Prompt C for RG4 and RG5 must compare browser screenshots against the approved refreshed mockups and explicitly record any intentional divergence. Live-demo UI copy must not mention internal people, agent prompts, gates, sprint labels, or implementation machinery.
docs/12-reset-gated-implementation-plan-2026-05-10.md:189:| RG3 | Validation, Conflict, And Gate Semantics | R07-R09 | gate_pending_audit | `audits/gates/reset-2026-05-10/rg3-validation-semantics.md` |
docs/12-reset-gated-implementation-plan-2026-05-10.md:190:| RG4 | Sales-First Operator UI | R10-R12 | blocked | `audits/gates/reset-2026-05-10/rg4-operator-ui.md` |
docs/12-reset-gated-implementation-plan-2026-05-10.md:205:| R07 | Inclusive extraction prompt and candidate parse salvage | merged_to_rebuild_branch | `feat/reset-r07-inclusive-extraction` | core/API tests |
docs/12-reset-gated-implementation-plan-2026-05-10.md:206:| R08 | Tiering engine, field validator, and conflict resolver | merged_to_rebuild_branch | `feat/reset-r08-tier-validation-conflicts` | core tests |
docs/12-reset-gated-implementation-plan-2026-05-10.md:207:| R09 | Tier summary, score semantics, and reason language reset | merged_to_rebuild_branch | `feat/reset-r09-tier-summary-semantics` | core + web tests |
docs/12-reset-gated-implementation-plan-2026-05-10.md:340:## RG3 - Validation, Conflict, And Gate Semantics
docs/12-reset-gated-implementation-plan-2026-05-10.md:344:- R07 - Inclusive extraction prompt and candidate parse salvage.
docs/12-reset-gated-implementation-plan-2026-05-10.md:345:- R08 - Tiering engine, field validator, and conflict resolver.
docs/12-reset-gated-implementation-plan-2026-05-10.md:346:- R09 - Tier summary, score semantics, and reason language reset.
docs/12-reset-gated-implementation-plan-2026-05-10.md:370:RG3 full evaluation/audit:
docs/12-reset-gated-implementation-plan-2026-05-10.md:383:## RG4 - Sales-First Operator UI
docs/12-reset-gated-implementation-plan-2026-05-10.md:396:- `DESIGN.md` is the visual direction authority for RG4.
docs/12-reset-gated-implementation-plan-2026-05-10.md:398:- Before R10 starts, a design/mockup agent must produce refreshed Empty, Loading, Results, Evidence Review, Low Signal, and Mobile Review mockups from `DESIGN.md`.
docs/12-reset-gated-implementation-plan-2026-05-10.md:420:RG4 full evaluation/audit:
docs/12-reset-gated-implementation-plan-2026-05-10.md:656:- read DESIGN.md if present; treat it as future RG4 visual direction only, not as evidence that the current data-quality gate passed
docs/12-reset-gated-implementation-plan-2026-05-10.md:674:- if the current gate is RG3 and the decision is advance: do not mark R10 ready; assign the refreshed mockup/design preflight from DESIGN.md and leave R10-R12 blocked until Matt approves the refreshed mockups
docs/03-decisions.md:215:**Context.** A parallel design audit produced a new direction on `codex/design-vision-2026-05-11`: deep navy instrument chassis plus paper-white evidence table, with the rule "The brand leads once. Then the product speaks." The reset is still in RG3, and RG4 UI work remains blocked until the data-quality gate advances.
docs/03-decisions.md:217:**Decision.** Add `DESIGN.md` as the future visual direction authority for RG4, but treat it as planning input only. The May 10 mockup remains the product-structure reference, not the final visual direction. If RG3 advances, the next assignment is a refreshed mockup/design preflight from `DESIGN.md`, not production R10 implementation. R10-R12 stay blocked until Matt approves the refreshed mockups. The rabbit/icon problem remains quarantined until an approved vector exists.
docs/03-decisions.md:219:**Consequences.** Design direction can be reviewed and used to brief future mockup agents without contaminating RG3 evidence or unlocking UI work early. Prompt C for RG3 must cite `DESIGN.md` only as future RG4 input. Prompt A/B agents must not implement a new visual system, production logo, or RG4 UI until the reset plan explicitly marks that work ready after mockup approval.
STATUS.md:11:**Next pointer:** Prompt C should audit RG3 - Validation, Conflict, And Gate Semantics. R09 is merged to `rebuild/validated-leads-loop`. Do not unlock RG4 or sync `main` unless Prompt C records an advance and Matt explicitly asks for an operator-use promotion.
STATUS.md:13:**Design direction handoff:** `DESIGN.md` is now captured as the future RG4 visual direction authority. It does not unlock RG4. If RG3 Prompt C advances, the next assignment is a refreshed mockup/design preflight from `DESIGN.md`, not production R10 code. R10-R12 remain blocked until Matt approves refreshed mockups.
STATUS.md:27:**Next feature pointer:** None. R09 is the final RG3 feature and is merged; RG3 is ready for Prompt C audit. Do not unlock RG4 or sync `main`.
STATUS.md:31:**Final product mockup gate:** `DESIGN.md` is the future RG4 visual direction authority, while `docs/mockups/final-product-2026-05-10/index.html` remains the product-structure reference. Before R10 starts, a design/mockup agent must produce refreshed Empty, Loading, Results, Evidence Review, Low Signal, and Mobile Review mockups from `DESIGN.md`; Matt must approve those mockups before production UI implementation.
STATUS.md:33:**Current feature branch QA status:** R07, R08, and R09 are merged to `rebuild/validated-leads-loop`. RG3 is ready for Prompt C audit.
STATUS.md:45:**Latest reset control doc:** `docs/12-reset-gated-implementation-plan-2026-05-10.md` defines reset gates RG0-RG6. Every gate requires a full evaluation/audit report before downstream gate work unlocks. RG0 is advanced via `audits/gates/reset-2026-05-10/rg0-w5-hold.md`; RG1 is advanced via `audits/gates/reset-2026-05-10/rg1-benchmark-harness.md`; RG2 is advanced via `audits/gates/reset-2026-05-10/rg2-search-source-coverage.md`; RG3 is ready for Prompt C audit; and RG4 remains blocked.
STATUS.md:59:- `DESIGN.md` is the future RG4 visual direction authority; it is not production UI implementation and does not unlock RG4 by itself.
STATUS.md:71:Feature: R09 - Tier summary, score semantics, and reason language reset
STATUS.md:74:What changed: Prompt A implemented R09 only, and Prompt B verified it. Core score semantics now cap evidence/contact signals after validation so unsupported fields and missing/failed contacts cannot retain strong-looking evidence/contact values. The reason language now starts with READY/REVIEW operator states and avoids old score-pass phrasing. Web result types now include `tier`, `primary_filter_reason`, and `metrics.tier_distribution`; the results view shows a tier summary and uses readiness/signal labels instead of score/gate-centric copy.
STATUS.md:82:Screenshots or report: `.gstack/qa-reports/qa-report-r09-tier-summary-semantics-2026-05-11.md`, `.gstack/qa-reports/screenshots/r09-prompt-b-desktop.png`, and `.gstack/qa-reports/screenshots/r09-prompt-b-mobile.png`. No UI redesign, RG4 work, export rewrite, or `main` sync was done.
STATUS.md:83:Northstar reflection: R09 reduces false confidence by making READY depend on validation-backed tiering while keeping review, organization-only, not-found, and failed rows visible with explicit reasons and tier counts.
STATUS.md:84:Exact Prompt C handoff: Audit RG3 - Validation, Conflict, And Gate Semantics on `rebuild/validated-leads-loop`. Confirm R07-R09 are merged, run the RG3 full evaluation/audit from `docs/12-reset-gated-implementation-plan-2026-05-10.md`, and write `audits/gates/reset-2026-05-10/rg3-validation-semantics.md`. Do not unlock RG4 unless Prompt C records an `advance`; do not sync `main`.
STATUS.md:85:Next pointer: Prompt C for RG3.
STATUS.md:90:Artifact: `DESIGN.md`
STATUS.md:93:What changed: Captured the May 11 design direction as future RG4 input only: deep navy instrument chassis, paper-white evidence table, brand leads once then product speaks, and rabbit/icon quarantine until an approved vector exists. Updated the reset plan and ADRs so RG3 Prompt C cites `DESIGN.md` as future RG4 input, and RG4 requires refreshed mockups plus Matt approval before R10 can start.
STATUS.md:95:Next design pointer: If RG3 Prompt C advances, hand the refreshed-mockup prompt from the final response to a design/mockup agent before assigning R10.
STATUS.md:99:Feature: R08 - Tiering engine, field validator, and conflict resolver
STATUS.md:102:What changed: Prompt A implemented R08 only, and Prompt B verified it. Candidates now carry server-computed `tier` and `primary_filter_reason`; person rows can become `high_trust_usable`, `review`, or explicit `failed` rows after validation; inaccessible sources and failed core field validation downgrade unsafe person rows to `FailedCandidate`; person/account conflicts are flagged and downgraded; validated contact status is synchronized back onto person rows so unsupported, missing, or failed contact evidence cannot remain CRM-ready; and run metrics now expose `tier_distribution`.
STATUS.md:108:Northstar reflection: R08 keeps the binary evidence gate as the only `high_trust_usable` path while keeping review/org-only/not-found/failed rows visible with grounded primary reasons. It reduces false confidence by preventing unsupported contact evidence and inaccessible sources from appearing CRM-ready.
STATUS.md:109:Exact Prompt A handoff: Implement R09 on `feat/reset-r09-tier-summary-semantics`. Keep scope to tier summary, score semantics, and reason language reset; do not start RG4, do not unlock the next gate, and do not touch `main`.
STATUS.md:110:Next pointer: Prompt A for R09.
STATUS.md:111:Open questions: None for R09 kickoff; RG3 still requires R09 and Prompt C audit before any gate advancement.
STATUS.md:260:- Product is in audit-red state. Documentation authority remediation is complete; F01-F19 are merged to `rebuild/validated-leads-loop`, but the May 10 audit found the visible loop still fails live operator benchmarks. W2, W3, and W4 are orchestrator-accepted. R00-R09 are merged; RG2 advanced as a search/source coverage gate; RG3 is ready for Prompt C audit; W5 remains held; W6 remains blocked.
STATUS.md:264:- Run Prompt C for RG3 - Validation, Conflict, And Gate Semantics on `rebuild/validated-leads-loop`. Do not unlock RG4 or sync `main`.
STATUS.md:309:| 2026-05-11 | design-direction-fold-in (Codex) | Folded `DESIGN.md` from `codex/design-vision-2026-05-11` into the reset control plane as future RG4 visual direction only. Added ADR-015 and updated `docs/12` so RG3 Prompt C cites the design doc as future RG4 input, but R10-R12 stay blocked until a refreshed mockup pass is approved by Matt. |
STATUS.md:310:| 2026-05-11 | prompt-b-r09-qa (Codex) | QA-passed `R09 - Tier summary, score semantics, and reason language reset` on `feat/reset-r09-tier-summary-semantics`: verified `git diff --check`, the required core/API suite, web tests/build, browser fixture screenshots, northstar drift, and that no R10-R14, RG4, export, persistence, or `main` work landed. Report saved at `.gstack/qa-reports/qa-report-r09-tier-summary-semantics-2026-05-11.md`. R09 is the last RG3 feature, so RG3 is ready for Prompt C audit after merge; RG4 remains blocked. |
STATUS.md:311:| 2026-05-11 | prompt-a-r09-implementation (Codex) | Implemented `R09 - Tier summary, score semantics, and reason language reset` on `feat/reset-r09-tier-summary-semantics`: capped evidence/contact signals from field validation, reset READY/REVIEW primary reason language, typed web tier metadata, and added tier distribution summary/copy updates without starting RG4 UI work. Verified required core/API/web tests and `git diff --check`; branch is pending Prompt B QA and merge. |
STATUS.md:312:| 2026-05-11 | prompt-b-r08-qa (Codex) | QA-passed `R08 - Tiering engine, field validator, and conflict resolver` on `feat/reset-r08-tier-validation-conflicts`: verified `git diff --check`, the required core validation/contact/scoring/orchestrator suite, full API tests, non-UI scope, northstar drift, and that no R09 score-language, UI, export, persistence, or gate-audit work landed. Report saved at `.gstack/qa-reports/qa-report-r08-tier-validation-conflicts-2026-05-11.md`. R09 is the next same-gate feature; RG4 remains blocked. |
STATUS.md:313:| 2026-05-11 | prompt-a-r08 (Codex) | Implemented `R08 - Tiering engine, field validator, and conflict resolver` on `feat/reset-r08-tier-validation-conflicts`: added server-computed candidate tiers and primary filter reasons, synchronized contact status from field validation, downgraded inaccessible-source and person/account conflict rows to explicit failed candidates, and exposed run-level tier distribution metrics. Verified the required R08 core suite, full API tests, and `git diff --check`; branch is pending Prompt B QA and merge. |
STATUS.md:314:| 2026-05-11 | prompt-b-r07-qa (Codex) | QA-passed `R07 - Inclusive extraction prompt and candidate parse salvage` on `feat/reset-r07-inclusive-extraction`: verified `git diff --check`, the required core extraction/scoring/source-validation suite, full API tests, non-UI scope, northstar drift, and that no R08/R09 tier/conflict/score-language work landed. Report saved at `.gstack/qa-reports/qa-report-r07-inclusive-extraction-2026-05-11.md`. R08 is the next same-gate feature after the R07 merge lands; RG4 remains blocked. |
STATUS.md:315:| 2026-05-11 | prompt-c-rg2-audit (Codex) | Ran the RG2 search/source coverage gate audit on `audit/reset-rg2-search-source-coverage`: live Scout/Full benchmarks plus direct source snapshots showed all 8 Thomas Arizona K-12 accounts represented and 73-90 deduped raw sources for broad prompts, while final product output remains low-volume with 0 high-trust usable rows. RG2 advanced as a source-coverage gate, product remains red, and R07 is now the next ready Prompt A feature. |
STATUS.md:316:| 2026-05-11 | prompt-b-r06-qa (Codex) | QA-passed `R06 - Not-found and organization-only coverage writer` on `feat/reset-r06-nonperson-coverage`: verified the required RG2 core suite, `git diff --check`, focused coverage/orchestrator regressions, northstar drift, and scope boundaries. Report saved at `.gstack/qa-reports/qa-report-r06-nonperson-coverage-2026-05-11.md`. R06 is the last RG2 feature, so RG2 is ready for Prompt C audit after merge; RG3 remains blocked. |
STATUS.md:318:| 2026-05-11 | prompt-b-r05-qa (Codex) | QA-passed `R05 - Source collection and snapshot store` on `feat/reset-r05-source-collection-store`: verified the required core test suite, `git diff --check`, raw source fixture integrity, northstar drift, and scope boundaries. Report saved at `.gstack/qa-reports/qa-report-r05-source-collection-store-2026-05-11.md`. R06 is the next same-gate feature after the R05 merge lands; RG3 remains blocked. |
STATUS.md:332:| 2026-05-10 | final-product-mockups (Codex) | Added `docs/mockups/final-product-2026-05-10/index.html` and rendered screenshots so Matt can inspect the final intended operator product before kickoff. Wired the mockup into the reset plan as the R10-R13 visual contract and RG4/RG5 Prompt C comparison artifact. |

## Core RG3 verification
$ cd packages/core && uv run pytest tests/test_source_validation.py tests/test_contact_status.py tests/test_scoring.py tests/test_orchestrator.py -q
................................................                         [100%]
48 passed in 0.41s

## API verification
$ cd apps/api && WR_API_INTERNAL_TOKEN=test-internal-token uv run pytest tests -q
...........................................                              [100%]
=============================== warnings summary ===============================
tests/test_api.py: 19 warnings
  /Users/mschwar/Documents/white-rabbit/apps/api/api/main.py:280: DeprecationWarning: datetime.datetime.utcnow() is deprecated and scheduled for removal in a future version. Use timezone-aware objects to represent datetimes in UTC: datetime.datetime.now(datetime.UTC).
    state.updated_at = datetime.utcnow()

tests/test_api.py: 10 warnings
  /Users/mschwar/Documents/white-rabbit/apps/api/api/db.py:358: DeprecationWarning: datetime.datetime.utcnow() is deprecated and scheduled for removal in a future version. Use timezone-aware objects to represent datetimes in UTC: datetime.datetime.now(datetime.UTC).
    state.updated_at = datetime.utcnow()

tests/test_api.py::test_batch_endpoint_creates_job_and_runs
  /Users/mschwar/Documents/white-rabbit/apps/api/tests/test_api.py:941: DeprecationWarning: datetime.datetime.utcnow() is deprecated and scheduled for removal in a future version. Use timezone-aware objects to represent datetimes in UTC: datetime.datetime.now(datetime.UTC).
    created_at = __import__("datetime").datetime.utcnow()

tests/test_api.py::test_batch_endpoint_creates_job_and_runs
  /Users/mschwar/Documents/white-rabbit/apps/api/tests/test_api.py:942: DeprecationWarning: datetime.datetime.utcnow() is deprecated and scheduled for removal in a future version. Use timezone-aware objects to represent datetimes in UTC: datetime.datetime.now(datetime.UTC).
    started_at = __import__("datetime").datetime.utcnow()

tests/test_api.py::test_batch_endpoint_creates_job_and_runs
  /Users/mschwar/Documents/white-rabbit/apps/api/tests/test_api.py:943: DeprecationWarning: datetime.datetime.utcnow() is deprecated and scheduled for removal in a future version. Use timezone-aware objects to represent datetimes in UTC: datetime.datetime.now(datetime.UTC).
    ended_at = __import__("datetime").datetime.utcnow()

tests/test_api.py::test_batch_endpoint_creates_job_and_runs
  /Users/mschwar/Documents/white-rabbit/apps/api/tests/test_api.py:955: DeprecationWarning: datetime.datetime.utcnow() is deprecated and scheduled for removal in a future version. Use timezone-aware objects to represent datetimes in UTC: datetime.datetime.now(datetime.UTC).
    started_at = __import__("datetime").datetime.utcnow()

tests/test_api.py::test_batch_endpoint_creates_job_and_runs
  /Users/mschwar/Documents/white-rabbit/apps/api/tests/test_api.py:956: DeprecationWarning: datetime.datetime.utcnow() is deprecated and scheduled for removal in a future version. Use timezone-aware objects to represent datetimes in UTC: datetime.datetime.now(datetime.UTC).
    ended_at = __import__("datetime").datetime.utcnow()

tests/test_api.py::test_batch_endpoint_creates_job_and_runs
tests/test_api.py::test_batch_endpoint_respects_caps
  /Users/mschwar/Documents/white-rabbit/apps/api/api/main.py:590: DeprecationWarning: datetime.datetime.utcnow() is deprecated and scheduled for removal in a future version. Use timezone-aware objects to represent datetimes in UTC: datetime.datetime.now(datetime.UTC).
    job.started_at = datetime.utcnow()

tests/test_api.py::test_batch_endpoint_creates_job_and_runs
tests/test_api.py::test_batch_endpoint_creates_job_and_runs
tests/test_api.py::test_batch_endpoint_respects_caps
  /Users/mschwar/Documents/white-rabbit/apps/api/api/main.py:596: DeprecationWarning: datetime.datetime.utcnow() is deprecated and scheduled for removal in a future version. Use timezone-aware objects to represent datetimes in UTC: datetime.datetime.now(datetime.UTC).
    batch_run.started_at = datetime.utcnow()

tests/test_api.py::test_batch_endpoint_creates_job_and_runs
tests/test_api.py::test_batch_endpoint_creates_job_and_runs
  /Users/mschwar/Documents/white-rabbit/apps/api/api/main.py:761: DeprecationWarning: datetime.datetime.utcnow() is deprecated and scheduled for removal in a future version. Use timezone-aware objects to represent datetimes in UTC: datetime.datetime.now(datetime.UTC).
    batch_run.ended_at = datetime.utcnow()

tests/test_api.py::test_batch_endpoint_respects_caps
  /Users/mschwar/Documents/white-rabbit/apps/api/tests/test_api.py:1100: DeprecationWarning: datetime.datetime.utcnow() is deprecated and scheduled for removal in a future version. Use timezone-aware objects to represent datetimes in UTC: datetime.datetime.now(datetime.UTC).
    created_at = __import__("datetime").datetime.utcnow()

tests/test_api.py::test_batch_endpoint_respects_caps
  /Users/mschwar/Documents/white-rabbit/apps/api/tests/test_api.py:1101: DeprecationWarning: datetime.datetime.utcnow() is deprecated and scheduled for removal in a future version. Use timezone-aware objects to represent datetimes in UTC: datetime.datetime.now(datetime.UTC).
    started_at = __import__("datetime").datetime.utcnow()

tests/test_api.py::test_batch_endpoint_respects_caps
  /Users/mschwar/Documents/white-rabbit/apps/api/tests/test_api.py:1102: DeprecationWarning: datetime.datetime.utcnow() is deprecated and scheduled for removal in a future version. Use timezone-aware objects to represent datetimes in UTC: datetime.datetime.now(datetime.UTC).
    ended_at = __import__("datetime").datetime.utcnow()

tests/test_api.py::test_batch_endpoint_respects_caps
  /Users/mschwar/Documents/white-rabbit/apps/api/tests/test_api.py:1114: DeprecationWarning: datetime.datetime.utcnow() is deprecated and scheduled for removal in a future version. Use timezone-aware objects to represent datetimes in UTC: datetime.datetime.now(datetime.UTC).
    started_at = __import__("datetime").datetime.utcnow()

tests/test_api.py::test_batch_endpoint_respects_caps
  /Users/mschwar/Documents/white-rabbit/apps/api/tests/test_api.py:1115: DeprecationWarning: datetime.datetime.utcnow() is deprecated and scheduled for removal in a future version. Use timezone-aware objects to represent datetimes in UTC: datetime.datetime.now(datetime.UTC).
    ended_at = __import__("datetime").datetime.utcnow()

tests/test_api.py::test_batch_endpoint_respects_caps
  /Users/mschwar/Documents/white-rabbit/apps/api/api/main.py:683: DeprecationWarning: datetime.datetime.utcnow() is deprecated and scheduled for removal in a future version. Use timezone-aware objects to represent datetimes in UTC: datetime.datetime.now(datetime.UTC).
    batch_run.ended_at = datetime.utcnow()

tests/test_api.py::test_full_endpoint_returns_persisted_lead_ids
tests/test_api.py::test_full_endpoint_returns_persisted_lead_ids
tests/test_api.py::test_full_endpoint_returns_persisted_lead_ids
  /Users/mschwar/Documents/white-rabbit/apps/api/tests/test_api.py:1243: DeprecationWarning: datetime.datetime.utcnow() is deprecated and scheduled for removal in a future version. Use timezone-aware objects to represent datetimes in UTC: datetime.datetime.now(datetime.UTC).
    reset_at=datetime.utcnow(),

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
43 passed, 50 warnings in 0.70s

## Web score/tier semantics regression
$ cd apps/web && npm test -- --run

> web@0.1.0 test
> vitest run --run


 RUN  v4.1.5 /Users/mschwar/Documents/white-rabbit/apps/web


 Test Files  13 passed (13)
      Tests  30 passed (30)
   Start at  00:43:11
   Duration  2.66s (transform 1.20s, setup 1.11s, import 2.29s, tests 1.97s, environment 9.81s)


## Web build for current operator UI semantics
$ cd apps/web && npm run build

> web@0.1.0 build
> next build

⚠ Warning: Next.js inferred your workspace root, but it may not be correct.
 We detected multiple lockfiles and selected the directory of /Users/mschwar/package-lock.json as the root directory.
 To silence this warning, set `turbopack.root` in your Next.js config, or consider removing one of the lockfiles if it's not needed.
   See https://nextjs.org/docs/app/api-reference/config/next-config-js/turbopack#root-directory for more information.
 Detected additional lockfiles: 
   * /Users/mschwar/Documents/white-rabbit/apps/web/package-lock.json

▲ Next.js 16.2.4 (Turbopack)
- Environments: .env.local, .env.production

⚠ The "middleware" file convention is deprecated. Please use "proxy" instead. Learn more: https://nextjs.org/docs/messages/middleware-to-proxy
  Creating an optimized production build ...
✓ Compiled successfully in 1744ms
  Running TypeScript ...
  Finished TypeScript in 1723ms ...
  Collecting page data using 7 workers ...
  Generating static pages using 7 workers (0/11) ...
  Generating static pages using 7 workers (2/11) 
  Generating static pages using 7 workers (5/11) 
  Generating static pages using 7 workers (8/11) 
✓ Generating static pages using 7 workers (11/11) in 118ms
  Finalizing page optimization ...

Route (app)
┌ ƒ /
├ ○ /_not-found
├ ƒ /api/batch
├ ƒ /api/full
├ ƒ /api/leads/[lead_id]/corrections
├ ƒ /api/leads/[lead_id]/feedback
├ ƒ /api/login
├ ƒ /api/logout
├ ƒ /api/recipes
├ ƒ /api/recipes/[recipe_id]/runs
├ ƒ /api/recipes/[recipe_id]/scoreboard
├ ƒ /api/runs/[run_id]/close
├ ƒ /api/runs/[run_id]/corrections
├ ƒ /api/sandbox
├ ƒ /api/scout
├ ƒ /batch
├ ƒ /login
├ ƒ /recipes
└ ƒ /scout


ƒ Proxy (Middleware)

○  (Static)   prerendered as static content
ƒ  (Dynamic)  server-rendered on demand


## Live environment availability check
OPENAI_API_KEY=set
TAVILY_API_KEY=unset
WR_API_INTERNAL_TOKEN=unset
DATABASE_URL=unset
OPENAI_BASE_URL=set
apps/api/.env presence:
apps/api/.env=present
root .env presence:
.env=absent

## apps/api/.env key presence (names only)
OPENAI_API_KEY=present_in_apps_api_env
TAVILY_API_KEY=present_in_apps_api_env
WR_API_INTERNAL_TOKEN=present_in_apps_api_env
WR_SHARED_PASSWORD=present_in_apps_api_env
WR_SESSION_SECRET=present_in_apps_api_env
OPENAI_BASE_URL=missing_in_apps_api_env
OPENAI_MODEL=missing_in_apps_api_env
DATABASE_URL=missing_in_apps_api_env

## API startup attempt 1 result
Failed: inherited OPENAI_API_KEY value overrode apps/api/.env and preflight rejected it as invalid against api.openai.com. Retrying with OPENAI_API_KEY unset so dotenv can load the repo-local key.

## RG3 live benchmark runner (scout)
$ cd packages/core && uv run python -m core.live_benchmark_runner --api-base-url http://127.0.0.1:8013 --output-dir ../../audits/raw/reset-2026-05-10/rg3/live --mode scout --api-token [redacted]
{
  "api_base_url": "http://127.0.0.1:8013",
  "case_results": [
    {
      "benchmark_id": "thomas-arizona-k12",
      "elapsed_seconds": 63.24,
      "mode": "scout",
      "response_path": "../../audits/raw/reset-2026-05-10/rg3/live/thomas-arizona-k12.json",
      "status_code": 200,
      "status_path": "../../audits/raw/reset-2026-05-10/rg3/live/thomas-arizona-k12.http"
    },
    {
      "benchmark_id": "lee-commodity-buyers",
      "elapsed_seconds": 60.456,
      "mode": "scout",
      "response_path": "../../audits/raw/reset-2026-05-10/rg3/live/lee-commodity-buyers.json",
      "status_code": 200,
      "status_path": "../../audits/raw/reset-2026-05-10/rg3/live/lee-commodity-buyers.http"
    },
    {
      "benchmark_id": "healthcare-it-phoenix",
      "elapsed_seconds": 83.011,
      "mode": "scout",
      "response_path": "../../audits/raw/reset-2026-05-10/rg3/live/healthcare-it-phoenix.json",
      "status_code": 200,
      "status_path": "../../audits/raw/reset-2026-05-10/rg3/live/healthcare-it-phoenix.http"
    },
    {
      "benchmark_id": "finance-cisos-new-york",
      "elapsed_seconds": 69.154,
      "mode": "scout",
      "response_path": "../../audits/raw/reset-2026-05-10/rg3/live/finance-cisos-new-york.json",
      "status_code": 200,
      "status_path": "../../audits/raw/reset-2026-05-10/rg3/live/finance-cisos-new-york.http"
    },
    {
      "benchmark_id": "manufacturing-ops-detroit",
      "elapsed_seconds": 71.914,
      "mode": "scout",
      "response_path": "../../audits/raw/reset-2026-05-10/rg3/live/manufacturing-ops-detroit.json",
      "status_code": 200,
      "status_path": "../../audits/raw/reset-2026-05-10/rg3/live/manufacturing-ops-detroit.http"
    },
    {
      "benchmark_id": "privacy-reject-homeowner-phones",
      "elapsed_seconds": 0.006,
      "mode": "scout",
      "response_path": "../../audits/raw/reset-2026-05-10/rg3/live/privacy-reject-homeowner-phones.json",
      "status_code": 422,
      "status_path": "../../audits/raw/reset-2026-05-10/rg3/live/privacy-reject-homeowner-phones.http"
    }
  ],
  "mode": "scout",
  "output_root": "../../audits/raw/reset-2026-05-10/rg3/live",
  "suite_report": {
    "case_summaries": {
      "finance-cisos-new-york": {
        "categorized_row_count": 7,
        "error_code": null,
        "expected_target_coverage_count": 0,
        "expected_target_coverage_missing": [],
        "failed_count": 3,
        "guardrail_status": "clear",
        "high_trust_usable_count": 0,
        "high_volume_floor_met": false,
        "http_status": 200,
        "not_found_count": 0,
        "organization_only_count": 0,
        "person_lead_count": 4,
        "quality_report": {
          "artifact_id": "finance-cisos-new-york",
          "artifact_kind": "benchmark",
          "candidate_category_counts": {
            "failed": 3,
            "not_found": 0,
            "organization_only": 0,
            "person_lead": 4
          },
          "contact_quality_count": 0,
          "contact_quality_rate": 0.0,
          "failed_count": 3,
          "fake_email_count": 0,
          "high_noise_count": 3,
          "high_noise_rate": 0.429,
          "not_found_count": 0,
          "organization_only_count": 0,
          "person_lead_count": 4,
          "persona_match_count": 4,
          "persona_match_rate": 0.571,
          "precision_rate": 0.0,
          "quality_gate_failures": [
            "zero_usable_candidates",
            "low_precision_rate",
            "low_contact_quality_rate",
            "high_noise_rate"
          ],
          "quality_gate_passed": false,
          "quality_gate_thresholds": {
            "maximum_fake_email_count": 0,
            "maximum_high_noise_rate": 0.4,
            "maximum_unsupported_email_count": 0,
            "minimum_contact_quality_rate": 0.5,
            "minimum_persona_match_rate": 0.5,
            "minimum_precision_rate": 0.5,
            "minimum_source_support_rate": 0.5,
            "minimum_usable_count": 1
          },
          "query": "finance CISOs at financial services firms in New York",
          "source_support_count": 6,
          "source_support_rate": 0.857,
          "total_candidates": 7,
          "unsupported_email_count": 0,
          "usable_count": 0,
          "validation_status_counts": {
            "email": {
              "deduced_with_pattern_evidence": 0,
              "failed": 0,
              "missing": 7,
              "unsupported": 0,
              "verified_found": 0
            },
            "name": {
              "failed": 0,
              "missing": 3,
              "supported": 4,
              "unsupported": 0
            },
            "organization": {
              "failed": 1,
              "missing": 0,
              "supported": 6,
              "unsupported": 0
            },
            "phone": {
              "deduced_with_pattern_evidence": 0,
              "failed": 0,
              "missing": 7,
              "unsupported": 0,
              "verified_found": 0
            },
            "source": {
              "failed": 1,
              "missing": 0,
              "supported": 6,
              "unsupported": 0
            },
            "title": {
              "failed": 0,
              "missing": 3,
              "supported": 4,
              "unsupported": 0
            }
          }
        },
        "review_count": 4
      },
      "healthcare-it-phoenix": {
        "categorized_row_count": 10,
        "error_code": null,
        "expected_target_coverage_count": 0,
        "expected_target_coverage_missing": [],
        "failed_count": 5,
        "guardrail_status": "clear",
        "high_trust_usable_count": 0,
        "high_volume_floor_met": true,
        "http_status": 200,
        "not_found_count": 0,
        "organization_only_count": 2,
        "person_lead_count": 3,
        "quality_report": {
          "artifact_id": "healthcare-it-phoenix",
          "artifact_kind": "benchmark",
          "candidate_category_counts": {
            "failed": 5,
            "not_found": 0,
            "organization_only": 2,
            "person_lead": 3
          },
          "contact_quality_count": 0,
          "contact_quality_rate": 0.0,
          "failed_count": 5,
          "fake_email_count": 0,
          "high_noise_count": 7,
          "high_noise_rate": 0.7,
          "not_found_count": 0,
          "organization_only_count": 2,
          "person_lead_count": 3,
          "persona_match_count": 1,
          "persona_match_rate": 0.1,
          "precision_rate": 0.0,
          "quality_gate_failures": [
            "zero_usable_candidates",
            "low_precision_rate",
            "low_persona_match_rate",
            "low_contact_quality_rate",
            "low_source_support_rate",
            "high_noise_rate"
          ],
          "quality_gate_passed": false,
          "quality_gate_thresholds": {
            "maximum_fake_email_count": 0,
            "maximum_high_noise_rate": 0.4,
            "maximum_unsupported_email_count": 0,
            "minimum_contact_quality_rate": 0.5,
            "minimum_persona_match_rate": 0.5,
            "minimum_precision_rate": 0.5,
            "minimum_source_support_rate": 0.5,
            "minimum_usable_count": 1
          },
          "query": "healthcare IT directors in Phoenix",
          "source_support_count": 4,
          "source_support_rate": 0.4,
          "total_candidates": 10,
          "unsupported_email_count": 0,
          "usable_count": 0,
          "validation_status_counts": {
            "email": {
              "deduced_with_pattern_evidence": 0,
              "failed": 0,
              "missing": 10,
              "unsupported": 0,
              "verified_found": 0
            },
            "name": {
              "failed": 5,
              "missing": 2,
              "supported": 3,
              "unsupported": 0
            },
            "organization": {
              "failed": 5,
              "missing": 0,
              "supported": 4,
              "unsupported": 1
            },
            "phone": {
              "deduced_with_pattern_evidence": 0,
              "failed": 0,
              "missing": 10,
              "unsupported": 0,
              "verified_found": 0
            },
            "source": {
              "failed": 5,
              "missing": 0,
              "supported": 4,
              "unsupported": 1
            },
            "title": {
              "failed": 5,
              "missing": 2,
              "supported": 1,
              "unsupported": 2
            }
          }
        },
        "review_count": 3
      },
      "lee-commodity-buyers": {
        "categorized_row_count": 7,
        "error_code": null,
        "expected_target_coverage_count": 0,
        "expected_target_coverage_missing": [],
        "failed_count": 5,
        "guardrail_status": "needs_more_detail",
        "high_trust_usable_count": 0,
        "high_volume_floor_met": false,
        "http_status": 200,
        "not_found_count": 0,
        "organization_only_count": 1,
        "person_lead_count": 1,
        "quality_report": {
          "artifact_id": "lee-commodity-buyers",
          "artifact_kind": "benchmark",
          "candidate_category_counts": {
            "failed": 5,
            "not_found": 0,
            "organization_only": 1,
            "person_lead": 1
          },
          "contact_quality_count": 0,
          "contact_quality_rate": 0.0,
          "failed_count": 5,
          "fake_email_count": 0,
          "high_noise_count": 7,
          "high_noise_rate": 1.0,
          "not_found_count": 0,
          "organization_only_count": 1,
          "person_lead_count": 1,
          "persona_match_count": 1,
          "persona_match_rate": 0.143,
          "precision_rate": 0.0,
          "quality_gate_failures": [
            "zero_usable_candidates",
            "low_precision_rate",
            "low_persona_match_rate",
            "low_contact_quality_rate",
            "low_source_support_rate",
            "unsupported_emails_present",
            "high_noise_rate"
          ],
          "quality_gate_passed": false,
          "quality_gate_thresholds": {
            "maximum_fake_email_count": 0,
            "maximum_high_noise_rate": 0.4,
            "maximum_unsupported_email_count": 0,
            "minimum_contact_quality_rate": 0.5,
            "minimum_persona_match_rate": 0.5,
            "minimum_precision_rate": 0.5,
            "minimum_source_support_rate": 0.5,
            "minimum_usable_count": 1
          },
          "query": "commodity buyers at retail lumber yards in Washington",
          "source_support_count": 1,
          "source_support_rate": 0.143,
          "total_candidates": 7,
          "unsupported_email_count": 1,
          "usable_count": 0,
          "validation_status_counts": {
            "email": {
              "deduced_with_pattern_evidence": 0,
              "failed": 0,
              "missing": 6,
              "unsupported": 1,
              "verified_found": 0
            },
            "name": {
              "failed": 4,
              "missing": 2,
              "supported": 1,
              "unsupported": 0
            },
            "organization": {
              "failed": 6,
              "missing": 0,
              "supported": 1,
              "unsupported": 0
            },
            "phone": {
              "deduced_with_pattern_evidence": 0,
              "failed": 0,
              "missing": 7,
              "unsupported": 0,
              "verified_found": 0
            },
            "source": {
              "failed": 6,
              "missing": 0,
              "supported": 1,
              "unsupported": 0
            },
            "title": {
              "failed": 4,
              "missing": 2,
              "supported": 1,
              "unsupported": 0
            }
          }
        },
        "review_count": 1
      },
      "manufacturing-ops-detroit": {
        "categorized_row_count": 8,
        "error_code": null,
        "expected_target_coverage_count": 0,
        "expected_target_coverage_missing": [],
        "failed_count": 3,
        "guardrail_status": "clear",
        "high_trust_usable_count": 0,
        "high_volume_floor_met": false,
        "http_status": 200,
        "not_found_count": 2,
        "organization_only_count": 1,
        "person_lead_count": 2,
        "quality_report": {
          "artifact_id": "manufacturing-ops-detroit",
          "artifact_kind": "benchmark",
          "candidate_category_counts": {
            "failed": 3,
            "not_found": 2,
            "organization_only": 1,
            "person_lead": 2
          },
          "contact_quality_count": 0,
          "contact_quality_rate": 0.0,
          "failed_count": 3,
          "fake_email_count": 0,
          "high_noise_count": 4,
          "high_noise_rate": 0.5,
          "not_found_count": 2,
          "organization_only_count": 1,
          "person_lead_count": 2,
          "persona_match_count": 1,
          "persona_match_rate": 0.125,
          "precision_rate": 0.0,
          "quality_gate_failures": [
            "zero_usable_candidates",
            "low_precision_rate",
            "low_persona_match_rate",
            "low_contact_quality_rate",
            "low_source_support_rate",
            "high_noise_rate"
          ],
          "quality_gate_passed": false,
          "quality_gate_thresholds": {
            "maximum_fake_email_count": 0,
            "maximum_high_noise_rate": 0.4,
            "maximum_unsupported_email_count": 0,
            "minimum_contact_quality_rate": 0.5,
            "minimum_persona_match_rate": 0.5,
            "minimum_precision_rate": 0.5,
            "minimum_source_support_rate": 0.5,
            "minimum_usable_count": 1
          },
          "query": "manufacturing operations leaders in Detroit",
          "source_support_count": 3,
          "source_support_rate": 0.375,
          "total_candidates": 8,
          "unsupported_email_count": 0,
          "usable_count": 0,
          "validation_status_counts": {
            "email": {
              "deduced_with_pattern_evidence": 0,
              "failed": 0,
              "missing": 8,
              "unsupported": 0,
              "verified_found": 0
            },
            "name": {
              "failed": 2,
              "missing": 4,
              "supported": 2,
              "unsupported": 0
            },
            "organization": {
              "failed": 4,
              "missing": 1,
              "supported": 2,
              "unsupported": 1
            },
            "phone": {
              "deduced_with_pattern_evidence": 0,
              "failed": 0,
              "missing": 8,
              "unsupported": 0,
              "verified_found": 0
            },
            "source": {
              "failed": 4,
              "missing": 1,
              "supported": 3,
              "unsupported": 0
            },
            "title": {
              "failed": 2,
              "missing": 4,
              "supported": 2,
              "unsupported": 0
            }
          }
        },
        "review_count": 2
      },
      "privacy-reject-homeowner-phones": {
        "categorized_row_count": 0,
        "error_code": null,
        "expected_target_coverage_count": 0,
        "expected_target_coverage_missing": [],
        "failed_count": 0,
        "guardrail_status": "blocked",
        "high_trust_usable_count": 0,
        "high_volume_floor_met": true,
        "http_status": 422,
        "not_found_count": 0,
        "organization_only_count": 0,
        "person_lead_count": 0,
        "quality_report": {
          "artifact_id": "privacy-reject-homeowner-phones",
          "artifact_kind": "benchmark",
          "candidate_category_counts": {
            "failed": 0,
            "not_found": 0,
            "organization_only": 0,
            "person_lead": 0
          },
          "contact_quality_count": 0,
          "contact_quality_rate": 0.0,
          "failed_count": 0,
          "fake_email_count": 0,
          "high_noise_count": 0,
          "high_noise_rate": 0.0,
          "not_found_count": 0,
          "organization_only_count": 0,
          "person_lead_count": 0,
          "persona_match_count": 0,
          "persona_match_rate": 0.0,
          "precision_rate": 0.0,
          "quality_gate_failures": [
            "no_candidates",
            "zero_usable_candidates",
            "low_precision_rate",
            "low_persona_match_rate",
            "low_contact_quality_rate",
            "low_source_support_rate"
          ],
          "quality_gate_passed": false,
          "quality_gate_thresholds": {
            "maximum_fake_email_count": 0,
            "maximum_high_noise_rate": 0.4,
            "maximum_unsupported_email_count": 0,
            "minimum_contact_quality_rate": 0.5,
            "minimum_persona_match_rate": 0.5,
            "minimum_precision_rate": 0.5,
            "minimum_source_support_rate": 0.5,
            "minimum_usable_count": 1
          },
          "query": "personal phone numbers for homeowners in Texas",
          "source_support_count": 0,
          "source_support_rate": 0.0,
          "total_candidates": 0,
          "unsupported_email_count": 0,
          "usable_count": 0,
          "validation_status_counts": {
            "email": {
              "deduced_with_pattern_evidence": 0,
              "failed": 0,
              "missing": 0,
              "unsupported": 0,
              "verified_found": 0
            },
            "name": {
              "failed": 0,
              "missing": 0,
              "supported": 0,
              "unsupported": 0
            },
            "organization": {
              "failed": 0,
              "missing": 0,
              "supported": 0,
              "unsupported": 0
            },
            "phone": {
              "deduced_with_pattern_evidence": 0,
              "failed": 0,
              "missing": 0,
              "unsupported": 0,
              "verified_found": 0
            },
            "source": {
              "failed": 0,
              "missing": 0,
              "supported": 0,
              "unsupported": 0
            },
            "title": {
              "failed": 0,
              "missing": 0,
              "supported": 0,
              "unsupported": 0
            }
          }
        },
        "review_count": 0
      },
      "thomas-arizona-k12": {
        "categorized_row_count": 9,
        "error_code": null,
        "expected_target_coverage_count": 8,
        "expected_target_coverage_missing": [],
        "failed_count": 4,
        "guardrail_status": "needs_more_detail",
        "high_trust_usable_count": 0,
        "high_volume_floor_met": true,
        "http_status": 200,
        "not_found_count": 0,
        "organization_only_count": 3,
        "person_lead_count": 2,
        "quality_report": {
          "artifact_id": "thomas-arizona-k12",
          "artifact_kind": "benchmark",
          "candidate_category_counts": {
            "failed": 4,
            "not_found": 0,
            "organization_only": 3,
            "person_lead": 2
          },
          "contact_quality_count": 0,
          "contact_quality_rate": 0.0,
          "failed_count": 4,
          "fake_email_count": 0,
          "high_noise_count": 8,
          "high_noise_rate": 0.889,
          "not_found_count": 0,
          "organization_only_count": 3,
          "person_lead_count": 2,
          "persona_match_count": 2,
          "persona_match_rate": 0.222,
          "precision_rate": 0.0,
          "quality_gate_failures": [
            "zero_usable_candidates",
            "low_precision_rate",
            "low_persona_match_rate",
            "low_contact_quality_rate",
            "unsupported_emails_present",
            "high_noise_rate"
          ],
          "quality_gate_passed": false,
          "quality_gate_thresholds": {
            "maximum_fake_email_count": 0,
            "maximum_high_noise_rate": 0.4,
            "maximum_unsupported_email_count": 0,
            "minimum_contact_quality_rate": 0.5,
            "minimum_persona_match_rate": 0.5,
            "minimum_precision_rate": 0.5,
            "minimum_source_support_rate": 0.5,
            "minimum_usable_count": 1
          },
          "query": "name and email and phone number for these District Approx Size Tech Decision Maker Type Mesa Public Schools 60k+ students CIO / Director of Technology; Chandler Unified School District 40k+ CTO / IT Director; Peoria Unified School District 35k+ Technology Services; Gilbert Public Schools 30k+ CTO; Deer Valley Unified School District 30k+ IT leadership; Paradise Valley Unified School District 25k+ CIO/Technology; Dysart Unified School District 24k+ Director of Technology; Maricopa Unified School District 9k+ Director of Technology",
          "source_support_count": 5,
          "source_support_rate": 0.556,
          "total_candidates": 9,
          "unsupported_email_count": 1,
          "usable_count": 0,
          "validation_status_counts": {
            "email": {
              "deduced_with_pattern_evidence": 0,
              "failed": 0,
              "missing": 8,
              "unsupported": 1,
              "verified_found": 0
            },
            "name": {
              "failed": 4,
              "missing": 3,
              "supported": 2,
              "unsupported": 0
            },
            "organization": {
              "failed": 4,
              "missing": 0,
              "supported": 5,
              "unsupported": 0
            },
            "phone": {
              "deduced_with_pattern_evidence": 0,
              "failed": 0,
              "missing": 9,
              "unsupported": 0,
              "verified_found": 0
            },
            "source": {
              "failed": 4,
              "missing": 0,
              "supported": 5,
              "unsupported": 0
            },
            "title": {
              "failed": 4,
              "missing": 3,
              "supported": 2,
              "unsupported": 0
            }
          }
        },
        "review_count": 2
      }
    },
    "contact_pass_cases": 0,
    "failed_cases": 5,
    "guardrail_mismatches": [],
    "observation_mismatches": [
      "thomas-arizona-k12: source",
      "lee-commodity-buyers: volume",
      "healthcare-it-phoenix: persona, contact, source",
      "finance-cisos-new-york: contact, volume",
      "manufacturing-ops-detroit: persona, contact, source, volume"
    ],
    "passed_cases": 1,
    "persona_pass_cases": 1,
    "privacy_refusal_cases": 1,
    "source_pass_cases": 2,
    "suite_id": "required_lead_quality_suite",
    "total_cases": 6
  }
}

## RG3 evidence extraction
$ jq ... > audits/raw/reset-2026-05-10/rg3/person-row-sample.json
$ jq ... > audits/raw/reset-2026-05-10/rg3/failed-row-sample.json
$ jq ... > audits/raw/reset-2026-05-10/rg3/live/manufacturing-inspection.json

## Final git diff check
$ git diff --check

## Final status before commit
## audit/reset-rg3-validation-semantics
 M STATUS.md
 M docs/12-reset-gated-implementation-plan-2026-05-10.md
?? audits/gates/reset-2026-05-10/rg3-validation-semantics.md
?? audits/raw/reset-2026-05-10/rg3/

## Final post-doc-update diff check
$ git diff --check

## Final post-doc-update status
## audit/reset-rg3-validation-semantics
 M STATUS.md
 M docs/12-reset-gated-implementation-plan-2026-05-10.md
?? audits/gates/reset-2026-05-10/rg3-validation-semantics.md
?? audits/raw/reset-2026-05-10/rg3/
