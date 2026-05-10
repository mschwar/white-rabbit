# 06 - v1 / proxy-lead Diff

**Verdict:** v1 was not a better data product, but it was a clearer operator product.

## What v1 Got Right

The frozen Streamlit app kept the operator story tighter:

- H1: `Find Your Target.`
- One target input.
- A small set of example briefings.
- A direct `Deploy Agent` command.
- A results table with Name, Title, Organization, Email, Email Status, Confidence, Evidence, Source URL.
- A right-side lead dossier.
- A single `Export CRM CSV` button.
- Ops/training panels hidden behind `?ops=1`.

The old app made the first action obvious and put the result in a table/dossier/export shape that resembles the sales workflow.

## What v1 Must Stay Dead

The v1 app was demo/fixture-heavy. `demo_data.py` hardcodes preverified examples, old email statuses, and VoIP/K-12 language. It also relied on Streamlit and a looser data contract. Do not move v2 back to v1 code.

## What v2 Lost

v2 added a stronger stack and better validation vocabulary, but lost the calm operator path. It now presents bucket cards, score pills, usage cards, Full/Scout modes, validation labels, large nested rows, feedback buttons, and export hidden behind Full mode. The result is more precise internally but worse as a sales-rep tool.

## What To Restore Conceptually

Restore v1's product shape, not its implementation:

```text
Find Your Target
single query
table of CRM-facing rows
selected-row evidence dossier
export CSV
```

Keep the stronger v2 validation contract under that surface. The operator should not have to understand the rebuild architecture to judge a lead.
