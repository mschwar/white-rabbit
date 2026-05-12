# Reset Gate Review - RG3 Validation, Conflict, And Gate Semantics

**Branch:** `audit/reset-rg3-validation-semantics`
**Integration branch:** `rebuild/validated-leads-loop`
**Date:** 2026-05-12
**Decision:** advance
**Current product gate:** red

## Evidence Used

- Current control docs: `AGENTS.md`, `STATUS.md`, `docs/00-product-northstar.md`, `docs/12-reset-gated-implementation-plan-2026-05-10.md`, `docs/13-pipeline-orchestrator-contract-2026.md`, and `docs/03-decisions.md`.
- Baseline audit: `audits/zero-trust-codebase-audit-2026-05-10.md`.
- Current branch and merge proof: `audits/raw/reset-2026-05-10/rg3/post-r09l-source-assisted-proof/commands/`.
- R09J bounded-readiness evidence: `audits/raw/reset-2026-05-10/r09j/missing-config-probe/`.
- R09K timeout-containment evidence: `audits/raw/reset-2026-05-10/r09k/`.
- R09L source-assisted proof: `audits/raw/reset-2026-05-10/r09l/live-source-assisted-proof.json` and `.md`.
- Current live service-boundary response: `audits/raw/reset-2026-05-10/rg3/post-r09l-source-assisted-proof/source-assisted-proof-live-response.json`.
- Prior live autonomous Scout benchmark summary after R09A: `audits/raw/reset-2026-05-10/r09a/live-prompt-b/quality-summary.json`.

## Commands Run

```bash
git fetch origin --prune
git switch -c audit/reset-rg3-validation-semantics origin/rebuild/validated-leads-loop
git status --short --branch
git merge-base --is-ancestor origin/feat/reset-r07-inclusive-extraction origin/rebuild/validated-leads-loop
git merge-base --is-ancestor origin/feat/reset-r08-tier-validation-conflicts origin/rebuild/validated-leads-loop
git merge-base --is-ancestor origin/feat/reset-r09-tier-summary-semantics origin/rebuild/validated-leads-loop
git merge-base --is-ancestor origin/feat/reset-r09a-live-value-recovery origin/rebuild/validated-leads-loop
git merge-base --is-ancestor origin/feat/reset-r09b-contact-evidence-acquisition origin/rebuild/validated-leads-loop
git merge-base --is-ancestor origin/feat/reset-r09c-deep-multisource-evidence-tier-calibration origin/rebuild/validated-leads-loop
git merge-base --is-ancestor origin/feat/reset-r09d-april-nm-manual-oracle origin/rebuild/validated-leads-loop
git merge-base --is-ancestor origin/feat/reset-r09e-k12-source-map-roster-collector origin/rebuild/validated-leads-loop
git merge-base --is-ancestor origin/feat/reset-r09f-source-assisted-lead-compiler origin/rebuild/validated-leads-loop
git merge-base --is-ancestor origin/feat/reset-r09g-research-workbook-tiering origin/rebuild/validated-leads-loop
git merge-base --is-ancestor origin/feat/reset-r09h-manual-oracle-proof-packet origin/rebuild/validated-leads-loop
git merge-base --is-ancestor origin/feat/reset-r09i-api-startup-live-proof origin/rebuild/validated-leads-loop
git merge-base --is-ancestor origin/feat/reset-r09j-bounded-readiness-diagnostics origin/rebuild/validated-leads-loop
git merge-base --is-ancestor origin/feat/reset-r09k-live-runner-timeout-containment origin/rebuild/validated-leads-loop
git merge-base --is-ancestor origin/feat/reset-r09l-live-source-assisted-proof origin/rebuild/validated-leads-loop
git diff --check
cd packages/core && uv run pytest tests/test_source_validation.py tests/test_contact_status.py tests/test_scoring.py tests/test_orchestrator.py tests/test_live_benchmark_runner.py tests/test_quality_report.py tests/test_live_source_assisted_proof.py tests/test_manual_oracle_proof_packet.py tests/test_research_workbook.py tests/test_source_assisted_compiler.py tests/test_manual_oracle.py tests/test_k12_source_map.py -q
cd apps/api && WR_API_INTERNAL_TOKEN=test-internal-token uv run pytest tests -q
cd apps/api && WR_API_INTERNAL_TOKEN=test-internal-token uv run uvicorn api.main:app --host 127.0.0.1 --port 8027
curl --max-time 5 http://127.0.0.1:8027/health
curl --max-time 8 http://127.0.0.1:8027/readiness
curl --max-time 8 -X POST http://127.0.0.1:8027/source-assisted-proof
curl --max-time 8 -X POST -H "x-white-rabbit-internal-token: test-internal-token" http://127.0.0.1:8027/source-assisted-proof
jq ... audits/raw/reset-2026-05-10/rg3/post-r09l-source-assisted-proof/source-assisted-proof-live-response.json
```

