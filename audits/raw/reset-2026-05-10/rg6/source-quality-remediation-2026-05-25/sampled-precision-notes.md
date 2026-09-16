# RG6 source-quality remediation sampled precision notes

Date: 2026-05-25
Branch: fix/rg6-source-quality-required-suite-remediation
Artifact directory: audits/raw/reset-2026-05-10/rg6/source-quality-remediation-2026-05-25/

## Scope

This note is required for broad required-suite precision sampling. The suite artifacts in this directory are startup-failure partial artifacts because the local API did not answer `/health` after Docker startup failed. Therefore there were no broad person rows available to sample in this run.

## Broad case sampling

| Case | Person rows present | Sampled rows | Persona | Org/geography | Source support | Contact status | Fake/unsupported contact count | Notes |
| --- | ---: | ---: | --- | --- | --- | --- | ---: | --- |
| lee-commodity-buyers | 0 | 0 | Not sampled | Not sampled | Not sampled | Not sampled | 0 | HTTP 599 `api_startup_failed`; no returned candidates. |
| healthcare-it-phoenix | 0 | 0 | Not sampled | Not sampled | Not sampled | Not sampled | 0 | HTTP 599 `api_startup_failed`; no returned candidates. |
| finance-cisos-new-york | 0 | 0 | Not sampled | Not sampled | Not sampled | Not sampled | 0 | HTTP 599 `api_startup_failed`; no returned candidates. |
| manufacturing-ops-detroit | 0 | 0 | Not sampled | Not sampled | Not sampled | Not sampled | 0 | HTTP 599 `api_startup_failed`; partial artifact generated instead of disappearing or parse-failing. |

## Precision conclusion

No broad precision pass is claimed from this run. The runner produced valid JSON/HTTP partial artifacts and `quality-summary.json`, but local API startup was blocked before live candidate generation. RG6 remains product-red; this evidence does not unlock yellow/green or Thomas/Lee dogfood.
