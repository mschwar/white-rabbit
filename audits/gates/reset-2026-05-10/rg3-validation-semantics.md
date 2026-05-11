# Reset Gate Review - RG3 Validation, Conflict, And Gate Semantics

**Branch:** `audit/reset-rg3-live-proof`
**Integration branch:** `rebuild/validated-leads-loop`
**Date:** 2026-05-11
**Decision:** hold
**Current product gate:** red

## Evidence Used

- Current reset docs: `AGENTS.md`, `STATUS.md`, `docs/00-product-northstar.md`, `docs/12-reset-gated-implementation-plan-2026-05-10.md`, `docs/13-pipeline-orchestrator-contract-2026.md`, and `docs/03-decisions.md`.
- `DESIGN.md` was read only as future RG4 visual direction. It is not evidence that the RG3 data-quality gate passed.
- Baseline audit: `audits/zero-trust-codebase-audit-2026-05-10.md`.
- Current branch proof: `audits/raw/reset-2026-05-10/rg3/post-r09i-live-proof/commands/state-proof.md`.
- Post-R09I evidence notes: `audits/raw/reset-2026-05-10/rg3/post-r09i-live-proof/evidence-notes.md`.
- Current manual-oracle replay packet: `audits/raw/reset-2026-05-10/rg3/post-r09i-live-proof/replay/manual-oracle-proof-packet.json`.
- Current live-runner attempts and API logs under `audits/raw/reset-2026-05-10/rg3/post-r09i-live-proof/`.
- Prior complete live suite after R09A: `audits/raw/reset-2026-05-10/r09a/live-prompt-b/quality-summary.json`.

## Commands Run

```bash
git fetch origin --prune
git switch -c audit/reset-rg3-live-proof origin/rebuild/validated-leads-loop
git status --short --branch
git merge-base --is-ancestor origin/feat/reset-r07-inclusive-extraction origin/rebuild/validated-leads-loop
git merge-base --is-ancestor origin/feat/reset-r08-tier-validation-conflicts origin/rebuild/validated-leads-loop
git merge-base --is-ancestor origin/feat/reset-r09-tier-summary-semantics origin/rebuild/validated-leads-loop
git merge-base --is-ancestor origin/feat/reset-r09a-live-value-recovery origin/rebuild/validated-leads-loop
git merge-base --is-ancestor origin/feat/reset-r09b-contact-evidence-acquisition origin/rebuild/validated-leads-loop
git merge-base --is-ancestor origin/feat/reset-r09c-deep-multisource-evidence-tier-calibration origin/rebuild/validated-leads-loop
git merge-base --is-ancestor origin/feat/reset-r09d-april-nm-manual-oracle origin/rebuild/validated-leads-loop
git merge-base --is-ancestor origin/feat/reset-r09e-k12-source-map-roster-collector origin/rebuild/validated-leads-loop
git merge-base --is-ancestor origin/feat/reset-r09f-source-assisted-lead-compiler origin/rebuild/validated-leads-loop
git merge-base --is-ancestor origin/feat/reset-r09g-research-workbook-tiering origin/rebuild/validated-leads-loop
git merge-base --is-ancestor origin/feat/reset-r09h-manual-oracle-proof-packet origin/rebuild/validated-leads-loop
git merge-base --is-ancestor origin/feat/reset-r09i-api-startup-live-proof origin/rebuild/validated-leads-loop
git diff --check
cd packages/core && uv run pytest tests/test_query_planner.py tests/test_search.py tests/test_coverage.py tests/test_source_validation.py tests/test_contact_status.py tests/test_scoring.py tests/test_orchestrator.py tests/test_live_benchmark_runner.py tests/test_quality_report.py -q
cd packages/core && uv run pytest tests/test_manual_oracle_proof_packet.py tests/test_research_workbook.py tests/test_source_assisted_compiler.py tests/test_manual_oracle.py tests/test_k12_source_map.py -q
cd packages/core && uv run pytest tests/test_live_benchmark_runner.py -q
cd apps/api && WR_API_INTERNAL_TOKEN=test-internal-token uv run pytest tests -q
cd packages/core && uv run python -m core.live_benchmark_runner --help
cd packages/core && uv run python -c "...write_r09h_proof_packet_artifacts(...)..."
cd apps/api && env -u OPENAI_BASE_URL -u OPENAI_API_KEY -u TAVILY_API_KEY -u WR_API_INTERNAL_TOKEN uv run uvicorn api.main:app --host 127.0.0.1 --port 8017
curl --max-time 5 http://127.0.0.1:8017/health
curl --max-time 8 http://127.0.0.1:8017/readiness
cd packages/core && source ../../apps/api/.env && unset OPENAI_BASE_URL && uv run python -m core.live_benchmark_runner --api-base-url http://127.0.0.1:8017 --output-dir ../../audits/raw/reset-2026-05-10/rg3/post-r09i-live-proof/live --mode scout --startup-timeout-seconds 20
cd apps/api && env -u OPENAI_BASE_URL -u OPENAI_API_KEY -u TAVILY_API_KEY -u WR_API_INTERNAL_TOKEN uv run uvicorn api.main:app --host 127.0.0.1 --port 8018
cd packages/core && source ../../apps/api/.env && unset OPENAI_BASE_URL && uv run python -m core.live_benchmark_runner --api-base-url http://127.0.0.1:8018 --output-dir ../../audits/raw/reset-2026-05-10/rg3/post-r09i-live-proof/live-clean --mode scout --startup-timeout-seconds 30
cd apps/api && env -u OPENAI_BASE_URL -u OPENAI_API_KEY -u TAVILY_API_KEY -u WR_API_INTERNAL_TOKEN uv run uvicorn api.main:app --host 127.0.0.1 --port 8019
cd packages/core && source ../../apps/api/.env && unset OPENAI_BASE_URL && uv run python -m core.live_benchmark_runner --api-base-url http://127.0.0.1:8019 --output-dir ../../audits/raw/reset-2026-05-10/rg3/post-r09i-live-proof/live-skip-startup --mode scout --skip-startup-check --no-reset-sandbox
curl --max-time 5 http://127.0.0.1:8019/health
```

