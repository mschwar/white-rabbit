# 09 - Rebuild Phase Gates

**Status:** Active gated implementation plan for the validated-leads rebuild.
**Created:** 2026-05-09.
**Integration branch:** `rebuild/validated-leads-loop`.
**Companion docs:** `docs/00-product-northstar.md`, `docs/08-agentic-buildout-plan.md`, `docs/qa-rubric.md`.

This document groups the feature cards in `docs/08-agentic-buildout-plan.md` into implementation waves. The two-prompt feature loop still runs one feature branch at a time, but each wave ends with an explicit gate review before the next wave is unlocked.

## Why Gates Exist

The zero-trust audit showed that White Rabbit can accumulate product surface while the core data-quality loop remains broken. Gates prevent that failure mode.

The rebuild must not move from one major milestone to the next until the current milestone has evidence that it reduced false confidence and improved:

```text
natural-language query
  -> high-quality validated leads
  -> transparent field-level evidence
  -> ranked results
  -> export
```

## Gate Mechanics

Every feature still follows the branch workflow in `docs/08-agentic-buildout-plan.md`:

- One feature branch.
- One PR.
- PR target is always `rebuild/validated-leads-loop`.
- Never target or merge to `main`.
- UI features require browser QA and screenshots.
- Non-UI features require explicit command/fixture verification.

At the end of each wave, create a docs-only gate review branch:

```text
feat/gate-wN-short-name
```

The gate review branch must:

- Run the gate's required verification.
- Write a gate review report under `.gstack/qa-reports/`.
- Update `docs/08-agentic-buildout-plan.md` statuses only for the next wave being unlocked.
- Update `STATUS.md` with the gate decision.
- Commit and push to `rebuild/validated-leads-loop`.

Gate decisions:

- `advance`: criteria met; unlock the first ready feature of the next wave.
- `hold`: criteria not met; keep next wave blocked and add remediation notes.
- `revise`: criteria exposed wrong sequencing; update docs before more implementation.
- `rollback`: a merged feature caused material regression; revert or repair before advancing.

Matt owns the final product gate decision. Agents prepare evidence; they do not declare yellow/green dogfood readiness by vibes.

## Wave Overview

| Wave | Name | Feature range | Gate result | Unlocks |
| --- | --- | --- | --- | --- |
| W0 | Control plane | F00 + phase-gate doc | docs complete | W1 |
| W1 | Red-state containment | F01-F03 | advance on 2026-05-09 (`.gstack/qa-reports/gate-w1-red-state-containment.md`) | W2 |
| W2 | Search planning and candidate contract | F04-F06 | typed bounded search contract | W3 |
| W3 | Validation and ranking engine | F07-F09 | false-confidence controls | W4 |
| W4 | Benchmarks and quality reporting | F10-F12 | quality gates measurable and passing threshold | W5 |
| W5 | Operator loop and export | F13-F16 | query-to-export browser path works with validation | W6 |
| W6 | Feedback and dogfood decision | F17 + deferred policy review | yellow/green decision evidence | post-rebuild roadmap |

No wave may unlock only because all previous features are merged. It unlocks when the gate review passes.

## W0 - Control Plane

Features:

- F00 - Northstar + buildout docs + branch protocol.
- This phase-gate document.

Goal:
Make the rebuild independently navigable by small agents without conversation context.

Gate criteria:

- `docs/00-product-northstar.md` exists and defines usable lead, failed lead, validation-by-field, export requirements, launch gates, and bad-data policy.
- `docs/08-agentic-buildout-plan.md` exists and has feature cards, statuses, branch workflow, two prompts, and reflection checklist.
- `docs/09-rebuild-phase-gates.md` exists and maps features into gated waves.
- `AGENTS.md` and `STATUS.md` reference the rebuild protocol.
- `main` is untouched.

Required verification:

```bash
git diff --check
rg -n "rebuild/validated-leads-loop|F01|Northstar reflection|Wave Overview|Gate criteria" docs AGENTS.md STATUS.md
```

Gate report:

- `.gstack/qa-reports/gate-w0-control-plane.md`

Decision standard:

- Advance if docs are present, branch protocol is clear, and the next agent can find F01 without chat context.

Current decision:

- Advance to W1 after this document merges.

## W1 - Red-State Containment

Features:

- F01 - Hide premature operator surfaces from primary navigation.
- F02 - Backend API boundary.
- F03 - Guardrail rewrite for B2B scope and privacy blocking.

