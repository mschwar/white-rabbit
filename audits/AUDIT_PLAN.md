# White Rabbit Hard Audit — Execution Plan

**Created:** 2026-05-07
**Source brief:** `audits/FRONTIER_AUDIT_PROMPT.md`
**Working directory:** `/Users/mschwar/Documents/white-rabbit`
**Reference codebase:** `/Users/mschwar/Documents/proxy-lead` (the original Streamlit demo this v2 was rewritten from)

---

## Premise

A real user hit three critical failures (VoIP-biased prompt, lead "names" that are titles, fake `not_available@…` emails) that survived 4+ sprints and multiple QA passes. Tests use mock leads; QA was UI-screenshot only; the LLM extraction path has never been independently verified. Treat *every* "done" claim as unverified.

The brief asks for an 8-dimension audit plus a master report and an action plan. This document is the execution plan to produce those deliverables.

---

## Reconnaissance facts (verified before planning)

These ground the plan and pre-empt errors in the original brief:

- **`packages/core/` is NOT testless.** It has `tests/test_models.py` (22 LOC), `tests/test_orchestrator.py` (154 LOC), `tests/test_query_guardrails.py` (30 LOC). The brief's "zero test files" assertion is wrong — but **all** of these tests use the same hand-crafted "Jane Smith" mock, so the *spirit* of the brief stands: zero tests exercise the real LLM extraction path. Audit must distinguish "tests exist" from "tests verify behavior."
- **`email_patterns.py` is dead code.** `infer_email_patterns` is defined at `packages/core/src/core/email_patterns.py:91` and imported by zero files in `packages/` or `apps/`. Confirmed via grep.
- **"Jane Smith" mock is pervasive.** Found in `apps/api/tests/test_api.py` (6 occurrences), `apps/web/src/app/api/scout/route.test.ts`, `apps/web/src/components/__tests__/scout-workspace.test.tsx`, `apps/web/src/lib/__tests__/full-export.test.ts`, `packages/core/tests/test_orchestrator.py`. Same fixture across all layers ⇒ no layer of the test pyramid catches extraction quality issues.
- **Surface area is small enough to read fully.** `packages/core/src/core/` is ~600 LOC across 6 modules. `apps/api/api/` is ~1100 LOC. `apps/web/src/` is bigger but bounded (~3 components, 11 API routes, ~6 tests). The full read mandated by the brief is feasible.
- **`proxy-lead/` at `/Users/mschwar/Documents/proxy-lead/`** has `agent.py` (5.8KB), `app.py` (32KB Streamlit), `models.py`, `email_patterns.py`, `export.py`, `history_store.py`, `bulk.py`, `demo_data.py`. The "what was lost" diff is doable.

---

## Phase 0 — Setup (locked 2026-05-07)

| Decision | Locked answer |
|---|---|
| Real-API budget | ✅ Approved (~$0.50–$2 for 4 queries + 1 Full run) |
| Branch | New branch `audit/hard-audit-2026-05-07`, cut from `feature/persisted-lead-ids` |
| Agent strategy | Full parallel — all 8 sub-audits delegated to read-only agents |
| Evidence bar | Reject thin reports; re-run agent with stricter quoting requirement |

**Locked test queries** (all phases use these strings verbatim):
- Q1: `Healthcare IT directors in Phoenix` — the failing query that triggered this audit
- Q2: `Financial services CISOs at mid-size banks in New York`
- Q3: `Manufacturing operations VPs in Detroit`
- Q4: `K-12 IT directors in Albuquerque` — the one that *appeared* to work; re-check under same scrutiny to test whether VoIP bias is systematic or vertical-leaked

**Phase 0 actions:**
1. `git checkout -b audit/hard-audit-2026-05-07`
2. Verify `TAVILY_API_KEY` and `OPENAI_API_KEY` are set and non-placeholder
3. Create `audits/sub/` and `audits/raw/` directories
4. Commit this plan doc to the new branch

---

## Phase 1 — Parallel sub-audits (≈2–3 hours wall, mostly agent time)

Eight dimensions, eight parallel agents. Each gets a self-contained brief, the relevant file list, and a fixed deliverable shape. Agents are read-only (Explore / researcher subagents) so they can run safely in parallel without write conflicts.

