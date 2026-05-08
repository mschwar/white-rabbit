# Dimension 4: Code Quality & Architectural Integrity

**Auditor:** code-reviewer subagent
**Date:** 2026-05-07
**Branch:** audit/hard-audit-2026-05-07
**Status:** Complete (read-only deep review)

---

## Executive verdict

The most substantive sub-audit. **14 findings**: 3 P0 (data loss / security / production breakage), 4 P1 (race conditions, missing retries, LLM trust violations, integrity gaps), 6 P2, 1 P3. Several findings independently corroborate earlier dimensions (sandbox_state migration missing → Dim 7; sandbox race → Dim 2 hypothesis; email_patterns dead → Dim 1, 5, 8). New findings include: `DATABASE_URL` silently ignored at runtime, session tokens never expire server-side, batch spend cap is post-bill (not pre-flight), and a length-mismatch early-return that defeats the timing-safe password compare.

---

## Severity table

| ID | Title | Severity | File:line | Category | Effort |
|----|-------|----------|-----------|----------|--------|
| D4-01 | `sandbox_state` table missing from all alembic migrations | P0 | apps/api/alembic/versions/ | Schema drift / fresh-deploy break | 15min AI |
| D4-02 | Session token `iat` decoded but never compared — tokens never expire | P0 | apps/web/src/lib/auth.ts:75–97 | Auth | 20min AI |
| D4-03 | `get_engine()` ignores `DATABASE_URL` env var; hardcoded localhost always used | P0 | apps/api/api/models.py:114–116 + main.py:47–50 | Wrong DB in any non-local env | 5min AI |
| D4-04 | Sandbox query counter non-atomic — concurrent requests bypass cap | P1 | apps/api/api/main.py:154–177, 196–201 | Race condition | 20min AI |
| D4-05 | Feedback label is free-form `str` — case mismatch silently breaks scoreboard | P1 | apps/api/api/main.py:82–83, db.py:172–174 | Data integrity | 10min AI |
| D4-06 | No retry on Tavily timeout / OpenAI rate limit — single transient = 503 | P1 | orchestrator.py:80–106, search.py:72–87 | Reliability | 30min AI |
| D4-07 | `gate_passed` set by LLM, never validated server-side against the 3 scores | P1 | orchestrator.py:30 + models.py:27–30 | LLM trust boundary | 30min AI |
| D4-08 | `email_patterns.py` is dead code — zero importers | P2 | packages/core/src/core/email_patterns.py | Dead code | 5min (delete) / 30min (wire) |
| D4-09 | `confidence` marked DEPRECATED but still required by schema + frontend | P2 | core/models.py:16–19, web/lib/scout.ts:64 | Type drift | 15min AI |
| D4-10 | `Lead.data` JSON duplicates 4 scalar columns with no reconciliation | P2 | apps/api/api/models.py:49–59, db.py:92–103 | JSON-without-schema | 30min AI |
| D4-11 | cost.py prices hardcoded; no test, no staleness check; `OPENAI_WEB_SEARCH_PRICE` is dead accumulation | P2 | packages/core/src/core/cost.py:4–13 | Observability | 20min AI |
| D4-12 | Batch spend cap checked AFTER API call — money already spent when cap fires | P2 | apps/api/api/main.py:447, 520–551 | Logic | 10min AI (preflight) |
| D4-13 | `get_recipe_scoreboard` runs N+1 queries (5 runs × 15 leads = 76 queries) | P3 | apps/api/api/db.py:161–174 | Performance | 20min AI |
| D4-14 | Password compare leaks length via early-return before timingSafeEqual | P2 | apps/web/src/lib/password.ts:3–11 | Auth (mild) | 10min AI |

**Counts:** P0 ×3, P1 ×4, P2 ×6, P3 ×1

---

## Findings

### D4-01: `sandbox_state` table missing from migrations [P0]

