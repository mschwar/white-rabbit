# Decision Log (ADRs)

Locked architectural and product decisions. Append new entries; **never edit historical ones**. If you believe a locked decision is wrong, surface it to Matt and (if accepted) write a *new* ADR that supersedes it. The old entry stays for the record.

Format: ADR-NNN — Title. Date. Status: Locked / Superseded by ADR-XXX. Context. Decision. Consequences.

---

## ADR-001 — Greenfield repo with modular code reuse

**Date:** 2026-05-05
**Status:** Locked

**Context.** The Scotty demo at `/Users/mschwar/Documents/proxy-lead` is Streamlit-based, fixture-coupled, and entangles demo concerns with real-search logic. Extending it to be a self-serve product would import that entanglement. Building from scratch lets us design recipe storage, the three-score model, and operator-time tracking from the start.

**Decision.** New repo at `/Users/mschwar/Documents/white-rabbit`. Lift load-bearing Python primitives from the demo (Tavily client, OpenAI extraction, Pydantic models, cost calculation) into `packages/core`. Throw away the Streamlit UI, fixtures, and orchestration. Build the new app on top of `packages/core`.

**Consequences.** Two repos to maintain (demo + product). Some upfront cost rebuilding orchestration. In exchange: clean schema, no demo-mode debt, free choice of frontend framework and auth model.

---

## ADR-002 — Stack: Next.js + Python (FastAPI) + Postgres

**Date:** 2026-05-05
**Status:** Locked

**Context.** Streamlit can't support real auth, multi-user state, or a real product UI. The Python ecosystem is where the search/extraction libraries already live (tavily-python, openai). Mixing them needs an HTTP boundary.

**Decision.**

- **Web layer:** Next.js (App Router, TypeScript, Tailwind, ESLint). Renders UI, handles auth, calls the Python API.
- **API layer:** Python (FastAPI). Owns all third-party calls (Tavily, OpenAI, future search vendors). Returns JSON.
- **Storage:** Postgres. Specific host TBD (Supabase, Neon, or local Docker — see open question in `STATUS.md`).
- **Communication:** Web ↔ API over HTTP. Web never holds API keys to upstream vendors.

**Consequences.** Two runtimes to operate. Two `node_modules` and one `.venv`. In exchange: frontend stays clean, Python keeps its native search libraries, API keys are server-side, future swap of either side is feasible.

---

## ADR-003 — Auth: shared password (Sprint 1 only)

**Date:** 2026-05-05
**Status:** Locked

**Context.** Three operators (Matt, Thomas, Lee) need access. Building real auth (per-user accounts, sessions, password reset, MFA) is weeks of work that doesn't validate any product hypothesis. The kill/keep gate at 90 days will tell us whether to invest.

**Decision.** Single shared password gates the entire app. Read from env var `WR_SHARED_PASSWORD` (or its bcrypt hash, `WR_SHARED_PASSWORD_HASH`). Next.js middleware checks a session cookie set by `POST /login`. Use `crypto.timingSafeEqual` for the comparison.

**Consequences.** No per-user attribution at the data layer in Sprint 1 — recipes are owned by "the team" not individuals. If we need per-operator KPIs (e.g., minutes-per-usable-lead by operator), we'll either (a) infer from session metadata if available, or (b) ship a "who are you" picker after login that's not an auth boundary, just an analytics tag. Real auth waits for the kill/keep gate.

---

## ADR-004 — Scotty demo frozen indefinitely

**Date:** 2026-05-05
**Status:** Locked

**Context.** The demo at `/Users/mschwar/Documents/proxy-lead` works, has shipped collateral (FAQ PDF, POC offer template, presenter scripts), and serves the customer-facing job. Rewriting it as part of v2 risks breaking what's working without a forcing function.

**Decision.** No code changes to the demo repo. It stays at its current state. Sunset only when the v2 product can demonstrably do the demo job *better* than the existing app — and that's a future decision, not a current one.

**Consequences.** v2 cannot share code with the demo via imports — only via copy. The two repos drift over time. Acceptable cost; the alternative (forcing them to share) would couple them again and undo ADR-001.

---

## ADR-005 — Shared internal API token for web-to-API boundary

**Date:** 2026-05-09
**Status:** Locked

