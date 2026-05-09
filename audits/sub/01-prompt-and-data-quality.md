# Dimension 1: Prompt & Data Quality

> **Status:** Historical Record. This document preserves evidence from the date it was written. Do not use it as the current work queue. Current product truth: `docs/00-product-northstar.md`; current state: `STATUS.md`; current rebuild execution: `docs/08-agentic-buildout-plan.md` and `docs/09-rebuild-phase-gates.md`.


**Auditor:** researcher subagent
**Date:** 2026-05-07
**Branch:** audit/hard-audit-2026-05-07
**Status:** Complete (read-only review — no live API calls)

---

## Executive verdict

The three production failures are **confirmed and root-caused** in the prompt and schema layer:

1. **VoIP hallucination** — SYSTEM_PROMPT explicitly tells the LLM it is "an expert B2B telecom lead researcher" finding "decision makers relevant to IT, Telecom, VoIP, and Networking." This applies to every query.
2. **Job titles as names** — `Lead.name` Field description says "First and last name" but no validation rejects titles, and the prompt gives no instruction to reject them.
3. **Fake `not_available@…` emails** — the prompt instructs the LLM to "deduce them based on common domain patterns" but `email_patterns.py` (the module that learns those patterns) is dead code, never imported.

White Rabbit v2 is working *exactly as designed* — for VoIP. The audit prompt's hypothesis (vertical bias hardcoded into the rewrite) is correct.

---

## Severity table

| ID | Title | Severity | File:line | Effort (human / AI) |
|----|-------|----------|-----------|---------------------|
| D1-01 | SYSTEM_PROMPT hardcodes VoIP/Telecom vertical | P0 | orchestrator.py:20–41 | 4h / 30min |
| D1-02 | Lead model field descriptions hardcode "VoIP sales" | P0 | models.py:21,23 | 1h / 10min |
| D1-03 | Prompt does not require name to be a real person | P0 | orchestrator.py:20–41 + models.py:8 | 1d / 1h |
| D1-04 | Prompt explicitly permits email hallucination | P0 | orchestrator.py:20–41 | 4h / 30min |
| D1-05 | Tavily `raw_content` not requested (regression vs proxy-lead) | P1 | search.py:68 | 1h / 15min |
| D1-06 | `email_patterns.py` is dead code; never imported | P1 | email_patterns.py (entire) | 1d / 2h |
| D1-07 | Prompt asks LLM to "deduce" emails with no pattern library passed in | P2 | orchestrator.py:20–41 | 4h / 30min |
| D1-08 | cost.py 2026 pricing | VERIFIED CLEAN | cost.py:4–5 | — |
| D1-09 | Query guardrails do not check vertical/domain | P2 | query_guardrails.py:10–45 | 4h / 1h |

**Counts:** P0 ×4, P1 ×2, P2 ×2, Verified ×1

---

## Findings

### D1-01: SYSTEM_PROMPT hardcodes VoIP/Telecom vertical [P0]

**Evidence (`packages/core/src/core/orchestrator.py:20–41`):**
> "You are an expert B2B telecom lead researcher. Your job is to parse the provided search results and extract decision makers relevant to IT, Telecom, VoIP, and Networking."

**Root cause:** The original `proxy-lead` Streamlit demo was built specifically for VoIP lead generation. When the rewrite landed, the vertical-specific prompt was copied verbatim into a system that's now positioned as vertical-agnostic.

**Why not caught:** Every QA run used the query `K-12 IT directors in Albuquerque` — a query whose vertical happens to align with the hidden bias, masking the issue. No test in the repo runs `scout()` with a non-IT/Telecom query.

**Fix:** Replace the role assertion with a query-derived persona. Either (a) parameterize the prompt with the user's query intent, or (b) drop the vertical assertion entirely and rely on search results to ground the LLM. Recommendation: (a) — pass the query into the system prompt and instruct the LLM to find decision makers relevant *to that query specifically*.

---

### D1-02: Lead model field descriptions hardcode "VoIP sales" [P0]

**Evidence (`packages/core/src/core/models.py:21, 23`):**
- `why_target`: `Field(description="1 sentence on why this role is good for VoIP sales")`
- `icebreaker`: `Field(description="one concrete reason a VoIP upgrade matters to them")`

**Root cause:** Same as D1-01 — vertical assumptions baked into the schema, not just the prompt. Pydantic Field descriptions are passed to OpenAI structured-output as part of the JSON schema, so the LLM sees these descriptions even if SYSTEM_PROMPT is fixed.

**Why not caught:** No test inspects the actual generated `why_target` / `icebreaker` text for vertical leakage. All test fixtures hardcode these fields with neutral text.

**Fix:** Rewrite descriptions to be vertical-agnostic. Example:
- `why_target`: `"1 sentence on why this role/organization fits the user's stated query intent"`
- `icebreaker`: `"one concrete, query-specific opener that references something true about the lead"`

---

### D1-03: Lead.name has no validation that it's a real person [P0]

**Evidence:**
- `models.py:8` — `name: str = Field(description="First and last name of the contact")` — description only, no validator.
- `orchestrator.py:20–41` SYSTEM_PROMPT contains no instruction to reject titles or generic role names.

**Root cause:** The schema *describes* the expected shape but doesn't *enforce* it. The LLM's structured output mode honors types but not natural-language Field descriptions strictly.

