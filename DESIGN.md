# White Rabbit Design Direction

**Status:** Draft design authority for mockup and future RG4 UI planning.
**Date:** 2026-05-11.
**Scope:** Visual design, product hierarchy, motion, layout, copy tone, and future build-agent guidance.
**Not authorized:** Production UI implementation, reset gate advancement, backend/API/data/export/persistence changes, or logo production.

This document captures the approved design direction from the May 11 design review. It does not unlock RG4. UI implementation still waits for the active reset plan to permit R10-R12 work.

## Product Premise

White Rabbit is not a generic lead-search SaaS, CRM, chatbot, dashboard, or marketing site.

White Rabbit is an evidence sorting instrument for operators.

The operator's real job is not search. Search is the ignition. The real job is:

> Show me the candidate universe, separate what is actionable from what is uncertain, and let me trust why.

The interface must make messy public-market research become a clear operating list. Every screen must support one of three jobs:

1. **Command:** state the target clearly.
2. **Categorize:** show the market distribution honestly.
3. **Prove:** expose evidence or blockers for every row.

If an element does not help command, categorize, or prove, remove it.

## Design Thesis

The product should feel like a serious navy research instrument opening onto a white evidence table.

Use a **deep navy instrument chassis** around a **paper-white evidence surface**. The brand has gravity before results exist; once results arrive, the table and evidence become the hierarchy.

Core rule:

> The brand leads once. Then the product speaks.

This resolves the previous false choice between a blank light SaaS table and a dark sci-fi console. White Rabbit needs both gravity and restraint:

- **Gravity** comes from the navy chassis, strong wordmark, measured contrast, and a correct rabbit/lens/data-trail mark.
- **Restraint** comes from the light work surface, CRM-first table, thin dividers, quiet status language, and evidence-first row actions.

## Visual Language

### Chassis

The app should have a real system frame, not only a thin header.

Use:

- Deep navy top rail.
- Deep navy left rail on desktop.
- Paper-white work area inside the chassis.
- Subtle grid, trace, or lens geometry only when it communicates instrument focus.
- Electric blue only for signal, focus, provenance, active state, and primary command.

Avoid:

- Full dark-console product UI.
- Blank white SaaS surfaces with a blue button.
- Glassmorphism.
- Purple gradients.
- Mascot decoration.
- Heavy rounded card stacks.
- Decorative motion unrelated to finding, verifying, categorizing, or proving.

### Work Surface

The evidence table is the product. It should feel dense, clinical, and calm.

Use:

- Paper white or near-white table surface.
- Deep navy text.
- Thin cool-gray dividers.
- Compact rows around 40-46px depending on final type scale.
- CRM fields first.
- Audit/provenance details one action away.

Avoid:

- Lead cards on desktop results.
- Row layouts that become mini dashboards.
- Score-first hierarchy.
- Over-styled READY rows.
- REVIEW rows that look almost as trustworthy as READY rows.

### Status Language

Operator-facing buckets:

- `READY`
- `REVIEW`
- `ORG-ONLY`
- `NOT FOUND`
- `FAILED` only where an explicit failure state is useful; otherwise fold into `REVIEW` or `NOT FOUND` per the product contract.

READY must look complete, not celebratory.

REVIEW must look unresolved, not almost-ready.

ORG-ONLY must make the absence of a person/contact clear.

NOT FOUND must explain absence, not look like an error.

FAILED must never look exportable.

### Typography

Use a high-legibility sans family for product UI. Geist or Inter-compatible system sans is acceptable.

Use mono sparingly for:

- run IDs,
- small state labels,
- source or provenance coordinates,
- compact metrics,
- table headers.

Do not turn the whole UI into a mono-label texture. Precision is hierarchy, not decoration.

### Color Tokens

Recommended draft tokens:

```css
:root {
  --wr-navy-1000: #02040b;
  --wr-navy-950: #050916;
  --wr-navy-900: #0a1226;
  --wr-navy-850: #0d1938;
  --wr-cobalt: #0e3a8a;
  --wr-signal: #2d7bff;
  --wr-signal-soft: #e8f1ff;
  --wr-paper: #fbfcfd;
  --wr-paper-2: #f6f7f9;
  --wr-line: #e3e7ee;
  --wr-line-strong: #ced6e4;
  --wr-ink: #0a1226;
  --wr-ink-muted: #657086;
  --wr-ready: #1f7a45;
  --wr-ready-bg: #e6f5ec;
  --wr-review: #a16207;
  --wr-review-bg: #fff4e1;
  --wr-org: #536175;
  --wr-org-bg: #eef1f5;
  --wr-fail: #a13c3c;
  --wr-fail-bg: #fcebeb;
}
```

