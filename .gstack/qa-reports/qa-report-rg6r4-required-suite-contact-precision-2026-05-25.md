# QA Report - RG6R4 Required-Suite Contact Precision

**Date:** 2026-05-25 local / 2026-05-26 UTC
**Prompt:** Prompt B QA
**Branch:** `fix/rg6r4-required-suite-contact-precision`
**Base:** `main` at `9a09c58`
**Feature commit:** `16c6597 fix: improve rg6 required-suite contact precision`
**Decision:** QA blocked; do not merge to `main`.

## Scope Reviewed

- Core contact-evidence promotion for person-matching direct emails on official contact/staff sources.
- Regression coverage for official contact-source acceptance and official non-contact-source rejection.
- Web middleware regression coverage for protected API boundaries.

Confirmed the branch does not add public SaaS, accounts, orgs, billing, recipe-library, batch, Friday review, or external self-serve scope.

## Verification

```bash
cd packages/core && PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 uv run pytest tests -q
# 176 passed, 6 skipped

cd apps/api && WR_API_INTERNAL_TOKEN=test-internal-token uv run pytest tests -q
# 57 passed, existing datetime.utcnow warnings

cd apps/web && npm test -- --run
# 16 files, 39 tests passed

cd apps/web && npm run build
# passed, existing Next.js middleware deprecation warning

git diff --check main...HEAD
# passed
```

## Fresh Evidence

Deployed RG6R4 API image for evidence only:

- Branch image: `registry.fly.io/white-rabbit-api:deployment-01KSH6T2FCA91NMVR5KQVQ60XR`
- Evidence path: `audits/raw/reset-2026-05-10/rg6/rg6r4-required-suite-contact-precision-2026-05-25/`

Web/API boundary evidence:

- Direct Fly `/health`: `200`
- Direct Fly `/readiness`: `200`, body status `ready`
- Direct tokenless Fly `/scout`: `401`
- Authenticated stable web login: `200`
- Authenticated web `/api/source-assisted-proof`: `200`
- Authenticated web `/api/sandbox` reset: `200`
- Local middleware regression: unauthenticated protected API returns `401`; valid shared-password session cookie passes middleware.

Required-suite product evidence:

- Product benchmark cases returned `503 tavily_failed`.
- Tavily error: pay-as-you-go limit exceeded.
- Privacy refusal still returned `422`.
- Sampled precision packet has `sampled_row_count=0`; contact precision is `0.000`.

## Precision Delta

Compared against RG6R3 direct evidence at `audits/raw/reset-2026-05-10/rg6/rg6r3-arizona-source-remediation-2026-05-25-direct/`.

| Metric | RG6R3 baseline | RG6R4 fresh | Delta |
| --- | ---: | ---: | ---: |
| Persona | 0.250 | 0.000 | -0.250 |
| Organization | 0.562 | 0.000 | -0.562 |
| Source | 0.604 | 0.000 | -0.604 |
| Contact | 0.146 | 0.000 | -0.146 |

This is not a valid quality improvement signal. It is a vendor-limit blocked run with zero sampled rows.

## Deployment Restoration

Because the merge condition failed, the API was restored to the prior mainline image:

- Restored image: `registry.fly.io/white-rabbit-api:deployment-01KSGJT21PZYH4A3V3WTHS55JY`
- Post-restore `/health`: `200`
- Post-restore `/readiness`: `200`, body status `ready`
- Post-restore direct tokenless `/scout`: `401`

## Decision

Do not merge `fix/rg6r4-required-suite-contact-precision` to `main` yet.

The branch passes local core/API/web checks and the auth boundary did not weaken, but Prompt B cannot prove the required merge condition. Contact precision did not improve in the fresh required-suite packet, and the suite is blocked by the Tavily pay-as-you-go limit.
