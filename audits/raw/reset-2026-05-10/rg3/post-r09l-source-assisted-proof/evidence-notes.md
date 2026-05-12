# RG3 Post-R09L Source-Assisted Proof Evidence Notes

**Date:** 2026-05-12
**Branch:** `audit/reset-rg3-validation-semantics`
**Decision supported:** `advance`

## State Proof

- `commands/git-status-initial.txt` shows the audit ran on `audit/reset-rg3-validation-semantics` from `origin/rebuild/validated-leads-loop`.
- `commands/merge-proof.txt` proves every RG3 feature branch from R07 through R09L is an ancestor of `origin/rebuild/validated-leads-loop`.
- `commands/gate-state-proof.txt` shows RG3 was still `gate_hold` in the gate table before this audit and had not already advanced.

## Verification Proof

- `commands/core-rg3-suite.txt`: `87 passed`.
- `commands/api-suite.txt`: `51 passed`, with existing datetime warnings.
- `commands/git-diff-check-before-report.txt`: no whitespace errors before report edits.

## Runtime Proof

- `commands/api-health-8027.status`: `/health` returned `200` in `0.004302s`.
- `commands/api-readiness-8027.status`: `/readiness` returned `200` in `0.469401s`.
- `commands/api-readiness-8027-summary.json`: readiness reported bounded, separated checks for process, config, database, OpenAI, Tavily, and sandbox. The local audit environment is not fully ready, but the endpoint no longer hangs.
- `commands/source-assisted-proof-no-token.status`: protected source-assisted route returned `401` without the internal token.
- `commands/source-assisted-proof-token.status`: protected source-assisted route returned `200` with the internal token.

## Source-Assisted Value Proof

- `source-assisted-proof-live-response.json`: canonical live response from the protected `/source-assisted-proof` route.
- `commands/source-assisted-proof-live-summary.json`: compact proof summary:
  - `passes=true`
  - 7 source-map districts
  - 13 source-map seeds
  - 0 generic search sources
  - 17 source-assisted candidates
  - 18 source-assisted sources
  - 17 workbook rows
  - 10 `READY_WITH_CONTACT`
  - 7 `MANUAL_LOOKUP`
  - 0 unsupported CRM-ready rows
  - 0 manual-lookup CRM-ready rows
  - private contact values redacted
- `commands/source-assisted-proof-sampled-rows.json`: first 10 ready rows have source URLs for name, title, organization, and email status, plus redacted verified-contact notes.
- `commands/source-assisted-proof-manual-lookup-rows.json`: all 7 manual-lookup rows are non-CRM-ready, preserve source URLs, and include next actions.
- `commands/private-contact-redaction-check.txt`: no `@` values were found in the live response artifact.

## Caveats Preserved

- `commands/r09a-live-summary.json` preserves the latest complete saved autonomous broad Scout suite caveat: broad row volume improved in R09A, but high-trust usable rows and contact-quality cases remained zero.
- `commands/r09k-sandbox-timeout-summary.json` proves the timeout path is now structured as artifact-backed failure evidence.
- This audit advances RG3 only for the source-assisted validation/runtime path. It does not mark the product yellow/green, does not prove autonomous broad Scout as the near-term value path, and does not unlock `main` promotion.
