# First-Principles Reset Execution Prompts

Created: 2026-06-03

These prompts are intentionally short. They are not a new gate system.

## Prompt 1 - Gather and Annotate Evidence

```text
Work in /Users/mschwar/Documents/white-rabbit. Do not edit product code.

Create or update the private evidence folder at /Users/mschwar/Documents/white-rabbit-private/lee-reset/. Use Gmail connector search/read tools to summarize, not dump, the White Rabbit evidence threads:

- GMAIL-LEE-01: 19e0e8dcf8ad1322
- GMAIL-LEE-02: 19e0eb0b801090da
- GMAIL-THOMAS-01/02/03: 19e08ef2c7c42bf6, 19e08fb5a55a240d, 19e092b5ad3e10a1
- Search once for recent Lee/Thomas White Rabbit, OrgAtlas, GPT, ZoomInfo, Scotty, CSV, school-district, and commodity-buyer threads.

Write one private index.md and short private per-thread summaries. Do not commit raw email bodies. The goal is to capture workflow signal: what Lee or Thomas tried, what artifact they produced, what failed, and what product behavior it implies.
```

## Prompt 2 - Write the Three Reset Docs

```text
Using the private Lee evidence index, write docs under docs/first-principles-reset/:

1. 01-white-rabbit-v2-postmortem.md
2. 02-proxy-lead-v1-summary.md
3. 03-lee-workflow-product-thesis.md

Keep the packet lean. Cite sources by repo path, proxy-lead path, or Gmail message ID. Do not quote private email bodies. Do not add a manifest schema, new gate process, or long provenance table.

The v2 postmortem must say the north-star thesis was sound but the reset machinery and autonomous-search assumption overwhelmed the product. The proxy-lead summary must explain what the Streamlit v1 demo proved and did not prove. The Lee thesis must explicitly call out the target-user pivot from Thomas-first to Lee-centered workflow automation.
```

## Prompt 3 - Force the Product Decision

```text
Read docs/first-principles-reset/01-white-rabbit-v2-postmortem.md, 02-proxy-lead-v1-summary.md, and 03-lee-workflow-product-thesis.md.

Produce a one-page decision memo that answers:

- Are we building an autonomous lead finder or a source-assisted concierge automation tool?
- What evidence supports that choice?
- What is the smallest useful next product slice Lee can use?
- What should be explicitly out of scope?

Do not soften the answer. If the evidence points to source-assisted concierge automation, say that directly and describe the first slice in operator terms, not reset-gate terms.
```

## Prompt 4 - Optional Implementation Starter

```text
Design the first implementation slice for Lee-centered source-assisted workbook automation.

Scope it to one local/operator workflow:
target bucket or seed artifact -> public-source research trail -> checked rows -> sales-first CSV/XLSX -> clear output filename.

Do not start with public SaaS, accounts, billing, a full Next/FastAPI/Postgres rebuild, or autonomous broad-search benchmarks. Use the simplest stack that lets Lee finish a real workbook faster than his current agent/manual workflow.
```

## Acceptance Checks

- The committed docs contain no raw private email bodies.
- Every major claim cites a Gmail message ID or a repo/proxy-lead source path.
- The thesis forces the autonomous-lead-finder vs source-assisted-concierge decision.
- The packet can be read in one sitting.
