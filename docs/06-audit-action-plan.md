# 06 — Audit Action Plan

**Source:** `audits/hard-audit-2026-05-07.md`
**Created:** 2026-05-07
**Status:** Authoritative for what gets fixed next. Supersedes `04-roadmap.md` for any work that overlaps.

---

## How to read this

Each item lists: title, severity, source finding(s), effort (human-team / AI-assisted), owner placeholder, and a success criterion. Phase 1 items must complete before Phase 2 begins. Within a phase, items are ordered by dependency.

Effort estimates per the global CLAUDE.md compression table (boilerplate ~100×, feature ~30×, architecture ~5×). AI estimates assume Claude Code with the working tree visible.

---

## Phase 1 — Must-fix-now (blocks any further user testing)

Goal: After this phase, a fresh-deploy install of white-rabbit with valid env vars produces a working scout call against any vertical, with no VoIP bias and with names/emails extracted reliably.

### P1.1 — Strip VoIP bias from prompt and schema
**Severity:** P0 · **Findings:** D1-01, D1-02, F2-01 · **Effort:** 4h human / 30min AI · **Owner:** _____

Edit `packages/core/src/core/orchestrator.py:20–41` to replace the role assertion with a query-driven persona. Edit `packages/core/src/core/models.py:21,23` Field descriptions to drop "VoIP sales" / "VoIP upgrade." Add the lost proxy-lead instructions ("Include the organization name for every lead", "Set source_url to the strongest URL").

**Success criterion:** Re-run `audits/raw/run_scout_audit.py` against the same 4 queries; explanation-leak rate drops from 89% to <10%. Manufacturing CISO doesn't get pitched VoIP.

### P1.2 — Remove `OPENAI_BASE_URL` Ollama trap
**Severity:** P0 · **Findings:** F2-05 · **Effort:** 1h human / 10min AI · **Owner:** _____

