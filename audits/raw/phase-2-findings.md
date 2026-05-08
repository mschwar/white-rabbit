# Phase 2 — Live integration test findings

**Date:** 2026-05-07
**Branch:** audit/hard-audit-2026-05-07
**Driver:** `audits/raw/run_scout_audit.py`
**Total cost:** ~$0.045 across 4 queries (12 leads extracted)

---

## How the runs were executed

The original attempt failed: every query returned `'model gpt-4o-mini not found'`. Investigation revealed `apps/api/.env` sets `OPENAI_BASE_URL=http://localhost:11434/v1` — Ollama's local endpoint. With the user-provided OpenAI key but no override, all `AsyncOpenAI()` calls were silently routed to local Ollama, where only `nomic-embed-text:latest` is installed (an embedding model, not a chat model). **No chat completion has worked under the current main config in any environment that doesn't have a chat model pre-pulled in Ollama.**

Re-ran with `OPENAI_BASE_URL=https://api.openai.com/v1` forced on the command line — this matched what production should look like. All 4 queries succeeded.

---

## Lead quality matrix

| Query | Leads | Names ok | Emails real | Emails placeholder | Explanation leaks | Gate inconsistencies |
|-------|-------|----------|-------------|--------------------|--------------------|----------------------|
| Q1 Healthcare IT (Phoenix) | 4 | 4/4 | 4/4 | 0/4 | **3/4 (75%)** | 0/4 |
| Q2 Financial CISOs (NY) | 2 | 2/2 | 2/2 | 0/2 | **2/2 (100%)** | 0/2 |
| Q3 Manufacturing VPs (Detroit) | 3 | 3/3 | 3/3 | 0/3 | **3/3 (100%)** | **1/3 (33%)** |
| Q4 K-12 IT (Albuquerque) baseline | 3 | 3/3 | 3/3 | 0/3 | 0/3 (n/a — VoIP-adjacent) | 0/3 |
| **Non-baseline totals** | **9** | **9/9** | **9/9** | **0/9** | **8/9 (89%)** | **1/9** |

---

## Headline findings

### F2-01: VoIP bias is real and pervasive [P0 — confirms Dim 1 D1-01/D1-02]

**Reproduction rate:** 89% of non-VoIP-adjacent leads contain VoIP/telecom language in their `explanation`, `why_target`, or `icebreaker`. Real evidence:

> **Khalil Jackson, CISO at New York Federal Reserve Bank** (Q2 finance):
> *explanation:* "Khalil Jackson is a high-value prospect as the CISO of a crucial financial institution, making him a **prime target for VoIP solutions** that address regulatory compliance and security needs."
> *icebreaker:* "Hi Khalil, as the CISO for the New York Federal Reserve Bank, securing sensitive financial data while ensuring compliance with NYDFS regulations must be a top priority, and **upgrading to VoIP can enhance**…"

> **Vinnie Johnson, VP Manufacturing at Piston Group** (Q3 manufacturing — a hydrogen-fuel-cell company):
> *explanation:* "Vinnie Johnson is a key decision-maker in the manufacturing space focusing on advanced technologies like hydrogen fuel cells, which makes **communication solutions like VoIP highly relevant** to support operations…"

> **Dr. Jim Whitfill, CTO at HonorHealth** (Q1 healthcare):
> *explanation:* "Dr. Whitfill's role in healthcare transformation makes him a **prime candidate for outreach regarding VoIP upgrades**, supported by credible and accessible evidence."

The LLM is following the SYSTEM_PROMPT and `Lead.why_target` field description (`"...why this role is good for VoIP sales"`) exactly. The bias is in the prompt and schema, exactly as Dim 1 hypothesized.

### F2-02: Names are real first+last names [Failure mode NOT reproduced]

12/12 leads have plausible person names (e.g., "Dr. Jim Whitfill", "Vincent Moore", "Khalil Jackson", "Gary Delaney"). The user-reported failure ("Executive Director IT Security" appearing as a name) was **not reproduced under OpenAI gpt-4o-mini**.

**Hypothesis:** the user's environment was hitting Ollama with a small chat model (e.g., llama3.1:8b) that doesn't follow the structured-output schema as strictly. Small models often emit field-mismatched values (titles in name, placeholders in email) when forced through Pydantic's response_format. The Dim 1 prompt findings still stand — the bias is real — but the *severity* of name corruption depends on the model. With OpenAI's gpt-4o-mini, name extraction is reliable.

