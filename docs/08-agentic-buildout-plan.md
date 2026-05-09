# 08 - Agentic Buildout Plan

**Status:** Active control document for the validated-leads rebuild.
**Created:** 2026-05-09.
**Integration branch:** `rebuild/validated-leads-loop`.
**Current gate:** Red.
**Next feature pointer:** F02 Backend API Boundary (implemented_pending_qa).

This document is the missing-feature list and handoff surface for small-model build sessions. It is optimized for Matt's two-prompt loop: one prompt builds the next feature branch; one prompt QA's, documents, and merges that feature back into the rebuild integration branch.

## Current Reality

Treat `audits/zero-trust-product-audit-2026-05-09.md` as the current product reality:

- Do not ship.
- Do not daily-dogfood with Thomas or Lee.
- The decisive loop failed: natural-language target -> high-quality validated leads -> export.
- The Arizona K-12 VoIP benchmark failed.
- Live sampled search returned 0 CRM-usable leads under the audit standard.
- Backend endpoints were directly callable outside the password-gated UI.
- Recipe library, Friday review export, and bulk workspace are premature operator surfaces.
- The UI exposes implementation details.
- Guardrails miss B2C/privacy-sensitive targeting and some normal sales language.
- Source links are too shallow; the product needs field-level validation.
- Export must carry validation status and evidence, not just raw rows.

## Branch And PR Workflow

Non-negotiable branch rule: leave `main` alone.

Use exactly one persistent integration branch:

```text
rebuild/validated-leads-loop
```

Workflow for every feature after F00:

1. Start from `rebuild/validated-leads-loop`.
2. Pull latest with fast-forward only.
3. Create exactly one feature branch using the branch in the feature card.
4. Implement only that feature.
5. Push the feature branch.
6. Open exactly one PR targeting `rebuild/validated-leads-loop`.
7. QA on the feature branch.
8. Merge only into `rebuild/validated-leads-loop`.
9. Push `rebuild/validated-leads-loop`.
10. Never merge to `main`. Never open a PR targeting `main`. If a tool defaults to `main`, override it.

F00 bootstrap exception: this planning task creates the integration branch and lands the rebuild control docs directly on `rebuild/validated-leads-loop`. Every later feature must use the branch/PR loop above.

## Two-Prompt Loop

### Prompt A - Build Next Feature

```text
You are working in /Users/mschwar/Documents/white-rabbit.

Work only on the rebuild integration line. Do not touch main.

1. Read AGENTS.md, STATUS.md, docs/00-product-northstar.md, and docs/08-agentic-buildout-plan.md.
2. Checkout rebuild/validated-leads-loop and pull latest.
3. Pick the next feature whose status is ready from docs/08-agentic-buildout-plan.md.
4. Create its feature branch from rebuild/validated-leads-loop using the branch name in the feature card.
5. Implement only that feature. No opportunistic refactors. No adjacent features.
6. Run the feature's required tests or non-UI verification.
7. Update docs/08-agentic-buildout-plan.md and STATUS.md with what changed, the feature status, tests run, and next handoff.
8. Commit atomically with conventional commit messages.
9. Push the feature branch.
10. Do not merge. Do not open or target main.

Return:
- feature ID/name
- branch
- commits
- tests run
- files changed
- current status
- exact QA instructions for the next prompt
```

### Prompt B - QA, Docs, Merge To Rebuild Branch

```text
You are working in /Users/mschwar/Documents/white-rabbit.

QA the current feature branch and merge only into rebuild/validated-leads-loop. Never merge to main.

1. Read AGENTS.md, STATUS.md, docs/00-product-northstar.md, docs/08-agentic-buildout-plan.md, and the feature card being QA'd.
2. Checkout the feature branch and pull latest.
3. Run the required tests.
4. If the feature is UI-visible, run browser QA, take screenshots, and save them under .gstack/qa-reports/screenshots/.
5. If the feature is non-UI, run the explicit verification from the feature card and capture output.
6. Check the northstar reflection. If the feature drifts, fails, or overbuilds, fix it or mark QA failed.
7. Write a QA report in .gstack/qa-reports/.
8. Update docs/08-agentic-buildout-plan.md and STATUS.md.
9. Commit QA/docs/fixes atomically.
10. Push the feature branch.
11. Merge the feature branch into rebuild/validated-leads-loop only.
12. Push rebuild/validated-leads-loop.
13. Do not merge to main. Do not open a main-targeted PR.

Return:
- QA verdict
- screenshots/report path
- tests run
- commits
- merge target confirmation
- updated next feature pointer
```

## Northstar Reflection

Every agent must run this before choosing or merging a feature:

1. Does this feature directly improve natural-language query -> high-quality validated leads -> export?
2. Does it reduce false confidence, bad contacts, wrong personas, or unsupported source claims?
3. Does it avoid organizing or beautifying untrusted data?
4. Does it keep main untouched and target only `rebuild/validated-leads-loop`?
5. Is the feature independently mergeable?
6. Can the next agent discover the state from docs without this chat?
7. Is there a browser test or explicit non-UI verification?
8. Is the scope small enough for GPT-5.3 Spark or GPT-5.4 Mini?

If any answer is no, revise the feature plan or mark the feature blocked.

## Feature Sequencing

Order is intentional. Early work removes false confidence and protects the boundary before adding richer UI.

1. Foundation / anti-drift: F00-F03.
2. Search trust core: F04-F09.
3. Benchmarks / evaluation: F10-F12.
4. Operator loop: F13-F17.
5. Deferred / internal only: F18-F23.

Do not pull deferred surfaces back into primary navigation while the gate is red.

Phase gates are defined in `docs/09-rebuild-phase-gates.md`. Features still merge one branch at a time, but the first feature of a downstream wave must stay blocked until the prior wave has an `advance` gate review report.

## Missing Feature Table

