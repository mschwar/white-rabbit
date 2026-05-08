# Dimension 2: Test Coverage Gaps

**Auditor:** researcher subagent
**Date:** 2026-05-07
**Branch:** audit/hard-audit-2026-05-07
**Status:** Complete (read-only review)

---

## Executive verdict

The test suite is **integration-layer mock testing, not data quality verification**. 16 test files (~46 unique tests) — all use hand-crafted "Jane Smith" mock leads. Zero tests call the real `scout()` function. Zero tests assert lead name format. Zero tests reject `not_available@*` emails. The three production failures the audit was triggered by **could not have been caught by any existing test**.

Critically: the FRONTIER_AUDIT_PROMPT.md claim that "core has zero test files" is **factually wrong** — there are 3 test files in `packages/core/tests/`. But the *spirit* of the brief stands: those tests verify nothing about extraction quality.

---

## Inventory: what tests exist

| File | LOC | Real APIs? | Key fixtures | What it actually verifies |
|------|-----|-----------|--------------|---------------------------|
| packages/core/tests/test_models.py | 23 | No | `lead_data = {"name": "John Doe", ...}` | Lead model accepts hand-crafted dict; no validation of name/email format |
| packages/core/tests/test_orchestrator.py | 155 | No | `fake_search`, `FakeCompletions`, `fake_client` | scout() accepts injected deps; returns metrics; raises on missing keys; handles search failure |
| packages/core/tests/test_query_guardrails.py | 31 | No | Hard-coded queries (incl. "K-12 IT directors in Albuquerque") | Query evaluation logic only; no production query diversity |
| apps/api/tests/test_api.py | 641 | No | `fake_scout`, mock db session | Health check; scout endpoint params; full endpoint persistence; sandbox caps; recipe scoreboard |
| apps/web/src/app/__tests__/login.test.tsx | 12 | No | Static props | Login form renders |
| apps/web/src/app/__tests__/page.test.tsx | 10 | No | Static props | Protected page shell renders |
| apps/web/src/app/api/scout/route.test.ts | 125 | No | VI mocks `fetch`; "Jane Smith" responseBody | Route validates blank queries; proxies to backend; surfaces guardrail responses |
| apps/web/src/components/__tests__/recipes-library.test.tsx | 211 | No | VI mocks `/api/recipes`, `/api/recipes/*/runs`, `/api/recipes/*/scoreboard` | Renders recipe list; scoreboard metrics; Friday review CSV export |
| apps/web/src/components/__tests__/scout-workspace-error-handling.test.tsx | 44 | No | VI mocks fetch returning plain-text 500 | Shows plain-text errors without crashing |
| apps/web/src/components/__tests__/scout-workspace.test.tsx | 275 | No | VI mocks `fetch` with Jane Smith leads | Submits query; renders results; sorts; guardrail warnings; CSV export |
| apps/web/src/lib/__tests__/auth.test.ts | 30 | No | Test secret tokens | Token round-trip; external redirect rejection; public path detection |
| apps/web/src/lib/__tests__/full-export.test.ts | 54 | No | Jane Smith lead | CSV row formatting; filename generation |
| apps/web/src/lib/__tests__/password.test.ts | 8 | No | `matchesSharedPassword("scout-pass", ...)` | Password comparison |
| apps/web/src/lib/__tests__/recipe-review.test.ts | 85 | No | Two recipes with scoreboard data | Friday review CSV/Markdown formatting |
| apps/web/src/lib/__tests__/scout.test.ts | 62 | No | Alpha/Bravo/Charlie leads with score tuples | sortScoutLeads() with 5 modes |
| apps/web/e2e/home.spec.ts | 6 | No | Playwright `page.goto('/')` | Title contains "Create Next App" — **placeholder, never updated** |

**Totals:** 16 files, ~46 unique tests, **0 hit a real external API**.

---

## Severity table

