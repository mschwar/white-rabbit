# RG3 Post-R09I Evidence Notes

**Date:** 2026-05-11
**Branch:** `audit/reset-rg3-live-proof`
**Integration branch:** `rebuild/validated-leads-loop`
**Decision supported:** `hold`

## Current State Proof

- `state-proof.md` records `audit/reset-rg3-live-proof` created from `origin/rebuild/validated-leads-loop` at `339bea0`.
- The reset gate table still marks RG3 as `gate_hold`; RG4 remains `blocked`.
- All RG3 feature branches R07-R09I are ancestors of `origin/rebuild/validated-leads-loop`.
- `git diff --check` passed before report edits.

## Test And Replay Evidence

- `core-rg3-semantic-suite.txt`: 78 core semantic/live-runner/quality tests passed.
- `core-manual-oracle-suite.txt`: 18 source-assisted/manual-oracle replay tests passed.
- `core-test-live-benchmark-runner.txt`: 5 live-runner tests passed.
- `api-tests.txt`: 48 API tests passed with existing datetime deprecation warnings.
- `manual-oracle-proof-packet.json`: source-assisted replay still passes with 17 workbook rows, 10 `READY_WITH_CONTACT`, 7 `MANUAL_LOOKUP`, 18 sources, sales-first export fields, and zero unsupported CRM-ready rows.

## Live Runtime Evidence

- On port 8017, direct `/health` initially returned 200 after startup, but `/readiness` timed out after 8 seconds. A following live-runner startup probe then failed all health attempts and wrote `api_startup_failed` artifacts for every case.
- On clean port 8018, the live-runner startup probe reached `/health` in 0.007 seconds and captured `health_ok=true`; `/readiness` still timed out and was recorded as `readiness_status=unavailable`. The runner then timed out on sandbox reset and exited with an unhandled `httpx.ReadTimeout`, so no full live case suite completed.
- On port 8019, running the live runner with `--skip-startup-check --no-reset-sandbox` isolated the product endpoint path. The first benchmark, `thomas-arizona-k12`, timed out after 120 seconds with `error_code=runner_timeout`, wrote a partial artifact, and the API stopped answering `/health` afterward.

## Gate Interpretation

- R09I improved the ability to distinguish process health from startup failure: `/health` can now answer independently when the server is fresh.
- R09I did not make the full live proof path reliable enough for RG3 advancement: readiness can stall, sandbox reset timeout is not converted into a complete suite artifact, and the first direct `/scout` benchmark can still hang for 120 seconds with no returned rows.
- Current live evidence therefore does not prove result volume, evidence quality, contact-quality passes, or export value for the operator loop.
- The source-assisted replay remains valuable evidence for the April New Mexico workbook pattern, but it is still replay/workbook proof, not a current live query-to-export operator path.
