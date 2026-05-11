# Reset Gate Review - RG3 Validation, Conflict, And Gate Semantics

**Branch:** `audit/reset-rg3-tavily-rerun`
**Integration branch:** `rebuild/validated-leads-loop`
**Date:** 2026-05-11
**Decision:** hold
**Current product gate:** red

## Current State Proof

- Required control docs read before audit: `AGENTS.md`, `STATUS.md`, `docs/00-product-northstar.md`, `docs/12-reset-gated-implementation-plan-2026-05-10.md`, `docs/13-pipeline-orchestrator-contract-2026.md`, and `audits/zero-trust-codebase-audit-2026-05-10.md`.
- Supporting docs read: `docs/03-decisions.md`, `DESIGN.md`, `audits/raw/zero-trust-2026-05-10/evidence-ledger.md`, and `audits/raw/zero-trust-2026-05-10/operator-feedback-volume-2026-05-10.md`.
- Current gate from `docs/12-reset-gated-implementation-plan-2026-05-10.md`: `RG3 - Validation, Conflict, And Gate Semantics`, status `in_progress / gate_hold`.
- Initial `git status --short --branch` on the integration branch: `## rebuild/validated-leads-loop...origin/rebuild/validated-leads-loop`, clean.
- Integration head proof: local `HEAD` and `origin/rebuild/validated-leads-loop` both resolved to `df9e831`.
- Feature merge proof: `origin/feat/reset-r07-inclusive-extraction`, `origin/feat/reset-r08-tier-validation-conflicts`, `origin/feat/reset-r09-tier-summary-semantics`, `origin/feat/reset-r09a-live-value-recovery`, `origin/feat/reset-r09b-contact-evidence-acquisition`, and `origin/feat/reset-r09c-deep-multisource-evidence-tier-calibration` are all ancestors of `rebuild/validated-leads-loop`.
- Gate-not-advanced proof: `STATUS.md` and `docs/12-reset-gated-implementation-plan-2026-05-10.md` still listed RG3 as `in_progress / gate_hold`, with RG4, refreshed mockups, R10-R12, export work, dogfood, and `main` promotion blocked unless Prompt C records `advance`.

Raw proof is saved in `audits/raw/reset-2026-05-10/rg3/command-output-tavily-rerun.md`.

## Commands Run

```bash
git status --short --branch
git rev-parse --short HEAD
git rev-parse --short origin/rebuild/validated-leads-loop
git merge-base --is-ancestor origin/feat/reset-r07-inclusive-extraction HEAD
git merge-base --is-ancestor origin/feat/reset-r08-tier-validation-conflicts HEAD
git merge-base --is-ancestor origin/feat/reset-r09-tier-summary-semantics HEAD
git merge-base --is-ancestor origin/feat/reset-r09a-live-value-recovery HEAD
git merge-base --is-ancestor origin/feat/reset-r09b-contact-evidence-acquisition HEAD
git merge-base --is-ancestor origin/feat/reset-r09c-deep-multisource-evidence-tier-calibration HEAD
rg -n "Current reset gate|RG3|R09C|gate_advanced|Next Prompt A|Current Prompt C handoff" STATUS.md docs/12-reset-gated-implementation-plan-2026-05-10.md audits/gates/reset-2026-05-10/rg3-validation-semantics.md
cd packages/core && uv run pytest tests/test_query_planner.py tests/test_search.py tests/test_coverage.py tests/test_source_validation.py tests/test_contact_status.py tests/test_scoring.py tests/test_orchestrator.py tests/test_live_benchmark_runner.py tests/test_quality_report.py -q
cd apps/api && WR_API_INTERNAL_TOKEN=test-internal-token uv run pytest tests -q
git diff --check
cd apps/api && env -u OPENAI_API_KEY -u OPENAI_BASE_URL -u TAVILY_API_KEY uv run uvicorn api.main:app --host 127.0.0.1 --port 8018
curl -sS http://127.0.0.1:8018/health
set -a; . apps/api/.env; set +a; cd packages/core && uv run python -m core.live_benchmark_runner --api-base-url http://127.0.0.1:8018 --output-dir ../../audits/raw/reset-2026-05-10/rg3/live-tavily-rerun --mode scout --api-token [redacted]
jq condensed summaries over audits/raw/reset-2026-05-10/rg3/live-tavily-rerun/quality-summary.json
```

Verification results:

- Core RG3/R09C suite: `76 passed in 0.77s`.
- API suite: `45 passed, 52 warnings in 1.20s`; warnings are existing `datetime.utcnow()` deprecations.
- `git diff --check`: passed before audit edits.
- API health: `{"status":"ok"}`.

## Live Results

Artifact root: `audits/raw/reset-2026-05-10/rg3/live-tavily-rerun/`

| Benchmark | HTTP | Categorized rows | Person rows | High-trust usable | Contact-quality passes | Result |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
| Thomas Arizona K-12 | 200 | 9 | 0 | 0 | 0 | Failed value gate; source inaccessible/org-only blockers. |
| Lee commodity buyers | 599 | 0 | 0 | 0 | 0 | Runner timeout at 120s; failed volume. |
| Healthcare IT Phoenix | 200 | 50 | 0 | 0 | 0 | Failed persona/contact/source gate; 31 source-inaccessible and 19 conflicting-evidence blockers. |
| Finance CISOs New York | 599 | 0 | 0 | 0 | 0 | Runner timeout at 120s; failed volume. |
| Manufacturing ops Detroit | 200 | 50 | 3 | 0 | 0 | No parse crash; still failed contact/source gate. |
| B2C private phone guardrail | 422 | 0 | 0 | 0 | 0 | Expected privacy refusal. |

