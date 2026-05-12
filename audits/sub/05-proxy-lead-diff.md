# Dimension 5: Drift From proxy-lead Reference

> **Status:** Historical Record. This document preserves evidence from the date it was written. Do not use it as the current work queue. Current product truth: `docs/00-product-northstar.md`; current state: `STATUS.md`; current reset execution: `docs/12-reset-gated-implementation-plan-2026-05-10.md`.


**Auditor:** researcher subagent
**Date:** 2026-05-07
**Branch:** audit/hard-audit-2026-05-07
**Status:** Complete (read-only side-by-side comparison)

---

## Executive verdict

White Rabbit v2 preserved most of the *fields* from proxy-lead but lost critical *instructions* in the SYSTEM_PROMPT and dropped two integrations that gave the original its quality signal: `email_patterns.py` (now dead code) and the SQLite history store (cost ledger). The 05-reuse.md doc is partially accurate — modules were "lifted" as code copies but not actually wired in.

The vertical bias in v2 (VoIP/Telecom) was inherited from proxy-lead. proxy-lead was *intentionally* a VoIP demo. The regression is not that v2 has VoIP language — it's that v2 *positions itself* as vertical-agnostic while keeping the VoIP language verbatim.

---

## Side-by-side: System prompt

### `proxy-lead/agent.py:30–33`

> "You are an expert B2B telecom lead researcher. Your job is to parse the provided search results and extract decision makers relevant to IT, Telecom, VoIP, and Networking. **Include the organization name for every lead.** If emails are not fully visible, deduce them based on company domain patterns if possible, or leave blank. Set email_status to Found, Deduced, or Missing. **Set source_url to the strongest URL from the provided results that supports the lead. Set confidence from 0.0 to 1.0 based on how directly the source supports the contact and email.** For each lead, write a specific 1-sentence cold email opener referencing their job title, their organization type (school district / government / SMB), and one concrete reason a VoIP upgrade matters to them specifically. Make it feel like homework was done, not a template."

### `white-rabbit/orchestrator.py:20–41`

> "You are an expert B2B telecom lead researcher. Your job is to parse the provided search results and extract decision makers relevant to IT, Telecom, VoIP, and Networking.
>
> SCORING GUIDELINES:
> - fit_score: 0.0 to 1.0. How well does this person/org match a high-value VoIP prospect?
> - evidence_score: 0.0 to 1.0. How current and direct is the source evidence?
> - contact_score: 0.0 to 1.0. How usable is the email/phone/title?
>
> GATE LOGIC:
> Set gate_passed = True if fit, evidence, and contact scores are all >= 0.6.
>
> EMAIL DEDUCTION:
> If emails are not fully visible, deduce them based on common domain patterns if possible.
> Set email_status to Found, Deduced, or Missing.
>
> CONTENT:
> For each lead, write a specific 1-sentence cold email opener referencing their job title, their organization type (school district / government / SMB), and one concrete reason a VoIP upgrade matters to them specifically. Make it feel like homework was done.
> Include a human-readable explanation of your ranking in the 'explanation' field."

### Lost instructions (every line that disappeared)

| Lost instruction | Impact |
|------------------|--------|
| "Include the organization name for every lead." | LLM may emit leads with empty `organization`. |
| "Set source_url to the strongest URL from the provided results that supports the lead." | LLM has no ranking instruction; may pick the first URL or hallucinate. |
| "Set confidence from 0.0 to 1.0 based on how directly the source supports the contact and email." | Replaced by 3 separate scores (fit/evidence/contact). The `confidence` field is still in the schema (marked "DEPRECATED") but no longer set with semantic meaning. |

### New in v2 (additions, not regressions)

- 3 sub-scores (fit, evidence, contact) with thresholds.
- `gate_passed` boolean.
- `explanation` field for human-readable ranking commentary.

---

## Side-by-side: Lead model fields

