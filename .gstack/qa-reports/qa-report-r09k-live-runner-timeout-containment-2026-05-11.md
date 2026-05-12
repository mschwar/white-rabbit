# QA Report - R09K Live Runner Timeout Containment

**Date:** 2026-05-11
**Prompt:** Prompt B
**Branch QA'd:** `feat/reset-r09k-live-runner-timeout-containment`
**Target branch:** `rebuild/validated-leads-loop` only
**Decision:** pass

## State Proof

- Read `AGENTS.md`, `STATUS.md`, `docs/00-product-northstar.md`, `docs/12-reset-gated-implementation-plan-2026-05-10.md`, and `docs/13-pipeline-orchestrator-contract-2026.md` before selecting the QA target.
- `STATUS.md`, `docs/12-reset-gated-implementation-plan-2026-05-10.md`, and the pushed branch state identified exactly one Prompt B target: `R09K - Live runner timeout containment` on `feat/reset-r09k-live-runner-timeout-containment`.
- `git status --short --branch` reported `## feat/reset-r09k-live-runner-timeout-containment...origin/feat/reset-r09k-live-runner-timeout-containment`.
- `git branch -vv` showed the feature branch at `bfcd40e` and `origin/rebuild/validated-leads-loop` at `cf8b1ee`.
- `git diff --name-only rebuild/validated-leads-loop...HEAD` showed only R09K scope:
  - `STATUS.md`
  - `docs/12-reset-gated-implementation-plan-2026-05-10.md`
  - `packages/core/src/core/live_benchmark_runner.py`
  - `packages/core/tests/test_live_benchmark_runner.py`
  - `audits/raw/reset-2026-05-10/r09k/*`

## Verification

- `git diff --check` passed.
- `cd packages/core && uv run pytest tests/test_live_benchmark_runner.py -q` passed: `8 passed`.
- `cd apps/api && WR_API_INTERNAL_TOKEN=test-internal-token uv run pytest tests -q` passed: `49 passed`, with existing `datetime.utcnow()` deprecation warnings.

## Artifact Tie-Out

Inspected the timeout-containment artifacts under `audits/raw/reset-2026-05-10/r09k/`:

- `api-startup-failed/healthcare-it-phoenix.json` recorded `error_code=api_startup_failed`, `health_ok=false`, two `ConnectError: connection refused` attempts, `quality_status=partial_artifact`, `http_status=599`, and zero leads.
- `readiness-timeout/healthcare-it-phoenix.json` recorded `error_code=readiness_timeout`, `health_ok=true`, `readiness_status=readiness_timeout`, `quality_status=partial_artifact`, `http_status=599`, and zero leads.
- `sandbox-reset-timeout/healthcare-it-phoenix.json` recorded `error_code=sandbox_reset_timeout`, `health_ok=true`, `readiness_status=ready`, `sandbox_reset_probe.reset_ok=false`, a successful post-timeout health probe, and zero leads.
- `product-request-timeout/healthcare-it-phoenix.json` recorded `error_code=product_request_timeout`, a successful post-timeout health probe, and zero leads.
- `runner-timeout-probe/healthcare-it-phoenix.json` recorded `error_code=product_request_timeout`, `post_timeout_health_probe.error_code=runner_timeout`, `health_ok=false`, `timeout_seconds=0.2`, and zero leads.
- Each timeout directory contains both the per-case artifact row and a `quality-summary.json` file.

## Northstar Drift Check

R09K aligns with `docs/00-product-northstar.md` because it improves runtime failure containment and evidence quality without changing lead-quality semantics, export behavior, or UI behavior. It keeps startup, readiness, sandbox reset, and post-timeout health failure states explicit instead of letting them masquerade as product output.

## Scope Check

R09K is non-UI. No browser QA or screenshots were required. The branch stayed inside live runner timeout handling, artifact generation, and associated tests; it did not implement lead-quality logic, prompts, search behavior, workbook/export semantics, UI, persistence, dogfood, RG4/R10-R12, Prompt C, or `main` promotion work.

## Result

R09K passes Prompt B QA. Merge only to `rebuild/validated-leads-loop`, mark `R09K` as `merged_to_rebuild_branch`, and hand off Prompt A for `R09L` only.
