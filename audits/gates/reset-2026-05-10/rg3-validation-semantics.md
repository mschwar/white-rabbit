# Reset Gate Review - RG3 Validation, Conflict, And Gate Semantics

**Branch:** `audit/reset-rg3-manual-oracle`
**Integration branch:** `rebuild/validated-leads-loop`
**Date:** 2026-05-11
**Decision:** hold
**Current product gate:** red

## Evidence Used

- Current reset docs: `AGENTS.md`, `STATUS.md`, `docs/00-product-northstar.md`, `docs/12-reset-gated-implementation-plan-2026-05-10.md`, `docs/13-pipeline-orchestrator-contract-2026.md`, and `docs/03-decisions.md`.
- `DESIGN.md` was read only as future RG4 visual direction. It is not evidence that the current data-quality gate passed.
- Baseline audit: `audits/zero-trust-codebase-audit-2026-05-10.md`.
- Current branch proof: `audit/reset-rg3-manual-oracle` at `a4dc4e9`, matching `origin/rebuild/validated-leads-loop`.
- Feature merge proof: every RG3 feature branch from R07 through R09H is an ancestor of `origin/rebuild/validated-leads-loop`.
- Current replay proof: `audits/raw/reset-2026-05-10/rg3/replay-r09h-reaudit/manual-oracle-proof-packet.json`.
- Current raw command and health evidence: `audits/raw/reset-2026-05-10/rg3/commands/`.
- Cited evidence notes: `audits/raw/reset-2026-05-10/rg3/evidence-notes-r09h-reaudit.md`.
- Prior complete live suite after R09A: `audits/raw/reset-2026-05-10/r09a/live-prompt-b/quality-summary.json`.
- Prior RG3 live hold baseline: `audits/raw/reset-2026-05-10/rg3/live/quality-summary.json`.

## Commands Run

```bash
git fetch origin --prune
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
git diff --check
cd packages/core && uv run pytest tests/test_manual_oracle_proof_packet.py tests/test_research_workbook.py tests/test_source_assisted_compiler.py tests/test_manual_oracle.py tests/test_k12_source_map.py -q
cd packages/core && uv run pytest tests/test_source_validation.py tests/test_contact_status.py -q
cd packages/core && uv run pytest tests/test_query_planner.py -q
cd packages/core && uv run pytest tests/test_search.py -q
cd packages/core && uv run pytest tests/test_coverage.py -q
cd packages/core && uv run pytest tests/test_scoring.py -q
cd packages/core && uv run pytest tests/test_live_benchmark_runner.py -q
cd packages/core && uv run pytest tests/test_quality_report.py -q
cd packages/core && uv run python -c "...write_r09h_proof_packet_artifacts(...)..."
cd apps/api && WR_API_INTERNAL_TOKEN=test-internal-token uv run pytest tests -q
cd apps/api && env -u OPENAI_BASE_URL -u OPENAI_API_KEY -u TAVILY_API_KEY uv run uvicorn api.main:app --host 127.0.0.1 --port 8016
curl --max-time 5 http://127.0.0.1:8016/health
```

Bounded verification note:

- Passing outputs are saved under `audits/raw/reset-2026-05-10/rg3/commands/`.
- The combined core suite, `tests/test_orchestrator.py` collection/import, and full API suite did not complete inside bounded runs. The API verbose run progressed through `test_scout_endpoint_returns_structured_error_on_orchestrator_failure` before timing out.
- The local API process reached `Waiting for application startup` but never reached startup completion during the audit window; `/health` returned HTTP `000` both before and after the additional startup wait.

## Live Results

No fresh RG3 live benchmark suite completed in this audit. The current API did not become healthy, so running `core.live_benchmark_runner` would not have produced a valid product run.

Current API startup evidence:

| Check | Result | Evidence |
| --- | --- | --- |
| Start API on `127.0.0.1:8016` with inherited `OPENAI_BASE_URL` cleared | Did not complete startup | `audits/raw/reset-2026-05-10/rg3/commands/api-server-r09h-reaudit.txt` |
| `/health` after initial wait | `000` | `audits/raw/reset-2026-05-10/rg3/commands/api-health-r09h-reaudit.txt` |
| `/health` after additional startup wait | `000` | `audits/raw/reset-2026-05-10/rg3/commands/api-health-after-startup-wait-r09h-reaudit.txt` |

Latest complete saved live suite after high-volume remediation, from R09A:

| Benchmark | HTTP | Categorized rows | Person rows | READY / high trust | Contact-quality passes | Review | Org-only | Not found | Failed | Volume status |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| Thomas Arizona K-12 | 200 | 12 | 3 | 0 | 0 | 3 | 3 | 2 | 4 | minimum_met |
| Lee commodity buyers | 200 | 50 | 2 | 0 | 0 | 2 | 2 | 0 | 46 | target_met |
| Healthcare IT Phoenix | 200 | 50 | 3 | 0 | 0 | 3 | 1 | 1 | 45 | target_met |
| Finance CISOs New York | 200 | 50 | 7 | 0 | 0 | 7 | 8 | 0 | 35 | target_met |
| Manufacturing ops Detroit | 200 | 50 | 1 | 0 | 0 | 1 | 1 | 2 | 46 | target_met |
| B2C private phone guardrail | 422 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | expected_privacy_refusal |

