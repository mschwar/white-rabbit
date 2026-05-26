# RG6R4 Required-Suite Contact Precision Evidence Summary

**Collected:** 2026-05-25 local / 2026-05-26 UTC
**Branch image used for evidence:** `registry.fly.io/white-rabbit-api:deployment-01KSH6T2FCA91NMVR5KQVQ60XR`
**Restored image after blocked QA:** `registry.fly.io/white-rabbit-api:deployment-01KSGJT21PZYH4A3V3WTHS55JY`

## Files

- `decision-inputs.json`: sanitized Prompt B decision inputs.
- `web-boundary-summary.json`: direct/API and web-boundary status summary.
- `direct-api-health-readiness-and-protection.json`: direct Fly health, readiness, and tokenless `/scout` protection.
- `web-auth-flow.json`: stable web login and authenticated home proof.
- `web-source-assisted-proof-route.json`: authenticated web `/api/source-assisted-proof` proof.
- `quality-summary.json`: required-suite summary from the authenticated web run.
- `sampled-precision-required-suite.json`: deterministic precision packet from saved outputs.
- `sampled-precision-delta.json`: RG6R4 packet compared with the RG6R3 direct baseline.
- `fly-restore-postcheck.json`: post-restore Fly health/readiness/tokenless protection proof.

## Boundary Result

- Direct Fly `/health`: `200`.
- Direct Fly `/readiness`: `200`, body status `ready`.
- Direct tokenless Fly `/scout`: `401`.
- Authenticated stable web login: `200`.
- Authenticated stable web `/api/source-assisted-proof`: `200`.
- Stable web sandbox reset: `200`.
- Local middleware regression coverage: unauthenticated protected API calls return `401`; a valid shared-password session cookie passes through.

## Required-Suite Result

The product benchmark suite did not produce fresh usable rows because Tavily rejected product searches:

```text
Tavily API error: 433 - This request exceeds the pay-as-you-go limit.
```

Observed product statuses:

- `thomas-arizona-k12`: `503`.
- `lee-commodity-buyers`: `503`.
- `healthcare-it-phoenix`: `503`.
- `finance-cisos-new-york`: `503`.
- `manufacturing-ops-detroit`: `503`.
- `privacy-reject-homeowner-phones`: `422`.

## Sampled Precision

| Metric | RG6R3 baseline | RG6R4 fresh | Delta |
| --- | ---: | ---: | ---: |
| Sampled rows | 48 | 0 | -48 |
| Persona | 0.250 | 0.000 | -0.250 |
| Organization | 0.562 | 0.000 | -0.562 |
| Source | 0.604 | 0.000 | -0.604 |
| Contact | 0.146 | 0.000 | -0.146 |
| Unsupported emails | 0 | 0 | 0 |
| Fake emails | 0 | 0 | 0 |

## Merge Decision

Do not merge RG6R4 from this Prompt B run. The branch passes local verification and web/API auth boundaries did not weaken, but the fresh required-suite evidence does not prove contact precision improved.
