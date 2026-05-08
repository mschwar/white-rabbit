# Dimension 3: QA Methodology Failure

**Auditor:** researcher subagent
**Date:** 2026-05-07
**Branch:** audit/hard-audit-2026-05-07
**Status:** Complete (read-only review of `.gstack/qa-reports/`)

---

## Executive verdict

The QA process tested the wrong layer. All three QA reports validated UI rendering ("did the page render? did the button work?") but **never opened a single lead card to inspect content**. Every report used the same query — `K-12 IT directors in Albuquerque` — the one query whose vertical happens to align with the hidden VoIP bias in the system prompt.

"5 lead cards rendered" ≠ "5 valid leads generated." That category error is the root cause.

---

## What QA actually tested

| Report | Date | Query used | Assertions made | Inspected lead content? |
|--------|------|-----------|-----------------|------------------------|
| `qa-report-white-rabbit-2026-05-06.md` | 2026-05-06 | Not disclosed in report | "rendered ranked leads", "5 lead cards", "CSV download link", "0 console errors" | **No** |
| `qa-report-white-rabbit-2026-05-06-sort-controls.md` | 2026-05-06 | `K-12 IT directors in Albuquerque` + filter `New Mexico` | "leads rendered correctly", "sort reordering worked", "console clean" | **No** |
| `baseline.json` | 2026-05-06 | n/a | All eight category scores 100/100 (console, links, visual, functional, ux, performance, content, accessibility) | **No detail or rubric** |

**Pattern:** Both reports run on `localhost:3004/3005`, count rendered cards, click sort and export buttons, verify zero console errors. No report opens a card and reads the rendered name, email, or explanation against the query intent.

---

## Severity table

| ID | Gap | Severity | Effort to fix process |
|----|-----|----------|----------------------|
| D3-01 | Single-vertical query exclusively used | P0 | 30min (add 3 verticals to the rubric) |
| D3-02 | Lead card *content* never inspected | P0 | 1h (define content rubric) |
| D3-03 | No end-to-end persistence read-back after Full runs | P0 | 1h (add DB read-back step) |
| D3-04 | "Ship-ready" / "100/100" scores with no defined rubric | P1 | 1h (write rubric in repo) |
| D3-05 | No regression visual-diff or prompt-validation tests | P1 | 4h (set up baseline + diff tooling) |
| D3-06 | CSV export validated for link presence, not content | P1 | 30min (add content checks) |
| D3-07 | gstack QA skill has only UI/functional mode, no data quality mode | P1 | half-day (extend skill) |
| D3-08 | QA reports written to confirm-the-spec, not test-against-it | P2 | culture/process change |

**Counts:** P0 ×3, P1 ×4, P2 ×1

---

## Findings

### D3-01: Single-vertical query exclusively used [P0]

**Evidence:** `qa-report-white-rabbit-2026-05-06-sort-controls.md` test query: "Returned leads rendered correctly for the query `K-12 IT directors in Albuquerque`." The other report omits the query. Across all artifacts there's no reference to a healthcare, finance, manufacturing, or any other vertical query.

**Why this failed to catch the bug:** This query happens to fall in the IT/Telecom vertical hardcoded in the SYSTEM_PROMPT (Dim 1). The bias is invisible because the test always asks for what the system is biased toward.

**Fix to QA process:** New rule — every QA pass must execute the same flow against ≥3 verticals from a fixed list (healthcare, finance, manufacturing, education, retail). Reports must enumerate which verticals were tested.

---

### D3-02: Lead card *content* never inspected [P0]

**Evidence:** Both QA reports count cards ("5 lead cards") and verify rendering. Neither quotes a name, an email, or an explanation. Neither asks "is this name a real person?" or "does this explanation reference the query?"

**Why this failed:** The QA framework treats lead cards as opaque blocks of UI. Card-counting is a valid UI test but is unrelated to product correctness.

