# 01 - Data Quality / Search Truth

**Verdict:** fail. The current live app still does not produce usable operator output for Thomas or Lee.

## Live Benchmark Result

| Query | HTTP | Rows | Usable | Main failure |
| --- | ---: | ---: | ---: | --- |
| Thomas Arizona K-12 exact prompt | 200 | 3 | 0 | Missed 5 of 8 named districts; all contacts missing. |
| Lee commodity buyers prompt | 200 | 4 | 0 | Some emails claimed, but field validation failed or unsupported. |
| Healthcare IT directors in Phoenix | 200 | 2 | 0 | Returned healthcare executives without contact; no usable IT-director row. |
| Finance CISOs in New York | 200 | 4 | 0 | Duplicate/conflicting Khalil Jackson rows, no contacts, secondary-list sourcing. |
| Manufacturing ops leaders in Detroit | 503 | 0 | 0 | LLM emitted a role as a name; Pydantic parse failure killed the whole query. |
| B2C/private phone prompt | 422 | 0 | 0 | Correctly blocked before search. |

Raw files: `audits/raw/zero-trust-2026-05-10/live/`.

## Operator-Fit Assessment

Thomas's core need is a small list of right people he can act on without rebuilding the research. The live Arizona run returned only David Sanders, Jill Thomas, and Shaun Creighton; it did not produce rows for Gilbert, Deer Valley, Paradise Valley, Dysart, or Maricopa, and every row had missing email and missing phone.

Lee's commodity-buyer prompt exposed the same failure from a different angle. The product returned named people, but the first row had a claimed email while every validation field failed on a 403 source. That is exactly the false-confidence shape Lee warned against: a CSV can only be trusted if the user-facing CRM columns are grounded before the audit columns.

The healthcare UI run is worse than the direct API sample because it returned a President & CEO row for an IT-director prompt, marked Fit 95-100% and Evidence 99-100%, then buried the problem under a large validation card.

## Classification

Under the northstar usable-lead definition:

- `usable`: 0 rows.
- `noisy_failed`: every returned person row.
- `organization_only`: only appeared in one browser healthcare run, not in the direct benchmark JSON.
- `not_found`: 0 rows, even for named accounts that should have explicit not-found outcomes.
- `failed query`: manufacturing prompt.

## Root Cause

The product can now label rows as non-usable, but the search/extraction loop still cannot reliably find or classify the right targets. It returns a few plausible-looking rows, then the UI and scores make those rows feel more substantial than they are.

## Required Reset

Do not continue W6/dogfood work. The next product benchmark must be target-account coverage first:

- For Thomas Arizona K-12: produce all 8 target accounts as `person_lead`, `organization_only`, `not_found`, or `failed`.
- A named account that lacks a validated person must appear as `organization_only` or `not_found`, not disappear.
- A person row without verified or deduced contact cannot be CRM-ready.
- Search success is measured by operator actionability, not by any nonzero row count.
