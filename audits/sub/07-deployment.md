# Dimension 7: Environment & Deployment Readiness

**Auditor:** researcher subagent
**Date:** 2026-05-07
**Branch:** audit/hard-audit-2026-05-07
**Status:** Complete (read-only review with **manual correction below** — see Note on D7-01)

---

## ⚠️ Note on agent reliability

The original agent's lead finding (D7-01: ".env.example files don't exist") **is wrong**. Phase 0 of this audit verified directly that all three exist:
- `/Users/mschwar/Documents/white-rabbit/.env.example` (490 bytes, May 6)
- `/Users/mschwar/Documents/white-rabbit/apps/api/.env.example` (490 bytes, May 6)
- `/Users/mschwar/Documents/white-rabbit/apps/web/.env.example` (410 bytes, May 6)

The agent did not verify file existence before writing the finding. **D7-01 has been re-scoped below** to the real gap (whether the templates are *complete*, not whether they *exist*). The remaining findings appear to be evidence-backed and are retained.

---

## Executive verdict

The deployment story has gaps but isn't catastrophic. Real issues: a missing alembic migration for `sandbox_state`, a hardcoded localhost Postgres fallback, an empty-string fall-through in the login route that could be exploitable if `WR_SHARED_PASSWORD` is unset, and a missing CI pipeline. README is bootstrap-era and out of date.

---

## Required env vars (consolidated from code)

| Var | Used in | In .env.example? | Failure mode if missing |
|-----|---------|-----------------|-------------------------|
| `OPENAI_API_KEY` | `packages/core/src/core/orchestrator.py:74` | **Need to verify** — see D7-01-revised | `OrchestratorError` → 503 with generic message (Dim 6 D6-04) |
| `TAVILY_API_KEY` | `packages/core/src/core/search.py:56` | **Need to verify** | Search call raises early; 503 to user |
| `DATABASE_URL` | `apps/api/alembic/env.py:67` | **Need to verify** | Falls back to hardcoded `localhost:5432`; cryptic SQLAlchemy connection error if Postgres isn't local |
| `WR_SHARED_PASSWORD` | `apps/web/src/app/api/login/route.ts:19` | **Need to verify** | Defaults to empty string; if empty matches empty, anyone can log in (D7-05 below) |
| `WR_SESSION_SECRET` | `apps/web/src/app/api/login/route.ts:32` | **Need to verify** | Login handler throws `Error: Missing WR_SESSION_SECRET` |