| ID | Gap | Severity | Affected behavior | Effort (human / AI) |
|----|-----|----------|-------------------|---------------------|
| D2-01 | Zero tests call real `scout()` | P0 | Whole extraction pipeline | 1d / 30min |
| D2-02 | No name-format validation tests | P0 | Lead.name | 4h / 30min |
| D2-03 | No email-format validation tests | P0 | Lead.email | 4h / 30min |
| D2-04 | No tests for orchestrator error cases | P1 | Tavily timeout, OpenAI 429, malformed JSON | 1d / 1h |
| D2-05 | No test that email_status matches reality | P1 | Trust signal accuracy | 4h / 30min |
| D2-06 | No contract tests between orchestrator schema and UI | P1 | Silent breakage on field rename | 4h / 30min |
| D2-07 | Sandbox cap edge cases untested | P1 | Race conditions, exact-boundary | 4h / 45min |
| D2-08 | Recipe CRUD untested | P2 | Recipe persistence | 4h / 1h |
| D2-09 | Lead feedback CRUD untested | P2 | Feedback aggregation | 4h / 1h |
| D2-10 | Batch error handling untested | P2 | Partial-failure batches | 4h / 1h |
| D2-11 | 10 of 11 Next.js API routes untested | P2 | Route validation, auth, proxying | 1d / 2h |
| D2-12 | No middleware auth test | P2 | Auth bypass | 4h / 1h |
| D2-13 | Guardrail tests cover only 3 queries | P2 | Edge cases (XSS, SQL, multi-word locs) | 4h / 30min |

**Counts:** P0 ×3, P1 ×4, P2 ×6

---

## Findings

### D2-01: Zero tests call the real `scout()` function [P0]

**Evidence:**
- `packages/core/tests/test_orchestrator.py:8–60` — `test_scout_uses_injected_dependencies_and_returns_metrics()` injects `fake_search` and `FakeCompletions`. Real `scout()` never invoked with real keys.
- `apps/api/tests/test_api.py:52` — `monkeypatch.setattr("api.main.scout", fake_scout)`. The real orchestrator is bypassed at every API test.
- `packages/core/src/core/orchestrator.py:57–124` — `scout()` is the production function calling real Tavily + OpenAI. Zero direct callers in tests.

**Risk:** The three known production failures (VoIP bias, fake names, invalid emails) went undetected because no test ever called the real LLM pipeline. All tests use Lead objects that bypass extraction entirely.

**Test to add:**
```python
# packages/core/tests/test_orchestrator_integration.py
@pytest.mark.integration
@pytest.mark.skipif(not os.getenv("OPENAI_API_KEY"), reason="needs real keys")
async def test_scout_with_real_apis_healthcare_query():
    leads, metrics = await scout(
        "Healthcare IT security directors in Phoenix, Arizona",
        openai_key=os.environ["OPENAI_API_KEY"],
        tavily_key=os.environ["TAVILY_API_KEY"],
    )
    assert len(leads) > 0
    for lead in leads:
        assert " " in lead.name, f"Name '{lead.name}' looks like a title"
        assert not any(w in lead.name.lower()
                       for w in ["director", "manager", "officer", "vp", "chief"]), \
            f"Name '{lead.name}' is a title"
        if lead.email:
            assert "not_available" not in lead.email
            assert "@" in lead.email and "." in lead.email.split("@", 1)[1]
        assert "voip" not in lead.explanation.lower(), \
            "VoIP mentioned in non-VoIP query"
```

---

### D2-02: No tests validate Lead name format [P0]

**Evidence:**
- `packages/core/tests/test_models.py:3–22` — only test creates `Lead(name="John Doe", ...)` and asserts `lead.name == "John Doe"`. No negative case.
- `packages/core/src/core/models.py:8` — `name: str = Field(description="First and last name of the contact")`. Description-only; no validator.

**Risk:** LLM extracts "VP of Engineering" as a name; system accepts it; user sees fake data. This is the exact production failure that triggered the audit.

**Test to add:**
```python
def test_lead_name_must_be_first_and_last_name():
    Lead(name="Jane Smith", title="Director", organization="Org", ...)  # ok
    with pytest.raises(ValueError, match="must be first and last"):
        Lead(name="Director of Technology", ...)
    with pytest.raises(ValueError, match="must be first and last"):
        Lead(name="VP Engineering", ...)
    with pytest.raises(ValueError, match="must be first and last"):
        Lead(name="John", ...)
```

