# Reset Gate Review - RG1 Operator Benchmark Harness

**Branch:** `audit/reset-rg1-benchmark-harness`
**Integration branch:** `rebuild/validated-leads-loop`
**Date:** 2026-05-10
**Decision:** `advance`
**Current product gate:** `red`

## Evidence Used

- `STATUS.md`
- `docs/00-product-northstar.md`
- `docs/12-reset-gated-implementation-plan-2026-05-10.md`
- `docs/13-pipeline-orchestrator-contract-2026.md`
- `audits/zero-trust-codebase-audit-2026-05-10.md`
- `audits/raw/zero-trust-2026-05-10/evidence-ledger.md`
- `audits/raw/zero-trust-2026-05-10/operator-feedback-volume-2026-05-10.md`
- `audits/raw/reset-2026-05-10/rg1/quality-summary.json`
- `audits/raw/reset-2026-05-10/rg1/evidence-notes.md`
- `packages/core/tests/fixtures/operator_evidence_fixture_pack.json`
- `packages/core/tests/fixtures/benchmark_suite.json`

## Commands Run

```bash
git fetch origin
git status --short --branch
git branch --all --merged rebuild/validated-leads-loop
git log --oneline --decorate --max-count=40 rebuild/validated-leads-loop
find audits/gates/reset-2026-05-10 -maxdepth 1 -type f | sort
cd packages/core && uv run pytest tests/test_arizona_k12_benchmark.py tests/test_benchmark_suite.py tests/test_quality_report.py -q
cd packages/core && uv run python -m core.live_benchmark_runner --help
curl -sS -i http://127.0.0.1:8000/health
cd apps/api && uv run alembic upgrade head
cd apps/api && env -u OPENAI_BASE_URL -u OPENAI_API_KEY uv run uvicorn api.main:app --port 8000
curl -sS -i http://127.0.0.1:8000/health
cd packages/core && WR_API_INTERNAL_TOKEN="$(awk -F= '/^WR_API_INTERNAL_TOKEN=/{print $2}' ../../apps/api/.env)" uv run python -m core.live_benchmark_runner --api-base-url http://127.0.0.1:8000 --output-dir ../../audits/raw/reset-2026-05-10/rg1
jq '{suite_id,total_cases,passed_cases,failed_cases,guardrail_mismatches,observation_mismatches}' audits/raw/reset-2026-05-10/rg1/quality-summary.json
git diff --check
git diff --name-only -- 'apps/**' 'packages/**'
```

Raw command excerpts are saved in `audits/raw/reset-2026-05-10/rg1/commands/command-output.md`.

## Live Results

Replay benchmarks passed:

```text
16 passed, 1 skipped in 0.30s
```

The live runner was executable against the protected local API path after applying Alembic migrations and starting FastAPI with `OPENAI_BASE_URL` and shell-level `OPENAI_API_KEY` unset. The runner reset the sandbox and saved JSON/HTTP artifacts for all six RG1 cases.

| Case | HTTP | Categorized rows | High-trust usable | Gate observation |
| --- | ---: | ---: | ---: | --- |
| `thomas-arizona-k12` | 200 | 9 | 0 | Missed 1 of 8 named targets: Maricopa Unified School District. |
| `lee-commodity-buyers` | 200 | 2 | 0 | Failed broad-query volume and quality expectations. |
| `healthcare-it-phoenix` | 200 | 2 | 0 | Failed persona, contact, source, and volume expectations. |
| `finance-cisos-new-york` | 200 | 3 | 0 | Failed contact and volume expectations. |
| `manufacturing-ops-detroit` | 503 | 0 | 0 | Still returns `openai_failed`; not yet a recoverable failed row. |
| `privacy-reject-homeowner-phones` | 422 | 0 | 0 | Blocked before search, as required. |

Suite totals: 6 cases, 1 passed, 5 failed, 0 guardrail mismatches. Observation mismatches were recorded for Thomas Arizona coverage plus broad-query volume/quality.

## Screenshots And Artifacts

No browser screenshots were required because RG1 is non-UI harness work.

Artifacts:

- Raw live benchmark outputs: `audits/raw/reset-2026-05-10/rg1/`
- Command output notes: `audits/raw/reset-2026-05-10/rg1/commands/command-output.md`
- Evidence notes: `audits/raw/reset-2026-05-10/rg1/evidence-notes.md`

## Value Prop Verdict

The current product does **not** give enough result volume, evidence, or export value for the operator loop.

Result volume is still inadequate: Lee's broad commodity-buyer benchmark returned 2 categorized rows, healthcare returned 2, finance returned 3, and manufacturing returned 0. That does not meet the product northstar's broad-query 50-500+ direction and does not even clear the earlier 10-row escape hatch for broad prompts.

Evidence is still inadequate: the non-privacy live cases produced 0 high-trust usable leads, missing or failed contacts dominate, and healthcare flagged a fake email. Thomas's named-account prompt improved to 9 categorized rows and 7 of 8 expected targets covered, but it still produced 0 high-trust usable rows and missed Maricopa.

Export value remains insufficient and unproven for RG1: this gate exercised Scout-mode benchmark evidence, not a sales-first UI-to-CSV path. The May 10 zero-trust audit's export finding still stands until RG5 proves that useful rows, tier labels, evidence, and sales-first columns survive CSV and DB readback.