(The "verify" cells should be filled in by reading the actual .env.example contents — left as a follow-up since the agent didn't do it cleanly.)

---

## Severity table

| ID | Issue | Severity | Effort |
|----|-------|----------|--------|
| D7-01-revised | `.env.example` completeness vs actual code env reads (verify all 5 vars are listed) | P1 | 30min |
| D7-02 | Hardcoded localhost Postgres fallback in `apps/api/api/models.py:115` | P1 | 15min |
| D7-03 | Missing alembic migration for `sandbox_state` table | P0 | 30min |
| D7-04 | README has no `alembic upgrade head` step | P1 | 30min |
| ~~D7-05~~ | ~~Empty-password fall-through~~ — **rejected; route has explicit guard** | ~~P0~~ → none | — |
| D7-06 | No CI/CD pipeline (`.github/workflows/` empty/missing) | P1 | 1.5h |
| D7-07 | `docker-compose.yml` only defines Postgres; no web/api services | P2 | 1h |
| D7-08 | No Postgres health check at FastAPI startup | P2 | 30min |

**Counts (after rejecting D7-05):** P0 ×1 (D7-03), P1 ×4, P2 ×2. **Two agent errors caught and corrected** (D7-01, D7-05).

---

## Findings

### D7-01-revised: Verify `.env.example` contents are complete [P1]

**Original agent claim (incorrect):** ".env.example files do not exist."

**Reality (verified Phase 0):** All three template files exist. They were created in the May 6 commit window.

**Real risk:** Whether each template lists every variable the code reads at runtime. Code reads ≥5 vars (table above); the templates may be partial. **Action:** Manually diff template contents against grepped `os.environ` / `process.env` calls. (To be completed during Phase 2 setup verification.)

**Fix:** Ensure each template lists all required vars with sensible-but-non-secret examples. Add comments explaining failure modes.

---

### D7-02: Hardcoded localhost Postgres fallback [P1]

**Evidence (`apps/api/api/models.py:115`):**
```python
url = database_url or "postgresql://white_rabbit:white_rabbit_dev@localhost:5432/white_rabbit"
```

**Impact:** If `DATABASE_URL` is unset, the API silently tries to connect to a local Postgres with hardcoded creds. In any non-local environment, this fails with a SQLAlchemy connection error, not a "DATABASE_URL not configured" message. Worse, the hardcoded password lives in source.

**Fix:**
```python
url = database_url
if not url:
    raise RuntimeError(
        "DATABASE_URL is required. Set it in your environment or .env.local."
    )
```

---

### D7-03: Missing alembic migration for `sandbox_state` table [P0]

**Evidence:**
- `apps/api/api/models.py` defines `SandboxState` (referenced in main.py `_sandbox_reserve_query_or_429`).
- `apps/api/alembic/versions/` contains exactly two files:
  - `a48a5caecfee_create_recipe_recipe_run_lead_lead_.py`
  - `129492e59179_add_batch_job_and_batch_run_tables.py`

No migration creates `sandbox_state`. A fresh deploy with `alembic upgrade head` will not have this table.

**Impact:** First Scout call after fresh deploy → `relation "sandbox_state" does not exist`. P0 because fresh deploy is broken.

**Fix:** Generate a migration: `alembic revision --autogenerate -m "add sandbox_state"`, review, commit, run.

---

### D7-04: README has no alembic step [P1]

**Evidence:** README is 32 lines, dated May 5. Reads like bootstrap copy. Does not mention `alembic upgrade head`, the new migrations directory, or the local Postgres setup beyond the docker-compose fragment.

**Fix:** Update README setup section to a deterministic order: clone → cp .env.example .env → fill in keys → `docker-compose up -d` for Postgres → `cd apps/api && uv run alembic upgrade head` → `uv run uvicorn` → `cd apps/web && npm install && npm run dev`. Test the sequence on a fresh checkout.

---

### D7-05: Empty-string password fall-through — **REJECTED on verification**

**Original agent claim (incorrect):** if `WR_SHARED_PASSWORD` is unset, an empty password would pass timing-safe comparison and grant access.

**Reality (verified — `apps/web/src/app/api/login/route.ts:21–23`):**
```typescript
const expectedPassword = process.env.WR_SHARED_PASSWORD ?? '';

if (!expectedPassword) {
  return NextResponse.json({ error: 'Shared password is not configured.' }, { status: 500 });
}
```

The route explicitly rejects empty/missing `WR_SHARED_PASSWORD` with a 500 *before* reaching the password comparison. The vulnerability the agent claimed does not exist.

**Caveat retained:** It would still be cleaner to fail at module load rather than per-request (so a misconfigured deployment is detected at boot, not on first login attempt), but this is a P3 polish item, not a P0 security hole. The agent's "fix" suggestion (throw at module load) is reasonable as a P3 improvement.

**Severity rebucketed:** ~~P0~~ → P3 (or omit). Treat the original D7-05 as a wrong finding. This is the second agent error caught (after D7-01).

---

### D7-06: No CI pipeline [P1]

**Evidence:** No `.github/workflows/` directory. No vercel.json, fly.toml, railway.toml. No deploy automation.

**Impact:** No automated test gating before merge. No automated migration run on deploy. No environment lint. STATUS.md decisions about "what's done" rely on manual local runs.

**Fix:** Add a minimal GH Actions workflow that runs `pytest` (api + core) and `npm test` on every PR. Defer deploy automation until a target environment is chosen.

---

### D7-07: `docker-compose.yml` only defines Postgres [P2]

**Evidence:** `docker-compose.yml` is 12 lines and defines only `postgres`. Web and api services are not containerized.

**Impact:** Setup is half-Dockerized. New developers need to run npm + uv locally even though Docker is "the path." Mixed setups invite "works on my machine."

**Fix:** Either (a) add web + api services (preferred), or (b) rename to `docker-compose.dev.yml` and document it as "Postgres only — run web/api locally."

---

### D7-08: No Postgres health check at FastAPI startup [P2]

**Evidence (`apps/api/api/main.py:50`):** `init_db()` is called without exception wrapping; if Postgres is unavailable, the app starts but the first request fails after a connection-timeout.

**Fix:** Wrap `init_db()` in a try/except; on connection failure, log a clear `"Postgres unreachable at <url>"` message and exit non-zero. Or implement a `/health/db` endpoint that's checked at startup by the deployment runner.

---

## "Setup from scratch" walkthrough (corrected)

Numbered as a fresh dev would experience it, after the fixes above land:

1. `git clone …` ✓
2. `cd white-rabbit` ✓
3. `cp .env.example .env` ✓ — files DO exist
4. Fill in `.env` (keys, password, session secret, db url) ✓
5. `docker-compose up -d` — currently only starts Postgres ⚠️
6. `cd apps/api && uv sync && uv run alembic upgrade head` ⚠️ **Fails today** — sandbox_state migration missing (D7-03)
7. `uv run uvicorn api.main:app --reload` ⚠️ Will start but first request crashes from D7-03
8. `cd apps/web && npm install && npm run dev` ⚠️ Will start; if WR_SHARED_PASSWORD unset, anyone can log in (D7-05)

After the listed fixes: ~10 minutes from clone to working app.

---

## Production-readiness checklist

- [x] `.env.example` files exist
- [ ] Every code env-read is documented in `.env.example` (verify)
- [ ] Code refuses to start with empty/missing critical secrets (D7-05)
- [ ] All DB tables have migrations (D7-03)
- [ ] README setup steps are tested fresh (D7-04)
- [x] Secrets gitignored (`.env*` in `.gitignore` per Phase 0)
- [ ] Pinned dependencies (need to check)
- [ ] CI runs migrations + tests (D7-06)
- [ ] Postgres health check at startup (D7-08)
- [ ] docker-compose covers full stack (D7-07)

---

## Top-3 fixes (priority order)

1. **D7-03 — Create the missing `sandbox_state` migration.** Unblocks fresh deploy. 30 minutes. (Cross-confirmed in Dim 4 D4-01.)
2. **D7-04 — Update README setup steps with the migration command and test it on a fresh clone.** 30 minutes. Lowest-tech, highest-leverage onboarding fix.
3. **D7-02 — Combined with D4-03 — make `get_engine()` read `DATABASE_URL` and remove the hardcoded localhost fallback in production.** 15 minutes. Prevents wrong-DB connections.