---

### D2-03: No tests validate email format or reject placeholder emails [P0]

**Evidence:**
- `email_patterns.py` defines `infer_email_patterns()` (line 91); grep across packages/ apps/ returns **0 import sites**.
- `apps/api/tests/test_api.py:25–50` uses `email="jane.smith@aps.edu"` — no test exercises `not_available@*` or any placeholder.

**Risk:** LLM extracts `not_available@valleywisehealth.com`. User emails it. Bounce. Trust shattered.

**Test to add:**
```python
def test_lead_email_must_be_valid_or_empty():
    Lead(email="john@example.com", ...)
    Lead(email="", ...)
    with pytest.raises(ValueError, match="placeholder"):
        Lead(email="not_available@company.com", ...)
    with pytest.raises(ValueError, match="format"):
        Lead(email="john@", ...)
```

---

### D2-04: No tests for orchestrator error branches [P1]

**Evidence:**
- `packages/core/tests/test_orchestrator.py:127–154` — only one error test (`test_scout_raises_on_tavily_failure`), tests a generic exception.
- Missing: Tavily zero-results, Tavily timeout (search.py:82–85 has timeout handling but untested), OpenAI rate-limit (no retry logic in orchestrator.py:105–106), OpenAI malformed JSON (defensive code in 108–111 untested), missing TAVILY_API_KEY (raises at search.py:56–58, untested).

**Risk:** Production failures cascade to users as opaque 503s.

**Tests to add:** zero-results, timeout, rate-limit, malformed JSON, missing key — see report body for code samples.

---

### D2-05: No tests verify email_status field accuracy [P1]

**Evidence:**
- `models.py:12–14` — `email_status: Literal["Found", "Deduced", "Missing"]`. No test verifies the LLM sets it correctly.
- All test fixtures hardcode `email_status="Found"` (e.g., `apps/api/tests/test_api.py:30`).

**Risk:** UI shows "Email: Found" when the email is actually deduced or fake. Trust signal becomes noise.

---

### D2-06: No contract tests between orchestrator output and UI render [P1]

**Evidence:**
- `models.py` defines 14 fields on Lead.
- `scout-workspace.test.tsx:81–83` asserts specific score percentages render but doesn't verify all fields are present or correctly typed at the contract boundary.

**Risk:** If orchestrator drops a field, every test still passes (mocks have it); UI silently breaks in production.

---

### D2-07: Sandbox cap edge cases untested [P1]

**Evidence:**
- `apps/api/tests/test_api.py:192–222` — only tests query cap. Row cap edge case (exactly remaining_rows = planned_rows) untested.
- `apps/api/api/main.py:154–177` — `_sandbox_reserve_query_or_429()` reserves query but doesn't decrement rows until line 228. Race condition between concurrent requests not tested.
- `reset_sandbox_state()` — no test verifies both counts (queries + rows) are cleared.

---

### D2-08: Recipe CRUD untested [P2]

**Evidence:**
- `apps/api/api/db.py:47–65` — `create_recipe()`. Not directly called in tests; only mocked.
- `db.py:118–125` — `get_recipes()`, `get_recipe_by_id()`. No test.

---

### D2-09: Lead feedback CRUD untested [P2]

**Evidence:**
- `db.py:107–116` — `add_lead_feedback()`. Zero tests.
- `apps/api/api/main.py:332–335` — `/leads/{lead_id}/feedback` endpoint. No test.
- `db.py:149–188` — `get_recipe_scoreboard()` aggregation tested only via mocked response.

---

### D2-10: Batch error handling untested [P2]

**Evidence:**
- `apps/api/tests/test_api.py:421–544` — `test_batch_endpoint_respects_caps()` mocks scout to return 1 lead. No test for cap-mid-batch.
- `apps/api/api/main.py:524–527` — truncates leads when cap hit; no test verifies `total_leads` is correct after truncation.
- No test that a single failed query doesn't abort the entire batch.

---

### D2-11: 10 of 11 Next.js API routes untested [P2]

