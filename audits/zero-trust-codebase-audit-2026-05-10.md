# White Rabbit Zero-Trust Codebase Audit - 2026-05-10

**Branch:** `audit/zero-trust-2026-05-10`
**Base:** `rebuild/validated-leads-loop` at `bc1270d`
**Scope:** read/report only for product code. Audit artifacts and `STATUS.md` updated.
**Verdict:** **Red. Do not ship. Do not dogfood with Thomas or Lee. Do not proceed to W6.**

## Executive Finding

The app is mechanically better than the May 9 audit state, but not product-better enough. The API boundary is fixed, guardrails now block the B2C/privacy prompt, the validation schema exists, and the UI can show buckets/evidence/export. But the live operator loop still fails the only test that matters:

```text
operator prompt -> right targets -> evidence-backed contacts -> exportable CRM rows
```

Across the live benchmark set, the audit found **0 usable leads**. The app now labels most bad rows as non-usable, which is progress, but the screen still makes those rows feel substantial through cards, scores, notes, and export ceremony. That is not the vision from Thomas/Lee. It is a better-looking wrapper around not-yet-good-enough search.

## Severity-Ranked Findings

### P0 - Live Search Still Produces 0 Usable Leads

Evidence: `audits/raw/zero-trust-2026-05-10/live/`.

| Query | HTTP | Rows | Usable |
| --- | ---: | ---: | ---: |
| Thomas Arizona K-12 exact prompt | 200 | 3 | 0 |
| Lee commodity buyers prompt | 200 | 4 | 0 |
| Healthcare IT directors in Phoenix | 200 | 2 | 0 |
| Finance CISOs in New York | 200 | 4 | 0 |
| Manufacturing ops leaders in Detroit | 503 | 0 | 0 |
| B2C/private phone guardrail | 422 | 0 | blocked correctly |

The Arizona benchmark missed five of eight named target accounts and produced no contact detail. Lee's prompt returned named rows, but contact/source validation did not support CRM use. Healthcare returned executives instead of IT directors. Finance duplicated a person across conflicting organizations. Manufacturing crashed.

### P0 - W5/W6 Gate Process Has Not Proven The Visible Operator Loop

No W5 or W6 gate report exists. F13-F19 are merged, but the required W5 proof is absent: query-to-export browser path with usable validation evidence and CSV inspection. The audit did run that path and captured a Full-mode export; it worked mechanically but exported three non-usable healthcare rows.

Gate recommendation: **W5 hold. W6 blocked.**

### P0 - Scores Still Create False Confidence

The live Full-mode export saved three healthcare rows with `fit_score=1.00` and `evidence_score=1.00`, while all three had missing contact and `gate_passed=false`. The UI displayed Evidence 100% for rows that were not usable. The gate is stricter now, but the score language still tells the operator "this is strong" before the evidence says "this is unsafe."

### P0 - Validation Is Field-Shaped But Still Too Shallow

`source_validation.py` validates by fetching one `source_url` and checking whether field strings appear in the normalized page text. That is not enough for current role, contact usability, source freshness, multiple-source disagreement, duplicate resolution, or target-account coverage. A single accessible LinkedIn page can support name/org while title/contact fail; a blocked company page can leave a claimed email in the row object while validation fails it.

### P1 - LLM Parse Failure Can Kill A Whole Query

The manufacturing Detroit benchmark returned 503 because the model emitted `"Chief Manufacturing Officer"` as `Lead.name`, causing Pydantic union validation errors. A bad candidate should become a `failed` row or be dropped with an error record; it should not kill the entire operator run.

### P1 - The UI Is Still An Internal QA Surface, Not A Sales Tool

The v2 screen shows a large shell, Scout/Full mode, usage cards, bucket cards, score pills, validation badges, long notes, feedback buttons, and hidden Full-mode export. Thomas asked for a Google-like search path. Lee asked for CRM-relevant columns first. The current UI is useful for agents auditing the validation system; it is not clean enough for an operator prospecting workflow.

### P1 - Export Has Validation Context But The Wrong Front Door

The CSV includes validation fields, which is good. But export only appears after Full mode, and the column order starts with generated/run metadata. Lee's feedback asks for organization/location/name/role/email/phone/icebreaker first, with report/run/status/evidence columns later. Current export is audit-first, not sales-first.

