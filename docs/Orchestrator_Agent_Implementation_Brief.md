# Orchestrator Agent Implementation Brief

**Status:** Active implementation brief for high-volume transparent tiering.
**Created:** 2026-05-10.
**Authority:** Implements ADR-013, `docs/13-pipeline-orchestrator-contract-2026.md`, and the reset plan before kickoff.

## Core Philosophy

The previous 10-25 row target was minimum escape velocity from the real failure: broad queries returning only 3-4 rows. It is not the ideal end state.

New principle:

> It is great to get 500 leads as long as it is instantly clear at a glance why 450 of them are not actionable and exactly what evidence, or lack of evidence, supports that conclusion.

Volume is a feature only when the system makes the distribution obvious and explains every blocker. White Rabbit should surface the full realistic picture the public web allows, apply rigorous checking, and make the output glanceable enough that an operator can understand both the usable rows and the non-usable rows immediately.

Hard constraints:

- Never create false confidence.
- Never invent names, emails, titles, organizations, contacts, or evidence.
- Every explanation and category decision must be grounded in supplied search result content or saved source evidence.
- Anti-bias rules remain in force; do not inject unsolicited VoIP, telecom, or other vertical language.

## Volume And Quality Targets

| Query type | Target | Notes |
| --- | --- | --- |
| Broad vertical + geography | 50-500+ categorized candidates | Primary high-volume mode. 10-25 is only the floor. |
| Named account / narrow | 5-30 categorized candidates | Keep tight when the target universe is genuinely small. |
| High-trust usable tier | At least 70% precision on benchmarks | Non-negotiable; do not loosen this tier to increase volume. |

## Pipeline Flow

The orchestrator stages are:

```text
DISCOVER -> EXTRACT -> VERIFY -> SYNTHESIZE -> ORCHESTRATE & DELIVER
```

Operating principles across all stages:

- Plan, then parallelize where safe.
- Verify at every handoff.
- Reflect and decide whether to continue, deepen, or route to human review.
- Produce auditable artifacts: provenance, per-field status, verification trace, confidence rationale, and checked timestamp.
- Keep state persistent and queryable for lead graph, source reputation, and correction memory.
- Treat human review as first-class for the `review` tier only.
- Log cost, latency, quality, and routing decisions.

## Required Architecture

### 1. Increase Raw Candidate Volume

Files:

- `packages/core/src/core/search.py`
- `packages/core/src/core/query_planner.py`

Required changes:

- Make `max_results` a parameter to `scout()` with a broad-query default closer to 30-50 raw search results per run.
- Tavily caps individual calls at 20 results, so use multi-query planning, client-side aggregation, and deduplication to reach higher totals.
- Add `aggressive_breadth: bool = False` for exploratory broad runs.
- Expand role synonyms intelligently for broad intents, for example IT Director, Director of Technology, Head of IT, CIO, CTO.
- Use geographic or vertical expansion only when the query is clearly broad.
- Keep every generated vendor query under `SAFE_VENDOR_QUERY_LENGTH`.

Goal after this layer: a broad query such as "K-12 IT decision makers in Arizona" should yield 100-500+ unique raw search hits before LLM extraction when the public web supports it.

### 2. Replace Binary Output With Tiered Output

The old flow filters too aggressively: LLM extraction -> validation -> hard evidence gate -> only a few survivors. Keep the old strict gate as the definition of `high_trust_usable`, but stop using it as the only return path.

New output tiers:

- `high_trust_usable` - strict evidence gate passed; CRM-ready.
- `review` - plausible person lead with partial evidence, medium scores, missing contact, or another explicit limitation.
- `organization_only` - target account found but no usable person validated.
- `not_found` - target searched, no acceptable contact/person found.
- `failed` - rejected because evidence contradicts or does not support the claim.

Files:

- `packages/core/src/core/models.py`
- `packages/core/src/core/orchestrator.py`

Required changes:

- Add non-breaking model fields such as `tier`, `primary_filter_reason`, and `detailed_reasons`.
- Add `compute_tier_and_reasons(candidate)` in orchestration.
- Return all tiers, or at least the top N per tier, with tier summary metadata.
- Treat old `max_leads` as a cap on `high_trust_usable` or as a global soft cap, not as the raw discovery ceiling.

### 3. Rewrite The Extraction Prompt

The LLM stage must become inclusive. Server-side orchestration owns strict tiering.

Core prompt language:

