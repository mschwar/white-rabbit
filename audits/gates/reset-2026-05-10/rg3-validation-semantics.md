# Reset Gate Review - RG3 Validation, Conflict, And Gate Semantics

**Branch:** `audit/reset-rg3-validation-semantics-r09a`
**Integration branch:** `rebuild/validated-leads-loop`
**Date:** 2026-05-11
**Decision:** hold
**Current product gate:** red

## Evidence Used

- Required state docs: `AGENTS.md`, `STATUS.md`, `docs/00-product-northstar.md`, `docs/12-reset-gated-implementation-plan-2026-05-10.md`, `docs/13-pipeline-orchestrator-contract-2026.md`, and latest ADRs in `docs/03-decisions.md`.
- `DESIGN.md` was read only as future RG4 visual direction. It is not evidence that this data-quality gate passed.
- Baseline audit: `audits/zero-trust-codebase-audit-2026-05-10.md`.
- R09A QA handoff: `.gstack/qa-reports/qa-report-r09a-live-value-recovery-2026-05-11.md` and `.gstack/qa-reports/r09a-live-value-recovery-note-2026-05-11.md`.
- Fresh live benchmark output: `audits/raw/reset-2026-05-10/rg3/live-r09a/`.
- Fresh row inspections: `audits/raw/reset-2026-05-10/rg3/person-row-sample-r09a.json`, `audits/raw/reset-2026-05-10/rg3/failed-row-sample-r09a.json`, and `audits/raw/reset-2026-05-10/rg3/manufacturing-inspection-r09a.json`.
- Command log: `audits/raw/reset-2026-05-10/rg3/commands/command-output.md`.

## Commands Run

```bash
git status --short --branch
git log --oneline --decorate -8 --first-parent
git merge-base --is-ancestor feat/reset-r07-inclusive-extraction rebuild/validated-leads-loop
git merge-base --is-ancestor feat/reset-r08-tier-validation-conflicts rebuild/validated-leads-loop
git merge-base --is-ancestor feat/reset-r09-tier-summary-semantics rebuild/validated-leads-loop
git merge-base --is-ancestor feat/reset-r09a-live-value-recovery rebuild/validated-leads-loop
cd packages/core && uv run pytest tests/test_query_planner.py tests/test_search.py tests/test_coverage.py tests/test_source_validation.py tests/test_contact_status.py tests/test_scoring.py tests/test_orchestrator.py tests/test_live_benchmark_runner.py tests/test_quality_report.py -q
cd apps/api && WR_API_INTERNAL_TOKEN=test-internal-token uv run pytest tests -q
cd apps/web && npm test -- --run
cd apps/web && npm run build
cd apps/api && env -u OPENAI_API_KEY -u OPENAI_BASE_URL -u OPENAI_MODEL uv run uvicorn api.main:app --host 127.0.0.1 --port 8015
cd packages/core && env -u OPENAI_API_KEY -u OPENAI_BASE_URL -u OPENAI_MODEL uv run python -m core.live_benchmark_runner --api-base-url http://127.0.0.1:8015 --output-dir ../../audits/raw/reset-2026-05-10/rg3/live-r09a --mode scout --api-token [redacted]
```

Results:

- Current branch before audit branch creation was clean and aligned: `rebuild/validated-leads-loop...origin/rebuild/validated-leads-loop`.
- RG3 current gate status was `gate_pending_audit`; RG0-RG2 were already advanced and RG4-RG6 were blocked.
- R07, R08, R09, and R09A are ancestors of `rebuild/validated-leads-loop`.
- Core R09A/RG3 suite: `70 passed`.
- API suite: `45 passed`, with existing datetime deprecation warnings.
- Web regression suite: `13` files / `30` tests passed.
- Web build passed with existing Next.js workspace-root and middleware/proxy warnings.
- Fresh live Scout suite completed under the local API on port `8015`; all artifacts were saved under `audits/raw/reset-2026-05-10/rg3/live-r09a/`.

## Live Results

