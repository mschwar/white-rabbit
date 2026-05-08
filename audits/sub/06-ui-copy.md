# Dimension 6: UI/UX & Copy Accuracy

**Auditor:** researcher subagent
**Date:** 2026-05-07
**Branch:** audit/hard-audit-2026-05-07
**Status:** Complete (read-only review)

---

## Executive verdict

The UI is mostly honest, but in three places it overstates what the backend delivers, and in one place its placeholder copy actively biases users toward the failing query that triggered this audit. Error messages on the API side too aggressively swallow root-cause detail. No dead links, no "Coming Soon" buttons.

---

## Severity table

| ID | Issue | Severity | Effort |
|----|-------|----------|--------|
| D6-01 | Scout description claims "10–20 leads" but cap is 15 | P1 | 5min |
| D6-04 | Generic 503/500 error messages hide root cause | P1 | 30min |
| D6-06 | Batch cap exhaustion only surfaces post-completion | P1 | 1h |
| D6-02 | "K-12 IT directors in Albuquerque" placeholder appears 3× and biases users | P2 | 10min |
| D6-15 | Lead export description omits `email_status` and `icebreaker` | P2 | 5min |
| D6-12 | Loading states ("Searching…") are vague | P3 | 30min |

**Counts:** P1 ×3, P2 ×2, P3 ×1. Verified clean: 9 areas (button accuracy, dead links, empty states, batch error display, etc.)

---

## Findings

### D6-01: Scout claims "10–20 leads" but backend caps at 15 [P1]

**UI claim (`apps/web/src/components/scout-workspace.tsx:237–239`):**
```tsx
<p className="max-w-3xl text-base leading-7 text-zinc-300 sm:text-lg">
  Scout: quick preview (10–20 leads, no storage). Full: stored recipe with up to 100 leads.
</p>
```

**Backend reality (`apps/api/api/main.py:136`):**
```python
SANDBOX_SCOUT_MAX_ROWS_PER_QUERY = 15
```

**Impact:** Users expect 10–20 leads but always get ≤15. If they get exactly 15, they assume the cap kicked in. If they get fewer, they assume the query was weak. Ambiguity erodes trust.

**Recommended copy:** `"Scout: quick preview (up to 15 leads, no storage). Full: stored recipe with up to 100 leads."`

---

### D6-02: K-12 Albuquerque placeholder appears 3× and biases users [P2]

**Three appearances:**
- `scout-workspace.tsx:296` — placeholder: `"K-12 IT directors in Albuquerque"`
- `scout-workspace.tsx:281` — recipe-name placeholder: `"My K-12 IT director recipe"`
- `batch-workspace.tsx:16–17` — initial batch defaults to two NM/IT/education queries

**Impact:** This specific query happens to align with the hidden VoIP bias in SYSTEM_PROMPT (Dim 1). When users copy the placeholder, they unknowingly select the one query that masks the prompt bug. The audit was triggered when a real user *didn't* use the placeholder.

**Recommended copy:** Use a vertical-neutral example, e.g. `"VPs of Operations at mid-size US manufacturers"`. Update batch defaults to span at least two distinct verticals to teach users that variety is OK.

---

### D6-04: Generic 503/500 errors hide root cause [P1]

**Backend (`apps/api/api/main.py:209–216`):**
```python
except OrchestratorError as exc:
    logging.getLogger("white_rabbit.api").error("Orchestrator error: %s", exc, exc_info=True)
    raise HTTPException(status_code=503, detail="The search service is currently unavailable. Please try again later.")
except Exception as exc:
    logging.getLogger("white_rabbit.api").error("Unexpected error: %s", exc, exc_info=True)
    raise HTTPException(status_code=500, detail="An unexpected error occurred. Please try again later.")
```

**Impact:** Users can't tell if Tavily, OpenAI, or the DB failed; can't tell if retrying in 10 seconds will help; ops staff have to dig logs to triage. Internal tool — error messages can afford to be specific.

**Recommended fix:**
1. Return an `error_code` field: `"tavily_timeout"`, `"openai_rate_limit"`, `"db_unavailable"`, `"unknown"`.
2. UI maps codes to specific guidance ("Search engine is rate-limited; try again in ~60s").
3. Keep generic strings for unmapped codes, but always include a request ID.

---

### D6-06: Batch cap exhaustion only surfaces post-completion [P1]