```text
Your primary job is to extract every relevant decision-maker mentioned anywhere in the supplied search results. The downstream orchestration layer will perform rigorous tiering, scoring, and annotation.

Do not pre-filter or omit candidates simply because the evidence feels incomplete or the person is only mentioned in passing.

For every candidate you extract, assign the most accurate candidate_category and produce a clear, specific primary_filter_reason, 1-2 sentences, that explains why this row belongs in its category and whether it is immediately actionable.

Be conservative on contact status and evidence strength. When in doubt, use the more cautious label and state the limitation explicitly.
```

Additional prompt requirements:

- Expand candidate category guidance with borderline examples.
- Keep and strengthen email deduction rules.
- Keep and strengthen anti-bias rules.
- Make `primary_filter_reason` mandatory.
- Use scores for ranking within tiers and tier assignment, not as unsupported optimism.
- Generate icebreaker/cold-opener copy only for person leads with at least medium evidence.

### 4. Add Tier Observability

Files:

- `packages/core/src/core/source_validation.py`
- `packages/core/src/core/quality_report.py`
- `packages/core/src/core/benchmark_suite.py`

Required changes:

- Emit tier distribution summary, for example 37 high-trust usable, 82 review, 143 organization-only, 219 not-found, 67 failed.
- Measure total volume surfaced on broad and narrow prompts.
- Preserve high-trust precision measurement.
- Track rough recall or coverage on known-good entities.
- Spot-check explanation quality in benchmark reports.
- Expose cost and latency guardrails such as `max_results`, `aggressive_breadth`, and budget/early-stop controls.

### 5. Produce The UI/Export Output Contract

The pipeline must produce exactly what the mockups consume:

- Categorized counts for `READY`, `REVIEW`, `ORG-ONLY`, and `NOT FOUND`.
- Per-lead evidence dossier with field support rows for name, title, organization, email, phone, and source.
- Each field support row has status, evidence link, and rationale.
- Grounded `why_target` and grounded icebreaker/opener only when evidence quality supports them.
- Contradictions or conflicting source signals surfaced explicitly when present.
- Full provenance/audit trail for export, with sales columns first and audit columns later.
- Aggregate stats and market insights describing the result distribution.
- Mobile-ready compact row shape with bucket, reason, key contact status, and one-tap evidence.
- Low-signal state for runs below volume expectations, with returned rows still visible and broadening suggestions.

## Implementation Order

1. Update `query_planner.py` and `search.py` for higher raw search volume, aggregation, and dedupe.
2. Update `models.py` with tier and reason fields.
3. Update `orchestrator.py` with inclusive extraction prompt, `compute_tier_and_reasons`, and all-tier annotation.
4. Update tests, `benchmark_suite.py`, and `quality_report.py`.
5. Add broad-query benchmark cases where needed.
6. Update docs and northstar references only after code behavior is verified.

## Success Criteria

- Broad realistic prompts produce at least 50 categorized candidates, ideally 100-500+ when the public web supports it.
- The `high_trust_usable` tier maintains the existing precision bar on Arizona K-12 and similar golden sets.
- Every candidate has a specific `primary_filter_reason` that a sales rep can read in under 3 seconds.
- The operator can immediately answer: how many real decision-makers are publicly findable, and what blocks the rest?
- Anti-bias, grounding, and no-false-confidence rules do not regress.
- Cost per broad query remains reasonable, targeting less than 3-4x current cost for 5-10x more candidates.

## Copy-Paste Prompt For Prompt A

```text
You are an expert Python engineer working on the White Rabbit B2B lead research system.

Your task is to evolve the orchestrator and supporting modules from a low-volume strict filter to a high-volume plus rigorous transparent tiering system.

Read and internalize docs/Orchestrator_Agent_Implementation_Brief.md, docs/00-product-northstar.md, docs/12-reset-gated-implementation-plan-2026-05-10.md, and docs/03-decisions.md.

Key outcomes required:
- Broad queries surface 50-500+ categorized candidates instead of single digits when the market supports it.
- A new tiered classification, high_trust_usable | review | organization_only | not_found | failed, replaces the binary gate for returned output.
- The LLM extraction stage becomes deliberately inclusive; tiering and annotation happen server-side.
- Every candidate receives a clear, glanceable primary_filter_reason.
- The strict high-trust tier maintains high precision on existing benchmarks.
- All changes stay grounded in the northstar: no false confidence, anti-bias, evidence-based reasoning.

Start by exploring packages/core/src/core/orchestrator.py, search.py, query_planner.py, and models.py.

Proceed in the order in the brief. After each logical change, run the existing tests and benchmark suite relevant to the edited modules.

When done, summarize files changed, new parameters, tests run, and any operator/caller-visible behavior changes.

Do not reduce the strictness of the high_trust_usable tier. Volume increases must not come at the expense of precision on the actionable bucket.
```
