# AGENTS.md — White Rabbit v2

**You are an AI agent. Read this entire file before doing anything else. It is short on purpose.**

## What this repo is

White Rabbit v2 is a greenfield, internal-first, self-serve B2B prospecting tool for three operators:

- **Matt** — product builder, fulfillment operator for paid customer briefings.
- **Thomas** — full-time B2B sales rep employed elsewhere; uses White Rabbit in his own daily prospecting. **Primary product signal.**
- **Lee** — full-time DTC sales rep employed elsewhere; uses White Rabbit to test generalization beyond B2B. Secondary signal. Also presents the Scotty demo.

The customer offer is scoped concierge briefings fulfilled by Matt. **There is no external self-serve product yet.** Self-serve here means the three operators can use the tool without asking each other for help.

## What this repo is NOT

- Not the Scotty demo. The demo lives outside this repo and is **frozen indefinitely**. Do not edit it.
- Not a multi-tenant SaaS. No accounts, no orgs, no billing. One shared password gates the app.
- Not a ZoomInfo competitor by data scale. Differentiation is recipes + visible provenance + ranked output, not list size.

## Read order before working

1. `STATUS.md` — what's done, what's next, what's in flight. **Always read this second.**
2. `docs/03-decisions.md` — locked decisions. Do not re-litigate. New entries append; old entries do not change.
3. `docs/00-product-northstar.md` — current product truth, launch gate, usable-lead definition, anti-drift rules.
4. `docs/08-agentic-buildout-plan.md` — active rebuild feature queue, branch workflow, next feature pointer.
5. `docs/09-rebuild-phase-gates.md` — active rebuild wave gates and required gate reports.
6. `docs/qa-rubric.md` — QA ship-gate tiers. Any change touching extraction/scoring must pass Tiers 1–4 unless a rebuild gate is stricter.
7. `docs/02-stack.md` — current Next.js + Python + Postgres layout, conventions, env vars.
8. `docs/00-context.md`, `docs/01-model.md`, `docs/05-reuse.md` — strategic and bootstrap reference. Check their status banners before treating them as active instructions.
9. `docs/04-roadmap.md`, `docs/06-audit-action-plan.md`, `docs/07-buildout-plan.md` — historical/superseded plans. Do not execute from these unless the current active docs explicitly say to.

## Project rules (do not break these)

1. **STATUS.md is the source of truth for "where we are."** Read it at session start. Update it at session end.
2. **Locked decisions in `docs/03-decisions.md` are locked.** If you disagree, surface it to Matt — do not silently change them.
3. **Demo is frozen.** Never edit anything in the external `proxy-lead` repo.
4. **Reuse before rewriting.** Before writing new search/extract/score code, check `docs/05-reuse.md`.
5. **No scope creep.** The active rebuild feature or gate in `docs/08-agentic-buildout-plan.md` / `docs/09-rebuild-phase-gates.md` is the work. New ideas → propose, don't ship.
6. **No external self-serve features.** No signup, no per-user accounts, no billing, no public landing pages until the kill/keep gate passes.
7. **Frontend never holds API keys.** All Tavily / OpenAI / search-vendor calls happen in the Python service.
8. **Recipes are internal while red.** Recipes remain strategically important, but recipe library / batch / Friday review surfaces stay out of the primary operator path until the launch gate allows them.
9. **Three scores remain visible only when evidence-backed.** Fit / Evidence / Contact are useful only when driven by field-level validation, not LLM optimism.
10. **Track operator minutes per usable lead.** This is the headline KPI. API cost is secondary, but do not add operator-minute ceremony before the validated query-to-export loop works.

## Rebuild branch protocol

For the validated-leads rebuild, feature/audit work still starts from `rebuild/validated-leads-loop`.

- Never merge feature branches directly to `main`. Never open a PR targeting `main`.
- ADR-010 promoted `rebuild/validated-leads-loop` to `main` for Thomas/Lee internal operator use. Treat `main` as the operator-use deployment line, not as proof that quality gates passed.
- Only fast-forward/sync `main` from `rebuild/validated-leads-loop` when Matt or the active gate plan explicitly calls for an operator-use promotion.
- Before rebuild work, read `docs/00-product-northstar.md` and `docs/08-agentic-buildout-plan.md`.
- Pick the next `ready` feature from `docs/08-agentic-buildout-plan.md`.
- All feature branches branch from `rebuild/validated-leads-loop` and all PRs target `rebuild/validated-leads-loop`.
- Update `docs/08-agentic-buildout-plan.md` and `STATUS.md` before ending.
- If a feature touches UI, browser QA and screenshots are required.
- If a feature does not touch UI, explicit non-UI verification is required.

## Anti-drift

- If `docs/03-decisions.md` and your instinct disagree, the doc wins. Surface the disagreement; don't act on it.
- If STATUS.md is stale or contradicts code, fix STATUS.md to match reality and note it in your update.
- If a scope question is ambiguous, default to the smaller scope. The rebuild queue is small on purpose.
- If you're tempted to "just also add X," resist. Add X as an explicit future candidate in `docs/08-agentic-buildout-plan.md` or as an open question in `STATUS.md`; do not revive the legacy roadmap.

## Session protocol

1. Read AGENTS.md, STATUS.md, and the most recent decision in `docs/03-decisions.md`.
2. Read `docs/00-product-northstar.md`, `docs/08-agentic-buildout-plan.md`, and `docs/09-rebuild-phase-gates.md` before selecting rebuild work.
3. Pick up the next task in STATUS.md (or one explicitly assigned by Matt). For rebuild work, the next task must match the next `ready` feature or gate in `docs/08-agentic-buildout-plan.md` / `docs/09-rebuild-phase-gates.md`.
4. Do the work. Reuse before writing new code.
5. Before ending the session, update STATUS.md: what you did, what's next, any open questions.
6. If the session touched `docs/07-buildout-plan.md` work, update that checklist in the same session so the next agent can pick up from the true state. For current rebuild work, prefer `docs/08-agentic-buildout-plan.md` and gate reports instead.
7. If you made any architectural / scope / dependency / documentation-authority decision that wasn't already in `docs/03-decisions.md`, append a new ADR entry there.
8. Commit your changes with a clear message. Conventional commits style preferred (`feat:`, `fix:`, `docs:`, `chore:`).

## Useful paths

- This repo in the current Codex workspace: `C:\Users\Matty\Documents\white-rabbit`
- Frozen demo (read-only reference): `C:\Users\Matty\Documents\proxy-lead` in this workspace; older docs may mention `/Users/mschwar/Documents/proxy-lead`
- Strategic plan archived from bootstrap: `/Users/mschwar/.claude/plans/the-demo-is-good-encapsulated-wigderson.md`

## When you finish

Mark your work done. Update STATUS.md. Commit. That's it.