Command outputs are saved under `audits/raw/reset-2026-05-10/rg3/post-r09i-live-proof/commands/`.

## Live Results

No fresh complete RG3 live benchmark suite completed in this audit.

R09I did improve one blocker: on a clean API process, `/health` can answer as process liveness without waiting for dependency readiness. The clean startup probe on port 8018 recorded one successful health attempt in `0.007s`.

The full live proof path is still not reliable enough to advance RG3:

| Attempt | Result | Evidence |
| --- | --- | --- |
| Direct API check on 8017 | `/health` returned 200 after startup, but `/readiness` timed out after 8 seconds | `commands/api-health-readiness-8017-after-startup.txt` |
| Live runner on 8017 after the timed-out readiness call | Startup probe failed all health attempts and wrote `api_startup_failed` / HTTP 599 artifacts for all six cases | `live/quality-summary.json` |
| Clean live runner on 8018 | `/health` passed, `/readiness` was recorded as `unavailable`, then sandbox reset timed out with an unhandled `httpx.ReadTimeout` | `live-clean/startup/startup-diagnostics.json`, `commands/live-benchmark-runner-8018-clean.txt` |
| Direct product-path run on 8019 with startup and sandbox reset skipped | First benchmark, `thomas-arizona-k12`, timed out after 120 seconds with `error_code=runner_timeout`; no returned rows | `live-skip-startup/thomas-arizona-k12.json` |
| Health after the 8019 product-path timeout | `/health` timed out with HTTP `000` | `commands/api-health-8019-after-runner-timeout.txt` |

Current post-R09I live summary from the 8017 runner:

| Benchmark | HTTP | Error | Categorized rows | Person rows | READY / high trust | Contact-quality passes |
| --- | ---: | --- | ---: | ---: | ---: | ---: |
| Thomas Arizona K-12 | 599 | `api_startup_failed` | 0 | 0 | 0 | 0 |
| Lee commodity buyers | 599 | `api_startup_failed` | 0 | 0 | 0 | 0 |
| Healthcare IT Phoenix | 599 | `api_startup_failed` | 0 | 0 | 0 | 0 |
| Finance CISOs New York | 599 | `api_startup_failed` | 0 | 0 | 0 | 0 |
| Manufacturing ops Detroit | 599 | `api_startup_failed` | 0 | 0 | 0 | 0 |
| B2C private phone guardrail | 599 | `api_startup_failed` | 0 | 0 | 0 | n/a |

The prior complete R09A live suite still remains the latest complete case-level suite with actual non-privacy product responses. It had improved broad volume in several broad cases, but it still had `0` high-trust usable rows and `0` contact-quality passes across evaluated cases.

## Screenshots And Artifacts

No screenshots were required because RG3 is a data-quality/runtime gate, not a UI implementation gate.

Raw artifacts:

- `audits/raw/reset-2026-05-10/rg3/post-r09i-live-proof/evidence-notes.md`
- `audits/raw/reset-2026-05-10/rg3/post-r09i-live-proof/commands/`
- `audits/raw/reset-2026-05-10/rg3/post-r09i-live-proof/live/quality-summary.json`
- `audits/raw/reset-2026-05-10/rg3/post-r09i-live-proof/live-clean/startup/`
- `audits/raw/reset-2026-05-10/rg3/post-r09i-live-proof/live-skip-startup/thomas-arizona-k12.json`
- `audits/raw/reset-2026-05-10/rg3/post-r09i-live-proof/replay/manual-oracle-proof-packet.json`

