# Reset Gate Review - RG3 Validation, Conflict, And Gate Semantics

**Branch:** `audit/reset-rg3-validation-semantics`
**Integration branch:** `rebuild/validated-leads-loop`
**Date:** 2026-05-11
**Decision:** hold
**Current product gate:** red

## Evidence Used

- `AGENTS.md`, `STATUS.md`, `docs/00-product-northstar.md`, `docs/12-reset-gated-implementation-plan-2026-05-10.md`, `docs/13-pipeline-orchestrator-contract-2026.md`, and latest ADR-015 in `docs/03-decisions.md`.
- `DESIGN.md` was read only as future RG4 visual direction. It is not evidence that this data-quality gate passed.
- Baseline audit: `audits/zero-trust-codebase-audit-2026-05-10.md`.
- Current live benchmark output: `audits/raw/reset-2026-05-10/rg3/live/`.
- Current sampled row inspections: `audits/raw/reset-2026-05-10/rg3/person-row-sample.json`, `audits/raw/reset-2026-05-10/rg3/failed-row-sample.json`, and `audits/raw/reset-2026-05-10/rg3/live/manufacturing-inspection.json`.
- Command log: `audits/raw/reset-2026-05-10/rg3/commands/command-output.md`.

## Commands Run

```bash
git status --short --branch
cd packages/core && uv run pytest tests/test_source_validation.py tests/test_contact_status.py tests/test_scoring.py tests/test_orchestrator.py -q
cd apps/api && WR_API_INTERNAL_TOKEN=test-internal-token uv run pytest tests -q
cd apps/web && npm test -- --run
cd apps/web && npm run build
env -u OPENAI_API_KEY -u OPENAI_BASE_URL -u OPENAI_MODEL uv run uvicorn api.main:app --host 127.0.0.1 --port 8013
cd packages/core && env -u OPENAI_API_KEY -u OPENAI_BASE_URL -u OPENAI_MODEL WR_API_INTERNAL_TOKEN=[redacted] uv run python -m core.live_benchmark_runner --api-base-url http://127.0.0.1:8013 --output-dir ../../audits/raw/reset-2026-05-10/rg3/live --mode scout --api-token [redacted]
```

Notes:

- The first API startup attempt failed because inherited shell variables routed OpenAI auth through the old Ollama-style `OPENAI_API_KEY=ollama` trap. The successful live run explicitly unset inherited OpenAI variables so `apps/api/.env` was used.
- The Next.js build passed with existing warnings about workspace-root inference and the `middleware` convention deprecation.
- API tests passed with the existing datetime deprecation warnings.

## Live Results

| Benchmark | HTTP | Categorized rows | Person rows | READY / high trust | Review | Org-only | Not found | Failed | High-volume floor |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| Thomas Arizona K-12 | 200 | 9 | 2 | 0 | 2 | 3 | 0 | 4 | true |
| Lee commodity buyers | 200 | 7 | 1 | 0 | 1 | 1 | 0 | 5 | false |
| Healthcare IT Phoenix | 200 | 10 | 3 | 0 | 3 | 2 | 0 | 5 | true |
| Finance CISOs New York | 200 | 7 | 4 | 0 | 4 | 0 | 0 | 3 | false |
| Manufacturing ops Detroit | 200 | 8 | 2 | 0 | 2 | 1 | 2 | 3 | false |
| B2C private phone guardrail | 422 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | true |

The live runner passed only the privacy refusal case. The suite recorded five failed cases and these mismatches: Thomas source support, Lee volume, healthcare persona/contact/source, finance contact/volume, and manufacturing persona/contact/source/volume.

Manufacturing specifically no longer 503s. It returned HTTP 200 with 8 categorized rows and a tier distribution of 2 `review`, 1 `organization_only`, 2 `not_found`, 3 `failed`, and 0 `high_trust_usable`.

## Screenshots And Artifacts

No new screenshots were required because RG3 is a data-quality and semantics gate, not a UI implementation gate. Existing R09 Prompt B fixture screenshots remain at:

- `.gstack/qa-reports/screenshots/r09-prompt-b-desktop.png`
- `.gstack/qa-reports/screenshots/r09-prompt-b-mobile.png`

New raw audit artifacts:

- `audits/raw/reset-2026-05-10/rg3/live/quality-summary.json`
- `audits/raw/reset-2026-05-10/rg3/person-row-sample.json`
- `audits/raw/reset-2026-05-10/rg3/failed-row-sample.json`
- `audits/raw/reset-2026-05-10/rg3/live/manufacturing-inspection.json`
- `audits/raw/reset-2026-05-10/rg3/evidence-notes.md`