**Evidence:**
```python
# apps/api/api/models.py:101-111
class SandboxState(Base):
    __tablename__ = "sandbox_state"
    id = Column(Integer, primary_key=True)
    total_queries = Column(Integer, nullable=False, default=0)
    ...
```
Only two migration files exist: `a48a5caecfee` (recipe/run/lead/lead_feedback) and `129492e59179` (batch_job/batch_run). **Verified at audit time** by direct `ls`: no `sandbox_state` in either.

The dev environment works because `init_db()` calls `Base.metadata.create_all(_engine)` at startup (`main.py:50`), creating tables alembic doesn't know about.

**Bug behavior:** Fresh deploy with `alembic upgrade head` ⇒ no `sandbox_state` ⇒ every call to `/scout`, `/full`, `/batch`, `/sandbox`, `/sandbox/reset` crashes at `get_sandbox_state()` with `ProgrammingError: relation "sandbox_state" does not exist`.

**Fix:**
```bash
cd apps/api && uv run alembic revision --autogenerate -m "add sandbox_state table"
```
Review and commit. Then drop `Base.metadata.create_all(_engine)` from `init_db()` so alembic is the single source of truth.

---

### D4-02: Session token `iat` never compared to clock — tokens never expire server-side [P0]

**Evidence (`apps/web/src/lib/auth.ts:75–97`):**
```typescript
export async function verifySessionToken(token: string, secret: string): Promise<boolean> {
  ...
  const parsed = JSON.parse(decoder.decode(base64UrlDecode(payload))) as {
    v?: number;
    iat?: number;
  };
  if (parsed.v !== SESSION_VERSION || typeof parsed.iat !== 'number') {
    return false;
  }
  // iat value is never compared to Date.now() — no max-age check
  const key = await importSecret(secret);
  return crypto.subtle.verify('HMAC', key, signatureBytes.buffer, encoder.encode(payload));
}
```

Cookie has `maxAge: 60 * 60 * 24 * 7` (`login/route.ts:41`) — but a stolen/manually-injected cookie with a year-old `iat` remains cryptographically valid indefinitely.

**Fix:** Insert after `parsed.iat` type check:
```typescript
const MAX_AGE_MS = 7 * 24 * 60 * 60 * 1000;
if (Date.now() - parsed.iat > MAX_AGE_MS) {
  return false;
}
```

---

### D4-03: `get_engine()` ignores `DATABASE_URL` env var [P0]

**Evidence (`apps/api/api/models.py:114–116`):**
```python
def get_engine(database_url: str | None = None):
    url = database_url or "postgresql://<dev_user>:<dev_pw>@localhost:5432/white_rabbit"
    return create_engine(url)
```

**Caller (`apps/api/api/main.py:47–50`):**
```python
load_dotenv()
...
init_db()   # called with no argument — database_url=None — hardcoded fallback always used
```

`load_dotenv()` puts `DATABASE_URL` in `os.environ` but `get_engine()` never reads it. Only `alembic/env.py:67` reads it from the environment. **Production always connects to localhost** unless someone happens to be running Postgres on the same machine with the dev creds.

**Fix:**
```python
import os

def get_engine(database_url: str | None = None):
    url = (
        database_url
        or os.environ.get("DATABASE_URL")
        or "postgresql://<dev_user>:<dev_pw>@localhost:5432/white_rabbit"
    )
    return create_engine(url)
```

