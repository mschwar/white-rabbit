# Lee Workflow Product Thesis

Created: 2026-06-03

## Foundation Change

The current White Rabbit north star names Thomas as the primary B2B product signal and Lee as secondary generalization/demo signal. This reset intentionally changes the foundation: the next product direction centers Lee's actual workflow.

That does not mean Thomas stops mattering. It means the next build should first automate the repeatable work Lee is already doing with agents: produce public-source prospecting artifacts, validate what can be validated, keep privacy boundaries, and hand off a usable workbook or CSV.

Sources: `docs/00-product-northstar.md`, `GMAIL-LEE-01`, `GMAIL-LEE-02`, `GMAIL-LEE-03`, `GMAIL-LEE-04`, proxy-lead `docs/demo/LEE_THOMAS_SCOTTY_REPORT_2026-05-05.md`.

## What Lee Actually Does

From the email evidence, Lee's workflow is:

1. Start with a concrete sales or demo bucket.
2. Use an AI agent/chatbot/Codex workflow to gather public-source contacts or offices.
3. Keep output in a CSV/workbook shape.
4. Prefer direct person contacts when public evidence supports them, but accept public office/unit contacts where privacy or source limits require that.
5. Put sales-usable fields first.
6. Preserve validation and run details behind the primary sales columns.
7. Continue partially completed work, fix weak rows, regenerate outputs, and rename files so they are easy to use.

Sources: private index `/Users/mschwar/Documents/white-rabbit-private/lee-reset/index.md`; `GMAIL-LEE-01`; `GMAIL-LEE-02`; `GMAIL-LEE-03`; `GMAIL-LEE-04`.

## Product Decision

White Rabbit should be rebuilt as a source-assisted concierge automation tool before it tries to be an autonomous lead finder.

The useful product is not:

```text
natural language prompt -> fully autonomous magic list -> dogfood
```

The useful product is:

```text
customer bucket or seed list
-> public source research with visible search/work trail
-> checked workbook rows
-> sales-first export
-> operator review and refinement
-> delivered briefing
```

Sources: `docs/00-product-northstar.md`, `docs/13-pipeline-orchestrator-contract-2026.md`, `docs/03-decisions.md` ADR-019, `GMAIL-LEE-03`, `GMAIL-LEE-04`.

## Minimum Product Shape

The next product should support one job:

> Given a target bucket and any seed material, help Lee produce a source-backed sales workbook that is good enough to deliver without starting over manually.

Minimum capabilities:

- Accept a target, seed list, pasted GPT output, uploaded CSV/doc, or source URLs.
- Search public sources with scoped queries and record the search trail in operator-readable language.
- Extract rows into a workbook shape with sales fields first.
- Mark each row as `ready`, `review`, `manual_lookup`, `organization_only`, or `not_found`.
- Never mark unsupported contact data as ready.
- Let the operator correct rows and rerun or continue a job.
- Export CSV/XLSX with simple names.

Sources: `docs/00-product-northstar.md`, `docs/13-pipeline-orchestrator-contract-2026.md`, `GMAIL-LEE-02`, `GMAIL-LEE-04`.

## What to Stop Doing

- Stop treating autonomous broad search as the first proof point.
- Stop hiding product uncertainty behind gates, scores, and status language.
- Stop making UI/export polish prove lead quality.
- Stop building public SaaS surfaces before the Lee workflow is repeatable.
- Stop adding ceremony unless it shortens the path from target bucket to deliverable workbook.

Sources: `STATUS.md`, `docs/reset-current-assignment.json`, `docs/12-reset-gated-implementation-plan-2026-05-10.md`.

## Success Criteria

The first reset should pass only if Lee can use it to produce or refine a real prospecting artifact faster than his current agent/manual workflow.

Practical bar:

- One target bucket goes from prompt/seed to checked CSV/XLSX in one session.
- The output has sales columns first.
- Every ready row has public evidence.
- Every non-ready row has a clear reason or next action.
- The operator can find the output file without help.
- The product preserves the search/work trail enough for Matt to audit it later.

Sources: `GMAIL-LEE-02`, `GMAIL-LEE-03`, `GMAIL-LEE-04`, proxy-lead `docs/demo/LEE_THOMAS_SCOTTY_REPORT_2026-05-05.md`.

## Stack Implication

The reset does not need to start with a full Next/FastAPI/Postgres rebuild. The stack should be chosen after the workflow is proven.

Conservative starting point:

- A small local/operator app or script-driven workspace that accepts a target and seed artifacts.
- Python for extraction, source checking, CSV/XLSX generation, and continuation state.
- Minimal UI only where it helps review/correct/export.
- Later web app only after Lee can finish a real workbook with less manual effort.

Sources: proxy-lead `README.md`, proxy-lead `PRD.md`, `docs/02-stack.md`, `STATUS.md`.