Three sub-tasks: (a) Remove or comment out `OPENAI_BASE_URL=http://localhost:11434/v1` in `apps/api/.env`. (b) Add the env var to `.env.example` with a comment explaining the Ollama dev-mode use case. (c) Add a startup config preflight that logs the actual model + base URL on boot and refuses to start if `OPENAI_API_KEY` looks invalid (calls `client.models.retrieve(model)` once, like proxy-lead's `_verify_openai_model`).

**Success criterion:** Boot logs explicitly state "OpenAI: gpt-4o-mini @ https://api.openai.com/v1" (or the configured override). A misconfigured key fails at boot, not at first request.

### P1.3 — Add the missing `sandbox_state` migration
**Severity:** P0 · **Findings:** D4-01, D7-03 · **Effort:** 30min human / 15min AI · **Owner:** _____

`cd apps/api && uv run alembic revision --autogenerate -m "add sandbox_state table"`. Review the generated migration. Commit. Drop `Base.metadata.create_all(_engine)` from `init_db()` so alembic is the single source of truth.

**Success criterion:** Drop the dev DB, run `alembic upgrade head` from scratch, hit `/scout` — no `relation "sandbox_state" does not exist` error.

### P1.4 — Make `get_engine()` honor `DATABASE_URL`
**Severity:** P0 · **Findings:** D4-03 · **Effort:** 15min human / 5min AI · **Owner:** _____

Edit `apps/api/api/models.py:114–116` to read `os.environ.get("DATABASE_URL")` in the fallback chain. Remove the hardcoded production credential or guard it with a `WR_ENV != "production"` check.

**Success criterion:** Starting the API with `DATABASE_URL=postgresql://other-host/...` connects to that host, not localhost.

### P1.5 — Server-side session expiry
**Severity:** P0 · **Findings:** D4-02 · **Effort:** 30min human / 20min AI · **Owner:** _____

Edit `apps/web/src/lib/auth.ts:75–97` to compare `parsed.iat` against `Date.now()` with a `MAX_AGE_MS` constant matching the cookie's maxAge.

**Success criterion:** A token created with a year-old `iat` is rejected by `verifySessionToken()`; auth tests cover both paths.

### P1.6 — Real-API integration test
**Severity:** P0 · **Findings:** D2-01, D3-02 · **Effort:** 4h human / 1h AI · **Owner:** _____

Add `packages/core/tests/test_orchestrator_integration.py` that runs `scout()` against the four locked queries (the same set in `audits/raw/run_scout_audit.py`) and asserts: real names, valid-or-empty emails, no VoIP leakage in non-VoIP queries, gate consistency. Mark `@pytest.mark.integration` and skip if env keys missing.

**Success criterion:** Test passes after P1.1 lands. Test fails if anyone re-introduces VoIP bias. CI can opt in/out via `INTEGRATION_TESTS=1`.

### P1.7 — Pydantic validators on Lead.name and Lead.email
**Severity:** P0 · **Findings:** D1-03, D2-02, D2-03 · **Effort:** 1h human / 30min AI · **Owner:** _____

Add validators in `packages/core/src/core/models.py`:
- `name`: must contain a space; must not contain role tokens (director, manager, vp, chief, executive, coordinator, head of, lead, principal); must not be a single word.
- `email`: must be empty OR match a real email regex; must NOT match `not_available@*`, `noreply@*`, `placeholder@*`.
Add corresponding unit tests in `tests/test_models.py`.

**Success criterion:** Hand-crafted `Lead(name="Director of Technology", ...)` raises ValidationError. `Lead(email="not_available@x.com", ...)` raises. Real cases pass.

### P1.8 — Server-side `gate_passed` validation
**Severity:** P1 · **Findings:** D4-07, F2-04 · **Effort:** 30min human / 30min AI · **Owner:** _____

After parsing the LLM response in `orchestrator.py:109`, recompute `gate_passed = all(s >= GATE_THRESHOLD for s in [fit_score, evidence_score, contact_score])` and overwrite the LLM's value. Make `GATE_THRESHOLD` a module constant (currently lives only in the prompt string).

**Success criterion:** A test that injects a Lead with `(0.2, 0.1, 0.3)` sub-scores and `gate_passed=True` ends up with `gate_passed=False` after orchestrator processing.

### P1.9 — README setup verification
**Severity:** P1 · **Findings:** D7-04 · **Effort:** 1h human / 30min AI · **Owner:** _____

Update README setup section to a deterministic order: clone → cp .env.example .env → fill in keys → start Postgres → `uv run alembic upgrade head` → start API → start web. Test the sequence on a fresh checkout in a clean directory.

**Success criterion:** Following README from clone to logged-in scout query takes < 10 minutes for someone with the correct API keys.

### P1.10 — Decide and decide on email_patterns.py
**Severity:** P1 · **Findings:** D1-06, D4-08, D5-04 · **Effort:** 30min human (decide) / 30min AI (execute) · **Owner:** _____

Either delete `packages/core/src/core/email_patterns.py` (recommended now — defer wiring) or wire it into the post-extraction pipeline as a validation pass. Decide before P1.1 lands so the prompt instructions stay aligned.

**Success criterion:** Either grep for `email_patterns` returns 0 hits across the repo (deleted) OR returns at least one importer that calls `infer_email_patterns()` with extracted leads.

**Phase 1 total effort:** ~13 hours human / ~4 hours AI-assisted. Single dev with Claude Code can ship this in one focused day.

---

## Phase 2 — Before any external user (including pilot)

Goal: After this phase, a pilot user can run their own queries with reasonable confidence the data is real and the system is auditable.

### P2.1 — QA rubric document and tier-1 multi-vertical check
**Severity:** P0 · **Findings:** D3-02, D3-04 · **Effort:** 4h human / 1h AI

Write `docs/qa-rubric.md` with the 6-tier rubric from Dim 3. Update STATUS "Definition of done" to require passing tiers 1–4. Make tier-1 multi-vertical checks part of the gstack QA skill (or the sprint sign-off process).

### P2.2 — Restore proxy-lead's `_verify_openai_model` and config plumbing
**Severity:** P1 · **Findings:** F2-05, D5-01 · **Effort:** 4h human / 30min AI

Restore `OPENAI_MODEL` and `OPENAI_BASE_URL` env handling explicitly in orchestrator.py. Add a 30-line preflight that runs at FastAPI startup: connectivity-check Tavily, OpenAI, Postgres; fail-fast with structured error messages.

### P2.3 — Sandbox query counter atomicity
**Severity:** P1 · **Findings:** D4-04 · **Effort:** 1h human / 20min AI

Add `with_for_update()` to the SandboxState read in `_sandbox_reserve_query_or_429`. Add a concurrency test that fires 10 simultaneous requests and asserts the cap holds.

### P2.4 — Feedback label enum + DB constraint
**Severity:** P1 · **Findings:** D4-05 · **Effort:** 30min human / 10min AI

Replace `label: str` with `Literal["usable", "wrong_persona", "bad_source", "bad_contact", "duplicate"]` in `apps/api/api/main.py:82–83`. Add a DB CHECK constraint via alembic.

### P2.5 — Tavily/OpenAI retries
**Severity:** P1 · **Findings:** D4-06, D2-04 · **Effort:** 2h human / 30min AI

Wrap Tavily and OpenAI calls in exponential backoff (max 2 retries) for `TimeoutException` and `RateLimitError` only. Add unit tests that simulate one failure followed by success.

### P2.6 — Specific error codes in API responses
**Severity:** P1 · **Findings:** D6-04 · **Effort:** 1h human / 30min AI

Add `error_code` field to API error responses. UI maps codes to specific guidance.

### P2.7 — UI placeholder de-bias
**Severity:** P2 · **Findings:** D6-02, D6-01, D6-15 · **Effort:** 30min human / 15min AI

Replace the K-12 Albuquerque placeholder with a vertical-neutral example in scout-workspace.tsx (and recipe-name placeholder, and batch defaults). Update Scout description from "10–20 leads" to "up to 15 leads." Update lead-export description to list all CSV columns accurately.

### P2.8 — STATUS.md correction
**Severity:** P1 · **Findings:** D8-01 · **Effort:** 30min human / 10min AI

Move the persisted-lead-IDs and server-side guardrail items from "Known issues" to "What's done" with commit references. Add an "Audit reality" section linking to the master audit report. (Handled in this audit's Phase 3c — see commit history.)

### P2.9 — Hardening: empty-password module-load check
**Severity:** P3 · **Findings:** D7-05 (rebucketed) · **Effort:** 15min human / 5min AI

Move the empty-password check from per-request to module load so misconfiguration is detected at boot, not at first login.

**Phase 2 total effort:** ~14 hours human / ~3.5 hours AI-assisted. Two days of focused work.

---

## Phase 3 — Polish (can ship without)

### P3.1 — Cost ledger in Postgres (D5-06): 1–2h. Persistent record per scout/full/batch run.
### P3.2 — Search history endpoint (D5-05): 1h. `/searches` listing prior runs.
### P3.3 — CSV first/last name split (D5-08): 20min. Restore proxy-lead's split_full_name logic.
### P3.4 — Lead.data vs scalar columns reconciliation (D4-10): 30min. Pick a source of truth.
### P3.5 — `confidence` field cleanup (D4-09, D5-03): 15min. Either default it or remove it.
### P3.6 — DEPRECATED dead code: `email_patterns.py`, `OPENAI_WEB_SEARCH_PRICE` accumulation (D4-08, D4-11): 15min.
### P3.7 — N+1 query in scoreboard (D4-13): 20min. Single join.
### P3.8 — Password compare length-leak fix (D4-14): 10min. Pad before timingSafeEqual.
### P3.9 — `/full` route DB section error handling (Dim 4 obs #4): 30min. Wrap create_recipe → save_leads in try/except, return structured error.
### P3.10 — Tier-by-tier per-Next.js-route tests (D2-11): 2.5h. 15min × 10 routes.
### P3.11 — Middleware integration tests (D2-12): 1h.
### P3.12 — Guardrail edge cases (D2-13): 30min.
### P3.13 — TESTING.md per-language conventions (D8-03): 15min.
### P3.14 — Reconciliation report header (D8-02): 5min.
### P3.15 — ADR for vertical scope decision (D8-04): 1h.
### P3.16 — CI pipeline (D7-06): 1.5h.
### P3.17 — docker-compose web/api services (D7-07): 1h.
### P3.18 — FastAPI startup Postgres healthcheck (D7-08): 30min.
### P3.19 — Loading state stage labels (D6-12): 30min.
### P3.20 — Live batch progress (D6-06): 1h or fold into a streaming refactor.

**Phase 3 total effort:** ~13 hours human / ~3 hours AI. Spread over a sprint as bandwidth allows.

---

## Sprint reconciliation decision

The audit re-evaluated each "completed" sprint against working software, not feature presence:

| Sprint | Original status | Audit verdict | Rework needed |
|--------|----------------|---------------|---------------|
| Sprint 1 (Scaffold + scout) | Done | **NEEDS REWORK** — VoIP bias was inherited as a feature, not flagged as a regression; tests don't verify any extraction quality | Phase 1.1, P1.6, P1.7 are essentially Sprint 1's missing definition-of-done. |
| Sprint 2 (Persistence + recipes) | Done | **NEEDS REWORK** — `sandbox_state` table missing from migrations; `DATABASE_URL` ignored at runtime; Lead.data JSON duplicates scalar columns | P1.3, P1.4, P3.4 |
| Sprint 3 (Scoreboard + sort + Friday export) | Done | Mostly clean — N+1 query (P3.7) and minor copy issues (P2.7); core functionality verified | Phase 3 only |
| Sprint 4 (Batch + caps) | Done | **NEEDS REWORK** — sandbox query counter race (P2.3); spend cap is post-bill (P3-batch); feedback label not constrained (P2.4) | P2.3, P2.4 |

**Recommendation:** Don't roll back. Don't redo. Treat Phase 1 of this plan as Sprint 1.5 — the actual definition-of-done that Sprint 1 should have had. Pause new feature work until Phase 1 completes.

---

## Owner template

Each task above has a `_____` owner placeholder. Fill in based on team:
- For dev with Claude Code: most P0s are 5–30 minutes of AI-assisted work; one focused day per phase is realistic.
- For team review: P1.1 (prompt rewrite) and P1.7 (validators) deserve a second pair of eyes — the cost of getting prompt engineering wrong is another audit.

---

## Sign-off check

A check that the work is actually done — not just claimed:

- [ ] Phase 1 complete: re-run `audits/raw/run_scout_audit.py` shows leak rate <10%.
- [ ] Phase 1 complete: fresh DB → `alembic upgrade head` → `/scout` works without create_all fallback.
- [ ] Phase 1 complete: integration test passes; CI runs it.
- [ ] Phase 2 complete: QA rubric document exists and is referenced from STATUS.
- [ ] Phase 2 complete: at least one full QA pass executed against ≥3 verticals.
- [ ] Phase 3 items pulled into upcoming sprints with explicit owners.
