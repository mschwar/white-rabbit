# QA Report - Reset Feature

**Feature ID:** R03
**Feature name:** Live benchmark runner and quality summary
**Branch:** feat/reset-r03-live-benchmark-runner
**PR target:** rebuild/validated-leads-loop
**Date:** 2026-05-10
**Agent:** Codex Prompt B
**Required verification type:** non-UI verification
**Buildout plan:** docs/12-reset-gated-implementation-plan-2026-05-10.md
**Northstar:** docs/00-product-northstar.md

## Scope Checked

- Feature card read: `RG1 - Operator Benchmark Harness` / `R03 - Live benchmark runner and quality summary`
- Files changed by feature branch: `packages/core/src/core/benchmark_suite.py`, `packages/core/src/core/live_benchmark_runner.py`, `packages/core/tests/test_live_benchmark_runner.py`, saved RG1 raw outputs, and reset control docs
- Explicit anti-goals reviewed: no RG2 search/source work, no UI work, no export work, no `main` sync
- Confirmed merge target is `rebuild/validated-leads-loop`: yes
- Confirmed adjacent reset features were not implemented: yes; diff stayed inside runner support, saved artifacts, and queue-state docs

## Non-UI Verification Steps

**Command(s):**

```bash
git diff --check rebuild/validated-leads-loop...feat/reset-r03-live-benchmark-runner
cd packages/core && uv run pytest tests/test_arizona_k12_benchmark.py tests/test_benchmark_suite.py tests/test_quality_report.py tests/test_live_benchmark_runner.py -q
cd packages/core && uv run python -m core.live_benchmark_runner --help
cd apps/api && uv run alembic upgrade head
cd apps/api && env -u OPENAI_BASE_URL -u OPENAI_API_KEY uv run uvicorn api.main:app --port 8000
export WR_API_INTERNAL_TOKEN="$(awk -F= '/^WR_API_INTERNAL_TOKEN=/{print $2}' apps/api/.env)"; cd packages/core && uv run python -m core.live_benchmark_runner --api-base-url http://127.0.0.1:8000 --output-dir ../../audits/raw/reset-2026-05-10/rg1
git diff --name-only rebuild/validated-leads-loop...feat/reset-r03-live-benchmark-runner
```

**Expected output:**

```text
Targeted core tests pass, the runner CLI is callable, the local API can execute the full RG1 live suite with the shell-level Ollama overrides unset, and the saved RG1 JSON/HTTP artifacts plus quality summary reflect the rerun.
```

**Actual output summary:**

```text
18 passed, 1 skipped in 0.32s
git diff --check returned clean
Runner help rendered successfully
Alembic upgrade head completed
Local API started cleanly only when OPENAI_BASE_URL and OPENAI_API_KEY were unset in the shell
Live runner completed all 6 RG1 cases and rewrote quality-summary.json plus per-case JSON/HTTP artifacts
HTTP artifacts: Arizona 200, Lee 200, Healthcare 503 openai_failed, Finance 200, Detroit 200, Privacy 422 blocked
Quality summary: 6 cases total, 1 pass, 5 fail; Arizona and Lee remain below the broad-query volume floor, privacy refusal still blocks before search
```

## Screenshots Required

R03 is explicitly non-UI. No browser QA or screenshots required.

## Tests Run

| Command | Result | Notes |
| --- | --- | --- |
| `git diff --check rebuild/validated-leads-loop...feat/reset-r03-live-benchmark-runner` | pass | No whitespace or conflict-marker issues in the feature diff |
| `cd packages/core && uv run pytest tests/test_arizona_k12_benchmark.py tests/test_benchmark_suite.py tests/test_quality_report.py tests/test_live_benchmark_runner.py -q` | pass | `18 passed, 1 skipped` |
| `cd packages/core && uv run python -m core.live_benchmark_runner --help` | pass | CLI help rendered with expected flags |
| `cd apps/api && uv run alembic upgrade head` | pass | Database schema up to date for local API run |
| `cd apps/api && env -u OPENAI_BASE_URL -u OPENAI_API_KEY uv run uvicorn api.main:app --port 8000` | pass | Protected local API started cleanly with shell-level Ollama overrides removed |
| `export WR_API_INTERNAL_TOKEN=...; cd packages/core && uv run python -m core.live_benchmark_runner --api-base-url http://127.0.0.1:8000 --output-dir ../../audits/raw/reset-2026-05-10/rg1` | pass | Executed all 6 live RG1 cases and saved raw JSON/HTTP artifacts plus quality summary |
| `git diff --name-only rebuild/validated-leads-loop...feat/reset-r03-live-benchmark-runner` | pass | Scope limited to runner support, saved artifacts, and reset control docs |

