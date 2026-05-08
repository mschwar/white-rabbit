# White Rabbit — Hard Audit 2026-05-07

**Branch:** audit/hard-audit-2026-05-07
**Auditor:** Claude Code (Opus 4.7) with 8 parallel sub-agents and live integration testing
**Source brief:** [`audits/FRONTIER_AUDIT_PROMPT.md`](FRONTIER_AUDIT_PROMPT.md)
**Plan:** [`audits/AUDIT_PLAN.md`](AUDIT_PLAN.md)
**Sub-reports:** [`audits/sub/01-08`](sub/)
**Phase 2 raw output:** [`audits/raw/`](raw/)
**Total findings:** 65 (with 2 agent errors caught and corrected)
**API spend:** ~$0.045 across 4 real scout() runs

---

## Executive summary — if we shipped this today

If you ship today, you ship a product where:

1. **Every chat completion silently fails** in any environment that doesn't have a local Ollama with a chat model installed. The current `apps/api/.env` sets `OPENAI_BASE_URL=http://localhost:11434/v1`; the OpenAI SDK reads this transparently. The audit machine had only `nomic-embed-text:latest`, so every scout call returned a 404 until we forced the base URL back to api.openai.com.
2. **Every non-VoIP query produces shoehorned VoIP pitches.** When we forced the working OpenAI endpoint, 89% of leads in healthcare, finance, and manufacturing queries had VoIP/telecom language injected into their `explanation`, `why_target`, and `icebreaker` fields. The CISO of the New York Federal Reserve Bank gets pitched VoIP for "regulatory compliance and security." A hydrogen-fuel-cell VP gets pitched VoIP for production efficiency. The bias is hardcoded into both the SYSTEM_PROMPT and the Pydantic Field descriptions.
3. **A fresh deploy doesn't work.** The `sandbox_state` table has no alembic migration; today's dev environment only has the table because `init_db()` calls `Base.metadata.create_all()` at startup as a parallel schema-management path. A clean alembic-only deploy crashes on the first call to any sandbox-aware route (which is all the user-facing routes).
4. **Production talks to localhost.** `get_engine()` ignores `DATABASE_URL`. Whatever DB credentials are in `apps/api/api/models.py:115` (hardcoded `localhost:5432` with `white_rabbit_dev`) are what production will try to use, regardless of `.env`.
5. **Sessions never expire.** `verifySessionToken` decodes `iat` but never compares it to `Date.now()`. A stolen cookie is valid forever.
6. **Tests verify the wrong things.** All 46 tests use a hand-crafted "Jane Smith" mock; zero exercise the real LLM extraction path. The three production failures the user reported could not have been caught by any existing test.

Net: **the product is not deployable as-is**. Findings 1, 3, 4 are infrastructure-broken; 2 is a product-correctness lie; 5 is a security regression; 6 explains why no one caught any of this. With ~10 hours of focused work the P0s are fixable, but the QA process and tests need a structural change before the product can be trusted again.

---

## Top 10 blockers (ranked by user impact)