Suite summary:

- Total cases: `6`.
- Passed cases: `2`.
- Failed cases: `4`.
- Persona pass cases: `0`.
- Contact pass cases: `0`.
- Source pass cases: `0`.
- Privacy refusal cases: `1`.
- Guardrail mismatches: none.
- Observation mismatches: Lee volume, healthcare persona/contact/source, finance persona/contact/source/volume, and manufacturing persona/contact/source.

Theme summary:

- `broad_b2b`: `100` categorized rows, `3` person rows, `0` high-trust usable rows, `0` contact-quality passes, `5` contact-evidence candidates searched, and `0` contacts acquired.
- `named_account`: `9` categorized rows, `0` person rows, `0` high-trust usable rows, `0` contact-quality passes, `1` contact-evidence candidate searched, and `0` contacts acquired.
- `privacy_rejection`: expected refusal and no quality failures.

## Gate Criteria Review

- Manufacturing no longer shows the earlier 503 parse crash. It returned HTTP `200` and 50 categorized rows.
- The live quality summary reports funnel drop-offs and separates the privacy refusal from no-candidate product failures.
- Runner timeout behavior wrote partial failure artifacts for Lee and finance with HTTP `599` instead of silently aborting the whole suite.
- Missing-contact rows are not being promoted to CRM-ready output. The only person rows returned were three manufacturing rows, all `review`, `gate_passed=false`, and `email_status=missing`.
- Conflict handling is visible. Healthcare and manufacturing both downgrade conflicted rows; the condensed summary reports `19` conflicting-evidence blockers in each case.
- Broad volume is only partially recovered. Healthcare and manufacturing reached 50 categorized rows, but Lee and finance timed out with 0 categorized rows in the saved artifacts.
- The required advance criteria are not met because no required live benchmark produced nonzero `high_trust_usable` output, and no required live benchmark produced nonzero contact-quality passes.

## Value Prop Verdict

The current product does **not** give enough result volume, evidence, and export value for the operator loop.

Result volume is partially better than the original RG3 hold baseline because two broad B2B runs reached 50 categorized rows, but volume is not reliable enough: two broad B2B cases timed out and saved zero categorized output. Evidence value is still insufficient because every case and theme produced `0` high-trust usable rows and `0` contact-quality passes. Export value is not enough because the current product cannot hand Thomas or Lee validated CRM-ready rows; the only person rows sampled are non-CRM-ready `review` rows with missing contact evidence.

The product is safer than before because it avoids promoting weak rows as READY, but it is not yet useful enough as a validated query-to-export operator loop.

## Findings

1. **Hold blocker - high-trust usable output is still zero.** The reset advance criteria require at least one required live benchmark with nonzero `high_trust_usable` output without unsupported contacts. This re-run produced `0` high-trust usable rows in every case and theme.
2. **Hold blocker - contact-quality output is still zero.** The live suite produced `0` contact-quality passes and acquired `0` contacts across the benchmark set.
3. **Hold blocker - broad runtime reliability is not gate-safe.** Lee commodity buyers and finance CISOs both timed out at 120s and saved HTTP `599` artifacts.
4. **Partial pass - broad categorized volume can recover when runs complete.** Healthcare and manufacturing each reached 50 categorized rows, which is materially better than the old 7-10 row broad-output failure.
5. **Pass - manufacturing parse crash is not present in this run.** Manufacturing returned HTTP `200` and 50 categorized rows.
6. **Pass - privacy guardrail remains correct.** The homeowner-phone case returned HTTP `422` and was treated as an expected privacy refusal.
7. **Pass - weak person rows are not mislabeled CRM-ready.** All three sampled person rows were `review`, `gate_passed=false`, and missing contact evidence.

## What Worked

- R07-R09C are merged before the audit.
- Required core and API suites pass.
- The Tavily-credit re-run produced live artifacts rather than a pure vendor-credit blocker.
- The product now exposes the real choke point: source volume can be high while person extraction, contact acquisition, and high-trust yield remain zero.
- Failed/conflicted/source-inaccessible rows are visible as blockers instead of being hidden or promoted.

## What Did Not Work

- The current loop still produces no READY/high-trust rows.
- The current loop still produces no contact-quality passes.
- Runner timeouts make broad-query output unreliable for at least two required cases.
- Existing export work remains blocked because there are no validated rows worth exporting.

## Recommended Scope Change For Next Gate

Keep RG3 held. Do not start RG4 mockups, R10-R12 UI work, export work, dogfood, or a `main` sync.

If Matt accepts another remediation pass, it should stay inside RG3 and focus on either:

- proving public-web contact evidence is structurally unavailable for these benchmark themes and making a product-positioning/vendor decision, or
- improving the live pipeline so at least one required benchmark produces source-backed high-trust rows and contact-quality passes without relaxing the READY definition, while also eliminating broad runner timeouts.

## Next Main Promotion Recommendation

Do not sync `main`. The decision is `hold`, and `main` should not receive another operator-use promotion unless Matt explicitly asks after seeing this gate decision.

## Next Prompt A Assignment

None. Because the decision is `hold`, no downstream Prompt A feature, no RG4 design/mockup preflight, no R10-R12 work, and no export work is unlocked.

If Matt accepts this hold and wants another remediation, the next assignment must remain an explicitly approved RG3 remediation slice. The exact Prompt A assignment is intentionally not provided because Prompt C did not record `advance`.
