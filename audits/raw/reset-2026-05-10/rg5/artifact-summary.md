# RG5 artifact summary

Source: saved R13-R14C QA artifacts on `audit/reset-rg5-export-persistence`.

- R13 CSV artifact: `.gstack/qa-reports/csv/r13-sales-first-export-2026-05-12/primary-sales-first-export.csv`
  - Data rows: 51
  - First 10 headers: `lead_name`, `title`, `organization`, `email`, `email_status`, `phone`, `phone_status`, `usable_candidate`, `operator_label`, `candidate_category`
  - First rows are READY/high-trust rows with `usable_candidate=yes`, `operator_label=READY`, `candidate_category=person_lead`, source URLs, validation notes, checked timestamps, and run/query context preserved.
- R14C browser smoke summary: `.gstack/qa-reports/screenshots/r14c-prod-smoke/browser-qa-summary.json`
  - Export line count: 4 (header + 3 deterministic browser-smoke rows)
  - Header begins with sales-first CRM columns before run/audit metadata.
  - Primary mode chrome check: `scoutVisible=0`, `fullVisible=0`.
  - API checks: skipped in saved R14C smoke; report states live Fly `/health` and `/readiness` were not directly re-verified during R14C.
- Prompt B reports present:
  - `.gstack/qa-reports/qa-report-r13-sales-first-export-2026-05-12.md`
  - `.gstack/qa-reports/qa-report-r14-persistence-quality-tieout-2026-05-12.md`
  - `.gstack/qa-reports/qa-report-r14a-image-overhaul-brand-cleanup-2026-05-12.md`
  - `.gstack/qa-reports/qa-report-r14b-ui-ux-consistency-2026-05-12.md`
  - `.gstack/qa-reports/qa-report-r14c-deployment-readiness-2026-05-19.md`

Fresh local command notes:

- `git diff --check` passed.
- Fresh web Vitest attempts failed before tests executed because Vitest workers did not respond within 60s under both Node v25.5.0 and Node v22.22.0. Logs:
  - `audits/raw/reset-2026-05-10/rg5/web-targeted-tests.txt`
  - `audits/raw/reset-2026-05-10/rg5/web-full-export-test.txt`
  - `audits/raw/reset-2026-05-10/rg5/web-full-export-test-node22.txt`
  - `audits/raw/reset-2026-05-10/rg5/web-full-export-test-node22-threads.txt`
- Fresh API pytest targeted attempts timed out during collection/setup in this shell. Logs:
  - `audits/raw/reset-2026-05-10/rg5/api-persistence-targeted-tests.txt`
- Direct production curl was blocked by the execution environment (`BLOCKED: User denied. Do NOT retry.`), so this audit does not add fresh live Fly/Vercel endpoint proof beyond existing R14C artifacts.
