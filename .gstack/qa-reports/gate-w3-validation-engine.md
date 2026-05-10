# Gate Review - W3 Validation Engine

**Branch:** `rebuild/validated-leads-loop`
**Integration branch:** `rebuild/validated-leads-loop`
**Date:** 2026-05-10
**Prepared recommendation:** advance
**Orchestrator decision:** advance
**Orchestrator acceptance:** Codex orchestrator / 2026-05-10
**Current product gate:** red

## Features Included

| Feature | Status | Commit/PR | QA report |
| --- | --- | --- | --- |
| F07 Source validator | merged_to_rebuild_branch | `feat/f07-source-validator` | `.gstack/qa-reports/qa-report-f07-source-validator-rerun-2026-05-10.md` |
| F08 Contact status model | merged_to_rebuild_branch | `feat/f08-contact-status-model` | `.gstack/qa-reports/qa-report-f08-contact-status-model-2026-05-10.md` |
| F09 Ranking gate based on evidence | merged_to_rebuild_branch | `feat/f09-ranking-gate` | `.gstack/qa-reports/qa-report-f09-ranking-gate-2026-05-09.md` |

## Required Verification

| Check | Result | Evidence |
| --- | --- | --- |
| W3 required command | pass after test harness repair | Initial run failed because `tests/test_scoring.py` did not exist. Added focused scoring-gate tests, then `$env:OPENAI_API_KEY=''; cd packages/core && uv run pytest tests/test_source_validation.py tests/test_contact_status.py tests/test_scoring.py tests/test_orchestrator.py -q` -> 39 passed |
| Full core regression | pass | `$env:OPENAI_API_KEY=''; cd packages/core && uv run pytest -q` -> 83 passed, 5 skipped |
| Whitespace check | pass | `git diff --check` -> no whitespace errors |

## Northstar Assessment

- Query: No new query changes; W2 remains the query contract.
- Validated leads: Candidate rows now carry source/contact validation records.
- Field-level evidence: Source validation checks resolved URL, status/access failure, direct field support, checked timestamp, snippets, and notes.
- Ranking: Person leads pass only when score thresholds and field/contact/source validation agree.
- Export: Not part of W3; W4/W5 must make benchmark and export quality measurable.
- False-confidence risk: Reduced by deterministic checks for unsupported source/title/org/email evidence, inaccessible sources, fake/failed contacts, organization-only rows, not-found rows, and wrong-persona score failure.

## Decision Rationale

Advance to W4 accepted. The W3 gate criteria are met in deterministic tests:

- 200-supported, 200-unsupported, 403, 404, and 999-like source states are covered.
- Contact statuses include verified, deduced-with-evidence, missing, failed, and unsupported.
- Unsupported guessed contacts cannot gate-pass as found.
- Organization-only and not-found rows are not person leads.
- Evidence-backed gate tests now live in `packages/core/tests/test_scoring.py`.

The product remains red. This gate only unlocks benchmark and quality reporting work; it does not authorize UI/export work or Thomas/Lee dogfood.

## Next Pointer

Unlock F10 Golden Arizona K-12 VoIP benchmark harness on `feat/f10-arizona-k12-benchmark`.

## Follow-Ups

- F10 must remain offline by default and must not treat GPT workbook rows as ground truth.
- F11/F12 remain blocked until F10 merges and passes QA.
