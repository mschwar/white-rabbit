# QA Report - R05 Source Collection And Snapshot Store

**Feature:** R05 - Source collection and snapshot store
**Branch:** `feat/reset-r05-source-collection-store`
**Integration target:** `rebuild/validated-leads-loop`
**Decision:** pass
**UI-visible:** no

## State Provenance

- Read `AGENTS.md`, `STATUS.md`, `docs/00-product-northstar.md`, `docs/12-reset-gated-implementation-plan-2026-05-10.md`, `docs/03-decisions.md`, and `docs/13-pipeline-orchestrator-contract-2026.md`.
- `STATUS.md` and `docs/12-reset-gated-implementation-plan-2026-05-10.md` identified exactly one Prompt B target: `R05 - Source collection and snapshot store`.
- Pushed branch state identified `origin/feat/reset-r05-source-collection-store` at `dfc9c3c`; `git branch --all --contains feat/reset-r05-source-collection-store` showed only the local and origin R05 branches, not `rebuild/validated-leads-loop`.
- `git status --short --branch` before QA: `## feat/reset-r05-source-collection-store...origin/feat/reset-r05-source-collection-store`.

## Required Verification

```bash
git diff --check
```

Result: passed.

```bash
cd packages/core && uv run pytest tests/test_query_planner.py tests/test_search.py tests/test_benchmark_suite.py -q
```

Result: `18 passed in 0.53s`.

Inspected `packages/core/tests/fixtures/raw_source_collection_snapshot.json`. The fixture is valid `source_collection.v1` data with original query, query-plan payload, requested raw-result ceiling, search depth, vendor-search count, two deduped sources, stable source IDs, vendor-query provenance, matched vendor queries, and content SHA-256 hashes.

## Non-UI Verification

No browser QA or screenshots were required because R05 changes only core source snapshot construction, attachment, and optional persistence.

Code review verified:

- `fetch_search_results()` attaches a `SourceCollectionSnapshot` to `SearchResults.source_collection`.
- The optional `SourceSnapshotStore` interface can persist the exact snapshot without requiring a database or UI surface.
- Snapshot rows preserve rank, URL, title, content, vendor score, first vendor query, matched vendor queries, and content hashes.
- The canonical raw fixture is generated from the same snapshot builder in `tests/test_search.py`.
- The feature does not change extraction, scoring, tiering, evidence-gate thresholds, API routes, web UI, export behavior, or persistence migrations.

## Northstar Drift Check

R05 supports the northstar by preserving source evidence for replay and audit before downstream extraction and validation. It does not present unsupported candidates as CRM-ready, loosen `high_trust_usable`, invent contacts, add external self-serve/account/billing surfaces, expose API keys in the frontend, or add recipe/batch/operator-minute ceremony.

The product remains red. R05 is evidence plumbing only; RG2 still needs R06 plus Prompt C live evidence under the `$5` cap before any gate advancement.

## Scope Check

Diff review against `rebuild/validated-leads-loop` showed reset implementation changes only in:

- `packages/core/src/core/search.py`
- `packages/core/src/core/source_collection.py`
- `packages/core/tests/test_search.py`
- `packages/core/tests/fixtures/raw_source_collection_snapshot.json`
- reset handoff docs in `STATUS.md` and `docs/12-reset-gated-implementation-plan-2026-05-10.md`

No `apps/web`, API route, export, database migration, organization-only/not-found writer, inclusive extraction, tiering engine, validation conflict resolver, score-language reset, or downstream RG3 implementation was present.

## Result

R05 passes Prompt B QA. Merge only into `rebuild/validated-leads-loop`, mark R06 ready inside RG2, and do not unlock RG3.