**Fix:** Add a content rubric. Per query, the QA must spot-check ≥2 lead cards on the following:
- Name field: real first+last name? Not a title.
- Email field: real-looking address (or empty), never `not_available@*`.
- Explanation field: cites the query intent? No vertical leakage (no "VoIP" if query isn't about VoIP).
- Source URL: resolves and supports the claimed name/title?

Quote the failing field if any check fails.

---

### D3-03: No end-to-end persistence read-back after Full runs [P0]

**Evidence:** No QA report performs a Full run, then reads the data back from Postgres directly to verify it was stored correctly. Reports stop at "the saved run banner appeared."

**Why this failed:** Storage may corrupt data (truncation, type coercion, encoding). UI rendering uses the response object, not the persisted record. So the response can look fine while the DB row is wrong.

**Fix:** Add a DB read-back step. After a Full run, the QA process queries `recipe_run` and `lead` tables for that run and asserts row counts + key field values match what the UI displayed.

---

### D3-04: "Ship-ready" / "100/100" with no defined rubric [P1]

**Evidence:** `baseline.json` records "100/100" across eight categories. Neither report quotes a rubric defining what "100" means. The full report concludes with "ship ready" without listing the criteria that decision is based on.

**Why this failed:** Without a rubric, "ship-ready" is a vibe. Vibes don't catch prompt drift.

**Fix:** Write a `docs/qa-rubric.md` that defines, for each category, the specific assertions that must pass. Update QA reports to cite the rubric and quote the passing/failing assertions.

---

### D3-05: No regression visual-diff or prompt-validation tests [P1]

**Evidence:** Screenshots dir contains `scout-before.png` and `scout-after.png` but no automated diff tool or assertion runs against them. No test file references the screenshots. They are decorative.

**Fix:** Either drop the screenshots (don't pretend they're tests) or hook them into a real visual-diff tool (Playwright snapshots, percy, etc.). Better: add a *prompt validation test* that runs scout() and asserts no vertical leakage in the response.

---

### D3-06: CSV export validated for link presence, not content [P1]

**Evidence:** "Lead export button produced a CSV download link with the expected filename." The CSV was never opened.

**Fix:** Download the CSV during QA and assert: header row matches schema, row count > 0, no `not_available@*` strings, no escape errors, dates valid.

---

### D3-07: gstack QA skill has only UI/functional mode [P1]

**Evidence:** The reports follow the gstack QA skill's rubric (functional / visual / accessibility / performance). There is no "data quality" category.

**Fix:** Extend the gstack QA skill with a `data-quality` mode that runs the content rubric from D3-02 and the read-back from D3-03.

---

### D3-08: QA reports written to confirm-the-spec [P2]

**Evidence:** The structure of both reports is "feature claimed → screenshot → verified." There's no adversarial element — no "what could go wrong here?" section, no negative-result scenarios.

**Fix:** Add a "What we tried to break" section to every QA report.

---

## Proposed new QA rubric

A new gating rubric for any change touching the extraction or scoring pipeline:

### Tier 1 — Multi-vertical content check (mandatory)
- [ ] Run Scout on 3 verticals: healthcare, finance, manufacturing.
- [ ] For each, open ≥2 lead cards and verify:
  - [ ] Name is a plausible first+last name (no titles, no single words).
  - [ ] Email is real-format or empty (no `not_available@*`).
  - [ ] Explanation references the query intent and contains no vertical leakage.
  - [ ] Source URL resolves and supports the claim.
- [ ] Run the same flow on the canonical "Albuquerque K-12" query (regression baseline).

### Tier 2 — Persistence read-back (mandatory for Full / Batch)
- [ ] After a Full run, query Postgres directly for the recipe + leads.
- [ ] Assert row counts match UI display.
- [ ] Assert no required field is NULL.
- [ ] Assert FK integrity (every lead → run → recipe).

### Tier 3 — CSV export (mandatory if export changed)
- [ ] Download the CSV.
- [ ] Open and verify header matches schema.
- [ ] Search for `not_available` substring → must be absent.
- [ ] Assert row count.

### Tier 4 — Prompt validation (mandatory if orchestrator.py or prompts changed)
- [ ] Diff the SYSTEM_PROMPT against the previous main branch.
- [ ] Run a prompt-validation test (cross-vertical assertions) and capture the response.
- [ ] No vertical-specific terms appear in responses to non-vertical queries.

### Tier 5 — Failure modes (mandatory weekly)
- [ ] Tavily down → user sees clear error.
- [ ] OpenAI rate-limited → user sees clear error.
- [ ] Sandbox cap hit mid-batch → user sees correct partial-state.

### Tier 6 — UI smoke (current rubric, kept as-is)
- [ ] Console errors zero.
- [ ] Buttons clickable.
- [ ] Empty states render.

**Ship gate:** Tiers 1–4 must all pass. Tier 5 weekly. Tier 6 every run.

---

## Top-3 fixes (priority order)

1. **Add the multi-vertical content check (Tier 1)** — single biggest unit of leverage. Without this, prompt drift will keep slipping through. ~30 minutes per QA pass.
2. **Add the persistence read-back (Tier 2)** — catches storage bugs that UI-only QA misses. ~10 minutes per QA pass.
3. **Write the rubric document and link it from STATUS.md** — turns QA from vibes into a contract. 1 hour, one-time.
