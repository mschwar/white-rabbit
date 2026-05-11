# RG3 R09C Re-audit Command Output

Date: Mon May 11 08:41:18 MDT 2026

## Branch and Worktree

Command: git status --short --branch

## audit/reset-rg3-validation-semantics-r09c
?? audits/raw/reset-2026-05-10/rg3/command-output-r09c-reaudit.md

Command: git rev-parse --short HEAD && git rev-parse --short origin/rebuild/validated-leads-loop

df9e831
df9e831

## RG3 Feature Merge Ancestry

Command: git merge-base --is-ancestor for R07-R09C feature refs

origin/feat/reset-r07-inclusive-extraction merged
origin/feat/reset-r08-tier-validation-conflicts merged
origin/feat/reset-r09-tier-summary-semantics merged
origin/feat/reset-r09a-live-value-recovery merged
origin/feat/reset-r09b-contact-evidence-acquisition merged
origin/feat/reset-r09c-deep-multisource-evidence-tier-calibration merged

## Current Gate State

Command: rg -n "Current reset gate|RG3|R09C|gate_advanced|Next Prompt A|Current Prompt C handoff" STATUS.md docs/12-reset-gated-implementation-plan-2026-05-10.md

docs/12-reset-gated-implementation-plan-2026-05-10.md:8:**Current reset gate:** RG3 - Validation, Conflict, And Gate Semantics, in_progress / gate_hold. R09B and R09C are now merged to `rebuild/validated-leads-loop`; RG3 remains held until a fresh Prompt C re-audits the gate.
docs/12-reset-gated-implementation-plan-2026-05-10.md:9:**Next Prompt A feature:** None. No new feature is ready while RG3 awaits Prompt C.
docs/12-reset-gated-implementation-plan-2026-05-10.md:10:**Current Prompt B handoff:** None. R09C Prompt B QA is complete and merged to `rebuild/validated-leads-loop`.
docs/12-reset-gated-implementation-plan-2026-05-10.md:11:**Current Prompt C handoff:** Audit RG3 - Validation, Conflict, And Gate Semantics on `rebuild/validated-leads-loop`. Confirm R07-R09C are merged, run the RG3 full evaluation/audit below, and update `audits/gates/reset-2026-05-10/rg3-validation-semantics.md`. Do not unlock RG4, refreshed mockups, R10-R12, R13-R15, export work, dogfood, or `main` unless Prompt C records `advance`.
docs/12-reset-gated-implementation-plan-2026-05-10.md:139:A refreshed RG4 design preflight artifact exists on `codex/rg4-design-preflight-2026-05-11` at commit `5c5a10f` with six mockup screens. It remains an unmerged inspection artifact while RG3 is held. It does not unlock RG4, R10, export, or production UI work, and it must be rechecked against the final data-quality state if RG3 later advances.
docs/12-reset-gated-implementation-plan-2026-05-10.md:141:If RG3 Prompt C records `advance`, it must not mark R10 ready directly. Instead, it must assign a refreshed mockup/design preflight using `DESIGN.md`. That mockup pass must produce Empty, Loading, Results, Evidence Review, Low Signal, and Mobile Review artifacts for Matt inspection. R10-R12 remain blocked until Matt approves the refreshed mockups.
docs/12-reset-gated-implementation-plan-2026-05-10.md:189:| RG0 | W5 Hold And Control Reset | R00 | gate_advanced | `audits/gates/reset-2026-05-10/rg0-w5-hold.md` |
docs/12-reset-gated-implementation-plan-2026-05-10.md:190:| RG1 | Operator Benchmark Harness | R01-R03 | gate_advanced | `audits/gates/reset-2026-05-10/rg1-benchmark-harness.md` |
docs/12-reset-gated-implementation-plan-2026-05-10.md:191:| RG2 | Search Coverage And Source Collection | R04-R06 | gate_advanced | `audits/gates/reset-2026-05-10/rg2-search-source-coverage.md` |
docs/12-reset-gated-implementation-plan-2026-05-10.md:192:| RG3 | Validation, Conflict, And Gate Semantics | R07-R09C | in_progress / gate_hold | `audits/gates/reset-2026-05-10/rg3-validation-semantics.md` |
docs/12-reset-gated-implementation-plan-2026-05-10.md:213:| R09C | Deep multi-source evidence acquisition and tier calibration | merged_to_rebuild_branch | `feat/reset-r09c-deep-multisource-evidence-tier-calibration` | core/API + live/replay evidence/tier calibration artifacts |
docs/12-reset-gated-implementation-plan-2026-05-10.md:346:## RG3 - Validation, Conflict, And Gate Semantics
docs/12-reset-gated-implementation-plan-2026-05-10.md:355:- R09C - Deep multi-source evidence acquisition and tier calibration.
docs/12-reset-gated-implementation-plan-2026-05-10.md:381:RG3 Prompt C recorded `hold` on 2026-05-11. Matt accepted the hold state instead of treating it as a queue blocker. R09A is the only valid remediation feature before RG3 can be re-audited. It must not start RG4, mockups, R10, export polish, persistence, dogfood, or a `main` sync.
docs/12-reset-gated-implementation-plan-2026-05-10.md:387:- Diagnose and repair the source-to-candidate-to-tier choke point that caused RG3 live runs to return only 7-10 categorized rows despite the high-volume source path. Do not satisfy this by lowering the `high_trust_usable` gate or inventing contacts.
docs/12-reset-gated-implementation-plan-2026-05-10.md:415:- Prompt B evidence summary: broad live cases now return 50 categorized rows and privacy refusal is handled as expected, but high-trust usable rows and contact-quality passes remain `0` across the live suite. This is enough to merge R09A as a remediation/diagnostic slice, not enough to advance RG3 without Prompt C.
docs/12-reset-gated-implementation-plan-2026-05-10.md:416:- Exact Prompt C handoff: Audit RG3 - Validation, Conflict, And Gate Semantics on `rebuild/validated-leads-loop`. Confirm R07-R09A are merged, run the RG3 full evaluation/audit below, and write/update `audits/gates/reset-2026-05-10/rg3-validation-semantics.md`. Do not unlock RG4, refreshed mockups, export work, dogfood, `main`, or downstream readiness unless Prompt C records an `advance`.
docs/12-reset-gated-implementation-plan-2026-05-10.md:424:- Reason: R09A recovered broad categorized volume and funnel observability, but every evaluated live benchmark still has `0` high-trust usable rows and `0` contact-quality passes. The current Prompt C re-run also timed out after the first live case, so RG3 cannot claim fresh full-suite runtime reliability.
docs/12-reset-gated-implementation-plan-2026-05-10.md:468:- Exact Prompt B handoff: QA `feat/reset-r09b-contact-evidence-acquisition`; verify the branch contains only R09B scope, rerun the required R09B core/API suites plus `git diff --check`, inspect `audits/raw/reset-2026-05-10/r09b/replay/quality-summary.json`, confirm no unsupported/missing/inaccessible/guessed contacts become CRM-ready, confirm direct email and explicit domain-pattern evidence are the only promotion paths, confirm READY blockers are reported for missing-contact and organization-only rows, confirm runner timeouts produce partial artifacts, and confirm no RG4/UI/export/main-sync scope creep landed. If QA passes, merge only to `rebuild/validated-leads-loop` and hand off Prompt C for RG3 re-audit; do not unlock RG4 from feature QA alone.
docs/12-reset-gated-implementation-plan-2026-05-10.md:470:Accepted post-R09B hold extension and R09C remediation:
docs/12-reset-gated-implementation-plan-2026-05-10.md:472:R09B completed the first contact/evidence remediation pass, but Matt directed that RG3 must remain `in_progress / gate_hold` and must not run Prompt C yet. R09B + R09C together now define the accepted RG3 remediation slice. R09C exists to materially improve contact quality and tier usefulness on promising review rows without relaxing the `high_trust_usable` definition.
docs/12-reset-gated-implementation-plan-2026-05-10.md:474:R09C scope:
docs/12-reset-gated-implementation-plan-2026-05-10.md:482:R09C non-goals:
docs/12-reset-gated-implementation-plan-2026-05-10.md:489:R09C required verification:
docs/12-reset-gated-implementation-plan-2026-05-10.md:497:R09C expected evidence:
docs/12-reset-gated-implementation-plan-2026-05-10.md:504:R09C Prompt A implementation handoff:
docs/12-reset-gated-implementation-plan-2026-05-10.md:509:- Prompt A verification: required R09C core suite (`76 passed`); API suite (`45 passed`, existing datetime deprecation warnings); integration marker run (`6 skipped`, no live integration credentials used); `git diff --check` passed.
docs/12-reset-gated-implementation-plan-2026-05-10.md:511:- Exact Prompt B handoff: QA `feat/reset-r09c-deep-multisource-evidence-tier-calibration`; verify the branch contains only R09C scope, rerun the required R09C core/API suites plus `git diff --check`, inspect the R09C replay artifacts, confirm missing/unsupported/inaccessible/conflicting/guessed contacts do not become CRM-ready, confirm contact-quality counts do not include failed/non-person rows, confirm theme-level benchmark summaries expose contact acquisition success and high-trust yield, and confirm no RG4/UI/export/persistence/dogfood/main-sync scope landed. If QA passes, merge only to `rebuild/validated-leads-loop`; keep RG3 in `in_progress / gate_hold` and hand off a future RG3 Prompt C only after confirming both R09B and R09C are merged. Do not unlock RG4, refreshed mockups, R10-R12, R13-R15, export work, or `main` from feature QA alone.
docs/12-reset-gated-implementation-plan-2026-05-10.md:513:- Prompt B verification: required R09C core suite (`76 passed`), API suite (`45 passed`, existing datetime warnings), `git diff --check`, and replay artifact inspection for `audits/raw/reset-2026-05-10/r09c/replay/deep-contact-evidence-pass.json` plus `quality-summary.json`.
docs/12-reset-gated-implementation-plan-2026-05-10.md:515:- Exact Prompt C handoff: Audit RG3 - Validation, Conflict, And Gate Semantics on `rebuild/validated-leads-loop`. Confirm R07-R09C are merged, run the RG3 full evaluation/audit below, and update `audits/gates/reset-2026-05-10/rg3-validation-semantics.md`. Do not unlock RG4, refreshed mockups, R10-R12, R13-R15, export work, dogfood, or `main` unless Prompt C records `advance`.
docs/12-reset-gated-implementation-plan-2026-05-10.md:517:R09C Prompt A draft for final instruction fill-in:
docs/12-reset-gated-implementation-plan-2026-05-10.md:535:- confirm it is `R09C - Deep multi-source evidence acquisition and tier calibration`
docs/12-reset-gated-implementation-plan-2026-05-10.md:540:Implement only R09C:
docs/12-reset-gated-implementation-plan-2026-05-10.md:547:Insert Matt's separate R09C high-level implementation instructions here before assigning this prompt.
docs/12-reset-gated-implementation-plan-2026-05-10.md:557:- implementation matching only R09C
docs/12-reset-gated-implementation-plan-2026-05-10.md:563:Do not merge. Do not trigger Prompt C. Do not change queue readiness beyond R09C's own status and Prompt B handoff. Do not sync main.
docs/12-reset-gated-implementation-plan-2026-05-10.md:566:RG3 full evaluation/audit:
docs/12-reset-gated-implementation-plan-2026-05-10.md:576:- Confirm both R09B and R09C are merged before any RG3 Prompt C re-audit begins.
docs/12-reset-gated-implementation-plan-2026-05-10.md:584:- Broad-query categorized output materially improves from the RG3 hold baseline or the gate report proves the public-web market is smaller.
docs/12-reset-gated-implementation-plan-2026-05-10.md:586:- RG4, refreshed mockups, R10-R12, export work, and any `main` promotion remain blocked until both R09B and R09C are complete and a future RG3 Prompt C records `advance`.
docs/12-reset-gated-implementation-plan-2026-05-10.md:734:- `gate_advanced`
docs/12-reset-gated-implementation-plan-2026-05-10.md:762:## Next Prompt A Assignment
docs/12-reset-gated-implementation-plan-2026-05-10.md:879:- if the current gate is RG3 and the decision is advance: do not mark R10 ready; assign the refreshed mockup/design preflight from DESIGN.md and leave R10-R12 blocked until Matt approves the refreshed mockups
STATUS.md:11:**Next pointer:** Prompt C audit for `RG3 - Validation, Conflict, And Gate Semantics` on `rebuild/validated-leads-loop`. R09B and R09C are both merged; RG4, the `DESIGN.md` mockup preflight, R10-R12, export work, and any `main` promotion remain blocked unless that audit records `advance`.
STATUS.md:13:**Design direction handoff:** `DESIGN.md` is now captured as the future RG4 visual direction authority. A refreshed RG4 mockup/design preflight exists on `codex/rg4-design-preflight-2026-05-11` at commit `5c5a10f`, with six rendered screens under `docs/mockups/rg4-design-preflight-2026-05-11/` on that branch. It is an unmerged inspection artifact only; it does not unlock RG4. R10-R12 remain blocked until a future RG3 Prompt C advances and Matt approves the refreshed mockups for production implementation.
STATUS.md:27:**Next feature pointer:** No Prompt A feature is ready. `R09C - Deep multi-source evidence acquisition and tier calibration` is now merged to `rebuild/validated-leads-loop`, so the next valid step is Prompt C for RG3. This remains an RG3 remediation gate state, not RG4. Do not unlock RG4 or sync `main` unless Prompt C records `advance`.
STATUS.md:31:**Final product mockup gate:** `DESIGN.md` is the future RG4 visual direction authority, while `docs/mockups/final-product-2026-05-10/index.html` remains the product-structure reference. A preflight artifact exists on `codex/rg4-design-preflight-2026-05-11`, but it remains unmerged and non-unlocking while RG3 is held. Matt must approve refreshed mockups after RG3 advances before production UI implementation.
STATUS.md:33:**Current feature branch QA status:** R07, R08, R09, R09A, R09B, and R09C are merged to `rebuild/validated-leads-loop`. Prompt B QA passed for R09C on `feat/reset-r09c-deep-multisource-evidence-tier-calibration`, and the branch was merged back into `rebuild/validated-leads-loop`. The post-R09A RG3 Prompt C re-audit remains the latest accepted gate decision (`hold`), but the accepted remediation slice is now complete. RG3 is ready for a fresh Prompt C audit; downstream RG4 work remains blocked unless that audit records `advance`.
STATUS.md:37:**Latest gate acceptance:** W4 accepted on 2026-05-10. W5 remains explicitly held on `rebuild/validated-leads-loop`; RG0 advanced on 2026-05-10 as a control-plane reset audit; RG1 advanced on 2026-05-10 as a benchmark-harness audit; RG2 advanced on 2026-05-11 as a search/source coverage audit; RG3 held on 2026-05-11 as a validation/value audit; Matt accepted the post-R09A RG3 hold, and the full R09B+R09C remediation slice is now merged and awaiting a fresh Prompt C decision; and W6 remains blocked until the visible operator loop is proven:
STATUS.md:44:- RG3 validation semantics hold report: `audits/gates/reset-2026-05-10/rg3-validation-semantics.md`
STATUS.md:46:**Latest reset control doc:** `docs/12-reset-gated-implementation-plan-2026-05-10.md` defines reset gates RG0-RG6. Every gate requires a full evaluation/audit report before downstream gate work unlocks. RG0 is advanced via `audits/gates/reset-2026-05-10/rg0-w5-hold.md`; RG1 is advanced via `audits/gates/reset-2026-05-10/rg1-benchmark-harness.md`; RG2 is advanced via `audits/gates/reset-2026-05-10/rg2-search-source-coverage.md`; RG3 remains `in_progress / gate_hold`, but both remediation features R09B and R09C are now merged and the next valid step is Prompt C; and RG4 remains blocked.
STATUS.md:72:Feature: R09C - Deep multi-source evidence acquisition and tier calibration
STATUS.md:75:Why it exists: R09B completed the first contact/evidence remediation pass, but Matt directed that RG3 must stay on hold and absorb one more remediation feature before any new Prompt C audit. R09C exists to materially improve contact quality and tier usefulness on promising review rows without relaxing the `high_trust_usable` definition.
STATUS.md:86:Exact result: Prompt B completed, QA passed, and R09C is merged to `rebuild/validated-leads-loop`. The branch stayed within R09C scope, preserved strict READY/high-trust gating, kept missing/unsupported/conflicting contacts non-CRM-ready, and exposed contact acquisition plus high-trust yield in benchmark theme summaries. RG3 remains held pending Prompt C; RG4/UI/export/main-sync scope stays blocked.
STATUS.md:87:Next pointer at that time: Prompt C for RG3.
STATUS.md:88:Open questions: Whether the completed R09B + R09C remediation slice is enough for RG3 to advance, or whether Prompt C should recommend another hold driven by live contact/value evidence.
STATUS.md:93:Why it exists: The post-R09A RG3 Prompt C re-audit held because R09A recovered broad volume but the complete live suite still had 0 high-trust usable rows and 0 contact-quality passes. Matt accepted the hold and asked to create R09B.
STATUS.md:102:Exact result: Prompt B completed and R09B is merged to `rebuild/validated-leads-loop`. Per Matt's queue update, do not trigger Prompt C from this completion. R09C is now the next same-gate remediation feature and the only valid Prompt A assignment. RG4/UI/export/main-sync scope remains blocked.
STATUS.md:103:Next pointer at that time: Superseded. R09C is now the only ready feature before any future RG3 Prompt C re-audit.
STATUS.md:104:Open questions: Whether the deeper R09C pass can materially improve contact quality and promising-row usefulness without weakening the READY/high-trust contract.
STATUS.md:109:Why it exists: RG3 Prompt C held because broad live runs returned only 7-10 categorized rows, produced 0 high-trust usable leads, and produced 0 contact-quality passes across the suite. Matt accepted the hold and asked for the remediation slice.
STATUS.md:119:Prompt C handoff: Audit RG3 - Validation, Conflict, And Gate Semantics on `rebuild/validated-leads-loop` after R09A merges. Confirm R07-R09A are merged, rerun the RG3 full evaluation/audit from `docs/12-reset-gated-implementation-plan-2026-05-10.md`, and write/update `audits/gates/reset-2026-05-10/rg3-validation-semantics.md`. R09A recovered broad categorized volume and funnel observability, but live contact quality and high-trust usable output remain zero, so RG3 must not advance from feature QA alone.
STATUS.md:121:Historical next pointer at that time: no Prompt A/B feature was ready until Matt accepted or revised the next RG3 remediation scope. Superseded by R09B after Matt accepted the hold.
STATUS.md:122:Open questions at that time: What level of contact/value recovery should the next RG3 remediation target before RG4 mockup preflight can begin? Superseded by R09B's contact/evidence acquisition scope.
STATUS.md:137:Exact Prompt C handoff: Audit RG3 - Validation, Conflict, And Gate Semantics on `rebuild/validated-leads-loop`. Confirm R07-R09 are merged, run the RG3 full evaluation/audit from `docs/12-reset-gated-implementation-plan-2026-05-10.md`, and write `audits/gates/reset-2026-05-10/rg3-validation-semantics.md`. Do not unlock RG4 unless Prompt C records an `advance`; do not sync `main`.
STATUS.md:138:Historical next pointer at that time: Prompt C for RG3; superseded by the accepted RG3 hold and R09A remediation slice.
STATUS.md:146:What changed: Captured the May 11 design direction as future RG4 input only: deep navy instrument chassis, paper-white evidence table, brand leads once then product speaks, and rabbit/icon quarantine until an approved vector exists. Updated the reset plan and ADRs so RG3 Prompt C cites `DESIGN.md` as future RG4 input, and RG4 requires refreshed mockups plus Matt approval before R10 can start.
STATUS.md:148:Next design pointer: If RG3 Prompt C advances, hand the refreshed-mockup prompt from the final response to a design/mockup agent before assigning R10.
STATUS.md:150:RG3 Prompt C audit:
STATUS.md:154:What happened: Prompt C confirmed R07-R09 are merged and RG3 had not already advanced, ran required core/API verification plus web regression/build checks, started the local API with inherited Ollama-routed OpenAI env vars cleared, and ran the live Scout benchmark suite against `http://127.0.0.1:8013`.
STATUS.md:156:Why: RG3 semantics improved, but the live product still fails the operator-value bar. Manufacturing no longer 503s and missing/unsupported contacts are not labeled CRM-ready, but broad live prompts returned only 7-10 categorized rows, the suite produced 0 high-trust usable leads, and contact quality was 0 across the benchmark set.
STATUS.md:164:Historical next pointer at that time: no Prompt A assignment was valid until Matt accepted or adjusted the RG3 remediation scope. Superseded by R09A after Matt accepted the hold.
STATUS.md:179:Historical next pointer at that time: Prompt A for R09; superseded by merged R09, RG3 Prompt C hold, and R09A remediation.
STATUS.md:180:Open questions: None for R09 kickoff; RG3 still requires R09 and Prompt C audit before any gate advancement.
STATUS.md:329:- Product is in audit-red state. Documentation authority remediation is complete; F01-F19 are merged to `rebuild/validated-leads-loop`, but the May 10 audit found the visible loop still fails live operator benchmarks. W2, W3, and W4 are orchestrator-accepted. R00-R09C are merged; RG2 advanced as a search/source coverage gate; RG3 remains `in_progress / gate_hold` and is ready for Prompt C audit; W5 remains held; W6 remains blocked.
STATUS.md:333:- Run Prompt C for `RG3 - Validation, Conflict, And Gate Semantics` on `rebuild/validated-leads-loop`. Confirm R07-R09C are merged, rerun the RG3 full evaluation/audit from `docs/12-reset-gated-implementation-plan-2026-05-10.md`, and update `audits/gates/reset-2026-05-10/rg3-validation-semantics.md`. Do not unlock RG4, refreshed mockups, export work, or sync `main` unless Prompt C records `advance`.
STATUS.md:378:| 2026-05-11 | prompt-b-r09c-deep-evidence (Codex) | QA-passed `R09C - Deep multi-source evidence acquisition and tier calibration` on `feat/reset-r09c-deep-multisource-evidence-tier-calibration`: verified `git diff --check`, the required core/API suites, replay artifact semantics, non-CRM-ready handling for missing/unsupported/conflicting contacts, theme summary contact-yield observability, northstar drift alignment, and scope boundaries. Report saved at `.gstack/qa-reports/qa-report-r09c-deep-multisource-evidence-tier-calibration-2026-05-11.md`. R09C is merged to `rebuild/validated-leads-loop`; RG3 is now ready for Prompt C audit. |
STATUS.md:379:| 2026-05-11 | rg3-r09c-queue-insert (Codex) | Updated the reset control plane so R09B completion does not trigger Prompt C. Added `R09C - Deep multi-source evidence acquisition and tier calibration` as the single ready RG3 remediation feature, kept RG3 in `in_progress / gate_hold`, added ADR-018, and blocked RG4/R10-R12/export/main until both R09B and R09C complete and a future RG3 Prompt C records `advance`. |
STATUS.md:380:| 2026-05-11 | prompt-b-r09b-contact-evidence (Codex) | QA-passed `R09B - Contact and evidence acquisition pass` on `feat/reset-r09b-contact-evidence-acquisition`: verified `git diff --check`, required core/API suites, replay artifact semantics, READY blocker reporting, northstar drift alignment, and the branch scope. QA report saved at `.gstack/qa-reports/qa-report-r09b-contact-evidence-acquisition-2026-05-11.md`; branch is ready to merge only to `rebuild/validated-leads-loop`. RG4, export, dogfood, and `main` remain blocked until a future RG3 Prompt C records `advance`. |
STATUS.md:381:| 2026-05-11 | rg3-r09b-remediation-slice (Codex) | Landed Matt's accepted post-R09A RG3 hold into the reset control plane and created `R09B - Contact and evidence acquisition pass` as the single ready Prompt A feature. Recorded the RG4 design preflight branch as an unmerged inspection artifact only; RG4, R10-R12, export, dogfood, and `main` sync remain blocked until a future RG3 Prompt C records `advance`. |
STATUS.md:382:| 2026-05-11 | prompt-b-r09a-live-value-recovery (Codex) | QA-passed `R09A - Live value recovery and benchmark funnel diagnosis` on `feat/reset-r09a-live-value-recovery`: verified `git diff --check`, required core/API suites, replay artifact semantics, missing-contact safety, failed source-gap language, and live Scout artifacts for all six benchmark cases. Broad live cases now return 50 categorized rows and privacy refusal is expected, but contact-quality passes and high-trust usable rows remain zero. Report saved at `.gstack/qa-reports/qa-report-r09a-live-value-recovery-2026-05-11.md`; RG3 is ready for Prompt C audit after merge. |
STATUS.md:384:| 2026-05-11 | rg3-remediation-slice (Codex) | Landed Matt's accepted RG3 hold into the reset control plane and created `R09A - Live value recovery and benchmark funnel diagnosis` as the single ready Prompt A feature. RG4, refreshed `DESIGN.md` mockups, R10-R12, export, dogfood, and `main` sync remain blocked until a future RG3 Prompt C records `advance`. |
STATUS.md:385:| 2026-05-11 | design-direction-fold-in (Codex) | Folded `DESIGN.md` from `codex/design-vision-2026-05-11` into the reset control plane as future RG4 visual direction only. Added ADR-015 and updated `docs/12` so RG3 Prompt C cites the design doc as future RG4 input, but R10-R12 stay blocked until a refreshed mockup pass is approved by Matt. |
STATUS.md:386:| 2026-05-11 | prompt-b-r09-qa (Codex) | QA-passed `R09 - Tier summary, score semantics, and reason language reset` on `feat/reset-r09-tier-summary-semantics`: verified `git diff --check`, the required core/API suite, web tests/build, browser fixture screenshots, northstar drift, and that no R10-R14, RG4, export, persistence, or `main` work landed. Report saved at `.gstack/qa-reports/qa-report-r09-tier-summary-semantics-2026-05-11.md`. R09 is the last RG3 feature, so RG3 is ready for Prompt C audit after merge; RG4 remains blocked. |
STATUS.md:392:| 2026-05-11 | prompt-b-r06-qa (Codex) | QA-passed `R06 - Not-found and organization-only coverage writer` on `feat/reset-r06-nonperson-coverage`: verified the required RG2 core suite, `git diff --check`, focused coverage/orchestrator regressions, northstar drift, and scope boundaries. Report saved at `.gstack/qa-reports/qa-report-r06-nonperson-coverage-2026-05-11.md`. R06 is the last RG2 feature, so RG2 is ready for Prompt C audit after merge; RG3 remains blocked. |
STATUS.md:394:| 2026-05-11 | prompt-b-r05-qa (Codex) | QA-passed `R05 - Source collection and snapshot store` on `feat/reset-r05-source-collection-store`: verified the required core test suite, `git diff --check`, raw source fixture integrity, northstar drift, and scope boundaries. Report saved at `.gstack/qa-reports/qa-report-r05-source-collection-store-2026-05-11.md`. R06 is the next same-gate feature after the R05 merge lands; RG3 remains blocked. |

