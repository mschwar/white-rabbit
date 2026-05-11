# RG3 Evidence Notes

Date: 2026-05-11
Branch: `audit/reset-rg3-validation-semantics-r09a`
Decision: `hold`

## State Proof

- `STATUS.md` and `docs/12-reset-gated-implementation-plan-2026-05-10.md` identify RG3 as ready for Prompt C audit after R09A Prompt B QA.
- The reset gate table shows RG3 as `gate_pending_audit`, not advanced.
- The reset feature table shows R07, R08, R09, and R09A as `merged_to_rebuild_branch`.
- `git merge-base --is-ancestor` returned success for all four RG3 feature branches against `rebuild/validated-leads-loop`.
- Existing RG3 report was the pre-R09A accepted hold; R09A is a merged remediation slice, so this is a valid RG3 re-audit rather than a rerun of a completed advanced gate.
- `DESIGN.md` was present and read only as future RG4 direction. It did not influence the data-quality decision.

## Live Benchmark Summary

Fresh live Scout suite output is under `audits/raw/reset-2026-05-10/rg3/live-r09a/`.

- Thomas Arizona K-12: HTTP 200, 10 categorized rows, 2 person rows, 0 high-trust usable, 0 contact passes, `volume_floor_status=minimum_met`.
- Lee commodity buyers: HTTP 200, 50 categorized rows, 3 person rows, 0 high-trust usable, 0 contact passes, `volume_floor_status=target_met`.
- Healthcare IT Phoenix: HTTP 200, 50 categorized rows, 3 person rows, 0 high-trust usable, 0 contact passes, `volume_floor_status=target_met`.
- Finance CISOs New York: HTTP 200, 50 categorized rows, 7 person rows, 0 high-trust usable, 0 contact passes, `volume_floor_status=target_met`.
- Manufacturing ops Detroit: HTTP 200, 50 categorized rows, 1 person row, 0 high-trust usable, 0 contact passes, `volume_floor_status=target_met`.
- Privacy homeowner phones: HTTP 422, `quality_status=expected_privacy_refusal`.

Suite totals:

- `total_cases=6`
- `passed_cases=3`
- `failed_cases=3`
- `privacy_refusal_cases=1`
- `persona_pass_cases=0`
- `contact_pass_cases=0`
- `source_pass_cases=0`

## Funnel Evidence

R09A materially improved result volume and observability:

- Lee commodity buyers: `raw_vendor_hits=240`, `deduped_sources=195`, `source_snapshots=195`, `extracted_candidates=5`, `categorized_rows=50`, `high_trust_usable_rows=0`.
- Healthcare IT Phoenix: `raw_vendor_hits=240`, `deduped_sources=160`, `source_snapshots=160`, `extracted_candidates=10`, `categorized_rows=50`, `high_trust_usable_rows=0`.
- Finance CISOs New York: `raw_vendor_hits=240`, `deduped_sources=163`, `source_snapshots=163`, `extracted_candidates=11`, `categorized_rows=50`, `high_trust_usable_rows=0`.
- Manufacturing ops Detroit: `raw_vendor_hits=227`, `deduped_sources=155`, `source_snapshots=155`, `extracted_candidates=7`, `categorized_rows=50`, `high_trust_usable_rows=0`.
- Thomas Arizona K-12: `raw_vendor_hits=56`, `deduped_sources=50`, `source_snapshots=50`, `extracted_candidates=9`, `categorized_rows=10`, `high_trust_usable_rows=0`.

## Row-Level Findings

- `person-row-sample-r09a.json` samples 10 live person rows across finance, healthcare, Lee, manufacturing, and Thomas cases.
- All sampled person rows are `tier=review` with `gate_passed=false`.
- Sampled person rows with `email_status=missing` or `email_status=unsupported` are not CRM-ready.
- `failed-row-sample-r09a.json` shows failed/source-gap rows are explicit `failed` rows, not hidden usable leads.
- `manufacturing-inspection-r09a.json` proves the manufacturing run no longer returns the old HTTP 503 parse crash. It returns 50 categorized rows with 1 `review`, 1 `organization_only`, 1 `not_found`, 47 `failed`, and 0 `high_trust_usable`.

## Decision Rationale

RG3 should remain held. R09A fixed the broad volume starvation and made the funnel observable, but RG3's advance criteria still require at least one required live benchmark with nonzero `high_trust_usable` output without unsupported contacts. The fresh suite produced zero high-trust usable rows and zero contact-quality passes. The product now shows the candidate universe more honestly, but it still does not provide enough evidence-backed, export-worthy sales value for the operator loop.
