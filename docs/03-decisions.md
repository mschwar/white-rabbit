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
**Status:** Superseded by ADR-012

**Context.** Matt reported a 2026-05-10 call with Lee and Thomas where they said the current tool is not useful when Scout returns 3 results and Full returns 4 results. Their target for broad Scout-style prospecting is more than 10 results, with 10-25 results as the preferred working range.

**Decision.** Broad Scout/Full-style prompts must produce enough categorized output to create sales value: more than 10 categorized results, targeting 10-25 results where the market supports it. Precision and evidence remain mandatory, but "only a few clean rows" is not an acceptable pass condition for broad prospecting. Narrow named-account prompts may return fewer person leads only when every requested account is explicitly represented as `person_lead`, `organization_only`, `not_found`, or `failed`.

**Consequences.** Reset gates cannot advance on quality alone if the product starves the operator with 3-4 rows for a broad market. Benchmarks, planner logic, UI review, export checks, and dogfood decisions must track row volume alongside precision and evidence. Agents should treat low-volume broad runs as `hold` unless the report proves the target universe itself is smaller.

---

## ADR-012 — High-volume transparent tiering is the broad-query target

**Date:** 2026-05-10
**Status:** Superseded by ADR-013

**Context.** ADR-011 corrected the immediate failure mode where broad Scout/Full runs returned only 3-4 rows. Matt clarified afterward that 10-25 categorized results was the minimum escape velocity from that failure, not the ideal end state. The stronger product direction is to surface the full realistic picture the public web allows, then make it instantly clear why most rows are not actionable.

**Decision.** For broad vertical + geography prompts, White Rabbit should move toward high-volume transparent tiering: 50-300+ categorized candidates where the market supports it, with a strict `high_trust_usable` tier preserving at least the benchmark precision bar and all other rows clearly separated as `review`, `organization_only`, `not_found`, or `failed`. Volume is useful only when every row carries grounded evidence or an explicit reason for non-actionability. The product must never create false confidence, invent fields, or let noisy candidates masquerade as CRM-ready leads.

**Consequences.** Search planning, Tavily aggregation, LLM extraction, validation, metrics, UI, export, and gate audits must measure both total surfaced coverage and high-trust precision. The LLM extraction stage should become inclusive, while server-side orchestration performs rigorous tiering and annotation. The old binary pass/fail gate remains the definition of `high_trust_usable`, but it no longer decides whether a candidate is returned at all. Broad-query gates should treat 10-25 as a floor, not a success target; narrow named-account prompts may remain tighter when the target universe is genuinely small.

---

## ADR-013 — Live-demo surface and pipeline contract use public operator language

**Date:** 2026-05-10
**Status:** Locked

**Context.** Matt approved the mockup direction but clarified that the live demo must drop internal language and internal operator names. The latest pipeline sheet also reframes the high-volume target as 50-500+ surfaced candidates, with the differentiator being transparent categorization, per-field evidence, and orchestrated multi-agent verification rather than a small perfect list.

**Decision.** Demo-facing UI and mockups must use external, operator-neutral language. They must not reference internal people, implementation gates, agent prompts, sprint labels, or "production target mockup" copy. Broad-query product language should target 50-500+ categorized candidates where the public web supports it, with four visible operator buckets: `READY`, `REVIEW`, `ORG-ONLY`, and `NOT FOUND`. Internal data models may keep `high_trust_usable`, `organization_only`, and other exact machine labels, but demo UI should translate them into plain operator states.

**Consequences.** Mockups, screenshots, output contracts, export labels, and gate docs must distinguish public/demo copy from internal implementation labels. The pipeline contract is now `DISCOVER -> EXTRACT -> VERIFY -> SYNTHESIZE -> ORCHESTRATE & DELIVER`, with auditable artifacts at every handoff. Review workflow stays lightweight for the demo: `REVIEW` means human judgment required with context, not a full assignment or CRM workflow unless Matt explicitly adds that later.

---

## ADR-014 — Reset plan is the active execution authority

**Date:** 2026-05-10
**Status:** Locked

**Context.** ADR-006 correctly established a documentation authority model before the May 10 reset existed. After R01 QA, the repo still had several top-level surfaces routing agents to the historical `docs/08-agentic-buildout-plan.md` and `docs/09-rebuild-phase-gates.md` flow. That caused Prompt A to stop even though the reset loop should have continued to R02 inside RG1.

