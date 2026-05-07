# WHILE-RABBIT HARD AUDIT — FRONTIER AGENT PROMPT

**Context:** You are conducting a ground-up, zero-trust audit of the White Rabbit v2 codebase. A real user just started testing the product and immediately hit three critical failures that survived 4+ sprints of development and multiple QA passes:

1. The system prompt is hard-coded for VoIP/telecom, causing hallucinated relevance for any non-VoIP query (e.g., "Healthcare IT directors in Phoenix" returned VoIP-themed explanations and icebreakers).
2. Lead "names" are actually just job titles (e.g., "Executive Director IT Security") — no actual person names were extracted.
3. Emails are fake (`not_available@valleywisehealth.com`) despite an `email_patterns.py` module existing in the repo but never being called.

These are DATA QUALITY failures, not UI bugs. Every prior QA pass used UI-level screenshot comparison and the same test query ("K-12 IT directors in Albuquerque"), which happened to align with the hidden VoIP bias. The tests use hand-crafted mock leads ("Jane Smith") that never exercise the real LLM extraction path. The core `packages/core/` directory has zero test files.

Your job is to find EVERYTHING else that is broken, half-built, misleading, architecturally unsound, or simply not production-ready. Do not assume any component works. Do not trust STATUS.md, docs, or prior QA reports. Verify everything.

---

## AUDIT SCOPE