| # | Finding | Severity | One-line fix | Sub-report |
|---|---------|----------|--------------|-----------|
| 1 | `OPENAI_BASE_URL=http://localhost:11434/v1` in `apps/api/.env` silently routes all chat completions to local Ollama | P0 | Remove the env var or restore `OPENAI_MODEL` + `_verify_openai_model()` plumbing from proxy-lead/agent.py:44–71 | [Phase 2 F2-05](raw/phase-2-findings.md) |
| 2 | SYSTEM_PROMPT hardcodes VoIP/Telecom — 89% of non-VoIP leads had injected VoIP pitches in real testing | P0 | Rewrite orchestrator.py:20–41 to be query-driven, not vertical-asserting | [Dim 1 D1-01](sub/01-prompt-and-data-quality.md) |
| 3 | `sandbox_state` table missing from all alembic migrations | P0 | `cd apps/api && uv run alembic revision --autogenerate -m "add sandbox_state"` | [Dim 4 D4-01](sub/04-code-quality.md) / [Dim 7 D7-03](sub/07-deployment.md) |
| 4 | `get_engine()` (apps/api/api/models.py:114–116) hardcodes localhost; ignores `DATABASE_URL` | P0 | Add `os.environ.get("DATABASE_URL")` to the fallback chain | [Dim 4 D4-03](sub/04-code-quality.md) |
| 5 | Session token `iat` decoded but never compared to clock — tokens valid indefinitely | P0 | Insert `if (Date.now() - parsed.iat > MAX_AGE_MS) return false;` in `apps/web/src/lib/auth.ts:87` | [Dim 4 D4-02](sub/04-code-quality.md) |
| 6 | `Lead.why_target` / `Lead.icebreaker` Field descriptions hardcode "VoIP sales" — feeds bias into the structured-output schema | P0 | Rewrite descriptions in models.py:21,23 to be vertical-agnostic | [Dim 1 D1-02](sub/01-prompt-and-data-quality.md) |
| 7 | Zero tests call the real `scout()` — every test uses "Jane Smith" mock; the three production failures could not have been caught | P0 | Add `tests/test_orchestrator_integration.py` with real-API runs against ≥3 verticals and assertions on name/email/leak | [Dim 2 D2-01](sub/02-test-coverage.md) |
| 8 | Lost proxy-lead instructions: "Include the organization name for every lead" + "Set source_url to the strongest URL" | P0 | Add both back to SYSTEM_PROMPT | [Dim 5 D5-01/D5-02](sub/05-proxy-lead-diff.md) |
| 9 | Prompt explicitly permits email hallucination ("deduce them based on common domain patterns"); `email_patterns.py` is dead code | P0/P1 | Replace with "If you cannot find an email in the search results, set email='' and email_status='Missing'. Never invent an email." Wire `email_patterns.py` back in or delete it. | [Dim 1 D1-04/D1-06](sub/01-prompt-and-data-quality.md) |
| 10 | `gate_passed` set by LLM, never validated server-side; 1/3 manufacturing leads had inconsistency in real testing | P1 | Compute `gate_passed = all(s >= 0.6 for s in [fit, evidence, contact])` server-side after parsing the LLM response | [Dim 4 D4-07](sub/04-code-quality.md), [Phase 2 F2-04](raw/phase-2-findings.md) |

---

## Per-dimension summaries

### [Dimension 1 — Prompt & Data Quality](sub/01-prompt-and-data-quality.md)
**4 P0, 2 P1, 2 P2, 1 verified clean.** Prompt explicitly assumes VoIP; field descriptions reinforce it; no validators on name or email; `raw_content=False` strips Tavily context the LLM needs; `email_patterns.py` exists but is dead. Confirmed end-to-end against real OpenAI in Phase 2.

### [Dimension 2 — Test Coverage](sub/02-test-coverage.md)
**3 P0, 4 P1, 6 P2.** 16 test files exist (~46 tests) but zero call real `scout()`. ~32 public functions have no direct coverage. The "Jane Smith" mock spans every layer. Brief's "core has zero tests" is factually wrong — 3 files, 206 LOC; but they verify nothing about extraction quality.

### [Dimension 3 — QA Methodology](sub/03-qa-methodology.md)
**3 P0, 4 P1, 1 P2.** All QA reports tested the same K-12 Albuquerque query — the one query that aligns with the hidden VoIP bias. Lead card *content* never inspected. CSV export validated for link-presence only. Recommended: a 6-tier QA rubric requiring multi-vertical content checks and DB read-back.

### [Dimension 4 — Code Quality](sub/04-code-quality.md)
**3 P0, 4 P1, 6 P2, 1 P3 — most substantive sub-audit.** New findings include `DATABASE_URL` ignored, session tokens never expire, batch spend cap is post-bill, Lead.data JSON duplicates 4 scalar columns, password compare leaks length via early-return, and feedback label is a free-form `str` with no enum.

