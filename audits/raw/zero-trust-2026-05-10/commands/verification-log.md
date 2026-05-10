# Verification Log - Zero-Trust Audit 2026-05-10

## Git And Inventory

- Branch created: `audit/zero-trust-2026-05-10` from `rebuild/validated-leads-loop`.
- Initial status: clean at `bc1270d`.
- `git diff --check`: no whitespace errors at audit start.
- Source hotspot scan:
  - `apps/web/src/components/scout-workspace.tsx`: 1,234 LOC.
  - `apps/api/api/main.py`: 878 LOC.
  - `apps/web/src/components/__tests__/scout-workspace.test.tsx`: 651 LOC.
  - `apps/web/src/lib/scout.ts`: 493 LOC.
  - `packages/core/src/core/source_validation.py`: 416 LOC.
  - Total scanned code across `apps/web/src`, `apps/api/api`, and `packages/core/src`: 9,680 LOC.

## Mechanical Test Baseline

| Command | Result | Notes |
| --- | --- | --- |
| `cd packages/core && uv run pytest -q` | fail: 1 failed, 93 passed, 6 skipped | Shell `OPENAI_API_KEY` made `test_scout_raises_on_missing_openai_key` hit OpenAI instead of missing-key branch. |
| `cd packages/core && env -u OPENAI_API_KEY uv run pytest -q` | pass: 94 passed, 6 skipped | Confirms suite is environment-sensitive, not code-broken under isolated env. |
| `cd apps/api && uv run pytest tests -q` | fail: 22 failed, 21 passed | Protected API tests received 401 because token env/header did not line up in the process. |
| `cd apps/api && WR_API_INTERNAL_TOKEN=test-internal-token uv run pytest tests -q` | pass: 43 passed, 50 warnings | Correct token matches the test client's `x-white-rabbit-internal-token` value. |
| `cd apps/web && npm test -- --run` | pass: 13 files, 29 tests | Uses mocked search responses and fixtures. |
| `cd apps/web && npm run build` | pass | Next.js build warns about workspace-root inference and deprecated middleware convention. |

## Local Service Checks

| Check | Result |
| --- | --- |
| `GET http://localhost:8000/health` | `200 {"status":"ok"}` |
| `GET http://localhost:3000/login` | `200` |
| Direct tokenless `POST /scout` | `401` |
| Direct tokenless `POST /full` | `401` |
| Direct tokenless `POST /batch` | `401` |
| Direct tokenless `POST /sandbox/reset` | `401` |
| Direct `GET /health` | `200` |

## Live Benchmarks

Run through authenticated local Next API (`http://localhost:3000/api/scout`) with saved raw JSON under `audits/raw/zero-trust-2026-05-10/live/`.

| Prompt | HTTP | Rows | Usable | Noisy / Failed | Organization-Only | Not Found | Failed Query |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Thomas Arizona K-12 exact prompt | 200 | 3 | 0 | 3 | 0 | 0 | 0 |
| Lee commodity buyers prompt | 200 | 4 | 0 | 4 | 0 | 0 | 0 |
| Healthcare IT directors in Phoenix | 200 | 2 | 0 | 2 | 0 | 0 | 0 |
| Finance CISOs in New York | 200 | 4 | 0 | 4 | 0 | 0 | 0 |
| Manufacturing operations leaders in Detroit | 503 | 0 | 0 | 0 | 0 | 0 | 1 |
| B2C/private phone guardrail | 422 | 0 | 0 | 0 | 0 | 0 | blocked before search |

Additional Full-mode browser run:

- Query: `Healthcare IT directors in Phoenix`; location `Phoenix`.
- Result: 3 rows, 0 usable, 3 noisy/failed.
- CSV: `audits/raw/zero-trust-2026-05-10/live/full-export-healthcare.csv`.
- Persisted DB readback: 3 saved leads, 3 rows in CSV, all `gate_passed=false`.

## Browser Screenshots

| Screenshot | Notes |
| --- | --- |
| `desktop-login.png` | Login page renders. |
| `desktop-scout-initial.png` | `/scout` default screen shows query `Healthcare IT directors in Phoenix` with default location `New Mexico`. |
| `desktop-scout-healthcare-results-complete.png` | Scout result for healthcare/Phoenix produced 0 usable rows, 1 noisy/failed, 1 organization-only. |
| `desktop-evidence-drawer.png` | Evidence drawer exposes field validation but still anchors on a noisy CEO row, not an IT director. |
| `desktop-full-export-ready.png` | Full-mode export ready state; hidden behind Full mode on `/scout`, not primary single-search path. |
| `mobile-scout-initial.png` | Mobile first screen captured for layout review. |

## Gate Report Inventory

Found W1-W4 reports only:

- `.gstack/qa-reports/gate-w1-red-state-containment.md`
- `.gstack/qa-reports/gate-w2-search-contract.md`
- `.gstack/qa-reports/gate-w3-validation-engine.md`
- `.gstack/qa-reports/gate-w4-benchmarks-quality.md`

No W5 or W6 gate report exists even though F13-F19 are merged to `rebuild/validated-leads-loop`.
