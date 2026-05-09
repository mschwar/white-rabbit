# QA Rubric — White Rabbit

**Source:** `audits/hard-audit-2026-05-07.md` Dimension 3 findings (D3-01 through D3-08)
**Created:** 2026-05-09
**Status:** Active — any change touching `orchestrator.py`, `models.py`, or extraction logic must pass Tiers 1–4 before merge.

---

## Why this exists

Previous QA validated UI rendering ("did the page render? did the button work?") but never opened a lead card to inspect content. Every QA report used `K-12 IT directors in Albuquerque` — the one query that happened to align with the hidden VoIP bias in the system prompt. The product shipped with 89% vertical leakage because card-counting was mistaken for correctness.

This rubric fixes that by defining **what to check**, **how to check it**, and **when each tier is required**.

---

## Ship gate summary

| Change type | Required tiers |
|-------------|--------------|
| Any change to `orchestrator.py`, `models.py`, prompts, or scoring | **1–4** |
| Any change to storage, export, or persistence layer | **2, 3** |
| Any change to UI, routing, or auth | **5, 6** |
| Weekly regression (no code change) | **1, 5, 6** |
| Before any external user / pilot access | **1–6** |

---

## Tier 1 — Multi-vertical content check (mandatory for extraction changes)

**Goal:** Verify the LLM produces real, relevant leads across multiple verticals with no prompt drift.

### Procedure

1. Run Scout on **3 distinct verticals** from the canonical list:
   - Healthcare
   - Finance
   - Manufacturing
   - (Optional 4th regression: K-12 education — the old baseline)

2. For each vertical, open **≥2 lead cards** and verify every field below.

### Per-lead assertions

| Field | Pass criterion | Fail examples |
|-------|---------------|---------------|
| **Name** | Plausible first+last name. Contains at least one whitespace. Not a job title. | `"Director of Technology"`, `"VP Engineering"`, `"John"` |
| **Email** | Real-format address OR empty string. Never a placeholder. | `"not_available@x.com"`, `"noreply@company.com"`, `"placeholder@x.com"` |
| **Explanation** | References the query intent. No vertical leakage (e.g., no "VoIP" in a non-VoIP query). | `"...ideal for a VoIP upgrade..."` on a healthcare query |
| **Source URL** | Resolves (HTTP 200 or 301/302). Page content supports the claimed name/title. | 404, generic homepage, unrelated article |

### Tier 1 checklist

- [ ] Scout run: Healthcare vertical
  - [ ] Lead 1 name passes
  - [ ] Lead 1 email passes
  - [ ] Lead 1 explanation passes
  - [ ] Lead 2 name passes
  - [ ] Lead 2 email passes
  - [ ] Lead 2 explanation passes
- [ ] Scout run: Finance vertical
  - [ ] Lead 1 name passes
  - [ ] Lead 1 email passes
  - [ ] Lead 1 explanation passes
  - [ ] Lead 2 name passes
  - [ ] Lead 2 email passes
  - [ ] Lead 2 explanation passes
- [ ] Scout run: Manufacturing vertical
  - [ ] Lead 1 name passes
  - [ ] Lead 1 email passes
  - [ ] Lead 1 explanation passes
  - [ ] Lead 2 name passes
  - [ ] Lead 2 email passes
  - [ ] Lead 2 explanation passes
- [ ] Regression: K-12 Albuquerque (if changing prompts)
  - [ ] Leads still return (no regression)
  - [ ] Explanation may contain VoIP (this is the allowed vertical)

### What to record

Quote the failing field in the QA report if any check fails. Include the exact query used and the lead's name.

---

## Tier 2 — Persistence read-back (mandatory for Full / Batch changes)

**Goal:** Verify data stored in Postgres matches what the UI displayed. UI rendering uses the response object, not the persisted record — storage corruption can be invisible to UI-only QA.

### Procedure

1. Execute a **Full run** (not Scout) with a real query.
2. Note the run ID returned by the API.
3. Query Postgres directly:

```sql
SELECT r.id AS recipe_id, rr.id AS run_id, rr.lead_count,
       l.id AS lead_id, l.data, l.fit_score, l.evidence_score, l.contact_score, l.gate_passed
FROM recipe r
JOIN recipe_run rr ON rr.recipe_id = r.id
JOIN lead l ON l.run_id = rr.id
WHERE rr.id = '<run_id>';
```

### Assertions

- [ ] Row count in `lead` table equals `lead_count` on `recipe_run`.
- [ ] Every lead has non-null `data` JSON.
- [ ] Scalar scores (`fit_score`, `evidence_score`, `contact_score`) match the values shown in the UI.
- [ ] `gate_passed` matches the server-computed rule: `all(s >= 0.6 for s in [fit, evidence, contact])`.
- [ ] FK integrity: every `lead.run_id` → `recipe_run.id` → `recipe.id` resolves.

### What to record

Include the SQL output (truncated to first 3 rows) and the UI screenshot showing the same run.

---

## Tier 3 — CSV export inspection (mandatory if export changed)

**Goal:** Verify the exported file is structurally correct and contains no corrupted or placeholder data.

### Procedure

1. Trigger a Full run.
2. Click the CSV export button.
3. Open the downloaded file in a text editor or spreadsheet.