**Backend (`apps/api/api/main.py:528–551`):**
```python
if total_cost + cost > job.cap_max_spend_usd:
    batch_run.status = "failed"
    batch_run.error_message = "Spend cap exceeded"
    ...
    break
```

**UI (`apps/web/src/components/batch-workspace.tsx:335–337`):**
```tsx
{run.error_message ? (
  <p className="mt-1 text-sm text-rose-300">{run.error_message}</p>
) : null}
```

**Impact:** Submit 10 queries with $10 cap. Cap hits on query 6. Queries 6–10 marked failed silently — user sees no progress until the entire response returns. No live indicator of remaining cap or expected stop point.

**Recommended fix:** Stream progress events from the backend (SSE or chunked JSON) showing cap usage; or compute estimated cost before submitting and show a "this will use ~$X.XX of $Y.YY budget" preflight.

**Quick-win copy fix on the error message:** `"Spend cap exceeded ($X.XX of $Y.YY). Run #6 of 10 cancelled; remaining queries skipped."`

---

### D6-15: Lead export description incomplete [P2]

**UI (`scout-workspace.tsx:452–454`):**
```tsx
<p className="mt-2 text-xs leading-6 text-zinc-400">
  Includes query, recipe, run metadata, scores, gate status, explanation, and validation context.
</p>
```

**Reality (`apps/web/src/lib/full-export.ts:107–129`)** — 21 columns, including `email_status` and `icebreaker` not mentioned in the description.

**Recommended copy:** `"Includes query, location, recipe name, run ID, rank, lead name/title/org/email, email status, source URL, fit/evidence/contact scores, gate status, icebreaker, why_target, explanation, and validation context."`

---

### D6-12: Loading states are vague [P3]

**Examples:**
- Scout/Full: `"Searching…"` (`scout-workspace.tsx:323`)
- Batch: `"Running batch…"` (`batch-workspace.tsx:267`)
- Recipes: `"Loading…"` × 3 sites

**Impact:** Users don't know if they're waiting on web search, LLM extraction, DB writes, or rendering. Scout takes ~10–20s; without staging, it can feel like a hang.

**Recommended fix:** Two-stage labels — `"Searching the web (1/2)…"` → `"Extracting and ranking (2/2)…"`. Drop polish-level for now if too much work.

---

## Verified clean

- Buttons (`Run Scout search`, `Run Full search`) wire to the correct endpoints. No silent extras.
- No dead links, no "Coming Soon", no no-op buttons.
- Empty states are present and actionable everywhere (recipes library, scout results, batch history, runs list).
- Recipes library correctly shows "No saved recipes yet. Run a Full search first."
- Friday review export description is accurate.
- Login error messages are specific.
- Sandbox error messages (429s) are specific and actionable.
- Feedback button null-id fallback works (`scout-workspace.tsx:540`).

---

## User-facing strings inventory (abbreviated)

Full inventory in agent transcript; key entries:

| Category | String | File:line | Verdict |
|----------|--------|-----------|---------|
| Description | "Scout: quick preview (10–20 leads...)" | scout-workspace.tsx:238 | D6-01 misleading |
| Placeholder | "K-12 IT directors in Albuquerque" | scout-workspace.tsx:296 | D6-02 biasing |
| Placeholder | "My K-12 IT director recipe" | scout-workspace.tsx:281 | D6-02 biasing |
| Error (503) | "The search service is currently unavailable..." | main.py:212 | D6-04 generic |
| Error (500) | "An unexpected error occurred..." | main.py:216 | D6-04 generic |
| Empty state | "Run a query to see ranked leads..." | scout-workspace.tsx:574 | Clean |
| Empty state | "No saved recipes yet. Run a Full search first." | recipes-library.tsx:191 | Clean |
| Empty state | "No batch jobs yet." | batch-workspace.tsx:350 | Clean |
| Loading | "Searching…" | scout-workspace.tsx:323 | D6-12 vague |
| Export desc | "Includes query, recipe, run metadata..." | scout-workspace.tsx:453 | D6-15 incomplete |

---

## Top-3 fixes (priority order)

1. **Replace the K-12 Albuquerque placeholder + batch defaults with vertical-neutral examples** (D6-02). 10 minutes. Stops the UI from teaching users the failing query pattern.
2. **Fix Scout copy from "10–20" to "up to 15"** (D6-01). 5 minutes. Honest expectation-setting.
3. **Add error_code field to API errors and map them in the UI** (D6-04). 30 minutes. Big debugging-time win for an internal tool.