| ID | Feature | Status | Branch | Verification |
| --- | --- | --- | --- | --- |
| F00 | Northstar + buildout docs + branch protocol | merged_to_rebuild_branch | feat/f00-agentic-buildout-plan | non-UI docs verification |
| F01 | Hide premature operator surfaces from primary navigation | merged_to_rebuild_branch | feat/f01-hide-premature-surfaces | browser |
| F02 | Backend API boundary | implemented_pending_qa | feat/f02-backend-api-boundary | browser + API |
| F03 | Guardrail rewrite for B2B scope and privacy blocking | ready | feat/f03-b2b-guardrails | non-UI |
| F04 | Query compiler / planner | blocked | feat/f04-query-compiler | non-UI |
| F05 | Candidate model separation | blocked | feat/f05-candidate-types | non-UI |
| F06 | Field-level validation schema | blocked | feat/f06-field-validation-schema | non-UI |
| F07 | Source validator | blocked | feat/f07-source-validator | non-UI |
| F08 | Contact status model | blocked | feat/f08-contact-status-model | non-UI |
| F09 | Ranking gate based on evidence | blocked | feat/f09-ranking-gate | non-UI |
| F10 | Golden Arizona K-12 VoIP benchmark harness | blocked | feat/f10-arizona-k12-benchmark | non-UI |
| F11 | Required benchmark suite | blocked | feat/f11-required-benchmark-suite | non-UI |
| F12 | Per-run quality report | blocked | feat/f12-run-quality-report | non-UI |
| F13 | Single search-bar UI | blocked | feat/f13-single-search-ui | browser |
| F14 | Results table with validation buckets | blocked | feat/f14-validation-results-table | browser |
| F15 | Evidence drawer / dossier | blocked | feat/f15-evidence-drawer | browser |
| F16 | Export rebuild with validation columns | blocked | feat/f16-validation-export | browser + CSV |
| F17 | Thomas/Lee correction feedback loop | blocked | feat/f17-corrections-feedback-loop | browser + DB |
| F18 | Recipe library internal-only policy | deferred | feat/f18-recipes-internal-only | browser |
| F19 | Batch workspace internal-only policy | deferred | feat/f19-batch-internal-only | browser |
| F20 | Friday review export internal-only policy | deferred | feat/f20-friday-review-internal-only | browser |
| F21 | Scoreboards internal-only policy | deferred | feat/f21-scoreboards-internal-only | browser |
| F22 | Operator minutes internal capture | deferred | feat/f22-operator-minutes-internal | browser |
| F23 | Sandbox reset internal-only policy | deferred | feat/f23-sandbox-reset-internal | browser |

## Status Rules

Use only these statuses:

- `blocked`: not ready because prerequisites or scope decisions are missing.
- `ready`: next build prompt may pick it.
- `in_progress`: build prompt is actively implementing it.
- `implemented_pending_qa`: branch is pushed and waiting for QA prompt.
- `qa_failed`: QA found a blocker; same feature branch must be fixed.
- `merged_to_rebuild_branch`: QA passed and feature branch merged into `rebuild/validated-leads-loop`.
- `deferred`: intentionally out of the red-gate operator path.

## Unblocking Rules

- F04 unblocks after F03 merges, because the planner must share the rewritten guardrail language and privacy boundary.
- F05-F09 unblock sequentially after F04 because they share the candidate/validation model.
- F10-F12 unblock after F09 because benchmarks must inspect the rebuilt validation and ranking outputs, not old lead cards.
- F13-F17 unblock after F12 because the operator UI should not organize untrusted data.
- F18-F23 remain deferred until the launch gate is yellow or green and Matt explicitly moves one to ready.

## Handoff Format

Every build and QA prompt must leave this in `STATUS.md` and, when useful, in the feature card note:

```text
Feature:
Branch:
Status:
What changed:
Tests or QA run:
Screenshots or report:
Northstar reflection:
Next pointer:
Open questions:
```

The next agent should understand the state in under 60 seconds from this block plus the feature table.

## Atomic Commit Guidelines

For each feature PR:

- Prefer 1-3 commits.
- Each commit should be coherent and revertible.
- Use conventional commits:
  - `docs(northstar): define validated-lead product loop`
  - `fix(auth): require backend access token for scout endpoints`
  - `feat(search): compile long benchmark prompts into bounded vendor queries`
  - `test(guardrails): block consumer privacy targeting`
  - `qa(f10): record arizona benchmark browser verification`
- Do not create "misc", "updates", or "fix stuff" commits.
- Do not mix docs, implementation, and broad cleanup unless the feature card calls for it.

---

## F00 - Northstar + Buildout Docs + Branch Protocol

Status: merged_to_rebuild_branch
Branch: feat/f00-agentic-buildout-plan
PR target: rebuild/validated-leads-loop
Estimated model fit: GPT-5.3 Spark / GPT-5.4 Mini
Max intended scope: 1 small feature, preferably <= 5 touched files unless justified.

Goal:
Create the anti-drift docs, rebuild branch protocol, status update, and QA template that make the two-prompt loop possible.

Why this matters to the northstar:
It prevents future agents from polishing premature surfaces instead of rebuilding natural-language query -> validated leads -> export.

User story:
As Matt, I need the rebuild plan to live in the repo so small models can pick up the next feature without chat context.

Anti-goals:
- Do not implement product features.
- Do not edit the frozen Scotty demo.
- Do not merge or target main.
- Do not declare the product yellow or green.

Implementation boundaries:
Files likely touched: `docs/00-product-northstar.md`, `docs/08-agentic-buildout-plan.md`, `AGENTS.md`, `STATUS.md`, `.gstack/qa-reports/qa-template-agentic-buildout.md`.
Files not to touch: `apps/web`, `apps/api`, `packages/core`, `/Users/mschwar/Documents/proxy-lead`.
No opportunistic refactors.

Acceptance criteria:
- Product northstar doc exists and states bad data shown confidently is worse than no data.
- Buildout plan includes branch workflow, two prompts, reflection checklist, feature table, and feature cards.
- AGENTS has a rebuild branch protocol.
- STATUS records integration branch, red gate, next pointer, and why main is untouched.
- QA template exists.

Verification:
non-UI verification:
- command(s): `git diff --check`; `rg -n "rebuild/validated-leads-loop|F01|Northstar reflection|Feature ID" docs AGENTS.md STATUS.md .gstack/qa-reports/qa-template-agentic-buildout.md`
- expected output: no whitespace errors; required markers found.
- fixture/test file: n/a.

Atomic commit plan:
- commit 1: `docs(northstar): define validated-leads rebuild loop`
- commit 2: `docs(buildout): add agentic feature plan and QA template`
- commit 3 if needed: `docs(status): record rebuild branch protocol`

Rollback plan:
Revert the docs-only commit on `rebuild/validated-leads-loop`; do not touch `main`.

Next-agent handoff note:
F00 was bootstrapped directly on the integration branch per Matt's planning-task instruction. Future features must use their feature branch and PR target.

---

## F01 - Hide Premature Operator Surfaces

Status: merged_to_rebuild_branch
Branch: feat/f01-hide-premature-surfaces
PR target: rebuild/validated-leads-loop
Estimated model fit: GPT-5.3 Spark / GPT-5.4 Mini
Max intended scope: 1 small feature, preferably <= 5 touched files unless justified.

Goal:
Remove recipe library, batch workspace, Friday export, sandbox reset, and implementation-detail copy from the primary operator path while the product is red.

Why this matters to the northstar:
It stops the UI from organizing untrusted data and refocuses operators on one query-to-results path.

User story:
As Thomas, I need the first screen to feel like a lead search tool, not an admin console for recipes, batch jobs, APIs, and quotas.

Anti-goals:
- Do not delete backend endpoints or data models.
- Do not redesign the full results experience.
- Do not add new nav surfaces.
- Do not change scoring or extraction.

Implementation boundaries:
Files likely touched: `apps/web/src/app/page.tsx`, `apps/web/src/components/scout-workspace.tsx`, related component tests.
Files not to touch: `apps/api`, `packages/core`, database migrations.
No opportunistic refactors.

