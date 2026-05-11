# Reset Gate Review - RG3 Validation, Conflict, And Gate Semantics

**Branch:** `audit/reset-rg3-validation-semantics-r09c`
**Integration branch:** `rebuild/validated-leads-loop`
**Date:** 2026-05-11
**Decision:** hold
**Current product gate:** red

## Evidence Used

- `AGENTS.md`, `STATUS.md`, `docs/00-product-northstar.md`, `docs/12-reset-gated-implementation-plan-2026-05-10.md`, `docs/13-pipeline-orchestrator-contract-2026.md`, `docs/03-decisions.md`, and `audits/zero-trust-codebase-audit-2026-05-10.md`.
- `DESIGN.md` was read only as future RG4 visual direction. It is not evidence that this data-quality gate passed.
- Reset gate table proof: RG3 remains `in_progress / gate_hold`; RG4 remains `blocked`; R10-R15 remain `blocked`.
- Feature merge proof: R07, R08, R09, R09A, R09B, and R09C are all ancestors of `rebuild/validated-leads-loop` at `df9e831`.
- Prior RG3 report proof: the previous accepted RG3 decision was `hold`, not `gate_advanced`.
- Current live Scout artifacts: `audits/raw/reset-2026-05-10/rg3/live-r09c-reaudit/`.
- Current raw command output and cited evidence notes: `audits/raw/reset-2026-05-10/rg3/command-output-r09c-reaudit.md` and `audits/raw/reset-2026-05-10/rg3/evidence-notes-r09c-reaudit.md`.
- R09C replay evidence: `audits/raw/reset-2026-05-10/r09c/replay/deep-contact-evidence-pass.json` and `audits/raw/reset-2026-05-10/r09c/replay/quality-summary.json`.

## Commands Run

```bash
git fetch origin --prune
git status --short --branch
git rev-parse --short HEAD
git rev-parse --short origin/rebuild/validated-leads-loop
git merge-base --is-ancestor origin/feat/reset-r07-inclusive-extraction HEAD
git merge-base --is-ancestor origin/feat/reset-r08-tier-validation-conflicts HEAD
git merge-base --is-ancestor origin/feat/reset-r09-tier-summary-semantics HEAD
git merge-base --is-ancestor origin/feat/reset-r09a-live-value-recovery HEAD
git merge-base --is-ancestor origin/feat/reset-r09b-contact-evidence-acquisition HEAD
git merge-base --is-ancestor origin/feat/reset-r09c-deep-multisource-evidence-tier-calibration HEAD
rg -n "Current reset gate|RG3|R09C|gate_advanced|Next Prompt A|Current Prompt C handoff" STATUS.md docs/12-reset-gated-implementation-plan-2026-05-10.md
cd packages/core && uv run pytest tests/test_query_planner.py tests/test_search.py tests/test_coverage.py tests/test_source_validation.py tests/test_contact_status.py tests/test_scoring.py tests/test_orchestrator.py tests/test_live_benchmark_runner.py tests/test_quality_report.py -q
cd apps/api && WR_API_INTERNAL_TOKEN=test-internal-token uv run pytest tests -q
git diff --check
cd apps/api && env -u OPENAI_API_KEY -u OPENAI_BASE_URL -u TAVILY_API_KEY uv run uvicorn api.main:app --host 127.0.0.1 --port 8017
curl -sS http://127.0.0.1:8017/health
set -a; . apps/api/.env; set +a; cd packages/core && uv run python -m core.live_benchmark_runner --api-base-url http://127.0.0.1:8017 --output-dir ../../audits/raw/reset-2026-05-10/rg3/live-r09c-reaudit --mode scout --api-token [redacted]
jq summaries over audits/raw/reset-2026-05-10/rg3/live-r09c-reaudit/quality-summary.json
jq summaries over audits/raw/reset-2026-05-10/r09c/replay/deep-contact-evidence-pass.json and quality-summary.json
```

Verification results:

- Core RG3/R09C required suite: `76 passed`.
- API suite: `45 passed`, with existing datetime deprecation warnings.
- `git diff --check`: passed before audit report edits and again after final status/report updates.
- Local API health: `{"status":"ok"}`.