## Core RG3/R09C Required Suite

Command: cd packages/core && uv run pytest tests/test_query_planner.py tests/test_search.py tests/test_coverage.py tests/test_source_validation.py tests/test_contact_status.py tests/test_scoring.py tests/test_orchestrator.py tests/test_live_benchmark_runner.py tests/test_quality_report.py -q


## API Required Suite

Command: cd apps/api && WR_API_INTERNAL_TOKEN=test-internal-token uv run pytest tests -q

........................................................................ [ 94%]
....                                                                     [100%]
76 passed in 0.73s
.............................................                            [100%]
=============================== warnings summary ===============================
tests/test_api.py: 21 warnings
  /Users/mschwar/Documents/white-rabbit/apps/api/api/main.py:307: DeprecationWarning: datetime.datetime.utcnow() is deprecated and scheduled for removal in a future version. Use timezone-aware objects to represent datetimes in UTC: datetime.datetime.now(datetime.UTC).
    state.updated_at = datetime.utcnow()

tests/test_api.py: 10 warnings
  /Users/mschwar/Documents/white-rabbit/apps/api/api/db.py:358: DeprecationWarning: datetime.datetime.utcnow() is deprecated and scheduled for removal in a future version. Use timezone-aware objects to represent datetimes in UTC: datetime.datetime.now(datetime.UTC).
    state.updated_at = datetime.utcnow()

