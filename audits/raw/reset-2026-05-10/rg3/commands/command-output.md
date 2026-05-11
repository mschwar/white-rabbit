# RG3 R09A Re-Audit Command Output

Date: 2026-05-11
Branch: `audit/reset-rg3-validation-semantics-r09a`
Integration branch: `rebuild/validated-leads-loop`

## Initial State

```text
$ git status --short --branch
## rebuild/validated-leads-loop...origin/rebuild/validated-leads-loop
```

```text
$ git log --oneline --decorate -8 --first-parent
09409ab (HEAD -> audit/reset-rg3-validation-semantics-r09a, origin/rebuild/validated-leads-loop, origin/feat/reset-r09a-live-value-recovery, rebuild/validated-leads-loop, feat/reset-r09a-live-value-recovery) qa: verify r09a live value recovery
961c70b feat: add r09a benchmark funnel recovery
e5c10ac (origin/codex/rg3-remediation-slice, codex/rg3-remediation-slice) docs(reset): add rg3 live value remediation slice
bab7f12 (origin/audit/reset-rg3-validation-semantics, audit/reset-rg3-validation-semantics) docs: record rg3 validation gate hold
fb12943 (origin/codex/fold-design-direction, codex/fold-design-direction) docs(design): fold direction into reset plan
7f8a142 docs: clarify rg3 audit handoff
03d375b docs: fix r09 qa report whitespace
b8ea483 merge: r09 tier summary semantics
```

## Gate And Feature Merge Proof

```text
$ rg -n "RG3|R07|R08|R09|R09A|gate_pending_audit|gate_advanced" docs/12-reset-gated-implementation-plan-2026-05-10.md STATUS.md audits/gates/reset-2026-05-10/rg3-validation-semantics.md
docs/12-reset-gated-implementation-plan-2026-05-10.md:8:**Current reset gate:** RG3 - Validation, Conflict, And Gate Semantics, ready for Prompt C audit after R09A Prompt B QA.
docs/12-reset-gated-implementation-plan-2026-05-10.md:189:| RG3 | Validation, Conflict, And Gate Semantics | R07-R09A | gate_pending_audit | `audits/gates/reset-2026-05-10/rg3-validation-semantics.md` |
docs/12-reset-gated-implementation-plan-2026-05-10.md:205:| R07 | Inclusive extraction prompt and candidate parse salvage | merged_to_rebuild_branch | `feat/reset-r07-inclusive-extraction` | core/API tests |
docs/12-reset-gated-implementation-plan-2026-05-10.md:206:| R08 | Tiering engine, field validator, and conflict resolver | merged_to_rebuild_branch | `feat/reset-r08-tier-validation-conflicts` | core tests |
docs/12-reset-gated-implementation-plan-2026-05-10.md:207:| R09 | Tier summary, score semantics, and reason language reset | merged_to_rebuild_branch | `feat/reset-r09-tier-summary-semantics` | core + web tests |
docs/12-reset-gated-implementation-plan-2026-05-10.md:208:| R09A | Live value recovery and benchmark funnel diagnosis | merged_to_rebuild_branch | `feat/reset-r09a-live-value-recovery` | core/API + live/replay benchmark artifacts |
STATUS.md:11:**Next pointer:** Prompt C audit for RG3 - Validation, Conflict, And Gate Semantics on `rebuild/validated-leads-loop` after the R09A merge.
STATUS.md:85:Prompt C handoff: Audit RG3 - Validation, Conflict, And Gate Semantics on `rebuild/validated-leads-loop` after R09A merges.
```

```text
$ git merge-base --is-ancestor feat/reset-r07-inclusive-extraction rebuild/validated-leads-loop
$ git merge-base --is-ancestor feat/reset-r08-tier-validation-conflicts rebuild/validated-leads-loop
$ git merge-base --is-ancestor feat/reset-r09-tier-summary-semantics rebuild/validated-leads-loop
$ git merge-base --is-ancestor feat/reset-r09a-live-value-recovery rebuild/validated-leads-loop
# all four commands exited 0
```

## Core Verification

