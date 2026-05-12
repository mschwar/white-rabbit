# 01 — Operator Model, Recipes, Scores, Run Model

**Status:** Archived Reference with active concepts.
**Current product truth:** See `docs/00-product-northstar.md`.
**Current reset execution:** See `docs/12-reset-gated-implementation-plan-2026-05-10.md`.

This document describes the original operator/recipe/scoring model. Keep the strategic concepts, but defer to the product northstar for current usable-lead, validation-by-field, and red/yellow/green gate rules.

## Operator model

Three operators, two distinct workflows sharing one toolset.

| Operator | Role | Workflow | Signal value |
|---|---|---|---|
| Matt | Builder + fulfillment operator | Runs the tool to produce paid customer briefings (e.g., Scotty POC). | Tells us whether the tool can fulfill paid work efficiently. |
| Thomas | Embedded design partner (B2B) | Runs the tool inside his own daily B2B sales prospecting at his employer. | **Primary signal.** Real working salesperson + ICP-aligned use case. |
| Lee | Embedded design partner (DTC) | Runs the tool inside his own DTC prospecting. Also presents the Scotty demo to customers. | Tests whether the tool generalizes outside obvious B2B sales motions. |

Lee and Thomas are **not OrgAtlas employees**. Commercial arrangement is an open question (see `STATUS.md`). Build can ship without it; public content cannot.

### Why "self-serve internal"

Building self-serve from day 1 is a forcing function. If Thomas can't run the tool without asking Matt, that's a P0 UX bug, not a "Matt will help." This avoids accumulating operator-handholding debt that becomes painful when external customers eventually arrive.

## The "recipe" — the unit of work

**Red-gate caveat (2026-05-09):** Recipes are internal/deferred while the product is red. The primary operator path should not expose recipe library, batch, Friday review, or scoreboard surfaces until validated-lead quality gates allow it.

A **query** is one-shot. A **recipe** is reusable IP.

A recipe stores:

- **Query** — the natural-language target description ("K-12 IT Directors in Albuquerque").
- **Filters** — geographic, vertical, role-level, organization-size constraints.
- **Source mix** — which web sources / search APIs / domains are weighted high/low.
- **Ranking weights** — how Fit/Evidence/Contact scores compose into the gate threshold (default: each ≥ 0.6).
- **Outcomes** — for every run of this recipe: leads returned, leads marked usable, minutes spent reviewing, API cost.

Recipes are stored in Postgres starting Sprint 2. Sprint 1 ships Scout-only with no persistence.

**Why recipes matter strategically.**

If recipes reuse across customers (e.g., a recipe Thomas built for K-12 IT directors works again for a customer in K-12 SLED), the boutique model has operating leverage and the kill/keep gate likely passes. If every customer needs a custom recipe build, the boutique model is bespoke labor and the gate likely fails. **Recipe reuse is the most important hypothesis the product tests.**

## Score model

**Red-gate caveat (2026-05-09):** Fit, Evidence, and Contact remain product concepts, but they must be driven by server-side field validation. Do not treat LLM-generated scores or old lead cards as product proof.

Three visible per-lead scores. **Composite is a gate, not a rank.**

| Score | What it measures | Range |
|---|---|---|
| **Fit** | Does this person/org match the target ICP? Title match, organization match, level match. | 0.0–1.0 |
| **Evidence** | How strong and fresh are the supporting sources? Number of distinct sources, source authority, date of source. | 0.0–1.0 |
| **Contact** | How usable is the email/phone/title information? Email status (Found > Deduced > Missing), phone presence, title precision. | 0.0–1.0 |

### Gate semantics

A lead "passes the gate" when **all three scores meet their thresholds**. Default thresholds: each ≥ 0.6. Configurable per-recipe.

UI shows passed leads above a visual divider, failed leads below (greyed). Operator sorts the passed leads by whichever score matters today.