**Context.** The rebuild audit found the backend endpoints could be called directly even though the UI was password-gated. The product does not need per-user auth yet, but it does need the web app and API to agree on one internal boundary so the protected routes cannot bypass the shell.

**Decision.** Protect the backend boundary with a shared internal token in `WR_API_INTERNAL_TOKEN`. The Next.js proxy adds the token as `x-white-rabbit-internal-token` on protected API calls, and FastAPI rejects protected endpoints without that token. `GET /health` remains public.

**Consequences.** Local and deployed environments must provision the token alongside the shared password. Direct calls to the protected backend now fail without the token, and tests must cover both allowed proxy traffic and denied direct traffic. This keeps the boundary simple until the product has a stronger reason for per-user auth or ingress-only enforcement.

---

## ADR-006 — Documentation authority and archival policy

**Date:** 2026-05-09
**Status:** Locked

**Context.** The repo accumulated bootstrap plans, sprint roadmaps, BUILDOUT remediation docs, QA reports, zero-trust audits, meeting notes, and rebuild control docs in a short period. Several older documents still looked like current instructions even after the validated-leads rebuild moved active work to `rebuild/validated-leads-loop`. Agents need a deterministic way to decide which document wins when docs conflict.

**Decision.** Documentation authority is layered:

1. This ADR log remains locked decision history. New decisions append; old entries are not rewritten.
2. `docs/00-product-northstar.md` is the current product source of truth for product quality, usable-lead definitions, launch gates, and anti-drift rules.
3. `STATUS.md` is the current repo state and next-handoff source of truth.
4. `docs/08-agentic-buildout-plan.md` is the active rebuild feature queue and branch workflow.
5. `docs/09-rebuild-phase-gates.md` is the active rebuild wave-gate process.
6. `docs/qa-rubric.md` remains the QA tier reference unless a rebuild gate requires stricter checks.

Every planning, audit, QA, meeting, or report document that is not active must carry one of these labels near the top:

- `Active` — current control document.
- `Superseded` — old plan or roadmap; keep for history, but do not execute from it.
- `Historical Record` — evidence/report/transcript; preserve content, but do not treat as current instructions.
- `Archived Reference` — bootstrap/reference context; link to current active docs.

**Consequences.** Future agents should not infer current work from old sprints, historical QA reports, or completed BUILDOUT plans. Historical reports stay intact as evidence, but they must link to the active control docs. Documentation-only remediation may edit historical docs to add status banners and current-doc pointers, but it must not rewrite quoted evidence, transcripts, or old findings as if they were newly created.

---

## ADR-007 — Wave gate advancement requires orchestrator acceptance

**Date:** 2026-05-10
**Status:** Locked

**Context.** The phase-gate document required gate reports before downstream waves unlocked, but it also told agents to update next-wave statuses and push accepted-looking gate decisions themselves. That left no explicit pause for the designated orchestrator before agents moved from one wave to the next.

**Decision.** Feature agents may prepare gate evidence and recommend `advance`, `hold`, `revise`, or `rollback`, but downstream waves unlock only after an orchestrator acceptance record exists in the gate report and `STATUS.md`. If acceptance is unavailable in the same session, the next wave remains blocked and the report is marked pending orchestrator review.

**Consequences.** The rebuild remains slower but auditable. Agents cannot self-advance through milestone gates just because tests pass. The current orchestrator may retroactively accept prior gate movement after reviewing evidence, but future downstream unlocks require the acceptance record before implementation starts.

---

## ADR-008 — Correction feedback stores identifiers as text for synthetic and real rows

**Date:** 2026-05-10
**Status:** Locked

**Context.** The correction feedback loop must work on the live validation-buckets browser fixture as well as on real persisted runs. The fixture uses synthetic string identifiers, while the stored review queue also needs to accept real UUID-shaped IDs from saved leads and runs. A UUID-only foreign key schema blocked browser QA and made the review queue too narrow for the benchmark loop.

**Decision.** Store correction `lead_id` and `run_id` values as text in `lead_correction` so the API can accept synthetic fixture IDs and real UUID strings without foreign key failures. Use the correction queue as a review artifact keyed by identifiers rather than as a hard relational join boundary. If a later need appears for analytics joins to persisted leads or runs, add optional linkage columns in a future migration instead of reintroducing UUID-only constraints on the primary queue record.

