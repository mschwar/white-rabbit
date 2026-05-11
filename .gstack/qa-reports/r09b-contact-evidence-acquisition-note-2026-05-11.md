# R09B Contact Evidence Acquisition Note

**Feature:** R09B - Contact and evidence acquisition pass  
**Branch:** `feat/reset-r09b-contact-evidence-acquisition`  
**Date:** 2026-05-11  
**Status:** Prompt A implementation complete, pending Prompt B QA/merge

## What Changed

- Added a bounded targeted contact-evidence pass after first source validation and before tiering.
- The pass searches up to 8 promising review/person or organization-only rows with contact-oriented public-web queries.
- Person rows can gain `verified_found` only from a direct public snippet containing the named person and matching email.
- Person rows can gain `deduced_with_pattern_evidence` only from explicit organization-domain email pattern evidence such as `first.last@domain`.
- Organization-only rows can gain organization/source support from staff/team/contact sources, but they remain `organization_only`.
- Benchmark quality payloads now include `ready_blocker_counts` and per-candidate READY blockers.
- Live benchmark case timeouts now write partial JSON/HTTP artifacts with `error_code=runner_timeout` instead of aborting the whole suite.

## Precision Guardrails

The implementation does not lower the `high_trust_usable` gate. Tiering still requires supported name, title, organization, source, and usable contact status. Missing, unsupported, inaccessible, guessed, failed, organization-only, and conflicting rows remain non-CRM-ready.

## Replay Evidence

Replay artifacts are saved under `audits/raw/reset-2026-05-10/r09b/replay/`.

- `contact-evidence-pass.json` shows one source-backed contact-quality pass promoted to `high_trust_usable`.
- The same replay keeps a missing-contact person row in `review` with `no_contact_source`.
- The same replay keeps an organization-only row in `organization_only`.
- `runner-timeout-partial.json` shows the timeout partial-artifact shape.
- `quality-summary.json` summarizes contact-quality passes and READY blockers.

## Verification

- `cd packages/core && uv run pytest tests/test_query_planner.py tests/test_search.py tests/test_coverage.py tests/test_source_validation.py tests/test_contact_status.py tests/test_scoring.py tests/test_orchestrator.py tests/test_live_benchmark_runner.py tests/test_quality_report.py -q` (`74 passed`)
- `cd apps/api && WR_API_INTERNAL_TOKEN=test-internal-token uv run pytest tests -q` (`45 passed`, existing datetime deprecation warnings)
