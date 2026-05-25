# QA Report - RG6R3 Arizona Source Remediation

**Date:** 2026-05-25
**Prompt:** Prompt B QA
**Branch:** `fix/rg6r3-arizona-source-targeting`
**Base:** `main` at `ae0559d`
**Feature commit:** `69815b3 fix: improve Arizona K-12 official-domain source targeting and citation grounding (RG6R3)`
**Decision:** QA passed; merge to `main`. RG6 remains product-red.

## Scope Reviewed

- Arizona-specific official-domain source targeting in `query_planner.py`.
- Arizona K-12 source-map fixture coverage for all 8 target districts.
- Citation/claim grounding helper in `source_validation.py`.
- Unit coverage for Arizona planner/source-map behavior and citation snippets.

Confirmed the feature branch does not change UI, API routes, auth, export columns, recipes, batch, scoreboards, public SaaS, accounts, orgs, billing, or `proxy-lead`.

## Verification

```bash
cd packages/core && PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 uv run pytest tests -q
# 174 passed, 6 skipped

cd packages/core && PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 uv run pytest tests/test_arizona_k12_benchmark.py -q --tb=line
# 5 passed, 1 skipped

git diff --check main..HEAD
# passed
```

Live API deployment for evidence:

- Fly image: `white-rabbit-api:deployment-01KSGJT21PZYH4A3V3WTHS55JY`.
- Startup/readiness/sandbox reset: HTTP 200.
- Required direct Fly API suite: 5 product cases returned HTTP 200; privacy refusal returned HTTP 422 as expected.

Artifacts:

- Direct API evidence: `audits/raw/reset-2026-05-10/rg6/rg6r3-arizona-source-remediation-2026-05-25-direct/`
- Failed web-proxy attempt retained separately: `audits/raw/reset-2026-05-10/rg6/rg6r3-arizona-source-remediation-2026-05-25/`

## Evidence Result

Arizona improved on the sampled precision slice:

| Metric | Before | After | Delta |
| --- | ---: | ---: | ---: |
| Arizona persona | 0.250 | 0.500 | +0.250 |
| Arizona organization | 0.625 | 0.750 | +0.125 |
| Arizona source | 0.625 | 0.750 | +0.125 |
| Arizona contact | 0.250 | 0.375 | +0.125 |

Overall required-suite persona, organization, and source precision also improved:

| Metric | Before | After | Delta |
| --- | ---: | ---: | ---: |
| Persona | 0.158 | 0.250 | +0.092 |
| Organization | 0.421 | 0.562 | +0.141 |
| Source | 0.447 | 0.604 | +0.157 |
| Contact | 0.184 | 0.146 | -0.038 |

Arizona coverage now has 6 of 8 rows represented by either source-backed person rows or explicit organization/blocker rows. Two districts remain failed due inaccessible/blocked sources.

## Residual Risk

RG6 is still red. Arizona remains at 2 high-trust usable rows, required-suite contact precision regressed in the sampled packet, and the web proxy attempt returned 401 for `/api/scout` and `/api/source-assisted-proof` even though the direct protected Fly API succeeded. The next narrow A/B slice should stay on source/contact precision and should not unlock yellow/green or Thomas/Lee dogfood claims.