### Assertions

- [ ] Header row exists and matches the documented schema.
- [ ] Row count > 0 and equals the number of leads in the run.
- [ ] Search for `not_available` substring → must be absent.
- [ ] No malformed escape sequences or broken quoting.
- [ ] Date columns are parseable ISO-8601.

### Expected CSV columns

`query`, `location`, `recipe_name`, `run_id`, `rank`, `lead_name`, `title`, `org`, `email`, `email_status`, `source_url`, `fit_score`, `evidence_score`, `contact_score`, `gate_passed`, `icebreaker`, `why_target`, `explanation`, `validation_context`

### What to record

Include the first 3 lines of the CSV in the QA report.

---

## Tier 4 — Prompt validation (mandatory if orchestrator.py or prompts changed)

**Goal:** Detect prompt drift before it reaches users.

### Procedure

1. Diff `packages/core/src/core/orchestrator.py` against `main`.
2. Run the integration test suite (`pytest -m integration` in `packages/core`).
3. If the diff touches `SYSTEM_PROMPT` or `Lead` schema descriptions, run the 4-vertical cross-check manually even if CI is not set up.

### Assertions

- [ ] Diff shows no re-introduction of vertical-specific language in `SYSTEM_PROMPT` or field descriptions.
- [ ] Integration tests pass (or are skipped with documented reason).
- [ ] No vertical-specific terms appear in responses to non-vertical queries.

### What to record

Paste the prompt diff (first 20 lines) and the integration test result summary.

---

## Tier 5 — Failure modes (mandatory weekly)

**Goal:** Confirm the system degrades gracefully under external dependency failure.

### Procedure

Run each failure scenario in isolation. Do not run all three simultaneously.

| Scenario | How to simulate | Expected behavior |
|----------|----------------|-------------------|
| Tavily down | Temporarily set `TAVILY_API_KEY=""` or disconnect network | UI shows: "Search engine is rate-limited; try again in ~60s" (error_code: `tavily_failed`) |
| OpenAI rate-limited | Temporarily set `OPENAI_API_KEY=""` | UI shows: "AI extraction service unavailable; check API key or try again later" (error_code: `openai_failed`) |
| Sandbox cap hit mid-batch | Run 11 Scout queries sequentially with cap=10 | 11th query shows: "Sandbox query cap reached (10). Reset to continue." (error_code: `sandbox_cap_exhausted`) |

### Assertions

- [ ] Tavily failure → specific error_code, user-friendly message, no stack trace in UI.
- [ ] OpenAI failure → specific error_code, user-friendly message, no stack trace in UI.
- [ ] Sandbox cap → 429 status, partial results from prior queries preserved if mid-batch.

### What to record

Screenshot the error state for each scenario.

---

## Tier 6 — UI smoke (mandatory every run)

**Goal:** Confirm the interface renders and responds correctly. This is the existing gstack QA skill baseline, kept unchanged.

### Assertions

- [ ] Zero console errors (DevTools → Console).
- [ ] All buttons clickable and produce expected state change.
- [ ] Empty states render with helpful copy.
- [ ] Loading states show progress (not frozen).
- [ ] Responsive layout: no horizontal scroll at 1280×800.

### What to record

Screenshots of each page state. Note any console warnings (non-blocking) separately from errors (blocking).

---

## How to use this rubric in a QA report

Every QA report must:

1. Cite this document: `Per docs/qa-rubric.md, Tiers X–Y required for this change.`
2. Include the Tier 1 checklist (or note "N/A — no extraction changes" with justification).
3. Quote any failing assertion with the exact observed value.
4. Attach screenshots to `.gstack/qa-reports/screenshots/`.

### Example report header

```markdown
# QA Report — BUILDOUT-15

**Branch:** feat/buildout-15-qa-rubric
**Date:** 2026-05-09
**Agent:** kimi-k2.6
**Required tiers:** 1–4 (touches orchestrator.py)
**Rubric:** docs/qa-rubric.md

## Tier 1 — Multi-vertical content check

### Healthcare IT directors in Phoenix
- [x] Lead 1: "Sarah Chen" — name passes, email `sarah.chen@example.org` passes, explanation cites healthcare IT.
- [x] Lead 2: "James Morrison" — name passes, email empty (allowed), explanation passes.

### Finance CISOs in New York
- [x] Lead 1: "Alicia Reyes" — name passes, email `areyes@bank.example` passes, explanation passes.
- [x] Lead 2: "David Park" — name passes, email passes, explanation passes.

### Manufacturing directors in Detroit
- [x] Lead 1: "Robert Hale" — name passes, email passes, explanation passes.
- [x] Lead 2: "Lisa Nguyen" — name passes, email empty, explanation passes.

## Tier 2 — Persistence read-back
- [x] Full run `run_id=abc-123` stored 8 leads; SQL count matches UI.
- [x] All scalar scores match UI display.
- [x] FK integrity verified.

... (tiers 3–6 as applicable)
```

---

## Maintenance

- **Updates to this rubric** require an ADR entry in `docs/03-decisions.md` if they change the ship-gate criteria.
- **New tiers** may be added; existing tiers may not be removed without a decision record.
- **QA report index** lives at `.gstack/qa-reports/index.md` and must reference this document.