```text
$ cd packages/core && uv run pytest tests/test_query_planner.py tests/test_search.py tests/test_coverage.py tests/test_source_validation.py tests/test_contact_status.py tests/test_scoring.py tests/test_orchestrator.py tests/test_live_benchmark_runner.py tests/test_quality_report.py -q
......................................................................   [100%]
70 passed in 0.48s
```

## API Verification

```text
$ cd apps/api && WR_API_INTERNAL_TOKEN=test-internal-token uv run pytest tests -q
.............................................                            [100%]
45 passed, 52 warnings in 0.83s
```

Warnings were existing `datetime.utcnow()` deprecation warnings in API code/tests.

## Web Regression And Build

```text
$ cd apps/web && npm test -- --run
Test Files  13 passed (13)
Tests  30 passed (30)
```

```text
$ cd apps/web && npm run build
✓ Compiled successfully in 5.6s
Finished TypeScript in 1938ms
✓ Generating static pages using 7 workers (11/11) in 117ms
```

Build warnings were existing Next.js workspace-root inference and `middleware` convention deprecation warnings.

## Local API Startup

```text
$ cd apps/api && env -u OPENAI_API_KEY -u OPENAI_BASE_URL -u OPENAI_MODEL uv run uvicorn api.main:app --host 127.0.0.1 --port 8015
INFO:     Started server process [75108]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://127.0.0.1:8015 (Press CTRL+C to quit)
INFO:     127.0.0.1:65277 - "POST /sandbox/reset HTTP/1.1" 200 OK
INFO:     127.0.0.1:65277 - "POST /scout HTTP/1.1" 200 OK
INFO:     127.0.0.1:65277 - "POST /scout HTTP/1.1" 200 OK
INFO:     127.0.0.1:65277 - "POST /scout HTTP/1.1" 200 OK
INFO:     127.0.0.1:65277 - "POST /scout HTTP/1.1" 200 OK
INFO:     127.0.0.1:65277 - "POST /scout HTTP/1.1" 200 OK
INFO:     127.0.0.1:65277 - "POST /scout HTTP/1.1" 422 Unprocessable Entity
```

## Fresh Live Benchmark

```text
$ cd packages/core && env -u OPENAI_API_KEY -u OPENAI_BASE_URL -u OPENAI_MODEL uv run python -m core.live_benchmark_runner --api-base-url http://127.0.0.1:8015 --output-dir ../../audits/raw/reset-2026-05-10/rg3/live-r09a --mode scout --api-token [redacted]
```

Per-case runner output:

```text
thomas-arizona-k12: HTTP 200, elapsed 62.046s
lee-commodity-buyers: HTTP 200, elapsed 69.85s
healthcare-it-phoenix: HTTP 200, elapsed 94.96s
finance-cisos-new-york: HTTP 200, elapsed 91.318s
manufacturing-ops-detroit: HTTP 200, elapsed 73.398s
privacy-reject-homeowner-phones: HTTP 422, elapsed 0.002s
```

Quality summary:

```text
total_cases=6
passed_cases=3
failed_cases=3
persona_pass_cases=0
contact_pass_cases=0
source_pass_cases=0
privacy_refusal_cases=1
observation_mismatches=[
  "healthcare-it-phoenix: persona, contact, source",
  "finance-cisos-new-york: persona, contact, source",
  "manufacturing-ops-detroit: persona, contact, source"
]
```

Case summaries:

```text
thomas-arizona-k12: rows=10, person=2, high_trust=0, review=2, org_only=1, not_found=3, failed=4, contact_passes=0, volume=minimum_met
lee-commodity-buyers: rows=50, person=3, high_trust=0, review=3, org_only=1, not_found=1, failed=45, contact_passes=0, volume=target_met
healthcare-it-phoenix: rows=50, person=3, high_trust=0, review=3, org_only=1, not_found=0, failed=46, contact_passes=0, volume=target_met
finance-cisos-new-york: rows=50, person=7, high_trust=0, review=7, org_only=1, not_found=1, failed=41, contact_passes=0, volume=target_met
manufacturing-ops-detroit: rows=50, person=1, high_trust=0, review=1, org_only=1, not_found=1, failed=47, contact_passes=0, volume=target_met
privacy-reject-homeowner-phones: rows=0, privacy_refusal=true, quality_status=expected_privacy_refusal
```