Goal:
Stop visible and structural trust leaks while the product is still red.

Why this wave comes first:

- The UI must stop organizing untrusted data.
- The backend must stop accepting direct anonymous lead-search calls.
- Unsafe and off-scope queries must be blocked before search spends money or emits misleading empty results.

Gate criteria:

- Primary operator navigation exposes only the single lead-search path or its current Scout equivalent.
- Recipe library, batch workspace, Friday export, scoreboards, sandbox reset, and implementation-detail copy are absent from primary operator navigation.
- Direct unauthenticated calls to `POST /scout`, `POST /full`, `POST /batch`, and `POST /sandbox/reset` fail with 401 or 403, or documented ingress restriction proves equivalent protection.
- `GET /health` remains public.
- Guardrails allow normal B2B sales language and block consumer/privacy-sensitive targeting.
- Blocked queries never call the search/extraction path.
- Browser QA screenshots exist for UI containment.
- API/core test output exists for boundary and guardrails.

Required verification:

```bash
cd apps/web && npm test -- --run
cd apps/api && uv run pytest tests/test_api.py -q -k "guardrail or sandbox or scout or full or batch"
cd packages/core && uv run pytest tests/test_query_guardrails.py -q
```

Browser QA:

- Login/home after F01.
- Primary lead-search/Scout page after F01.
- Direct API rejection evidence for F02 captured in the QA report.

Gate report:

- `.gstack/qa-reports/gate-w1-red-state-containment.md`

Decision standard:

- Advance to W2 only if the product is still red but contained: no premature operator surfaces, no public lead endpoints, and privacy-sensitive queries refused.

Hold examples:

- Backend direct calls still work without boundary.
- B2C/privacy targeting returns `200` instead of refusal.
- UI still links operators to recipes, batch, Friday review, or reset.

## W2 - Search Planning And Candidate Contract

Features:

- F04 - Query compiler / planner.
- F05 - Candidate model separation.
- F06 - Field-level validation schema.

Goal:
Define the shape of trustworthy search output before implementing validators or UI around it.

Why this wave comes before validation:

- Thomas's realistic prompt must be decomposed before Tavily receives bounded searches.
- Candidate categories must exist before validation can decide whether a row is a usable lead, organization-only, not-found, or failed.
- Field-level validation schema must exist before source/contact validators can populate it.

Gate criteria:

- Thomas's full Arizona prompt compiles into a plan with eight named accounts and no vendor query over 400 characters.
- Simple B2B queries still compile into bounded searches without losing persona, geography, or vertical.
- Candidate categories exist: `person_lead`, `organization_only`, `not_found`, `failed`.
- Company-as-person and role-as-person fixtures fail validation or become non-person categories.
- Field validation records exist for name, title, organization, email, phone, and source.
- Every validation record has status, source URL or source absence, checked_at, and notes.
- API serialization remains backward-compatible enough for existing routes/tests to pass or has a documented compatibility shim.

Required verification:

```bash
cd packages/core && uv run pytest tests/test_query_planner.py tests/test_models.py -q
cd apps/api && uv run pytest tests/test_api.py -q -k "scout or full"
```

Gate report:

- `.gstack/qa-reports/gate-w2-search-contract.md`

Decision standard:

- Advance to W3 only if the search plan and candidate contract can represent the audit failures without lying.

Hold examples:

- Planner still sends long prompts directly to Tavily.
- Companies can still appear in a person-name field.
- Field validation schema cannot express unsupported or failed evidence.

## W3 - Validation And Ranking Engine

Features:

- F07 - Source validator.
- F08 - Contact status model.
- F09 - Ranking gate based on evidence.

Goal:
Populate the candidate contract with source/contact evidence and compute usability gates from evidence, not LLM confidence.

Why this wave matters:

This is the core trust rebuild. It is where White Rabbit stops treating a source URL as proof and starts downgrading bad, missing, inaccessible, or unsupported data.

Gate criteria:

- Source validator records resolved URL, HTTP/access status, checked_at, and field support.
- 200-supported, 200-unsupported, 403, 404, and blocked/999-like sources are covered by tests.
- Contact statuses exist and are enforced: `verified_found`, `deduced_with_pattern_evidence`, `missing`, `failed`, `unsupported`.
- Unsupported guessed contacts cannot be emitted as found.
- Ranking/gate is server-computed from persona fit, field evidence, contact usability, and source support.
- Wrong persona, unsupported title/org, failed contact, organization-only, and not-found rows cannot pass as usable person leads.
- Tests include fake email, wrong persona, organization-only, not-found, verified lead, and inaccessible source cases.