Command outputs and extracted summaries are saved under `audits/raw/reset-2026-05-10/rg3/post-r09l-source-assisted-proof/commands/`.

## Live Results

R09J-R09L resolve the specific blockers from the post-R09I hold:

| Check | Result | Evidence |
| --- | --- | --- |
| RG3 feature merge proof | R07-R09L are all ancestors of `origin/rebuild/validated-leads-loop` | `commands/merge-proof.txt` |
| Gate state proof | RG3 was still `gate_hold`, not already advanced, before this audit | `commands/gate-state-proof.txt` |
| Core RG3 suite | `87 passed` | `commands/core-rg3-suite.txt` |
| API suite | `51 passed` with existing datetime warnings | `commands/api-suite.txt` |
| `/health` | HTTP 200 in `0.004302s` | `commands/api-health-8027.status` |
| `/readiness` | HTTP 200 in `0.469401s`; status `unavailable` because local env is not fully configured, but diagnostics are bounded and specific | `commands/api-readiness-8027-summary.json` |
| Tokenless `/source-assisted-proof` | HTTP 401 | `commands/source-assisted-proof-no-token.status` |
| Tokened `/source-assisted-proof` | HTTP 200 in `0.003648s`, `passes=true` | `source-assisted-proof-live-response.json` |

Current source-assisted live result:

| Metric | Value |
| --- | ---: |
| Source map reproduced | yes |
| Source-map districts | 7 |
| Source-map seeds | 13 |
| Generic search sources | 0 |
| Source-assisted candidates | 17 |
| Source-assisted sources | 18 |
| Workbook rows | 17 |
| `READY_WITH_CONTACT` rows | 10 |
| `MANUAL_LOOKUP` rows | 7 |
| Unsupported CRM-ready rows | 0 |
| Manual-lookup CRM-ready rows | 0 |
| Missing source rows | 0 |
| Missing next-action rows | 0 |
| Private contact values redacted | yes |

The prior autonomous Scout path is not treated as the launch wedge. The latest complete saved autonomous broad suite after R09A had improved broad volume in several cases, but still had `0` high-trust usable rows and `0` contact-quality cases. That remains a product caveat, not a reason to hold RG3 after ADR-019 pivoted the near-term value path to source-assisted research workbooks.

## Screenshots And Artifacts

No screenshots were required because RG3 is a non-UI data-quality/runtime gate. Raw artifacts:

- `audits/raw/reset-2026-05-10/rg3/post-r09l-source-assisted-proof/source-assisted-proof-live-response.json`
- `audits/raw/reset-2026-05-10/rg3/post-r09l-source-assisted-proof/commands/source-assisted-proof-live-summary.json`
- `audits/raw/reset-2026-05-10/rg3/post-r09l-source-assisted-proof/commands/source-assisted-proof-sampled-rows.json`
- `audits/raw/reset-2026-05-10/rg3/post-r09l-source-assisted-proof/commands/source-assisted-proof-manual-lookup-rows.json`
- `audits/raw/reset-2026-05-10/rg3/post-r09l-source-assisted-proof/evidence-notes.md`
- `audits/raw/reset-2026-05-10/r09j/missing-config-probe/`
- `audits/raw/reset-2026-05-10/r09k/`
- `audits/raw/reset-2026-05-10/r09l/live-source-assisted-proof.json`
- `audits/raw/reset-2026-05-10/r09l/live-source-assisted-proof.md`

## Value Prop Verdict

The current product now gives enough result volume, evidence, and export value to advance RG3 for the source-assisted operator loop.