RG1 advances anyway because its job is not to prove the product valuable. Its job is to make these failures executable, reproducible, and hard to hand-wave.

## Findings

1. RG1 was ready for audit: R01, R02, and R03 are merged into `rebuild/validated-leads-loop`; no RG1 gate report existed before this branch; RG1 had not already advanced.
2. The replay harness is reproducible without live credentials: the required benchmark tests passed with 16 passing and 1 skipped.
3. The live runner is executable against the protected local API path and saves per-case JSON/HTTP artifacts plus `quality-summary.json`.
4. The harness fails bad output correctly. It records broad-query volume misses, low contact/source/persona quality, target coverage misses, and privacy guardrail behavior.
5. Thomas's exact Arizona prompt is now measurable across all 8 target accounts, but the current run covered only 7 of 8 and produced 0 high-trust usable leads.
6. Broad Lee/Thomas-style prompts do not pass with 2-3 returned rows. The suite marks volume mismatches and quality failures for Lee commodity buyers, healthcare IT Phoenix, finance CISOs New York, and manufacturing ops Detroit.
7. Manufacturing role-as-name is still not recoverable in live product output. It returns HTTP 503 with `openai_failed`. The harness captures that as a failing case, and RG3 must convert this class of failure into explicit failed/noisy rows.
8. B2C/private phone targeting is blocked before search with HTTP 422 and no guardrail mismatch.

## What Worked

- The reset queue now has a live benchmark harness instead of anecdotal operator feedback.
- The raw artifacts are organized under the required RG1 directory and can be re-read by future Prompt A/B/C agents.
- The privacy guardrail case passed in the live run.
- The quality summary is specific enough to identify the next search-volume work: Lee commodity buyers, healthcare IT Phoenix, finance CISOs New York, and manufacturing ops Detroit are the broad prompts RG2 must improve.

## What Did Not Work

- The product still returns too few broad-query candidates.
- The product still returns 0 high-trust usable leads across live non-privacy cases.
- The manufacturing parse failure still crashes the request instead of becoming a failed/review row.
- The live harness does not prove export value; it only proves Scout-mode benchmark evidence.

## New Gaps Found

- The RG1 audit criteria ask reviewers to confirm manufacturing role-as-name is represented as failed rather than 503, but RG3 owns the parse-salvage repair needed to make that true. Carry this forward as a hard RG3 acceptance check.
- Thomas Arizona coverage is better than the May 10 zero-trust audit, but still incomplete. RG2 must preserve all 8 named accounts as coverage obligations and stop treating 7 of 8 as enough.

## Recommended Scope Change For Next Gate

No expansion beyond RG2. Execute R04-R06 in order, with one additional emphasis: every RG2 report and QA handoff should compare raw source/candidate volume against the same RG1 benchmark prompts so the team can see whether planner/source aggregation actually increased useful coverage.

RG2 should use these exact broad prompts for result-volume proof:

- `commodity buyers at retail lumber yards in Washington`
- `healthcare IT directors in Phoenix`
- `finance CISOs at financial services firms in New York`
- `manufacturing operations leaders in Detroit`

RG2 should use the Thomas Arizona prompt for named-account coverage proof and must require all 8 target accounts to appear in an output category.

## Next Main Promotion Recommendation

Do not sync `main`. RG1 advancement is a harness/control advancement only. The product remains red and should not receive another operator-use promotion until RG2/RG3 materially improve volume, coverage, and evidence quality, and a later Prompt C explicitly recommends promotion.

## Next Prompt A Assignment

Advance RG1, mark RG2 `in_progress`, and mark `R04 - High-volume query planner and search aggregation` as `ready`.

```text
You are Prompt A for White Rabbit reset feature R04.

Work in /Users/mschwar/Documents/white-rabbit on rebuild/validated-leads-loop only. Do not merge or target main.

First prove current state:
- read AGENTS.md
- read STATUS.md
- read docs/00-product-northstar.md
- read docs/12-reset-gated-implementation-plan-2026-05-10.md
- read docs/13-pipeline-orchestrator-contract-2026.md
- read audits/gates/reset-2026-05-10/rg1-benchmark-harness.md
- run git status --short --branch

Create or resume branch feat/reset-r04-high-volume-search from rebuild/validated-leads-loop.

Implement only R04 - High-volume query planner and search aggregation.

Required scope:
- follow the RG2 requirements in docs/12-reset-gated-implementation-plan-2026-05-10.md
- preserve Thomas Arizona named-account coverage obligations for all 8 districts
- add safe volume controls such as max_results and optional aggressive_breadth where they belong in the existing core/API path
- use multi-query planning, aggregation, and deduplication so broad prompts are not artificially starved by a single Tavily call
- use role synonyms and light geographic/vertical expansion only for broad prompts
- do not implement R05 source snapshot storage or R06 not-found/organization-only writers
- do not edit UI/export/persistence surfaces

Required verification:
- cd packages/core && uv run pytest tests/test_query_planner.py tests/test_search.py tests/test_benchmark_suite.py -q
- git diff --check
- update STATUS.md and docs/12 with the R04 status and exact Prompt B handoff
- commit and push the feature branch

Do not merge. Do not unlock R05 until Prompt B QA passes and merges R04 into rebuild/validated-leads-loop. Do not sync main.
```
