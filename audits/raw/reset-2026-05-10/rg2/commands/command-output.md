# RG2 Command Output

Branch: `audit/reset-rg2-search-source-coverage`

## State Proof

```text
$ git status --short --branch
## codex/clinical-final-mockups
```

The initial checkout was clean but not on the integration branch. Prompt C then fetched and branched from `rebuild/validated-leads-loop`.

```text
$ git fetch origin rebuild/validated-leads-loop
From https://github.com/mschwar/white-rabbit
 * branch            rebuild/validated-leads-loop -> FETCH_HEAD

$ git switch rebuild/validated-leads-loop
Switched to branch 'rebuild/validated-leads-loop'
Your branch is up to date with 'origin/rebuild/validated-leads-loop'.

$ git pull --ff-only origin rebuild/validated-leads-loop
Already up to date.

$ git switch -c audit/reset-rg2-search-source-coverage
Switched to a new branch 'audit/reset-rg2-search-source-coverage'
```

R04, R05, and R06 were confirmed merged into `rebuild/validated-leads-loop`.

```text
$ git rev-parse rebuild/validated-leads-loop origin/rebuild/validated-leads-loop HEAD
b9bf2c6a4074c59ea5a64797ef62c3083af75180
b9bf2c6a4074c59ea5a64797ef62c3083af75180
b9bf2c6a4074c59ea5a64797ef62c3083af75180

$ git merge-base --is-ancestor 5673540 rebuild/validated-leads-loop; printf 'r04=%s\n' $?
r04=0

$ git merge-base --is-ancestor ca700ae rebuild/validated-leads-loop; printf 'r05=%s\n' $?
r05=0

$ git merge-base --is-ancestor aad7d7d rebuild/validated-leads-loop; printf 'r06qa=%s\n' $?
r06qa=0
```

Existing gate reports before RG2:

```text
$ find audits/gates/reset-2026-05-10 -maxdepth 1 -type f -print | sort
audits/gates/reset-2026-05-10/rg0-w5-hold.md
audits/gates/reset-2026-05-10/rg1-benchmark-harness.md
```

## Required Non-UI Verification

```text
$ git diff --check
```

No output.

```text
$ cd packages/core && uv run pytest tests/test_query_planner.py tests/test_search.py tests/test_benchmark_suite.py -q
..................                                                       [100%]
18 passed in 0.27s
```

## Local API Startup

The first startup attempt failed because the ambient shell had an invalid OpenAI override. The actual key is not recorded here.

```text
$ cd apps/api && env -u OPENAI_BASE_URL uv run uvicorn api.main:app --host 127.0.0.1 --port 8000
RuntimeError: OpenAI model unreachable: gpt-4o-mini @ https://api.openai.com/v1 - Error code: 401 - Incorrect API key provided.
```

The API started after unsetting both ambient OpenAI overrides so `apps/api/.env` supplied the local development values.

```text
$ cd apps/api && env -u OPENAI_API_KEY -u OPENAI_BASE_URL uv run uvicorn api.main:app --host 127.0.0.1 --port 8000
INFO:     Application startup complete.
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
```

## Live Scout Benchmark

```text
$ cd packages/core && env -u OPENAI_API_KEY -u OPENAI_BASE_URL WR_API_INTERNAL_TOKEN="$(awk -F= '/^WR_API_INTERNAL_TOKEN=/{print $2}' ../../apps/api/.env)" uv run python -m core.live_benchmark_runner --api-base-url http://127.0.0.1:8000 --output-dir ../../audits/raw/reset-2026-05-10/rg2/scout
```

Summary excerpt from `audits/raw/reset-2026-05-10/rg2/scout/quality-summary.json`:

