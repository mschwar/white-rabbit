# AGENTS.md — White Rabbit v2

**You are an AI agent. Read this entire file before doing anything else. It is short on purpose.**

## What this repo is

White Rabbit v2 is a greenfield, internal-first, self-serve B2B prospecting tool for three operators:

- **Matt** — product builder, fulfillment operator for paid customer briefings.
- **Thomas** — full-time B2B sales rep employed elsewhere; uses White Rabbit in his own daily prospecting. **Primary product signal.**
- **Lee** — full-time DTC sales rep employed elsewhere; uses White Rabbit to test generalization beyond B2B. Secondary signal. Also presents the Scotty demo.

The customer offer is scoped concierge briefings fulfilled by Matt. **There is no external self-serve product yet.** Self-serve here means the three operators can use the tool without asking each other for help.

## What this repo is NOT

- Not the Scotty demo. The demo lives at `/Users/mschwar/Documents/proxy-lead` and is **frozen indefinitely**. Do not edit it.
- Not a multi-tenant SaaS. No accounts, no orgs, no billing. One shared password gates the app.
- Not a ZoomInfo competitor by data scale. Differentiation is recipes + visible provenance + ranked output, not list size.

## Read order before working

1. `STATUS.md` — what's done, what's next, what's in flight. **Always read this second.**
2. `docs/03-decisions.md` — locked decisions. Do not re-litigate. New entries append; old entries do not change.
3. `docs/04-roadmap.md` — current build slice, kill/keep gate, sprint scope.
4. `docs/00-context.md` — strategic background.
5. `docs/01-model.md` — operator model, recipes, score model, run model.
6. `docs/02-stack.md` — Next.js + Python + Postgres layout, conventions, env vars.
7. `docs/05-reuse.md` — explicit lift list from `/Users/mschwar/Documents/proxy-lead`.

## Project rules (do not break these)

1. **STATUS.md is the source of truth for "where we are."** Read it at session start. Update it at session end.
2. **Locked decisions in `docs/03-decisions.md` are locked.** If you disagree, surface it to Matt — do not silently change them.
3. **Demo is frozen.** Never edit anything in `/Users/mschwar/Documents/proxy-lead`.
4. **Reuse before rewriting.** Before writing new search/extract/score code, check `docs/05-reuse.md`.
5. **No scope creep.** The current build slice in `docs/04-roadmap.md` is the work. New ideas → propose, don't ship.
6. **No external self-serve features.** No signup, no per-user accounts, no billing, no public landing pages until the kill/keep gate passes.
7. **Frontend never holds API keys.** All Tavily / OpenAI / search-vendor calls happen in the Python service.
8. **Recipes are first-class.** Every Full run produces a stored recipe (query + filters + source mix + ranking weights + outcomes).
9. **Three visible scores.** Fit / Evidence / Contact. Composite is a gate, not a rank.
10. **Track operator minutes per run.** This is the headline KPI — `minutes / usable lead`. API cost is secondary.

## Anti-drift

- If `docs/03-decisions.md` and your instinct disagree, the doc wins. Surface the disagreement; don't act on it.
- If STATUS.md is stale or contradicts code, fix STATUS.md to match reality and note it in your update.
- If a scope question is ambiguous, default to the smaller scope. The roadmap is small on purpose.
- If you're tempted to "just also add X," resist. Add X to `docs/04-roadmap.md` as a future slice.

## Session protocol

1. Read AGENTS.md, STATUS.md, the most recent decision in `docs/03-decisions.md`, and the current sprint section of `docs/04-roadmap.md`.
2. Pick up the next task in STATUS.md (or one explicitly assigned by Matt).
3. Do the work. Reuse before writing new code.
4. Before ending the session, update STATUS.md: what you did, what's next, any open questions.
5. If you made any architectural / scope / dependency decision that wasn't already in `docs/03-decisions.md`, append a new ADR entry there.
6. Commit your changes with a clear message. Conventional commits style preferred (`feat:`, `fix:`, `docs:`, `chore:`).

## Useful paths

- This repo: `/Users/mschwar/Documents/white-rabbit`
- Frozen demo (read-only reference): `/Users/mschwar/Documents/proxy-lead`
- Strategic plan archived from bootstrap: `/Users/mschwar/.claude/plans/the-demo-is-good-encapsulated-wigderson.md`

## When you finish

Mark your work done. Update STATUS.md. Commit. That's it.