### [Dimension 5 — Proxy-lead Drift](sub/05-proxy-lead-diff.md)
**2 P0, 5 P1, 1 P2.** Two instructions silently dropped from SYSTEM_PROMPT during the LangChain → OpenAI SDK rewrite ("organization required", "strongest source URL"). `confidence` deprecated but still required. Search history APIs and persistent cost ledger lost. Bulk failure semantics changed from try-all to halt-on-cap.

### [Dimension 6 — UI/UX Copy](sub/06-ui-copy.md)
**3 P1, 2 P2, 1 P3.** Scout description claims "10–20 leads" but cap is 15. K-12 Albuquerque placeholder appears 3× in the UI, teaching users the failing query. Generic 503/500 errors mask root cause. No dead links / no "Coming Soon" buttons — clean on that axis.

### [Dimension 7 — Deployment](sub/07-deployment.md)
**1 P0, 4 P1, 2 P2 — after correction. Two agent errors caught and rejected** (D7-01 falsely claimed `.env.example` files don't exist; D7-05 falsely claimed empty-password fall-through). Real findings: missing `sandbox_state` migration (P0), README has no alembic step, hardcoded localhost Postgres credentials, no CI, no Docker for web/api.

### [Dimension 8 — Doc Drift](sub/08-doc-drift.md)
**2 P1, 2 P2.** 93% of doc claims verified accurate. STATUS.md "Known issues" lists items that are already fixed (persisted lead IDs, server guardrails). 2026-05-06 reconciliation report is stale. TESTING.md `__tests__/` convention applied universally but Python uses `tests/`. Notably absent: any doc claims vertical-agnosticism, so VoIP bias is not a *contradiction* — it's an *unaddressed scope question*.

### [Phase 2 — Live integration](raw/phase-2-findings.md)
**5 findings — one new P0** (`OPENAI_BASE_URL` routing to Ollama). VoIP bias reproduced at 89% rate. Names and emails were correctly extracted by gpt-4o-mini, suggesting the user's reported "titles as names" / "fake emails" failures came from a previous Ollama+small-model configuration where structured-output schema adherence is unreliable. Total spend $0.045.

---

## Cross-cutting themes

### Theme A — "Lifted ≠ wired"

The proxy-lead → white-rabbit rewrite copied modules byte-for-byte but didn't always integrate them. `email_patterns.py` is the most visible example: 132 lines of working pattern-inference code with zero importers. The prompt instructs the LLM to deduce emails from "common domain patterns" while the module that learns those patterns is dead. Lifting code is half the work; integration is the other half. Several "completed Sprint 1" items in STATUS are actually "code present" not "code working."

### Theme B — Trust boundaries are inverted

The system trusts the LLM to enforce a deterministic business rule (`gate_passed = all(s >= 0.6)`) but doesn't trust *itself* to validate user input formats (no Pydantic validators on name or email). Real testing caught one gate inconsistency in 9 leads. Server-side computation of `gate_passed` and Pydantic validators on Lead fields fix both halves at low cost.

### Theme C — Configuration is tribal knowledge

`OPENAI_BASE_URL` quietly routes to Ollama. `DATABASE_URL` is silently ignored. Required env vars aren't enforced. The proxy-lead reference had a `_verify_openai_model()` startup check that made model availability explicit; v2 dropped it. A 30-line "config preflight" function at FastAPI startup that validates every required env var and tests connectivity to OpenAI/Tavily/Postgres would have caught all three of these issues at boot, not at first-request.

### Theme D — UI-only QA cannot catch data-quality bugs

The QA process counts rendered lead cards. The product fails at lead content. These are different abstraction layers, and no test suite or QA pass spans both. The 6-tier QA rubric in Dim 3 addresses this; the integration test in D2-01 is its automated sibling.

### Theme E — One vertical, one query, one false signal

Both QA runs used "K-12 IT directors in Albuquerque" — a query whose vertical aligns with the hidden VoIP bias. The placeholder and batch defaults teach users to use the same query. The reason the bug went undetected for 4+ sprints is that the test signal was the bug's mascot. New rule: every QA pass must hit ≥3 verticals; placeholders must rotate.

---

## Risk register — what could still be wrong after fixes

1. **Ollama config history.** The user's reported failures (titles as names, fake emails) didn't reproduce under OpenAI but did appear in their screenshots. If those screenshots were generated by Ollama + a small chat model that didn't exit cleanly when it couldn't follow the schema, the *same product on a different operator's machine* could produce broken output even after the prompt is fixed. Recommendation: enforce a known-good model whitelist at boot.
2. **proxy-lead config.py drift.** Dim 5 noted `config.py` was not lifted (intentional, per docs). But proxy-lead's auth/secret resolution logic was richer than v2's — there may be additional env-resolution corner cases worth porting (e.g., the bcrypt detection).
3. **Storage path coverage.** Phase 2 didn't boot the full stack, so `/full` end-to-end persistence wasn't verified live. Dim 4's code review found the `/full` DB section is unguarded by any try/except — a DB error mid-write returns an unstructured 500 and leaves the run partially-stored. This is unverified but inferred.
4. **Cost ledger absence.** No persistent cost record means we cannot answer "how much did this account spend in the last 30 days?" — a billing/audit blind spot called out in Dim 5 D5-06 but not fixed by anything in the Top-10 list.
5. **Auth blast radius.** Single shared password + tokens-never-expire means a single leak of `WR_SHARED_PASSWORD` requires rotating both that AND `WR_SESSION_SECRET` to fully invalidate sessions. Fix #5 (iat expiry) reduces the rotation window to 7 days, but doesn't eliminate it.
6. **Agent reliability.** Two of eight sub-agents made factually wrong claims (D7-01, D7-05). The evidence-bar verification process caught both, but a less-careful synthesis would have repeated them. Future audits should bake in a same-day verification step for any P0 claim.

---

## What's notably **not** broken (verified clean during this audit)

- SQL injection: no raw SQL with interpolation anywhere. SQLAlchemy ORM throughout (Dim 4).
- Cookie security flags (`httpOnly`, `sameSite`, conditional `secure`): correct (Dim 4).
- `normalizeNextPath` open-redirect protection: correct (Dim 4).
- Login route's empty-password guard: present (rejected agent's D7-05 claim).
- `.env.example` files: present (rejected agent's D7-01 claim).
- Tavily zero-result handling: graceful (Dim 4).
- USER_GUIDE.md feature claims: 100% verified against code (Dim 8).
- Migration chain integrity (for the tables that *do* have migrations): clean.
- Names and emails under gpt-4o-mini: high quality (Phase 2).

---

## Decision points for the user

1. **Vertical scope.** Commit to "VoIP/Telecom only" (preserve the bias as intentional) or commit to "vertical-agnostic" (strip the bias). The current code does the former; the docs and UI imply the latter. Ship the audit's recommendation: **strip the bias** and parameterize the prompt by query intent. Document via a new ADR.
2. **Ollama vs OpenAI in dev.** The `OPENAI_BASE_URL` to Ollama trick is fine for local dev (free), but it must be (a) explicit (commented in `.env.example`), (b) bypassed in CI/staging, and (c) verifiable at boot. Keep it as a documented dev-only override.
3. **Sprint reconciliation.** STATUS marks Sprints 1–4 done. After this audit, none are "done" by a definition that includes "works in a fresh deploy." Recommend: reframe STATUS to track completion against the new QA rubric (Dim 3), not just feature presence.
4. **External user pause.** The brief asked whether prior sprints need to be revisited. Recommendation: pause any external-user testing until Phase 1 of the action plan (P0s) lands. Internal dogfooding can continue as long as the Ollama + small-model variance is understood.

---

## Audit deliverable status

| Deliverable | Status |
|-------------|--------|
| 8 sub-reports in `audits/sub/0X-*.md` | ✅ all written, 2 corrections applied |
| Live integration tests with raw JSON | ✅ 4 queries, 12 leads, $0.045 spent |
| Lead quality matrix | ✅ `audits/raw/lead-quality-matrix.md` |
| Master audit report | ✅ this document |
| Action plan | → see [`docs/06-audit-action-plan.md`](../docs/06-audit-action-plan.md) |
| STATUS.md correction | → in progress |