Result volume is sufficient for the accepted April New Mexico source-assisted proof point: the live protected route returns 17 categorized workbook rows, including 10 `READY_WITH_CONTACT` rows and 7 `MANUAL_LOOKUP` rows.

Evidence is sufficient for RG3 because every row carries source URLs or explicit manual-lookup blockers, contact status is not silently guessed, unsupported contacts are not CRM-ready, and private contact values remain redacted in the repo artifact.

Export value is sufficient for RG3 because the workbook replay exposes sales-first export headers and preserves validation/audit context. It is not yet sufficient for operator dogfood because the production UI/export path still has to be implemented in RG4/RG5.

This verdict does not say the autonomous broad Scout path is commercially ready. It says the source-assisted value path is now proven enough to stop holding the validation/runtime gate and move to the next pre-implementation UI design step.

## Findings

1. **Advance - source-assisted live proof meets the accepted RG3 pivot.** The protected route reproduced the manual-oracle workbook structure through the API boundary with 17 rows, 10 ready rows, 7 manual-lookup rows, source URLs, blocker notes, and no unsupported CRM-ready rows.
2. **Advance - R09J fixed the audit-blocking readiness behavior.** `/readiness` returned a bounded diagnostic response during this audit; it did not hang the process.
3. **Advance - R09K fixed the unhandled timeout class.** Timeout-containment artifacts now record sandbox and product request failures as structured HTTP 599/summary evidence instead of unhandled runner tracebacks.
4. **Pass - missing or unsupported contact stays non-CRM-ready.** The sampled manual-lookup rows have `crm_ready=false`, `email_status=missing`, source URLs, blocker notes, and explicit next actions.
5. **Pass - protected API boundary holds.** Tokenless source-assisted proof returned 401; tokened request returned 200.
6. **Caveat - autonomous broad Scout still is not the near-term value path.** The latest complete saved broad suite still has zero high-trust/contact-quality cases. Do not market or design around autonomous broad search as if it were proven.
7. **Caveat - product remains red.** RG3 advancement unlocks only RG4 design/mockup preflight. It does not unlock production UI implementation, export, dogfood, or a `main` promotion.

## Next Main Promotion Recommendation

Do not sync `main`.

The gate advances on the integration audit branch for source-assisted validation/runtime readiness only. The product remains red, R10-R12 production UI is not approved, export/persistence is not complete, and Matt has not explicitly asked for another operator-use promotion.

## Next Prompt A Assignment

Per ADR-015, do not mark R10 ready yet. The next valid assignment is a refreshed RG4 mockup/design preflight from `DESIGN.md`.

```text
You are Prompt A for the White Rabbit reset queue.

Work in /Users/mschwar/Documents/white-rabbit. Use rebuild/validated-leads-loop as the integration branch. This is a refreshed RG4 mockup/design preflight, not production UI implementation. Do not edit production UI code. Do not merge or target main.

First prove current state:
- read AGENTS.md
- read STATUS.md
- read DESIGN.md
- read docs/00-product-northstar.md
- read docs/12-reset-gated-implementation-plan-2026-05-10.md
- read docs/13-pipeline-orchestrator-contract-2026.md
- read audits/gates/reset-2026-05-10/rg3-validation-semantics.md
- run git status --short --branch

Create a branch from rebuild/validated-leads-loop using codex/rg4-design-preflight-2026-05-12.

Produce refreshed RG4 mockup/design preflight artifacts under docs/mockups/rg4-design-preflight-2026-05-12/ for Empty, Loading, Results, Evidence Review, Low Signal, and Mobile Review.

Use DESIGN.md as the visual direction authority and docs/mockups/final-product-2026-05-10/index.html as the product-structure reference. Reconcile the preflight against the post-R09L source-assisted evidence: 17 source-assisted workbook rows, READY/REVIEW/manual-lookup semantics, evidence one action away, blocker/next-action notes, and sales-first export framing. Keep public/demo copy free of internal people, sprint IDs, gate IDs, and implementation machinery.

Required output:
- static mockup artifacts and rendered screenshots for all six states
- a short preflight report explaining how the mockups align with DESIGN.md, the product northstar, and the post-R09L source-assisted proof
- STATUS.md and docs/12 update with the handoff for Matt approval

Do not mark R10 ready. Do not start R10-R12 production UI implementation. Do not start export, persistence, dogfood, or main promotion.
```