## Value Prop Verdict

The current product does **not** give enough result volume, evidence, or export value for the operator loop.

RG3 materially improves honesty: bad candidates degrade instead of crashing, contacts with missing or unsupported evidence do not appear CRM-ready, and non-actionable rows carry tier reasons. But the live product still gives Thomas/Lee too little sales value: broad prompts returned only 7-10 categorized rows, all six live benchmark cases produced 0 high-trust usable leads, and there is no current sales-first export proof in this gate. This is a better failure mode, not a useful operator loop.

## Findings

1. **Hold blocker - broad live output still misses the reset volume/value bar.** Lee, finance, and manufacturing all failed the high-volume floor in `quality-summary.json`. The broader reset target is 50-500+ categorized candidates where the market supports it, and this gate did not prove the market was smaller.
2. **Hold blocker - current live benchmark set produced 0 high-trust usable leads.** Every benchmark had `high_trust_usable_count: 0`; quality reports record `zero_usable_candidates` across the live suite.
3. **Pass - manufacturing parse crash is fixed.** The prior 503 failure mode now returns HTTP 200 with explicit `review`, `organization_only`, `not_found`, and `failed` rows.
4. **Pass - missing/unsupported contact is no longer CRM-ready.** The 12 sampled person rows all have `gate_passed=false`; rows with `email_status` `missing` or `unsupported` are `review` with primary reasons such as `contact is missing; row is not CRM-ready`.
5. **Pass with caution - blocked or inaccessible sources downgrade instead of validating.** Failed samples include LinkedIn `http_status=999` and website `403` cases marked `failed`, not usable. Some reason language is still rough and occasionally repeats stale narrative text, but the tier outcome is conservative.

## What Worked

- Required RG3 core/API checks passed: 48 core tests and 43 API tests.
- Web test/build checks passed: 30 Vitest tests and Next build.
- `tier_distribution` is present in live run metrics.
- Bad candidates are visible as explicit non-usable rows rather than disappearing or crashing the run.
- Contact semantics are materially safer than the May 10 baseline: no sampled row with missing or unsupported contact was labeled high trust or CRM-ready.

## What Did Not Work

- The live benchmark suite still fails the product-value bar with 0 high-trust usable rows.
- Broad live prompts are still low-volume after the high-volume path landed.
- Contact discovery remains too weak: live quality reports show `contact_quality_count: 0` across the benchmark set.
- Source/persona support remains uneven, especially healthcare and manufacturing.
- RG3 cannot honestly unlock RG4 because the next UI pass would be designing around a data loop that still starves the operator.

## New Gaps Found

- Live benchmark status naming may be too lenient: Thomas and healthcare show `high_volume_floor_met: true` at 9-10 rows, which conflicts with the reset plan's 50-500+ direction after high-volume mode lands. The quality summary should distinguish the old escape-velocity floor from the current broad-query target.
- Some failed rows preserve old prose that sounds like a lead exists while `name` and `title` are null. Failed-row copy should be normalized so the explanation cannot imply hidden usable contact detail.
- The runner currently writes `privacy-reject-homeowner-phones` quality failures for no candidates even though the guardrail behavior is correct. The gate report can interpret it, but the automated summary should treat expected privacy refusal separately.

## Recommended Scope Change For Next Gate

Do not start RG4 mockups yet. Add one narrow remediation slice inside RG3 or a new RG3a patch before design preflight:

- tighten live quality-summary floor semantics for broad prompts,
- improve contact discovery or deduced-with-pattern evidence enough to produce at least some high-trust usable rows in one required benchmark,
- normalize failed-row reason/explanation language,
- rerun the RG3 live suite and require at least: no parse crashes, no unsupported CRM-ready contacts, no broad prompt below the active floor unless market-size evidence is cited, and at least one benchmark with nonzero high-trust usable output.

## Next Main Promotion Recommendation

Do not sync `main`. The current `main` operator-use exception remains a Matt-directed internal-use line only. This audit records a hold, so there is no new operator-use promotion recommendation.

## Next Prompt A Assignment

None. Because the decision is `hold`, no downstream Prompt A feature and no RG4 design/mockup preflight is unlocked.

The next valid assignment should be a Matt-approved RG3 remediation prompt on `rebuild/validated-leads-loop`, scoped to live quality-summary semantics, contact/value recovery, and failed-row language. R10-R12 remain blocked, and the refreshed mockup/design preflight from `DESIGN.md` remains blocked until a future Prompt C records an RG3 `advance`.
