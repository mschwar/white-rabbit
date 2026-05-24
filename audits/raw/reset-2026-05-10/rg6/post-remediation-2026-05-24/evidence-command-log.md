# RG6 post-remediation evidence command log

Date: 2026-05-24 UTC
Branch: audit/reset-rg6-post-remediation
Base: current main at 7054574 docs: advance rg6 remediation to prompt c

## Successful commands

```bash
WR_EXTERNAL_ENV_FILE=/Users/mschwar/Documents/white-rabbit.pre-hygiene-backup.20260522-225154/apps/web/.env.local \
  python3 audits/raw/reset-2026-05-10/rg6/post-remediation-2026-05-24/collect_post_remediation_web_evidence.py
```

Result: captured sanitized production web evidence under this directory. Direct API health/readiness passed; tokenless direct scout remained protected; web auth and privacy guardrail passed; source-assisted proof route returned 200; Arizona K-12 primary scout returned HTTP 429 because the production sandbox query cap was already exhausted.

```bash
cd packages/core && \
  uv run python -m core.sampled_precision \
  ../../audits/raw/reset-2026-05-10/rg6/post-remediation-2026-05-24/live-required-benchmark \
  --write-json ../../audits/raw/reset-2026-05-10/rg6/post-remediation-2026-05-24/sampled-precision-required-suite.json
```

Result: wrote a deterministic sampled-precision packet, but the required benchmark output directory had no fresh case outputs because the live benchmark run was blocked before execution. The packet therefore has sampled_row_count=0 and cannot clear RG6.

## Blocked command

```bash
set -a; . /Users/mschwar/Documents/white-rabbit.pre-hygiene-backup.20260522-225154/apps/web/.env.local; set +a; \
cd packages/core && \
uv run python -m core.live_benchmark_runner \
  --api-base-url https://white-rabbit-api.fly.dev \
  --output-dir ../../audits/raw/reset-2026-05-10/rg6/post-remediation-2026-05-24/live-required-benchmark \
  --mode scout \
  --no-reset-sandbox \
  --startup-timeout-seconds 45
```

Result: tool returned `BLOCKED: User denied. Do NOT retry.` No live required-suite benchmark artifacts were created from this command, and it was not retried.

No secret values were printed or saved in this log.
