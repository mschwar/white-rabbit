# RG3 R09A Re-Audit Command Output

Date: 2026-05-11
Branch: `audit/reset-rg3-r09a-value-audit`
Integration branch: `rebuild/validated-leads-loop`

## State Proof

```text
$ git status --short --branch
## rebuild/validated-leads-loop...origin/rebuild/validated-leads-loop
```

After branch creation:

```text
Switched to a new branch 'audit/reset-rg3-r09a-value-audit'
```

Feature merge checks:

```text
$ git merge-base --is-ancestor feat/reset-r07-inclusive-extraction rebuild/validated-leads-loop && echo R07_merged
R07_merged

$ git merge-base --is-ancestor feat/reset-r08-tier-validation-conflicts rebuild/validated-leads-loop && echo R08_merged
R08_merged

$ git merge-base --is-ancestor feat/reset-r09-tier-summary-semantics rebuild/validated-leads-loop && echo R09_merged
R09_merged

$ git merge-base --is-ancestor feat/reset-r09a-live-value-recovery rebuild/validated-leads-loop && echo R09A_merged
R09A_merged
```

Gate status search:

```text
docs/12-reset-gated-implementation-plan-2026-05-10.md:8:**Current reset gate:** RG3 - Validation, Conflict, And Gate Semantics, ready for Prompt C audit after R09A Prompt B QA.
docs/12-reset-gated-implementation-plan-2026-05-10.md:189:| RG3 | Validation, Conflict, And Gate Semantics | R07-R09A | gate_pending_audit | `audits/gates/reset-2026-05-10/rg3-validation-semantics.md` |
docs/12-reset-gated-implementation-plan-2026-05-10.md:209:| R10 | Primary search workspace simplification | blocked | `feat/reset-r10-primary-search-ui` | browser |
STATUS.md:27:**Next feature pointer:** No Prompt A or Prompt B feature is ready. R09A passed Prompt B QA and is the last RG3 remediation feature, so the next valid assignment is Prompt C audit for RG3 on `rebuild/validated-leads-loop`. This remains RG3, not RG4. Do not unlock RG4 or sync `main`.
```

## Required Verification

```text
$ cd packages/core && uv run pytest tests/test_source_validation.py tests/test_contact_status.py tests/test_scoring.py tests/test_orchestrator.py -q
.................................................                        [100%]
49 passed in 3.55s
```

```text
$ cd apps/api && WR_API_INTERNAL_TOKEN=test-internal-token uv run pytest tests -q
.............................................                            [100%]
45 passed, 52 warnings in 8.16s
```

```text
$ git diff --check
[no output]
```

## Live Runner

API startup:

```text
INFO:     Started server process [56530]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://127.0.0.1:8016 (Press CTRL+C to quit)
INFO:     127.0.0.1:55082 - "POST /sandbox/reset HTTP/1.1" 200 OK
INFO:     127.0.0.1:55082 - "POST /scout HTTP/1.1" 200 OK
```

Prompt C live runner result:

```text
$ cd packages/core && uv run python -m core.live_benchmark_runner --api-base-url http://127.0.0.1:8016 --output-dir ../../audits/raw/reset-2026-05-10/rg3-r09a/live --mode scout --api-token [redacted]
httpx.ReadTimeout
```

Partial artifact written:

```text
audits/raw/reset-2026-05-10/rg3/r09a-live-rerun/thomas-arizona-k12.json
audits/raw/reset-2026-05-10/rg3/r09a-live-rerun/thomas-arizona-k12.http
```

Partial Thomas summary:

```json
{
  "benchmark_id": "thomas-arizona-k12",
  "runner_elapsed_seconds": 61.556,
  "lead_count": 12,
  "tier_distribution": {
    "failed": 9,
    "high_trust_usable": 0,
    "not_found": 0,
    "organization_only": 3,
    "review": 0
  },
  "funnel_counts": {
    "categorized_rows": 12,
    "contact_quality_passes": 0,
    "deduped_sources": 50,
    "extracted_candidates": 9,
    "high_trust_usable_rows": 0,
    "person_rows": 0,
    "raw_vendor_hits": 56,
    "source_snapshots": 50
  }
}
```

## Complete R09A Prompt B Live Suite Summary

```json
[
  {"id":"finance-cisos-new-york","rows":50,"persons":7,"high_trust":0,"contact_quality":0,"status":"evaluated","failures":["zero_usable_candidates","low_precision_rate","low_persona_match_rate","low_contact_quality_rate","low_source_support_rate","high_noise_rate"]},
  {"id":"healthcare-it-phoenix","rows":50,"persons":3,"high_trust":0,"contact_quality":0,"status":"evaluated","failures":["zero_usable_candidates","low_precision_rate","low_persona_match_rate","low_contact_quality_rate","low_source_support_rate","high_noise_rate"]},
  {"id":"lee-commodity-buyers","rows":50,"persons":2,"high_trust":0,"contact_quality":0,"status":"evaluated","failures":["zero_usable_candidates","low_precision_rate","low_persona_match_rate","low_contact_quality_rate","low_source_support_rate","high_noise_rate"]},
  {"id":"manufacturing-ops-detroit","rows":50,"persons":1,"high_trust":0,"contact_quality":0,"status":"evaluated","failures":["zero_usable_candidates","low_precision_rate","low_persona_match_rate","low_contact_quality_rate","low_source_support_rate","high_noise_rate"]},
  {"id":"privacy-reject-homeowner-phones","rows":0,"persons":0,"high_trust":0,"contact_quality":0,"status":"expected_privacy_refusal","failures":[]},
  {"id":"thomas-arizona-k12","rows":12,"persons":3,"high_trust":0,"contact_quality":0,"status":"evaluated","failures":["zero_usable_candidates","low_precision_rate","low_persona_match_rate","low_contact_quality_rate","low_source_support_rate","high_noise_rate"]}
]
```