| # | Dimension                                | Agent type      | Primary inputs                                                                                                                        | Deliverable                                                                  |
|---|------------------------------------------|-----------------|---------------------------------------------------------------------------------------------------------------------------------------|------------------------------------------------------------------------------|
| 1 | Prompt & data quality                    | researcher      | `packages/core/src/core/orchestrator.py`, `models.py`, `search.py`; `proxy-lead/agent.py`, `proxy-lead/models.py`                     | `audits/sub/01-prompt-and-data-quality.md`                                   |
| 2 | Test coverage gaps                       | researcher      | All `tests/` dirs across the 3 packages; every `*.test.*` and `*.spec.*` in `apps/web`                                                | `audits/sub/02-test-coverage.md` (with gap matrix)                           |
| 3 | QA methodology failure                   | researcher      | `.gstack/qa-reports/*.md`, `.gstack/qa-reports/baseline.json`, screenshots dir                                                        | `audits/sub/03-qa-methodology.md`                                            |
| 4 | Code quality & architectural integrity   | code-reviewer   | `packages/core/src/core/*.py`, `apps/api/api/{main,db,models}.py`, alembic migrations, `apps/web/src/middleware.ts` if present        | `audits/sub/04-code-quality.md`                                              |
| 5 | Prompt drift from proxy-lead             | researcher      | Entire `/Users/mschwar/Documents/proxy-lead` tree; mirror modules in white-rabbit v2                                                  | `audits/sub/05-proxy-lead-diff.md` (side-by-side)                            |
| 6 | UI/UX & copy accuracy                    | researcher      | `apps/web/src/components/*.tsx`, `apps/web/src/app/**/page.tsx`, all user-facing strings                                              | `audits/sub/06-ui-copy.md`                                                   |
| 7 | Environment & deployment readiness       | researcher      | `.env.example`, `docker-compose.yml`, root `README.md`, alembic config, `apps/api/main.py`, `apps/web/next.config.*`                  | `audits/sub/07-deployment.md`                                                |
| 8 | Documentation drift                      | researcher      | `STATUS.md`, `AGENTS.md`, `docs/00..05-*.md`, `docs/USER_GUIDE.md`, `docs/reports/*`                                                  | `audits/sub/08-doc-drift.md`                                                 |

**Common deliverable shape (each sub-report MUST contain):**
- Severity table (P0/P1/P2/P3) with one row per finding.
- Each row: title, file path, line numbers, exact quote (copy-paste, not paraphrase), root cause hypothesis, remediation effort estimate (human-team / AI-assisted).
- "Why this wasn't caught" explanation.
- Top-3 recommended fixes for that dimension.

**Anti-pattern to avoid:** A sub-report that says "X is fine, no issues found" without evidence is rejected. Every section must cite either a finding or a verification step that ruled the area out. Negative-result reports are valuable but must be specific.

**Cross-agent note:** Dimension 1 and Dimension 5 will overlap on prompt content. Have Agent 1 own the *current state* and Agent 5 own the *diff*. Both are needed.

---

## Phase 2 — Live integration testing (45 min, sequential — needs main context)

This phase runs in the main context (not delegated) because results inform the final synthesis and need careful interpretation.

1. **Boot the stack locally.**
   - Postgres up, alembic migrations applied, FastAPI running, Next.js running.
   - If anything errors, that's a P0 finding for Dimension 7.
2. **Real `scout()` calls with the 4 locked queries from Phase 0.**
   - Capture full JSON response per query into `audits/raw/scout-Q{1..4}.json`.
   - For each lead returned, score it on a rubric:
     - Name field: real first+last name? title? generic? hallucinated?
     - Email: real-looking address? `not_available@…`? blank? plausible pattern?
     - Explanation: cites the query intent? mentions VoIP/telecom unprompted? hallucinated facts?
     - Source: matches a real Tavily result? fabricated URL?
   - Tabulate in `audits/raw/lead-quality-matrix.md`.
3. **Full flow end-to-end with one query.**
   - Run a Full run via the UI. Verify: recipe persisted, leads persisted with stable IDs (relevant to current `feature/persisted-lead-ids` branch), feedback buttons round-trip, recipe re-loadable.
   - Read back from the DB directly (`psql` or alembic shell) and confirm row counts, FK integrity, no NULLs in required fields.
4. **CSV export.**
   - Trigger the export. Open the CSV. Verify: headers, row count, no `not_available` strings, dates/timestamps formatted, escaping correct.
