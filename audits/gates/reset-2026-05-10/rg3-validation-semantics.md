# Reset Gate Review - RG3 Validation, Conflict, And Gate Semantics

**Branch:** `audit/reset-rg3-r09a-value-audit`
**Integration branch:** `rebuild/validated-leads-loop`
**Date:** 2026-05-11
**Decision:** hold
**Current product gate:** red

## Evidence Used

- `AGENTS.md`, `STATUS.md`, `docs/00-product-northstar.md`, `docs/12-reset-gated-implementation-plan-2026-05-10.md`, `docs/13-pipeline-orchestrator-contract-2026.md`, `docs/03-decisions.md`, and `audits/zero-trust-codebase-audit-2026-05-10.md`.
- `DESIGN.md` was read only as future RG4 visual direction. It is not evidence that this data-quality gate passed.
- Current branch proof: `rebuild/validated-leads-loop` matched `origin/rebuild/validated-leads-loop` at `09409ab`.
- Feature merge proof: R07, R08, R09, and R09A are all ancestors of `rebuild/validated-leads-loop`.
- Current R09A live suite: `audits/raw/reset-2026-05-10/r09a/live-prompt-b/`.
- Current Prompt C partial live re-run: `audits/raw/reset-2026-05-10/rg3/r09a-live-rerun/`.
- Raw audit notes and command outputs: `audits/raw/reset-2026-05-10/rg3/evidence-notes-r09a-reaudit.md` and `audits/raw/reset-2026-05-10/rg3/command-output-r09a-reaudit.md`.

## Commands Run

```bash
git status --short --branch
git merge-base --is-ancestor feat/reset-r07-inclusive-extraction rebuild/validated-leads-loop
git merge-base --is-ancestor feat/reset-r08-tier-validation-conflicts rebuild/validated-leads-loop
git merge-base --is-ancestor feat/reset-r09-tier-summary-semantics rebuild/validated-leads-loop
git merge-base --is-ancestor feat/reset-r09a-live-value-recovery rebuild/validated-leads-loop
rg -n "RG3 \| Validation|gate_pending_audit|gate_advanced|R09A|R10 \|" docs/12-reset-gated-implementation-plan-2026-05-10.md STATUS.md
cd packages/core && uv run pytest tests/test_source_validation.py tests/test_contact_status.py tests/test_scoring.py tests/test_orchestrator.py -q
cd apps/api && WR_API_INTERNAL_TOKEN=test-internal-token uv run pytest tests -q
git diff --check
set -a; source .env; source apps/api/.env; unset OPENAI_BASE_URL; cd apps/api && uv run uvicorn api.main:app --host 127.0.0.1 --port 8016
cd packages/core && uv run python -m core.live_benchmark_runner --api-base-url http://127.0.0.1:8016 --output-dir ../../audits/raw/reset-2026-05-10/rg3-r09a/live --mode scout --api-token [redacted]
jq summaries over audits/raw/reset-2026-05-10/r09a/live-prompt-b/quality-summary.json
```

The current Prompt C live re-run produced a fresh Thomas Arizona artifact, then timed out before the full suite completed. That timeout is itself a reliability concern, but it is not the sole basis for the hold: the complete R09A Prompt B live suite is current to the merged R09A head and shows the same product-value blocker across all six benchmark cases.

## Live Results

Complete R09A Prompt B live suite:

| Benchmark | HTTP | Categorized rows | Person rows | READY / high trust | Contact-quality passes | Review | Org-only | Not found | Failed | Quality status |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| Thomas Arizona K-12 | 200 | 12 | 3 | 0 | 0 | 3 | 3 | 2 | 4 | evaluated |
| Lee commodity buyers | 200 | 50 | 2 | 0 | 0 | 2 | 2 | 0 | 46 | evaluated |
| Healthcare IT Phoenix | 200 | 50 | 3 | 0 | 0 | 3 | 1 | 1 | 45 | evaluated |
| Finance CISOs New York | 200 | 50 | 7 | 0 | 0 | 7 | 8 | 0 | 35 | evaluated |
| Manufacturing ops Detroit | 200 | 50 | 1 | 0 | 0 | 1 | 1 | 2 | 46 | evaluated |
| B2C private phone guardrail | 422 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | expected_privacy_refusal |

Current Prompt C partial re-run:

| Benchmark | HTTP | Categorized rows | Person rows | READY / high trust | Contact-quality passes | Notes |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
| Thomas Arizona K-12 | 200 | 12 | 0 | 0 | 0 | Runner elapsed 61.556s; 56 raw hits, 50 deduped sources, 9 extracted candidates, 9 failed rows, 3 organization-only rows. |
| Suite continuation | n/a | n/a | n/a | n/a | n/a | Runner exited with `httpx.ReadTimeout` before completing the second case. |

Manufacturing no longer 503s in the complete R09A live suite. It returns HTTP 200 with 50 categorized rows, which proves the parse-crash class improved.

## Screenshots And Artifacts

No new screenshots were required because RG3 is a data-quality and semantics gate, not a UI implementation gate. Existing R09 Prompt B fixture screenshots remain available at:

- `.gstack/qa-reports/screenshots/r09-prompt-b-desktop.png`
- `.gstack/qa-reports/screenshots/r09-prompt-b-mobile.png`

