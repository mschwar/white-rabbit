# QA Report - R09G Research-Workbook Tiering And Export Semantics

**Date:** 2026-05-11
**Prompt:** Prompt B
**Branch QA'd:** `feat/reset-r09g-research-workbook-tiering`
**Target merge branch:** `rebuild/validated-leads-loop` only
**Decision:** pass

## State Proof

- Read `AGENTS.md`, `STATUS.md`, `docs/00-product-northstar.md`, `docs/12-reset-gated-implementation-plan-2026-05-10.md`, latest ADRs in `docs/03-decisions.md`, and `docs/13-pipeline-orchestrator-contract-2026.md`.
- `STATUS.md` and `docs/12-reset-gated-implementation-plan-2026-05-10.md` identify R09G as implemented pending Prompt B QA.
- `git ls-remote --heads origin 'refs/heads/feat/reset-r09g-research-workbook-tiering' 'refs/heads/rebuild/validated-leads-loop'` showed:
  - `feat/reset-r09g-research-workbook-tiering` at `55f9e29e6ce4c89752450b7b2a69c7f0adc46e77`
  - `rebuild/validated-leads-loop` at `04924e61ada1f057a0b1ec3bf1c9af6f709bbeb4`
- `git log --oneline origin/rebuild/validated-leads-loop..origin/feat/reset-r09g-research-workbook-tiering` showed the single feature commit `55f9e29 feat: add r09g research workbook semantics`.
- `git status --short --branch` after aligning local branch:
  - `## feat/reset-r09g-research-workbook-tiering...origin/feat/reset-r09g-research-workbook-tiering`

## Required Verification

```bash
git diff --check
```

Result: passed.

```bash
cd packages/core && uv run pytest tests/test_research_workbook.py tests/test_source_assisted_compiler.py tests/test_manual_oracle.py tests/test_k12_source_map.py -q
```

Result: `15 passed in 9.84s`.

```bash
cd packages/core && uv run pytest tests/test_source_validation.py tests/test_contact_status.py -q
```

Result: `21 passed in 65.61s`.

Replay artifact tie-out:

```bash
cd packages/core && uv run python - <<'PY'
import json
from pathlib import Path
from core.research_workbook import build_april_nm_research_workbook_replay
repo = Path.cwd().parents[1]
artifact = repo / "audits/raw/reset-2026-05-10/r09g/research-workbook-replay.json"
current = json.loads(artifact.read_text())
expected = build_april_nm_research_workbook_replay().to_payload()
print("artifact_matches_generated", current == expected)
print("row_count", current["row_count"])
print("tier_distribution", current["tier_distribution"])
print("passes", current["passes"])
PY
```

Result:

```text
artifact_matches_generated True
row_count 17
tier_distribution {'FAILED': 0, 'MANUAL_LOOKUP': 7, 'NOT_FOUND': 0, 'ORG_ONLY': 0, 'READY_WITH_CONTACT': 10, 'REVIEW': 0}
passes True
```

## Artifact Inspection

Inspected `audits/raw/reset-2026-05-10/r09g/research-workbook-replay.json`.

- `row_count`: `17`
- `READY_WITH_CONTACT`: `10`
- `MANUAL_LOOKUP`: `7`
- `downgraded_ready_rows`: `[]`
- `passes`: `true`
- Export headers include the sales-first and validation/audit/source columns required by the feature card.
- All 7 manual-lookup rows are non-CRM-ready, have `email_status=missing`, blank exported email, and a next action.
- All 10 ready rows are CRM-ready and have `email_status=verified_found`.
- No row is missing all source URL fields.
- The targeted test suite covers synthetic claimed-ready downgrade behavior when contact support is missing.

## Scope Check

Feature diff versus `origin/rebuild/validated-leads-loop`:

```text
M STATUS.md
A audits/raw/reset-2026-05-10/r09g/research-workbook-replay.json
M docs/12-reset-gated-implementation-plan-2026-05-10.md
A packages/core/src/core/research_workbook.py
A packages/core/tests/test_research_workbook.py
```

Confirmed no UI files, API endpoint files, persistence files, R09H proof packet, Prompt C audit, RG4/R10-R12 work, dogfood packet, or `main` sync scope landed in R09G.

## Northstar Drift Check

R09G aligns with `docs/00-product-northstar.md` by preserving the source-assisted research workbook path, keeping strict CRM-ready contact semantics, and retaining manual-lookup rows as useful non-ready work instead of flattening them into failures or ready rows. It does not add signup/accounts/billing/public self-serve surfaces, expose frontend API keys, or move recipe/batch/Friday review/operator UI surfaces forward while the product remains red.

## Result

R09G passes Prompt B QA. Merge only to `rebuild/validated-leads-loop`, mark R09H as the next same-gate ready feature, keep RG4/R10-R12/export/dogfood/main blocked, and do not run Prompt C until R09H has merged.