### P1 - Tests Prove Rendering And Contracts More Than Product Truth

Web tests use mocked `Jane Smith`/`Noisy Lead` fixtures. Core tests pass under isolated env but live queries fail product standards. API tests require exact token environment setup or fail as blanket 401s. The tests are useful as regression checks, but they are insufficient as launch-gate evidence.

### P2 - v1 Was Clearer Even Though It Was Demo-Backed

The frozen Streamlit app should not be revived as code. It was fixture-heavy and less rigorous. But its interaction model was closer: one target input, table, lead dossier, export. v2 should restore that shape while keeping v2's stronger backend contract.

### P2 - Docs Know The Standard, But Status Understates Current Failure

`docs/00-product-northstar.md` remains correct. The problem is that live behavior does not meet it. `STATUS.md` now needs to say plainly that the May 10 audit keeps the product red and recommends a W5 hold.

## Why Previous Audits Missed It

They did not entirely miss it; the May 9 audit correctly called the product red. The miss happened after that: rebuild features were accepted because they implemented the planned surfaces and deterministic checks. The acceptance evidence was mostly contract-level, fixture-level, and UI-level. It did not re-anchor the product in Thomas/Lee prompts plus live query-to-export output.

W4 also skipped optional live verification because live keys were not available in that shell. In this audit, the running local app did have keys, and live verification showed the core gap still exists.

## Kill / Keep / Rebuild Recommendations

## Kill Or Hide Now

- Hide Scout/Full mode from the primary path.
- Hide quota cards unless nearing cap.
- Hide recipes, batch, Friday review, scoreboards, operator-minute capture, and correction controls from the operator path.
- Stop using score-sort controls until score semantics are rebuilt.
- Stop presenting Evidence/Fit/Contact scores as operator-facing confidence when gate is false.

## Keep

- Shared password plus internal API token.
- Candidate categories.
- Field-level validation shape.
- Evidence drawer concept.
- Export with validation context.
- Guardrails that block B2C/private-person targeting.
- Persistence readback for Full runs.

## Rebuild First

1. Target-account coverage for Thomas-style prompts.
2. Source collection and field validation before LLM narrative.
3. Duplicate/conflict resolution.
4. Query-to-export primary UI.
5. Sales-first CSV order.
6. Golden fixtures grounded in operator evidence and source snapshots.

## Sub-Reports

- `audits/sub/zero-trust-2026-05-10/01-data-quality-search-truth.md`
- `audits/sub/zero-trust-2026-05-10/02-prompt-model-validation-pipeline.md`
- `audits/sub/zero-trust-2026-05-10/03-test-coverage.md`
- `audits/sub/zero-trust-2026-05-10/04-qa-gate-process.md`
- `audits/sub/zero-trust-2026-05-10/05-code-quality-architecture.md`
- `audits/sub/zero-trust-2026-05-10/06-v1-proxy-lead-diff.md`
- `audits/sub/zero-trust-2026-05-10/07-ui-ux-copy.md`
- `audits/sub/zero-trust-2026-05-10/08-docs-status-decision-drift.md`

## Raw Evidence

- Evidence ledger: `audits/raw/zero-trust-2026-05-10/evidence-ledger.md`
- Verification log: `audits/raw/zero-trust-2026-05-10/commands/verification-log.md`
- Live JSON: `audits/raw/zero-trust-2026-05-10/live/`
- Screenshots: `audits/raw/zero-trust-2026-05-10/screenshots/`
- Full export sample: `audits/raw/zero-trust-2026-05-10/live/full-export-healthcare.csv`
- DB readback: `audits/raw/zero-trust-2026-05-10/db-readback.md`
- iMessage limitation note: `audits/raw/zero-trust-2026-05-10/imessage-targeted-search.md`
- Arizona workbook readback: `audits/raw/zero-trust-2026-05-10/workbook-arizona-k12-readback.md`

## Final Recommendation

Do not polish the current screen. Do not add another operator feature. Treat the next sprint as a product reset:

```text
single prompt
-> target-account coverage
-> validated fields
-> compact table/dossier
-> sales-first export
```

If that loop cannot produce at least a few genuinely usable rows for Thomas and Lee's exact prompts, the correct move is to pause v2 and fulfill concierge briefings manually from a smaller internal research harness.
