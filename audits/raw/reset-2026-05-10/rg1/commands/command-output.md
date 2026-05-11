# RG1 Command Output - 2026-05-10

Branch: `audit/reset-rg1-benchmark-harness`
Integration branch: `rebuild/validated-leads-loop`

## Initial State

```text
$ git status --short --branch
## rebuild/validated-leads-loop...origin/rebuild/validated-leads-loop
```

```text
$ find audits/gates/reset-2026-05-10 -maxdepth 1 -type f | sort
audits/gates/reset-2026-05-10/rg0-w5-hold.md
```

```text
$ git log --oneline --decorate --max-count=8 rebuild/validated-leads-loop
f832f32 (HEAD -> rebuild/validated-leads-loop, origin/rebuild/validated-leads-loop) merge: qa r03 live benchmark runner
45c25d1 (origin/feat/reset-r03-live-benchmark-runner, feat/reset-r03-live-benchmark-runner) test(r03): qa live benchmark runner
225bd01 feat(r03): add live benchmark runner
d12724d (origin/feat/reset-r02-benchmark-replay-harness, feat/reset-r02-benchmark-replay-harness) qa(r02): verify benchmark replay harness
57a22e7 feat: add benchmark replay harness
af5dc52 docs(reset): harden control-plane authority
ab90c32 docs(reset): unblock r02 after r01 qa
a114e5c docs(reset): record r01 qa merge state
```

## Replay Benchmarks

```text
$ cd packages/core && uv run pytest tests/test_arizona_k12_benchmark.py tests/test_benchmark_suite.py tests/test_quality_report.py -q
....s............                                                        [100%]
16 passed, 1 skipped in 0.30s
```

## Live Runner Setup

```text
$ cd packages/core && uv run python -m core.live_benchmark_runner --help
usage: live_benchmark_runner.py [-h] [--api-base-url API_BASE_URL]
                                [--output-dir OUTPUT_DIR]
                                [--mode {scout,full}] [--no-reset-sandbox]
                                [--api-token API_TOKEN]

Run the White Rabbit RG1 live benchmark suite.
```

```text
$ curl -sS -i http://127.0.0.1:8000/health
curl: (7) Failed to connect to 127.0.0.1 port 8000 after 0 ms: Couldn't connect to server
```

```text
$ cd apps/api && uv run alembic upgrade head
INFO  [alembic.runtime.migration] Context impl PostgresqlImpl.
INFO  [alembic.runtime.migration] Will assume transactional DDL.
```

```text
$ cd apps/api && env -u OPENAI_BASE_URL -u OPENAI_API_KEY uv run uvicorn api.main:app --port 8000
INFO:     Started server process [76264]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
```

```text
$ curl -sS -i http://127.0.0.1:8000/health
HTTP/1.1 200 OK
date: Mon, 11 May 2026 03:53:21 GMT
server: uvicorn
content-length: 15
content-type: application/json

{"status":"ok"}
```

## Live Runner

```text
$ cd packages/core && WR_API_INTERNAL_TOKEN="$(awk -F= '/^WR_API_INTERNAL_TOKEN=/{print $2}' ../../apps/api/.env)" uv run python -m core.live_benchmark_runner --api-base-url http://127.0.0.1:8000 --output-dir ../../audits/raw/reset-2026-05-10/rg1
{
  "api_base_url": "http://127.0.0.1:8000",
  "mode": "scout",
  "output_root": "../../audits/raw/reset-2026-05-10/rg1",
  "suite_report": {
    "suite_id": "required_lead_quality_suite",
    "total_cases": 6,
    "passed_cases": 1,
    "failed_cases": 5,
    "guardrail_mismatches": [],
    "observation_mismatches": [
      "thomas-arizona-k12: coverage",
      "lee-commodity-buyers: volume",
      "healthcare-it-phoenix: persona, contact, source, volume",
      "finance-cisos-new-york: contact, volume",
      "manufacturing-ops-detroit: persona, contact, source, volume"
    ]
  }
}
```

## Live Summary Extraction

```text
$ jq '{suite_id,total_cases,passed_cases,failed_cases,guardrail_mismatches,observation_mismatches}' audits/raw/reset-2026-05-10/rg1/quality-summary.json
{
  "suite_id": "required_lead_quality_suite",
  "total_cases": 6,
  "passed_cases": 1,
  "failed_cases": 5,
  "guardrail_mismatches": [],
  "observation_mismatches": [
    "thomas-arizona-k12: coverage",
    "lee-commodity-buyers: volume",
    "healthcare-it-phoenix: persona, contact, source, volume",
    "finance-cisos-new-york: contact, volume",
    "manufacturing-ops-detroit: persona, contact, source, volume"
  ]
}
```

## Final Checks

```text
$ git diff --check
```

No output.

```text
$ git diff --name-only -- 'apps/**' 'packages/**'
```

No output.

```text
$ git status --short --branch
## audit/reset-rg1-benchmark-harness
 M STATUS.md
 M audits/raw/reset-2026-05-10/rg1/finance-cisos-new-york.json
 M audits/raw/reset-2026-05-10/rg1/healthcare-it-phoenix.http
 M audits/raw/reset-2026-05-10/rg1/healthcare-it-phoenix.json
 M audits/raw/reset-2026-05-10/rg1/lee-commodity-buyers.json
 M audits/raw/reset-2026-05-10/rg1/manufacturing-ops-detroit.http
 M audits/raw/reset-2026-05-10/rg1/manufacturing-ops-detroit.json
 M audits/raw/reset-2026-05-10/rg1/privacy-reject-homeowner-phones.json
 M audits/raw/reset-2026-05-10/rg1/quality-summary.json
 M audits/raw/reset-2026-05-10/rg1/thomas-arizona-k12.json
 M docs/12-reset-gated-implementation-plan-2026-05-10.md
?? audits/gates/reset-2026-05-10/rg1-benchmark-harness.md
?? audits/raw/reset-2026-05-10/rg1/commands/
?? audits/raw/reset-2026-05-10/rg1/evidence-notes.md
```