**Evidence:** `apps/web/src/app/api/` contains 11 routes. Only `scout/route.ts` has a test. Untested: login, logout, full, batch, sandbox, recipes, recipes/[id]/runs, recipes/[id]/scoreboard, leads/[id]/feedback, runs/[id]/close.

---

### D2-12: No middleware auth integration test [P2]

**Evidence:**
- `apps/web/src/lib/__tests__/auth.test.ts` tests token primitives in isolation.
- No test that `middleware.ts` redirects unauthenticated requests to login or honors valid cookies.
- `apps/web/src/app/__tests__/page.test.tsx` renders the protected page in isolation; never tests gating.

---

### D2-13: Guardrail tests cover only 3 fixed queries [P2]

**Evidence:** `packages/core/tests/test_query_guardrails.py:4–31` covers exactly 3 queries (the K-12 one + two negatives). No multi-word locations, no XSS injection, no SQL-flavored input.

---

## Gap matrix: functions with zero direct test coverage

| Module | Function | File:line | Status |
|--------|----------|-----------|--------|
| orchestrator.py | `async def scout(...)` | 57–124 | Called only with injected fakes |
| search.py | `async def fetch_search_results(...)` | 48–87 | Never called; search_fn always injected |
| email_patterns.py | `def infer_email_patterns(...)` | 91–132 | Never called; not imported anywhere |
| cost.py | `def estimate_search_cost(...)` | 35–53 | Never called |
| api/db.py | `create_recipe`, `get_recipe_by_id`, `get_recipes`, `add_lead_feedback`, `get_recipe_scoreboard`, `create_batch_job`, `update_batch_run`, `get_batch_job` | 47–265 | Mocked or absent |
| api/main.py | `run_full`, `list_recipes`, `list_recipe_runs`, `recipe_scoreboard`, `submit_feedback`, `close_run` | 220–344 | No direct tests |
| web/api/* | login, logout, full, batch, sandbox, recipes, recipes/*/runs, recipes/*/scoreboard, leads/*/feedback, runs/*/close | — | 10 of 11 routes untested |

**Total untested public functions: ~32**

---

## Test plan: minimum tests to add (priority order)

### Phase 1 — P0 blockers (must add before any external user)

1. **`packages/core/tests/test_orchestrator_integration.py`** (new file)
   - `test_scout_with_real_apis_healthcare_query`
   - `test_scout_with_real_apis_finance_query`
   - `test_scout_with_real_apis_manufacturing_query`
   - Marker: `@pytest.mark.integration`; skip if no env keys.
   - Effort: 1h
2. **`packages/core/src/core/models.py`** + **`packages/core/tests/test_models.py`**
   - Add Pydantic validators for `name` (require space + word chars, reject role keywords) and `email` (valid format or empty, reject `not_available@*`).
   - Add unit tests for valid + invalid cases.
   - Effort: 1h

### Phase 2 — P1 fixes (before pilot)

3. Orchestrator error-branch tests (zero-results, timeout, 429, malformed JSON, missing keys). 1h.
4. `email_status` consistency test. 30min.
5. Schema contract test between orchestrator output and UI render. 30min.
6. Sandbox cap boundary + reset tests. 45min.

### Phase 3 — P2 coverage

7. Recipe CRUD round-trip tests. 1h.
8. Lead feedback CRUD + aggregation tests. 1h.
9. Batch truncation + partial-failure tests. 1h.
10. Per-route Next.js tests for the 10 untested routes (~15min each). 2.5h.
11. Middleware auth integration tests. 1h.
12. Guardrail edge-case tests. 30min.

**Total to reach P0-safe:** ~2h. **To reach P1-safe:** ~5h. **Comprehensive:** ~12h.

---

## Top-3 fixes (priority order)

1. **Add a real-API integration test that runs `scout()` on 3 diverse queries and asserts no VoIP leakage, real names, valid-or-empty emails.** This is the single biggest unit-of-leverage in the entire test gap.
2. **Add Pydantic validators on Lead.name and Lead.email.** Defense-in-depth for when prompts drift again.
3. **Add a contract test that the UI's expected lead shape matches the orchestrator's actual output.** Prevents silent UI breakage on schema changes.
