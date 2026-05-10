# 04 - QA / Gate Process

**Verdict:** process improved on paper, then drifted again.

## What The Repo Claims

The active gate doc says W5 cannot advance until a browser user can complete query -> validated results -> evidence review -> export, with CSV inspection and screenshots. W6 is supposed to make the dogfood decision only after feedback and launch-gate evidence.

## What Exists

Only W1-W4 gate reports exist:

- `.gstack/qa-reports/gate-w1-red-state-containment.md`
- `.gstack/qa-reports/gate-w2-search-contract.md`
- `.gstack/qa-reports/gate-w3-validation-engine.md`
- `.gstack/qa-reports/gate-w4-benchmarks-quality.md`

No W5 gate report exists. No W6 gate report exists. Yet F13-F19 are merged.

## Gate Failure

W5 should currently be a hold:

- Authenticated `/scout` still shows Scout/Full mode, location filter, usage quota, score cards, and internal-ish concepts.
- Export exists only after choosing Full mode, not as a clean primary query-to-export path.
- The saved healthcare export included all validation columns, but the first columns are generated/run metadata, not Lee's CRM-facing order.
- Browser query-to-export works mechanically, but live output has 0 usable rows.

W6 should be blocked:

- The product is still red under `docs/00-product-northstar.md`.
- There is no evidence that Thomas or Lee can complete a query without re-researching most rows.
- Feedback UI exists, but it attaches to bad rows before the product can create enough trusted rows.

## Why Prior Audits Missed It

The previous audits found many real issues, but subsequent gates accepted deterministic feature completion instead of re-running the operator loop from evidence. The W4 report explicitly skipped live Arizona verification because live keys were absent in that shell. In this audit, local app keys were available, and the live run proved the gap remains.

## Required Reset

Write a W5 hold report before any new feature work. The hold criteria should be:

- 0 usable live benchmark rows,
- missing W5 report,
- export not operator-ordered,
- query-to-export works mechanically but not product-wise.

Then set W6 and all deferred feature work to blocked until the reset plan is accepted.