tests/test_api.py::test_batch_endpoint_creates_job_and_runs
  /Users/mschwar/Documents/white-rabbit/apps/api/tests/test_api.py:1015: DeprecationWarning: datetime.datetime.utcnow() is deprecated and scheduled for removal in a future version. Use timezone-aware objects to represent datetimes in UTC: datetime.datetime.now(datetime.UTC).
    created_at = __import__("datetime").datetime.utcnow()

tests/test_api.py::test_batch_endpoint_creates_job_and_runs
  /Users/mschwar/Documents/white-rabbit/apps/api/tests/test_api.py:1016: DeprecationWarning: datetime.datetime.utcnow() is deprecated and scheduled for removal in a future version. Use timezone-aware objects to represent datetimes in UTC: datetime.datetime.now(datetime.UTC).
    started_at = __import__("datetime").datetime.utcnow()

tests/test_api.py::test_batch_endpoint_creates_job_and_runs
  /Users/mschwar/Documents/white-rabbit/apps/api/tests/test_api.py:1017: DeprecationWarning: datetime.datetime.utcnow() is deprecated and scheduled for removal in a future version. Use timezone-aware objects to represent datetimes in UTC: datetime.datetime.now(datetime.UTC).
    ended_at = __import__("datetime").datetime.utcnow()

tests/test_api.py::test_batch_endpoint_creates_job_and_runs
  /Users/mschwar/Documents/white-rabbit/apps/api/tests/test_api.py:1029: DeprecationWarning: datetime.datetime.utcnow() is deprecated and scheduled for removal in a future version. Use timezone-aware objects to represent datetimes in UTC: datetime.datetime.now(datetime.UTC).
    started_at = __import__("datetime").datetime.utcnow()

tests/test_api.py::test_batch_endpoint_creates_job_and_runs
  /Users/mschwar/Documents/white-rabbit/apps/api/tests/test_api.py:1030: DeprecationWarning: datetime.datetime.utcnow() is deprecated and scheduled for removal in a future version. Use timezone-aware objects to represent datetimes in UTC: datetime.datetime.now(datetime.UTC).
    ended_at = __import__("datetime").datetime.utcnow()

