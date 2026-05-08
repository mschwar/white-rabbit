# Dimension 8: Documentation Drift

**Auditor:** researcher subagent
**Date:** 2026-05-07
**Branch:** audit/hard-audit-2026-05-07
**Status:** Complete (read-only review of all docs vs code)

---

## Executive verdict

Documentation is **~93% consistent with the code** — better than expected given the audit's premise. Only three meaningful drifts:

1. STATUS.md "Known issues" lists problems that have since been fixed (persisted lead IDs, server-side guardrails). The doc lags reality in the *good* direction — it understates progress.
2. The 2026-05-06 reconciliation report is now stale.
3. TESTING.md describes a `__tests__/` convention that Python tests don't follow.

Notably absent: any doc that claims "vertical-agnostic" — so the VoIP-bias bug is *not* a documentation lie. It's a product-positioning vs implementation gap. Docs simply don't address vertical scope.

---

## STATUS.md "What's done" verification table

| Claim | Reality | Verdict |
|-------|---------|---------|
| "Repo created at /Users/mschwar/Documents/white-rabbit/" (line 11) | Confirmed | ✓ |
| "Sprint 1: Scaffold apps/web (Next.js) completed" (line 28) | Next.js scaffold present | ✓ |
| "Sprint 1: Scaffold apps/api (FastAPI + uv) completed" (line 29) | API present at apps/api | ✓ |
| "Sprint 1: Core primitives lifted and adapted" (line 30) | packages/core present | ✓ (but with caveats — see Dim 5) |
| "Pricing constants in packages/core/core/cost.py updated to 2026-05" (line 82) | cost.py header confirms 2026-05 | ✓ |
| "Feedback buttons may not be fully usable…persisted lead IDs not returned" (line 86) | apps/api/api/main.py:261–263 injects `lead.id = str(db_lead.id)`. Merged in commit 76c0987. | **STALE — already fixed** |
| "Current app has no server-side lead-generation prompt guardrail" (line 87) | `_query_guardrail_or_422()` exists at main.py:195, 222, 419; query_guardrails.py:149–204 implemented. | **FALSE — already shipped** |
| "no query/row usage ledger for the meeting's sandbox cap" (line 87) | Sandbox caps merged in #11 — STATUS itself acknowledges this on the same page. | **Self-contradicting** |

---

## Severity table

| ID | Drift | Severity | Effort |
|----|-------|----------|--------|
| D8-01 | STATUS.md "Known issues" lists already-fixed items | P1 | 10min |
| D8-02 | `build-meeting-reconciliation-2026-05-06.md` is stale | P2 | 5min (mark historical) |
| D8-03 | TESTING.md `__tests__/` convention not followed by Python | P2 | 15min |
| D8-04 | No doc addresses vertical scope; product is positioned as cross-vertical but code is VoIP-hardcoded | P1 | 1h (write architectural decision) |

**Counts:** P1 ×2, P2 ×2. Verified clean: USER_GUIDE, AGENTS, README, 00-context, 01-model, 02-stack, 03-decisions, 04-roadmap, 05-reuse (with caveats from Dim 5).

---

## Findings

### D8-01: STATUS.md "Known issues" lists already-fixed items [P1]

**STATUS.md:85–87 says:**
> "Feedback buttons may not be fully usable after Full runs until persisted lead IDs are returned to the web UI; current core `Lead` objects do not include the database `lead.id`."
> "Current app has no server-side lead-generation prompt guardrail and no query/row usage ledger for the meeting's sandbox cap."

**Code says (apps/api/api/main.py:261–263):**
```python
for lead, db_lead in zip(leads, db_leads):
    lead.id = str(db_lead.id)
```

**Code says (apps/api/api/main.py:195, 222, 419):** `_query_guardrail_or_422()` is wired into every scout / full / batch route, calling `evaluate_query_guardrails()` from `query_guardrails.py:149–204`.

**Drift:** STATUS understates progress. The persisted-lead-IDs fix landed in commit `76c0987` (current HEAD). Guardrails are wired throughout the API.

**Fix:** Move both items from "Known issues" to "What's done." Reference the commits that closed them.

---

### D8-02: 2026-05-06 reconciliation report is stale [P2]

**`docs/reports/build-meeting-reconciliation-2026-05-06.md:178–181` says:**
> "Feedback buttons likely need a wiring fix. The API saves leads to Postgres, but `FullResponse` returns the original core `Lead` objects. The core `Lead` model has no persisted database `id`…"

