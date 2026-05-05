# 00 — Context

## Why this repo exists

OrgAtlas (the company) ships **White Rabbit** (the tool). The original White Rabbit, at `/Users/mschwar/Documents/proxy-lead`, was built as a Streamlit app to win the Scotty demo — a customer pitch where Lee presents and Thomas closes. The demo is good enough; that mission is done.

The strategic decision in 2026-05 was: do **not** push that app as a self-serve product. Building self-serve B2B intelligence puts us in a knife fight with ZoomInfo, Apollo, Clay, Clearbit, and 20 others with bigger data, bigger sales orgs, and bigger budgets. We will not out-buy them on data and we will not out-engineer them on UI.

The route where a small team wins is: **the operators using the tool become the marketing**. Working salespeople use it daily, the tool gets better through their feedback, and they make content about using it. That requires a different product than the demo — one designed for daily use by operators, not a 30-minute pitch.

This repo is that product.

## Three roles

- **Matt** — builds the product, fulfills paid customer briefings.
- **Thomas** — full-time B2B sales rep at his own company. Uses White Rabbit in his daily prospecting. **Primary product signal** because his use case matches OrgAtlas's likely paid customer ICP.
- **Lee** — full-time DTC sales rep at his own company. Uses White Rabbit to test generalization beyond B2B. Also presents the Scotty demo.

Lee and Thomas are not OrgAtlas employees. They're embedded design partners. The commercial arrangement (free seats, revenue share, equity, content rights) is an open question that has to be settled before they go public with usage. Build can proceed without it; public content cannot.

## Two artifacts

- **The demo** at `/proxy-lead`. Frozen. It does the customer pitch job.
- **The product** here at `/white-rabbit`. Internal first. Three operators. Self-serve from day 1.

They share Python primitives via copy (not imports — they will drift). See `docs/05-reuse.md`.

## What "self-serve internal" means

- Any of the three operators can run the tool without asking the others.
- One shared password gates the app. No per-user accounts in Sprint 1.
- No customer-facing surfaces. No public landing page. No signup flow.
- Every workaround the team would otherwise tolerate ("oh I'll just SSH in and rerun it") is a UX bug we have to fix.

This is a forcing function. We don't accumulate operator-handholding debt that has to be paid down later when external customers arrive.

## What's at stake commercially

- **Scotty POC** — first paid customer engagement, $10K, two custom briefings, 14-day delivery. Fulfilled by Matt using whatever combination of tools serves him best (today: the demo + manual work). The product here will eventually replace that workflow.
- **ZoomInfo replacement narrative** — Scotty pays ZoomInfo $45K/yr. The boutique briefing positioning explicitly punches at that.
- **Future paid customers** — who and how is undecided. That's downstream of getting Thomas using the product reliably and producing public content about it.

## Why "recipes" matter

A query is one-shot. A recipe is reusable IP. The differentiation versus commodity vendors is:

1. **Visible provenance** — every lead shows where it came from and why it ranked where it did.
2. **Three explicit scores** — Fit, Evidence, Contact — composable by the operator instead of hidden in a black-box "intent score."
3. **Reusable recipes** — the artifact that survives a single batch is the *recipe* (query + filters + source mix + ranking weights + outcomes). Recipes can be sold, shared, or reused for the next customer in the same vertical.

If recipes don't reuse across customers, the boutique model has no operating leverage and the kill/keep gate fails. That's the most important hypothesis the product will test.

## Reading order from here

- `docs/01-model.md` — the operator model, recipe structure, score model, run model in detail.
- `docs/02-stack.md` — how the code is laid out.
- `docs/03-decisions.md` — what's been decided and why.
- `docs/04-roadmap.md` — what we build next.
- `docs/05-reuse.md` — what to lift from the demo.