Audit the following dimensions in this order. For each dimension, produce:
- A severity rating (P0 = ship-blocking, P1 = major flaw, P2 = misleading/confusing, P3 = cleanup)
- Concrete evidence (file paths, line numbers, exact quotes)
- Root cause analysis (why this wasn't caught before)
- A remediation plan (what to fix, in what order, with estimated effort)

### DIMENSION 1: DATA QUALITY & PROMPT ENGINEERING (CRITICAL)

The prompt → LLM → data pipeline is the PRODUCT. If this is wrong, nothing else matters.

- [ ] Read `packages/core/src/core/orchestrator.py` SYSTEM_PROMPT line by line. Is it query-agnostic or does it hardcode assumptions about product, industry, or use case?
- [ ] Read `packages/core/src/core/models.py`. Do field descriptions contain hidden assumptions (e.g., "why this role is good for VoIP sales")? Are there fields that don't match what the UI displays?
- [ ] Is the prompt actually testing Tavily results for real names, or is it allowing hallucination? Does it instruct the LLM to source every claim from the provided search results?
- [ ] Is `email_patterns.py` actually imported and used anywhere? (HINT: grep the repo for `infer_email_patterns` and `email_patterns`). If not, why not?
- [ ] Is there prompt drift between `proxy-lead/agent.py` (the original working demo) and `packages/core/src/core/orchestrator.py` (the rewrite)? List every instruction that was lost during the LangChain → OpenAI SDK rewrite.
- [ ] Does the prompt request `raw_content` from Tavily? If not, is the LLM being asked to extract leads from just titles and snippets?
- [ ] Does the prompt specify that `name` MUST be a real person's first and last name, not a job title or generic descriptor?
- [ ] Test extraction manually: run the actual `scout()` function with 3 diverse queries (healthcare IT, financial services, manufacturing) and inspect every field of every lead for hallucination, bias, and quality.

**Deliverable:** Prompt audit report with before/after prompt comparison, plus a corrected prompt specification.

### DIMENSION 2: TEST COVERAGE & VERIFICATION GAPS (CRITICAL)

Every test in the repo is a UI/API integration test using mock data. Zero tests verify that the LLM extraction pipeline produces real, high-quality leads.

- [ ] `packages/core/` has test directory stubs but no actual tests. List every file that should have tests but doesn't.
- [ ] `apps/api/tests/test_api.py` uses `fake_scout` that returns hand-crafted `Lead` objects. Does any test call the real `scout()` function with real API keys?
- [ ] Are there property-based tests or contract tests for `Lead` schema validation?
- [ ] Is there any test that asserts "returned lead names contain a first name and last name, not a title"?
- [ ] Is there any test that asserts "email is either a real address or blank, never `not_available@domain.com`"?
- [ ] Is there any test that runs the same query twice and asserts consistency?
- [ ] Are there tests for error branches: Tavily returns zero results, Tavily returns garbage, OpenAI returns malformed JSON, OpenAI refuses, missing API keys, rate limits?
- [ ] Read every test file in `apps/web/src/components/__tests__/`, `apps/web/src/lib/__tests__/`, `apps/web/src/app/api/*/route.test.ts`. Are they testing UI rendering with fake data, or actual data quality? Do any test the real API integration?
- [ ] Is there a contract test between what `orchestrator.py` returns and what `scout-workspace.tsx` expects?
- [ ] What unit tests are missing from the FastAPI layer? Test CRUD operations on recipes, runs, leads, feedback. Test sandbox cap enforcement edge cases.

**Deliverable:** Test gap analysis with a table of "What exists / What's missing / Priority / What to test for". Plus a concrete test plan with exact test cases to write.

### DIMENSION 3: QA METHODOLOGY FAILURE (CRITICAL)

The current QA process validated "does the page render?" not "does the product actually work?"

- [ ] Read every file in `.gstack/qa-reports/`. What exactly was tested? What questions were asked? What assertions were made?
- [ ] Is there any QA report that tested a query OTHER than "K-12 IT directors in Albuquerque"?
- [ ] Is there any QA report that inspected lead card CONTENT (names, emails, explanations) for correctness? Or only counted lead cards?
- [ ] Is there any QA report that tested the Full run pipeline end-to-end with real storage, then read back the recipe and verified data integrity?
- [ ] Is there a QA checklist or rubric that defines "good enough to ship" for data quality?
- [ ] Are there visual regression tests, screenshot baselines, or any automated checks that would catch prompt drift?
- [ ] Does the `gstack` QA skill have a mode for testing data quality, or only UI/functional QA?

**Deliverable:** QA methodology failure analysis + a new QA rubric that includes data quality gates, prompt validation tests, and multi-vertical query testing.

### DIMENSION 4: CODE QUALITY & ARCHITECTURAL INTEGRITY

- [ ] Read every file in `packages/core/src/core/`. Is each module doing one thing well? Are there circular dependencies?
- [ ] Is `cost.py` using accurate 2026 pricing? Where did the numbers come from? Are they documented?
- [ ] Is the `search.py` `_clean_results` function stripping useful context? Does it include `raw_content` from Tavily? If not, the LLM has very little to work with.
- [ ] Does `orchestrator.py` handle the case where Tavily returns fewer results than requested? Does it warn the user or just silently under-deliver?
- [ ] Is there retry logic for Tavily timeouts? For OpenAI rate limits?
- [ ] Is the `gate_passed` logic configurable or hardcoded to `0.6`? Where does `0.6` come from?
- [ ] Are database models in `apps/api/api/db.py` or wherever they live correctly typed? Any `Any` types or untyped columns that could cause data loss?
- [ ] Is Alembic migration wired correctly? Would a fresh deploy create the right schema?
- [ ] Are there SQL injection risks in the FastAPI layer?
- [ ] Is the Next.js middleware auth actually secure? Could someone bypass it with a forged cookie?
- [ ] Is `WR_SHARED_PASSWORD` in `.env.local` committed or in `.gitignore`? What's the blast radius if it leaks?

**Deliverable:** Code quality audit report with per-file findings and architectural recommendations.

### DIMENSION 5: PROMPT DRIFT FROM PROXY-LEAD (REFERENCE CHECK)

The original `proxy-lead` demo at `/Users/mschwar/Documents/proxy-lead` was functional for its use case. White Rabbit v2 was a "rewrite" that appears to have lost instructions during the LangChain → OpenAI SDK port.

- [ ] Read `proxy-lead/agent.py` entirely. Extract the exact prompt text.
- [ ] Read `proxy-lead/models.py`. Compare every field and description to `packages/core/src/core/models.py`.
- [ ] Read `proxy-lead/app.py`. What did the original Streamlit UI promise vs. what the Next.js UI promises? Are expectations aligned?
- [ ] Read `proxy-lead/export.py`. What export formats existed? Are they ported?
- [ ] Read `proxy-lead/history_store.py`. What cost tracking did it do? Is that replicated?
- [ ] What other files in `proxy-lead` contain logic that should have been lifted but wasn't?

**Deliverable:** Detailed diff/spec comparison between proxy-lead and white-rabbit, listing everything that was lost, changed, or degraded.

### DIMENSION 6: UI/UX & COPY ACCURACY

- [ ] Read `apps/web/src/components/scout-workspace.tsx`. Does the description text match reality? (e.g., "Scout: quick preview (10-20 leads)" — is 3 leads "10-20"?)
- [ ] Is the placeholder query "K-12 IT directors in Albuquerque" teaching users to use a query that happens to work with the VoIP bias?
- [ ] Do error messages actually explain what went wrong, or are they generic?
- [ ] Does the "Query could be tighter" warning provide actionable advice?
- [ ] Are buttons and labels accurate? E.g., does "Run Scout search" actually run a scout search or does it also extract, score, and format?
- [ ] Are there dead links, 404s, or unimplemented features exposed in the UI?
- [ ] Does the recipe library show meaningful data? What does it show when there are zero recipes?
- [ ] Does the batch workspace handle errors gracefully? What happens when the sandbox caps are hit mid-batch?

**Deliverable:** UI/UX accuracy report with specific copy changes needed.

### DIMENSION 7: ENVIRONMENT & DEPLOYMENT READINESS

- [ ] Are `.env.example` files complete and accurate? Do they include every required variable?
- [ ] What happens if an env var is missing? Does the app crash with a clear message or fail silently?
- [ ] Is PostgreSQL required? What happens if it's not running?
- [ ] Are there Dockerfiles, docker-compose files, or deployment configs? Are they up to date?
- [ ] Are there any hardcoded localhost URLs that would break in production?
- [ ] Is there a README with setup instructions that actually work? Test the setup from scratch.
- [ ] Are there any dependency version conflicts or security vulnerabilities?

**Deliverable:** Deployment readiness checklist and gap analysis.

### DIMENSION 8: DOCUMENTATION DRIFT

- [ ] Read `docs/03-decisions.md`. Are the decisions still accurate, or has the code diverged?
- [ ] Read `docs/01-model.md`. Does the "operator model, recipes, score model, run model" match the actual implementation?
- [ ] Read `docs/04-roadmap.md`. Are "completed" items actually complete and working?
- [ ] Read `docs/05-reuse.md`. Was everything that was supposed to be lifted actually lifted correctly?
- [ ] Is `STATUS.md` truthful, or does it claim things are done that are broken?
- [ ] Is there any mismatched ADR that documents a decision but the code does the opposite?

**Deliverable:** Documentation accuracy report listing every inconsistency with file/line references.

---

## AUDIT WORKFLOW

1. **Start by reading the entire repo.** Read `AGENTS.md`, `STATUS.md`, every doc in `docs/`, every source file in `packages/core/`, `apps/api/`, `apps/web/src/`. Do not skip files. Take notes.

2. **For each dimension above, produce a sub-report.** Each sub-report must include:
   - Severity ratings for every finding
   - File paths and line numbers
   - Exact quotes from the code (copy-paste, don't paraphrase)
   - A remediation plan with estimated effort and priority order

3. **Run actual integration tests.** Do not rely on existing tests — they use mocks. Instead:
   - Run `scout()` with real API keys and 3 diverse queries
   - Inspect every lead field
   - Run a Full flow end-to-end
   - Export a recipe and read it back
   - Verify the CSV export format

4. **Produce a master audit report** at `/Users/mschwar/Documents/white-rabbit/audits/hard-audit-YYYY-MM-DD.md` with:
   - Executive summary: "If we shipped this today, what would happen?"
   - Top 10 blockers ranked by user impact
   - Per-dimension detailed findings
   - Remediation roadmap (Phase 1 = must-fix-now, Phase 2 = before-any-external-user, Phase 3 = polish)

5. **Produce a `docs/06-audit-action-plan.md`** that is the authoritative source for what gets fixed next. This replaces or supplements the current roadmap.

6. **Update `STATUS.md`** to reflect the audit reality. If something was marked "done" but is actually broken, mark it as such and explain why.

---

## AUDIT PRINCIPLES

- **Assume nothing works until proven otherwise.** The prompt quality failure proves that passing tests and QA screenshots mean nothing for data quality.
- **Read the code, don't trust the docs.** STATUS.md says things are done. Prove it or flag it.
- **Test with real data, not mocks.** A test that passes with `fake_scout` tells you nothing about production behavior.
- **Distinguish UI bugs from data quality bugs.** A page rendering 5 lead cards is a UI success. Those 5 leads containing fake names, wrong explanations, and missing emails is a product failure.
- **Compare to the original.** The `proxy-lead` demo worked for its scope. If white-rabbit v2 is worse in any dimension, that's a regression.
- **Be brutal but constructive.** Every finding needs a clear fix.

---

## SUCCESS CRITERIA

This audit is complete when:
1. Every file in the repo has been read by you at least once.
2. Every dimension above has a dedicated, detailed sub-report.
3. You have manually tested the real extraction pipeline with ≥3 diverse queries.
4. A master audit report exists in the repo.
5. An action plan exists with clear priorities and owner assignments.
6. STATUS.md is updated to reflect reality.
7. A decision is documented on whether any prior "completed" sprints need to be revisited.

---

**Start now. Do not skip steps. Do not assume. Verify everything.**
