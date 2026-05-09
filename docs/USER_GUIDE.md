# White Rabbit Red-Gate Internal Guide

**Status:** Active Matt-only guide while the validated-leads rebuild is red.
**Audience:** Matt and agents. Not Thomas/Lee daily dogfood.

White Rabbit is not currently an operator-ready lead tool. The active product truth is in [`docs/00-product-northstar.md`](00-product-northstar.md), and the current rebuild queue is in [`docs/08-agentic-buildout-plan.md`](08-agentic-buildout-plan.md).

## What You Can Use Today

Use the app only to evaluate rebuild work and verify gates.

Allowed red-gate usage:

- Matt/agent local checks.
- QA against a specific feature card or gate.
- Benchmark and validation experiments that record evidence.
- Internal inspection of hidden/deferred surfaces when needed for debugging.

Not allowed while red:

- Thomas or Lee daily prospecting.
- Customer-facing usage.
- Treating returned rows as CRM-ready leads.
- Promoting recipes, batch, Friday review, scoreboards, or sandbox reset as operator features.

## Current Core Loop Being Rebuilt

```text
natural-language B2B query
  -> bounded search plan
  -> separated candidates
  -> field-level validation
  -> evidence-backed ranking
  -> export with validation context
```

Until that loop passes benchmarks, any lead output is untrusted.

## Login And Local Access

1. Start Postgres, API, and web using the root [`README.md`](../README.md).
2. Open `http://localhost:3000`.
3. Log in with the local `WR_SHARED_PASSWORD`.
4. Use the primary lead-search path only for the feature/gate being tested.

Backend lead/search/sandbox endpoints require `WR_API_INTERNAL_TOKEN` through the Next.js proxy. Direct unauthenticated backend calls should fail.

## How To Judge Results

A usable lead must satisfy the northstar definition:

- Real person, not a company, department, title, or generic role.
- Title and organization match the query and are source-supported.
- Contact is verified, or deduced only with explicit domain-pattern evidence.
- Missing/failed/unsupported contact is clearly labeled.
- Field-level evidence travels with the row.

If a card looks plausible but lacks field-level evidence, it is not product proof.

## Current Surfaces

| Surface | Red-gate policy |
| --- | --- |
| Primary search | Allowed for feature/gate verification only. |
| Recipes | Internal/deferred. Do not present as an operator workflow. |
| Batch | Internal/deferred. Bulk bad data is product harm. |
| Friday review export | Internal/deferred. |
| Scoreboards | Internal/deferred until quality metrics are real. |
| Sandbox reset | Internal/deferred; not an operator control. |
| Operator minutes | Strategic KPI, but keep low-ceremony until usable outputs exist. |

## If A Result Looks Wrong

Record it as evidence instead of working around it:

- Query used.
- Full returned row.
- Claimed source URL.
- Which field failed: name, title, organization, email, phone, source, category, or rank.
- Independent source checked.
- Verdict: wrong persona, bad source, bad contact, duplicate, hallucinated, unverified, or not found.

Prefer adding durable fixtures or QA evidence over ad hoc notes.

## Where To Work Next

Use `STATUS.md` for the latest handoff. As of this guide, the active next pointer is F04 Query compiler / planner on the rebuild line.

Do not use legacy Sprint/BUILDOUT docs as the next-task queue.