Acceptance criteria:
- Home page primary navigation links only to the lead search path.
- `/recipes` and `/batch` are not linked from primary operator navigation.
- Scout page no longer displays `FastAPI`, raw endpoint names, recipe storage, or sandbox reset implementation copy.
- Sandbox reset button is hidden from the primary operator path.
- Existing routes may remain reachable for internal use unless the feature intentionally gates them.

Verification:
Browser-testable:
- route: `/`, `/scout`
- steps: log in, confirm home navigation, open Scout, inspect visible text, confirm no recipe/batch/implementation-detail primary calls to action.
- required screenshots: home after login, Scout empty state, Scout quota area without reset/internal implementation copy.

Build verification run on 2026-05-09:
- `npm test` in `apps/web`: 25 tests passed.
- `npm run build` in `apps/web`: passed; existing Next.js warnings about root lockfile inference and `middleware.ts` deprecation remain.
- Browser smoke on `http://localhost:3000`: logged in with local test env, confirmed home has only the lead-search link, Scout hides reset/internal endpoint/storage copy, and console errors were empty.
- Screenshots saved: `.gstack/qa-reports/screenshots/f01-home-after-login.png`, `.gstack/qa-reports/screenshots/f01-scout-empty-state.png`.

Atomic commit plan:
- commit 1: `fix(ui): hide premature operator surfaces from primary navigation`
- commit 2: `test(ui): update navigation and scout copy expectations`
- commit 3 if needed: `docs(f01): record surface-hiding QA handoff`

Rollback plan:
Revert the UI commit to restore prior navigation and Scout copy; data and endpoints remain untouched.

Next-agent handoff note:
QA passed and branch `feat/f01-hide-premature-surfaces` is merged to `rebuild/validated-leads-loop`. Home now links only to lead search; Scout hides recipe-library links, raw endpoint/FastAPI/storage copy, and the sandbox reset button while keeping existing internal routes reachable. Screenshot paths:

- `.gstack/qa-reports/screenshots/f01-home-after-login.png`
- `.gstack/qa-reports/screenshots/f01-scout-empty-state.png`

---

## F02 - Backend API Boundary

Status: implemented_pending_qa
Branch: feat/f02-backend-api-boundary
PR target: rebuild/validated-leads-loop
Estimated model fit: GPT-5.3 Spark / GPT-5.4 Mini
Max intended scope: 1 small feature, preferably <= 5 touched files unless justified.

Goal:
Prevent public direct calls to lead-search and reset endpoints outside the same boundary expected by the app, or explicitly restrict ingress.

Why this matters to the northstar:
A validated-lead product cannot be trusted if `/scout`, `/full`, `/batch`, or `/sandbox/reset` can be called directly and anonymously.

User story:
As Matt, I need the backend boundary to match the password-gated app boundary before any operator testing.

Anti-goals:
- Do not build per-user auth.
- Do not add signup, accounts, orgs, billing, or multi-tenancy.
- Do not redesign the web auth flow unless required for the boundary.

Implementation boundaries:
Files likely touched: `apps/api/api/main.py`, `apps/api/tests/test_api.py`, Next proxy routes in `apps/web/src/app/api/**/route.ts`, `.env.example` files, README or deployment notes if env vars change.
Files not to touch: lead extraction logic, UI layout except error handling if needed.
No opportunistic refactors.

Acceptance criteria:
- Direct unauthenticated calls to `POST /scout`, `POST /full`, `POST /batch`, and `POST /sandbox/reset` fail with 401 or 403.
- App proxy calls still work when configured with the internal token or ingress boundary.
- `GET /health` remains public.
- Local development setup documents the boundary env var or ingress rule.
- Tests prove allowed and denied paths.

Verification:
Browser-testable:
- route: `/scout`
- steps: run API and web locally with boundary env vars, log in, run a Scout query or mocked route, confirm web proxy succeeds; use curl/PowerShell against the API directly without token and confirm protected endpoints reject.
- required screenshots: Scout successful or expected non-data error through UI, terminal/API output in QA report for direct-call rejection.

Atomic commit plan:
- commit 1: `fix(auth): require backend boundary for lead endpoints`
- commit 2: `test(auth): cover protected backend endpoints`
- commit 3 if needed: `docs(auth): document internal API boundary`

Rollback plan:
Revert token/ingress enforcement and proxy env wiring together; verify local `/health` still works.

Next-agent handoff note:
The app-token path is in place. QA should verify the web proxy succeeds with `WR_API_INTERNAL_TOKEN` set, then prove tokenless direct API calls to the protected endpoints return 401/403 and capture the browser/API evidence in the QA report.

---

## F03 - Guardrail Rewrite For B2B Scope And Privacy Blocking

Status: ready
Branch: feat/f03-b2b-guardrails
PR target: rebuild/validated-leads-loop
Estimated model fit: GPT-5.3 Spark / GPT-5.4 Mini
Max intended scope: 1 small feature, preferably <= 5 touched files unless justified.

Goal:
Rewrite query guardrails so normal B2B sales language is allowed and B2C/privacy-sensitive targeting is blocked before search.

Why this matters to the northstar:
It prevents unsafe or out-of-scope searches while allowing Thomas's real sales language to enter the validated-leads loop.

User story:
As Thomas, I need to type normal phrases like "financial services CISOs in New York" and be guided only when the prompt is truly outside lead generation or privacy-safe B2B prospecting.

Anti-goals:
- Do not call an LLM for guardrails in this feature.
- Do not implement query planning.
- Do not weaken privacy boundaries to preserve recall.

Implementation boundaries:
Files likely touched: `packages/core/src/core/query_guardrails.py`, `packages/core/tests/test_query_guardrails.py`, `apps/api/tests/test_api.py` if API expectations change.
Files not to touch: orchestrator, search vendor calls, UI redesign.
No opportunistic refactors.

Acceptance criteria:
- Allows: `financial services CISOs in New York`, `manufacturing operations leaders in Detroit`, `food and beverage operations leaders in Texas`, `contractors in Illinois`, and the Arizona K-12 target prompt.
- Blocks: home-refinance/private-person targeting, public social-media vacation-photo email targeting, non-lead advice, and weapon/off-topic prompts.
- Vague B2B lead queries return a warning status, not a hard block.
- Blocked queries never call `scout()`.

Verification:
non-UI verification:
- command(s): `cd packages/core && uv run pytest tests/test_query_guardrails.py -q`; `cd apps/api && uv run pytest tests/test_api.py -q -k guardrail`
- expected output: tests pass; explicit privacy examples are blocked.
- fixture/test file: `packages/core/tests/test_query_guardrails.py`.

Atomic commit plan:
- commit 1: `fix(guardrails): allow normal b2b sales language`
- commit 2: `test(guardrails): block consumer privacy targeting`
- commit 3 if needed: `docs(f03): record guardrail verification`

Rollback plan:
Revert guardrail and tests together; API falls back to previous guardrail behavior.

Next-agent handoff note:
After F03 merges, update this doc to mark F04 ready if no new guardrail blockers appear.

---

## F04 - Query Compiler / Planner

