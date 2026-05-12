# 05 — Reuse Manifest

**Status:** Archived Reference.
**Current reset execution:** See `docs/12-reset-gated-implementation-plan-2026-05-10.md`.

This document records bootstrap-era copy/adapt guidance from the frozen Scotty demo. Use it for historical context before touching search/extract/score code, but do not treat its lift order or Sprint references as the active work queue.

What to lift from `/Users/mschwar/Documents/proxy-lead` into `packages/core/`. Reuse is by **copy + adapt**, not by import. The two repos will drift; that's intentional (see ADR-004).

## Lift table

| Source (in /proxy-lead) | Target (in white-rabbit) | Action | Notes |
|---|---|---|---|
| `models.py` | `packages/core/models.py` | Copy + extend | Add fields: `fit_score: float`, `evidence_score: float`, `contact_score: float`, `gate_passed: bool`, `explanation: str`. Keep the existing `confidence` field for now; mark deprecated. |
| `tavily_validation.py` | `packages/core/search.py` | Lift primitive only | Extract just the Tavily call wrapper (`TAVILY_SEARCH_DEPTH`, the search invocation, error handling). Drop the validation-suite dataclasses (`TavilyValidationTarget`, `TavilyValidationResult`) — those are demo-specific. |
| `email_patterns.py` | `packages/core/email_patterns.py` | Deferred; deleted in BUILDOUT-08 | Removed as dead code in BUILDOUT-08; see audit D5-04 for context. |
| `history_store.py` | `packages/core/cost.py` | Adapt heavily | Lift the pricing constants and `estimate_search_cost` function. **Drop the SQLite store entirely** — Postgres replaces it (see `docs/02-stack.md`). **UPDATE THE PRICES** — see "Pricing currency" below. |
| `agent.py` | `packages/core/orchestrator.py` | Reference only, rewrite | The current implementation is LangChain-coupled (`langchain_openai`, `langchain_community`). Rewrite using `openai` SDK and `tavily-python` direct. Preserve the prompt structure and the fallback / error-handling shape. |
| `bulk.py` | `packages/core/batch.py` | Reference + adapt | The dataclass shape (`BulkSearchResult`, sequential processing) is the model for Full runs. Rewrite without LangChain dependencies. |
| `export.py` | `packages/core/export.py` | Copy if needed in Sprint 1 | HubSpot CSV export. Useful but **not required for Sprint 1**. Defer until first user asks. |

## Do NOT lift

| File | Why |
|---|---|
| `app.py` | Streamlit UI. v2 uses Next.js. Total throwaway. |
| `demo_data.py` | Hardcoded fixtures for the four Scotty demo queries. Demo-specific. Stays at `/proxy-lead`. |
| `results_summary.py` | Streamlit-coupled rendering. UI lives in Next.js now. |
| `config.py` | bcrypt/Streamlit-secrets coupled. Replace with simple env-var loading via `python-dotenv` + Pydantic settings. |
| `supabase_client.py` | Optional: lift if and only if Postgres host = Supabase. Otherwise replace with `psycopg` or SQLAlchemy. See `docs/02-stack.md`. |
| `logger.py` | Reasonable shape but small enough to reimplement cleanly. Use `structlog` or stdlib `logging` directly. |
| `render_customer_faq_pdf.py`, `pilot_agreement_pdf.py` | Customer-facing artifacts for the demo. Out of scope for v2. |
| Anything in `proxy-lead/scripts/`, `proxy-lead/assets/`, `proxy-lead/tests/` | Demo-coupled. Tests should be rewritten for the new orchestrator, not lifted. |

## Pricing currency

The `proxy-lead/history_store.py` file contains pricing constants dated **"as of 2025-04"**. Today is **2026-05**. These prices are stale.

Known shifts since then (per OpenAI and Tavily docs as referenced in the original brief):

- **OpenAI** added `web_search_preview` at **$10 per 1k calls**. This is now a non-trivial cost driver if used.
- **Tavily** moved to **credit-based pricing** where basic search, advanced search, extraction, crawl, and research consume credits at different rates.

**Action when lifting `history_store.py` → `cost.py`:**

1. Pull current OpenAI API pricing for `gpt-4o-mini` (or whichever model the orchestrator uses) from the OpenAI pricing page.
2. Pull current Tavily pricing / credit rates from Tavily's docs.
3. Update the constants. Add a comment with the date checked and the source URL.
4. Schedule a recurring reminder (in the form of a pinned task in `STATUS.md`'s open questions) to re-check pricing quarterly.

If the price is unknown, the `cost.py` module should expose a `cost_breakdown()` function that returns the unit counts (number of Tavily calls, input tokens, output tokens, web-search calls) and lets the caller multiply against current rates pulled from a config file. This is more durable than baking 2025 numbers into the module.

## Lift order (recommended)

1. `models.py` first — everything else depends on `Lead`.
2. `cost.py` second — orchestrator and batch will reference cost calculations from the start.
3. `search.py` third — orchestrator depends on it.
4. `orchestrator.py` fourth — the rewrite. Use `openai` and `tavily-python` directly.
5. `email_patterns.py` fifth — independent of the above; can land any time.
6. `batch.py` last — Sprint 2 territory.

## File-level notes for the agent doing the lift

### `models.py` extension

The new fields:

```python
class Lead(BaseModel):
    # ... existing fields preserved ...
    confidence: float  # deprecated, kept for compat
    fit_score: float = Field(ge=0, le=1, description="Match between person/org and target ICP")
    evidence_score: float = Field(ge=0, le=1, description="Strength and freshness of supporting sources")
    contact_score: float = Field(ge=0, le=1, description="Usability of email/phone/title information")
    gate_passed: bool = Field(description="True if all three scores cleared their thresholds")
    explanation: str = Field(description="Human-readable rationale for ranking")
```

Thresholds for the gate are configurable. Default suggestion: each score ≥ 0.6 → `gate_passed = True`. Make this a constant in `cost.py` or a new `scoring.py`, easily tweakable.

### `orchestrator.py` rewrite shape

Mirror the existing `agent.run_agent()` contract but:

- Use `openai.OpenAI()` client directly with `chat.completions.create(...)` and structured outputs (response_format with the Pydantic schema).
- Use `tavily-python` (`TavilyClient(api_key=...).search(...)`).
- Keep the existing prompt that defines what a Lead is and how to fill it in.
- Add a Scout vs. Full flag — Scout returns 10–20 leads, Full returns up to 100.
- Return both the `LeadList` and a `RunMetrics` object with token counts, search counts, elapsed time, estimated cost.
