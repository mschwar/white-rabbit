# QA Report - R13 Sales-First CSV Export

**Date:** 2026-05-12
**Prompt:** B
**Feature:** R13 - Sales-first CSV export
**Branch:** `feat/reset-r13-sales-first-export`
**Base:** `origin/rebuild/validated-leads-loop` at `ff4eb14`
**Decision:** Pass

## Scope Reviewed

R13 adds primary-path CSV export after rows exist, uses sales-first column ordering, sorts READY rows first, and preserves validation/source/run context for non-actionable rows.

The branch diff is confined to:

- `apps/web/src/components/scout-workspace.tsx`
- `apps/web/src/components/__tests__/scout-workspace.test.tsx`
- `apps/web/src/lib/full-export.ts`
- `apps/web/src/lib/__tests__/full-export.test.ts`
- R13 browser/CSV QA artifacts under `.gstack/qa-reports/`
- reset handoff docs

No R14 persistence, DB readback, backend/API/core behavior, source-assisted compiler, benchmark, dogfood, RG5 Prompt C, or `main` promotion scope landed.

## Verification

Passed:

```bash
git diff --check
git diff --check origin/rebuild/validated-leads-loop...HEAD
cd apps/web && npm test -- --run
cd apps/web && npm run build
cd apps/api && WR_API_INTERNAL_TOKEN=test-internal-token uv run pytest tests -q
```

Results:

- Web Vitest: `13` files, `30` tests passed.
- Web build: passed, with existing Next.js warnings about workspace-root inference and deprecated middleware naming.
- API pytest: `51 passed`, with existing datetime deprecation warnings.
- Diff hygiene: passed.

## Browser And CSV Evidence

Inspected the saved R13 browser QA artifacts:

- `.gstack/qa-reports/screenshots/r13-sales-first-export-2026-05-12/01-desktop-results-before-export.png`
- `.gstack/qa-reports/screenshots/r13-sales-first-export-2026-05-12/02-desktop-export-ready.png`
- `.gstack/qa-reports/screenshots/r13-sales-first-export-2026-05-12/03-mobile-export-ready.png`
- `.gstack/qa-reports/csv/r13-sales-first-export-2026-05-12/primary-sales-first-export.csv`
- `.gstack/qa-reports/csv/r13-sales-first-export-2026-05-12/browser-qa-summary.json`

Artifact checks:

- Exported row count: `51`.
- First 10 CSV headers: `lead_name`, `title`, `organization`, `email`, `email_status`, `phone`, `phone_status`, `usable_candidate`, `operator_label`, `candidate_category`.
- READY rows sort first in the exported artifact.
- REVIEW rows preserve missing contact status and do not become CRM-ready.
- Mobile browser artifact reports `scrollWidth=390` and `innerWidth=390`.
- Validation notes, source URLs, field/contact statuses, checked timestamp, and run/query context remain in the export.

## Northstar Check

Pass. The export is sales-first without flattening uncertainty into false confidence. CRM-facing columns come first, but audit/provenance fields remain available later in the CSV, and non-actionable tiers retain visible operator labels and blocker context.

## Result

QA passed. Merge only to `rebuild/validated-leads-loop`.

Queue update after merge:

- Mark R13 `merged_to_rebuild_branch`.
- Mark R14 `ready`.
- Keep R14A, R14B, R14C, RG6, dogfood, and `main` promotion blocked.
