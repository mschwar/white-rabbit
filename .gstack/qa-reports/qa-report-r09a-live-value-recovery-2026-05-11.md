# QA Report - R09A Live Value Recovery And Benchmark Funnel Diagnosis

**Date:** 2026-05-11
**Prompt:** Prompt B
**Feature branch:** `feat/reset-r09a-live-value-recovery`
**Integration branch:** `rebuild/validated-leads-loop`
**Result:** Pass for feature QA; ready to merge to integration branch

## State Proven

- `STATUS.md` points to `R09A - Live value recovery and benchmark funnel diagnosis` on `feat/reset-r09a-live-value-recovery`.
- `docs/12-reset-gated-implementation-plan-2026-05-10.md` marks R09A `implemented_pending_qa` and identifies it as the only Prompt B handoff.
- `origin/rebuild/validated-leads-loop` is an ancestor of `origin/feat/reset-r09a-live-value-recovery`; the feature branch is not merged back yet.
- `git status --short --branch` before QA: `## feat/reset-r09a-live-value-recovery...origin/feat/reset-r09a-live-value-recovery`.

## Commands Run

```bash
git diff --check origin/rebuild/validated-leads-loop...HEAD
cd packages/core && uv run pytest tests/test_query_planner.py tests/test_search.py tests/test_coverage.py tests/test_source_validation.py tests/test_contact_status.py tests/test_scoring.py tests/test_orchestrator.py tests/test_live_benchmark_runner.py tests/test_quality_report.py -q
cd apps/api && WR_API_INTERNAL_TOKEN=test-internal-token uv run pytest tests -q
cd apps/api && env -u OPENAI_API_KEY -u OPENAI_BASE_URL -u TAVILY_API_KEY uv run uvicorn api.main:app --host 127.0.0.1 --port 8014
set -a; . apps/api/.env; set +a; cd packages/core && uv run python -m core.live_benchmark_runner --api-base-url http://127.0.0.1:8014 --output-dir ../../audits/raw/reset-2026-05-10/r09a/live-prompt-b --mode scout --api-token "$WR_API_INTERNAL_TOKEN"
```

The first full live-runner invocation timed out on the fourth case because the runner has a fixed 120 second HTTP timeout. The first three case artifacts had already saved. I reran the remaining three cases with the same runner function and a 300 second `httpx.AsyncClient` timeout, then rebuilt `audits/raw/reset-2026-05-10/r09a/live-prompt-b/quality-summary.json` from all six saved case artifacts.

## Verification Results

- `git diff --check`: passed.
- Core R09A suite: `70 passed`.
- API suite: `45 passed`, with existing datetime deprecation warnings.
- UI/browser QA: not required. The branch is non-UI; no React pages/components were changed. `apps/web/src/lib/scout.ts` only received response type additions for funnel fields.

## Replay Artifact Inspection

Prompt A replay artifacts under `audits/raw/reset-2026-05-10/r09a/replay/` contain the expected R09A fields:

- `lee-commodity-buyers`: `raw_vendor_hits=96`, `deduped_sources=72`, `source_snapshots=72`, `extracted_candidates=8`, `categorized_rows=50`, `high_trust_usable_rows=0`, `contact_quality_passes=0`, `volume_floor_status=target_met`.
- `privacy-reject-homeowner-phones`: `quality_status=expected_privacy_refusal`, `quality_report=null`, `volume_floor_status=expected_privacy_refusal`.

## Live Artifact Inspection

Live Scout artifacts were saved under `audits/raw/reset-2026-05-10/r09a/live-prompt-b/`.

| Case | HTTP | Categorized rows | Person rows | High-trust | Contact passes | Volume status |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
| `thomas-arizona-k12` | 200 | 12 | 3 | 0 | 0 | `minimum_met` |
| `lee-commodity-buyers` | 200 | 50 | 2 | 0 | 0 | `target_met` |
| `healthcare-it-phoenix` | 200 | 50 | 3 | 0 | 0 | `target_met` |
| `finance-cisos-new-york` | 200 | 50 | 7 | 0 | 0 | `target_met` |
| `manufacturing-ops-detroit` | 200 | 50 | 1 | 0 | 0 | `target_met` |
| `privacy-reject-homeowner-phones` | 422 | 0 | 0 | 0 | 0 | `expected_privacy_refusal` |

The consolidated live quality summary reports `total_cases=6`, `passed_cases=3`, `failed_cases=3`, and `privacy_refusal_cases=1`. The remaining failures are product-value failures: healthcare, finance, and manufacturing still miss persona/contact/source quality expectations. That is RG3 Prompt C evidence, not a reason to reject R09A, because R09A's feature scope is funnel diagnosis, volume recovery, target-floor semantics, and preserving strict READY safety.

## Northstar Drift Check

R09A aligns with `docs/00-product-northstar.md`:

- Broad prompts no longer silently return 3-4 rows where the source universe is larger; live broad cases now return 50 categorized rows.
- Missing contacts stay non-CRM-ready. Live person rows with missing or failed contact evidence remained `review`, with primary reasons such as `REVIEW: contact is missing; row is not CRM-ready.`
- Failed source-gap rows explicitly say no hidden usable lead is implied.
- Privacy-sensitive consumer targeting is refused before search and reported as an expected refusal, not as a no-candidate product failure.

R09A does not make the product yellow or green. Live contact quality remains `0` across all six cases, and high-trust usable rows remain `0`.

## Scope Check

The branch stayed within R09A:

- Touched core/API benchmark, search, coverage, orchestrator, cost metrics, API request breadth, and response typing needed for funnel observability.
- Added replay/live benchmark artifacts and QA docs.
- Did not implement RG4 UI, refreshed mockups, R10-R12, export, persistence, dogfood, recipe/batch/scoreboard work, or a `main` sync.

## Decision

Pass Prompt B QA and merge R09A only into `rebuild/validated-leads-loop`.

Because R09A is the last feature in current RG3, mark RG3 `gate_pending_audit` and hand off to Prompt C. Do not unlock RG4, refreshed mockups, R10-R12, export, dogfood, or `main`.