**Consequences.** Browser QA can save corrections against fixture rows, the queue export can include synthetic IDs, and the queue remains usable for benchmark review. The tradeoff is that correction rows no longer enforce referential integrity against `lead` and `recipe_run` at the database layer. That is acceptable for this internal feedback loop because the queue's job is to preserve operator corrections first and resolve relationships later if needed.

---

## ADR-009 — Reset gates require full evaluation and audit before advancement

**Date:** 2026-05-10
**Status:** Locked

**Context.** The May 10 zero-trust audit found that the rebuild accumulated implementation surface after W4 without a W5 or W6 gate report proving the visible operator loop. Matt explicitly asked for a full gated plan where every gate has a full evaluation and audit before downstream implementation proceeds.

**Decision.** Reset implementation is controlled by `docs/12-reset-gated-implementation-plan-2026-05-10.md`. Every reset gate requires a repo-backed evaluation/audit report before the next gate unlocks. Feature QA can prove a slice works, but only a gate audit can advance the reset. Gate reports must cite operator evidence, live or replayed benchmark results, browser evidence when UI is touched, CSV/DB readback when export or persistence is touched, and a clear decision: `advance`, `hold`, `revise`, `rollback`, or `kill`.

**Consequences.** The reset will move slower than feature-only implementation, but downstream agents will not treat UI completion, test pass, or mocked fixtures as product readiness. Superseded by ADR-010 for operator-use promotion: `main` may be synced from `rebuild/validated-leads-loop` when Matt explicitly asks Thomas/Lee to use the latest internal version, but feature work still integrates through `rebuild/validated-leads-loop`. W6 and dogfood decisions stay blocked until the reset gate evidence satisfies `docs/00-product-northstar.md`.

---

## ADR-010 — Promote rebuild branch to main for internal operator use

**Date:** 2026-05-10
**Status:** Locked

**Context.** The active rebuild docs previously kept `main` untouched and blocked Thomas/Lee dogfood until the reset gates proved the visible operator loop. Matt explicitly directed the team to merge `rebuild/validated-leads-loop` to `main` because Thomas and Lee want to use the current internal tool.

**Decision.** Promote `rebuild/validated-leads-loop` to `main` and allow Thomas and Lee to use the internal deployment under Matt's direction. This is a manual operator-use promotion, not a claim that the quality gate is green or that the reset audit evidence passed. The product remains internal-only, password-gated, and not a public self-serve SaaS.

**Consequences.** `main` becomes the operator-use deployment line for the current rebuild state. Future agents must not infer that all red/yellow/green quality criteria were satisfied simply because the rebuild is on `main`. Generated leads still require evidence review, and follow-up work should preserve visible provenance, validation status, and export context.

---

## ADR-011 — Broad Scout/Full runs need 10-25 categorized results

**Date:** 2026-05-10
**Status:** Locked

**Context.** Matt reported a 2026-05-10 call with Lee and Thomas where they said the current tool is not useful when Scout returns 3 results and Full returns 4 results. Their target for broad Scout-style prospecting is more than 10 results, with 10-25 results as the preferred working range.

**Decision.** Broad Scout/Full-style prompts must produce enough categorized output to create sales value: more than 10 categorized results, targeting 10-25 results where the market supports it. Precision and evidence remain mandatory, but "only a few clean rows" is not an acceptable pass condition for broad prospecting. Narrow named-account prompts may return fewer person leads only when every requested account is explicitly represented as `person_lead`, `organization_only`, `not_found`, or `failed`.

**Consequences.** Reset gates cannot advance on quality alone if the product starves the operator with 3-4 rows for a broad market. Benchmarks, planner logic, UI review, export checks, and dogfood decisions must track row volume alongside precision and evidence. Agents should treat low-volume broad runs as `hold` unless the report proves the target universe itself is smaller.

---

## How to add a new ADR

1. Pick the next ADR number (ADR-012, ADR-013, ...).
2. Add an entry at the bottom of this file with the same format.
3. Set Status to "Locked" once Matt confirms.
4. If the new ADR overrides an old one, mark the old one's Status as "Superseded by ADR-NNN" but **do not delete or rewrite its body**.

ADRs are about "we considered alternatives and chose this." If the choice is trivial or reversible (e.g., a logging library), it doesn't need an ADR — just code it and note in commit message.