tests/test_api.py::test_batch_endpoint_creates_job_and_runs
tests/test_api.py::test_batch_endpoint_respects_caps
  /Users/mschwar/Documents/white-rabbit/apps/api/api/main.py:629: DeprecationWarning: datetime.datetime.utcnow() is deprecated and scheduled for removal in a future version. Use timezone-aware objects to represent datetimes in UTC: datetime.datetime.now(datetime.UTC).
    job.started_at = datetime.utcnow()

tests/test_api.py::test_batch_endpoint_creates_job_and_runs
tests/test_api.py::test_batch_endpoint_creates_job_and_runs
tests/test_api.py::test_batch_endpoint_respects_caps
  /Users/mschwar/Documents/white-rabbit/apps/api/api/main.py:635: DeprecationWarning: datetime.datetime.utcnow() is deprecated and scheduled for removal in a future version. Use timezone-aware objects to represent datetimes in UTC: datetime.datetime.now(datetime.UTC).
    batch_run.started_at = datetime.utcnow()

tests/test_api.py::test_batch_endpoint_creates_job_and_runs
tests/test_api.py::test_batch_endpoint_creates_job_and_runs
  /Users/mschwar/Documents/white-rabbit/apps/api/api/main.py:800: DeprecationWarning: datetime.datetime.utcnow() is deprecated and scheduled for removal in a future version. Use timezone-aware objects to represent datetimes in UTC: datetime.datetime.now(datetime.UTC).
    batch_run.ended_at = datetime.utcnow()

tests/test_api.py::test_batch_endpoint_respects_caps
  /Users/mschwar/Documents/white-rabbit/apps/api/tests/test_api.py:1174: DeprecationWarning: datetime.datetime.utcnow() is deprecated and scheduled for removal in a future version. Use timezone-aware objects to represent datetimes in UTC: datetime.datetime.now(datetime.UTC).
    created_at = __import__("datetime").datetime.utcnow()

tests/test_api.py::test_batch_endpoint_respects_caps
  /Users/mschwar/Documents/white-rabbit/apps/api/tests/test_api.py:1175: DeprecationWarning: datetime.datetime.utcnow() is deprecated and scheduled for removal in a future version. Use timezone-aware objects to represent datetimes in UTC: datetime.datetime.now(datetime.UTC).
    started_at = __import__("datetime").datetime.utcnow()

tests/test_api.py::test_batch_endpoint_respects_caps
  /Users/mschwar/Documents/white-rabbit/apps/api/tests/test_api.py:1176: DeprecationWarning: datetime.datetime.utcnow() is deprecated and scheduled for removal in a future version. Use timezone-aware objects to represent datetimes in UTC: datetime.datetime.now(datetime.UTC).
    ended_at = __import__("datetime").datetime.utcnow()

tests/test_api.py::test_batch_endpoint_respects_caps
  /Users/mschwar/Documents/white-rabbit/apps/api/tests/test_api.py:1188: DeprecationWarning: datetime.datetime.utcnow() is deprecated and scheduled for removal in a future version. Use timezone-aware objects to represent datetimes in UTC: datetime.datetime.now(datetime.UTC).
    started_at = __import__("datetime").datetime.utcnow()

tests/test_api.py::test_batch_endpoint_respects_caps
  /Users/mschwar/Documents/white-rabbit/apps/api/tests/test_api.py:1189: DeprecationWarning: datetime.datetime.utcnow() is deprecated and scheduled for removal in a future version. Use timezone-aware objects to represent datetimes in UTC: datetime.datetime.now(datetime.UTC).
    ended_at = __import__("datetime").datetime.utcnow()

tests/test_api.py::test_batch_endpoint_respects_caps
  /Users/mschwar/Documents/white-rabbit/apps/api/api/main.py:722: DeprecationWarning: datetime.datetime.utcnow() is deprecated and scheduled for removal in a future version. Use timezone-aware objects to represent datetimes in UTC: datetime.datetime.now(datetime.UTC).
    batch_run.ended_at = datetime.utcnow()

tests/test_api.py::test_full_endpoint_returns_persisted_lead_ids
tests/test_api.py::test_full_endpoint_returns_persisted_lead_ids
tests/test_api.py::test_full_endpoint_returns_persisted_lead_ids
  /Users/mschwar/Documents/white-rabbit/apps/api/tests/test_api.py:1317: DeprecationWarning: datetime.datetime.utcnow() is deprecated and scheduled for removal in a future version. Use timezone-aware objects to represent datetimes in UTC: datetime.datetime.now(datetime.UTC).
    reset_at=datetime.utcnow(),

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
45 passed, 52 warnings in 1.20s

## Diff Check

Command: git diff --check


## Local API Startup For Live RG3 Re-audit

Command: cd apps/api && env -u OPENAI_API_KEY -u OPENAI_BASE_URL -u TAVILY_API_KEY uv run uvicorn api.main:app --host 127.0.0.1 --port 8017

INFO:     Started server process [72568]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://127.0.0.1:8017 (Press CTRL+C to quit)

## Local API Health Check

Command: curl -sS http://127.0.0.1:8017/health

INFO:     127.0.0.1:58455 - "GET /health HTTP/1.1" 200 OK
{"status":"ok"}

## Live Scout Benchmark Suite

Command: set -a; . apps/api/.env; set +a; cd packages/core && uv run python -m core.live_benchmark_runner --api-base-url http://127.0.0.1:8017 --output-dir ../../audits/raw/reset-2026-05-10/rg3/live-r09c-reaudit --mode scout --api-token [redacted]

INFO:     127.0.0.1:58464 - "POST /sandbox/reset HTTP/1.1" 200 OK
INFO:     127.0.0.1:58464 - "POST /scout HTTP/1.1" 200 OK
Orchestrator error: Tavily search failed: Tavily API error: 432 - {"detail":{"error":"This request exceeds your plan's set usage limit. Please upgrade your plan or contact support@tavily.com"}}
Traceback (most recent call last):
  File "/Users/mschwar/Documents/white-rabbit/packages/core/src/core/search.py", line 101, in _fetch_single_search_results
    response.raise_for_status()
  File "/Users/mschwar/Documents/white-rabbit/apps/api/.venv/lib/python3.12/site-packages/httpx/_models.py", line 829, in raise_for_status
    raise HTTPStatusError(message, request=request, response=self)
httpx.HTTPStatusError: Client error '432 ' for url 'https://api.tavily.com/search'
For more information check: https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/432

The above exception was the direct cause of the following exception:

Traceback (most recent call last):
  File "/Users/mschwar/Documents/white-rabbit/packages/core/src/core/orchestrator.py", line 691, in scout
    search_results = await search_fn(query, **search_kwargs)
                     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/Users/mschwar/Documents/white-rabbit/packages/core/src/core/search.py", line 145, in fetch_search_results
    await _fetch_single_search_results(
  File "/Users/mschwar/Documents/white-rabbit/packages/core/src/core/search.py", line 105, in _fetch_single_search_results
    raise TavilySearchError(
core.search.TavilySearchError: Tavily API error: 432 - {"detail":{"error":"This request exceeds your plan's set usage limit. Please upgrade your plan or contact support@tavily.com"}}

The above exception was the direct cause of the following exception:

Traceback (most recent call last):
  File "/Users/mschwar/Documents/white-rabbit/apps/api/api/main.py", line 331, in run_scout
    leads, metrics = await scout(
                     ^^^^^^^^^^^^
  File "/Users/mschwar/Documents/white-rabbit/packages/core/src/core/orchestrator.py", line 694, in scout
    raise OrchestratorError(f"Tavily search failed: {exc}") from exc
core.orchestrator.OrchestratorError: Tavily search failed: Tavily API error: 432 - {"detail":{"error":"This request exceeds your plan's set usage limit. Please upgrade your plan or contact support@tavily.com"}}
INFO:     127.0.0.1:58464 - "POST /scout HTTP/1.1" 503 Service Unavailable
Orchestrator error: Tavily search failed: Tavily API error: 432 - {"detail":{"error":"This request exceeds your plan's set usage limit. Please upgrade your plan or contact support@tavily.com"}}
Traceback (most recent call last):
  File "/Users/mschwar/Documents/white-rabbit/packages/core/src/core/search.py", line 101, in _fetch_single_search_results
    response.raise_for_status()
  File "/Users/mschwar/Documents/white-rabbit/apps/api/.venv/lib/python3.12/site-packages/httpx/_models.py", line 829, in raise_for_status
    raise HTTPStatusError(message, request=request, response=self)
httpx.HTTPStatusError: Client error '432 ' for url 'https://api.tavily.com/search'
For more information check: https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/432

The above exception was the direct cause of the following exception:

Traceback (most recent call last):
  File "/Users/mschwar/Documents/white-rabbit/packages/core/src/core/orchestrator.py", line 691, in scout
    search_results = await search_fn(query, **search_kwargs)
                     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/Users/mschwar/Documents/white-rabbit/packages/core/src/core/search.py", line 145, in fetch_search_results
    await _fetch_single_search_results(
  File "/Users/mschwar/Documents/white-rabbit/packages/core/src/core/search.py", line 105, in _fetch_single_search_results
    raise TavilySearchError(
core.search.TavilySearchError: Tavily API error: 432 - {"detail":{"error":"This request exceeds your plan's set usage limit. Please upgrade your plan or contact support@tavily.com"}}

The above exception was the direct cause of the following exception:

Traceback (most recent call last):
  File "/Users/mschwar/Documents/white-rabbit/apps/api/api/main.py", line 331, in run_scout
    leads, metrics = await scout(
                     ^^^^^^^^^^^^
  File "/Users/mschwar/Documents/white-rabbit/packages/core/src/core/orchestrator.py", line 694, in scout
    raise OrchestratorError(f"Tavily search failed: {exc}") from exc
core.orchestrator.OrchestratorError: Tavily search failed: Tavily API error: 432 - {"detail":{"error":"This request exceeds your plan's set usage limit. Please upgrade your plan or contact support@tavily.com"}}
INFO:     127.0.0.1:58464 - "POST /scout HTTP/1.1" 503 Service Unavailable
Orchestrator error: Tavily search failed: Tavily API error: 432 - {"detail":{"error":"This request exceeds your plan's set usage limit. Please upgrade your plan or contact support@tavily.com"}}
Traceback (most recent call last):
  File "/Users/mschwar/Documents/white-rabbit/packages/core/src/core/search.py", line 101, in _fetch_single_search_results
    response.raise_for_status()
  File "/Users/mschwar/Documents/white-rabbit/apps/api/.venv/lib/python3.12/site-packages/httpx/_models.py", line 829, in raise_for_status
    raise HTTPStatusError(message, request=request, response=self)
httpx.HTTPStatusError: Client error '432 ' for url 'https://api.tavily.com/search'
For more information check: https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/432

The above exception was the direct cause of the following exception:

Traceback (most recent call last):
  File "/Users/mschwar/Documents/white-rabbit/packages/core/src/core/orchestrator.py", line 691, in scout
    search_results = await search_fn(query, **search_kwargs)
                     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/Users/mschwar/Documents/white-rabbit/packages/core/src/core/search.py", line 145, in fetch_search_results
    await _fetch_single_search_results(
  File "/Users/mschwar/Documents/white-rabbit/packages/core/src/core/search.py", line 105, in _fetch_single_search_results
    raise TavilySearchError(
core.search.TavilySearchError: Tavily API error: 432 - {"detail":{"error":"This request exceeds your plan's set usage limit. Please upgrade your plan or contact support@tavily.com"}}

The above exception was the direct cause of the following exception:

Traceback (most recent call last):
  File "/Users/mschwar/Documents/white-rabbit/apps/api/api/main.py", line 331, in run_scout
    leads, metrics = await scout(
                     ^^^^^^^^^^^^
  File "/Users/mschwar/Documents/white-rabbit/packages/core/src/core/orchestrator.py", line 694, in scout
    raise OrchestratorError(f"Tavily search failed: {exc}") from exc
core.orchestrator.OrchestratorError: Tavily search failed: Tavily API error: 432 - {"detail":{"error":"This request exceeds your plan's set usage limit. Please upgrade your plan or contact support@tavily.com"}}
INFO:     127.0.0.1:58464 - "POST /scout HTTP/1.1" 503 Service Unavailable
Orchestrator error: Tavily search failed: Tavily API error: 432 - {"detail":{"error":"This request exceeds your plan's set usage limit. Please upgrade your plan or contact support@tavily.com"}}
Traceback (most recent call last):
  File "/Users/mschwar/Documents/white-rabbit/packages/core/src/core/search.py", line 101, in _fetch_single_search_results
    response.raise_for_status()
  File "/Users/mschwar/Documents/white-rabbit/apps/api/.venv/lib/python3.12/site-packages/httpx/_models.py", line 829, in raise_for_status
    raise HTTPStatusError(message, request=request, response=self)
httpx.HTTPStatusError: Client error '432 ' for url 'https://api.tavily.com/search'
For more information check: https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/432

The above exception was the direct cause of the following exception:

Traceback (most recent call last):
  File "/Users/mschwar/Documents/white-rabbit/packages/core/src/core/orchestrator.py", line 691, in scout
    search_results = await search_fn(query, **search_kwargs)
                     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/Users/mschwar/Documents/white-rabbit/packages/core/src/core/search.py", line 145, in fetch_search_results
    await _fetch_single_search_results(
  File "/Users/mschwar/Documents/white-rabbit/packages/core/src/core/search.py", line 105, in _fetch_single_search_results
    raise TavilySearchError(
core.search.TavilySearchError: Tavily API error: 432 - {"detail":{"error":"This request exceeds your plan's set usage limit. Please upgrade your plan or contact support@tavily.com"}}

The above exception was the direct cause of the following exception:

Traceback (most recent call last):
  File "/Users/mschwar/Documents/white-rabbit/apps/api/api/main.py", line 331, in run_scout
    leads, metrics = await scout(
                     ^^^^^^^^^^^^
  File "/Users/mschwar/Documents/white-rabbit/packages/core/src/core/orchestrator.py", line 694, in scout
    raise OrchestratorError(f"Tavily search failed: {exc}") from exc
core.orchestrator.OrchestratorError: Tavily search failed: Tavily API error: 432 - {"detail":{"error":"This request exceeds your plan's set usage limit. Please upgrade your plan or contact support@tavily.com"}}
INFO:     127.0.0.1:58464 - "POST /scout HTTP/1.1" 503 Service Unavailable
INFO:     127.0.0.1:58464 - "POST /scout HTTP/1.1" 422 Unprocessable Entity
{
  "api_base_url": "http://127.0.0.1:8017",
  "case_results": [
    {
      "benchmark_id": "thomas-arizona-k12",
      "elapsed_seconds": 57.519,
      "mode": "scout",
      "response_path": "../../audits/raw/reset-2026-05-10/rg3/live-r09c-reaudit/thomas-arizona-k12.json",
      "status_code": 200,
      "status_path": "../../audits/raw/reset-2026-05-10/rg3/live-r09c-reaudit/thomas-arizona-k12.http"
    },
    {
      "benchmark_id": "lee-commodity-buyers",
      "elapsed_seconds": 12.341,
      "mode": "scout",
      "response_path": "../../audits/raw/reset-2026-05-10/rg3/live-r09c-reaudit/lee-commodity-buyers.json",
      "status_code": 503,
      "status_path": "../../audits/raw/reset-2026-05-10/rg3/live-r09c-reaudit/lee-commodity-buyers.http"
    },
    {
      "benchmark_id": "healthcare-it-phoenix",
      "elapsed_seconds": 0.287,
      "mode": "scout",
      "response_path": "../../audits/raw/reset-2026-05-10/rg3/live-r09c-reaudit/healthcare-it-phoenix.json",
      "status_code": 503,
      "status_path": "../../audits/raw/reset-2026-05-10/rg3/live-r09c-reaudit/healthcare-it-phoenix.http"
    },
    {
      "benchmark_id": "finance-cisos-new-york",
      "elapsed_seconds": 0.264,
      "mode": "scout",
      "response_path": "../../audits/raw/reset-2026-05-10/rg3/live-r09c-reaudit/finance-cisos-new-york.json",
      "status_code": 503,
      "status_path": "../../audits/raw/reset-2026-05-10/rg3/live-r09c-reaudit/finance-cisos-new-york.http"
    },
    {
      "benchmark_id": "manufacturing-ops-detroit",
      "elapsed_seconds": 0.351,
      "mode": "scout",
      "response_path": "../../audits/raw/reset-2026-05-10/rg3/live-r09c-reaudit/manufacturing-ops-detroit.json",
      "status_code": 503,
      "status_path": "../../audits/raw/reset-2026-05-10/rg3/live-r09c-reaudit/manufacturing-ops-detroit.http"
    },
    {
      "benchmark_id": "privacy-reject-homeowner-phones",
      "elapsed_seconds": 0.069,
      "mode": "scout",
      "response_path": "../../audits/raw/reset-2026-05-10/rg3/live-r09c-reaudit/privacy-reject-homeowner-phones.json",
      "status_code": 422,
      "status_path": "../../audits/raw/reset-2026-05-10/rg3/live-r09c-reaudit/privacy-reject-homeowner-phones.http"
    }
  ],
  "mode": "scout",
  "output_root": "../../audits/raw/reset-2026-05-10/rg3/live-r09c-reaudit",
  "suite_report": {
    "case_summaries": {
      "finance-cisos-new-york": {
        "candidate_ready_blockers": [],
        "categorized_row_count": 0,
        "error_code": "tavily_failed",
        "escape_velocity_floor_met": false,
        "expected_target_coverage_count": 0,
        "expected_target_coverage_missing": [],
        "failed_count": 0,
        "funnel_counts": {
          "categorized_rows": 0,
          "contact_evidence_candidates_searched": 0,
          "contact_evidence_conflicting_signals": 0,
          "contact_evidence_contacts_acquired": 0,
          "contact_evidence_field_corroborations": 0,
          "contact_evidence_review_to_high_trust": 0,
          "contact_evidence_searches": 0,
          "contact_quality_passes": 0,
          "deduped_sources": 0,
          "extracted_candidates": 0,
          "high_trust_usable_rows": 0,
          "person_rows": 0,
          "raw_vendor_hits": 0,
          "source_snapshots": 0
        },
        "guardrail_status": "clear",
        "high_trust_usable_count": 0,
        "high_volume_floor_met": false,
        "http_status": 503,
        "minimum_escape_rows": 10,
        "not_found_count": 0,
        "organization_only_count": 0,
        "person_lead_count": 0,
        "privacy_refusal": false,
        "quality_report": {
          "artifact_id": "finance-cisos-new-york",
          "artifact_kind": "benchmark",
          "candidate_category_counts": {
            "failed": 0,
            "not_found": 0,
            "organization_only": 0,
            "person_lead": 0
          },
          "candidate_ready_blockers": [],
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
          "query": "finance CISOs at financial services firms in New York",
          "ready_blocker_counts": {},
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
        "quality_status": "evaluated",
        "ready_blocker_counts": {},
        "review_count": 0,
        "target_categorized_rows": 50,
        "target_volume_floor_met": false,
        "volume_floor_status": "below_active_50_plus_target"
      },
      "healthcare-it-phoenix": {
        "candidate_ready_blockers": [],
        "categorized_row_count": 0,
        "error_code": "tavily_failed",
        "escape_velocity_floor_met": false,
        "expected_target_coverage_count": 0,
        "expected_target_coverage_missing": [],
        "failed_count": 0,
        "funnel_counts": {
          "categorized_rows": 0,
          "contact_evidence_candidates_searched": 0,
          "contact_evidence_conflicting_signals": 0,
          "contact_evidence_contacts_acquired": 0,
          "contact_evidence_field_corroborations": 0,
          "contact_evidence_review_to_high_trust": 0,
          "contact_evidence_searches": 0,
          "contact_quality_passes": 0,
          "deduped_sources": 0,
          "extracted_candidates": 0,
          "high_trust_usable_rows": 0,
          "person_rows": 0,
          "raw_vendor_hits": 0,
          "source_snapshots": 0
        },
        "guardrail_status": "clear",
        "high_trust_usable_count": 0,
        "high_volume_floor_met": false,
        "http_status": 503,
        "minimum_escape_rows": 10,
        "not_found_count": 0,
        "organization_only_count": 0,
        "person_lead_count": 0,
        "privacy_refusal": false,
        "quality_report": {
          "artifact_id": "healthcare-it-phoenix",
          "artifact_kind": "benchmark",
          "candidate_category_counts": {
            "failed": 0,
            "not_found": 0,
            "organization_only": 0,
            "person_lead": 0
          },
          "candidate_ready_blockers": [],
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
          "query": "healthcare IT directors in Phoenix",
          "ready_blocker_counts": {},
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
        "quality_status": "evaluated",
        "ready_blocker_counts": {},
        "review_count": 0,
        "target_categorized_rows": 50,
        "target_volume_floor_met": false,
        "volume_floor_status": "below_active_50_plus_target"
      },
      "lee-commodity-buyers": {
        "candidate_ready_blockers": [],
        "categorized_row_count": 0,
        "error_code": "tavily_failed",
        "escape_velocity_floor_met": false,
        "expected_target_coverage_count": 0,
        "expected_target_coverage_missing": [],
        "failed_count": 0,
        "funnel_counts": {
          "categorized_rows": 0,
          "contact_evidence_candidates_searched": 0,
          "contact_evidence_conflicting_signals": 0,
          "contact_evidence_contacts_acquired": 0,
          "contact_evidence_field_corroborations": 0,
          "contact_evidence_review_to_high_trust": 0,
          "contact_evidence_searches": 0,
          "contact_quality_passes": 0,
          "deduped_sources": 0,
          "extracted_candidates": 0,
          "high_trust_usable_rows": 0,
          "person_rows": 0,
          "raw_vendor_hits": 0,
          "source_snapshots": 0
        },
        "guardrail_status": "needs_more_detail",
        "high_trust_usable_count": 0,
        "high_volume_floor_met": false,
        "http_status": 503,
        "minimum_escape_rows": 10,
        "not_found_count": 0,
        "organization_only_count": 0,
        "person_lead_count": 0,
        "privacy_refusal": false,
        "quality_report": {
          "artifact_id": "lee-commodity-buyers",
          "artifact_kind": "benchmark",
          "candidate_category_counts": {
            "failed": 0,
            "not_found": 0,
            "organization_only": 0,
            "person_lead": 0
          },
          "candidate_ready_blockers": [],
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
          "query": "commodity buyers at retail lumber yards in Washington",
          "ready_blocker_counts": {},
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
        "quality_status": "evaluated",
        "ready_blocker_counts": {},
        "review_count": 0,
        "target_categorized_rows": 50,
        "target_volume_floor_met": false,
        "volume_floor_status": "below_active_50_plus_target"
      },
      "manufacturing-ops-detroit": {
        "candidate_ready_blockers": [],
        "categorized_row_count": 0,
        "error_code": "tavily_failed",
        "escape_velocity_floor_met": false,
        "expected_target_coverage_count": 0,
        "expected_target_coverage_missing": [],
        "failed_count": 0,
        "funnel_counts": {
          "categorized_rows": 0,
          "contact_evidence_candidates_searched": 0,
          "contact_evidence_conflicting_signals": 0,
          "contact_evidence_contacts_acquired": 0,
          "contact_evidence_field_corroborations": 0,
          "contact_evidence_review_to_high_trust": 0,
          "contact_evidence_searches": 0,
          "contact_quality_passes": 0,
          "deduped_sources": 0,
          "extracted_candidates": 0,
          "high_trust_usable_rows": 0,
          "person_rows": 0,
          "raw_vendor_hits": 0,
          "source_snapshots": 0
        },
        "guardrail_status": "clear",
        "high_trust_usable_count": 0,
        "high_volume_floor_met": false,
        "http_status": 503,
        "minimum_escape_rows": 10,
        "not_found_count": 0,
        "organization_only_count": 0,
        "person_lead_count": 0,
        "privacy_refusal": false,
        "quality_report": {
          "artifact_id": "manufacturing-ops-detroit",
          "artifact_kind": "benchmark",
          "candidate_category_counts": {
            "failed": 0,
            "not_found": 0,
            "organization_only": 0,
            "person_lead": 0
          },
          "candidate_ready_blockers": [],
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
          "query": "manufacturing operations leaders in Detroit",
          "ready_blocker_counts": {},
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
        "quality_status": "evaluated",
        "ready_blocker_counts": {},
        "review_count": 0,
        "target_categorized_rows": 50,
        "target_volume_floor_met": false,
        "volume_floor_status": "below_active_50_plus_target"
      },
      "privacy-reject-homeowner-phones": {
        "candidate_ready_blockers": [],
        "categorized_row_count": 0,
        "error_code": null,
        "escape_velocity_floor_met": true,
        "expected_target_coverage_count": 0,
        "expected_target_coverage_missing": [],
        "failed_count": 0,
        "funnel_counts": {
          "categorized_rows": 0,
          "contact_evidence_candidates_searched": 0,
          "contact_evidence_conflicting_signals": 0,
          "contact_evidence_contacts_acquired": 0,
          "contact_evidence_field_corroborations": 0,
          "contact_evidence_review_to_high_trust": 0,
          "contact_evidence_searches": 0,
          "contact_quality_passes": 0,
          "deduped_sources": 0,
          "extracted_candidates": 0,
          "high_trust_usable_rows": 0,
          "person_rows": 0,
          "raw_vendor_hits": 0,
          "source_snapshots": 0
        },
        "guardrail_status": "blocked",
        "high_trust_usable_count": 0,
        "high_volume_floor_met": true,
        "http_status": 422,
        "minimum_escape_rows": 0,
        "not_found_count": 0,
        "organization_only_count": 0,
        "person_lead_count": 0,
        "privacy_refusal": true,
        "quality_report": null,
        "quality_status": "expected_privacy_refusal",
        "ready_blocker_counts": {
          "privacy_refusal": 1
        },
        "review_count": 0,
        "target_categorized_rows": 0,
        "target_volume_floor_met": true,
        "volume_floor_status": "expected_privacy_refusal"
      },
      "thomas-arizona-k12": {
        "candidate_ready_blockers": [
          {
            "blocker": "source_inaccessible",
            "candidate_category": "failed",
            "index": 0,
            "reason": "REVIEW: rejected row; no hidden usable lead is implied. Source could not validate the person row: http_status=999 resolved_url=https://www.linkedin.com/in/dbsanders67",
            "tier": "failed"
          },
          {
            "blocker": "source_inaccessible",
            "candidate_category": "failed",
            "index": 1,
            "reason": "REVIEW: rejected row; no hidden usable lead is implied. Source could not validate the person row: http_status=999 resolved_url=https://www.linkedin.com/in/kevin-molino-661716117",
            "tier": "failed"
          },
          {
            "blocker": "source_inaccessible",
            "candidate_category": "failed",
            "index": 2,
            "reason": "REVIEW: rejected row; no hidden usable lead is implied. Source could not validate the person row: http_status=999 resolved_url=https://www.linkedin.com/in/jill-thomas-2aa89614",
            "tier": "failed"
          },
          {
            "blocker": "source_inaccessible",
            "candidate_category": "failed",
            "index": 3,
            "reason": "REVIEW: rejected row; no hidden usable lead is implied. Source could not validate the person row: http_status=999 resolved_url=https://www.linkedin.com/in/joncastelhano",
            "tier": "failed"
          },
          {
            "blocker": "source_inaccessible",
            "candidate_category": "failed",
            "index": 4,
            "reason": "REVIEW: rejected row; no hidden usable lead is implied. Source could not validate the person row: http_status=999 resolved_url=https://www.linkedin.com/in/diana-hawari",
            "tier": "failed"
          },
          {
            "blocker": "source_inaccessible",
            "candidate_category": "failed",
            "index": 5,
            "reason": "REVIEW: rejected row; no hidden usable lead is implied. Source could not validate the person row: http_status=999 resolved_url=https://www.linkedin.com/in/carter-plante-412825155",
            "tier": "failed"
          },
          {
            "blocker": "source_inaccessible",
            "candidate_category": "failed",
            "index": 6,
            "reason": "REVIEW: rejected row; no hidden usable lead is implied. No email or phone contact information found.",
            "tier": "failed"
          },
          {
            "blocker": "source_inaccessible",
            "candidate_category": "failed",
            "index": 7,
            "reason": "REVIEW: rejected row; no hidden usable lead is implied. Source could not validate the person row: http_status=999 resolved_url=https://www.linkedin.com/in/brian-boone-74447541",
            "tier": "failed"
          },
          {
            "blocker": "source_inaccessible",
            "candidate_category": "failed",
            "index": 8,
            "reason": "REVIEW: rejected row; no hidden usable lead is implied. Source could not validate the person row: http_status=999 resolved_url=https://www.linkedin.com/in/christine-dickinson-517b3545",
            "tier": "failed"
          },
          {
            "blocker": "organization_only",
            "candidate_category": "organization_only",
            "index": 9,
            "reason": "ORG-ONLY: account found, but no validated person is CRM-ready. Source coverage was found for Paradise Valley Unified School District, but no usable person lead was validated from the collected results.",
            "tier": "organization_only"
          }
        ],
        "categorized_row_count": 10,
        "error_code": null,
        "escape_velocity_floor_met": true,
        "expected_target_coverage_count": 8,
        "expected_target_coverage_missing": [],
        "failed_count": 9,
        "funnel_counts": {
          "categorized_rows": 10,
          "contact_evidence_candidates_searched": 1,
          "contact_evidence_conflicting_signals": 0,
          "contact_evidence_contacts_acquired": 0,
          "contact_evidence_field_corroborations": 0,
          "contact_evidence_review_to_high_trust": 0,
          "contact_evidence_searches": 1,
          "contact_quality_passes": 0,
          "deduped_sources": 50,
          "extracted_candidates": 9,
          "high_trust_usable_rows": 0,
          "person_rows": 0,
          "raw_vendor_hits": 56,
          "source_snapshots": 50
        },
        "guardrail_status": "needs_more_detail",
        "high_trust_usable_count": 0,
        "high_volume_floor_met": true,
        "http_status": 200,
        "minimum_escape_rows": 8,
        "not_found_count": 0,
        "organization_only_count": 1,
        "person_lead_count": 0,
        "privacy_refusal": false,
        "quality_report": {
          "artifact_id": "thomas-arizona-k12",
          "artifact_kind": "benchmark",
          "candidate_category_counts": {
            "failed": 9,
            "not_found": 0,
            "organization_only": 1,
            "person_lead": 0
          },
          "candidate_ready_blockers": [
            {
              "blocker": "source_inaccessible",
              "candidate_category": "failed",
              "index": 0,
              "reason": "REVIEW: rejected row; no hidden usable lead is implied. Source could not validate the person row: http_status=999 resolved_url=https://www.linkedin.com/in/dbsanders67",
              "tier": "failed"
            },
            {
              "blocker": "source_inaccessible",
              "candidate_category": "failed",
              "index": 1,
              "reason": "REVIEW: rejected row; no hidden usable lead is implied. Source could not validate the person row: http_status=999 resolved_url=https://www.linkedin.com/in/kevin-molino-661716117",
              "tier": "failed"
            },
            {
              "blocker": "source_inaccessible",
              "candidate_category": "failed",
              "index": 2,
              "reason": "REVIEW: rejected row; no hidden usable lead is implied. Source could not validate the person row: http_status=999 resolved_url=https://www.linkedin.com/in/jill-thomas-2aa89614",
              "tier": "failed"
            },
            {
              "blocker": "source_inaccessible",
              "candidate_category": "failed",
              "index": 3,
              "reason": "REVIEW: rejected row; no hidden usable lead is implied. Source could not validate the person row: http_status=999 resolved_url=https://www.linkedin.com/in/joncastelhano",
              "tier": "failed"
            },
            {
              "blocker": "source_inaccessible",
              "candidate_category": "failed",
              "index": 4,
              "reason": "REVIEW: rejected row; no hidden usable lead is implied. Source could not validate the person row: http_status=999 resolved_url=https://www.linkedin.com/in/diana-hawari",
              "tier": "failed"
            },
            {
              "blocker": "source_inaccessible",
              "candidate_category": "failed",
              "index": 5,
              "reason": "REVIEW: rejected row; no hidden usable lead is implied. Source could not validate the person row: http_status=999 resolved_url=https://www.linkedin.com/in/carter-plante-412825155",
              "tier": "failed"
            },
            {
              "blocker": "source_inaccessible",
              "candidate_category": "failed",
              "index": 6,
              "reason": "REVIEW: rejected row; no hidden usable lead is implied. No email or phone contact information found.",
              "tier": "failed"
            },
            {
              "blocker": "source_inaccessible",
              "candidate_category": "failed",
              "index": 7,
              "reason": "REVIEW: rejected row; no hidden usable lead is implied. Source could not validate the person row: http_status=999 resolved_url=https://www.linkedin.com/in/brian-boone-74447541",
              "tier": "failed"
            },
            {
              "blocker": "source_inaccessible",
              "candidate_category": "failed",
              "index": 8,
              "reason": "REVIEW: rejected row; no hidden usable lead is implied. Source could not validate the person row: http_status=999 resolved_url=https://www.linkedin.com/in/christine-dickinson-517b3545",
              "tier": "failed"
            },
            {
              "blocker": "organization_only",
              "candidate_category": "organization_only",
              "index": 9,
              "reason": "ORG-ONLY: account found, but no validated person is CRM-ready. Source coverage was found for Paradise Valley Unified School District, but no usable person lead was validated from the collected results.",
              "tier": "organization_only"
            }
          ],
          "contact_quality_count": 0,
          "contact_quality_rate": 0.0,
          "failed_count": 9,
          "fake_email_count": 5,
          "high_noise_count": 10,
          "high_noise_rate": 1.0,
          "not_found_count": 0,
          "organization_only_count": 1,
          "person_lead_count": 0,
          "persona_match_count": 0,
          "persona_match_rate": 0.0,
          "precision_rate": 0.0,
          "quality_gate_failures": [
            "zero_usable_candidates",
            "low_precision_rate",
            "low_persona_match_rate",
            "low_contact_quality_rate",
            "low_source_support_rate",
            "fake_emails_present",
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
          "ready_blocker_counts": {
            "organization_only": 1,
            "source_inaccessible": 9
          },
          "source_support_count": 1,
          "source_support_rate": 0.1,
          "total_candidates": 10,
          "unsupported_email_count": 0,
          "usable_count": 0,
          "validation_status_counts": {
            "email": {
              "deduced_with_pattern_evidence": 0,
              "failed": 5,
              "missing": 5,
              "unsupported": 0,
              "verified_found": 0
            },
            "name": {
              "failed": 8,
              "missing": 2,
              "supported": 0,
              "unsupported": 0
            },
            "organization": {
              "failed": 9,
              "missing": 0,
              "supported": 1,
              "unsupported": 0
            },
            "phone": {
              "deduced_with_pattern_evidence": 0,
              "failed": 0,
              "missing": 10,
              "unsupported": 0,
              "verified_found": 0
            },
            "source": {
              "failed": 9,
              "missing": 0,
              "supported": 1,
              "unsupported": 0
            },
            "title": {
              "failed": 8,
              "missing": 2,
              "supported": 0,
              "unsupported": 0
            }
          }
        },
        "quality_status": "evaluated",
        "ready_blocker_counts": {
          "organization_only": 1,
          "source_inaccessible": 9
        },
        "review_count": 0,
        "target_categorized_rows": 8,
        "target_volume_floor_met": true,
        "volume_floor_status": "minimum_met"
      }
    },
    "contact_pass_cases": 0,
    "failed_cases": 4,
    "guardrail_mismatches": [],
    "observation_mismatches": [
      "lee-commodity-buyers: volume",
      "healthcare-it-phoenix: persona, contact, source, volume",
      "finance-cisos-new-york: persona, contact, source, volume",
      "manufacturing-ops-detroit: persona, contact, source, volume"
    ],
    "passed_cases": 2,
    "persona_pass_cases": 0,
    "privacy_refusal_cases": 1,
    "source_pass_cases": 0,
    "suite_id": "required_lead_quality_suite",
    "theme_summaries": {
      "broad_b2b": {
        "case_count": 4,
        "categorized_rows": 0,
        "contact_acquisition_success_rate": 0.0,
        "contact_evidence_candidates_searched": 0,
        "contact_evidence_contacts_acquired": 0,
        "contact_evidence_review_to_high_trust": 0,
        "contact_quality_passes": 0,
        "contact_quality_rate": 0.0,
        "high_trust_usable_rows": 0,
        "high_trust_usable_yield": 0.0,
        "person_rows": 0,
        "review_to_high_trust_rate": 0.0
      },
      "named_account": {
        "case_count": 1,
        "categorized_rows": 10,
        "contact_acquisition_success_rate": 0.0,
        "contact_evidence_candidates_searched": 1,
        "contact_evidence_contacts_acquired": 0,
        "contact_evidence_review_to_high_trust": 0,
        "contact_quality_passes": 0,
        "contact_quality_rate": 0.0,
        "high_trust_usable_rows": 0,
        "high_trust_usable_yield": 0.0,
        "person_rows": 0,
        "review_to_high_trust_rate": 0.0
      },
      "privacy_rejection": {
        "case_count": 1,
        "categorized_rows": 0,
        "contact_acquisition_success_rate": 0.0,
        "contact_evidence_candidates_searched": 0,
        "contact_evidence_contacts_acquired": 0,
        "contact_evidence_review_to_high_trust": 0,
        "contact_quality_passes": 0,
        "contact_quality_rate": 0.0,
        "high_trust_usable_rows": 0,
        "high_trust_usable_yield": 0.0,
        "person_rows": 0,
        "review_to_high_trust_rate": 0.0
      }
    },
    "total_cases": 6
  }
}

## Live Quality Summary Inspection

Command: jq case/theme summary from live-r09c-reaudit/quality-summary.json


## Live Artifact Inventory

Command: find audits/raw/reset-2026-05-10/rg3/live-r09c-reaudit -maxdepth 1 -type f | sort


## R09C Replay Artifact Summary

Command: jq replay summary from audits/raw/reset-2026-05-10/r09c/replay/quality-summary.json

audits/raw/reset-2026-05-10/rg3/live-r09c-reaudit/finance-cisos-new-york.http
audits/raw/reset-2026-05-10/rg3/live-r09c-reaudit/finance-cisos-new-york.json
audits/raw/reset-2026-05-10/rg3/live-r09c-reaudit/healthcare-it-phoenix.http
audits/raw/reset-2026-05-10/rg3/live-r09c-reaudit/healthcare-it-phoenix.json
audits/raw/reset-2026-05-10/rg3/live-r09c-reaudit/lee-commodity-buyers.http
audits/raw/reset-2026-05-10/rg3/live-r09c-reaudit/lee-commodity-buyers.json
audits/raw/reset-2026-05-10/rg3/live-r09c-reaudit/manufacturing-ops-detroit.http
audits/raw/reset-2026-05-10/rg3/live-r09c-reaudit/manufacturing-ops-detroit.json
audits/raw/reset-2026-05-10/rg3/live-r09c-reaudit/privacy-reject-homeowner-phones.http
audits/raw/reset-2026-05-10/rg3/live-r09c-reaudit/privacy-reject-homeowner-phones.json
audits/raw/reset-2026-05-10/rg3/live-r09c-reaudit/quality-summary.json
audits/raw/reset-2026-05-10/rg3/live-r09c-reaudit/thomas-arizona-k12.http
audits/raw/reset-2026-05-10/rg3/live-r09c-reaudit/thomas-arizona-k12.json
jq: error (at audits/raw/reset-2026-05-10/r09c/replay/quality-summary.json:102): null (null) has no keys
{
  "total_cases": 6,
  "passed_cases": 2,
  "failed_cases": 4,
  "persona_pass_cases": 0,
  "contact_pass_cases": 0,
  "source_pass_cases": 0,
  "privacy_refusal_cases": 1,
  "observation_mismatches": [
    "lee-commodity-buyers: volume",
    "healthcare-it-phoenix: persona, contact, source, volume",
    "finance-cisos-new-york: persona, contact, source, volume",
    "manufacturing-ops-detroit: persona, contact, source, volume"
  ],
  "theme_summaries": {
    "broad_b2b": {
      "case_count": 4,
      "categorized_rows": 0,
      "contact_acquisition_success_rate": 0.0,
      "contact_evidence_candidates_searched": 0,
      "contact_evidence_contacts_acquired": 0,
      "contact_evidence_review_to_high_trust": 0,
      "contact_quality_passes": 0,
      "contact_quality_rate": 0.0,
      "high_trust_usable_rows": 0,
      "high_trust_usable_yield": 0.0,
      "person_rows": 0,
      "review_to_high_trust_rate": 0.0
    },
    "named_account": {
      "case_count": 1,
      "categorized_rows": 10,
      "contact_acquisition_success_rate": 0.0,
      "contact_evidence_candidates_searched": 1,
      "contact_evidence_contacts_acquired": 0,
      "contact_evidence_review_to_high_trust": 0,
      "contact_quality_passes": 0,
      "contact_quality_rate": 0.0,
      "high_trust_usable_rows": 0,
      "high_trust_usable_yield": 0.0,
      "person_rows": 0,
      "review_to_high_trust_rate": 0.0
    },
    "privacy_rejection": {
      "case_count": 1,
      "categorized_rows": 0,
      "contact_acquisition_success_rate": 0.0,
      "contact_evidence_candidates_searched": 0,
      "contact_evidence_contacts_acquired": 0,
      "contact_evidence_review_to_high_trust": 0,
      "contact_quality_passes": 0,
      "contact_quality_rate": 0.0,
      "high_trust_usable_rows": 0,
      "high_trust_usable_yield": 0.0,
      "person_rows": 0,
      "review_to_high_trust_rate": 0.0
    }
  },
  "case_summaries": {
    "finance-cisos-new-york": {
      "http_status": 503,
      "guardrail_status": "clear",
      "categorized_row_count": 0,
      "person_lead_count": 0,
      "high_trust_usable_count": 0,
      "review_count": 0,
      "organization_only_count": 0,
      "not_found_count": 0,
      "failed_count": 0,
      "contact_quality_passes": 0,
      "contact_evidence_candidates_searched": 0,
      "contact_evidence_contacts_acquired": 0,
      "raw_vendor_hits": 0,
      "deduped_sources": 0,
      "error_code": "tavily_failed",
      "quality_status": "evaluated",
      "ready_blocker_counts": {},
      "quality_gate_failures": [
        "no_candidates",
        "zero_usable_candidates",
        "low_precision_rate",
        "low_persona_match_rate",
        "low_contact_quality_rate",
        "low_source_support_rate"
      ]
    },
    "healthcare-it-phoenix": {
      "http_status": 503,
      "guardrail_status": "clear",
      "categorized_row_count": 0,
      "person_lead_count": 0,
      "high_trust_usable_count": 0,
      "review_count": 0,
      "organization_only_count": 0,
      "not_found_count": 0,
      "failed_count": 0,
      "contact_quality_passes": 0,
      "contact_evidence_candidates_searched": 0,
      "contact_evidence_contacts_acquired": 0,
      "raw_vendor_hits": 0,
      "deduped_sources": 0,
      "error_code": "tavily_failed",
      "quality_status": "evaluated",
      "ready_blocker_counts": {},
      "quality_gate_failures": [
        "no_candidates",
        "zero_usable_candidates",
        "low_precision_rate",
        "low_persona_match_rate",
        "low_contact_quality_rate",
        "low_source_support_rate"
      ]
    },
    "lee-commodity-buyers": {
      "http_status": 503,
      "guardrail_status": "needs_more_detail",
      "categorized_row_count": 0,
      "person_lead_count": 0,
      "high_trust_usable_count": 0,
      "review_count": 0,
      "organization_only_count": 0,
      "not_found_count": 0,
      "failed_count": 0,
      "contact_quality_passes": 0,
      "contact_evidence_candidates_searched": 0,
      "contact_evidence_contacts_acquired": 0,
      "raw_vendor_hits": 0,
      "deduped_sources": 0,
      "error_code": "tavily_failed",
      "quality_status": "evaluated",
      "ready_blocker_counts": {},
      "quality_gate_failures": [
        "no_candidates",
        "zero_usable_candidates",
        "low_precision_rate",
        "low_persona_match_rate",
        "low_contact_quality_rate",
        "low_source_support_rate"
      ]
    },
    "manufacturing-ops-detroit": {
      "http_status": 503,
      "guardrail_status": "clear",
      "categorized_row_count": 0,
      "person_lead_count": 0,
      "high_trust_usable_count": 0,
      "review_count": 0,
      "organization_only_count": 0,
      "not_found_count": 0,
      "failed_count": 0,
      "contact_quality_passes": 0,
      "contact_evidence_candidates_searched": 0,
      "contact_evidence_contacts_acquired": 0,
      "raw_vendor_hits": 0,
      "deduped_sources": 0,
      "error_code": "tavily_failed",
      "quality_status": "evaluated",
      "ready_blocker_counts": {},
      "quality_gate_failures": [
        "no_candidates",
        "zero_usable_candidates",
        "low_precision_rate",
        "low_persona_match_rate",
        "low_contact_quality_rate",
        "low_source_support_rate"
      ]
    },
    "privacy-reject-homeowner-phones": {
      "http_status": 422,
      "guardrail_status": "blocked",
      "categorized_row_count": 0,
      "person_lead_count": 0,
      "high_trust_usable_count": 0,
      "review_count": 0,
      "organization_only_count": 0,
      "not_found_count": 0,
      "failed_count": 0,
      "contact_quality_passes": 0,
      "contact_evidence_candidates_searched": 0,
      "contact_evidence_contacts_acquired": 0,
      "raw_vendor_hits": 0,
      "deduped_sources": 0,
      "error_code": null,
      "quality_status": "expected_privacy_refusal",
      "ready_blocker_counts": {
        "privacy_refusal": 1
      },
      "quality_gate_failures": []
    },
    "thomas-arizona-k12": {
      "http_status": 200,
      "guardrail_status": "needs_more_detail",
      "categorized_row_count": 10,
      "person_lead_count": 0,
      "high_trust_usable_count": 0,
      "review_count": 0,
      "organization_only_count": 1,
      "not_found_count": 0,
      "failed_count": 9,
      "contact_quality_passes": 0,
      "contact_evidence_candidates_searched": 1,
      "contact_evidence_contacts_acquired": 0,
      "raw_vendor_hits": 56,
      "deduped_sources": 50,
      "error_code": null,
      "quality_status": "evaluated",
      "ready_blocker_counts": {
        "organization_only": 1,
        "source_inaccessible": 9
      },
      "quality_gate_failures": [
        "zero_usable_candidates",
        "low_precision_rate",
        "low_persona_match_rate",
        "low_contact_quality_rate",
        "low_source_support_rate",
        "fake_emails_present",
        "high_noise_rate"
      ]
    }
  }
}

## R09C Replay Artifact Summary

Command: jq replay quality report and deep contact pass summary

### quality-summary.json

{
  "artifact_id": "r09c-replay",
  "total_candidates": 3,
  "usable_count": 1,
  "person_lead_count": 2,
  "contact_quality_count": 1,
  "contact_quality_rate": 0.333,
  "precision_rate": 0.333,
  "source_support_rate": 1.0,
  "fake_email_count": 0,
  "unsupported_email_count": 0,
  "ready_blocker_counts": {
    "conflicting_evidence": 1,
    "no_contact_source": 1
  },
  "quality_gate_passed": false,
  "quality_gate_failures": [
    "low_precision_rate",
    "low_contact_quality_rate"
  ],
  "validation_status_counts": {
    "email": {
      "deduced_with_pattern_evidence": 0,
      "failed": 0,
      "missing": 1,
      "unsupported": 0,
      "verified_found": 2
    },
    "name": {
      "failed": 0,
      "missing": 0,
      "supported": 3,
      "unsupported": 0
    },
    "organization": {
      "failed": 0,
      "missing": 0,
      "supported": 3,
      "unsupported": 0
    },
    "phone": {
      "deduced_with_pattern_evidence": 0,
      "failed": 0,
      "missing": 3,
      "unsupported": 0,
      "verified_found": 0
    },
    "source": {
      "failed": 0,
      "missing": 0,
      "supported": 3,
      "unsupported": 0
    },
    "title": {
      "failed": 0,
      "missing": 0,
      "supported": 3,
      "unsupported": 0
    }
  }
}

### deep-contact-evidence-pass.json

{
  "scenario": "deterministic replay fixture covering review-to-ready, review blocker, and conflict downgrade",
  "feature": "R09C - Deep multi-source evidence acquisition and tier calibration",
  "lead_count": 3,
  "tier_distribution": {
    "failed": 1,
    "high_trust_usable": 1,
    "not_found": 0,
    "organization_only": 0,
    "review": 1
  },
  "funnel_counts": {
    "categorized_rows": 3,
    "contact_evidence_candidates_searched": 3,
    "contact_evidence_conflicting_signals": 1,
    "contact_evidence_contacts_acquired": 2,
    "contact_evidence_field_corroborations": 3,
    "contact_evidence_review_to_high_trust": 1,
    "contact_evidence_searches": 7,
    "contact_quality_passes": 1,
    "deduped_sources": 0,
    "extracted_candidates": 3,
    "high_trust_usable_rows": 1,
    "person_rows": 2,
    "raw_vendor_hits": 0,
    "source_snapshots": 0
  },
  "funnel_notes": [
    "Deep contact evidence pass searched 3 promising rows and acquired 2 source-backed contacts; 1 rows gained enough contact evidence to clear the READY gate.",
    "Deep contact evidence pass observed 3 field corroborations and 1 conflicting signals across public-web sources."
  ],
  "leads": [
    {
      "name": "Jordan Lee",
      "organization": "Example Corp",
      "candidate_category": "person_lead",
      "tier": "high_trust_usable",
      "email_status": "verified_found",
      "gate_passed": true,
      "primary_filter_reason": "READY: supported person, organization, source, and usable contact cleared the evidence gate."
    },
    {
      "name": "Taylor Chen",
      "organization": "Acme Manufacturing",
      "candidate_category": "person_lead",
      "tier": "review",
      "email_status": "missing",
      "gate_passed": false,
      "primary_filter_reason": "REVIEW: contact is missing; deeper public-web pass did not find a direct email or explicit domain-pattern source."
    },
    {
      "name": null,
      "organization": "Northstar Parts",
      "candidate_category": "failed",
      "tier": "failed",
      "email_status": null,
      "gate_passed": null,
      "primary_filter_reason": "REVIEW: rejected row; no hidden usable lead is implied. Cross-source verification found conflicting evidence:  cross_check_conflicts=Possible stale role signal on https://northstarparts.example/archive."
    }
  ]
}

## Local API Shutdown

Command: lsof -ti tcp:8017 | xargs kill

stopped local API on 8017
INFO:     Shutting down
INFO:     Waiting for application shutdown.
INFO:     Application shutdown complete.
INFO:     Finished server process [72568]

## Final Diff Check After Audit Edits

Command: git diff --check


## Final Diff Check After Status Pointer Update

Command: git diff --check


## Final Diff Check After Text Tightening

Command: git diff --check