## Live Results

Fresh live Scout suite under `audits/raw/reset-2026-05-10/rg3/live-r09c-reaudit/`:

| Benchmark | HTTP | Categorized rows | Person rows | READY / high trust | Contact-quality passes | Error / status |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
| Thomas Arizona K-12 | 200 | 10 | 0 | 0 | 0 | evaluated |
| Lee commodity buyers | 503 | 0 | 0 | 0 | 0 | `tavily_failed` |
| Healthcare IT Phoenix | 503 | 0 | 0 | 0 | 0 | `tavily_failed` |
| Finance CISOs New York | 503 | 0 | 0 | 0 | 0 | `tavily_failed` |
| Manufacturing ops Detroit | 503 | 0 | 0 | 0 | 0 | `tavily_failed` |
| B2C private phone guardrail | 422 | 0 | 0 | 0 | 0 | expected privacy refusal |

Theme summary:

| Theme | Cases | Categorized rows | Person rows | READY / high trust | Contact-quality passes | Contacts acquired |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| named_account | 1 | 10 | 0 | 0 | 0 | 0 |
| broad_b2b | 4 | 0 | 0 | 0 | 0 | 0 |
| privacy_rejection | 1 | 0 | 0 | 0 | 0 | 0 |

The four broad B2B cases did not produce current live evidence because Tavily returned the plan-limit error below, surfaced by the API as `503` / `tavily_failed`:

```text
Tavily API error: 432 - {"detail":{"error":"This request exceeds your plan's set usage limit. Please upgrade your plan or contact support@tavily.com"}}
```

The completed Thomas Arizona case preserved target-account coverage and did not crash, but it produced 9 failed rows and 1 organization-only row. It had `0` person rows, `0` high-trust usable rows, and `0` contact-quality passes. The main READY blockers were `source_inaccessible: 9` and `organization_only: 1`.

## Screenshots And Artifacts

No new screenshots were required because RG3 is a data-quality and semantics gate, not a UI implementation gate. Existing R09 Prompt B fixture screenshots remain available at:

- `.gstack/qa-reports/screenshots/r09-prompt-b-desktop.png`
- `.gstack/qa-reports/screenshots/r09-prompt-b-mobile.png`

Raw artifacts:

- `audits/raw/reset-2026-05-10/rg3/live-r09c-reaudit/quality-summary.json`
- `audits/raw/reset-2026-05-10/rg3/live-r09c-reaudit/*.json`
- `audits/raw/reset-2026-05-10/rg3/live-r09c-reaudit/*.http`
- `audits/raw/reset-2026-05-10/rg3/evidence-notes-r09c-reaudit.md`
- `audits/raw/reset-2026-05-10/rg3/command-output-r09c-reaudit.md`
- `audits/raw/reset-2026-05-10/r09c/replay/deep-contact-evidence-pass.json`
- `audits/raw/reset-2026-05-10/r09c/replay/quality-summary.json`

## Value Prop Verdict

The current product does **not** give enough result volume, evidence, or export value for the operator loop.

Result volume is not proven: the one completed live case returned only 10 categorized rows for a named-account benchmark, and all four broad B2B cases returned 0 rows because the live search vendor is quota-blocked. Evidence value is not enough: the completed live case had 0 person rows, 0 high-trust usable rows, 0 contact-quality passes, 9 source-inaccessible failed rows, and 1 organization-only row. Export value is not enough: RG5 remains blocked, the current gate produced no READY/high-trust rows to export, and the product has not yet proven sales-first export value for Thomas or Lee.

R09C replay proves the mechanics can promote a review row only when direct contact evidence exists, keep missing-contact rows in review, and downgrade conflicting evidence. That is good implementation evidence, but it is not current live operator value and cannot advance RG3.

## Findings