## Northstar Reflection Result

| Question | Yes/No | Notes |
| --- | --- | --- |
| Does this directly improve natural-language query -> high-quality validated leads -> export? | Yes | Indirectly but materially: it makes the live gate executable and preserves the real output shape for audit. |
| Does it reduce false confidence, bad contacts, wrong personas, or unsupported source claims? | Yes | The runner saves those failures explicitly instead of leaving RG1 at replay-only evidence. |
| Does it avoid organizing or beautifying untrusted data? | Yes | No UI or export surface changed. |
| Does it keep `main` untouched and target only `rebuild/validated-leads-loop`? | Yes | QA and merge stay on rebuild only. |
| Is the feature independently mergeable? | Yes | The live runner, parser reuse, tests, and saved artifacts stand on their own. |
| Can the next agent discover state from docs without chat context? | Yes | STATUS and docs/12 are updated to send the queue to Prompt C for RG1 audit. |
| Is there browser QA or explicit non-UI verification? | Yes | Explicit non-UI verification captured above. |
| Is the scope small enough for a narrow reset feature? | Yes | No adjacent RG2 or UI/export implementation leaked into the branch. |

## Findings

### Blocking

- None on the R03 feature itself.

### Non-Blocking

- The previously saved RG1 artifact summary in `STATUS.md` was stale. The rerun changed Detroit from `503 openai_failed` to `200` with one weak review row, while healthcare remained the only `503 openai_failed` case.
- The product remains red by northstar. Arizona returned 4 categorized rows with 5 named-account coverage misses; Lee broad-query volume remained 4 categorized rows; finance and Detroit each returned only 1 categorized row; privacy still blocked correctly before search.

## Merge Decision

**Decision:** merge

**Reason:**

- The required test/API/live-runner verification passed.
- The runner is executable against the protected local API path and correctly writes the raw RG1 evidence bundle.
- The diff is scoped to the runner slice and its evidence artifacts.
- The rerun strengthens audit truth by replacing stale saved outputs with current reproducible ones.

**Merged into:** rebuild/validated-leads-loop

## Follow-Up Issues

- Assign Prompt C to audit `RG1 - Operator Benchmark Harness`.
- Keep RG2 and all downstream gates blocked until the RG1 gate report records an explicit decision.

## Handoff

```text
Feature: R03 - Live benchmark runner and quality summary
Branch: feat/reset-r03-live-benchmark-runner
Status: qa_passed_merge_allowed
What changed: Added an executable live benchmark runner and CLI, reused saved-artifact observation parsing, reset the protected sandbox before suite execution by default, and saved the current RG1 live JSON/HTTP bundle plus quality summary under audits/raw/reset-2026-05-10/rg1.
Tests or QA run: git diff --check on the feature diff, targeted core pytest suite, runner --help, alembic upgrade head, protected local uvicorn startup with OPENAI overrides unset, and the full live runner command against http://127.0.0.1:8000
Screenshots or report: .gstack/qa-reports/qa-report-r03-live-benchmark-runner-2026-05-10.md
Northstar reflection: The feature does not make the product green, but it makes RG1 auditable with live saved evidence instead of replay-only evidence and keeps the red failures visible.
Next pointer: Prompt C only. Audit RG1 on rebuild/validated-leads-loop; do not unlock RG2 unless the gate report explicitly advances.
Open questions: none blocking RG1 audit; the known requirement remains that local API startup must unset shell-level OPENAI_BASE_URL and OPENAI_API_KEY overrides.
```