```
Fit  Evid  Cont   Lead
0.91  0.87  0.95   ✓  Jane Doe — IT Dir, ABQ ISD
0.88  0.92  0.40   ✓  John Roe — IT Dir, Rio Rancho
0.95  0.71  0.85   ✓  Ana Vega — CIO, Sandoval
──── threshold gate ────
0.62  0.81  0.90      Sam Lee — IT Mgr, NM Tech (low Fit)

Sort by: [Fit ▼] [Evidence] [Contact]
```

### Per-lead explanation string

Every lead carries a short `explanation` field rendered inline:

> "Ranked because title matched IT decision-maker, organization matched K-12 district, source came from district website, email was deduced not verified."

This is the differentiator versus opaque "intent score" vendors. **Always render it.** Never hide it behind a click.

### Why no single composite "Priority Rank"

Tested in early planning, rejected. The moment you compose three scores into one number, operators sort by that number and ignore the components — you've reintroduced the black-box rank with extra steps. Show the three scores; let the operator weight them.

## Run model

Two run modes:

### Scout run

- **Cost:** cheap.
- **Lead cap:** 10–20.
- **Use:** exploratory pass. Operator iterates on the query/recipe before committing budget.
- **Returns:** leads with three scores + a quality/cost preview ("you searched 6 sources, 2 returned signal, 4 were noise; estimated cost for Full run: $X").
- **Persistence:** none (Sprint 1) / optional (Sprint 2+).
- **Sprint 1 scope:** ship this end-to-end.

### Full run

- **Cost:** real.
- **Lead cap:** up to 100.
- **Use:** confirmed harvest after recipe stabilizes.
- **Returns:** leads with three scores + per-lead explanation + run metrics (cost breakdown, time elapsed).
- **Persistence:** required. Stores recipe + run + all leads + (eventually) feedback.
- **Sprint 2 scope:** ship this with feedback loop.

### Caps that matter

Cap on:

- Source searches per run.
- Pages extracted per run.
- LLM calls per run.
- Elapsed wall-clock time per run.
- **Estimated spend per run** (the dollar number).

Lead count is a **sanity bound**, not a user-facing cap. Don't show "max 100 leads" as a UI constraint. Show "estimated cost: $X.XX, estimated time: Y minutes" instead.

### Internal batch budget

- Maximum 10 Full runs per recipe-batch = 1000 leads per batch.
- This is an **internal sanity bound**, not a product feature. Not exposed in the UI.

## Feedback loop

### In-app per-lead feedback

Five labels, mutually exclusive per lead:

- `usable` — Operator would actually contact this lead.
- `wrong persona` — Title or seniority doesn't match the target.
- `bad source` — Source URL is broken / outdated / wrong organization.
- `bad contact` — Email/phone is wrong, deduced incorrectly, or unverifiable.
- `duplicate` — Already in the operator's CRM or pipeline.

Required to close out a Full run. Sprint 2 ships this.

### Weekly recipe review

Friday 30-min ritual: Matt + Lee + Thomas walk through the week's recipes. Which produced usable leads, which failed, which got re-run. The in-app buttons feed this; they don't replace it. The conversation is the real product feedback loop.

## Headline KPI

> **Minutes of operator review per usable lead** (Thomas's runs).

Why this and not API cost: in a boutique fulfillment model, operator time dominates economics by an order of magnitude. If Thomas reviews 100 leads for 2 hours and gets 12 usable (10 min/usable), that's barely better than him searching LinkedIn manually — even if API cost was $0. If he reviews 20 leads in 30 minutes and gets 8 usable (3.75 min/usable), that's a winning recipe — even if API cost was $5.

### Secondary KPIs

- API cost per usable lead — informs future self-serve pricing.
- Recipe-reuse rate — informs whether boutique has operating leverage.
- Customer-confirmed "usable" rate per delivered briefing — Matt's fulfillment quality.

## Anti-patterns to avoid

- ❌ A single "confidence score" or "priority score" that hides the three components.
- ❌ Storing API keys in the frontend.
