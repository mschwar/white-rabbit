# 11 - Product Reset Plan

**Status:** Accepted for gated planning. Execution is controlled by `docs/12-reset-gated-implementation-plan-2026-05-10.md`.
**Audit:** `audits/zero-trust-codebase-audit-2026-05-10.md`
**Current gate:** Red.

## Reset Goal

Make White Rabbit useful for one operator loop before adding anything else:

```text
natural-language target
-> target-account coverage
-> field-validated leads
-> evidence review
-> sales-first CSV export
```

The reset is not a redesign sprint. It is a deletion and simplification sprint around Thomas/Lee's actual workflow.

## Decision Needed From Matt

Accept or reject this recommendation:

> Hold W5, block W6, and run a reset sprint before any new feature work.

No ADR should be appended until Matt explicitly accepts a product decision.

## What To Delete Or Hide From The Primary Path

| Surface | Action | Reason |
| --- | --- | --- |
| Scout/Full toggle | Hide | Operator should not choose internal persistence mode. |
| Search usage card | Hide unless cap is near | Dominates the first screen with implementation metering. |
| Recipes | Keep internal, no primary path | Organizes untrusted results before repeatability is proven. |
| Batch | Keep internal only | Bulk bad data is worse than single-query bad data. |
| Friday review | Keep deferred | Adds ceremony before usable output exists. |
| Scoreboards | Keep internal only | Metrics are not meaningful until row quality exists. |
| Operator minutes | Keep internal after export | Important KPI, but not part of first action. |
| Correction feedback buttons | Move to review mode | Current screen turns operators into QA testers. |
| Score sort controls | Hide | Fit/Evidence/Contact scores are not trustworthy enough yet. |
| QA fixture path in product component | Move out of operator component | Fixture support should not shape the runtime component. |

## What To Keep

- Shared password and internal API token.
- Guardrail refusal for B2C/private-person targeting.
- Candidate categories: `person_lead`, `organization_only`, `not_found`, `failed`.
- Field validation record shape.
- Evidence drawer/dossier concept.
- Persistence for Full runs, but not as an operator-facing mode.
- Export validation context.

## Rebuild Order

### R1 - W5 Hold Report

Create `.gstack/qa-reports/gate-w5-operator-loop-export.md` with decision `hold`.

Required evidence:

- May 10 live benchmark: 0 usable rows.
- Missing W5 gate report before F17-F19 merge.
- Query-to-export works mechanically but exported non-usable healthcare rows.
- CSV columns are audit-first, not Lee's CRM-first order.

Done when `STATUS.md` says W5 is held and W6 is blocked.

### R2 - Golden Operator Benchmark

Create a replayable benchmark from:

- Thomas exact Arizona K-12 prompt.
- Lee commodity-buyer prompt.
- Healthcare IT Phoenix.
- Finance CISOs New York.
- Manufacturing ops Detroit.
- B2C/private-person refusal.

Done criteria:

- Thomas prompt emits all 8 named target accounts as one of the four allowed categories.
- At least 6 of 8 have correct person or explicit non-person outcome.
- No unsupported email can appear as found.
- Manufacturing role-as-name becomes a failed candidate, not 503.

### R3 - Source Collection Before Lead Extraction

Rebuild the core pipeline around source evidence:

```text
query plan
-> target account/source collection
-> candidate proposals
-> field validator
-> row category/gate
-> narrative/export
```

Done criteria:

- The validator can explain why a target account is not-found or organization-only.
- Duplicate people across incompatible organizations are flagged.
- Single blocked source cannot create a verified contact.
- Phone status is either real or removed from the visible CRM promise.

### R4 - Sales-First UI

Replace the current operator surface with:

- one search input,
- one run button,
- compact run status,
- table of rows,
- side evidence dossier,
- export button.

CRM-facing table fields first:

1. organization
2. location
3. lead_name
4. title
5. email
6. phone
7. source
8. icebreaker / why target
9. category
10. gate

Detailed validation fields can remain available in the dossier and export.

### R5 - Sales-First Export

Default CSV order should match Lee's feedback:

1. organization
2. location
3. lead_name
4. title
5. email
6. phone
7. source_url
8. icebreaker
9. why_target
10. candidate_category
11. usable_candidate
12. email_status
13. phone_status
14. fit_score
15. evidence_score
16. contact_score
17. ranking_gate
18. query
19. run_id
20. rank
21. validation_notes
22. checked_at
23. source field URLs/statuses

Done criteria:

- Export usable rows first.
- No uncertain row is flattened into a clean CRM row.
- First 10 columns are useful to a sales rep without reading audit metadata.

## Kill / Keep Gate After Reset

After R1-R5, re-run the live benchmark with saved JSON, screenshots, CSV, and DB readback.

Move to yellow only if:

- Thomas Arizona prompt covers all 8 accounts and satisfies the northstar yellow threshold.
- At least half of sampled person rows are right persona and source-backed.
- Export order is sales-first and preserves validation context.
- Query-to-export can be completed without Matt explaining modes.

If this fails, pause v2 feature work and use a smaller internal research harness for concierge briefings until the search/validation core is rebuilt.
