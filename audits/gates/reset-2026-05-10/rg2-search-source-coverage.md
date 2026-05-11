# Reset Gate Review - RG2 Search Coverage And Source Collection

**Branch:** `audit/reset-rg2-search-source-coverage`
**Integration branch:** `rebuild/validated-leads-loop`
**Date:** 2026-05-11
**Decision:** `advance`
**Current product gate:** `red`

## Evidence Used

- `AGENTS.md`
- `STATUS.md`
- `docs/00-product-northstar.md`
- `docs/12-reset-gated-implementation-plan-2026-05-10.md`
- `docs/13-pipeline-orchestrator-contract-2026.md`
- `audits/zero-trust-codebase-audit-2026-05-10.md`
- `audits/raw/zero-trust-2026-05-10/evidence-ledger.md`
- `audits/raw/zero-trust-2026-05-10/operator-feedback-volume-2026-05-10.md`
- `audits/gates/reset-2026-05-10/rg1-benchmark-harness.md`
- `audits/raw/reset-2026-05-10/rg2/scout/quality-summary.json`
- `audits/raw/reset-2026-05-10/rg2/full/quality-summary.json`
- `audits/raw/reset-2026-05-10/rg2/source-snapshot-summary.json`
- `audits/raw/reset-2026-05-10/rg2/source-snapshots.jsonl`
- `audits/raw/reset-2026-05-10/rg2/evidence-notes.md`

## Commands Run

```bash
git status --short --branch
git fetch origin rebuild/validated-leads-loop
git switch rebuild/validated-leads-loop
git pull --ff-only origin rebuild/validated-leads-loop
git switch -c audit/reset-rg2-search-source-coverage
git rev-parse rebuild/validated-leads-loop origin/rebuild/validated-leads-loop HEAD
git merge-base --is-ancestor 5673540 rebuild/validated-leads-loop
git merge-base --is-ancestor ca700ae rebuild/validated-leads-loop
git merge-base --is-ancestor aad7d7d rebuild/validated-leads-loop
find audits/gates/reset-2026-05-10 -maxdepth 1 -type f -print | sort
git diff --check
cd packages/core && uv run pytest tests/test_query_planner.py tests/test_search.py tests/test_benchmark_suite.py -q
curl -sS -m 5 http://127.0.0.1:8000/health || true
cd apps/api && env -u OPENAI_API_KEY -u OPENAI_BASE_URL uv run uvicorn api.main:app --host 127.0.0.1 --port 8000
cd packages/core && env -u OPENAI_API_KEY -u OPENAI_BASE_URL WR_API_INTERNAL_TOKEN="$(awk -F= '/^WR_API_INTERNAL_TOKEN=/{print $2}' ../../apps/api/.env)" uv run python -m core.live_benchmark_runner --api-base-url http://127.0.0.1:8000 --output-dir ../../audits/raw/reset-2026-05-10/rg2/scout
cd packages/core && env -u OPENAI_API_KEY -u OPENAI_BASE_URL WR_API_INTERNAL_TOKEN="$(awk -F= '/^WR_API_INTERNAL_TOKEN=/{print $2}' ../../apps/api/.env)" uv run python -m core.live_benchmark_runner --api-base-url http://127.0.0.1:8000 --output-dir ../../audits/raw/reset-2026-05-10/rg2/full --mode full
cd packages/core && env -u OPENAI_API_KEY -u OPENAI_BASE_URL uv run python - <<'PY'
...
PY
jq '[.[] | {benchmark_id,returned_source_count,tavily_searches,vendor_query_count,max_vendor_query_length,vendor_queries_over_400,broad_query,named_accounts,target_source_hits}]' audits/raw/reset-2026-05-10/rg2/source-snapshot-summary.json
```

Raw command excerpts are saved in `audits/raw/reset-2026-05-10/rg2/commands/command-output.md`.

## Live Results

The required RG2 unit checks passed:

```text
18 passed in 0.27s
```

Scout live results:

| Case | HTTP | Categorized rows | High-trust usable | RG2 observation |
| --- | ---: | ---: | ---: | --- |
| `thomas-arizona-k12` | 200 | 8 | 0 | All 8 target accounts represented; 3 are `organization_only`. |
| `lee-commodity-buyers` | 200 | 2 | 0 | Final output still starves the operator. |
| `healthcare-it-phoenix` | 200 | 4 | 0 | Final output still starves the operator and includes a fake email finding. |
| `finance-cisos-new-york` | 503 | 0 | 0 | LLM parse/extraction failure; RG3 owns salvage. |
| `manufacturing-ops-detroit` | 503 | 0 | 0 | LLM parse/extraction failure; RG3 owns salvage. |
| `privacy-reject-homeowner-phones` | 422 | 0 | 0 | Blocked before search. |

