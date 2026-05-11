# QA Report - Reset Feature

**Feature ID:** R02
**Feature name:** Golden benchmark replay harness
**Branch:** feat/reset-r02-benchmark-replay-harness
**PR target:** rebuild/validated-leads-loop
**Date:** 2026-05-10
**Agent:** Codex Prompt B
**Required verification type:** non-UI verification
**Buildout plan:** docs/12-reset-gated-implementation-plan-2026-05-10.md
**Northstar:** docs/00-product-northstar.md

## Scope Checked

- Feature card read: `RG1 - Operator Benchmark Harness` / `R02 - Golden benchmark replay harness`
- Files changed: `packages/core/src/core/benchmark_suite.py`, `packages/core/tests/test_benchmark_suite.py`, `STATUS.md`, `docs/12-reset-gated-implementation-plan-2026-05-10.md`
- Explicit anti-goals reviewed: no live runner implementation, no RG2 search/source changes, no UI work, no `main` sync
- Confirmed `main` untouched: yes
- Confirmed merge target is `rebuild/validated-leads-loop`: yes

## Non-UI Verification Steps

**Command(s):**

```bash
cd packages/core && uv run pytest tests/test_arizona_k12_benchmark.py tests/test_benchmark_suite.py tests/test_quality_report.py -q
git diff --check
cd packages/core && uv run python - <<'PY'
from core.benchmark_suite import build_required_benchmark_suite, build_replay_benchmark_observations, evaluate_required_benchmark_suite
suite = build_required_benchmark_suite()
observations = build_replay_benchmark_observations()
report = evaluate_required_benchmark_suite(suite, observations)
print('suite', report.suite_id)
print('cases', report.total_cases, 'passed', report.passed_cases, 'failed', report.failed_cases)
for bid, obs in observations.items():
    print(
        bid,
        'rows=', obs.categorized_row_count,
        'usable=', obs.high_trust_usable_count,
        'review=', obs.review_count,
        'org_only=', obs.organization_only_count,
        'not_found=', obs.not_found_count,
        'failed=', obs.failed_count,
        'coverage_missing=', list(getattr(obs, 'expected_target_coverage_missing', ())),
        'http=', obs.http_status,
        'error=', obs.error_code,
        'guardrail=', obs.guardrail_status,
    )
print('guardrail_mismatches', list(report.guardrail_mismatches))
print('observation_mismatches', list(report.observation_mismatches))
PY
git diff --name-only rebuild/validated-leads-loop...feat/reset-r02-benchmark-replay-harness
git diff --name-only rebuild/validated-leads-loop...feat/reset-r02-benchmark-replay-harness -- 'apps/**' 'packages/core/tests/fixtures/**' 'apps/web/**' 'apps/api/**'
```

**Expected output:**

```text
Targeted core tests pass, the patch is whitespace-clean, replay observations reproduce the saved May 10 failures offline, and the diff stays limited to replay-harness code/tests plus reset status docs.
```

**Actual output summary:**

```text
16 passed, 1 skipped in 0.47s
git diff --check returned clean
Replay suite summary: 6 cases, 1 pass, 5 fail against saved May 10 evidence
Arizona replay preserved 3 categorized review rows with 5 missing target accounts
Lee broad replay preserved 4 categorized rows and failed the volume floor
Detroit replay preserved HTTP 503 with error_code=openai_failed
Changed files were limited to benchmark replay code/tests plus STATUS/docs/12
No fixtures, web files, API files, or RG2 search implementation files changed
```

## Screenshots Required

R02 is explicitly non-UI. No browser QA or screenshots required.

## Tests Run

| Command | Result | Notes |
| --- | --- | --- |
| `cd packages/core && uv run pytest tests/test_arizona_k12_benchmark.py tests/test_benchmark_suite.py tests/test_quality_report.py -q` | pass | `16 passed, 1 skipped` |
| `git diff --check` | pass | No whitespace or conflict-marker issues |
| `cd packages/core && uv run python ... replay summary` | pass | Confirmed offline replay preserves current failures and tier/coverage counts |
| `git diff --name-only rebuild/validated-leads-loop...feat/reset-r02-benchmark-replay-harness` | pass | Scope stayed inside replay-harness code/tests and reset control docs |
| `git diff --name-only ... -- 'apps/**' 'packages/core/tests/fixtures/**' 'apps/web/**' 'apps/api/**'` | pass | No live runner, search-source, fixture-pack, API, or UI leakage |

## Northstar Reflection Result

| Question | Yes/No | Notes |
| --- | --- | --- |
| Does this directly improve natural-language query -> high-quality validated leads -> export? | Yes | Indirectly: it makes the benchmark gate fail saved bad outputs instead of silently accepting them. |
| Does it reduce false confidence, bad contacts, wrong personas, or unsupported source claims? | Yes | The replay summary now exposes missing target coverage, volume misses, contact misses, and preserved HTTP failures. |
| Does it avoid organizing or beautifying untrusted data? | Yes | No UI or presentation surface changed. |
| Does it keep `main` untouched and target only `rebuild/validated-leads-loop`? | Yes | QA and merge target are rebuild only. |
| Is the feature independently mergeable? | Yes | The diff is small, test-backed, and scoped to replay evaluation. |
| Can the next agent discover state from docs without chat context? | Yes | STATUS and docs/12 now point to R03 as the next same-gate feature after merge. |
| Is there browser QA or explicit non-UI verification? | Yes | Explicit non-UI verification captured above. |
| Is the scope small enough for a narrow reset feature? | Yes | No adjacent RG2 or UI work landed. |

## Findings

### Blocking

- None.

### Non-Blocking

- None.

## Merge Decision

**Decision:** merge

**Reason:**

- The required core verification passes cleanly.
- Replay evaluation reproduces the current saved failures offline, which is exactly the R02 benchmark-harness goal.
- The diff is scoped to replay-harness logic/tests plus required queue-state docs.
- No live runner, search-coverage, API, or UI implementation leaked into the branch.

**Merged into:** rebuild/validated-leads-loop

## Follow-Up Issues

- Mark `R03 - Live benchmark runner and quality summary` as the next same-gate `ready` feature after merge.
- Keep RG2 and downstream gates blocked until Prompt C advances RG1.

## Handoff

```text
Feature: R02 - Golden benchmark replay harness
Branch: feat/reset-r02-benchmark-replay-harness
Status: qa_passed_merge_allowed
What changed: Added replay observations over saved May 10 benchmark artifacts, reused quality-report logic, surfaced broad-query volume and target-coverage failures, and preserved HTTP/error evidence for Detroit and the B2C refusal replay.
Tests or QA run: targeted core pytest suite, git diff --check, replay summary command, scope diff audit
Screenshots or report: .gstack/qa-reports/qa-report-r02-benchmark-replay-harness-2026-05-10.md
Northstar reflection: The branch makes RG1 fail bad saved outputs offline instead of hiding low-volume or missing-coverage runs behind synthetic expectations.
Next pointer: Prompt A only. Start `R03 - Live benchmark runner and quality summary` on `feat/reset-r03-live-benchmark-runner`; do not unlock RG2.
Open questions: none blocking R03.
```
