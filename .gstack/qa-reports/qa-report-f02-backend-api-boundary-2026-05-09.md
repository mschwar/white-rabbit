# QA Report — F02 Backend API Boundary

> **Status:** Historical QA Record. This report is retained as evidence for the gate it evaluated, not as current instructions. Current product truth: `docs/00-product-northstar.md`; current state: `STATUS.md`; current reset execution: `docs/12-reset-gated-implementation-plan-2026-05-10.md`.


**Feature ID:** F02
**Feature name:** Backend API boundary
**Branch:** feat/f02-backend-api-boundary
**PR target:** rebuild/validated-leads-loop
**Date:** 2026-05-09
**Agent:** Codex
**Required verification type:** Browser + explicit non-UI
**Buildout plan:** docs/08-agentic-buildout-plan.md
**Northstar:** docs/00-product-northstar.md

## Scope Checked

- Feature card read from `docs/08-agentic-buildout-plan.md` (F02).
- Verifications executed for UI proxy path and direct API endpoint boundary behavior.
- Verified no `main` scope in this QA artifact.
- Merge target remains `rebuild/validated-leads-loop`.

## Browser Test Steps

**Route(s):**

- `/scout`

**Steps:**

1. Start `apps/web` locally with required env vars:
   - `WR_API_INTERNAL_TOKEN`
   - `WR_SHARED_PASSWORD`
   - `WR_SESSION_SECRET`
   - `WR_API_BASE_URL`
2. Open `/scout`, submit login password, and wait for authenticated UI.
3. Fill a basic Scout query and click search.
4. Capture the `/api/scout` call and resulting response.

**Expected result:**

- Successful proxying from Next.js API layer to backend when `WR_API_INTERNAL_TOKEN` is set, returning structured Scout response (or service-level API error if upstream dependency is unavailable).

**Actual result:**

- Proxy route reached; `/api/scout` was called with the internal token propagated.
- Backend response was `503` with body `{"error_code":"tavily_failed","message":"Tavily search failed: Tavily API error: 401 - ...","request_id":"52b5fb71-d054-4233-829c-355f1dfcc162"}` due missing/invalid Tavily key in local environment.
- This confirms end-to-end proxy path and internal-boundary forwarding behavior.

## Non-UI Verification Steps

**Command(s):**

```bash
uv run pytest tests/test_api.py -q  # in apps/api
npm test  # in apps/web
npm run build  # in apps/web
curl -i -X POST http://127.0.0.1:8000/scout
curl -i -X POST http://127.0.0.1:8000/full
curl -i -X POST http://127.0.0.1:8000/batch
curl -i -X POST http://127.0.0.1:8000/sandbox/reset
```

**Expected output:**

- Unit/integration tests pass.
- Protected API endpoints return unauthorized output when the internal token is missing.

**Actual output summary:**

- API tests and web tests/build passed (previously run in the QA session).
- `POST /scout`, `/full`, `/batch`, `/sandbox/reset` without token each returned:
  - HTTP status `401 Unauthorized`
  - body `{"detail":"Missing or invalid internal API token."}`

### API boundary 401 checks

```text
POST /scout        => 401 Unauthorized
POST /full         => 401 Unauthorized
POST /batch        => 401 Unauthorized
POST /sandbox/reset=> 401 Unauthorized
```

**Fixture/test file(s):**

- `apps/api/tests/test_api.py`

## Screenshots Required

| Required screenshot | Saved path | Pass/fail |
| --- | --- | --- |
| `/scout` successful proxy call (authenticated, token path exercised) | `.gstack/qa-reports/screenshots/f02-scout-proxy-success.png` | Pass |

## Tests Run

| Command | Result | Notes |
| --- | --- | --- |
| `docker compose up -d postgres` | Pass | Postgres available for API tests |
| `uv run alembic upgrade head` (apps/api) | Pass | Migrated schema successfully |
| `uv run pytest tests/test_api.py -q` (apps/api) | Pass | 33 tests passed |
| `npm test` (apps/web) | Pass | Frontend test suite passed |
| `npm run build` (apps/web) | Pass | Production build completed |
| Manual Playwright-style browser flow on `/scout` | Pass | Proxy call path confirmed via response capture |

## Northstar Reflection Result

| Question | Yes/No | Notes |
| --- | --- | --- |
| Does this directly improve natural-language query -> high-quality validated leads -> export? | Yes | It protects the run pipeline so only intended operator flows can trigger lead generation. |
| Does it reduce false confidence, bad contacts, wrong personas, or unsupported source claims? | Yes | It blocks unauthorized direct calls that could bypass boundary checks and create unsafe lead-generation behavior. |
| Does it avoid organizing or beautifying untrusted data? | Yes | Scope is auth boundary enforcement, not result formatting. |
| Does it keep main untouched and target only rebuild/validated-leads-loop? | Yes | QA scope stayed on feature branch and targeted rebuild branch only. |
| Is the feature independently mergeable? | Yes | Limited to boundary proxy/auth enforcement. |
| Can the next agent discover state from docs without chat context? | Yes | Updated `docs/08-agentic-buildout-plan.md` and `STATUS.md` with handoff details and report location. |
| Is there browser QA or explicit non-UI verification? | Yes | Both executed as requested. |
| Is the scope small enough for GPT-5.3 Spark or GPT-5.4 Mini? | Yes | Single cross-service auth boundary feature. |

## Findings

### Blocking

- None

### Non-Blocking

- Local environment returned `503 Tavily` for real `/api/scout` payload because upstream API key is not present in this run.

## Merge Decision

**Decision:** merge

**Reason:** Boundary tests pass and acceptance checks passed; only environmental limitation is expected upstream search-key dependency.

**Merged into:** rebuild/validated-leads-loop

## Follow-Up Issues

- None

## Handoff

```text
Feature: F02 Backend API Boundary
Branch: feat/f02-backend-api-boundary
Status: merged_to_rebuild_branch
What changed: Verified internal token boundary for scout/full/batch/reset (protected API + Next.js proxy forwarding)
Tests or QA run: Alembic upgrade, pytest, npm test/build, direct endpoint unauthorized checks, browser `/scout` proxy verification
Screenshots or report: .gstack/qa-reports/qa-report-f02-backend-api-boundary-2026-05-09.md
Northstar reflection: pass
Next pointer: F03
Open questions: None
``` 