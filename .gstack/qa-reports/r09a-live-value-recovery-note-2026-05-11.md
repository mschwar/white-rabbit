# R09A Prompt A Note - Live Value Recovery And Benchmark Funnel Diagnosis

**Branch:** `feat/reset-r09a-live-value-recovery`
**Date:** 2026-05-11
**Scope:** Prompt A implementation note only; Prompt B still owns QA/merge.

## Choke Point Found

The RG3 live run used `/scout`, which still exercised the old low-volume path: 15 planned Scout rows, default 50 raw search results, and no broad source-gap representation after extraction. Even when search collected enough sources, rows disappeared between `deduped_sources` and `categorized_rows` because broad source hits that extraction did not convert into person/non-person rows were silently dropped.

## Fix

- Broad Scout queries now use 50 planned rows, 240 raw search results, and aggressive breadth.
- Broad Full queries now use aggressive breadth and the same 240-result source ceiling.
- `RunMetrics` now carries `funnel_counts` and `funnel_notes` for raw vendor hits, deduped sources, source snapshots, extracted candidates, categorized rows, person rows, high-trust rows, and contact-quality passes.
- Broad source hits not represented by extraction are backfilled as explicit failed gap rows. These rows preserve source-to-candidate loss without relaxing READY/high-trust precision or inventing contacts.
- Failed, org-only, and not-found reason language now starts from operator state and makes clear that non-person rows do not imply hidden usable leads.
- Live/replay benchmark summaries now distinguish the old 10-row escape floor from the active 50+ broad-query target, and expected privacy refusals are reported as expected refusals instead of no-candidate quality failures.

## Replay Evidence

Deterministic replay artifacts were saved under `audits/raw/reset-2026-05-10/r09a/replay/`.

The replay quality summary shows:

- `lee-commodity-buyers`: `raw_vendor_hits=96`, `deduped_sources=72`, `source_snapshots=72`, `extracted_candidates=8`, `categorized_rows=50`, `high_trust_usable_rows=0`, `contact_quality_passes=0`, `volume_floor_status=target_met`.
- `privacy-reject-homeowner-phones`: `quality_status=expected_privacy_refusal`, `quality_report=null`, `volume_floor_status=expected_privacy_refusal`.

This proves the new funnel fields and privacy-refusal semantics without live API spend. It does not claim the product is useful yet; contact quality remains zero in the replay and must stay a Prompt B/RG3 audit focus.

## Verification Run By Prompt A

```bash
cd packages/core && uv run pytest tests/test_query_planner.py tests/test_search.py tests/test_coverage.py tests/test_source_validation.py tests/test_contact_status.py tests/test_scoring.py tests/test_orchestrator.py tests/test_live_benchmark_runner.py tests/test_quality_report.py -q
cd apps/api && WR_API_INTERNAL_TOKEN=test-internal-token uv run pytest tests -q
cd packages/core && uv run pytest -m integration -q
```

Prompt B should rerun the feature-card commands, inspect the replay artifacts, and run live benchmarks if credentials/services are available under the reset spend cap.