## Value Prop Verdict

The current product does **not** give enough result volume, evidence, or export value for the operator loop.

Result volume is not proven in the current live product path: the complete post-R09I runner produced only startup-failure artifacts, and the isolated `/scout` attempt timed out on the first Thomas benchmark without returning rows.

Evidence quality is split. The source-assisted replay is strong offline evidence for the April New Mexico workbook pattern: 17 rows, 10 `READY_WITH_CONTACT`, 7 `MANUAL_LOOKUP`, 18 sources, sales-first export fields, and zero unsupported CRM-ready rows. But current live benchmark evidence still does not prove source-backed contacts, field support, or READY blockers through the operator path.

Export value is proven only in replay/workbook semantics, not in a current query-to-export operator flow. A salesperson still cannot rely on the current live product to produce a usable result set and export without rerunning or debugging the system.

## Findings

1. **Hold blocker - live runner still cannot produce a complete current RG3 suite.** Post-R09I attempts either produced `api_startup_failed` artifacts, timed out on sandbox reset, or timed out on the first `/scout` benchmark.
2. **Hold blocker - readiness can still stall runtime.** `/readiness` timed out and appears to block later health/product requests on the same single-worker process. That means the readiness diagnostics are not yet safe enough as a gate-audit dependency.
3. **Hold blocker - product endpoint runtime is not bounded.** With startup checks and sandbox reset skipped, the Thomas Arizona K-12 `/scout` case timed out after 120 seconds and left `/health` timing out afterward.
4. **Pass - R09I improved process-liveness visibility.** On a clean process, `/health` answered `200` and the runner captured a successful health startup probe before readiness failed.
5. **Pass - regression tests and replay checks pass.** Core RG3 semantic suite passed (`78 passed`), API suite passed (`48 passed`), live-runner unit tests passed (`5 passed`), and the manual-oracle replay suite passed (`18 passed`).
6. **Pass - source-assisted manual-oracle replay still works offline.** The replay packet reproduces the April New Mexico structure with verified-contact rows, manual-lookup rows, source URLs, blocker/next-action semantics, sales-first export fields, and no unsupported CRM-ready rows.
7. **No downstream unlock.** RG4, refreshed `DESIGN.md` mockup/design preflight, R10-R12, export work, dogfood, and `main` promotion remain blocked because this decision is `hold`.

## What Worked

- Current git ancestry proves R07-R09I are merged into `origin/rebuild/validated-leads-loop`.
- `git diff --check` passed before audit edits.
- API unit tests now cover the R09I health/readiness behavior and pass.
- The live benchmark runner writes structured startup-failure artifacts when its startup probe cannot reach `/health`.
- Manual-oracle replay and workbook export semantics remain intact.

## What Did Not Work

- `/readiness` did not return a bounded actionable payload in live audit conditions; it timed out.
- The live benchmark runner does not handle sandbox reset `ReadTimeout` as a suite-level partial artifact; it exits with a traceback.
- The direct `/scout` live path can still time out on the first benchmark and leave the API unresponsive to `/health`.
- No current live benchmark produced nonzero high-trust usable rows, nonzero contact-quality passes, or exportable operator value.

## New Gaps Found

- R09I separated health from readiness at the contract level, but readiness checks still perform blocking work that can stall the API process.
- The live runner's startup-failure path is structured, but its post-startup setup path is not fully protected against timeouts.
- The source-assisted replay path needs a live operator-runnable API or CLI flow before it can count as current product evidence for RG3.
- The gate table/status text had stale R09I handoff language after the branch was merged; this audit branch updates the docs to match the live git state.

## Recommended Scope Change For Next Gate

Keep RG3 held. Do not start RG4 mockups, R10-R12 UI work, export polish, dogfood, or a `main` sync.

If Matt accepts this hold and wants another remediation, keep it inside RG3 and make it a narrow runtime/live-proof slice. The scope should be: bound `/readiness` so it cannot block `/health`, wrap sandbox reset and first-case runner timeouts into complete suite artifacts, and prove either a live source-assisted operator path or a current Scout benchmark path returns rows without relaxing READY/high-trust contact rules.

## Next Main Promotion Recommendation

Do not sync `main`. The decision is `hold`; the operator-use branch should not receive another promotion unless Matt explicitly asks after seeing this gate decision.

## Next Prompt A Assignment

None. Because the decision is `hold`, no downstream Prompt A feature and no RG4 design/mockup preflight is unlocked.

R10-R12 remain blocked. The refreshed mockup/design preflight from `DESIGN.md` also remains blocked until a future RG3 Prompt C records `advance`; if RG3 later advances, that preflight is the next assignment, not R10.
