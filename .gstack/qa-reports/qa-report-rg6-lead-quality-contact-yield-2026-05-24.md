# QA Report - RG6 Lead Quality / Contact Yield Remediation

**Date:** 2026-05-24
**Prompt:** Prompt B QA
**Branch:** `fix/rg6-lead-quality-contact-yield`
**Base:** `main` at `9f890bc` after control-plane routing repair
**Feature commit:** `7c5ece9 fix: remediate rg6 lead quality evidence`
**Decision:** QA passed; merge to `main`.

## Scope Reviewed

- Shared core READY policy in `packages/core/src/core/lead_quality_policy.py`.
- Orchestrator, quality-report, and benchmark-summary reuse of that policy.
- Arizona K-12 named-account query expansion with bounded role/source variants.
- Official-source contact evidence promotion/blocking, including third-party directory and shared-public-suffix rejection.
- Deterministic sampled-precision packet tooling.
- Primary CSV export auto-close using persisted `run_id` and elapsed operator minutes.
- Type/test updates for emitted funnel counts.
- Assignment-lock/status docs for the waiting Prompt B handoff.

## Scope Boundaries

Confirmed branch diff excludes public SaaS, account/org/billing, signup, recipe-library promotion, batch promotion, dogfood/yellow/green claims, and external `proxy-lead` edits.

## Verification

```bash
cd packages/core && PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 uv run pytest tests -q
# 161 passed, 6 skipped

cd apps/api && WR_API_INTERNAL_TOKEN=test-internal-token uv run pytest tests -q
# 56 passed, 82 existing datetime.utcnow deprecation warnings

cd apps/web && npm test -- --run
# 15 files passed, 37 tests passed

cd apps/web && npm run build
# passed; existing Next.js middleware-to-proxy warning

git diff --check
# passed
```

Browser QA used local Next dev at `http://127.0.0.1:3010` with test auth and mocked `/api/scout` plus `/api/runs/browser-rg6-run-1/close`. It verified primary results, evidence review, export, and auto-close behavior with `operator_minutes=0.01`.

Screenshots and browser summary:

- `.gstack/qa-reports/screenshots/rg6-lead-quality-contact-yield-2026-05-24/01-primary-results.png`
- `.gstack/qa-reports/screenshots/rg6-lead-quality-contact-yield-2026-05-24/02-evidence-review.png`
- `.gstack/qa-reports/screenshots/rg6-lead-quality-contact-yield-2026-05-24/03-export-auto-close.png`
- `.gstack/qa-reports/screenshots/rg6-lead-quality-contact-yield-2026-05-24/browser-qa-summary.json`

## Findings

No blocking findings.

The implementation keeps READY strict. `lead_is_ready_eligible` requires a person lead, supported name/title/organization/source, source-backed contact status, and threshold scores. `ready_blocker_for_candidate` no longer trusts a preexisting `high_trust_usable` tier without required field/contact support.

Contact evidence promotion is source-backed. Direct emails require candidate name plus organization/title on an authoritative same-domain source or qualifying board PDF, and explicit pattern emails must match a candidate source domain. Tests cover rejection of third-party directory mirrors and unrelated shared public suffix domains.

The sampled-precision tooling is deterministic and report-shaped, but it is evidence tooling only. It does not itself satisfy RG6 sampled precision until run against the required production benchmark outputs.

The primary export close behavior is low ceremony and uses existing `/runs/{run_id}/close` plus `RecipeRun.operator_minutes`. Browser QA and Vitest confirm a persisted primary Scout run closes once on export with a positive elapsed-minute payload.

## Residual Gate Risk

This QA does not clear RG6. It proves the remediation branch is mergeable and locally verified. A later Prompt C gate record still must rerun live Arizona K-12, generate sampled precision from required outputs, and capture a timed no-assistance operator run against the stable alias before any yellow/green or dogfood claim.