**Decision.** While the May 10 reset is active, `docs/12-reset-gated-implementation-plan-2026-05-10.md` is the active execution authority for feature selection, Prompt A/B/C copy, reset gate state, and next-feature readiness. `docs/08-agentic-buildout-plan.md` and `docs/09-rebuild-phase-gates.md` remain historical context for F00-F23 and W0-W6, but agents must not execute from them unless `docs/12` explicitly sends them back.

**Consequences.** AGENTS.md, STATUS.md, archived reference banners, historical QA reports, and future gate reports must point to `docs/12` for active reset execution. Prompt B may unlock the next feature inside the same in-progress reset gate after QA passes; only Prompt C can advance a reset gate or unlock the first feature in the next gate.

---

## ADR-015 — Design direction is captured but cannot unlock UI implementation

**Date:** 2026-05-11
**Status:** Locked

**Context.** A parallel design audit produced a new direction on `codex/design-vision-2026-05-11`: deep navy instrument chassis plus paper-white evidence table, with the rule "The brand leads once. Then the product speaks." The reset is still in RG3, and RG4 UI work remains blocked until the data-quality gate advances.

**Decision.** Add `DESIGN.md` as the future visual direction authority for RG4, but treat it as planning input only. The May 10 mockup remains the product-structure reference, not the final visual direction. If RG3 advances, the next assignment is a refreshed mockup/design preflight from `DESIGN.md`, not production R10 implementation. R10-R12 stay blocked until Matt approves the refreshed mockups. The rabbit/icon problem remains quarantined until an approved vector exists.

**Consequences.** Design direction can be reviewed and used to brief future mockup agents without contaminating RG3 evidence or unlocking UI work early. Prompt C for RG3 must cite `DESIGN.md` only as future RG4 input. Prompt A/B agents must not implement a new visual system, production logo, or RG4 UI until the reset plan explicitly marks that work ready after mockup approval.

---

## ADR-016 — Accepted RG3 hold requires a narrow live-value remediation slice

**Date:** 2026-05-11
**Status:** Locked

**Context.** RG3 Prompt C held after live benchmark evidence showed the product had safer validation semantics but still failed the operator-value bar: broad runs returned only 7-10 categorized rows, the suite produced 0 high-trust usable leads, and contact-quality passes were 0. Matt accepted the hold instead of advancing RG4 or treating the hold as an unresolved queue blocker.

**Decision.** Keep RG3 active and insert one remediation feature before any design or UI work: `R09A - Live value recovery and benchmark funnel diagnosis`. R09A must diagnose and repair the source-to-candidate-to-tier funnel, fix benchmark floor semantics, preserve strict READY/high-trust precision, keep unsupported contacts non-CRM-ready, and normalize failed/not-found reasons. RG4, refreshed mockups, R10-R12, export work, dogfood, and `main` sync remain blocked until a future RG3 Prompt C records `advance`.

**Consequences.** Prompt A now has exactly one valid next feature, and the A/B loop can resume without reopening downstream scope. The remediation is allowed to touch search/extraction/tiering/quality-report code only where it directly improves live value or proves the exact choke point. Agents must not satisfy R09A by lowering validation strictness, inventing contacts, or making UI/export work compensate for weak data.

---

## ADR-017 — Post-R09A hold targets contact evidence before UI

**Date:** 2026-05-11
**Status:** Locked

**Context.** The post-R09A RG3 re-audit held again. R09A recovered broad categorized volume for most broad prompts and added useful funnel observability, but the complete live benchmark suite still produced `0` high-trust usable rows and `0` contact-quality passes. A parallel RG4 mockup/design preflight also exists, but RG3 did not advance.

**Decision.** Keep RG3 active and insert exactly one next remediation feature: `R09B - Contact and evidence acquisition pass`. R09B must target the contact/evidence choke point with source-backed public-web evidence acquisition, READY-blocker reporting, and live-runner partial-failure reliability. RG4, refreshed mockup merge, R10-R12, export polish, dogfood, paid contact-source integration, and `main` sync remain blocked until a future RG3 Prompt C records `advance`. The RG4 design preflight branch is an inspection artifact only until Matt approves it after data-quality advancement.

**Consequences.** The reset avoids designing or exporting around a dataset that still has no CRM-ready contact value. Prompt A has exactly one valid next feature, and that feature cannot pass by lowering high-trust precision, inventing emails, treating inaccessible sources as support, or hiding missing contacts behind UI copy. If R09B still cannot produce contact-quality passes, the next decision should be product-positioning or vendor/source strategy, not another UI pass.