(Combined with D7-05's "fail-on-missing" approach, the localhost fallback should be removed entirely in non-dev modes.)

---

### D4-04: Sandbox query counter is non-atomic [P1]

**Evidence (`apps/api/api/main.py:154–177`):**
```python
def _sandbox_reserve_query_or_429(session, planned_rows: int) -> SandboxUsageOut:
    state = get_sandbox_state(session)
    remaining_queries = state.max_queries - state.total_queries
    ...
    state.total_queries += 1
    state.updated_at = datetime.utcnow()
    return _sandbox_usage_out(session)
```

Two concurrent requests both read `total_queries=N`, both pass the check, both commit `N+1`. Cap is bypassable by the number of concurrent requests.

**Fix:** Lock the row:
```python
state = (
    session.query(SandboxState)
    .filter(SandboxState.id == _SANDBOX_STATE_ID)
    .with_for_update()
    .first()
)
```

---

### D4-05: Feedback label is free-form `str` — case mismatch silently miscounts [P1]

**Evidence:**
```python
# apps/api/api/main.py:82–83
class FeedbackRequest(BaseModel):
    label: str  # usable, wrong_persona, bad_source, bad_contact, duplicate

# apps/api/api/db.py:172–174
if feedback.label == "usable":
    usable_lead_count += 1
```

No Pydantic enum, no DB CHECK constraint. `POST /leads/{id}/feedback {"label": "Usable"}` returns 200 OK; `usable_lead_count` doesn't change.

**Fix:**
```python
from typing import Literal
class FeedbackRequest(BaseModel):
    label: Literal["usable", "wrong_persona", "bad_source", "bad_contact", "duplicate"]
```

Add a DB CHECK constraint as belt-and-suspenders.

---

### D4-06: No retries on Tavily timeout / OpenAI rate limit [P1]

**Evidence (`packages/core/src/core/orchestrator.py:80–88`):**
```python
try:
    search_results = await search_fn(query, api_key=tavily_key, ...)
except Exception as exc:
    raise OrchestratorError(f"Tavily search failed: {exc}") from exc
```

Single transient failure ⇒ user sees a generic 503 (Dim 6 D6-04 echoes this).

**Fix:** Wrap Tavily and OpenAI calls in exponential backoff with ≤2 retries on `TimeoutException` and `RateLimitError` only (do not retry validation errors or 4xx).

---

### D4-07: `gate_passed` is LLM-controlled, never server-validated [P1]

**Evidence (`orchestrator.py:30` inside SYSTEM_PROMPT string):**
> "GATE LOGIC:\nSet gate_passed = True if fit, evidence, and contact scores are all >= 0.6."

`models.py:30` declares `gate_passed: bool` but no validator checks it against the three sub-scores. Pydantic enforces type but not the business rule.

**Risk:** A lead with `(0.2, 0.1, 0.3)` sub-scores can arrive with `gate_passed=True` and be persisted as passing.

**Fix:** After `leads_list = completion.choices[0].message.parsed`:
```python
GATE_THRESHOLD = 0.6
for lead in leads_list.leads:
    expected = all(s >= GATE_THRESHOLD for s in
                   [lead.fit_score, lead.evidence_score, lead.contact_score])
    if lead.gate_passed != expected:
        lead.gate_passed = expected
```

(Bonus: parameterize `GATE_THRESHOLD` via env or config so it isn't hardcoded twice.)

---

### D4-08: `email_patterns.py` is dead code [P2]

**Evidence:** Grep confirms zero importers anywhere in `packages/`, `apps/`, or tests. (Cross-confirmed in Dim 1 D1-06, Dim 5 D5-04, Dim 8 D8-04.)

**Fix:** Delete the file (recommended for now) or wire it into a `/runs/{run_id}/email-patterns` endpoint.

---

### D4-09: `confidence` field DEPRECATED but still required [P2]

**Evidence (`packages/core/src/core/models.py:16–19`):**
```python
confidence: float = Field(
    ge=0, le=1,
    description="DEPRECATED: Confidence score from 0.0 to 1.0 based on source strength. Use scores instead.",
)
```

No `default`, so the LLM is forced to set it for an undocumented field (SYSTEM_PROMPT never mentions `confidence`). Frontend type still requires it (`apps/web/src/lib/scout.ts:64`). Test fixtures all set it.

**Fix:** Either (a) remove the field entirely (correct cleanup) or (b) add `default=0.0` and document. (a) requires updating the export CSV column too.

---

### D4-10: `Lead.data` JSON duplicates scalar columns [P2]

**Evidence (`apps/api/api/models.py:49–59`):**
```python
class Lead(Base):
    data = Column(JSON, nullable=False)            # full lead dict, unschemaed
    fit_score = Column(Float, nullable=True)       # also in data["fit_score"]
    evidence_score = Column(Float, nullable=True)
    contact_score = Column(Float, nullable=True)
    gate_passed = Column(Boolean, nullable=True)
    rank = Column(Integer, nullable=True)
```

`db.py:92–103` writes both from the same source. If JSON is later patched directly or `model_dump()` output drifts, scalar columns silently diverge from `data` with no constraint.

**Fix:** Pick one source of truth. If JSON is authoritative, drop the scalar columns. If scalars are authoritative, exclude them from `data` at write time.

---

### D4-11: cost.py prices hardcoded without test or staleness check [P2]

**Evidence (`packages/core/src/core/cost.py:4–13`):**
```python
# Pricing as of 2026-05
OPENAI_GPT4O_MINI_INPUT_PRICE = 0.15
OPENAI_GPT4O_MINI_OUTPUT_PRICE = 0.60
TAVILY_SEARCH_PRICE = 0.01
OPENAI_WEB_SEARCH_PRICE = 0.01    # dead — openai_web_searches always 0 in orchestrator
```

`OPENAI_WEB_SEARCH_PRICE` is referenced in `calculate_cost()` but the corresponding `openai_web_searches` field on `RunMetrics` is always 0. No unit test covers the calculation. Prices will silently go stale.

**Fix:** Add a `test_calculate_cost_snapshot` in `packages/core/tests/test_cost.py` with frozen expected outputs. Remove the dead web-search accumulation or wire it to a real signal. Add a date-check that flags pricing > 12 months old.

---

### D4-12: Batch spend cap is post-bill, not pre-flight [P2]

**Evidence (`apps/api/api/main.py:447, 520–551`):**
```python
leads, metrics = await scout(...)               # Tavily + OpenAI billed here
cost = metrics.estimated_cost_usd
...
if total_cost + cost > job.cap_max_spend_usd:   # checked AFTER billing
    batch_run.status = "failed"
    ...
    break
```

Leads aren't saved, but the API cost is real. Batch with $1.00 cap and $0.95 accumulated triggers a final $0.08 spend that's discarded ⇒ user spent $1.03.

**Fix:** Use `estimate_search_cost()` (already in cost.py) to pre-flight the next call; skip if estimate would exceed remaining budget.

---

### D4-13: `get_recipe_scoreboard` runs N+1 queries [P3]

**Evidence (`apps/api/api/db.py:161–174`):**
```python
for run in runs:
    for lead in get_leads_for_run(session, run.id):
        feedback = session.query(LeadFeedback).filter(
            LeadFeedback.lead_id == lead.id
        ).first()
```

5 runs × 15 leads = 76 queries per scoreboard hit. Acceptable today, embarrassing at scale.

**Fix:** Single join across `recipe_run → lead → lead_feedback`.

---

### D4-14: Password compare leaks length via early return [P2]

**Evidence (`apps/web/src/lib/password.ts:3–11`):**
```typescript
export function matchesSharedPassword(candidate: string, expected: string): boolean {
  const candidateBuffer = Buffer.from(candidate);
  const expectedBuffer = Buffer.from(expected);

  if (candidateBuffer.length !== expectedBuffer.length) {
    return false;   // distinguishable from timingSafeEqual path
  }

  return timingSafeEqual(candidateBuffer, expectedBuffer);
}
```

The early return is measurably faster than the timingSafeEqual path. Network jitter dominates in practice but the timing-safe intent is defeated.

**Fix:**
```typescript
const maxLen = Math.max(candidate.length, expected.length);
const a = Buffer.alloc(maxLen);
const b = Buffer.alloc(maxLen);
Buffer.from(candidate).copy(a);
Buffer.from(expected).copy(b);
return timingSafeEqual(a, b) && candidate.length === expected.length;
```

---

## Architecture observations

1. **Two divergent schema-management paths.** `init_db()` calls `Base.metadata.create_all()` AND alembic exists for some tables. Today this isn't latent risk — it's a broken deploy path: alembic-only deploys lack `sandbox_state`.
2. **LLM owns a deterministic business rule.** `gate_passed` is LLM-set, not server-computed. The server could derive it in one line. The LLM is now in the trust boundary for a pure-arithmetic check.
3. **Sandbox cap semantics are inconsistent.** Query: pre-call, race-vulnerable. Row: pre-checked against `planned_rows`, not actual returned. Spend (batch): post-call, after billing. None are atomic guarantees.
4. **`/full` DB section has no error handler.** `scout()` is guarded but `create_recipe → create_recipe_run → save_leads` (`main.py:239–272`) is bare. A DB failure mid-write returns an unstructured 500 and leaves the run in partial state.
5. **Single shared password, no per-user attribution.** Sandbox cap is a shared counter. No audit trail.

---

## Specific Q&A from prompt

| Q | Answer |
|---|--------|
| Tavily/OpenAI retries? | None (D4-06) |
| Tavily zero-results? | Handled cleanly via `data.get("results", [])` ⇒ empty LeadList. **Verified clean.** |
| 0.6 gate threshold source / configurable? | Hardcoded prompt string (orchestrator.py:30); not configurable, not validated server-side (D4-07) |
| cost.py pricing sources / staleness? | Comment-only, no test (D4-11) |
| DB types / `Any` leaks? | `data`, `filters`, `source_mix`, `weights`, `api_cost_breakdown` are all unschemaed JSON. `Lead.data` duplicates 4 scalars (D4-10). |
| SQL injection? | None found. SQLAlchemy ORM throughout. **Verified clean.** |
| Auth bypass / cookie forgery? | HMAC-SHA256 prevents forgery. But `iat` ignored (D4-02) and password length leaks (D4-14). |
| Migrations vs. running code? | `sandbox_state` missing (D4-01). Other 6 tables match. |
| Type annotations? | `search_fn` and `openai_client: Any | None` untyped in orchestrator.py:66–67. `get_engine` / `get_session_maker` lack return annotations. |
| Dead code, TODOs? | `email_patterns.py` (D4-08); `OPENAI_WEB_SEARCH_PRICE` accumulation (D4-11); DEPRECATED confidence (D4-09). No TODO/FIXME in production code. |
| Route error handling consistency? | `/full` DB section unguarded (architecture obs #4); `/leads/{id}/feedback` no 404 path; `/batch` rolls back all writes on any unhandled exception in the giant outer `with get_db_session()`. |
| email_patterns imported? | No. (D4-08) |

---

## Verified clean

- SQL injection: clean across `db.py`, `main.py`.
- `search.py` `_clean_results` and Tavily zero-results handling.
- `query_guardrails.py` (no external calls, no injection surface).
- `orchestrator.py` `_format_filters` (output goes only to LLM context).
- `auth.ts` `normalizeNextPath` (correctly rejects `//` and external prefixes).
- Cookie security flags: `httpOnly`, `sameSite: 'lax'`, `secure` conditional on prod.
- Migration chain integrity (linear, no orphans for the tables it covers).

---

## Top-3 fixes (priority order)

1. **D4-01 — Generate the `sandbox_state` migration.** Unblocks fresh deploys today. 15 minutes.
2. **D4-03 — Make `get_engine()` read `DATABASE_URL`.** Five minutes that prevents catastrophic prod misconfiguration.
3. **D4-02 — Validate `iat` against `Date.now()` in `verifySessionToken`.** Twenty minutes that gives session tokens a server-side expiry.