| Field | proxy-lead description | v2 description | Drift? |
|-------|------------------------|----------------|--------|
| `name` | "First and last name of the contact" | "First and last name of the contact" | None |
| `title` | "Job title" | "Job title" | None |
| `organization` | "Organization, district, agency, or company name" | "Organization, district, agency, or company name" | None |
| `email` | "Professional email address, or blank if unavailable" | "Professional email address, or blank if unavailable" | None |
| `email_status` | "Email evidence status: Found, Deduced, or Missing" | "Email evidence status: Found, Deduced, or Missing" | None |
| `source_url` | "Best source URL supporting the contact, title, or email" | "Best source URL supporting the contact, title, or email" | None |
| `confidence` | "Confidence score from 0.0 to 1.0 based on source strength" | "DEPRECATED: Confidence score from 0.0 to 1.0 based on source strength. Use scores instead." | Marked deprecated but kept |
| `why_target` | "1 sentence on why this role is good for VoIP sales" | "1 sentence on why this role is good for VoIP sales" | **None — and that's the bug.** |
| `icebreaker` | "...one concrete reason a VoIP upgrade matters to them" | "...one concrete reason a VoIP upgrade matters to them" | **None — and that's the bug.** |
| `fit_score` | n/a | "0.0 to 1.0" | NEW |
| `evidence_score` | n/a | "0.0 to 1.0" | NEW |
| `contact_score` | n/a | "0.0 to 1.0" | NEW |
| `gate_passed` | n/a | bool | NEW |
| `explanation` | n/a | str | NEW |

The vertical-bias bug isn't a drift — the descriptions are identical to proxy-lead. The issue is that proxy-lead was *meant* to be VoIP-only; v2 inherited VoIP language while claiming to be vertical-agnostic. (Cross-references Dim 1.)

---

## Module-by-module comparison

| Module | Did in proxy-lead | Replaced (or dropped) in v2 | Severity |
|--------|-------------------|----------------------------|----------|
| `agent.py` | LangChain orchestration: Tavily → ChatOpenAI → LeadList | `orchestrator.py`: OpenAI SDK async, prompt simplified, scoring split into 3 sub-scores | P0 (instructions lost — see "Lost instructions" above) |
| `models.py` | Lead + LeadList | Lead + LeadList + scoring fields; old `confidence` deprecated but retained | P1 (deprecation without migration path) |
| `email_patterns.py` | Inferred patterns from leads, surfaced in UI as QA signal | **Identical code copy. Never imported.** | P1 (dead code; QA signal lost) |
| `export.py` | HubSpot CSV with `First Name` + `Last Name` split, honorific-aware | `apps/web/src/lib/full-export.ts`: single `name` column, more metadata columns | P2 (gain: metadata. loss: CRM-friendly name split) |
| `history_store.py` | SQLite ledger with per-search cost, `list_recent_searches()`, `load_search()`, per-user attribution | `cost.py`: estimation only, no persistence, no history APIs | P1 (no billing/audit ledger) |
| `bulk.py` | Sequential batch with per-query error capture, all-queries-tried | `apps/api/api/main.py /batch`: stops on cap; failure halts remainder | P1 (different failure semantics) |
| `config.py` | Streamlit secrets + bcrypt + auth fallbacks | Not lifted (web auth handled differently) | n/a (intentional) |
| `logger.py` | File + stderr + optional Supabase mirror | Not lifted (stdlib logging in API/web) | n/a (intentional) |

---

## Severity table

| ID | Regression | Severity | File:line | Effort |
|----|-----------|----------|-----------|--------|
| D5-01 | Lost "include organization for every lead" instruction | P0 | proxy-lead/agent.py:30–33 vs orchestrator.py:20–41 | 2min |
| D5-02 | Lost "source_url to strongest URL" ranking | P0 | proxy-lead/agent.py:30–33 vs orchestrator.py:20–41 | 3min |
| D5-03 | `confidence` deprecated without migration path; still exported | P1 | models.py:16–20 + full-export.ts:17 | 15min |
| D5-04 | `email_patterns.py` is dead code | P1 | white-rabbit/email_patterns.py (entire file unused) | 30min (integrate) or 5min (delete) |
| D5-05 | Search history APIs removed (`list_recent_searches`, `load_search`) | P1 | proxy-lead/history_store.py:160–239 (no v2 equivalent) | 45min |
| D5-06 | No persistent cost ledger | P1 | proxy-lead/history_store.py:93–115 vs cost.py:35–54 | 1–2h |
| D5-07 | Bulk failure semantics changed (stops on cap vs tries all) | P1 | proxy-lead/bulk.py:65–145 vs main.py:392–621 | 1h or 15min docs |
| D5-08 | Export CSV lost First/Last name split + honorific handling | P2 | proxy-lead/export.py:23–33 vs full-export.ts | 20min |

---

## Findings

### D5-01: Lost "Include organization for every lead" instruction [P0]

**proxy-lead text (agent.py:30–33):** "Include the organization name for every lead."
**v2 state:** Absent from SYSTEM_PROMPT.

**Impact:** LLM is free to emit leads with empty `organization`. For sales outreach, organization is non-optional.

**Fix:** Add the instruction back: "Include the organization name for every lead. If you cannot find one, omit the lead entirely."

---

### D5-02: Lost "source_url to strongest URL" ranking [P0]

