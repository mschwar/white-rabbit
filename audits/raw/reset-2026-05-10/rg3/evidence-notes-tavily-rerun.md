# RG3 Tavily Credit Re-run Evidence Notes

Date: 2026-05-11
Branch: `audit/reset-rg3-tavily-rerun`
Integration branch audited: `rebuild/validated-leads-loop`

## Current State Proof

- `AGENTS.md`, `STATUS.md`, `docs/00-product-northstar.md`, `docs/12-reset-gated-implementation-plan-2026-05-10.md`, `docs/13-pipeline-orchestrator-contract-2026.md`, and `audits/zero-trust-codebase-audit-2026-05-10.md` were read before the audit.
- `docs/12-reset-gated-implementation-plan-2026-05-10.md` identified the current reset gate as `RG3 - Validation, Conflict, And Gate Semantics`, status `in_progress / gate_hold`.
- `git status --short --branch` before audit branch creation showed `## rebuild/validated-leads-loop...origin/rebuild/validated-leads-loop` with a clean worktree.
- `git rev-parse --short HEAD` and `git rev-parse --short origin/rebuild/validated-leads-loop` both returned `df9e831`.
- `git merge-base --is-ancestor` confirmed these RG3 feature refs were merged before auditing: `origin/feat/reset-r07-inclusive-extraction`, `origin/feat/reset-r08-tier-validation-conflicts`, `origin/feat/reset-r09-tier-summary-semantics`, `origin/feat/reset-r09a-live-value-recovery`, `origin/feat/reset-r09b-contact-evidence-acquisition`, and `origin/feat/reset-r09c-deep-multisource-evidence-tier-calibration`.
- `rg` over `STATUS.md`, `docs/12-reset-gated-implementation-plan-2026-05-10.md`, and the existing RG3 gate report confirmed the gate had not already advanced. RG3 remained `in_progress / gate_hold`, and downstream RG4/R10/export/main promotion remained blocked.
- Raw proof is captured in `audits/raw/reset-2026-05-10/rg3/command-output-tavily-rerun.md`.

## Verification Commands

- Core RG3/R09C suite passed: `76 passed in 0.77s`.
- API suite passed: `45 passed, 52 warnings in 1.20s`. Warnings are existing `datetime.utcnow()` deprecations.
- `git diff --check` passed before audit edits.
- Local API health check on `http://127.0.0.1:8018/health` returned `{"status":"ok"}`.

## Live Benchmark Evidence

Artifact root: `audits/raw/reset-2026-05-10/rg3/live-tavily-rerun/`

The Tavily-credit re-run completed enough live work to move the blocker from vendor-credit uncertainty to product-value failure:

- Total cases: `6`.
- Passed cases: `2`.
- Failed cases: `4`.
- Persona pass cases: `0`.
- Contact pass cases: `0`.
- Source pass cases: `0`.
- Privacy refusal cases: `1`.
- Guardrail mismatches: none.
- Observation mismatches: `lee-commodity-buyers: volume`, `healthcare-it-phoenix: persona, contact, source`, `finance-cisos-new-york: persona, contact, source, volume`, and `manufacturing-ops-detroit: persona, contact, source`.

Theme summary:

- `broad_b2b`: `100` categorized rows, `3` person rows, `0` high-trust usable rows, `0` contact-quality passes, `5` contact-evidence candidates searched, and `0` contacts acquired.
- `named_account`: `9` categorized rows, `0` person rows, `0` high-trust usable rows, `0` contact-quality passes, `1` contact-evidence candidate searched, and `0` contacts acquired.
- `privacy_rejection`: expected refusal with `0` categorized rows and `0` quality failures.

Case summary:

| Case | HTTP | Categorized | Person | High-trust usable | Contact-quality passes | Key blocker |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
| `thomas-arizona-k12` | 200 | 9 | 0 | 0 | 0 | Source inaccessible and org-only output. |
| `lee-commodity-buyers` | 599 | 0 | 0 | 0 | 0 | Runner timeout after 120s; volume failed. |
| `healthcare-it-phoenix` | 200 | 50 | 0 | 0 | 0 | `31` source-inaccessible blockers and `19` conflicting-evidence blockers. |
| `finance-cisos-new-york` | 599 | 0 | 0 | 0 | 0 | Runner timeout after 120s; volume failed. |
| `manufacturing-ops-detroit` | 200 | 50 | 3 | 0 | 0 | `19` conflicting-evidence, `3` no-contact-source, `2` organization-only, and `26` source-inaccessible blockers. |
| `privacy-reject-homeowner-phones` | 422 | 0 | 0 | 0 | 0 | Expected privacy refusal. |

## Contact And CRM-Ready Evidence

Only `manufacturing-ops-detroit` produced person rows in the live re-run. All three were `review`, `gate_passed=false`, with missing email/contact evidence:

- Bruce Smith, Detroit Manufacturing Systems LLC, CEO: `email_status=missing`, reason says deeper public-web pass did not find a direct email or explicit domain-pattern source.
- Jim Schmidt, Oliver Wyman, Vice President: `email_status=missing`, reason says row is not CRM-ready.
- Nigel Francis, LIFT, CEO: `email_status=missing`, reason says deeper public-web pass did not find a direct email or explicit domain-pattern source.

This confirms missing-contact rows are not being promoted to CRM-ready output, but it also confirms the current loop still produces no exportable high-trust rows.

## Gate Decision Evidence

Decision: `hold`.

The gate cannot advance because the required live evidence still fails both value criteria that matter most for the operator loop:

- `high_trust_usable_rows` is `0` for every live case and every theme.
- `contact_quality_passes` is `0` for every live case and every theme.
- Two broad B2B cases timed out with HTTP `599`, so the live runner and/or product path is not reliable enough for gate advancement.
- Two broad B2B cases did reach `50` categorized rows, which proves volume can recover when the runner completes, but the output still lacks validated contact evidence and export-ready rows.

## Promotion And Queue Consequence

- Do not sync `main`.
- Do not unlock RG4, refreshed mockups, R10-R12, export work, dogfood, or production UI work.
- No next Prompt A assignment is valid unless Matt accepts or revises another RG3 remediation slice.
