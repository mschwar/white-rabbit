# QA Report — F04 Query Compiler / Planner

**Feature ID:** F04  
**Feature name:** Query Compiler / Planner  
**Branch:** `feat/f04-query-compiler`  
**PR target:** `rebuild/validated-leads-loop`  
**Date:** 2026-05-10  
**Agent:** Codex  
**Required verification type:** Non-UI  
**Buildout plan:** `docs/08-agentic-buildout-plan.md`  
**Northstar:** `docs/00-product-northstar.md`  

## Scope Checked

- F04 feature card and acceptance criteria in `docs/08-agentic-buildout-plan.md`  
- Files changed since implementation include QA evidence only (no code changes this session)  
- Confirmed `main` untouched: yes  
- Confirmed merge target is `rebuild/validated-leads-loop`: yes  

## Non-UI Verification Steps

### Command

```bash
cd packages/core && uv run pytest tests/test_query_planner.py tests/test_search.py -q
```

#### Expected

- Test suite passes
- No compiled query exceeds the Tavily limit

#### Actual

- `..... [100%]`  
- `5 passed in 0.06s`

### Verification script (benchmark compilation check)

```bash
python script:
- compile_query_plan(long_arizona_prompt)
```

#### Actual output summary

- named_accounts_count = 8  
- vendor_queries_count = 8  
- max_query_length = 86  
- limit = 380  
- all queries under limit and each includes `arizona` and named account terms  

Example first query:  
`Mesa decision maker decision makers k-12 voip telecom technology it arizona`

## Tests Run

| Command | Result | Notes |
| --- | --- | --- |
| `cd packages/core && uv run pytest tests/test_query_planner.py tests/test_search.py -q` | Pass | 5 tests passed |

## Northstar Reflection

| Question | Yes/No | Notes |
| --- | --- | --- |
| Does this directly improve natural-language query -> high-quality validated leads -> export? | Yes | It prevents overlong malformed inputs reaching Tavily and preserves named-account intent for better query quality. |
| Does it reduce false confidence, bad contacts, wrong personas, or unsupported source claims? | Yes | It addresses the query-crash/overrun failure path; output quality still depends on downstream extraction. |
| Does it avoid organizing or beautifying untrusted data? | Yes | Core-only change; no UI flow or presentation changes. |
| Does it keep main untouched and target only rebuild/validated-leads-loop? | Yes | This is a feature-branch QA pass with merge constrained to rebuild branch. |
| Is the feature independently mergeable? | Yes | Self-contained planner/search integration and tests are branch-scoped. |
| Can the next agent discover state from docs without chat context? | Yes | `STATUS.md` and feature table updated with handoff. |
| Is there browser QA or explicit non-UI verification? | Yes | Explicit non-UI verification executed (`pytest` + benchmark compile script). |
| Is the scope small enough for the requested model class? | Yes | Feature scope remains planner + search orchestration tests only. |

## Findings

### Blocking

- None.

### Non-blocking

- Long prompt compilation is effectively reduced to compact per-account vendor queries, but this verification only covers planner behavior, not downstream extraction ranking.  

## Merge Decision

**Decision:** merge  

**Reason:** Required tests and explicit long-benchmark bounded-query verification passed. No code regressions found in this QA session.

## Handoff

```text
Feature:
F04 Query compiler / planner
Branch:
feat/f04-query-compiler
Status:
qa_passed
What changed:
Verified planner decomposition and bounded compilation for long Arizona benchmark prompts.
Tests or QA run:
- cd packages/core && uv run pytest tests/test_query_planner.py tests/test_search.py -q
- Long Arizona benchmark compile script check (8 named accounts, max vendor query length 86, limit 380)
Screenshots or report:
.gstack/qa-reports/qa-report-f04-query-compiler-2026-05-10.md
Northstar reflection:
Prevents Tavily overrun from long prompts and preserves named-account decomposition constraints.
Next pointer:
Merge this branch into `rebuild/validated-leads-loop`, then begin `feat/f05-candidate-types`.
Open questions:
None.
```