Status: blocked
Branch: feat/f04-query-compiler
PR target: rebuild/validated-leads-loop
Estimated model fit: GPT-5.3 Spark / GPT-5.4 Mini
Max intended scope: 1 small feature, preferably <= 5 touched files unless justified.

Goal:
Convert long natural-language prompts into bounded vendor searches under Tavily limits, including named-account decomposition.

Why this matters to the northstar:
The Arizona benchmark failed because the app sent Thomas's full prompt directly to Tavily; planning is required before validated leads can exist.

User story:
As Thomas, I need to paste a realistic target prompt and have White Rabbit search the right bounded account/persona queries instead of crashing.

Anti-goals:
- Do not change UI.
- Do not build field validation in this feature.
- Do not add broad vendor abstraction.

Implementation boundaries:
Files likely touched: new `packages/core/src/core/query_planner.py`, `packages/core/src/core/search.py`, `packages/core/src/core/orchestrator.py`, core tests.
Files not to touch: web components, database schema.
No opportunistic refactors.

Acceptance criteria:
- Thomas's full Arizona prompt compiles into one plan with eight named accounts.
- Every vendor query is <= 400 characters.
- Planner preserves persona, geography, vertical, and named-account constraints.
- Existing simple queries still produce one bounded search.

Verification:
non-UI verification:
- command(s): `cd packages/core && uv run pytest tests/test_query_planner.py tests/test_search.py -q`
- expected output: planner tests pass; no compiled query exceeds Tavily limit.
- fixture/test file: `packages/core/tests/test_query_planner.py`.

Atomic commit plan:
- commit 1: `feat(search): add bounded query planner`
- commit 2: `test(search): compile arizona benchmark prompt under tavily limits`
- commit 3 if needed: `docs(f04): mark planner handoff`

Rollback plan:
Remove planner module and revert search/orchestrator integration; old direct query path returns.

Next-agent handoff note:
F05 should consume the planner output without reworking its parsing rules.

---

## F05 - Candidate Model Separation

Status: blocked
Branch: feat/f05-candidate-types
PR target: rebuild/validated-leads-loop
Estimated model fit: GPT-5.3 Spark / GPT-5.4 Mini
Max intended scope: 1 small feature, preferably <= 5 touched files unless justified.

Goal:
Distinguish `person_lead`, `organization_only`, and `not_found`, and prevent companies from appearing in the person name field.

Why this matters to the northstar:
The audit found companies returned as people; separating candidate types prevents wrong personas from being dressed up as leads.

User story:
As Thomas, I need account-only or not-found results clearly labeled so I do not waste time treating a company row as a contact.

Anti-goals:
- Do not build the final results table.
- Do not implement source validation.
- Do not remove existing persistence unless required by typed compatibility.

Implementation boundaries:
Files likely touched: `packages/core/src/core/models.py`, `packages/core/tests/test_models.py`, `apps/api/api/main.py` response models if needed, API tests.
Files not to touch: UI layout beyond type compatibility.
No opportunistic refactors.

Acceptance criteria:
- Candidate category is explicit on every returned item.
- `person_lead.name` validators reject organization-like names and role-only names.
- Organization-only rows cannot pass as person leads.
- Not-found rows can explain a searched target account without fake lead fields.

Verification:
non-UI verification:
- command(s): `cd packages/core && uv run pytest tests/test_models.py -q`; `cd apps/api && uv run pytest tests/test_api.py -q -k scout`
- expected output: model/API tests pass and company-as-person fixtures fail validation.
- fixture/test file: `packages/core/tests/test_models.py`.

Atomic commit plan:
- commit 1: `feat(core): add lead candidate categories`
- commit 2: `test(core): reject company rows in person fields`
- commit 3 if needed: `docs(f05): record candidate model handoff`

Rollback plan:
Revert candidate schema and API mapping together; previous Lead model returns.

Next-agent handoff note:
F06 should add field validation to these candidate categories rather than inventing a parallel schema.

---

## F06 - Field-Level Validation Schema

Status: blocked
Branch: feat/f06-field-validation-schema
PR target: rebuild/validated-leads-loop
Estimated model fit: GPT-5.3 Spark / GPT-5.4 Mini
Max intended scope: 1 small feature, preferably <= 5 touched files unless justified.

Goal:
Add a validation schema for name, title, organization, email, phone, source, status, checked_at, and validation notes.

Why this matters to the northstar:
White Rabbit's value is transparent field-level evidence, not a naked source URL and a confident card.

User story:
As Thomas, I need to know which source supports each field before I trust a row.

Anti-goals:
- Do not build the evidence drawer.
- Do not implement URL fetching logic.
- Do not change ranking.

Implementation boundaries:
Files likely touched: `packages/core/src/core/models.py`, API serialization tests, possibly DB JSON storage tests.
Files not to touch: UI components except type compatibility.
No opportunistic refactors.

Acceptance criteria:
- Every candidate can carry validation records for name, title, org, email, phone, and source.
- Each validation record includes status, source URL, checked_at, and notes.
- Existing leads without full validation are explicitly unsupported or missing, not implicitly trusted.

Verification:
non-UI verification:
- command(s): `cd packages/core && uv run pytest tests/test_models.py -q`; `cd apps/api && uv run pytest tests/test_api.py -q -k full`
- expected output: schema tests pass; serialization stays stable.
- fixture/test file: `packages/core/tests/test_models.py`.

Atomic commit plan:
- commit 1: `feat(core): add field validation schema`
- commit 2: `test(core): serialize field validation records`
- commit 3 if needed: `docs(f06): record schema handoff`

Rollback plan:
Revert schema additions and compatibility mappings; persisted historical JSON remains untouched.

Next-agent handoff note:
F07 is responsible for populating this schema with source checks.

---

## F07 - Source Validator

Status: blocked
Branch: feat/f07-source-validator
PR target: rebuild/validated-leads-loop
Estimated model fit: GPT-5.3 Spark / GPT-5.4 Mini
Max intended scope: 1 small feature, preferably <= 5 touched files unless justified.

Goal:
Resolve source URLs and check which fields each source supports; source URL alone is not evidence.

Why this matters to the northstar:
The audit found URLs that resolved but did not support the claimed title/org/email, plus inaccessible sources treated as evidence.

User story:
As Matt, I need each source to say what it actually proves so unsupported claims can be downgraded before export.

Anti-goals:
- Do not add browser UI.
- Do not implement paid enrichment.
- Do not scrape LinkedIn behind access controls.

Implementation boundaries:
Files likely touched: new `packages/core/src/core/source_validation.py`, orchestrator integration, tests with mocked HTTP.
Files not to touch: web UI, database migrations unless unavoidable.
No opportunistic refactors.

Acceptance criteria:
- Validator records resolved URL, HTTP/access status, checked_at, and field support booleans or statuses.
- Inaccessible sources mark evidence as unsupported/failed.
- Field support requires text adjacency or explicit source content, not URL presence.
- Tests cover 200 supported, 200 unsupported, 403, 404, and blocked/999-like responses.

Verification:
non-UI verification:
- command(s): `cd packages/core && uv run pytest tests/test_source_validation.py -q`
- expected output: all mocked source validation cases pass.
- fixture/test file: `packages/core/tests/test_source_validation.py`.

