# RG3 Evidence Notes

Date: 2026-05-11
Branch: audit/reset-rg3-validation-semantics
Decision: hold

## State Proof

- `STATUS.md` and `docs/12-reset-gated-implementation-plan-2026-05-10.md` both identify RG3 as ready for Prompt C audit.
- Reset feature table shows R07, R08, and R09 merged to `rebuild/validated-leads-loop`.
- Existing gate reports stop at RG2; no RG3 report existed before this audit.
- `DESIGN.md` was present and read as future RG4 direction only.

## Live Benchmark Summary

Live Scout suite output is under `audits/raw/reset-2026-05-10/rg3/live/`.

- Thomas Arizona K-12: 200, 9 categorized rows, 0 high-trust usable, 2 review, 3 organization-only, 4 failed.
- Lee commodity buyers: 200, 7 categorized rows, 0 high-trust usable, high-volume floor false.
- Healthcare IT Phoenix: 200, 10 categorized rows, 0 high-trust usable.
- Finance CISOs New York: 200, 7 categorized rows, 0 high-trust usable, high-volume floor false.
- Manufacturing ops Detroit: 200, 8 categorized rows, 0 high-trust usable, high-volume floor false. This proves the old 503 parse-crash path is fixed.
- Privacy homeowner phones: 422, guardrail blocked before search.

## Row-Level Findings

- `person-row-sample.json` sampled 12 live person rows. All are `tier: review` with `gate_passed: false`.
- Sampled person rows with `email_status: missing` or `unsupported` are not CRM-ready.
- `failed-row-sample.json` shows inaccessible LinkedIn/403 cases become `failed` rows with failed validation, not usable rows.
- `manufacturing-inspection.json` shows manufacturing now returns explicit review/org-only/not-found/failed rows instead of an HTTP 503.

## Decision Rationale

RG3 semantics improved, but the gate does not advance because live operator value remains below the reset bar: broad outputs are too small, contact quality is zero, and all benchmarks have zero high-trust usable rows. The product is safer, but not yet useful enough to unlock RG4 design work.
