# RG1 Evidence Notes - Operator Benchmark Harness

**Date:** 2026-05-10
**Branch:** `audit/reset-rg1-benchmark-harness`
**Integration branch:** `rebuild/validated-leads-loop`

## Gate Readiness

- `STATUS.md` identified `RG1 - Operator Benchmark Harness` as `gate_pending_audit`.
- `docs/12-reset-gated-implementation-plan-2026-05-10.md` listed RG1 as `gate_pending_audit` and R01-R03 as the gate feature range.
- `git branch --all --merged rebuild/validated-leads-loop` showed `feat/reset-r01-operator-evidence-fixtures`, `feat/reset-r02-benchmark-replay-harness`, and `feat/reset-r03-live-benchmark-runner` merged into the integration branch.
- `find audits/gates/reset-2026-05-10 -maxdepth 1 -type f | sort` showed only `rg0-w5-hold.md`, so RG1 had not already advanced and had not already been audited.

## Replay Evidence

- Replay benchmark command passed: `16 passed, 1 skipped in 0.30s`.
- This proves the benchmark suite is reproducible without live keys and includes Arizona K-12, Lee commodity buyers, healthcare IT Phoenix, finance CISOs New York, manufacturing ops Detroit, and B2C/private refusal cases.

## Live Evidence

Fresh live runner output was saved under this directory on 2026-05-10:

- `quality-summary.json`
- `thomas-arizona-k12.json` and `.http`
- `lee-commodity-buyers.json` and `.http`
- `healthcare-it-phoenix.json` and `.http`
- `finance-cisos-new-york.json` and `.http`
- `manufacturing-ops-detroit.json` and `.http`
- `privacy-reject-homeowner-phones.json` and `.http`

Suite summary from `quality-summary.json`:

| Case | HTTP | Categorized rows | High-trust usable | Key result |
| --- | ---: | ---: | ---: | --- |
| `thomas-arizona-k12` | 200 | 9 | 0 | Covered 7 of 8 named targets; missed Maricopa Unified School District. |
| `lee-commodity-buyers` | 200 | 2 | 0 | Failed volume, persona, contact, and source expectations. |
| `healthcare-it-phoenix` | 200 | 2 | 0 | Failed persona, contact, source, and volume expectations; one fake email flagged. |
| `finance-cisos-new-york` | 200 | 3 | 0 | Failed contact and volume expectations. |
| `manufacturing-ops-detroit` | 503 | 0 | 0 | Still crashes as `openai_failed`; this must become recoverable in RG3. |
| `privacy-reject-homeowner-phones` | 422 | 0 | 0 | Privacy-sensitive request blocked before search. |

Overall live suite: 6 cases, 1 passed, 5 failed, 0 guardrail mismatches.

## Gate Interpretation

RG1 advances only as a harness gate. It does not prove the product is useful yet.

The harness can now:

- fail low-volume broad outputs instead of treating 2-3 rows as enough,
- track target coverage for Thomas's named-account Arizona prompt,
- save live JSON and HTTP evidence for every benchmark case,
- preserve a quality summary with observation mismatches,
- prove the B2C/private guardrail blocks before search.

Carry-forward blockers:

- Current product result volume is still far below the northstar for broad prompts.
- Current live output has 0 high-trust usable leads in the non-privacy cases.
- Manufacturing role-as-name still returns a 503 instead of a recoverable failed row; R07/RG3 must fix this before validation semantics can advance.
- Export value remains unproven by RG1 because the live runner exercises Scout mode only; RG5 must inspect UI, CSV, and DB readback.
