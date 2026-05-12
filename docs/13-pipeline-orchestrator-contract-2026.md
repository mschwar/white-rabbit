# 13 - Pipeline Orchestrator Contract 2026

**Status:** Active high-level pipeline contract for the live demo and orchestrator implementation.
**Created:** 2026-05-10.
**Source artifacts:** `/Users/mschwar/Downloads/table.csv` and `/Users/mschwar/Downloads/White_Rabbit_Pipeline_Orchestrator_Sheet_2026.xlsx`.
**Authority:** Implements ADR-013 and supports `docs/Orchestrator_Agent_Implementation_Brief.md`.

## Fresh Eyes Philosophy 2026

High volume is not the problem. Opaque or low-confidence volume is the problem.

White Rabbit's superpower is surfacing 50-500+ candidates when the public web supports that universe, then making the result set instantly understandable through categorization, per-field evidence, provenance, and concise reasons. The operator should trust every `READY` row because the system also makes it obvious why the other rows are `REVIEW`, `ORG-ONLY`, or `NOT FOUND`.

Agentic systems make the scale possible only when every handoff is verified, logged, and inspectable. The pipeline must produce auditable artifacts, not polished guesses.

The April 2026 New Mexico school-district IT proof point narrows the first implementation target: source-assisted research workbooks. The orchestrator should accept or gather public-source evidence, not depend solely on generic autonomous search. A human/chatbot/source workflow that finds rosters, staff pages, PDFs, and district technology pages is valid input. The pipeline's job is to compile that evidence into verified contacts, review/manual-lookup rows, not-found rows, and a sales-first export.

## Pipeline At A Glance

```text
DISCOVER -> EXTRACT -> VERIFY -> SYNTHESIZE -> ORCHESTRATE & DELIVER
```

| Stage | Objective | Orchestrator directive | Success signal |
| --- | --- | --- | --- |
| `DISCOVER` | Surface broad yet relevant candidates and source evidence from a target. | Decompose the target, prioritize authoritative/public rosters and source maps, accept operator-supplied URLs or seed files, spawn parallel discoverers where safe, aggregate, dedupe, preliminarily triage, and log source diversity. | Source-backed coverage of the target universe; 50+ categorized candidates where the market supports it; manual-oracle replay can be reproduced or improved. |
| `EXTRACT` | Pull structured, evidence-linked data from pages and modern layouts. | Dispatch targeted extract agents per page type, capture raw evidence, timestamps, and per-field confidence. | Key-field extraction above 95%; evidence links valid; extraction rationale logged. |
| `VERIFY` | Establish ground truth for every claim/contact with zero unlabelled guesses. | Run independent verifiers per field, enforce consensus or explicit status, build provenance graph, flag contradictions. | Per-field status on 100% of surfaced rows; key claims corroborated; contradictions visible. |
| `SYNTHESIZE` | Turn vetted data into operator-ready buckets, dossiers, scores, and narratives. | Package vetted context and verification graph, generate buckets, validate output contract, produce aggregate market insights. | Bucket consistency above human-agreement threshold; every `READY` row has complete field support and grounded rationale. |
| `ORCHESTRATE & DELIVER` | Maintain state, quality gates, human review, and exact UI/export artifacts. | Preserve global state, enforce handoff gates, route `REVIEW` rows with context, deliver Results/Evidence, Mobile, and Export artifacts. | Full audit trail on every exported row; review queue actionable in under 3 clicks; any decision traceable to source evidence in one tap. |

## Core Operating Principles

- Plan, then execute in parallel where safe.
- Verify at every handoff; do not trust upstream output by default.
- Reflect and decide: continue, route deeper, or escalate to human review.
- Produce auditable artifacts every time: source URLs, field status, validation trace, rationale, and checked timestamp.
- Maintain persistent, queryable state across runs for source reputation, vertical patterns, and correction learning.
- Treat human-in-loop as first-class for `REVIEW` only; `READY` must be automated with strong guarantees.
- Make cost, latency, and quality routing explicit and logged.

## Fresh Eyes Leverage

The pipeline should bias toward 2026 agentic leverage where it directly improves evidence quality:

- WebMCP or other structured site interfaces when available for hallucination-free pulls.
- VLM + DOM cross-validation for pages where HTML alone misses layout context.
- Cross-agent critique, including proposer/skeptic verification loops, before promoting a row to `READY`.
- Source and agent reputation graphs across runs so high-performing source patterns are reused and weak patterns are downgraded.
- Vertical source maps for public rosters, staff directories, district technology pages, board PDFs, and other source families that reliably beat generic search for a known market.
- Market-pulse side outputs that summarize common evidence gaps, source coverage, buying-signal patterns, and target-market shape.
- Lightweight rankers on top of LLM scores when enough corrected examples exist.
- Privacy-aware routing for sensitive verification steps, including local/on-device options where appropriate.

## Output Contract

The pipeline must directly power the live-demo UI and export:

- Categorized counts: `READY`, `REVIEW`, `ORG-ONLY`, `NOT FOUND`.
- Source-assisted input summary: which URLs, rosters, seed files, or pasted source packs were used, deduped, skipped, or blocked.
- Per-lead evidence dossier with field support for name, title, organization, email, phone, and source.
- Field status, evidence link, and rationale for each supported or unsupported claim.
- Grounded `why_target` and grounded opener/icebreaker only when evidence quality supports it.
- Full provenance/audit trail for export, with sales columns first and audit columns later.
- Aggregate stats and market insights that explain the shape of the result set.
- Mobile-ready compact row data with one-tap evidence access.
- Low-signal state that shows returned rows but clearly explains why the run is below volume expectations and suggests broadening the target.

## Demo Copy Rules

Live-demo UI must use customer-safe operator language:

- Use `READY`, `REVIEW`, `ORG-ONLY`, and `NOT FOUND`.
- Do not show internal labels such as `high_trust_usable` unless inside audit/export metadata.
- Do not mention internal people, agent prompts, sprint IDs, gate IDs, or implementation machinery.
- Use "review queue" for human judgment, not assignments or team workflow unless explicitly added later.
- Keep the first screen simple: target input, one command, result distribution expectation, and pipeline flow.