**Why not caught:** Every test uses `name="Jane Smith"` (verified across `test_orchestrator.py:24`, `test_models.py`, `test_api.py`, all web tests). Mock data is always shaped correctly, so validation gap is invisible.

**Fix:** Two layers.
1. Pydantic validator in `models.py`: reject single-word names, reject names containing role keywords (`director`, `manager`, `vp`, `chief`, `executive`, `coordinator`, etc.).
2. Add explicit instruction to SYSTEM_PROMPT: "The `name` field MUST be a real person's first and last name (e.g., 'Sarah Chen'). If you cannot find a real name in the search results for a contact, omit that contact entirely. Never put a job title or role description in the name field."

---

### D1-04: Prompt explicitly permits email hallucination [P0]

**Evidence (`orchestrator.py:20–41`):**
> "If emails are not fully visible, **deduce them** based on common domain patterns if possible"

**Root cause:** The original proxy-lead demo had this same instruction, but it was paired with the email_patterns.py module being actively called to *learn* domain patterns from real extracted leads — so "deduce" had context. In v2, email_patterns.py was lifted but never wired in, leaving the LLM with no pattern library and no recourse but to fabricate.

**Why not caught:** No test asserts `email != "not_available@*"`. No test compares email validity to email_status field.

**Fix (immediate):**
1. Replace "deduce them" with "If you cannot find an email in the search results, set `email = ""` and `email_status = \"Missing\"`. Never invent or guess an email."
2. Add a Pydantic validator to reject `not_available@*` and any email whose domain isn't present in any search result snippet.

**Fix (correct):** Re-wire email_patterns.py — see D1-06.

---

### D1-05: Tavily `raw_content` not requested (regression vs proxy-lead) [P1]

**Evidence (`search.py:68`):**
> `"include_raw_content": False,`

**proxy-lead reference (`proxy-lead/agent.py:91–92`):**
> conditionally passes `raw_content` if available from API

**Impact:** With `raw_content=False`, the LLM only sees Tavily's titles + ~250-char snippets. Real names and emails frequently live in the body of a page (executive bio paragraphs, contact pages). The current setup forces the LLM into hallucination territory because the data simply isn't in front of it.

**Fix:** Set `include_raw_content: True` in the Tavily request. Audit token cost — likely +30–60% per query — and budget for it.

---

### D1-06: `email_patterns.py` is dead code [P1]

**Evidence:**
- `packages/core/src/core/email_patterns.py:91` — `def infer_email_patterns(leads: Iterable[Lead | Mapping[str, Any]]) -> list[EmailPatternInsight]:` — full implementation present (132 lines).
- Grep `infer_email_patterns` across `packages/`, `apps/api/`, `apps/web/` — **0 import sites**.
- proxy-lead used it in `app.py` to feed learned patterns back into subsequent extractions.

**Root cause:** Module was lifted as a "code asset" but the integration glue was never built in v2. Classic rewrite mistake — vertical re-implementation, horizontal integration forgotten.

**Why not caught:** No integration test, no architectural check that all modules are imported somewhere.

**Fix:** Two paths.
- **Short-term:** Delete the module so it stops misleading auditors and contributors.
- **Long-term (recommended):** Hook it into `orchestrator.py` after a successful extraction — pass extracted leads with verified emails to `infer_email_patterns()`, store the resulting patterns per-domain, and inject them into the next prompt as a known-pattern hint.

---

### D1-07: Prompt asks LLM to "deduce" emails with no pattern library passed in [P2]

**Evidence:** Same as D1-04 + D1-06. Pairing them: the prompt tells the LLM to deduce, but no patterns are passed in the prompt context, so the LLM resorts to formulaic fakes (`{firstname}@{domain}`, `not_available@{domain}`, `info@{domain}`, etc.).

**Fix:** Rolled into D1-04 + D1-06.

---

### D1-08: cost.py 2026 pricing — VERIFIED CLEAN

**Evidence (`packages/core/src/core/cost.py:4–5`):**
- File header timestamps "2026-05" pricing.
- Numbers appear consistent with current Tavily + OpenAI rate cards.

**Caveat:** No automated check that pricing stays current. Recommend a calendar reminder or a CI check that flags pricing >12 months old.

---

### D1-09: Query guardrails do not check vertical/domain [P2]

**Evidence (`query_guardrails.py:10–45`):** Guardrails check for presence of role keywords, organization indicators, and locations. No check on whether the vertical implied by the query matches what the prompt was trained for.

**Impact:** A query like "CEOs in Texas" passes the guardrail but is then run through a VoIP-hardcoded prompt, producing nonsense.

**Fix:** Once the SYSTEM_PROMPT is parameterized (D1-01), this becomes moot. Until then, guardrails could surface a warning: "This query does not specify a vertical; results will reflect the system default (VoIP/Telecom)."

---

## Top-3 fixes (priority order)

1. **Rewrite SYSTEM_PROMPT to be query-driven, vertical-agnostic** (D1-01, D1-04). Single source of bias removal. ~30 minutes of careful prompt work.
2. **Rewrite Field descriptions in models.py** (D1-02). 10 minutes.
3. **Add Pydantic validators for name + email** (D1-03, D1-04). Belt-and-suspenders defense in case the prompt ever drifts again. 1 hour.

D1-05 (raw_content) and D1-06 (email_patterns wiring) are quality-of-extraction improvements that should follow but are not strictly required to ship a non-broken product.
