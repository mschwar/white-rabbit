# 05 - Code Quality / Architecture

**Verdict:** too much product surface for an unproven core.

## Hotspots

- `apps/web/src/components/scout-workspace.tsx`: 1,234 LOC.
- `apps/api/api/main.py`: 878 LOC.
- `apps/web/src/components/__tests__/scout-workspace.test.tsx`: 651 LOC.
- `apps/web/src/lib/scout.ts`: 493 LOC.
- `packages/core/src/core/source_validation.py`: 416 LOC.

These hotspots are not automatically bad, but their responsibilities are mixed.

## Frontend Coupling

`scout-workspace.tsx` owns query form state, mode switching, sandbox usage, loading/error mapping, Full-run persistence controls, export, feedback, corrections, evidence drawer state, QA fixture injection, and rendering shell. That is why the UI feels noisy: the component mirrors internal implementation concerns.

The default `/scout` state also contradicts itself: query defaults to `Healthcare IT directors in Phoenix`, while location defaults to `New Mexico`. That is a direct operator-trust bug.

## API Coupling

`apps/api/api/main.py` mixes auth dependency, sandbox reserve/accounting, guardrails, Scout/Full orchestration, persistence, feedback, corrections, recipes, sandbox, and batch. The internal token boundary is now real, but the route file is becoming a coordination dump.

Sandbox reserve happens before Scout, rows are recorded after Scout, and spend caps in batch are checked after cost has already been incurred. That may be acceptable for a demo sandbox, but it should not be confused with product metering.

## Core Coupling

The core has better primitives than before, but the actual path is still:

```text
Tavily search -> LLM structured extraction -> literal source validation -> score/gate
```

That is not a robust prospecting architecture. It lacks an evidence store, source snapshots, account-level coverage, conflict resolution, and partial parse recovery.

## Required Reset

Split the surface by operator loop:

- `SearchForm`: one query, optional location only if the query does not already include one.
- `ResultsGrid`: CRM fields first, compact categories.
- `EvidencePanel`: selected row details.
- `ExportPanel`: always tied to the current run and visible when rows exist.

Split the backend by product boundary:

- guardrails,
- planner,
- source collection,
- candidate extraction,
- field validation,
- persistence/export.

Do not add new abstractions for their own sake. Delete or park surfaces that are not in the single-query validated-lead loop.
