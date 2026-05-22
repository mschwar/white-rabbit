# R15 Evidence Summary - Internal Correction Review And Dogfood Decision Packet

Date: 2026-05-22
Branch: `feat/reset-r15-dogfood-decision-packet`
Feature: `R15 - Internal correction review and dogfood decision packet`

## Source artifacts inspected

- `audits/gates/reset-2026-05-10/rg5-export-persistence.md`
- `audits/raw/reset-2026-05-10/rg5/artifact-summary.md`
- `.gstack/qa-reports/csv/r13-sales-first-export-2026-05-12/primary-sales-first-export.csv`
- `.gstack/qa-reports/csv/r13-sales-first-export-2026-05-12/browser-qa-summary.json`
- `.gstack/qa-reports/qa-report-r14-persistence-quality-tieout-2026-05-12.md`
- `.gstack/qa-reports/qa-report-r14c-deployment-readiness-2026-05-19.md`
- `.gstack/qa-reports/screenshots/r14c-prod-smoke/browser-qa-summary.json`
- `audits/gates/reset-2026-05-10/rg3-validation-semantics.md`
- `audits/gates/reset-2026-05-10/rg4-operator-ui.md`
- `audits/raw/reset-2026-05-10/r09l/live-source-assisted-proof.json`
- `docs/00-product-northstar.md`
- `docs/12-reset-gated-implementation-plan-2026-05-10.md`

## Extracted evidence

### R13 export artifact

- CSV artifact exists: `.gstack/qa-reports/csv/r13-sales-first-export-2026-05-12/primary-sales-first-export.csv`.
- Data rows: 51.
- First sales-first headers: `lead_name`, `title`, `organization`, `email`, `email_status`, `phone`, `phone_status`, `usable_candidate`, `operator_label`, `candidate_category`.
- `operator_label` counts: `REVIEW=23`, `ORG-ONLY=15`, `NOT FOUND=8`, `READY=5`.
- `candidate_category` counts: `person_lead=25`, `organization_only=15`, `not_found=8`, `failed=3`.
- `usable_candidate` counts: `yes=5`, `no=46`.

### R14 persistence/readback QA

- R14 Prompt B report passed.
- API suite passed in that report: `53 passed`.
- Targeted persistence/readback smoke passed for scoped Scout payloads, persisted run-lead readback, and Full persisted lead IDs.
- R14 did not include dogfood, production promotion, source/compiler changes, or UI changes.

### R14C operator-use smoke

- Browser smoke report passed locally against `next start` at `http://127.0.0.1:3000`.
- Flow verified: login gate, protected workspace, mocked operator run, evidence drawer, export download.
- Export artifact from R14C smoke: `white-rabbit-lead-export-2026-05-19.csv`, 3 data rows.
- API checks were skipped in the saved browser summary.
- R14C report explicitly deferred live Fly `/health` and `/readiness` because direct API curl had been blocked earlier.

### R09L / RG3 source-assisted proof

- Source-assisted proof passed for April 2026 New Mexico school-district IT shape.
- Candidates: 17.
- Sources: 18.
- Workbook/manual oracle rows: 17.
- Tier distribution: `high_trust_usable=10`, `manual_lookup=7`.
- Workbook replay distribution: `READY_WITH_CONTACT=10`, `MANUAL_LOOKUP=7`.
- Unsupported CRM-ready rows: 0.
- This proof advanced RG3 only; it explicitly did not prove production UI/export dogfood readiness at that time.

### Fresh production proof limitation

- A fresh production probe of the stable Vercel alias and Fly endpoints was attempted in this R15 session.
- The execution environment denied the command before it ran: `BLOCKED: User denied. Do NOT retry.`
- No `audits/raw/reset-2026-05-10/rg6/production-endpoint-probe.txt` artifact exists.
- The R15 packet therefore must not claim fresh live production endpoint proof.

## Correction review conclusions

1. RG5 proved sales-first export mechanics and API persistence/readback contracts, not live lead-quality readiness.
2. Saved export evidence is transparent and safe enough to review because uncertain rows keep labels and validation context.
3. Saved export evidence is not strong enough for Thomas/Lee dogfood because only `5/51` rows are marked usable/READY in the R13 artifact.
4. The strongest source-assisted data-quality proof remains the R09L April New Mexico replay, but it is narrow and not fresh production query-to-export evidence.
5. Production endpoint proof and live DB readback from a fresh production query are still missing.
6. Operator minutes per usable lead have not been measured in a no-assistance Thomas/Lee run.
7. The correct R15 decision is continued red hold with manual-concierge/internal Matt evaluation only, not yellow or green.