---

## ADR-018 — RG3 remediation expands to R09B plus R09C before any new gate audit

**Date:** 2026-05-11
**Status:** Locked

**Context.** R09B completed the first contact/evidence remediation pass inside the accepted RG3 hold. Matt explicitly directed that RG3 must not run Prompt C after R09B and that a second remediation feature is required inside the same gate before any re-audit. The purpose of the added feature is to improve contact quality and tier usefulness on promising rows without weakening the strict `high_trust_usable` contract.

**Decision.** Keep RG3 in `in_progress / gate_hold` after R09B and insert `R09C - Deep multi-source evidence acquisition and tier calibration` as the single ready feature. Treat R09B plus R09C together as the accepted RG3 remediation slice. Do not unlock RG4, refreshed mockups, R10-R12, export work, dogfood work, or any `main` promotion until both R09B and R09C are complete and a future RG3 Prompt C records `advance`.

**Consequences.** Prompt C is explicitly blocked after R09B. Prompt A has exactly one valid next assignment: R09C. R09C may improve evidence acquisition depth, corroboration, and tier usefulness for promising rows, but it cannot pass by relaxing the `high_trust_usable` definition, inventing contacts, compensating with UI/export work, or treating unsupported evidence as support.

---

## ADR-019 — Source-assisted research compiler is the next value path

**Date:** 2026-05-11
**Status:** Locked

**Context.** The post-R09C RG3 Tavily re-run remained held: live benchmarks still produced `0` high-trust usable rows and `0` contact-quality passes despite high-volume source and evidence-acquisition work. Matt then pointed back to Lee's April "NM IT for school districts" email thread. That thread shows the real commercial proof point: a human plus basic chatbot/Codex workflow produced a source-backed New Mexico school-district IT workbook with verified public emails, manual-lookup rows, source URLs, verification notes, and outreach/export artifacts. Thomas asked for the output, and that proof point helped drive live sales/demo momentum. The successful pattern was not fully autonomous broad Scout search; it was targeted public-source research compiled into an honest workbook.

**Decision.** Keep RG3 active, but pivot the next remediation from autonomous broad-search patching to a source-assisted research compiler path. The April New Mexico school-district IT package becomes the manual-oracle benchmark. Add `R09D-R09H` before any RG3 advance decision:

- `R09D - April NM evidence fixture and manual-oracle replay`
- `R09E - K-12 source map and public roster collector`
- `R09F - Source-assisted lead compiler`
- `R09G - Research-workbook tiering and export semantics`
- `R09H - Manual-oracle proof replay gate packet`

The product may still use autonomous search, Tavily, browser automation, expensive models, and multi-agent verification, but the launch wedge is source-assisted public-web research that beats the human+chatbot baseline on speed, evidence, categorization, and export honesty. Missing contact information may remain valuable as a `manual_lookup` or `review` row when name, title, organization, source, and next action are clear. Missing, unsupported, inaccessible, guessed, or conflicting contacts must still never be marked CRM-ready.

**Consequences.** No downstream RG4 UI, export polish, dogfood, or `main` promotion is unlocked by the post-R09C hold. The next valid Prompt A is R09D after this control-plane patch lands. Prompt C must not re-run RG3 until R09D-R09H have merged. The gate should judge whether White Rabbit can reproduce or improve the April New Mexico source-backed workbook, not whether the current autonomous Scout path can magically produce CRM-ready contacts from broad generic web search. High-volume transparent tiering remains a future/product-scale target, but it no longer overrides the nearer proof point: source-assisted research workbooks with verified rows, manual-lookup rows, not-found rows, and auditable evidence.

---

## ADR-020 — Accepted post-R09H hold requires API startup proof before more value work

**Date:** 2026-05-11
**Status:** Locked

**Context.** The post-R09H RG3 Prompt C audit held. The source-assisted manual-oracle replay now proves the offline workbook pattern: 17 rows, 10 `READY_WITH_CONTACT`, 7 `MANUAL_LOOKUP`, sales-first export fields, and zero unsupported CRM-ready rows. But the live operator loop remains unproven because the local API stayed in startup, `/health` returned `000`, no fresh live benchmark suite completed, and the latest complete saved live suite still has `0` high-trust usable rows and `0` contact-quality passes. Matt accepted the hold.