| Benchmark | HTTP | Categorized rows | Person rows | READY / high trust | Review | Org-only | Not found | Failed | Volume status | Contact passes |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | ---: |
| Thomas Arizona K-12 | 200 | 10 | 2 | 0 | 2 | 1 | 3 | 4 | `minimum_met` | 0 |
| Lee commodity buyers | 200 | 50 | 3 | 0 | 3 | 1 | 1 | 45 | `target_met` | 0 |
| Healthcare IT Phoenix | 200 | 50 | 3 | 0 | 3 | 1 | 0 | 46 | `target_met` | 0 |
| Finance CISOs New York | 200 | 50 | 7 | 0 | 7 | 1 | 1 | 41 | `target_met` | 0 |
| Manufacturing ops Detroit | 200 | 50 | 1 | 0 | 1 | 1 | 1 | 47 | `target_met` | 0 |
| B2C private phone guardrail | 422 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | `expected_privacy_refusal` | n/a |

The live runner recorded `total_cases=6`, `passed_cases=3`, `failed_cases=3`, `privacy_refusal_cases=1`, `persona_pass_cases=0`, `contact_pass_cases=0`, and `source_pass_cases=0`. The failed evaluated cases are healthcare, finance, and manufacturing, with persona/contact/source mismatches. All non-private evaluated cases still have `high_trust_usable_count=0`.

Funnel counts now prove the R09A volume recovery path:

| Benchmark | Raw vendor hits | Deduped sources | Source snapshots | Extracted candidates | Categorized rows | High-trust rows |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Thomas Arizona K-12 | 56 | 50 | 50 | 9 | 10 | 0 |
| Lee commodity buyers | 240 | 195 | 195 | 5 | 50 | 0 |
| Healthcare IT Phoenix | 240 | 160 | 160 | 10 | 50 | 0 |
| Finance CISOs New York | 240 | 163 | 163 | 11 | 50 | 0 |
| Manufacturing ops Detroit | 227 | 155 | 155 | 7 | 50 | 0 |

## Screenshots And Artifacts

No new screenshots were required because RG3 is a data-quality and semantics gate, not a UI implementation gate. Existing R09 Prompt B fixture screenshots remain at:

- `.gstack/qa-reports/screenshots/r09-prompt-b-desktop.png`
- `.gstack/qa-reports/screenshots/r09-prompt-b-mobile.png`

Fresh raw audit artifacts:

- `audits/raw/reset-2026-05-10/rg3/live-r09a/quality-summary.json`
- `audits/raw/reset-2026-05-10/rg3/live-r09a/*.json`
- `audits/raw/reset-2026-05-10/rg3/live-r09a/*.http`
- `audits/raw/reset-2026-05-10/rg3/person-row-sample-r09a.json`
- `audits/raw/reset-2026-05-10/rg3/failed-row-sample-r09a.json`
- `audits/raw/reset-2026-05-10/rg3/manufacturing-inspection-r09a.json`
- `audits/raw/reset-2026-05-10/rg3/evidence-notes.md`

## Value Prop Verdict

The current product does **not** give enough combined result volume, evidence, and export value for the operator loop.

Result volume is materially better after R09A: broad live Scout cases now return 50 categorized rows, and the named-account Thomas case represents all 8 expected accounts across explicit categories. That clears the old 3-4 row starvation failure for broad cases.

Evidence and export value are still not good enough. The fresh live suite produced 0 `high_trust_usable` rows, 0 contact-quality passes, 0 source-pass cases, and no evaluated case with a CRM-ready contact. A sales-first export cannot create operator value from a result set whose only person rows are `review` because contact evidence is missing or unsupported. Volume is now visible, but the usable-lead loop is still not useful enough.

## Findings