Atomic commit plan:
- commit 1: `feat(validation): add source field-support checks`
- commit 2: `test(validation): cover inaccessible and unsupported sources`
- commit 3 if needed: `docs(f07): record source validator handoff`

Rollback plan:
Remove validator integration and keep field validation statuses unsupported.

Next-agent handoff note:
F08 should reuse source validation evidence for contact statuses.

---

## F08 - Contact Status Model

Status: blocked
Branch: feat/f08-contact-status-model
PR target: rebuild/validated-leads-loop
Estimated model fit: GPT-5.3 Spark / GPT-5.4 Mini
Max intended scope: 1 small feature, preferably <= 5 touched files unless justified.

Goal:
Replace shallow email status with `verified_found`, `deduced_with_pattern_evidence`, `missing`, `failed`, and `unsupported`.

Why this matters to the northstar:
No silent guessing is allowed; contact usability must be explicit before a row can be CRM-ready.

User story:
As Thomas, I need to know whether an email or phone is verified, deduced with evidence, missing, failed, or unsupported.

Anti-goals:
- Do not send emails or verify inbox deliverability.
- Do not add paid enrichment providers.
- Do not infer contacts without pattern evidence.

Implementation boundaries:
Files likely touched: `packages/core/src/core/models.py`, contact validation helpers, export typings/tests if needed.
Files not to touch: UI evidence drawer, ranking gate except compatibility.
No opportunistic refactors.

Acceptance criteria:
- Contact status enum exists for email and phone.
- `Found` cannot be emitted without direct source support.
- Deduced emails require verified domain-pattern evidence and notes.
- Missing/failed/unsupported are represented distinctly.

Verification:
non-UI verification:
- command(s): `cd packages/core && uv run pytest tests/test_models.py tests/test_contact_status.py -q`
- expected output: contact status tests pass; unsupported guesses fail.
- fixture/test file: `packages/core/tests/test_contact_status.py`.

Atomic commit plan:
- commit 1: `feat(validation): add explicit contact statuses`
- commit 2: `test(validation): reject silent email guessing`
- commit 3 if needed: `docs(f08): record contact model handoff`

Rollback plan:
Revert contact status enum and mappings to previous email_status behavior.

Next-agent handoff note:
F09 should use these statuses to compute contact usability and ranking gates.

---

## F09 - Ranking Gate Based On Evidence

Status: blocked
Branch: feat/f09-ranking-gate
PR target: rebuild/validated-leads-loop
Estimated model fit: GPT-5.3 Spark / GPT-5.4 Mini
Max intended scope: 1 small feature, preferably <= 5 touched files unless justified.

Goal:
Rank and gate rows based on persona fit, field evidence, contact usability, and source support, not generic LLM confidence.

Why this matters to the northstar:
Validated signal must determine what appears usable; raw LLM optimism cannot rank leads.

User story:
As Thomas, I need the top rows to be the most usable and defensible contacts, not the best-written explanations.

Anti-goals:
- Do not redesign UI.
- Do not introduce a single opaque composite rank.
- Do not hide failed/noisy rows by deleting them.

Implementation boundaries:
Files likely touched: new or existing scoring module in `packages/core/src/core`, orchestrator post-processing, tests.
Files not to touch: browser UI except type compatibility.
No opportunistic refactors.

Acceptance criteria:
- Gate is server-computed from validation evidence and contact status.
- Wrong persona, unsupported title/org, and failed contact cannot pass.
- Composite score may be used as a gate/order helper but is not exposed as the primary rank.
- Tests cover fake email, wrong persona, organization-only, not-found, and verified lead cases.

Verification:
non-UI verification:
- command(s): `cd packages/core && uv run pytest tests/test_scoring.py tests/test_orchestrator.py -q`
- expected output: ranking/gate tests pass.
- fixture/test file: `packages/core/tests/test_scoring.py`.

Atomic commit plan:
- commit 1: `feat(scoring): gate leads on validation evidence`
- commit 2: `test(scoring): block false-confidence rows`
- commit 3 if needed: `docs(f09): record ranking handoff`

Rollback plan:
Revert scoring module and post-processing integration; previous gate behavior returns.

Next-agent handoff note:
F10 should treat these gates as the benchmark output contract.

---

## F10 - Golden Arizona K-12 VoIP Benchmark Harness

Status: blocked
Branch: feat/f10-arizona-k12-benchmark
PR target: rebuild/validated-leads-loop
Estimated model fit: GPT-5.3 Spark / GPT-5.4 Mini
Max intended scope: 1 small feature, preferably <= 5 touched files unless justified.

Goal:
Create the golden Arizona K-12 VoIP benchmark harness with target districts and known failure cases.

Why this matters to the northstar:
This is the decisive customer benchmark; passing it is required before Thomas or Lee dogfood.

User story:
As Matt, I need a repeatable harness that proves White Rabbit handles Thomas's actual district/persona/contact standard.

Anti-goals:
- Do not hardcode VoIP bias into production prompts.
- Do not treat GPT workbook rows as ground truth.
- Do not require live API keys for default CI.

Implementation boundaries:
Files likely touched: `benchmarks/` or `packages/core/tests/fixtures/`, `packages/core/tests/test_arizona_k12_benchmark.py`, docs references.
Files not to touch: UI, production extraction logic except test hooks if necessary.
No opportunistic refactors.

Acceptance criteria:
- Fixture lists Mesa, Chandler, Peoria, Gilbert, Deer Valley, Paradise Valley, Dysart, and Maricopa.
- Fixture includes Thomas workbook annotations: failed email, not-correct contact, in CRM, added to CRM where known.
- Harness can run offline against mocked outputs and optionally live with env flag.
- Failing cases check zero fake emails and explicit not-found/failed states.

Verification:
non-UI verification:
- command(s): `cd packages/core && uv run pytest tests/test_arizona_k12_benchmark.py -q`
- expected output: offline benchmark tests pass.
- fixture/test file: `packages/core/tests/fixtures/arizona_k12_voip.json`.

Atomic commit plan:
- commit 1: `test(benchmarks): add arizona k12 voip fixture`
- commit 2: `test(benchmarks): add golden benchmark harness`
- commit 3 if needed: `docs(f10): document arizona benchmark standard`

Rollback plan:
Remove benchmark fixture and tests; production code remains untouched.

Next-agent handoff note:
F11 should extend this harness rather than creating a parallel evaluation path.

---

## F11 - Required Benchmark Suite

Status: blocked
Branch: feat/f11-required-benchmark-suite
PR target: rebuild/validated-leads-loop
Estimated model fit: GPT-5.3 Spark / GPT-5.4 Mini
Max intended scope: 1 small feature, preferably <= 5 touched files unless justified.

Goal:
Add required benchmark coverage for simple B2B queries, vertical generalization, guardrails, and privacy rejection.

Why this matters to the northstar:
One golden benchmark proves the core case; a suite prevents rebuilding another single-vertical demo.