5. **Sandbox cap edge cases (recently merged in #11).**
   - Trigger cap exhaustion mid-run. Observe behavior. Reset. Confirm state.
6. **Auth bypass attempt.**
   - Try forging the auth cookie with a known-bad `WR_SHARED_PASSWORD` hash. Confirm middleware rejects.

All raw artifacts land in `audits/raw/`. Phase 3 cites them.

---

## Phase 3 — Synthesis (60 min, main context)

Aggregate the eight sub-reports + Phase 2 raw findings into:

### 3a. Master audit report
**Path:** `audits/hard-audit-2026-05-07.md`
**Sections:**
1. **Executive summary** — one paragraph: "If we shipped this today, here's what would happen." Brutally specific.
2. **Top 10 blockers** — ranked by user impact, each with file:line reference and 1-line fix.
3. **Per-dimension findings** — links to the eight sub-reports with a 3-line summary each. No content duplication.
4. **Cross-cutting themes** — patterns that span dimensions (e.g., "every layer trusts the layer below it").
5. **Risk register** — what could still be wrong even after all the above is fixed.

### 3b. Action plan
**Path:** `docs/06-audit-action-plan.md`
**Structure:**
- **Phase 1 (must-fix-now, blocks any further user testing)** — P0s only, ordered by dependency.
- **Phase 2 (before any external user, including pilot)** — P1s.
- **Phase 3 (polish, can ship without)** — P2/P3.
- Each item: title, owner placeholder, effort (human + AI), success criteria, sign-off check.

### 3c. STATUS.md correction
**Path:** `STATUS.md`
- For every "done" claim contradicted by audit findings, mark `⚠️ AUDIT FAILED — see audits/hard-audit-2026-05-07.md#…` and explain in one line.
- Add an "Audit reality" section at the top.
- Do not delete the original "done" history — strikethrough it so the regression is visible.

### 3d. Sprint reconciliation decision
- For each completed sprint, decide: clean / needs-rework / needs-redo.
- Document at the bottom of `docs/06-audit-action-plan.md`.

---

## Phase 4 — Decision gate (you, not me)

I produce the four artifacts above and stop. Before any remediation work begins, you decide:

- Accept the action plan as written? Re-prioritize?
- Pause feature/persisted-lead-ids work to focus on P0s?
- Roll back to a known-good commit? (This audit may surface that the answer is yes.)
- Bring in a second reviewer (e.g., Codex consult) on the master report?

---

## Time & cost estimate

| Phase | Wall time | Active assistant time | API cost  |
|-------|-----------|-----------------------|-----------|
| 0     | 15 min    | 15 min                | $0        |
| 1     | 2–3 hr    | ~30 min (agent dispatch + review)| $0 (read-only)        |
| 2     | 45 min    | 45 min                | $0.50–$2  |
| 3     | 60 min    | 60 min                | $0        |
| **Total** | **~4–5 hr** | **~2.5 hr** | **<$2** |

Compression vs. a human team doing this by hand: ~10–15x. (Per CLAUDE.md effort calibration: this is "architecture/design" tier work, not boilerplate.)

---

## Risks & failure modes for the audit itself

- **Agent confabulation.** A sub-agent that hits a long file may summarize instead of quoting. Mitigation: every finding requires a copy-pasted quote — reports without quotes get rejected and re-run.
- **Anchor bias from the brief.** The brief is opinionated about VoIP bias. Agents may rubber-stamp that finding instead of independently verifying. Mitigation: Phase 2 runs a non-VoIP-aligned query (Q4 Albuquerque) under the same scrutiny to test whether the bias is *systematic* or *prompt-leaked-by-vertical*.
- **Real-API flakiness.** Tavily/OpenAI may rate-limit or return degraded results during the audit window. Mitigation: capture raw JSON; if a run looks anomalous, re-run once; document if results vary.
- **Scope creep.** The audit could become a rewrite. Mitigation: this plan ends at the action plan. Remediation is a separate engagement requiring its own approval.

---

## Out of scope for this audit

- Fixing anything. This is read-and-report only.
- Performance benchmarking beyond cost-per-query observation.
- Security pentesting beyond the auth bypass spot-check in Phase 2.
- Refactoring suggestions that don't tie to a finding.
- Anything in `.gemini/superskills-repo/` (vendored skills, not product code).

---

## Deliverable checklist (success criteria)

- [ ] `audits/sub/01-prompt-and-data-quality.md`
- [ ] `audits/sub/02-test-coverage.md`
- [ ] `audits/sub/03-qa-methodology.md`
- [ ] `audits/sub/04-code-quality.md`
- [ ] `audits/sub/05-proxy-lead-diff.md`
- [ ] `audits/sub/06-ui-copy.md`
- [ ] `audits/sub/07-deployment.md`
- [ ] `audits/sub/08-doc-drift.md`
- [ ] `audits/raw/scout-Q1.json` … `scout-Q4.json`
- [ ] `audits/raw/lead-quality-matrix.md`
- [ ] `audits/hard-audit-2026-05-07.md`
- [ ] `docs/06-audit-action-plan.md`
- [ ] `STATUS.md` updated with audit-reality section