```json
{
  "total_cases": 6,
  "passed_cases": 1,
  "failed_cases": 5,
  "guardrail_mismatches": [],
  "observation_mismatches": [
    "thomas-arizona-k12: source",
    "lee-commodity-buyers: volume",
    "healthcare-it-phoenix: persona, contact, source, volume",
    "finance-cisos-new-york: persona, contact, source, volume",
    "manufacturing-ops-detroit: persona, contact, source, volume"
  ]
}
```

Case summary:

```text
thomas-arizona-k12: HTTP 200, 8 rows, 8/8 target accounts covered, 0 high-trust usable
lee-commodity-buyers: HTTP 200, 2 rows, 0 high-trust usable, high-volume floor false
healthcare-it-phoenix: HTTP 200, 4 rows, 0 high-trust usable, high-volume floor false
finance-cisos-new-york: HTTP 503, 0 rows, error_code openai_failed
manufacturing-ops-detroit: HTTP 503, 0 rows, error_code openai_failed
privacy-reject-homeowner-phones: HTTP 422, blocked before search
```

## Live Full Benchmark

```text
$ cd packages/core && env -u OPENAI_API_KEY -u OPENAI_BASE_URL WR_API_INTERNAL_TOKEN="$(awk -F= '/^WR_API_INTERNAL_TOKEN=/{print $2}' ../../apps/api/.env)" uv run python -m core.live_benchmark_runner --api-base-url http://127.0.0.1:8000 --output-dir ../../audits/raw/reset-2026-05-10/rg2/full --mode full
```

Summary excerpt from `audits/raw/reset-2026-05-10/rg2/full/quality-summary.json`:

```json
{
  "total_cases": 6,
  "passed_cases": 2,
  "failed_cases": 4,
  "guardrail_mismatches": [],
  "observation_mismatches": [
    "lee-commodity-buyers: source, volume",
    "healthcare-it-phoenix: persona, contact, source, volume",
    "finance-cisos-new-york: persona, contact, volume",
    "manufacturing-ops-detroit: persona, contact, source, volume"
  ]
}
```

Case summary:

```text
thomas-arizona-k12: HTTP 200, 9 rows, 8/8 target accounts covered, 0 high-trust usable
lee-commodity-buyers: HTTP 200, 4 rows, 0 high-trust usable, high-volume floor false
healthcare-it-phoenix: HTTP 200, 3 rows, 0 high-trust usable, high-volume floor false
finance-cisos-new-york: HTTP 200, 5 rows, 0 high-trust usable, high-volume floor false
manufacturing-ops-detroit: HTTP 503, 0 rows, error_code openai_failed
privacy-reject-homeowner-phones: HTTP 422, blocked before search
```

## Source Snapshot Collection

```text
$ cd packages/core && env -u OPENAI_API_KEY -u OPENAI_BASE_URL uv run python - <<'PY'
...
PY
```

The script ran `fetch_search_results()` against the five non-privacy benchmark prompts with `max_results=100` and saved:

- `audits/raw/reset-2026-05-10/rg2/source-snapshots.jsonl`
- `audits/raw/reset-2026-05-10/rg2/source-snapshot-summary.json`

Summary:

```text
thomas-arizona-k12: 98 sources, 8 Tavily searches, 8 vendor queries, max query length 164, 0 queries over 400 chars, all 8 target accounts had source hits.
lee-commodity-buyers: 90 sources, 6 Tavily searches, 6 vendor queries, max query length 57, 0 queries over 400 chars.
healthcare-it-phoenix: 75 sources, 6 Tavily searches, 6 vendor queries, max query length 55, 0 queries over 400 chars.
finance-cisos-new-york: 73 sources, 6 Tavily searches, 6 vendor queries, max query length 68, 0 queries over 400 chars.
manufacturing-ops-detroit: 90 sources, 6 Tavily searches, 6 vendor queries, max query length 49, 0 queries over 400 chars.
```

## Worktree Note

During the long live runs, another process switched the checkout to `codex/clinical-final-mockups` and committed unrelated mockup work. The audit branch was resumed afterward. No product code was edited by this audit.