User story:
As Matt, I need every extraction/scoring change to prove it works beyond Arizona schools.

Anti-goals:
- Do not require live APIs in default tests.
- Do not add UI screenshots as a substitute for data-quality checks.
- Do not loosen the Arizona standard.

Implementation boundaries:
Files likely touched: benchmark fixtures/tests under `packages/core/tests` or `benchmarks/`, `docs/qa-rubric.md` references if needed.
Files not to touch: UI, production schema unless tests reveal an existing blocker.
No opportunistic refactors.

Acceptance criteria:
- Includes simple B2B queries from the audit: contractors in Illinois, food/beverage operations leaders in Texas, healthcare IT directors in Phoenix, finance CISOs in New York, manufacturing operations leaders in Detroit.
- Includes guardrail accept/reject fixtures.
- Reports pass/fail by persona, contact, source, and privacy refusal.
- Can run in CI without live keys.

Verification:
non-UI verification:
- command(s): `cd packages/core && uv run pytest tests/test_benchmark_suite.py -q`
- expected output: offline benchmark suite passes.
- fixture/test file: `packages/core/tests/fixtures/benchmark_suite.json`.

Atomic commit plan:
- commit 1: `test(benchmarks): add required lead-quality suite`
- commit 2: `test(benchmarks): cover privacy rejection fixtures`
- commit 3 if needed: `docs(f11): document benchmark suite usage`

Rollback plan:
Remove suite fixtures/tests; Arizona harness remains.

Next-agent handoff note:
F12 should generate metrics from this suite and from live runs using the same definitions.

---

## F12 - Per-Run Quality Report

Status: blocked
Branch: feat/f12-run-quality-report
PR target: rebuild/validated-leads-loop
Estimated model fit: GPT-5.3 Spark / GPT-5.4 Mini
Max intended scope: 1 small feature, preferably <= 5 touched files unless justified.

Goal:
Produce per-run quality metrics: precision, persona match, contact quality, source support, fake-email count, and not-found count.

Why this matters to the northstar:
The product needs objective run quality before UI surfaces can be trusted.

User story:
As Matt, I need a run report that tells me whether a result set is usable or dangerous before giving it to Thomas.

Anti-goals:
- Do not create a scoreboard UI.
- Do not add customer-facing analytics.
- Do not call a model to grade itself.

Implementation boundaries:
Files likely touched: `packages/core/src/core/quality_report.py`, core tests, API response typing if exposed.
Files not to touch: primary UI, recipe scoreboard.
No opportunistic refactors.

Acceptance criteria:
- Quality report computes counts and rates from candidate categories and validation statuses.
- Fake/unsupported email count is explicit.
- Not-found count is explicit for named-account searches.
- Report can be serialized for benchmark and run artifacts.

Verification:
non-UI verification:
- command(s): `cd packages/core && uv run pytest tests/test_quality_report.py -q`
- expected output: metrics tests pass against fixture rows.
- fixture/test file: `packages/core/tests/test_quality_report.py`.

Atomic commit plan:
- commit 1: `feat(evaluation): add per-run quality report`
- commit 2: `test(evaluation): count fake emails and not-found rows`
- commit 3 if needed: `docs(f12): record quality report handoff`

Rollback plan:
Remove quality report module and any API field additions.

Next-agent handoff note:
F13 can now build UI against quality-checked outputs.

---

## F13 - Single Search-Bar UI

Status: blocked
Branch: feat/f13-single-search-ui
PR target: rebuild/validated-leads-loop
Estimated model fit: GPT-5.3 Spark / GPT-5.4 Mini
Max intended scope: 1 small feature, preferably <= 5 touched files unless justified.

Goal:
Orient the primary UI around one natural-language lead search bar.

Why this matters to the northstar:
Thomas's desired workflow is "type the sales target and get validated leads," not choose modes or understand internal app concepts.

User story:
As Thomas, I need to start with a single lead-search input that accepts job title, vertical, company size, location, and named accounts in natural language.

Anti-goals:
- Do not bring back recipe/batch navigation.
- Do not build the evidence drawer.
- Do not add marketing/landing-page content.

Implementation boundaries:
Files likely touched: `apps/web/src/app/page.tsx`, `apps/web/src/components/scout-workspace.tsx` or new focused component, tests.
Files not to touch: backend validation/scoring.
No opportunistic refactors.

Acceptance criteria:
- First authenticated screen centers on a single lead-search input.
- Scout/Full terminology is absent from primary copy.
- Operator can run one search without selecting internal mode concepts.
- Empty state does not expose implementation details.

Verification:
Browser-testable:
- route: `/`
- steps: log in, enter a natural-language B2B query, submit, confirm loading and result/error state.
- required screenshots: empty search state, loading state, returned state or validation error.

Atomic commit plan:
- commit 1: `feat(ui): add single natural-language lead search`
- commit 2: `test(ui): cover primary search workflow`
- commit 3 if needed: `docs(f13): record browser QA handoff`

Rollback plan:
Revert UI component/page changes; hidden internal routes remain available.

Next-agent handoff note:
F14 should replace card-first rendering with bucketed validated results.

---

## F14 - Results Table With Validation Buckets

Status: blocked
Branch: feat/f14-validation-results-table
PR target: rebuild/validated-leads-loop
Estimated model fit: GPT-5.3 Spark / GPT-5.4 Mini
Max intended scope: 1 small feature, preferably <= 5 touched files unless justified.

Goal:
Show validated results in a table with badges and separate usable, noisy, organization-only, not-found, and failed rows.

Why this matters to the northstar:
Noise is useful only when it is visibly separated from usable leads and does not masquerade as CRM-ready data.

User story:
As Thomas, I need to scan which rows are usable and which rows are noisy or not found.

Anti-goals:
- Do not build export changes.
- Do not add recipe or batch surfaces.
- Do not hide failed rows by deleting them.

Implementation boundaries:
Files likely touched: results component and tests in `apps/web/src/components`, `apps/web/src/lib/scout.ts` types.
Files not to touch: backend scoring logic.
No opportunistic refactors.

Acceptance criteria:
- Person leads, noisy/failed rows, organization-only rows, and not-found rows render in clearly labeled groups.
- Validation badges reflect field/contact/source statuses.
- Companies never render in the person-name column unless category is organization-only.
- Existing card-only view is removed or secondary.

Verification:
Browser-testable:
- route: primary search route from F13.
- steps: use mocked or fixture-backed response with all candidate categories; verify grouping and badges.
- required screenshots: usable group, noisy/failed group, organization-only/not-found group.

Atomic commit plan:
- commit 1: `feat(ui): render validation-bucketed results table`
- commit 2: `test(ui): cover candidate categories and badges`
- commit 3 if needed: `docs(f14): record results table handoff`

Rollback plan:
Revert results table component and restore previous result rendering.

Next-agent handoff note:
F15 should add drill-down evidence without changing bucket definitions.

---

## F15 - Evidence Drawer Or Dossier

Status: blocked
Branch: feat/f15-evidence-drawer
PR target: rebuild/validated-leads-loop
Estimated model fit: GPT-5.3 Spark / GPT-5.4 Mini
Max intended scope: 1 small feature, preferably <= 5 touched files unless justified.