These tokens are provisional. Before implementation, add final token names to the project design system rather than hardcoding one-off values in components.

## Logo And Mark

The current generated rabbit icons are not acceptable.

The mark is a separate asset problem and must not block the product design direction. Until an approved vector exists, build agents should use a placeholder mark or existing approved asset, not redraw it.

Approved mark requirements:

- Rabbit silhouette.
- Magnifying lens.
- Rightward structured data trail.
- Blue evidence/provenance nodes.
- Legible at 16px, 24px, 32px, and large empty-state scale.
- Works on deep navy and paper-white surfaces.
- Preserves the same silhouette and geometry everywhere.

Do not:

- Recreate the mark with ad hoc CSS.
- Let an LLM invent a new rabbit.
- Use multiple unrelated rabbit drawings.
- Use a mascot illustration in the working app.
- Make the mark compete with the table after results exist.

## Core Screens

### A. Empty / Ready To Search

Goal: one composed brand moment.

The empty state is allowed to be dramatic because no data exists yet. It should establish the brand's mass, then give the operator a precise command surface.

Required:

- Deep navy chassis and brand field.
- Correct mark or placeholder mark clearly flagged as replaceable.
- Strong wordmark treatment.
- One query bay.
- One primary action.
- Helper copy that explains broad vs narrow targets.

Do not make this a landing page. Do not add marketing navigation. Do not add public SaaS copy.

Recommended copy:

- Placeholder: `VP Sales at Series B SaaS companies in NY`
- Button: `Find Candidates`
- Helper: `Broad targets return a categorized market view. Narrow targets return a tighter review set.`

### B. Running / Loading

Goal: the instrument is alive.

Required:

- Chassis remains visible.
- Query is compact in the header/work surface.
- Stage label is prominent.
- Counts update realistically, not theatrically.
- Table begins to form with skeleton rows and partial rows.

Preferred stage labels:

- `Finding companies`
- `Matching people`
- `Checking contact evidence`
- `Categorizing rows`

Avoid fake precision. Avoid spinner-only states.

### C. High-Volume Results

Goal: calm density.

The table is the hero.

Required:

- Chassis recedes.
- Brand compresses to rail-level identity.
- Summary band becomes a control strip.
- Table fields are CRM-first:
  - Company
  - Person
  - Role
  - Location
  - Email
  - Phone
  - Source
  - Status
  - Evidence
- `ALL`, `READY`, `REVIEW`, `ORG-ONLY`, `NOT FOUND` filters are visible.
- `Export READY rows` is available but secondary to the table.
- Evidence action is available for every row.

Do not add cards, scoreboards, recipe surfaces, batch surfaces, or implementation-status copy.

### D. Evidence Review

Goal: proof without losing context.

Required:

- Selected row remains visually anchored in the table.
- Evidence panel opens beside the table on desktop.
- Evidence panel becomes a full-screen or bottom sheet on mobile.
- Panel begins with status and primary blocker.
- Field-level evidence is structured by field.
- Source trail is visible and scan-friendly.

Recommended panel order:

1. Header: `Evidence: [Person] @ [Company]`
2. Verdict: `Status: REVIEW`
3. Primary blocker.
4. Field evidence.
5. Source trail.
6. Secondary actions.

Safe footer actions:

- `Copy evidence`
- `Keep in review`
- `Mark failed`

Avoid `Force to READY` or any language implying evidence can be overridden casually.

### E. Low-Signal / Weak Market

Goal: honest reporting.

Required:

- Summary counts tell the story first.
- Low-signal notice appears between counts and table.
- Returned rows remain visible.
- Copy explains low public data footprint without shame or jargon.

Recommended copy:

```text
Low Public Signal
This market has a low public data footprint. Most candidates lack enough traceable contact evidence to mark READY.
```

### F. Mobile Review

Goal: triage and evidence checking on the go.

Mobile is not the full research-control surface.

Required:

- Compact navy header.
- Horizontal bucket pills.
- Compact row cards.
- `Inspect Evidence` as thumb-safe action on review rows.
- Evidence opens as a full-screen or bottom sheet.
- No horizontal overflow.

## Copy Rules

Use operator-facing language only in the product UI.

Use:

- `Find Candidates`
- `READY`
- `REVIEW`
- `ORG-ONLY`
- `NOT FOUND`
- `Evidence`
- `Source`
- `Blocker`
- `Last checked`
- `Export`
- `Low Public Signal`

Do not use product UI copy that references:

- prompts,
- gates,
- sprints,
- agents,
- benchmarks,
- correction loops,
- pipeline internals,
- implementation plans,
- internal people names,
- AI magic language.

The product should not flatter its intelligence. It should show its work.

## Relationship To Existing Mockups

