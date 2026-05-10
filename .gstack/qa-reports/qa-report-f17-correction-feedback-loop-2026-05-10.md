# QA Report - F17 Correction Feedback Loop

**Feature ID:** F17
**Feature name:** Thomas/Lee Correction Feedback Loop
**Branch:** feat/f17-corrections-feedback-loop
**PR target:** rebuild/validated-leads-loop
**Date:** 2026-05-10
**Agent:** Codex
**Required verification type:** Browser-testable
**Buildout plan:** docs/08-agentic-buildout-plan.md
**Northstar:** docs/00-product-northstar.md

## Scope Checked

- Feature card read: yes
- Files changed: `apps/api/api/models.py`, `apps/api/api/db.py`, `apps/api/api/main.py`, `apps/api/alembic/versions/6c9d2f10a9b1_allow_synthetic_correction_identifiers.py`, `apps/api/tests/test_api.py`, `apps/web/src/components/__tests__/scout-workspace.test.tsx`
- Explicit anti-goals reviewed: yes
- Confirmed `main` untouched: yes
- Confirmed PR/merge target is `rebuild/validated-leads-loop`: yes

## Browser Test Steps

**Route(s):**

- `/login?next=%2Fscout%3Fqa%3Dvalidation-buckets`
- `/scout?qa=validation-buckets`

**Steps:**

1. Log in with the shared workspace password.
2. Run the Full search on the validation-buckets fixture route.
3. Open the Jane Smith evidence drawer.
4. Submit a `corrected_field` correction for `title`.
5. Confirm the review queue export link appears and the download name is `white-rabbit-corrections-qa-validation-buckets-run.json`.

**Expected result:**

- The correction saves against the fixture row, the review queue fetch succeeds, and the export link becomes visible.

**Actual result:**

- Passed. The browser showed the correction drawer, saved the correction, and rendered the review queue export link. The visible browser text after save read `Saved corrected field correction for title. Loaded 3 corrections from the review queue.` because the synthetic validation run already had earlier smoke entries.

## Non-UI Verification Steps

**Command(s):**

```bash
cd apps/api && uv run pytest tests/test_api.py -q
cd apps/web && npm test -- --run src/components/__tests__/scout-workspace.test.tsx
curl -sS -i -X POST http://localhost:8000/leads/qa-usable-1/corrections \
  -H 'Content-Type: application/json' \
  -H 'x-white-rabbit-internal-token: test-internal-token' \
  -d '{"run_id":"qa-validation-buckets-run","query":"K-12 IT directors in Albuquerque","label":"corrected_field","field_name":"title","previous_value":"Director of Technology","corrected_value":"Director of IT","notes":"Title was updated after a better source was found."}'
curl -sS -i http://localhost:8000/runs/qa-validation-buckets-run/corrections \
  -H 'x-white-rabbit-internal-token: test-internal-token'
```

**Expected output:**

- API tests pass.
- Scout workspace component test passes.
- The correction POST returns `200 OK`.
- The review queue GET returns `200 OK` with the stored correction.

**Actual output summary:**

```text
40 passed in apps/api/tests/test_api.py
8 passed in apps/web/src/components/__tests__/scout-workspace.test.tsx
POST /leads/qa-usable-1/corrections -> 200 OK
GET /runs/qa-validation-buckets-run/corrections -> 200 OK
```

**Fixture/test file(s):**

- `apps/web/src/components/__tests__/scout-workspace.test.tsx`

## Screenshots Required

| Required screenshot | Saved path | Pass/fail |
| --- | --- | --- |
| Correction control | `.gstack/qa-reports/screenshots/f17-01-correction-drawer.png` | pass |
| Submitted state / review queue export | `.gstack/qa-reports/screenshots/f17-02-correction-queue-export.png` | pass |

## Tests Run

| Command | Result | Notes |
| --- | --- | --- |
| `cd apps/api && uv run pytest tests/test_api.py -q` | pass | 40 passed |
| `cd apps/web && npm test -- --run src/components/__tests__/scout-workspace.test.tsx` | pass | 8 passed |
| `curl -sS -i -X POST http://localhost:8000/leads/qa-usable-1/corrections ...` | pass | Stored correction against the synthetic fixture row |
| `curl -sS -i http://localhost:8000/runs/qa-validation-buckets-run/corrections ...` | pass | Review queue returned the stored correction |

## Northstar Reflection Result

| Question | Yes/No | Notes |
| --- | --- | --- |
| Does this directly improve natural-language query -> high-quality validated leads -> export? | Yes | Corrections feed the review queue and benchmark loop. |
| Does it reduce false confidence, bad contacts, wrong personas, or unsupported source claims? | Yes | Operators can mark bad rows and corrected fields. |
| Does it avoid organizing or beautifying untrusted data? | Yes | The feature records corrections and exports them for review. |
| Does it keep main untouched and target only rebuild/validated-leads-loop? | Yes | Branch targeted only the rebuild integration line. |
| Is the feature independently mergeable? | Yes | API, DB, and UI changes are scoped to the correction loop. |
| Can the next agent discover state from docs without chat context? | Yes | STATUS, the buildout plan, and this report capture the handoff. |
| Is there browser QA or explicit non-UI verification? | Yes | Both were run. |
| Is the scope small enough for GPT-5.3 Spark or GPT-5.4 Mini? | Yes | One focused feature slice. |

## Findings

### Blocking

- None.

### Non-Blocking

- The synthetic validation run already had prior smoke corrections, so the browser message reported 3 queued corrections instead of 1.

## Merge Decision

**Decision:** do not merge

**Reason:**

- This is the build prompt. The branch is pushed and documented, and the next prompt should review and merge it.

**Merged into:** not merged

## Follow-Up Issues

- None.

## Handoff

```text
Feature: F17 - Thomas/Lee Correction Feedback Loop
Branch: feat/f17-corrections-feedback-loop
Status: implemented_pending_qa
What changed: Correction records now accept synthetic fixture IDs and real UUID strings as text identifiers, so the validation-buckets browser route can save corrections and export the review queue.
Tests or QA run: api pytest, web component test, direct API curl checks, browser QA on /scout?qa=validation-buckets
Screenshots or report: .gstack/qa-reports/screenshots/f17-01-correction-drawer.png; .gstack/qa-reports/screenshots/f17-02-correction-queue-export.png; .gstack/qa-reports/qa-report-f17-correction-feedback-loop-2026-05-10.md
Northstar reflection: Pass
Next pointer: F17 is ready for merge review against rebuild/validated-leads-loop.
Open questions: None blocking
```
