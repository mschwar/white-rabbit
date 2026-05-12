# QA Report - R09D April NM evidence fixture and manual-oracle replay

- Date: 2026-05-11
- Branch: `feat/reset-r09d-april-nm-manual-oracle`
- Commit: `31a2b6518ec85babb20e2e73b933c30274fe13d2`
- Merge target: `rebuild/validated-leads-loop`

## Decision

Pass. R09D is QA-verified and ready to merge to `rebuild/validated-leads-loop` only.

## Checks

- `git diff --check 31a2b6518ec85babb20e2e73b933c30274fe13d2^ 31a2b6518ec85babb20e2e73b933c30274fe13d2` - clean
- `cd packages/core && uv run pytest tests/test_manual_oracle.py -q` - `5 passed in 1.14s`
- Northstar drift review - passed; the fixture/replay slice stays internal-first, red-gated, offline, and sanitized.
- Privacy/scope review - passed; stored fixture data and replay artifacts contain sanitized counts, notes, and paths only, with no private email bodies or unrelated product behavior changes.
- Scope review - passed; the feature commit range only touches `STATUS.md`, `docs/12-reset-gated-implementation-plan-2026-05-10.md`, `packages/core/src/core/manual_oracle.py`, `packages/core/tests/fixtures/april_nm_manual_oracle.json`, `packages/core/tests/test_manual_oracle.py`, and `audits/raw/reset-2026-05-10/r09d/manual-oracle-current-failure-replay.json`.

## Fixture Summary

- 17 total rows
- 10 verified-contact / `high_trust_usable` rows
- 7 `manual_lookup` rows
- `contact_status` values are `verified_found` and `missing`
- no unsupported READY contacts

## Result

Merge R09D into `rebuild/validated-leads-loop` only. Keep RG4, R10-R12, export, dogfood, and `main` blocked.