The prior mockup at `docs/mockups/final-product-2026-05-10/index.html` remains useful for product structure but is no longer sufficient as visual direction.

Keep from the prior mockup:

- one command input,
- high-volume categorized output,
- CRM-first results,
- evidence one action away,
- low-signal state,
- mobile triage structure.

Replace from the prior mockup:

- generic light SaaS feel,
- weak brand presence,
- CSS-drawn rabbit mark,
- low-gravity empty state,
- purely table-on-white presentation.

The strongest current direction is:

> V3 product structure plus the brand schema's gravity, with the mark treated as pending vector source.

## Design-System Updates Required Before Implementation

Before any RG4 implementation, add or update tokens for:

- navy chassis surfaces,
- paper work surfaces,
- signal blue,
- status text/background pairs,
- table row height,
- left rail width,
- top rail height,
- evidence panel width,
- selected-row treatment,
- focus ring,
- compact icon button,
- summary control strip,
- empty-state query bay,
- evidence source card.

Component primitives needed:

- `AppChassis`
- `TopRail`
- `LeftRail`
- `QueryBay`
- `SummaryControlStrip`
- `ResultsTable`
- `StatusLabel`
- `EvidenceButton`
- `EvidencePanel`
- `LowSignalNotice`
- `MobileBucketNav`
- `MobileResultCard`
- `EvidenceSheet`

These names are implementation guidance, not a requirement to create new abstractions if the existing component structure can absorb them cleanly.

## Future Build-Agent Notes

Do not implement this until RG4/R10-R12 are unlocked by the active reset plan.

When implementation is approved, keep the write scope to web UI files only. Do not edit backend, API contracts, core logic, data models, persistence, exports, search behavior, benchmark harnesses, or reset gate statuses.

Likely files to inspect first:

- `apps/web/src/components/scout-workspace.tsx`
- `apps/web/src/components/scout-results-table.tsx`
- `apps/web/src/app/globals.css`
- existing brand assets under `apps/web/public/brand/`

Expected high-level changes after approval:

- Replace the current glass/dark-card workspace with the navy chassis + paper evidence surface.
- Replace score/gate-forward visual hierarchy with bucket/status/evidence hierarchy.
- Convert desktop results to a compact CRM-first table.
- Move evidence into a persistent side inspector.
- Preserve current functionality exactly.
- Hide or quarantine recipe, batch, scoreboard, Friday review, and sandbox reset surfaces from the primary operator path while product remains red.

## Mockup Agent Copy-Paste Prompt

Use this prompt for the next design/mockup agent:

```text
Create White Rabbit visual mockups from the repo DESIGN.md direction.

Do not implement production code.
Do not change backend, APIs, data models, exports, persistence, search, benchmark harnesses, reset statuses, or gates.

Design direction:
White Rabbit is an evidence sorting instrument for operators. It should feel like a serious deep-navy research instrument opening onto a paper-white evidence table.

Core rule:
The brand leads once. Then the product speaks.

Use a deep navy top/left chassis, a paper-white work surface, electric blue as signal/provenance, and restrained status colors. The empty state may have one composed brand moment. Once results exist, the table and evidence hierarchy must dominate and the brand must recede to rail-level identity.

The current rabbit icon is not approved. Do not redraw it. Use a clearly replaceable placeholder until an approved vector mark exists. The approved mark must be rabbit silhouette + magnifying lens + rightward data trail + blue evidence nodes.

Required mockups:
1. Empty / Ready To Search
2. Running / Loading
3. High-Volume Results
4. Evidence Review
5. Low-Signal / Weak Market
6. Mobile Review

Required product structure:
- one query input,
- one primary action: Find Candidates,
- high-volume bucket counts,
- CRM-first results table,
- READY / REVIEW / ORG-ONLY / NOT FOUND row separation,
- evidence action on every row,
- evidence panel/sheet,
- low public signal notice,
- mobile triage cards.

Do not create a landing page, SaaS dashboard, chat UI, mascot-led interface, recipe library, batch workflow, public signup, account system, billing UI, or marketing navigation.

Quality bar:
In two seconds, an operator should know what target was searched, how many candidates exist, how many are READY, which rows need review, and where to inspect evidence.

If the brand attracts more attention than the result table after results exist, the mockup is wrong.
If REVIEW looks almost as trustworthy as READY, the mockup is wrong.
If evidence feels hidden, the mockup is wrong.
If it looks like generic SaaS, the mockup is wrong.
```

## Open Items

- Create or source the approved vector mark.
- Decide whether to commit a refreshed mockup under `docs/mockups/` after Matt reviews the next visual pass.
- After mockup approval, update active reset docs only if Matt explicitly approves replacing the May 10 mockup as the RG4 visual reference.
- Keep this document draft until that approval is recorded.
