# RG2 Evidence Notes

## Gate Eligibility

- RG2 was the current gate in `docs/12-reset-gated-implementation-plan-2026-05-10.md`.
- RG2 was not already advanced; only RG0 and RG1 gate reports existed before this audit.
- R04, R05, and R06 were all ancestors of `rebuild/validated-leads-loop`.
- The audit branch was created from `rebuild/validated-leads-loop` at `b9bf2c6`.

## Required Evidence Files Read

- `AGENTS.md`
- `STATUS.md`
- `docs/00-product-northstar.md`
- `docs/12-reset-gated-implementation-plan-2026-05-10.md`
- `docs/13-pipeline-orchestrator-contract-2026.md`
- `audits/zero-trust-codebase-audit-2026-05-10.md`
- `audits/raw/zero-trust-2026-05-10/evidence-ledger.md`
- `audits/raw/zero-trust-2026-05-10/operator-feedback-volume-2026-05-10.md`
- `audits/gates/reset-2026-05-10/rg1-benchmark-harness.md`

## Live Evidence

Current live evidence was saved under:

- `audits/raw/reset-2026-05-10/rg2/scout/`
- `audits/raw/reset-2026-05-10/rg2/full/`
- `audits/raw/reset-2026-05-10/rg2/source-snapshots.jsonl`
- `audits/raw/reset-2026-05-10/rg2/source-snapshot-summary.json`

The live API startup required unsetting ambient shell `OPENAI_API_KEY` and `OPENAI_BASE_URL` so FastAPI used `apps/api/.env`. The failed ambient key was not written into repo artifacts.

## RG2 Criteria Notes

- Named-account coverage: met. Scout and Full both represented all 8 Thomas Arizona K-12 target accounts, and the source snapshot had source hits for every target account.
- Source collection: met. Source snapshots preserve query plans, vendor queries, source IDs, source URLs, matched vendor queries, and content hashes.
- Tavily query length: met. No vendor query exceeded 400 characters in the RG2 source snapshot summary.
- Broad raw source volume: met at the search/source layer. The four broad non-privacy prompts returned 73-90 deduped sources each with `max_results=100`.
- Final categorized result volume: not met in the current product path. Scout returned 2, 4, 0, and 0 rows for the broad non-privacy prompts; Full returned 4, 3, 5, and 0 rows.
- Evidence/usable lead value: not met. All non-privacy live runs produced 0 high-trust usable rows.
- Export value: not proven or valuable yet. RG2 did not touch UI/export, and the May 10 export caveat still stands until RG5.

## Interpretation

RG2 can advance as a search/source coverage gate because the planner/source layer now supplies enough raw source material for RG3 to attempt inclusive extraction and tiering. The product remains red: the current operator-facing loop still has low final row counts, weak evidence, no usable leads, and no sales-first export proof.
