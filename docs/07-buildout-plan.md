# 07 — Production Buildout Plan (Agentic Loop)

**Source:** `audits/hard-audit-2026-05-07.md` and `docs/06-audit-action-plan.md`
**Created:** 2026-05-07
**Status:** Authoritative for the iterative buildout loop. Updated by the agent on every feature merge, and the checklist must be marked before the merge is considered complete.

---

## What this document is

A sequential, atomically-mergeable feature list to take White Rabbit from "audit-failing" to "deployed and verified." It is optimized for the following two-prompt iteration loop the user will run:

**Prompt A (build):**
> "create a feature branch and develop the next feature on the missing feature list. When you finish, commit and push."

**Prompt B (QA + merge):**
> "/qa and test feature in the web browser. take screen shots to make sure everything looks right. Update docs. Commit, push, and merge"

Between each iteration the user runs `/new` so context resets. The agent in each iteration must be able to figure out *exactly where to pick up* by reading this document. Don't add ambiguity. Don't skip ahead. Don't bundle features.

---

## How the agent finds "next"

### For Prompt A (build):
1. Read this document end-to-end.
2. Read `STATUS.md` — confirm there is no in-flight work.
3. Find the first `- [ ]` (unchecked) item in the [Buildout checklist](#buildout-checklist) below.
4. Scroll down to the matching `### BUILDOUT-NN` section. That section is your spec.
5. Confirm prerequisites (`Depends on:` line) are all `- [x]` already.
6. Create the branch named exactly as specified.
7. Implement per the spec. Run the listed commands. Match the acceptance criteria.
8. Commit with the prescribed message format.
9. Push the branch (no merge — that's Prompt B's job).

### For Prompt B (QA + merge):
1. Identify the in-flight branch via `git branch --show-current` and `git log --oneline main..HEAD`.
2. Look up the matching `### BUILDOUT-NN` section in this doc.
3. Run the **Browser test** (or the **Backend verification** for non-UI features) per the spec.
4. Capture screenshots into `.gstack/qa-reports/screenshots/buildout-NN-*.png`.
5. Write a QA report at `.gstack/qa-reports/buildout-NN-<branch>.md`.
6. Update **this doc**: change `- [ ]` to `- [x] (yyyy-mm-dd, commit-sha-short)` for the matching item.
7. Update `STATUS.md` "What's done" with one bullet referencing the feature.
8. Commit (`docs+qa: BUILDOUT-NN ship-and-merge artifacts`), push, then `gh pr create` + `gh pr merge --squash`. If on a solo workflow without PRs, `git checkout main && git merge --no-ff <branch> && git push`.

---

## Conventions

- **Branch name:** `feat/buildout-NN-short-slug` (e.g., `feat/buildout-01-config-preflight`).
- **Commit subject:** `BUILDOUT-NN: <imperative summary>` (e.g., `BUILDOUT-01: read DATABASE_URL and verify model at startup`). Multiple commits per branch is fine; the **first** commit must have this prefix so the QA agent can find the feature.
- **PR title:** Same as commit subject.
- **PR body:** Reference this section: `Implements docs/07-buildout-plan.md#buildout-NN. Audit ref: <finding ID>.`
- **Screenshots:** PNGs at `.gstack/qa-reports/screenshots/buildout-NN-*.png`.
- **QA report:** `.gstack/qa-reports/buildout-NN-<branch-slug>.md`.
- **Definition of Done (DoD):** Every feature must satisfy:
  1. Branch passes `pytest` (api+core) and `npm test` (web). Skip an integration test only with explicit reason in the QA report.
  2. Browser test (or backend verification) passes per the feature spec.
  3. This doc updated: checklist line marked `- [x]`.
  4. `STATUS.md` "What's done" updated with one bullet.
  5. PR merged or branch merged to main; `git status` clean.

---

## How to recover from a stalled iteration

If the agent finds an in-flight branch (HEAD ≠ main, with un-merged commits):

- If it has a `BUILDOUT-NN:` commit and matches a `- [ ]` item: continue or QA it.
- If it has a `BUILDOUT-NN:` commit but the matching item is already `- [x]`: this is a re-do. Confirm with the user before proceeding.
- If it has no `BUILDOUT-NN:` commit: it's unrelated work. Stop and ask the user.

If a feature looks too big once you start: split it. Add a second `- [ ]` row to this doc with a sub-letter (e.g., `BUILDOUT-04a` and `BUILDOUT-04b`), commit the doc change first, then proceed with the first sub-feature only.

---

## Buildout checklist

> Mark `- [x] (date, commit)` only after merge. Reorder only with care — dependencies are noted in each spec.

### Phase A — Infrastructure (P0, blocks everything)
- [x] (2026-05-08, a5c5dbf) BUILDOUT-01: Config preflight + DATABASE_URL respect + remove Ollama trap (`feat/buildout-01-config-preflight`)
- [x] (2026-05-08, a5c5dbf) BUILDOUT-02: Add `sandbox_state` alembic migration (`feat/buildout-02-sandbox-state-migration`)
- [x] (2026-05-08, 4a4cd32) BUILDOUT-03: Server-side session token expiry (`feat/buildout-03-session-expiry`)

### Phase B — Product correctness (P0, makes the product not-lying)
- [x] (2026-05-08, af4bc1c) BUILDOUT-04: Strip VoIP bias; restore lost proxy-lead prompt instructions (`feat/buildout-04-vertical-agnostic-prompt`)
- [x] BUILDOUT-05: Pydantic validators on Lead.name and Lead.email (`feat/buildout-05-lead-validators`)
  - QA verified in browser on 2026-05-08: Scout query returned valid person names and non-placeholder emails; recipe library showed the saved Full run and scoreboard with no console errors.
- [x] BUILDOUT-06: Server-side `gate_passed` validation (`feat/buildout-06-server-gate`)
  - QA verified in browser on 2026-05-08: Scout query rendered a lead card with 70/70/0 scores, the Gate pass/fail sort selected correctly, and the console stayed clean.

### Phase C — Verification (P0, automated regression)
- [x] BUILDOUT-07: Real-API integration test for `scout()` (`feat/buildout-07-integration-test`)
  - QA verified on 2026-05-08: browser-checked the protected shell, Scout workspace, recipe library, and bulk run workspace; `pytest -m integration -q` in `packages/core` skipped cleanly without real API keys (`5 skipped, 26 deselected`).

### Phase D — Cleanup that prevents drift
- [x] (2026-05-08, 6f11d6f) BUILDOUT-08: Delete `email_patterns.py` dead code (`feat/buildout-08-remove-email-patterns`)
  - QA verified in browser on 2026-05-08: logged in, opened Scout, recipe library, and bulk workspace; confirmed the Scout results page, saved recipes scoreboard, and batch history render cleanly with no console errors.
- [x] (2026-05-08, 6907767) BUILDOUT-09: UI de-bias — placeholders, scout copy, export description (`feat/buildout-09-ui-debias`)

### Phase E — Hardening (P1)
- [x] BUILDOUT-10: Tavily + OpenAI retries with backoff (`feat/buildout-10-retries`) — implemented, tested, and browser-verified on localhost:3000
- [ ] BUILDOUT-11: Feedback label enum + DB CHECK (`feat/buildout-11-feedback-enum`)
- [ ] BUILDOUT-12: Atomic sandbox cap counter (`feat/buildout-12-sandbox-atomicity`)
- [ ] BUILDOUT-13: Specific API error codes for UI (`feat/buildout-13-error-codes`)

### Phase F — Documentation & process
- [ ] BUILDOUT-14: README setup walkthrough verified end-to-end (`feat/buildout-14-readme-verified`)
- [ ] BUILDOUT-15: QA rubric document + multi-vertical gate (`feat/buildout-15-qa-rubric`)

### Phase G — Deploy
- [ ] BUILDOUT-16: Choose hosting; configure environments and secrets (`feat/buildout-16-deploy-config`)
- [ ] BUILDOUT-17: Live deploy + smoke test against production URL (`feat/buildout-17-deploy-smoke`)

**Stop criteria:** When all 17 are `- [x]`, the product is deployed and verified. Anything beyond that is `06-audit-action-plan.md` Phase 3 polish.

---

## Feature specs

### BUILDOUT-01: Config preflight + DATABASE_URL respect + remove Ollama trap

**Why:** The audit's #1 finding. `apps/api/.env` sets `OPENAI_BASE_URL=http://localhost:11434/v1` which silently routes every chat completion to local Ollama. `get_engine()` ignores `DATABASE_URL` so production tries hardcoded localhost. There's no startup verification that env is sane. (Audit refs: F2-05, D4-03)

**Branch:** `feat/buildout-01-config-preflight`

**Depends on:** none (this unblocks everything else)

**Files to read first:**
- `apps/api/api/main.py:30–60` (FastAPI startup)
- `apps/api/api/models.py:114–120` (`get_engine`)
- `apps/api/.env` (the trap; do not commit changes that re-introduce it)
- `packages/core/src/core/orchestrator.py:57–80` (where the OpenAI client is built)
- `/Users/mschwar/Documents/proxy-lead/agent.py:44–71` (reference implementation: `_resolve_openai_config` + `_verify_openai_model`)

**Implementation steps:**
1. Edit `apps/api/api/models.py:114–116` so `get_engine()` reads `os.environ.get("DATABASE_URL")` in the fallback chain. Keep the localhost default but only when `WR_ENV != "production"`.
2. Edit `apps/api/.env`: comment out `OPENAI_BASE_URL=http://localhost:11434/v1` (do not delete — leave a comment explaining the dev-Ollama use case). Confirm `.env` is not tracked (it should already be in `.gitignore`).
3. Edit `apps/api/.env.example` and `apps/api/.env.example` (root): add `OPENAI_BASE_URL=` line with a comment `# Optional. Override only for dev with local OpenAI-compatible endpoint (e.g. http://localhost:11434/v1 for Ollama).` Same for `WR_ENV=development`.
4. Add a startup preflight in `apps/api/api/main.py`. New function `def _preflight_check():` that:
   - Confirms `OPENAI_API_KEY`, `TAVILY_API_KEY`, `WR_SHARED_PASSWORD`, `WR_SESSION_SECRET`, `DATABASE_URL` are set (raise `RuntimeError` with a clear message listing missing vars if any are blank).
   - Calls `OpenAI(api_key=...).models.retrieve(DEFAULT_MODEL)` to verify the model is reachable. On failure, raise with the model name and base URL in the error.
   - Logs `OpenAI: <model> @ <base_url or default>` and `Postgres: <hostname from DATABASE_URL>` at INFO level on success.
   - Called from `init_db()` or app startup.
5. Add a unit test for `_preflight_check()` that mocks the env and asserts the missing-key path raises with the right message.

**Acceptance criteria:**
- `cd apps/api && uv run uvicorn api.main:app` starts and logs the resolved model + postgres host.
- Setting `OPENAI_API_KEY=""` in env makes startup fail with `RuntimeError: Missing required env: OPENAI_API_KEY`.
- Setting `DATABASE_URL=postgresql://elsewhere/db` in env makes the engine connect to elsewhere (verify with `\conninfo` in psql or by intentionally pointing at a non-existent host and confirming the error names that host, not localhost).
- A real scout call from the web UI returns lead cards with non-VoIP-only content (still biased — that's BUILDOUT-04 — but no longer 503s).

**Browser test (Prompt B):**
1. Start Postgres + API + web. Confirm API logs show `OpenAI: gpt-4o-mini @ https://api.openai.com/v1`.
2. Navigate to `/login`, sign in, run a Scout query for `Healthcare IT directors in Phoenix`.
3. Verify lead cards render with real names and emails. Screenshot.
4. Stop the API. Set `DATABASE_URL=postgresql://nonexistent:5432/x`. Restart. Confirm API logs the failure clearly with the bad hostname. Screenshot.

**Commit message (first commit):** `BUILDOUT-01: read DATABASE_URL and verify model at startup`

**Doc updates:** Update this doc's checklist; add bullet to `STATUS.md` "What's done"; update `README.md` if env var list changed.

**Estimated effort:** 1h human / 30min AI.

---

### BUILDOUT-02: Add `sandbox_state` alembic migration

**Why:** Fresh deploys break because the `sandbox_state` table has no migration; today's dev env only has it because `init_db()` calls `Base.metadata.create_all()` as a parallel schema path. (Audit refs: D4-01, D7-03)

**Branch:** `feat/buildout-02-sandbox-state-migration`

**Depends on:** `- [x] BUILDOUT-01` (preflight will validate DB connectivity).

**Files to read first:**
- `apps/api/api/models.py:101–111` (the `SandboxState` model definition)
- `apps/api/alembic/versions/` (existing migrations)
- `apps/api/alembic/env.py` (alembic config)
- `apps/api/api/main.py` (find the `Base.metadata.create_all(_engine)` call to remove)

**Implementation steps:**
1. `cd apps/api && uv run alembic revision --autogenerate -m "add sandbox_state table"`. Review the generated file under `alembic/versions/`.
2. Confirm the migration creates the `sandbox_state` table with all columns from `SandboxState` and the seed row referenced by `_SANDBOX_STATE_ID`. If the seed row is needed, add an `op.bulk_insert` to the upgrade.
3. Remove `Base.metadata.create_all(_engine)` from `init_db()` (or its caller). Alembic is now the single source of truth.
4. Drop the dev DB locally: `dropdb white_rabbit && createdb white_rabbit && uv run alembic upgrade head`. Verify all 7 tables exist.
5. Add a test in `apps/api/tests/test_api.py` that calls `/sandbox` after a fresh migration and asserts no `relation does not exist` error.

**Acceptance criteria:**
- Fresh DB → `alembic upgrade head` → `/scout` works without `Base.metadata.create_all()` fallback.
- `alembic downgrade -1` cleanly removes the table.
- All existing tests still pass.

**Browser test (Prompt B):**
1. Drop and re-create the local DB; run `alembic upgrade head`.
2. Navigate to `/scout`, run a query, confirm the sandbox usage card shows "Queries: 1 / 10" and "Rows: N / 1000". Screenshot.
3. Click the "Reset sandbox" button (if present) and confirm counters reset. Screenshot.

**Commit message:** `BUILDOUT-02: add sandbox_state migration and remove create_all fallback`

**Estimated effort:** 30min human / 15min AI.

---

### BUILDOUT-03: Server-side session token expiry

**Why:** `verifySessionToken` decodes `iat` but never compares to `Date.now()`. Stolen cookies are valid forever. (Audit ref: D4-02)

**Branch:** `feat/buildout-03-session-expiry`

**Depends on:** none (independent of A-1, A-2)

**Files to read first:**
- `apps/web/src/lib/auth.ts` (full file; specifically lines 75–97)
- `apps/web/src/lib/__tests__/auth.test.ts`
- `apps/web/src/app/api/login/route.ts:30–50` (where `maxAge` is set)

**Implementation steps:**
1. In `auth.ts`, add a module constant `const SESSION_MAX_AGE_MS = 7 * 24 * 60 * 60 * 1000;` matching the cookie `maxAge`.
2. After the `parsed.iat` type check in `verifySessionToken`, add: `if (Date.now() - parsed.iat > SESSION_MAX_AGE_MS) return false;` and `if (parsed.iat > Date.now() + 60_000) return false;` (clock-skew guard against future-dated tokens).
3. Add tests in `auth.test.ts`:
   - Valid token → true.
   - Token with `iat` 8 days old → false.
   - Token with `iat` 2 hours in the future → false.
   - Token with `iat = Date.now() - 30s` (skew-tolerable past) → true.

**Acceptance criteria:**
- Existing auth tests still pass.
- New tests for expiry pass.
- Manual: forge a cookie with old `iat` (use the test helpers); confirm middleware redirects to login.

**Browser test (Prompt B):**
1. Sign in.
2. Open DevTools → Application → Cookies. Note the session cookie name.
3. Hit `/scout`, confirm authenticated. Screenshot.
4. (If easy) Use a test page or fetch in the console with a cookie whose `iat` is forced backwards 8 days. Confirm 401/redirect. Screenshot.

If forging the cookie in the browser is awkward, document this skip in the QA report and rely on the unit tests. Tag the QA report with `auth-expiry-unit-tests-only`.

**Commit message:** `BUILDOUT-03: enforce session iat max-age in verifySessionToken`

**Estimated effort:** 30min human / 20min AI.

---

### BUILDOUT-04: Strip VoIP bias; restore lost proxy-lead instructions

**Why:** The audit's central product-correctness finding. SYSTEM_PROMPT and Field descriptions hardcode VoIP/Telecom; live testing reproduced 89% leak rate. proxy-lead's "include organization for every lead" and "set source_url to the strongest URL" instructions were dropped during rewrite. (Audit refs: D1-01, D1-02, D1-04, D5-01, D5-02, F2-01)

**Branch:** `feat/buildout-04-vertical-agnostic-prompt`

**Depends on:** `- [x] BUILDOUT-01` (need real OpenAI to verify).

**Files to read first:**
- `packages/core/src/core/orchestrator.py:20–41` (current SYSTEM_PROMPT)
- `packages/core/src/core/models.py:6–35` (Lead field descriptions)
- `/Users/mschwar/Documents/proxy-lead/agent.py:30–33` (original prompt with the lost instructions)
- `audits/raw/scout-Q1_healthcare.json` (concrete leak examples to write tests against)

**Implementation steps:**
1. Rewrite SYSTEM_PROMPT in `orchestrator.py:20–41`:
   - Remove "B2B telecom lead researcher" → replace with "B2B lead research assistant".
   - Remove "IT, Telecom, VoIP, and Networking" → replace with a query-driven persona: "Extract decision makers from the search results that match the user's query intent."
   - Replace "VoIP prospect" / "VoIP upgrade" with "the role/organization described in the query".
   - Remove "(school district / government / SMB)" example specificity from the icebreaker instruction → keep "their organization type" generic.
   - **Add back from proxy-lead:** "Include the organization name for every lead. If you cannot find a clear organization, omit the lead entirely."
   - **Add back from proxy-lead:** "Set source_url as the URL with the strongest direct evidence of the contact's name, title, and/or organization. Rank by relevance and recency."
   - Replace "If emails are not fully visible, deduce them..." with "If you cannot find an email in the search results, set email='' and email_status='Missing'. Never invent or guess an email."
   - Add: "The 'name' field MUST be a real person's first and last name (e.g., 'Sarah Chen'). Never put a job title or role description in the name field."
2. Edit `packages/core/src/core/models.py`:
   - `why_target` description: `"1 sentence on why this role/organization fits the user's stated query intent"`
   - `icebreaker` description: `"A specific 1-sentence cold email opener referencing their job title, their organization, and one concrete reason their work aligns with the query intent. No template language."`
3. Re-run the audit driver with the new prompt and capture results to `audits/raw/post-buildout-04/`:
   ```
   cd packages/core && env -u OPENAI_BASE_URL OPENAI_API_KEY=<your-key> .venv/bin/python ../../audits/raw/run_scout_audit.py
   ```
   Move the resulting `scout-Q*.json` files into `audits/raw/post-buildout-04/`. Confirm `explanation_leak` rate is < 10% across non-K-12 queries.

**Acceptance criteria:**
- Re-running `audits/raw/run_scout_audit.py` against the same 4 queries shows VoIP leak rate < 10%.
- Each lead's `explanation`, `why_target`, `icebreaker` references the actual query intent (healthcare → healthcare; finance → finance).
- No lead has empty `organization`.
- All existing tests pass.

**Browser test (Prompt B):**
1. Run a Scout query for `Healthcare IT directors in Phoenix`. Inspect ≥2 lead cards. Verify no "VoIP" / "telecom" language. Screenshot each card.
2. Run a Scout query for `Financial services CISOs at mid-size banks in New York`. Inspect ≥2 lead cards. Verify no VoIP language. Screenshot.
3. Run a Scout query for `Manufacturing operations VPs in Detroit`. Inspect ≥2 lead cards. Verify. Screenshot.
4. Verify every lead has an organization rendered.

**Commit message:** `BUILDOUT-04: rewrite SYSTEM_PROMPT to be vertical-agnostic and query-driven`

**Estimated effort:** 4h human / 30min AI.

---

### BUILDOUT-05: Pydantic validators on Lead.name and Lead.email

**Why:** Even if the prompt drifts, validators give defense-in-depth. The user-reported "names are titles" and "fake `not_available@*` emails" failures must not be possible at the schema layer. (Audit refs: D1-03, D2-02, D2-03)

**Branch:** `feat/buildout-05-lead-validators`

**Depends on:** none (independent of BUILDOUT-04 but ideally lands after, so BUILDOUT-04's prompt-only fix is verified before validators kick in).

**Files to read first:**
- `packages/core/src/core/models.py` (full file)
- `packages/core/tests/test_models.py`

**Implementation steps:**
1. In `models.py`, add a `field_validator` for `name`:
   - Must contain at least one whitespace.
   - Must not be a single word.
   - Lowercased name must not contain any of: `director`, `manager`, `officer`, `vp`, `vice president`, `chief`, `executive`, `coordinator`, `supervisor`, `head of`, `principal`, `lead` (as a standalone word — be careful with "leadership", which is fine).
   - Raise `ValueError` with a clear message on violation.
2. Add a `field_validator` for `email`:
   - Empty string is OK.
   - Must match a basic email regex: `^[^@\s]+@[^@\s]+\.[^@\s]+$`.
   - Lowercased email must not start with: `not_available@`, `noreply@`, `no-reply@`, `placeholder@`, `email@`, `info@`, `admin@`, `contact@` (these are placeholders, not real contact emails).
3. Update `tests/test_models.py` with thorough cases:
   - Valid names: `"Sarah Chen"`, `"Jean-Luc Picard"`, `"Dr. Mary O'Brien"`.
   - Invalid names: `"Director of Technology"`, `"VP Engineering"`, `"John"`, `""`.
   - Valid emails: `"a@b.co"`, `""`, `"sarah.chen+work@example.org"`.
   - Invalid emails: `"not_available@x.com"`, `"info@x.com"`, `"a@"`, `"@b.co"`.
4. Re-run `pytest`. Update any test fixtures or mocks elsewhere that violate the new rules. (Hint: search for `name="Jane Smith"` test fixtures — those should still pass since "Jane Smith" is a real name.)

**Acceptance criteria:**
- New tests pass.
- `Lead(name="Director of Technology", ...)` raises `ValidationError`.
- `Lead(email="not_available@x.com", ...)` raises `ValidationError`.
- All existing tests pass.

**Browser test (Prompt B):**
1. Run a real Scout query. The orchestrator should produce only valid leads (no validator errors at runtime). Screenshot the lead cards. Open DevTools console — no errors.
2. If you can mock the orchestrator to attempt to return an invalid lead (e.g., name = "VP Engineering"), confirm the API responds with a 500 + structured error, and the UI surfaces it gracefully. (Optional — note in QA report if skipped.)

**Commit message:** `BUILDOUT-05: add Pydantic validators rejecting role-name and placeholder-email leads`

**Estimated effort:** 1h human / 30min AI.

---

### BUILDOUT-06: Server-side `gate_passed` validation

**Why:** The LLM sets `gate_passed`, but it can disagree with the deterministic `(fit ≥ 0.6 AND evidence ≥ 0.6 AND contact ≥ 0.6)` computation — Phase 2 found 1/9 leads inconsistent. The server should be the source of truth for this pure-arithmetic rule. (Audit refs: D4-07, F2-04)

**Branch:** `feat/buildout-06-server-gate`

**Depends on:** none (independent).

**Files to read first:**
- `packages/core/src/core/orchestrator.py:96–124` (after the LLM completion is parsed)
- `packages/core/src/core/models.py` (`Lead` schema)
- `packages/core/src/core/cost.py` (find a good place to put the threshold constant, or define new module-level)

**Implementation steps:**
1. In `orchestrator.py`, define module constant `GATE_THRESHOLD = 0.6`.
2. After `leads_list = completion.choices[0].message.parsed`, add:
   ```python
   for lead in leads_list.leads:
       expected_gate = (
           lead.fit_score >= GATE_THRESHOLD
           and lead.evidence_score >= GATE_THRESHOLD
           and lead.contact_score >= GATE_THRESHOLD
       )
       lead.gate_passed = expected_gate
   ```
3. Update SYSTEM_PROMPT — remove the "GATE LOGIC" section that asks the LLM to set `gate_passed` (the LLM doesn't need to do this anymore; the server does it). Keep the description of what the gate means but move the threshold definition to a server-only concern.
4. Update `tests/test_orchestrator.py`: add a test where the mock returns a `Lead` with `(fit=0.2, evidence=0.1, contact=0.3, gate_passed=True)` and assert that after `scout()` returns, `gate_passed=False`.

**Acceptance criteria:**
- New test passes.
- Visiting the recipe scoreboard or sort-by-gate UI uses the server-computed values.

**Browser test (Prompt B):**
1. Run a Scout query. Sort by "Pass/Fail Gate". Verify gate icons match the visible sub-scores (a lead with fit=0.55 should fail; a lead with all sub-scores ≥0.6 should pass). Screenshot.
2. Spot-check 3 lead cards: do the gate badges align with the displayed sub-scores?

**Commit message:** `BUILDOUT-06: server-compute gate_passed from sub-scores after LLM parse`

**Estimated effort:** 30min human / 30min AI.

---

### BUILDOUT-07: Real-API integration test for `scout()`

**Why:** Zero existing tests exercise the real LLM extraction path. The audit's central QA finding. This test prevents the entire audit's class of bugs from regressing. (Audit refs: D2-01, D3-02)

**Branch:** `feat/buildout-07-integration-test`

**Depends on:** `- [x] BUILDOUT-01` (real-API path works), `- [x] BUILDOUT-04` (otherwise the test will fail on VoIP leak).

**Files to read first:**
- `audits/raw/run_scout_audit.py` (the standalone driver — port its logic into pytest form)
- `packages/core/tests/test_orchestrator.py`
- `packages/core/pyproject.toml`

**Implementation steps:**
1. Create `packages/core/tests/test_orchestrator_integration.py`. Mark every test with `@pytest.mark.integration` and `@pytest.mark.skipif(not os.getenv("OPENAI_API_KEY"), reason="needs real keys")`.
2. Add tests for the 3 cross-vertical queries (healthcare, finance, manufacturing). Each test:
   - Calls `scout(query)` for real.
   - Asserts `len(leads) > 0`.
   - For each lead: asserts `name` has a space and contains no role tokens, `email == "" or matches regex` and not a placeholder, `explanation` lower-cased does NOT contain `voip` or `telecom`.
3. Add a 4th test (the K-12 baseline) — same query — assert `len(leads) > 0` and the same rules but allow VoIP-adjacent language since K-12 IT is plausibly VoIP-relevant.
4. Add a test for `gate_passed` consistency: for every returned lead, assert `lead.gate_passed == all(s >= 0.6 for s in [lead.fit_score, lead.evidence_score, lead.contact_score])`.
5. Update `pyproject.toml` to register the `integration` marker so pytest doesn't warn.
6. Update `TESTING.md`: add a section "Integration tests" explaining `pytest -m integration` requires env keys and incurs cost (~$0.05 per full run).
7. (Optional, if CI exists) Wire `pytest -m integration` into a separate CI job that runs on demand or weekly, not on every PR.

**Acceptance criteria:**
- `pytest -m integration` runs all 4 queries in <2 minutes and passes.
- `pytest` (no marker) skips the integration tests as expected.
- Test failures are descriptive — when a lead fails an assertion, the failure message includes the lead's name and the failing field.

**Browser test (Prompt B):** This is a backend feature with no UI surface. Run `pytest -m integration` instead of a browser test. Capture the full passing pytest output as `.gstack/qa-reports/buildout-07-pytest-output.txt`. In the QA report, copy the test names and durations.

**Commit message:** `BUILDOUT-07: integration test verifying real scout() across 4 verticals`

**Estimated effort:** 4h human / 1h AI.

---

### BUILDOUT-08: Delete `email_patterns.py` dead code

**Why:** 132 lines of code that nothing imports. Misleads contributors. The `infer_email_patterns` integration was the wrong call for now — defer until we have a real use for it. (Audit refs: D1-06, D4-08, D5-04, D8-04)

**Branch:** `feat/buildout-08-remove-email-patterns`

**Depends on:** `- [x] BUILDOUT-04` (so the prompt no longer references "deduce emails from common domain patterns" — otherwise removing this implies a prompt mismatch).

**Files to read first:**
- `packages/core/src/core/email_patterns.py` (the file being deleted)
- `packages/core/src/core/__init__.py` (confirm no re-export)
- The whole repo: `grep -r "email_patterns\|infer_email_patterns\|EmailPatternInsight" packages/ apps/`

**Implementation steps:**
1. Verify with grep that `email_patterns` is not imported anywhere outside the file itself. If anything is found, stop and update the spec.
2. Delete `packages/core/src/core/email_patterns.py`.
3. Remove any references in `docs/05-reuse.md` that claim it was lifted as a working module — update to "deferred; deleted in BUILDOUT-08, see audit D5-04 for context."
4. Run `pytest`. Run `npm test`. Run `mypy` or `ruff` if configured.

**Acceptance criteria:**
- File deleted.
- `grep` returns 0 hits for `email_patterns` and `infer_email_patterns` and `EmailPatternInsight` across `packages/` and `apps/`.
- All tests pass.

**Browser test (Prompt B):** Backend-only change with no UI surface. Run scout and confirm leads still come back; the old `email_status` field still works (Found / Deduced / Missing — the labels are still meaningful even without the pattern-inference module). Screenshot a lead card with each `email_status` value if available.

**Commit message:** `BUILDOUT-08: delete unused email_patterns.py dead code`

**Estimated effort:** 15min human / 5min AI.

---

### BUILDOUT-09: UI de-bias — placeholders, scout copy, export description

**Why:** The K-12 Albuquerque placeholder appears 3× in the UI and trains users to use the failing query. Scout description claims "10–20 leads" but cap is 15. Export description is incomplete. (Audit refs: D6-01, D6-02, D6-15)

**Branch:** `feat/buildout-09-ui-debias`

**Depends on:** none (UI-only).

**Files to read first:**
- `apps/web/src/components/scout-workspace.tsx:230–460`
- `apps/web/src/components/batch-workspace.tsx:14–20`
- `apps/web/src/lib/full-export.ts:107–129` (the actual CSV columns)

**Implementation steps:**
1. In `scout-workspace.tsx`:
   - Change `placeholder="K-12 IT directors in Albuquerque"` → `placeholder="Healthcare IT directors in Phoenix"` (a vertical-neutral diverse example — pick any of the 3 verticals from the integration test).
   - Change recipe-name placeholder `"My K-12 IT director recipe"` → `"My prospect list"` (or similar generic).
   - Change Scout description from `"Scout: quick preview (10–20 leads, no storage). Full: stored recipe with up to 100 leads."` → `"Scout: quick preview (up to 15 leads, no storage). Full: stored recipe with up to 100 leads."`.
   - Update lead-export description to list all CSV columns accurately. Suggested: `"Includes query, location, recipe name, run ID, rank, lead name/title/org/email, email status, source URL, fit/evidence/contact scores, gate status, icebreaker, why_target, explanation, and validation context."`
2. In `batch-workspace.tsx:16–17`: replace the two K-12 New Mexico defaults with two distinct verticals — e.g., `"Healthcare IT directors in Phoenix"` (filters: Arizona) and `"Financial services CISOs in New York"` (filters: New York). Diversity teaches users to explore.
3. Update any tests that assert on the old placeholder/description text.

**Acceptance criteria:**
- All tests pass.
- Visual: scout page shows the new placeholder; batch page shows the two new defaults.

**Browser test (Prompt B):**
1. Visit `/scout`. Screenshot the empty state showing the new placeholder.
2. Visit `/batch`. Screenshot the empty state showing the two new defaults.
3. Run a search using the new placeholder text — it should produce non-VoIP-themed leads (assuming BUILDOUT-04 has landed). Screenshot.

**Commit message:** `BUILDOUT-09: replace K-12 placeholder defaults; correct scout copy and export description`

**Estimated effort:** 30min human / 15min AI.

---

### BUILDOUT-10: Tavily + OpenAI retries with exponential backoff

**Why:** A single transient failure on Tavily or OpenAI surfaces as an unstructured 503 today. Add ≤2 retries with backoff for transient errors only. (Audit refs: D4-06, D2-04)

**Branch:** `feat/buildout-10-retries`

**Depends on:** none.

**Files to read first:**
- `packages/core/src/core/orchestrator.py:80–106`
- `packages/core/src/core/search.py:48–87`
- OpenAI SDK retry support: many SDKs have built-in retry; check if `AsyncOpenAI(max_retries=2)` is sufficient instead of hand-rolled.

**Implementation steps:**
1. For OpenAI: pass `max_retries=2` to `AsyncOpenAI(...)` constructor. The SDK retries on 429/5xx by default.
2. For Tavily: wrap `_call_tavily` (or equivalent) in a small retry loop:
   ```python
   for attempt in range(3):
       try:
           return await _call_tavily(...)
       except (httpx.TimeoutException, httpx.NetworkError):
           if attempt == 2:
               raise
           await asyncio.sleep(0.5 * (2 ** attempt))
   ```
   Do NOT retry validation errors or 4xx responses.
3. Add unit tests: `fake_search` raises `TimeoutException` once then succeeds → orchestrator retries and returns leads. `fake_search` raises 3 times → orchestrator raises `OrchestratorError`.

**Acceptance criteria:**
- New tests pass.
- The retry behavior is reflected in metrics (the existing `tavily_searches` count should still equal the number of successful Tavily calls, not retry attempts — adjust if needed).

**Browser test (Prompt B):**
Backend-only. Run scout normally to confirm no regression. Screenshot a successful run. In QA report note: "retry behavior validated by unit tests; no manual fault injection."

**Commit message:** `BUILDOUT-10: retry Tavily and OpenAI on transient failures`

**Estimated effort:** 2h human / 30min AI.

---

### BUILDOUT-11: Feedback label enum + DB CHECK constraint

**Why:** `FeedbackRequest.label: str` with no enum means `"Usable"` (capitalized) silently breaks scoreboard counts. (Audit ref: D4-05)

**Branch:** `feat/buildout-11-feedback-enum`

**Depends on:** none.

**Files to read first:**
- `apps/api/api/main.py:82–83` (FeedbackRequest)
- `apps/api/api/db.py:107–116, 172–174` (`add_lead_feedback`, scoreboard aggregation)
- `apps/api/api/models.py` (LeadFeedback table)

**Implementation steps:**
1. Replace `label: str` with `label: Literal["usable", "wrong_persona", "bad_source", "bad_contact", "duplicate"]` in `FeedbackRequest`.
2. Generate a new alembic migration adding a CHECK constraint on `lead_feedback.label`:
   ```sql
   CHECK (label IN ('usable','wrong_persona','bad_source','bad_contact','duplicate'))
   ```
3. Add a unit test: `POST /leads/{id}/feedback {"label":"Usable"}` returns 422 with a clear validation error (not 200).
4. Frontend (`apps/web/src/components/scout-workspace.tsx` or wherever feedback buttons are): confirm only the canonical lowercase strings are sent.

**Acceptance criteria:**
- Validation tests pass.
- Migration runs cleanly up and down.

**Browser test (Prompt B):**
1. Click each of the 5 feedback buttons on a lead. Confirm in DevTools Network tab that the `label` is the canonical lowercase string. Screenshot one click.
2. Refresh the recipe scoreboard. Confirm `usable_lead_count` reflects the click. Screenshot.

**Commit message:** `BUILDOUT-11: enforce feedback label enum at API and DB layers`

**Estimated effort:** 30min human / 10min AI.

---

### BUILDOUT-12: Atomic sandbox cap counter

**Why:** Concurrent requests can both pass the pre-call cap check and both increment, exceeding the cap. (Audit ref: D4-04)

**Branch:** `feat/buildout-12-sandbox-atomicity`

**Depends on:** `- [x] BUILDOUT-02` (the migration must exist before we can lock the row).

**Files to read first:**
- `apps/api/api/main.py:154–177, 196–228` (`_sandbox_reserve_query_or_429`, scout/full handlers)
- `apps/api/api/db.py:get_sandbox_state`

**Implementation steps:**
1. In `db.py`, add a function `get_sandbox_state_for_update(session)` that does:
   ```python
   return session.query(SandboxState).filter(SandboxState.id == _SANDBOX_STATE_ID).with_for_update().first()
   ```
2. In `_sandbox_reserve_query_or_429`, replace `get_sandbox_state(session)` with the locking version. The session-level commit will release the row lock.
3. Add a concurrency test: spawn 12 simultaneous Scout requests via `httpx.AsyncClient` against the test API, with cap=10. Assert that exactly 10 succeed (200) and 2 fail (429). The non-atomic version typically lets 11–12 through.

**Acceptance criteria:**
- Concurrency test passes deterministically (run it 5× to confirm).
- All existing tests pass.

**Browser test (Prompt B):**
Hard to demonstrate concurrency in a browser. Note in QA report: "atomicity validated by concurrency test in apps/api/tests/test_api.py::test_sandbox_atomic_cap." Do a single sandbox-cap exhaustion run via the UI: send 11 sequential queries, confirm the 11th gets the 429 message. Screenshot the error toast.

**Commit message:** `BUILDOUT-12: lock sandbox_state row during cap check`

**Estimated effort:** 1h human / 20min AI.

---

### BUILDOUT-13: Specific API error codes for UI

**Why:** Generic 503 / 500 responses tell users nothing about why things failed. (Audit ref: D6-04)

**Branch:** `feat/buildout-13-error-codes`

**Depends on:** none.

**Files to read first:**
- `apps/api/api/main.py:209–216` (current generic error handlers)
- `apps/web/src/components/scout-workspace.tsx` error rendering paths
- `apps/web/src/app/api/scout/route.ts`

**Implementation steps:**
1. In `apps/api/api/main.py`, change the OrchestratorError handler to return a structured body: `{"error_code": "orchestrator_error", "message": str(exc), "request_id": <uuid>}`. Distinguish sub-cases:
   - Tavily failure → `error_code: "tavily_failed"`.
   - OpenAI failure → `error_code: "openai_failed"`.
   - LLM parse failure → `error_code: "llm_parse_failed"`.
2. In the generic Exception handler, return `{"error_code": "internal_error", "message": "An unexpected error occurred.", "request_id": <uuid>}` with a 500.
3. In `scout-workspace.tsx`, parse the structured error and map known `error_code` values to specific user-facing messages: e.g., `"Search engine is rate-limited; try again in ~60s"` for `tavily_failed`. Fall back to the generic message for unknown codes.

**Acceptance criteria:**
- Existing error-handling tests pass with the new structure.
- New test: when the orchestrator raises `OrchestratorError("Tavily search failed: timeout")`, the API returns 503 with `error_code: "tavily_failed"` (or generic `orchestrator_error` if you don't want to introspect the exception message).

**Browser test (Prompt B):**
Hard to provoke real failures. If you have a way to force an error (e.g., temporarily set `TAVILY_API_KEY=""` in a dev session), do it and screenshot the new specific error message. Otherwise note "tested via unit test only" in the QA report.

**Commit message:** `BUILDOUT-13: return structured error_code in API responses`

**Estimated effort:** 1h human / 30min AI.

---

### BUILDOUT-14: README setup walkthrough verified end-to-end

**Why:** README doesn't mention `alembic upgrade head`, has stale "not yet scaffolded" copy in places. A fresh-checkout developer needs a deterministic path. (Audit ref: D7-04)

**Branch:** `feat/buildout-14-readme-verified`

**Depends on:** `- [x] BUILDOUT-01`, `- [x] BUILDOUT-02` (both must work for the walkthrough to succeed).

**Files to read first:**
- `README.md`
- `docker-compose.yml`
- `apps/api/.env.example`, `apps/web/.env.example`, root `.env.example`

**Implementation steps:**
1. Rewrite README setup section to a deterministic order:
   ```
   1. git clone <url> && cd white-rabbit
   2. cp .env.example .env (and likewise for apps/api and apps/web — list each)
   3. Fill in API keys: OPENAI_API_KEY, TAVILY_API_KEY, WR_SHARED_PASSWORD, WR_SESSION_SECRET, DATABASE_URL
   4. docker-compose up -d   # starts Postgres
   5. cd apps/api && uv sync && uv run alembic upgrade head
   6. uv run uvicorn api.main:app --reload   # API on :8000
   7. (new terminal) cd apps/web && npm install && npm run dev   # web on :3000
   8. Open http://localhost:3000, log in with WR_SHARED_PASSWORD, run a Scout query
   ```
2. Test the sequence on a fresh clone in a temp directory. Note any step that fails or has unstated prerequisites. Fix.
3. Add a "Common issues" section at the bottom with troubleshooting (e.g., "If you see `model not found`, check that OPENAI_BASE_URL is unset or points to api.openai.com").

**Acceptance criteria:**
- A fresh clone in `/tmp/wr-test` running the steps reaches a working /scout in <10 minutes.
- A non-Matt developer (i.e., me as the agent) follows the steps without needing tribal knowledge.

**Browser test (Prompt B):**
Run the walkthrough. After step 8, take a screenshot of the working scout page. Capture the full terminal log of the walkthrough. Save both to `.gstack/qa-reports/buildout-14-fresh-clone-walkthrough/`.

**Commit message:** `BUILDOUT-14: rewrite README setup; verified on fresh clone`

**Estimated effort:** 1h human / 30min AI.

---

### BUILDOUT-15: QA rubric document + multi-vertical gate

**Why:** The audit's central QA finding — UI-only QA can't catch data-quality bugs. Document the 6-tier rubric so it becomes a process, not a one-off. (Audit refs: D3-02, D3-04)

**Branch:** `feat/buildout-15-qa-rubric`

**Depends on:** `- [x] BUILDOUT-04` (otherwise the rubric's vertical-leak check will keep failing).

**Files to read first:**
- `audits/sub/03-qa-methodology.md` (the rubric draft)
- `.gstack/qa-reports/index.md` (current QA report index)

**Implementation steps:**
1. Write `docs/qa-rubric.md` with the 6 tiers from `audits/sub/03-qa-methodology.md`:
   - Tier 1: Multi-vertical content check
   - Tier 2: Persistence read-back
   - Tier 3: CSV export inspection
   - Tier 4: Prompt validation
   - Tier 5: Failure modes
   - Tier 6: UI smoke
2. For each tier, write 2–4 explicit checks with example assertions (e.g., for Tier 1: "lead.name contains a space", "lead.explanation does not contain 'voip' for non-VoIP queries").
3. Add a "Ship gate" section: Tiers 1–4 must pass before any change touching `orchestrator.py` or `models.py` ships. Tiers 5–6 every PR.
4. Update `.gstack/qa-reports/index.md` to reference the rubric.
5. (Optional) Add a `qa-template.md` skeleton for new QA reports that prompts the writer through each tier.

**Acceptance criteria:**
- `docs/qa-rubric.md` exists, is concrete, and is referenced from `STATUS.md` and `AGENTS.md`.

**Browser test (Prompt B):** This is documentation. No browser test. The QA agent should read the new rubric and apply Tier 1 to a fresh scout run, capturing screenshots that satisfy each Tier 1 check.

**Commit message:** `BUILDOUT-15: add docs/qa-rubric.md with 6-tier ship-gate`

**Estimated effort:** 2h human / 1h AI.

---

### BUILDOUT-16: Choose hosting; configure environments and secrets

**Why:** The product is local-only today. Pre-deploy: pick targets, configure secrets, write deploy config. (Audit ref: deployment readiness — D7 dimension)

**Branch:** `feat/buildout-16-deploy-config`

**Depends on:** All P0 items above (`- [x] BUILDOUT-01..09`).

**User decision required:** Three platform choices that the agent should NOT decide alone. The agent's first action on this feature is to surface these choices to the user (block in chat — do not proceed silently):

1. **Web hosting:** Vercel (default for Next.js, free tier fine for this scale) vs. self-hosted (Fly, Railway, Render).
2. **API hosting:** Fly.io / Railway / Render / Vercel Functions. (Vercel Functions has cold-start cost for Python; Fly is the closest to a "real" server.)
3. **Postgres:** Neon / Supabase Postgres / Railway Postgres / managed RDS.

**Default recommendation if user is silent:** Vercel + Fly.io + Neon. All have free tiers, all have first-class git integration.

**Files to read first / create:**
- `apps/web/next.config.ts` (or `.js`/`.mjs` — confirm what's there)
- Create `apps/api/Dockerfile` if Fly.io chosen
- Create `apps/api/fly.toml` if Fly.io chosen
- Create `vercel.json` at repo root if Vercel chosen for the web app

**Implementation steps:**
1. **First step:** post a message in chat listing the three choices and asking for selection. If running headlessly, default to Vercel + Fly.io + Neon and document the choice in commit.
2. Create the chosen platform's config files. Example (Fly.io):
   - `apps/api/Dockerfile` building from `python:3.13-slim`, installing `uv`, copying source, running migrations on startup.
   - `apps/api/fly.toml` with the app name, primary region, internal port 8000.
3. Configure secrets on the chosen platform (the user will need to do this part — the agent can document the commands but should not handle the actual secret values):
   - `OPENAI_API_KEY`, `TAVILY_API_KEY`, `WR_SHARED_PASSWORD`, `WR_SESSION_SECRET`, `DATABASE_URL` (Neon connection string).
4. Update `apps/web/next.config.ts` if needed (e.g., `serverActions` config, image domains).
5. Add a `.github/workflows/deploy.yml` that:
   - On push to main, runs the test suite.
   - If passing, deploys web to Vercel and api to Fly (using the platform's GitHub Actions integration).
   - Runs `alembic upgrade head` against the production DB before the API deploy completes.

**Acceptance criteria:**
- Deploy config files exist and are syntactically valid.
- README has a new "Deployment" section with the chosen targets and the commands to set secrets.
- A dry-run deploy (e.g., `flyctl deploy --no-strategy` or Vercel preview deploy) succeeds.

**Browser test (Prompt B):**
Push the branch. If GitHub Actions workflows are set up, watch the deploy job. Capture screenshots of:
- The deploy job running and succeeding in GitHub Actions.
- The Fly.io / Vercel dashboards showing the new deployment.
- (Optional) curl the deployed `/health` endpoint and capture the response.

If the deployment requires user-only secrets to actually deploy, mark the QA report with "deploy config validated; awaiting user to set secrets." Then BUILDOUT-17 picks up live deploy.

**Commit message:** `BUILDOUT-16: deploy config for <platforms>; CI workflow for prod deploys`

**Estimated effort:** 2h human / 1h AI + user time to set secrets.

---

### BUILDOUT-17: Live deploy + smoke test against production URL

**Why:** Confirm the product actually works on the chosen platforms with real users hitting it.

**Branch:** `feat/buildout-17-deploy-smoke`

**Depends on:** `- [x] BUILDOUT-16` (deploy config exists). User must have set platform secrets.

**Files to read first:**
- The deploy config from BUILDOUT-16.
- `apps/web/e2e/home.spec.ts` (existing Playwright spec — extend for prod URL).

**Implementation steps:**
1. Trigger a fresh deploy: push an empty commit (`git commit --allow-empty -m "BUILDOUT-17: trigger prod deploy"`) and let the CI workflow run.
2. Once both web and api are live, capture the public URLs.
3. Add an environment variable `WR_PROD_URL` for tests. Update the existing Playwright e2e to optionally target prod.
4. Run a smoke flow against the live URL:
   - Visit prod URL, log in with `WR_SHARED_PASSWORD`.
   - Run a Scout query for `Healthcare IT directors in Phoenix`.
   - Confirm leads render with no VoIP language.
   - Submit a Full run.
   - Verify the recipe shows up in `/recipes`.
   - Add feedback. Confirm scoreboard updates.
5. Document the deploy URL in `STATUS.md` (or a new `DEPLOYMENT.md`).
6. Close out: this is the last BUILDOUT feature. Update this doc's "Stop criteria" to confirm completion.

**Acceptance criteria:**
- Production URL is reachable and serves the app.
- Smoke flow above passes against the live URL.
- `STATUS.md` shows the live URL and confirms deployment.

**Browser test (Prompt B):**
Run the smoke flow above against the production URL. Screenshot every step. Add a "Production smoke test" section to the QA report with each screenshot annotated.

**Commit message:** `BUILDOUT-17: live deploy verified; smoke test passes against prod`

**Estimated effort:** 1h human / 30min AI + user time for any platform-specific friction.

---

## Notes for the agent

### When the build prompt fires (Prompt A)
- Do **not** also run QA. The user's two prompts split build from QA. Trust the loop.
- Do **not** merge the branch. Push only.
- After the push, **stop and report** in chat: "BUILDOUT-NN pushed on branch `<name>`. Ready for QA prompt."
- If the spec's prerequisites aren't met (a depended-on feature isn't `- [x]`), stop and tell the user. Don't attempt to do two features in one branch.

### When the QA prompt fires (Prompt B)
- Find the in-flight branch.
- Run the spec's Browser test (or Backend verification).
- Take screenshots into `.gstack/qa-reports/screenshots/buildout-NN-*.png`.
- Write a QA report at `.gstack/qa-reports/buildout-NN-<branch-slug>.md` summarizing what was tested and what passed.
- Update this doc's checklist line to `- [x] (yyyy-mm-dd, <commit-sha-short>) BUILDOUT-NN: ...`.
- Update `STATUS.md` "What's done" with one bullet pointing at the feature and any user-visible change.
- Commit the QA report + doc updates with message `docs+qa: BUILDOUT-NN ship and merge`.
- Push, open a PR (`gh pr create`), and merge it (`gh pr merge --squash --delete-branch`). If the user prefers no PRs, merge directly to main with `--no-ff` and push.
- If QA finds bugs: fix them, commit on the same branch, re-run QA. Don't merge until clean.

### General rules
- Do **not** modify `audits/` or `docs/06-audit-action-plan.md`. Those are historical record. Use this doc for live progress.
- Do **not** skip writing the QA report. It's part of the audit-recommended QA rubric.
- If a feature spec turns out to be wrong (e.g., audit was mistaken), fix the spec in this doc *first* (commit the doc change), then proceed.
- Keep this doc as the single source of truth for buildout state. STATUS.md is the broader project log; this doc is the active sprint board.

---

## Stop criteria

Buildout is complete when:

- [ ] All checklist items above are `- [x]` with date and commit.
- [ ] `pytest -m integration` passes locally and in CI.
- [ ] Production URL is documented in STATUS.md and reachable from a browser.
- [ ] At least one full smoke flow has been run against production by either Matt or an agent.

When all four boxes are checked, mark the file with `**Status: Complete**` at the top and the loop exits.