1. **Hold blocker - current live evidence is service-blocked.** From RG2 onward, the reset plan requires current live evidence. Four required broad B2B live cases failed because Tavily returned HTTP 432 plan-limit errors. A gate cannot advance from replay evidence when the live search service is unavailable.
2. **Hold blocker - the completed live case has no CRM-ready value.** Thomas Arizona returned 10 categorized rows, but 0 person rows, 0 high-trust usable rows, and 0 contact-quality passes.
3. **Hold blocker - RG3 advance criteria are not met.** The reset plan requires at least one required live benchmark with nonzero high-trust output without unsupported contacts. The current live suite has none.
4. **Hold blocker - contact-quality proof is absent.** The reset plan requires at least one required live benchmark with nonzero contact-quality passes, or proof that source-backed public contact evidence is unavailable. Current broad search is quota-blocked, so the report cannot prove source unavailability.
5. **Pass - false-confidence handling is safer.** The completed live rows did not label missing, unsupported, inaccessible, or conflicting contact evidence as CRM-ready.
6. **Pass - R09C deterministic replay shows the intended mechanics.** Replay produced 1 high-trust row only with `verified_found` contact evidence, kept 1 missing-contact row in `review`, and downgraded 1 stale/conflicting row to `failed`.
7. **Partial - manufacturing parse-crash class is no longer the observed live error, but the current live case is still not product-evaluable.** Manufacturing failed before extraction because Tavily quota was exhausted, so this audit cannot use current live manufacturing evidence to prove parse-crash recovery.

## What Worked

- Required core and API suites passed.
- The live runner completed the suite and wrote per-case JSON/HTTP artifacts plus a quality summary.
- Privacy-sensitive B2C targeting returned the expected 422 refusal and is counted separately from no-candidate product failures.
- Funnel metrics now expose raw hits, deduped sources, extracted candidates, contact-evidence searches, contacts acquired, high-trust yield, and READY blockers.
- Current live output avoided promoting source-inaccessible or organization-only rows to CRM-ready status.
- R09C replay demonstrates evidence-backed promotion, missing-contact review preservation, and conflict downgrade behavior.

## What Did Not Work

- Broad live benchmarking is currently blocked by Tavily quota.
- The only completed live non-privacy case still has 0 high-trust rows and 0 contact-quality passes.
- Thomas Arizona uses mostly inaccessible LinkedIn sources and does not produce validated person rows.
- The current suite cannot prove broad-query result volume because four broad cases returned 503 before search results were available.
- The current suite cannot prove export value because there are no READY/high-trust rows to export and RG5 is still blocked.

## New Gaps Found

- The high-volume public-web path depends on Tavily quota availability. A quota-exhausted vendor makes RG2+ live gates unauditable and should be treated as an operational blocker, not as a passable product state.
- The completed named-account case shows the next value choke point after R09C: source collection can be large while validated person/contact output remains zero.
- The live quality summary can show `fake_emails_present` on failed rows while still keeping those rows non-CRM-ready. That is safer than false confidence, but the operator still gets no usable rows.

## Recommended Scope Change For Next Gate

Keep RG3 held. Do not start RG4 mockups, R10-R12 UI work, R13-R15 export/persistence/dogfood work, or a `main` sync.

No downstream Prompt A assignment is valid from this audit. Matt should first decide whether to restore/upgrade Tavily search quota and rerun the exact RG3 Prompt C live suite, or accept that RG3 still lacks public-web contact value and define another RG3 remediation/vendor-positioning slice.

If quota is restored, rerun Prompt C before changing product code. If the rerun still shows 0 high-trust rows and 0 contact-quality passes, the next remediation should stay inside RG3 and focus on source/vendor strategy, accessible-source targeting, and evidence-backed contact acquisition rather than UI/export work.

## Next Main Promotion Recommendation

Do not sync `main`. The decision is `hold`, live evidence is quota-blocked, and the completed live case has no CRM-ready output. Another operator-use promotion should happen only if Matt explicitly asks after reviewing this gate decision.

## Next Prompt A Assignment

None. Because the decision is `hold`, no downstream Prompt A feature and no RG4 design/mockup preflight is unlocked.

If Matt accepts this hold and wants another remediation, the next assignment must remain inside RG3. R10-R12 remain blocked. The refreshed mockup/design preflight from `DESIGN.md` remains blocked until a future Prompt C records RG3 `advance`.
