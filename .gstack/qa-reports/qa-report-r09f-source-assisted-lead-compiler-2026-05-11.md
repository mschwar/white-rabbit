# QA Report - R09F Source-assisted lead compiler

**Date:** 2026-05-11
**Prompt:** Prompt B
**Branch QA'd:** `feat/reset-r09f-source-assisted-lead-compiler`
**Target branch:** `rebuild/validated-leads-loop`
**Decision:** pass

## State Proof

- `STATUS.md` and `docs/12-reset-gated-implementation-plan-2026-05-10.md` identified exactly one Prompt B target: `R09F - Source-assisted lead compiler`.
- `git status --short --branch` was clean at QA start on `feat/reset-r09f-source-assisted-lead-compiler`, tracking `origin/feat/reset-r09f-source-assisted-lead-compiler`.
- R09G-R09H, RG4, R10-R12, export, dogfood, and `main` promotion were blocked before this QA pass.

## Verification

- `git diff --check` passed.
- `git diff --cached --check` passed.
- `cd packages/core && uv run pytest tests/test_source_assisted_compiler.py tests/test_manual_oracle.py tests/test_k12_source_map.py -q` passed: `12 passed`.
- `cd packages/core && uv run pytest tests/test_source_validation.py -q` passed: `6 passed`.
- `cd packages/core && uv run pytest tests/test_contact_status.py -q` passed: `15 passed`.
- `cd apps/api && WR_API_INTERNAL_TOKEN=test-internal-token uv run pytest tests -q` passed: `45 passed`, with existing datetime deprecation warnings.

## API QA Blocker Fix

Prompt B initially reproduced the reported API verification blocker: `api.main` and the API pytest process appeared idle during import/startup. The root cause was eager API import work plus slow local dependency import paths, not an R09F compiler assertion failure.

Fixes made during QA:

- Lazy-load `core.orchestrator.scout` from API execution paths instead of importing the OpenAI-backed orchestrator at `api.main` import time.
- Move DB initialization to FastAPI lifespan and keep `get_db_session()` lazily initialized for direct test usage.
- Disable unused Pydantic plugin discovery and SQLAlchemy optional C-extension loading for deterministic API startup.
- Replace the direct PostgreSQL UUID dialect import with SQLAlchemy's generic `Uuid`, preserving UUID semantics while avoiding extra dialect import work at module load.

The API suite still takes a long time on this local `.venv` first-import path, but it now reaches and completes all assertions instead of remaining blocked.

## Replay Artifact Review

`audits/raw/reset-2026-05-10/r09f/source-assisted-compiler-replay.json` reports:

- `candidate_count`: 17
- `high_trust_usable`: 10
- `manual_lookup`: 7
- `passes`: true
- `structure_reproduced`: true

The replay keeps unsupported or missing contacts out of `high_trust_usable`, includes source IDs on every row, preserves field evidence for name/title/organization/email/source, avoids generic search source URLs, and exercises duplicate handling for source packs and seed rows.

## Scope Review

R09F remains a source-assisted compiler slice plus API QA-unblock support. No R09G workbook/export tier semantics, UI, persistence, dogfood, Prompt C, RG4, R10-R12, or `main` sync scope landed.

## Northstar Drift Check

R09F aligns with the source-backed April New Mexico research pattern: it turns accepted public sources, source packs, pasted search/chatbot output, and seed CSV rows into auditable candidate rows. It does not invent contacts, does not promote missing/unsupported contacts to READY/high-trust, and keeps manual lookup rows visibly distinct from immediately usable leads.

## Non-UI QA

R09F is non-UI. Browser screenshots are not required. The explicit non-UI verification is the targeted core pytest suite, source-validation/contact-status suites, replay artifact inspection, full API test suite, and scope/northstar review above.

## Result

R09F passes Prompt B QA. Merge only into `rebuild/validated-leads-loop`, mark `R09G - Research-workbook tiering and export semantics` ready, and keep R09H, RG4, R10-R12, export, dogfood, and `main` blocked.