1. **Hold blocker - RG3 still fails the explicit advance criterion for usable output.** The reset plan requires at least one required live benchmark to produce nonzero `high_trust_usable` output without unsupported contacts. This audit produced zero high-trust rows across every evaluated benchmark.
2. **Hold blocker - contact/value recovery remains zero.** `contact_pass_cases=0`, every non-private evaluated case has `contact_quality_passes=0`, and the 10 sampled person rows are all `review` with `gate_passed=false`.
3. **Pass - R09A recovered broad categorized volume.** Lee, healthcare, finance, and manufacturing now each returned 50 categorized rows with funnel counts showing source-to-row drop-offs. The broad low-volume failure from the prior RG3 hold is materially improved.
4. **Pass - manufacturing no longer crashes.** The manufacturing benchmark returned HTTP 200 with 50 categorized rows, including 1 `review`, 1 `organization_only`, 1 `not_found`, and 47 `failed` rows. The old role-as-name parse crash is gone.
5. **Pass - privacy-sensitive query handling is now correctly separated.** The homeowner phone query returned 422 with `quality_status=expected_privacy_refusal`, not a no-candidate product failure.
6. **Pass with caution - score semantics are safer but still uncomfortable.** Sampled review rows are not CRM-ready and carry contact-missing/unsupported reasons. Some review rows still show high fit/evidence scores, so the UI/export path must keep the tier and primary reason dominant over raw score values.
7. **Pass with caution - failed-row language improved but still uses `REVIEW:` on failed rows.** Failed source-gap rows now say no usable lead is implied, but the prefix can still blur operator state. This is not enough to hold by itself, but it should be cleaned up in the next remediation if the hold is accepted.

## What Worked

- Required core/API/web verification passed.
- R07-R09A are merged into `rebuild/validated-leads-loop`.
- Broad source recovery now preserves high-volume source gaps as explicit non-ready rows instead of silently dropping them.
- Missing or unsupported contacts are not labeled CRM-ready in sampled person rows.
- Inaccessible and unsupported sources downgrade rows instead of validating them.
- The live quality summary now reports funnel counts and treats privacy refusal separately from product no-candidate failures.

## What Did Not Work

- No live benchmark produced a high-trust usable row.
- No evaluated case had contact-quality passes.
- Healthcare, finance, and manufacturing still fail persona/contact/source quality checks.
- Thomas named-account output covers targets but still has only 2 person rows and no CRM-ready contact.
- Export value remains theoretical at this gate because there are no READY rows worth exporting for the operator loop.

## New Gaps Found

- R09A fixed broad result volume, which makes the next bottleneck sharper: extraction/verification can collect many sources but still cannot recover verified or pattern-supported contacts.
- Source support is still too coarse for READY promotion. The product can support name/title/org on some rows, but contact status remains missing or unsupported.
- `guardrail_status` for some evaluated B2B benchmarks is `needs_more_detail` even when the API runs and returns useful coverage categories. That may be acceptable internally, but it should not confuse future gate summaries.
- Failed rows that are intentionally non-actionable should use `FAILED:` or `NOT FOUND:` rather than a `REVIEW:` prefix when there is no human-reviewable person.

## Recommended Scope Change For Next Gate

Keep RG3 held. If Matt accepts this hold, add one narrow RG3 remediation slice focused on contact/value recovery rather than more UI or export work:

- produce at least one live benchmark with nonzero `high_trust_usable` rows without unsupported contacts,
- add source-backed domain-pattern or verified-contact recovery where evidence supports it,
- preserve R09A's 50-row broad visibility and funnel reporting,
- clean failed-row operator-state prefixes so failed/source-gap rows cannot look review-worthy,
- rerun this RG3 audit and require nonzero high-trust usable output before RG4 design preflight.

Do not start RG4 mockups, R10-R12, export, persistence, dogfood, or a `main` sync from this audit.

## Next Main Promotion Recommendation

Do not sync `main`. `main` remains the Matt-directed Thomas/Lee internal-use exception from ADR-010, not proof that quality gates passed. This audit records a hold, so there is no new operator-use promotion recommendation.

## Next Prompt A Assignment

None. Because the decision is `hold`, no downstream Prompt A feature and no RG4 design/mockup preflight is unlocked.

If Matt accepts the hold and wants one more remediation pass, the next assignment should be a new RG3 remediation slice on `rebuild/validated-leads-loop` focused only on contact/value recovery and failed-row state language. R10-R12 remain blocked, and the refreshed mockup/design preflight from `DESIGN.md` remains blocked until a future Prompt C records RG3 `advance`.