**Code reality:** Wiring fix shipped (see D8-01).

**Fix:** Mark the report as historical at the top: `> **Status: Historical (2026-05-06).** Recommendations addressed in commits 76c0987 and earlier. Retained for context.`

---

### D8-03: TESTING.md `__tests__/` convention not followed by Python [P2]

**`TESTING.md:22–24` says:**
> "Place in `__tests__` directories adjacent to the code they test. Use `.test.tsx` or `.test.ts`."

**Code reality:**
- Web tests follow the convention (`apps/web/src/**/__tests__/`).
- Python tests live in `packages/core/tests/` and `apps/api/tests/`, not `__tests__` adjacency, and use `test_*.py` not `*.test.py`.

**Drift:** Convention applies to web only; doc presents it as universal.

**Fix:** Update TESTING.md to clarify per-language conventions:
- TypeScript: `__tests__/` adjacent, `.test.ts(x)` suffix.
- Python: `tests/` directory at the package root, `test_*.py` prefix (pytest standard).

---

### D8-04: No doc addresses vertical scope [P1]

**Evidence:**
- `docs/00-context.md`, `docs/01-model.md`, `docs/05-reuse.md`, `docs/USER_GUIDE.md` — none commit to a vertical or to vertical-agnosticism. They use generic "leads" / "decision makers" language.
- `packages/core/src/core/orchestrator.py:20–41` SYSTEM_PROMPT hardcodes "B2B telecom" / "VoIP" / "IT/Networking."
- `models.py:21,23` field descriptions hardcode "VoIP sales" / "VoIP upgrade."

**Drift type:** Not a contradiction — *an absence*. The product positions itself as a generic lead-research tool but the implementation is VoIP-only. The user who triggered this audit assumed cross-vertical capability based on the docs.

**Fix:** Either:
- (a) Add an ADR to `docs/03-decisions.md` stating "Pre-pilot scope is VoIP/Telecom only; cross-vertical support deferred." and update USER_GUIDE.md to caveat the example queries.
- (b) Delete the VoIP hardcoding from prompt + schema (preferred; see Dim 1 D1-01, D1-02).

---

## Per-doc summary

| Doc | Total claims sampled | Verified | Drift |
|-----|---------------------|----------|-------|
| STATUS.md | 18 | 16 | 2 (D8-01) |
| AGENTS.md | 12 | 12 | 0 |
| README.md | 5 | 5 | 0 |
| TESTING.md | 6 | 5 | 1 (D8-03) |
| docs/00-context.md | 8 | 8 | 0 |
| docs/01-model.md | 14 | 14 | 0 (but Dim 5 notes prompt-level drift) |
| docs/02-stack.md | 9 | 9 | 0 |
| docs/03-decisions.md | 4 ADRs | 4 | 0 |
| docs/04-roadmap.md | All 4 sprints | All verified done | 0 |
| docs/05-reuse.md | 8 lift claims | 5 fully, 3 partial | overlaps with Dim 5 |
| docs/USER_GUIDE.md | 12 features | 12 | 0 |
| docs/reports/build-meeting-reconciliation-2026-05-06.md | n/a | stale | D8-02 |

**Aggregate:** ~87 claims sampled, ~84 verified accurate (~96%). Three drifts (~3.4%); one absence (D8-04).

---

## Recommended documentation updates

1. **STATUS.md (D8-01):** Move "feedback button needs persisted lead IDs" and "no server-side guardrail" from Known Issues → What's Done with commit references. 10 minutes.
2. **`docs/reports/build-meeting-reconciliation-2026-05-06.md` (D8-02):** Add a "Historical" header noting items are addressed. 5 minutes.
3. **TESTING.md (D8-03):** Split conventions per-language. 15 minutes.
4. **docs/03-decisions.md (D8-04):** Add ADR-005 documenting the vertical scope decision (whether VoIP-only by design or to be removed). 1 hour.
5. **STATUS.md:** Add an "Audit reality" section linking to `audits/hard-audit-2026-05-07.md` once the master report exists. 5 minutes — handled in Phase 3c.

---

## Top-3 fixes (priority order)

1. **D8-01 STATUS.md correction** — Removes false statements that are actively misleading new contributors. 10 minutes.
2. **D8-04 ADR for vertical scope** — Forces a decision (commit to VoIP or remove the bias) and documents whichever way. 1 hour. Highest semantic value.
3. **D8-03 TESTING.md split** — Removes a small inconsistency that confuses devs writing new tests. 15 minutes.