R09D-R09H did not include product API/UI/export integration work, so this audit cannot treat the source-assisted replay as a replacement for current live operator-loop evidence.

## Screenshots And Artifacts

No new screenshots were required because RG3 is a data-quality and semantics gate, not a UI implementation gate.

Raw artifacts:

- `audits/raw/reset-2026-05-10/rg3/evidence-notes-r09h-reaudit.md`
- `audits/raw/reset-2026-05-10/rg3/replay-r09h-reaudit/manual-oracle-proof-packet.json`
- `audits/raw/reset-2026-05-10/rg3/replay-r09h-reaudit/manual-oracle-proof-packet.md`
- `audits/raw/reset-2026-05-10/rg3/commands/`
- `audits/raw/reset-2026-05-10/r09a/live-prompt-b/quality-summary.json`

## Value Prop Verdict

The current product does **not** give enough result volume, evidence, and export value for the operator loop.

The source-assisted replay now gives a credible offline workbook proof for the April New Mexico school-district IT pattern: 17 rows, 10 `READY_WITH_CONTACT`, 7 `MANUAL_LOOKUP`, preserved source URLs, sales-first workbook headers, and zero unsupported CRM-ready rows. That is real progress against the near-term wedge.

But the gate cannot advance because the current live product loop is not proven. The API did not reach health during this audit, no fresh live benchmark suite completed, and the latest complete live suite still has zero high-trust usable rows plus zero contact-quality passes across evaluated cases. Export value is also only proven in replay/workbook semantics, not as a current query-to-export operator path.

## Findings

1. **Hold blocker - current live evidence is unavailable.** The reset plan requires current live evidence from RG2 onward. The API stayed at application startup and `/health` returned `000`, so RG3 cannot advance.
2. **Hold blocker - latest complete live suite still has zero CRM-ready value.** R09A's complete saved live suite has 0 high-trust usable rows and 0 contact-quality passes across evaluated cases.
3. **Pass - source-assisted manual-oracle replay works offline.** The R09H replay packet passes and reproduces the April New Mexico workbook structure: verified-contact rows, manual-lookup rows, source URLs, blocker/next-action semantics, sales-first export fields, and no unsupported CRM-ready contacts.
4. **Pass - broad saved live volume improved after R09A.** Lee, healthcare, finance, and manufacturing reached 50 categorized rows in the latest complete saved live suite. Thomas Arizona reached only 12 rows.
5. **Hold concern - runtime/import reliability is still not clean.** Bounded combined core/API runs timed out around orchestrator import or API startup paths. Focused non-orchestrator checks passed, but the current product path still cannot be treated as runtime-proven.
6. **No downstream unlock.** RG4, the refreshed `DESIGN.md` mockup/design preflight, R10-R12, export work, dogfood, and `main` promotion remain blocked unless a future Prompt C records `advance`.

## What Worked

- `git diff --check` passed before audit edits.
- Current git ancestry proves R07-R09H are merged into `origin/rebuild/validated-leads-loop`.
- Core replay suite passed: `18 passed`.
- Source validation/contact status suite passed: `21 passed`.
- Individual core query/search/coverage/scoring/live-runner/quality-report checks passed.
- R09H replay packet passed and regenerated under the current RG3 raw audit folder.

## What Did Not Work

- The local API did not reach health, so no fresh live benchmark suite could run.
- Combined core/API verification was not cleanly bounded; several broader runs timed out rather than producing a full pass/fail result.
- The source-assisted workbook path is still replay/artifact proof, not a live operator query-to-export path.
- Prior complete live evidence remains at zero high-trust/contact-quality output.

## New Gaps Found

- RG3 now has a split proof state: source-assisted replay is strong, but live runtime is not currently auditable.
- Before another RG3 advance attempt, the team needs a bounded live verification path that either starts the API reliably or records a structured startup/preflight failure without unbounded waits.
- The next value proof should connect the source-assisted compiler/workbook path to a live operator path or explicitly decide that RG3's next remediation is runtime/integration rather than more offline replay.

## Recommended Scope Change For Next Gate

Keep RG3 held. Do not start RG4 mockups, R10-R12 UI work, export polish, dogfood, or a `main` sync.

If Matt accepts this hold and wants another remediation, keep it inside RG3. The most valuable next scope is a narrow live integration/reliability slice that proves the source-assisted workbook path through an operator-runnable API or CLI flow, with bounded startup checks, saved live artifacts, and no relaxation of READY/high-trust contact rules.

## Next Main Promotion Recommendation

Do not sync `main`. The decision is `hold`, and `main` should not receive another operator-use promotion unless Matt explicitly asks after seeing this gate decision.

## Next Prompt A Assignment

None. Because the decision is `hold`, no downstream Prompt A feature and no RG4 design/mockup preflight is unlocked.

R10-R12 remain blocked. The refreshed mockup/design preflight from `DESIGN.md` also remains blocked until a future RG3 Prompt C records `advance`; if RG3 later advances, that preflight is the next assignment, not R10.