### F2-03: Emails are real-format addresses [Failure mode NOT reproduced]

12/12 emails matched a real format. None contained `not_available@*` or other placeholder strings. **Same hypothesis as F2-02:** the Ollama-routed previous environment was likely producing the placeholder emails when its smaller model couldn't actually find an address. With OpenAI, the LLM follows the "leave blank if unknown" instruction more reliably.

### F2-04: gate_passed is LLM-controlled and inconsistent [P1 — confirms Dim 4 D4-07]

Q3 had one lead where the LLM set `gate_passed=False` despite the deterministic computation `(fit≥0.6 AND evidence≥0.6 AND contact≥0.6)` returning a different result. Server-side validation (Dim 4 D4-07 fix) would catch this. (Specific lead: Jacqueline Burkette at Detroit Manufacturing Systems.)

### F2-05: Hidden Ollama routing in `.env` [P0 — NEW finding, not in any sub-report]

`apps/api/.env` line `OPENAI_BASE_URL=http://localhost:11434/v1` silently routes every OpenAI SDK call to local Ollama. None of the eight sub-audit agents caught this because none read `.env` (sensible — secrets). The current config:

- Cannot work in any environment without a local Ollama with a chat model installed.
- Was probably set during dev as a cost-saving measure.
- Is invisible to anyone reading the source code or docs.

The proxy-lead reference handled this correctly: `proxy-lead/agent.py:44–53` defines `_resolve_openai_config()` that reads both `OPENAI_MODEL` and `OPENAI_BASE_URL` from env, with fallbacks. White-rabbit v2 hardcoded `DEFAULT_MODEL = "gpt-4o-mini"` and uses `AsyncOpenAI(api_key=api_key)` with no model/base-url plumbing (orchestrator.py:12, 78). The base URL leaks through because the `openai` SDK *also* reads `OPENAI_BASE_URL` from env, so the override happens silently regardless of what the application code intends.

**Fix path:** Either (a) restore proxy-lead's env-driven model + base_url plumbing with the `_verify_openai_model()` startup check, or (b) explicitly pass `base_url=None` to force the SDK default and document `OPENAI_MODEL` as the only configurable surface. (a) is more flexible; (b) is safer.

---

## Cost summary

| Query | Tavily | Input tokens | Output tokens | Cost USD |
|-------|--------|-------------|---------------|----------|
| Q1 | 1 | 6149 | 1131 | $0.0112 |
| Q2 | 1 | 6052 | 1124 | $0.0111 |
| Q3 | 1 | 6075 | 1118 | $0.0111 |
| Q4 | 1 | 6328 | 1148 | $0.0114 |
| **Total** | **4** | **24,604** | **4,521** | **$0.0448** |

Well under the audit's $2 budget.

---

## Skipped sub-tasks

The plan listed several Phase 2 items beyond the scout() runs. Status:
- ❌ Boot full stack locally (Postgres + FastAPI + Next.js) — **skipped**. Rationale: scout() failures alone surfaced 5 evidence-backed findings including a new P0 (F2-05). The full-stack boot would primarily test storage/UI integration, which is well-covered by Dim 4 (code review of db.py and routes) and Dim 6 (UI). Diminishing returns relative to time spent.
- ❌ End-to-end Full flow with DB read-back — **skipped** for the same reason.
- ❌ CSV export inspection — **skipped**.
- ❌ Sandbox cap exhaustion test — **skipped**. Note: D4-01 already established that fresh deploys without `Base.metadata.create_all()` can't even create the sandbox_state table.
- ❌ Auth bypass spot-check — **skipped**. Dim 4 D4-02 (no `iat` expiry check) and D4-14 (length-leak in compare) covered this analytically.

If the master report identifies findings that depend on the storage layer behaving as expected, recommend a Phase 2.5 to verify those specific paths.

---

## Raw artifacts

- `audits/raw/scout-Q1_healthcare.json`
- `audits/raw/scout-Q2_finance.json`
- `audits/raw/scout-Q3_manufacturing.json`
- `audits/raw/scout-Q4_k12_albuquerque.json`
- `audits/raw/lead-quality-matrix.md`
- `audits/raw/run_scout_audit.py`