Full live results:

| Case | HTTP | Categorized rows | High-trust usable | RG2 observation |
| --- | ---: | ---: | ---: | --- |
| `thomas-arizona-k12` | 200 | 9 | 0 | All 8 target accounts represented; 3 are `organization_only`. |
| `lee-commodity-buyers` | 200 | 4 | 0 | Final output still below the broad-query floor. |
| `healthcare-it-phoenix` | 200 | 3 | 0 | Final output still below the broad-query floor. |
| `finance-cisos-new-york` | 200 | 5 | 0 | Final output still below the broad-query floor. |
| `manufacturing-ops-detroit` | 503 | 0 | 0 | LLM parse/extraction failure; RG3 owns salvage. |
| `privacy-reject-homeowner-phones` | 422 | 0 | 0 | Blocked before search. |

Source snapshot results using the same benchmark prompts with `max_results=100`:

| Case | Deduped sources | Tavily searches | Vendor queries | Max query length | Query over 400 chars |
| --- | ---: | ---: | ---: | ---: | ---: |
| `thomas-arizona-k12` | 98 | 8 | 8 | 164 | 0 |
| `lee-commodity-buyers` | 90 | 6 | 6 | 57 | 0 |
| `healthcare-it-phoenix` | 75 | 6 | 6 | 55 | 0 |
| `finance-cisos-new-york` | 73 | 6 | 6 | 68 | 0 |
| `manufacturing-ops-detroit` | 90 | 6 | 6 | 49 | 0 |

For Thomas Arizona K-12, source snapshots found supporting source mentions for every named account: Mesa 17, Chandler 14, Peoria 14, Gilbert 20, Deer Valley 13, Paradise Valley 15, Dysart 17, and Maricopa 20.

## Screenshots And Artifacts

No browser screenshots were required because RG2 is non-UI review/report work.

Artifacts:

- Live Scout outputs: `audits/raw/reset-2026-05-10/rg2/scout/`
- Live Full outputs: `audits/raw/reset-2026-05-10/rg2/full/`
- Source snapshots: `audits/raw/reset-2026-05-10/rg2/source-snapshots.jsonl`
- Source snapshot summary: `audits/raw/reset-2026-05-10/rg2/source-snapshot-summary.json`
- Command output: `audits/raw/reset-2026-05-10/rg2/commands/command-output.md`
- Evidence notes: `audits/raw/reset-2026-05-10/rg2/evidence-notes.md`

## Value Prop Verdict

The current product does **not** give enough result volume, evidence, or export value for the operator loop.

Result volume is still not enough at the operator-facing output layer. Broad Scout returned 2, 4, 0, and 0 categorized rows for the non-privacy broad prompts. Broad Full returned 4, 3, 5, and 0. That is far below the 50-500+ northstar and below even the prior 10-row escape hatch.

Evidence is still not enough. Every non-privacy live benchmark produced 0 high-trust usable rows. Contacts are missing or failed, source support is inconsistent, and two Scout cases still return `openai_failed` instead of explicit failed/review rows.

Export value is not enough and remains unproven for the reset loop. RG2 did not change UI/export, and the May 10 export caveat still stands until RG5 proves sales-first CSV output with validation context.

RG2 advances anyway because this gate is specifically the search/source coverage gate. The search/source layer now supplies all named-account obligations and 73-90 deduped raw sources for broad prompts, which is enough raw material for RG3 to attempt inclusive extraction, validation, conflict handling, and tier semantics. The product remains red.

## Findings

1. RG2 was eligible for Prompt C: R04, R05, and R06 are merged into `rebuild/validated-leads-loop`; no RG2 gate report existed before this branch; RG2 had not already advanced.
2. Named-account coverage improved materially. Scout and Full both represented all 8 Thomas Arizona K-12 target accounts, and source snapshots found source hits for every account.
3. Vendor queries are bounded. The largest RG2 source-snapshot vendor query was 164 characters, and no query exceeded Tavily's 400-character limit.
4. Broad raw source collection is no longer artificially starved. The broad benchmark prompts returned 73-90 deduped sources each with six vendor searches.
5. R05 source artifacts are sufficient for replay/audit at the source layer: snapshots preserve source IDs, URLs, content hashes, matched vendor queries, and the query plan.
6. Final categorized output is still starved because the extraction/tiering path is not yet inclusive. This is the handoff to RG3, not evidence that RG2 source collection failed.
7. Adjacent/filler candidates are not promoted to CRM-ready rows, but they are also not yet explained with mature tier semantics. RG3 must make every non-ready row carry a grounded reason and downgrade parse failures into explicit failed/review rows.
8. The privacy guardrail remains intact in both Scout and Full with HTTP 422.