Goal:
Add a dossier/drawer that shows which source supports which field.

Why this matters to the northstar:
Transparent evidence is the product differentiator; operators must see why each field is trusted or rejected.

User story:
As Thomas, I need to open a row and see the source support for name, title, organization, email, and phone.

Anti-goals:
- Do not build source validation logic.
- Do not redesign the whole page.
- Do not add a generic CRM profile view.

Implementation boundaries:
Files likely touched: results component, evidence drawer component, tests.
Files not to touch: core validation algorithms.
No opportunistic refactors.

Acceptance criteria:
- Drawer opens from a result row.
- Drawer lists field, status, source URL, checked_at, and notes.
- Unsupported/missing/failed fields are visually distinct from verified fields.
- Drawer can be used on person, organization-only, not-found, and failed rows.

Verification:
Browser-testable:
- route: primary search route from F13.
- steps: load fixture response, open evidence for one usable and one failed/noisy row.
- required screenshots: evidence drawer for usable row, evidence drawer for failed/noisy row.

Atomic commit plan:
- commit 1: `feat(ui): add field evidence drawer`
- commit 2: `test(ui): cover evidence drawer statuses`
- commit 3 if needed: `docs(f15): record evidence drawer handoff`

Rollback plan:
Revert drawer component and row action; results table remains.

Next-agent handoff note:
F16 should export the same evidence fields shown here.

---

## F16 - Export Rebuild With Validation Columns

Status: blocked
Branch: feat/f16-validation-export
PR target: rebuild/validated-leads-loop
Estimated model fit: GPT-5.3 Spark / GPT-5.4 Mini
Max intended scope: 1 small feature, preferably <= 5 touched files unless justified.

Goal:
Rebuild export so validation columns travel with the data and default export includes usable leads plus explicitly flagged noisy rows.

Why this matters to the northstar:
Export is the final step of the core loop; raw rows without validation recreate the ZoomInfo/DiscoverOrg problem.

User story:
As Thomas, I need a CSV/Excel-style export that tells me which fields were validated and which rows are safe to contact.

Anti-goals:
- Do not add HubSpot-specific automation unless explicitly scoped.
- Do not export uncertain rows as clean leads.
- Do not build batch export.

Implementation boundaries:
Files likely touched: `apps/web/src/lib/full-export.ts` or new export helper, export UI component/tests, possibly API response typings.
Files not to touch: benchmark harness, backend auth.
No opportunistic refactors.

Acceptance criteria:
- CSV includes required northstar validation columns.
- Default export clearly flags usable, noisy, organization-only, not-found, and failed rows.
- Fake/unsupported contacts are marked failed/unsupported in export.
- CSV inspection test verifies header, row count, validation notes, and absence of placeholder contacts.

Verification:
Browser-testable:
- route: primary search/results route.
- steps: run or load fixture results, build export, open/inspect CSV content.
- required screenshots: export control, export ready state, CSV content or QA report excerpt.

Atomic commit plan:
- commit 1: `feat(export): include field validation columns`
- commit 2: `test(export): inspect validation CSV output`
- commit 3 if needed: `docs(f16): record export QA handoff`

Rollback plan:
Revert export helper and UI wiring; prior export path returns.

Next-agent handoff note:
F17 should use exported/validated rows as the feedback target, not raw lead cards.

---

## F17 - Thomas/Lee Correction Feedback Loop

Status: blocked
Branch: feat/f17-corrections-feedback-loop
PR target: rebuild/validated-leads-loop
Estimated model fit: GPT-5.3 Spark / GPT-5.4 Mini
Max intended scope: 1 small feature, preferably <= 5 touched files unless justified.

Goal:
Record Thomas/Lee corrections into benchmark fixtures or a review queue.

Why this matters to the northstar:
Operator corrections should improve validation and benchmarks, not disappear into generic feedback buttons.

User story:
As Matt, I need Thomas and Lee's corrections to become durable evaluation data.

Anti-goals:
- Do not train a model.
- Do not add full CRM management.
- Do not require per-user accounts.

Implementation boundaries:
Files likely touched: feedback API/DB or local fixture queue, results UI correction control, tests.
Files not to touch: recipe library, batch workspace.
No opportunistic refactors.

Acceptance criteria:
- Operator can mark correction type: wrong persona, bad contact, bad source, duplicate, corrected field, or usable.
- Correction stores candidate ID/run ID/query and the field being corrected.
- Corrections are exportable into a benchmark fixture or review queue.
- Existing feedback labels remain compatible or are migrated intentionally.

Verification:
Browser-testable:
- route: primary results route.
- steps: submit a correction on a fixture row, verify API/storage or fixture queue record.
- required screenshots: correction control, submitted state, QA evidence of stored correction.

Atomic commit plan:
- commit 1: `feat(feedback): capture field-level operator corrections`
- commit 2: `test(feedback): store corrections for benchmark review`
- commit 3 if needed: `docs(f17): record feedback loop handoff`

Rollback plan:
Revert correction UI/API additions; previous feedback buttons remain.

Next-agent handoff note:
After F17 and QA pass, reassess red/yellow/green gate before exposing Thomas/Lee dogfood.

---

## F18 - Recipe Library Internal-Only Policy

Status: deferred
Branch: feat/f18-recipes-internal-only
PR target: rebuild/validated-leads-loop
Estimated model fit: GPT-5.3 Spark / GPT-5.4 Mini
Max intended scope: 1 small feature, preferably <= 5 touched files unless justified.

Goal:
Keep recipe library internal-only until search quality gates are yellow or green.

Why this matters to the northstar:
Recipes are valuable only after outputs are validated; otherwise they preserve false confidence.

User story:
As Matt, I need recipe history available for internal evaluation only after the core loop is trustworthy.

Anti-goals:
- Do not reintroduce recipes to primary navigation.
- Do not expand recipe editing.
- Do not build recipe sharing.

Implementation boundaries:
Files likely touched: route gating/navigation docs if revived.
Files not to touch: search validation core.
No opportunistic refactors.

Acceptance criteria:
- No primary operator path exposes recipe library while gate is red.
- Any internal access is clearly marked internal/Matt-only.

Verification:
Browser-testable:
- route: `/`
- steps: confirm recipe library is absent from primary nav.
- required screenshots: home/primary nav.

Atomic commit plan:
- commit 1: `chore(ui): keep recipes internal-only`
- commit 2: `docs(f18): record deferred recipe policy`
- commit 3 if needed: n/a.

Rollback plan:
Revert route/nav policy change.

Next-agent handoff note:
Do not move to ready until the gate is yellow or green.

---

## F19 - Batch Workspace Internal-Only Policy

Status: deferred
Branch: feat/f19-batch-internal-only
PR target: rebuild/validated-leads-loop
Estimated model fit: GPT-5.3 Spark / GPT-5.4 Mini
Max intended scope: 1 small feature, preferably <= 5 touched files unless justified.