Required verification:

```bash
cd packages/core && uv run pytest tests/test_source_validation.py tests/test_contact_status.py tests/test_scoring.py tests/test_orchestrator.py -q
```

Gate report:

- `.gstack/qa-reports/gate-w3-validation-engine.md`

Decision standard:

- Advance to W4 only if false-confidence rows are rejected or downgraded in deterministic tests.

Hold examples:

- Source URL presence still counts as evidence without content support.
- Deduced email lacks domain-pattern evidence.
- LLM can still mark `gate_passed=true` for bad rows.

## W4 - Benchmarks And Quality Reporting

Features:

- F10 - Golden Arizona K-12 VoIP benchmark harness.
- F11 - Required benchmark suite.
- F12 - Per-run quality report.

Goal:
Make quality measurable and enforceable before building the operator-facing UI.

Why this wave gates UI:

The audit failure was not lack of UI polish; it was absence of proof. Do not build a better-looking lead surface until benchmarks can distinguish usable leads from bad data.

Gate criteria:

- Arizona fixture includes Mesa, Chandler, Peoria, Gilbert, Deer Valley, Paradise Valley, Dysart, and Maricopa.
- Arizona fixture preserves Thomas workbook annotations without treating GPT output as ground truth.
- Required suite covers simple B2B queries, vertical generalization, guardrails, and privacy rejection.
- Per-run quality report computes precision, persona match, contact quality, source support, fake-email count, unsupported-email count, not-found count, and failed count.
- Offline benchmark suite runs in CI without live API keys.
- Optional live benchmark run has a saved report when API keys are available.
- Gate thresholds for yellow candidacy are evaluated and recorded, even if the decision is "hold."

Required verification:

```bash
cd packages/core && uv run pytest tests/test_arizona_k12_benchmark.py tests/test_benchmark_suite.py tests/test_quality_report.py -q
```

Optional live verification:

```bash
cd packages/core && RUN_LIVE=1 uv run pytest tests/test_orchestrator_integration.py -q
```

Minimum threshold to advance to W5:

- Offline benchmarks pass.
- Arizona benchmark produces no fake or unsupported emails in accepted rows.
- Quality report can identify zero-usable or high-noise runs as failures.
- If live keys are available, live Arizona run must not crash on query length.

Gate report:

- `.gstack/qa-reports/gate-w4-benchmarks-quality.md`

Decision standard:

- Advance to W5 only when the team can measure whether UI-visible rows are trustworthy.

Hold examples:

- Benchmark harness exists but does not fail bad rows.
- Quality report cannot count fake/unsupported emails.
- Arizona prompt still crashes or loses named-account constraints.

## W5 - Operator Loop And Export

Features:

- F13 - Single search-bar UI.
- F14 - Results table with validation buckets.
- F15 - Evidence drawer or dossier.
- F16 - Export rebuild with validation columns.

Goal:
Build the visible operator loop only after the underlying validated-lead contract and benchmarks exist.

Why this wave comes late:

UI can amplify trust or amplify harm. W5 is allowed only after data-quality gates exist.

Gate criteria:

- Authenticated first screen is a single natural-language lead-search input.
- Scout/Full, recipes, batch, endpoint names, and reset mechanics are absent from the primary operator path.
- Results table separates usable, noisy/failed, organization-only, and not-found rows.
- Field/contact/source validation badges are visible.
- Evidence drawer shows which source supports which field.
- Export includes all required validation columns from `docs/00-product-northstar.md`.
- Default export does not flatten uncertain rows into clean CRM-ready rows.
- Browser QA confirms query-to-export path.
- CSV inspection confirms headers, row counts, validation notes, statuses, and no placeholders.

Required verification:

```bash
cd apps/web && npm test -- --run
cd apps/web && npm run build
```

Browser QA:

- Login.
- Single search empty state.
- Search submit/loading state.
- Results with all candidate categories.
- Evidence drawer for usable and failed/noisy rows.
- Export ready state.
- CSV content inspection.

Required screenshots:

- `.gstack/qa-reports/screenshots/gate-w5-01-search-empty.png`
- `.gstack/qa-reports/screenshots/gate-w5-02-results-buckets.png`
- `.gstack/qa-reports/screenshots/gate-w5-03-evidence-drawer.png`
- `.gstack/qa-reports/screenshots/gate-w5-04-export-ready.png`

Gate report:

- `.gstack/qa-reports/gate-w5-operator-loop-export.md`

Decision standard:

- Advance to W6 only if a browser user can complete query -> validated results -> evidence review -> export without seeing premature surfaces or unsupported confidence.

Hold examples:

- Export omits validation status/evidence.
- Evidence drawer shows URLs but not field support.
- Results table hides failed/noisy rows instead of flagging them.

## W6 - Feedback And Dogfood Decision

Features:

- F17 - Thomas/Lee correction feedback loop.
- Deferred/internal-only policy review for F18-F23.

Goal:
Turn operator corrections into durable evaluation data and decide whether the product can move from red to yellow or green.

Why this wave is last:

Feedback is only useful when it attaches to validated fields and benchmark definitions. Before then, it becomes generic sentiment about bad cards.

Gate criteria:

- Corrections can be recorded by field and reason.
- Correction record includes run ID, query, candidate ID/category, field, previous value, corrected value if supplied, operator label, and notes.
- Corrections can be exported or transformed into benchmark fixture updates or a review queue.
- F18-F23 remain hidden/internal unless Matt explicitly moves one to ready after reviewing evidence.
- Red/yellow/green launch gate in `docs/00-product-northstar.md` is evaluated with current benchmark and browser QA evidence.
- STATUS records whether the product remains red, moves to yellow for Matt-only evaluation, or moves to green for Thomas/Lee dogfood.

Required verification:

```bash
cd apps/api && uv run pytest tests/test_api.py -q -k "feedback or correction"
cd apps/web && npm test -- --run
```

Browser QA:

- Submit a field-level correction.
- Verify stored correction or fixture/review-queue output.
- Confirm no deferred surfaces reappeared in primary navigation.

Gate report:

- `.gstack/qa-reports/gate-w6-feedback-dogfood-decision.md`

Decision standard:

- Yellow only if Matt can run internal evaluation with benchmark evidence and validation export.
- Green only if the northstar green gate is met: strong sampled precision, usable contact quality, zero fake emails, query-to-export under 5 minutes, and no Matt explanation required.

Hold examples:

- Corrections do not attach to fields.
- Deferred surfaces return before quality gates are met.
- Gate evidence is anecdotal rather than benchmark/browser/report backed.

## How To Unlock The Next Wave

When a wave gate advances:

1. Update `docs/08-agentic-buildout-plan.md` so the first feature in the next wave has `Status: ready`.
2. Keep later features in that wave blocked unless they are truly independent and safe to parallelize.
3. Update the feature table in `docs/08-agentic-buildout-plan.md`.
4. Update `STATUS.md` with the gate report path, decision, next feature pointer, and current red/yellow/green gate.
5. Commit with a message like `docs(gate): advance to wave 2 search contract`.

When a wave gate holds:

1. Keep the next wave blocked.
2. Add remediation bullets to the gate report.
3. Add or adjust feature cards only if the current sequence cannot satisfy the gate.
4. Update `STATUS.md` with the hold decision and next remediation pointer.
5. Do not continue into downstream UI or export work to "make progress."

## Gate Report Template

Use `.gstack/qa-reports/qa-template-agentic-buildout.md` for feature QA. For wave gates, include this minimum structure:

```markdown
# Gate Review - WN Name

**Branch:**
**Integration branch:** rebuild/validated-leads-loop
**Date:**
**Decision:** advance / hold / revise / rollback
**Current product gate:** red / yellow / green

## Features Included

| Feature | Status | Commit/PR | QA report |
| --- | --- | --- | --- |

## Required Verification

| Check | Result | Evidence |
| --- | --- | --- |

## Northstar Assessment

- Query:
- Validated leads:
- Field-level evidence:
- Ranking:
- Export:
- False-confidence risk:

## Decision Rationale

## Next Pointer

## Follow-Ups
```

## Agent Rules

- Do not unlock a downstream wave inside a normal feature branch.
- Do not mark the product yellow or green without a gate review report.
- Do not build UI for data contracts that do not exist yet.
- Do not create broad "wave implementation" branches. Waves are gates; features remain atomic.
- If a gate fails, prefer fixing the smallest upstream feature over adding downstream compensating UI.