Raw artifacts:

- `audits/raw/reset-2026-05-10/r09a/live-prompt-b/quality-summary.json`
- `audits/raw/reset-2026-05-10/r09a/live-prompt-b/*.json`
- `audits/raw/reset-2026-05-10/rg3/r09a-live-rerun/thomas-arizona-k12.json`
- `audits/raw/reset-2026-05-10/rg3/r09a-live-rerun/thomas-arizona-k12.http`
- `audits/raw/reset-2026-05-10/rg3/evidence-notes-r09a-reaudit.md`
- `audits/raw/reset-2026-05-10/rg3/command-output-r09a-reaudit.md`

## Value Prop Verdict

The current product does **not** give enough result volume, evidence, and export value for the operator loop.

R09A materially improved result volume for broad prompts: Lee, healthcare, finance, and manufacturing now reach 50 categorized rows, and the privacy case is correctly treated as an expected refusal. But the product still does not provide enough evidence or exportable sales value because every evaluated live benchmark has `0` high-trust usable rows and `0` contact-quality passes. The current output is better as an audit distribution, but it is not yet a useful operator loop for Thomas or Lee.

Export value also remains unproven for this gate. RG5 is still blocked, and the current gate evidence does not show a sales-first export path that can hand Thomas/Lee READY rows with validated contact evidence.

## Findings

1. **Hold blocker - RG3 advance criteria are not met.** The reset plan requires at least one required live benchmark with nonzero `high_trust_usable` output without unsupported contacts. The complete R09A live suite has `0` high-trust usable rows in every evaluated case.
2. **Hold blocker - contact/value recovery is still zero.** Funnel counts show `contact_quality_passes: 0` for every evaluated live benchmark. The product avoids false confidence, but it still does not create CRM-ready value.
3. **Pass - broad volume recovered for most broad prompts.** Lee, healthcare, finance, and manufacturing now produce 50 categorized rows, which fixes the prior 7-10 broad-row failure for those cases.
4. **Partial - Thomas Arizona coverage is still below the active target.** Thomas Arizona produced 12 categorized rows in the complete R09A suite and again 12 rows in the current partial re-run. It is no longer a zero-row crash, but it does not prove enough target-account value.
5. **Pass - manufacturing parse crash is fixed.** Manufacturing returned HTTP 200 and explicit non-usable tiers instead of a 503.
6. **Pass - missing or failed contacts are not CRM-ready.** Sampled person rows are `review` and state that contact is missing or failed; no sampled row with missing/unsupported contact is marked `high_trust_usable`.
7. **Hold concern - current full-suite re-run timed out.** Prompt C's live runner timed out after the first case. That does not erase the complete R09A live evidence, but it means the gate cannot claim fresh full-suite runtime reliability.

## What Worked

- Required RG3 core checks passed: `49 passed`.
- Required API checks passed: `45 passed`, with existing datetime deprecation warnings.
- `git diff --check` passed before audit edits.
- R09A adds useful funnel observability: raw vendor hits, deduped sources, extracted candidates, categorized rows, person rows, high-trust rows, and contact-quality passes.
- Privacy-sensitive B2C targeting is handled as an expected refusal instead of a no-candidate product failure.
- Bad candidates degrade into `review`, `organization_only`, `not_found`, or `failed` rows instead of crashing or looking CRM-ready.

## What Did Not Work

- The live benchmark suite still produces no READY/high-trust rows.
- Contact discovery remains too weak to produce any contact-quality passes.
- Broad volume without usable contact evidence does not yet create sales value.
- Thomas Arizona still does not prove sufficient target-account coverage or usable contact output.
- The current Prompt C live full-suite re-run did not complete within the runner timeout.

## New Gaps Found

- Runtime reliability now matters for the gate: a broad suite that can take more than the runner timeout cannot support a confident gate advance even if prior artifacts exist.
- Funnel observability makes the real choke point visible: raw/source volume can be high while extracted person rows and contact-quality passes stay near zero.
- The next remediation needs to recover evidence-backed contact value, not just more source-gap rows.

## Recommended Scope Change For Next Gate

Keep RG3 held. Do not start RG4 mockups, R10-R12 UI work, export work, dogfood, or a `main` sync.

The next valid work should be a Matt-approved RG3 remediation slice focused on:

- recovering evidence-backed contacts or domain-pattern evidence without relaxing READY precision,
- improving person extraction from the expanded source universe,
- preserving high-volume categorized rows while reducing failed/source-gap dominance,
- making the live benchmark runner robust enough to complete the suite or emit partial-failure artifacts cleanly,
- proving at least one required live benchmark with nonzero high-trust usable output and no unsupported contacts.

## Next Main Promotion Recommendation

Do not sync `main`. The decision is `hold`, and `main` should not receive another operator-use promotion unless Matt explicitly asks after seeing this gate decision.

## Next Prompt A Assignment

None. Because the decision is `hold`, no downstream Prompt A feature and no RG4 design/mockup preflight is unlocked.

If Matt accepts this hold and wants another remediation, the next assignment should remain inside RG3. R10-R12 remain blocked. The refreshed mockup/design preflight from `DESIGN.md` remains blocked until a future Prompt C records RG3 `advance`.