## What Worked

- All 8 Thomas target accounts appear in live output categories.
- The source layer has enough raw broad-query material to support high-volume tiering work.
- Source artifacts are saved under the required RG2 raw evidence path.
- The planner uses multiple bounded vendor queries and avoids the Tavily query-length failure mode.
- The R06 coverage writer prevents missing named accounts from silently disappearing.

## What Did Not Work

- The operator-facing product still returns low single-digit broad outputs.
- The product still returns 0 high-trust usable leads across live non-privacy benchmarks.
- Finance Scout and manufacturing Scout/Full still fail with `openai_failed` parse/extraction errors.
- Contact evidence is not ready: missing contacts dominate every non-privacy live run.
- Sales-first export value was not improved by RG2 and remains unproven.

## New Gaps Found

- The API product path does not expose `aggressive_breadth`; Full mode uses higher `max_results`, but Scout remains capped to low final row counts by extraction and `max_leads`.
- Source collection exists in core and in this audit's direct source snapshots, but the API benchmark responses do not expose source snapshots directly. Gate reports must continue saving raw source artifacts until persistence/UI tie-out lands.
- The source layer can surface job boards, LinkedIn snippets, company pages, and generic directories. RG3 must distinguish these as review/failed/org-only with grounded `primary_filter_reason` rather than letting the LLM decide silently.

## Recommended Scope Change For Next Gate

No expansion beyond RG3. Keep RG3 focused on validation, conflict, and gate semantics, with one hard addition from this audit: RG3 must prove that the 73-90 raw broad sources can become visibly categorized output without creating false confidence.

RG3 should not add UI/export polish. It should make these failures impossible to hide:

- parse failures become explicit failed/review rows, not HTTP 503s;
- broad raw source hits become categorized tiers instead of disappearing;
- no missing/unsupported contact row is labeled CRM-ready;
- every non-ready row has a grounded reason.

## Next Main Promotion Recommendation

Do not sync `main`. RG2 advancement is a source-coverage advancement only. The current product still lacks operator-facing result volume, high-trust usable evidence, and sales-first export proof.

## Next Prompt A Assignment

Advance RG2, mark RG3 `in_progress`, and mark `R07 - Inclusive extraction prompt and candidate parse salvage` as `ready`.

```text
You are Prompt A for White Rabbit reset feature R07.

Work in /Users/mschwar/Documents/white-rabbit on rebuild/validated-leads-loop only. Do not merge or target main.

First prove current state:
- read AGENTS.md
- read STATUS.md
- read docs/00-product-northstar.md
- read docs/12-reset-gated-implementation-plan-2026-05-10.md
- read docs/13-pipeline-orchestrator-contract-2026.md
- read audits/gates/reset-2026-05-10/rg2-search-source-coverage.md
- run git status --short --branch

Create or resume branch feat/reset-r07-inclusive-extraction from rebuild/validated-leads-loop.

Implement only R07 - Inclusive extraction prompt and candidate parse salvage.

Required scope:
- preserve the RG2 search/source planner and source snapshot behavior
- make one invalid LLM candidate degrade into an explicit failed/review-style row or recoverable error record instead of crashing the whole query
- make extraction more inclusive so plausible raw source hits can survive into downstream tiering without being presented as CRM-ready
- do not implement R08 tiering/conflict validation, R09 score semantics, UI work, export work, recipe/batch work, or main promotion
- keep false-confidence rules from docs/00-product-northstar.md intact

Required verification:
- cd packages/core && uv run pytest tests/test_source_validation.py tests/test_contact_status.py tests/test_scoring.py tests/test_orchestrator.py -q
- cd apps/api && WR_API_INTERNAL_TOKEN=test-internal-token uv run pytest tests -q
- git diff --check
- update STATUS.md and docs/12 with the R07 status and exact Prompt B handoff
- commit and push the feature branch

Do not merge. Do not unlock R08 until Prompt B QA passes and merges R07 into rebuild/validated-leads-loop. Do not sync main.
```
