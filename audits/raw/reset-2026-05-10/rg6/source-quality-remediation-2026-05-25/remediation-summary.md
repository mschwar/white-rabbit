# RG6 source-quality remediation summary

Date: 2026-05-25
Branch: `fix/rg6-source-quality-required-suite-remediation`
Worktree: `/Users/mschwar/Documents/white-rabbit-rg6-source-quality`
Artifact directory: `audits/raw/reset-2026-05-10/rg6/source-quality-remediation-2026-05-25/`

## Summary

Matt-directed RG6 source-quality red remediation was completed as a scoped implementation/test/doc pass. This is not a yellow/green claim and does not unlock Thomas/Lee dogfood.

The code remediation keeps official/source ordering behavior and manufacturing partial-artifact handling from the copied partial work, then adds a guard against adjacent Arizona K-12 named-account alias drift: single-word named-account aliases such as `Gilbert` or `Chandler` only satisfy named-account coverage when K-12/district context is also present. This prevents adjacent organizations such as `Chandler-Gilbert Community College` from counting toward the named K-12 district coverage requirement.

## What changed

- `packages/core/src/core/coverage.py`
  - Added context-aware matching for single-word named-account aliases.
  - Preserved multi-word account-name matching.
  - Applied the same coverage rule to candidate rows and source coverage.
- `packages/core/tests/test_coverage.py`
  - Added a regression proving `Chandler-Gilbert Community College` does not satisfy `Gilbert Public Schools` or `Chandler Unified School District` named-account coverage.
- Required-suite artifact directory
  - Generated valid `.json` and `.http` files for all six required cases.
  - Generated `quality-summary.json` including `manufacturing-ops-detroit`.
  - Added this `remediation-summary.md` and `sampled-precision-notes.md`.

## Commands run and results

Focused core tests:

```bash
cd packages/core
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 uv run --no-sync pytest tests/test_coverage.py tests/test_search.py tests/test_live_benchmark_runner.py -q
```

Result: `24 passed in 0.23s`.

Required core subset requested by Matt, corrected for the repo's actual test files because `tests/test_source_collection.py` does not exist:

```bash
cd packages/core
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 uv run --no-sync pytest tests/test_arizona_k12_benchmark.py tests/test_benchmark_suite.py tests/test_query_planner.py tests/test_search.py tests/test_source_validation.py tests/test_orchestrator.py tests/test_live_benchmark_runner.py tests/test_quality_report.py -q
```

Result: `69 passed, 1 skipped in 0.71s`.

API tests:

```bash
cd apps/api
WR_API_INTERNAL_TOKEN=[REDACTED] PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 uv run --no-sync pytest tests -q
```

Result: `57 passed, 82 warnings in 1.01s`. Warnings are existing `datetime.utcnow()` deprecation warnings.

Diff hygiene:

```bash
git diff --check -- packages/core/src/core/search.py packages/core/src/core/coverage.py packages/core/src/core/live_benchmark_runner.py packages/core/tests/test_coverage.py packages/core/tests/test_search.py packages/core/tests/test_live_benchmark_runner.py
```

Result: passed. Whole-repo `git diff --check` timed out in this worktree, so path-scoped checks were used.

Local service startup attempt:

```bash
docker compose up -d
```

Result: blocked by unavailable Docker daemon/socket:

```text
unable to get image 'postgres:16-alpine': failed to connect to the docker API at unix:///Users/mschwar/.docker/run/docker.sock; check if the path is correct and if the daemon is running: dial unix /Users/mschwar/.docker/run/docker.sock: connect: no such file or directory
```

Live/local required-suite attempt against localhost:

```bash
cd packages/core
WR_API_INTERNAL_TOKEN=[REDACTED] uv run python -m core.live_benchmark_runner --api-base-url http://127.0.0.1:8000 --output-dir ../../audits/raw/reset-2026-05-10/rg6/source-quality-remediation-2026-05-25 --mode scout --api-token [REDACTED] --startup-timeout-seconds 5
```

Result: completed with startup-failure partial artifacts. `/health` did not answer on localhost, all six benchmark cases wrote valid `.json` and `.http` artifacts with HTTP `599`, and `quality-summary.json` was generated.

## Required-suite metrics

From `quality-summary.json`:

- Suite: `required_lead_quality_suite`
- Total cases: 6
- Passed cases: 1
- Failed cases: 5
- Suite failure: `api_startup_failed`
- Startup message: `API did not answer /health before live benchmark case execution.`
- Guardrail mismatches: none
- Observation mismatches:
  - `thomas-arizona-k12: coverage, volume`
  - `lee-commodity-buyers: volume`
  - `healthcare-it-phoenix: persona, contact, source, volume`
  - `finance-cisos-new-york: persona, contact, source, volume`
  - `manufacturing-ops-detroit: persona, contact, source, volume`

## Arizona 6-of-8 outcome

Arizona did not reach 6-of-8 in this local/live suite attempt. The local API never started, so the suite produced `api_startup_failed` partial artifacts with zero categorized rows and all eight Arizona target accounts missing:

- Mesa Public Schools
- Chandler Unified School District
- Peoria Unified School District
- Gilbert Public Schools
- Deer Valley Unified School District
- Paradise Valley Unified School District
- Dysart Unified School District
- Maricopa Unified School District

The code-level regression specifically prevents adjacent district/persona drift from being counted, but no fresh live candidate evidence exists in this artifact set.

## Manufacturing artifact outcome

Manufacturing artifact generation is fixed at the runner/artifact level for this blocked run: `manufacturing-ops-detroit.json`, `manufacturing-ops-detroit.http`, and a `manufacturing-ops-detroit` entry in `quality-summary.json` were produced. The case is `quality_status=partial_artifact`, `http_status=599`, `error_code=api_startup_failed`. It did not disappear, crash the suite, or become an unhandled 503 parse failure.

## Remaining red/yellow/green gaps

- RG6 remains product-red.
- No yellow claim.
- No green claim.
- No Thomas/Lee dogfood unlock.
- Arizona 6-of-8 quality is not proven by this run.
- Broad required-suite precision/contact/source/persona quality is not proven by this run because there were no live candidate rows to sample.
- Local API live suite is blocked until Docker/Postgres/API startup is available or a valid remote API target with credentials is supplied.
- Whole-repo git commands are still slow/hanging in this worktree; path-scoped checks were used.

## Exact Prompt B handoff

QA `fix/rg6-source-quality-required-suite-remediation`; verify only Matt-directed RG6 source-quality red remediation landed; rerun focused core tests, the corrected required core subset, API tests, and `git diff --check`; inspect `audits/raw/reset-2026-05-10/rg6/source-quality-remediation-2026-05-25/` for valid six-case `.json`/`.http` artifacts plus `quality-summary.json`, `sampled-precision-notes.md`, and `remediation-summary.md`; confirm official/source ordering and adjacent Arizona K-12 alias-drift regression behavior; confirm `manufacturing-ops-detroit` remains present in `quality-summary.json` even when the API is unavailable; confirm RG6 remains product-red with no yellow/green, no Thomas/Lee dogfood unlock, and no public SaaS/account/org/billing scope. Do not merge unless Matt explicitly authorizes it after QA.