Goal:
Keep batch workspace out of the operator path until single-query quality is reliable.

Why this matters to the northstar:
Scaling bad data multiplies harm; batch should not return before validated single-query output works.

User story:
As Matt, I need batch to remain unavailable to operators while the product is red.

Anti-goals:
- Do not add CSV upload improvements.
- Do not add scheduling.
- Do not improve batch UI polish.

Implementation boundaries:
Files likely touched: route gating/navigation docs if revived.
Files not to touch: core validation sequence.
No opportunistic refactors.

Acceptance criteria:
- Batch workspace is absent from primary navigation.
- Any remaining route is internal-only or explicitly deferred.

Verification:
Browser-testable:
- route: `/`
- steps: confirm batch is absent from primary nav.
- required screenshots: home/primary nav.

Atomic commit plan:
- commit 1: `chore(ui): keep batch workspace internal-only`
- commit 2: `docs(f19): record deferred batch policy`
- commit 3 if needed: n/a.

Rollback plan:
Revert route/nav policy change.

Next-agent handoff note:
Do not move to ready until single-query benchmark precision is reliable.

---

## F20 - Friday Review Export Internal-Only Policy

Status: deferred
Branch: feat/f20-friday-review-internal-only
PR target: rebuild/validated-leads-loop
Estimated model fit: GPT-5.3 Spark / GPT-5.4 Mini
Max intended scope: 1 small feature, preferably <= 5 touched files unless justified.

Goal:
Keep Friday review export out of the red-gate operator product.

Why this matters to the northstar:
Review packets are ceremony around recipes; they do not fix natural-language query -> validated leads -> export.

User story:
As Matt, I need weekly review artifacts only after outputs are worth reviewing.

Anti-goals:
- Do not improve Friday export formatting.
- Do not add weekly automation.
- Do not add new scoreboard cards.

Implementation boundaries:
Files likely touched: recipe library internals only if revived.
Files not to touch: primary search UI.
No opportunistic refactors.

Acceptance criteria:
- Friday export is not visible in primary operator navigation or red-gate flows.
- If retained internally, it is labeled internal evaluation only.

Verification:
Browser-testable:
- route: primary search route.
- steps: confirm no Friday review export control in primary operator path.
- required screenshots: primary search/results.

Atomic commit plan:
- commit 1: `chore(ui): keep friday review export internal-only`
- commit 2: `docs(f20): record deferred friday review policy`
- commit 3 if needed: n/a.

Rollback plan:
Revert route/nav policy change.

Next-agent handoff note:
Do not move to ready until recipe quality has evidence.

---

## F21 - Scoreboards Internal-Only Policy

Status: deferred
Branch: feat/f21-scoreboards-internal-only
PR target: rebuild/validated-leads-loop
Estimated model fit: GPT-5.3 Spark / GPT-5.4 Mini
Max intended scope: 1 small feature, preferably <= 5 touched files unless justified.

Goal:
Keep scoreboards internal-only until the underlying validation and feedback metrics are trustworthy.

Why this matters to the northstar:
Scoreboards around bad data create false progress.

User story:
As Matt, I need quality metrics after validation is real, not before.

Anti-goals:
- Do not add dashboard polish.
- Do not add new analytics surfaces.
- Do not show composite confidence as a success metric.

Implementation boundaries:
Files likely touched: recipe/scoreboard route gating if revived.
Files not to touch: scoring core.
No opportunistic refactors.

Acceptance criteria:
- Scoreboards are absent from primary operator path in red state.
- Any internal scoreboard uses validation-quality metrics after F12.

Verification:
Browser-testable:
- route: primary search route.
- steps: confirm scoreboards are not visible in operator path.
- required screenshots: primary route.

Atomic commit plan:
- commit 1: `chore(ui): keep scoreboards internal-only`
- commit 2: `docs(f21): record deferred scoreboard policy`
- commit 3 if needed: n/a.

Rollback plan:
Revert route/nav policy change.

Next-agent handoff note:
Do not move to ready before F12 metrics exist.

---

## F22 - Operator Minutes Internal Capture

Status: deferred
Branch: feat/f22-operator-minutes-internal
PR target: rebuild/validated-leads-loop
Estimated model fit: GPT-5.3 Spark / GPT-5.4 Mini
Max intended scope: 1 small feature, preferably <= 5 touched files unless justified.

Goal:
Keep operator minutes as a low-ceremony internal KPI capture rather than primary UI ceremony.

Why this matters to the northstar:
Minutes per usable lead is the headline KPI, but it should not distract from search quality or export.

User story:
As Matt, I need to measure operator time after usable outputs exist.

Anti-goals:
- Do not remove the KPI from strategy docs.
- Do not add timers to the red-state primary flow.
- Do not require per-user accounts.

Implementation boundaries:
Files likely touched: closeout form or internal route if revived.
Files not to touch: lead validation core.
No opportunistic refactors.

Acceptance criteria:
- No operator-minutes ceremony appears before validated results/export.
- Internal capture can be restored after green/yellow gate without changing core search.

Verification:
Browser-testable:
- route: primary search/results.
- steps: confirm minutes UI is absent or low-ceremony after export only.
- required screenshots: primary result/export state.

Atomic commit plan:
- commit 1: `chore(ui): keep operator minutes out of primary search`
- commit 2: `docs(f22): record deferred operator-minutes policy`
- commit 3 if needed: n/a.

Rollback plan:
Revert UI placement change.

Next-agent handoff note:
Do not move to ready until F16 export and F17 corrections are stable.

---

## F23 - Sandbox Reset Internal-Only Policy

Status: deferred
Branch: feat/f23-sandbox-reset-internal
PR target: rebuild/validated-leads-loop
Estimated model fit: GPT-5.3 Spark / GPT-5.4 Mini
Max intended scope: 1 small feature, preferably <= 5 touched files unless justified.

Goal:
Keep sandbox reset out of primary operator UI and protect any reset endpoint behind the backend boundary.

Why this matters to the northstar:
Public or prominent reset controls weaken quota trust and expose implementation machinery.

User story:
As Matt, I need reset mechanics available only internally while operators focus on validated lead output.

Anti-goals:
- Do not remove all quota accounting.
- Do not add customer-facing quota management.
- Do not expose backend endpoint names.

Implementation boundaries:
Files likely touched: Scout UI and backend boundary only if revived.
Files not to touch: search validation core.
No opportunistic refactors.

Acceptance criteria:
- Reset control is absent from primary operator path.
- Direct reset endpoint is protected by F02 boundary.
- Any internal reset path is labeled internal.

Verification:
Browser-testable:
- route: primary search route.
- steps: confirm reset control is absent; direct reset API requires boundary.
- required screenshots: primary search quota area and API rejection evidence in QA report.

Atomic commit plan:
- commit 1: `chore(ui): keep sandbox reset internal-only`
- commit 2: `docs(f23): record deferred sandbox reset policy`
- commit 3 if needed: n/a.

Rollback plan:
Revert reset UI/gating change.

Next-agent handoff note:
Do not move to ready while gate is red except as a security follow-up to F02.