**Decision.** Keep RG3 in `gate_hold` and insert one narrow remediation feature before any further data-quality, UI, export, dogfood, or `main` work: `R09I - API startup and live proof harness`. R09I must make API startup and live verification deterministic enough for future Prompt C audits to trust the evidence. It must split basic process health from readiness/vendor checks, expose actionable readiness diagnostics, make live benchmark startup wait on health/readiness with clear timeouts, and capture startup failure artifacts instead of ambiguous `000` results.

**Consequences.** Prompt A has exactly one valid next feature: R09I. RG4, refreshed mockups, R10-R12, export work, dogfood, and `main` promotion remain blocked. R09I cannot pass by changing lead-quality logic, relaxing READY/high-trust semantics, implementing UI/export, or hiding startup failures. Its job is to make the live loop observable and auditable so the next RG3 Prompt C can distinguish product-value failure from API/runtime failure.

---

## ADR-021 — Accepted post-R09I hold requires bounded live runtime before another RG3 audit

**Date:** 2026-05-11
**Status:** Locked

**Context.** The post-R09I RG3 Prompt C audit held. R09I proved one important runtime boundary: a clean API process can now answer `/health` as process liveness. The rest of the live operator loop is still not trustworthy evidence. `/readiness` can time out and block the app, the live benchmark runner can die during sandbox reset with an unhandled `httpx.ReadTimeout`, and a direct `/scout` run timed out on the first Thomas benchmark with zero returned rows. The offline source-assisted manual-oracle replay still passes, but the live service boundary does not yet prove either the autonomous Scout path or the source-assisted workbook path.

**Decision.** Keep RG3 in `gate_hold` and insert three ordered remediation slices before the next RG3 Prompt C audit:

- `R09J - Bounded readiness diagnostics`
- `R09K - Live runner timeout containment`
- `R09L - Live source-assisted product proof`

Only R09J is ready at first. R09K remains blocked until R09J passes Prompt B and merges. R09L remains blocked until R09K passes Prompt B and merges. Prompt C for RG3 must not rerun until R09J-R09L are merged. These slices are runtime and live-proof remediation inside RG3, not a new gate.

**Consequences.** The reset loop now attacks the remaining ambiguity in order: first make dependency readiness bounded and diagnostic, then make benchmark execution complete and artifact-preserving under timeouts, then prove the source-assisted workbook value path through the live API/service boundary. RG4, refreshed mockups, R10-R12, export polish, persistence, dogfood, and `main` promotion remain blocked. The new slices cannot pass by relaxing high-trust/READY semantics, inventing contacts, hiding runtime failures, or converting offline replay success into live product claims without current service-boundary evidence.

---

## ADR-022 — Approved RG4 mockups unlock R10 only

**Date:** 2026-05-12
**Status:** Locked

**Context.** RG3 advanced on the source-assisted operator loop, then the refreshed RG4 mockup/design preflight produced inspection artifacts under `docs/mockups/rg4-refreshed-preflight-2026-05-12/`. Matt reviewed and approved the design direction. The approved preflight reconciles `DESIGN.md` with the post-R09L source-assisted proof, including target/source context, categorized source-backed rows, READY/REVIEW separation, evidence dossier, low-signal guidance, and mobile triage.

**Decision.** Treat the refreshed RG4 mockups as the approved production UI direction for the RG4 implementation sequence. Unlock `R10 - Primary search workspace simplification` as the single ready Prompt A feature. Keep `R11 - Compact CRM-first results table`, `R12 - Evidence dossier review mode`, RG5 export/persistence, RG6 dogfood, and `main` promotion blocked until their documented prerequisites pass.

**Consequences.** R10 agents must implement against `DESIGN.md` and `docs/mockups/rg4-refreshed-preflight-2026-05-12/`, not the older May 10 visual styling. R10 may touch production UI only for the primary workspace/search-start/loading shell assigned to R10. It must not implement the full results table, evidence dossier, export, persistence, dogfood packet, or `main` sync. Any intentional divergence from the approved mockups must be documented in the R10 handoff and later audited in RG4 Prompt C.

---

## How to add a new ADR

1. Pick the next ADR number (ADR-023, ADR-024, ...).
2. Add an entry at the bottom of this file with the same format.
3. Set Status to "Locked" once Matt confirms.
4. If the new ADR overrides an old one, mark the old one's Status as "Superseded by ADR-NNN" but **do not delete or rewrite its body**.

ADRs are about "we considered alternatives and chose this." If the choice is trivial or reversible (e.g., a logging library), it doesn't need an ADR — just code it and note in commit message.