**proxy-lead text:** "Set source_url to the strongest URL from the provided results that supports the lead."
**v2 state:** Field description says "Best source URL supporting the contact, title, or email" but the prompt no longer instructs the LLM how to pick. Field-level description is weaker than prompt-level instruction.

**Fix:** Add back: "Select source_url as the URL with the strongest direct evidence of the contact's name, title, and/or organization. Rank by relevance and recency."

---

### D5-03: `confidence` deprecated without migration path [P1]

**Evidence:** `models.py:16–20` marks the field "DEPRECATED" but it remains in the schema and is exported via `full-export.ts:17`. Downstream consumers (CRM, dashboards) using confidence bins get values that have no business meaning.

**Fix:** Either (a) define `confidence = (fit_score + evidence_score + contact_score) / 3` at export time, or (b) remove from CSV export and update consumers.

---

### D5-04: `email_patterns.py` is dead code [P1]

**Evidence:** `packages/core/src/core/email_patterns.py` is a byte-for-byte copy of the proxy-lead module. Grep across packages/ apps/ shows zero import sites. proxy-lead used it in `app.py:33` to surface inferred patterns to users.

**Impact:** Lost a valuable QA signal (does this lead's email fit the org's pattern?), and the dead code misleads future contributors.

**Fix:** Either integrate it into the post-extraction pipeline (preferred) or delete the file.

---

### D5-05: Search history APIs removed [P1]

**Evidence:** proxy-lead `history_store.py:160–239` has `list_recent_searches()` and `load_search()`. v2 has no equivalent. Users must know the recipe ID to revisit.

**Fix:** Add a `/searches` or `/history` endpoint that returns the last N searches with cost + lead-count summaries.

---

### D5-06: No persistent cost ledger [P1]

**Evidence:** proxy-lead persisted every search's cost to SQLite for billing and audit. v2 estimates cost on the fly (cost.py) but doesn't write it anywhere queryable. STATUS.md and 05-reuse.md mention Postgres replaces SQLite, but the cost-ledger table doesn't exist in any migration.

**Fix:** Add a `cost_ledger` table; write a row after every scout/full/batch run.

---

### D5-07: Bulk failure semantics changed [P1]

**Evidence:** proxy-lead `bulk.py:65–145` ran every query and returned partial results. v2 `main.py:528–551` halts the entire job on a single cap-exceeded run.

**Impact:** A user submitting 100 queries with a tight cap can have the job halt at query 47 without finishing. proxy-lead would have tried all 100.

**Fix:** Either implement resumable batch jobs (preferred) or document the all-or-nothing behavior + add a pre-flight cost calculator.

---

### D5-08: Export CSV lost First/Last name split [P2]

**Evidence:** proxy-lead `export.py:23–33` had `split_full_name()` honoring honorifics ("Dr. Sarah Chen" → First: Sarah, Last: Chen). v2 `full-export.ts` exports a single `name` column.

**Impact:** HubSpot/Salesforce expect First Name + Last Name as separate columns. Manual post-processing required.

**Fix:** Add First Name + Last Name columns; port the proxy-lead split logic.

---

## `docs/05-reuse.md` verification

| Claim | Status | Evidence |
|-------|--------|----------|
| "models.py: Copy + extend with fit/evidence/contact scores, gate, explanation" | TRUE | white-rabbit/models.py:27–31 match the spec |
| "email_patterns.py: Copy clean" | PARTIAL | File copied byte-for-byte, but **never imported** — "lifted" as text, not as integration |
| "history_store.py → cost.py: Lift pricing constants and estimate_search_cost" | PARTIAL | cost.py has the estimate function (35–54) but no SQLite history store / no Postgres replacement |
| "history_store.py: DROP the SQLite store entirely" | TRUE | No SQLite anywhere; Postgres used. But cost-ledger table not implemented. |
| "agent.py → orchestrator.py: Preserve prompt structure" | FALSE | Two explicit instructions lost (D5-01, D5-02) |
| "bulk.py → main.py /batch: Sequential processing" | PARTIAL | Sequential preserved; failure semantics changed (D5-07) |
| "export.py: HubSpot CSV export" | PARTIAL | CSV exists; First Name / Last Name split lost (D5-08) |

---

## Top-3 fixes (priority order)

1. **Restore the two lost prompt instructions** (D5-01, D5-02). 5 minutes of editing for the highest-impact fix in this dimension.
2. **Decide on email_patterns.py** (D5-04). Either wire it back in or delete it. Removes ambiguity.
3. **Add the cost ledger table** (D5-06). Unblocks billing and audit visibility — proxy-lead had this for a reason.
