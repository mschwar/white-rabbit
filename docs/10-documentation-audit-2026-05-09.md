# 10 - Documentation Audit 2026-05-09

**Status:** Historical Remediation Report.
**Created:** 2026-05-09.
**Branch:** `feat/docs-hard-audit-remediation`.

**Post-reset note (2026-05-10):** This report is historical evidence for the May 9 documentation cleanup. The active execution authority has since moved to `docs/12-reset-gated-implementation-plan-2026-05-10.md` per ADR-014. Preserve the findings below, but do not use this report's older `docs/08` / `docs/09` authority model to select current reset work.

## Verdict

The documentation set contained multiple live-looking instructions from different product eras:

- Bootstrap sprint docs that still described Sprint 1 as current.
- BUILDOUT remediation docs that were completed on `main` before the validated-leads rebuild.
- User-facing guides that described recipes, batch, Friday review, sandbox reset, and Scout/Full as primary operator flows even though the product is red and those surfaces are hidden or deferred.
- QA and deployment reports that were useful historical evidence but easy to misread as current operational truth.

This remediation makes the authority model explicit and labels historical material so future agents can move without guessing which doc wins.

## Current Authority Model

Use this hierarchy when docs conflict:

1. `docs/03-decisions.md` for locked ADR history. New decisions append; old decisions do not get rewritten.
2. `docs/00-product-northstar.md` for current product truth, usable-lead definitions, red/yellow/green launch gate, and anti-drift rules.
3. `STATUS.md` for current branch, current state, next pointer, and latest handoff.
4. `docs/12-reset-gated-implementation-plan-2026-05-10.md` for reset feature sequencing, Prompt A/B/C copy, and reset gate rules.
5. `docs/08-agentic-buildout-plan.md` / `docs/09-rebuild-phase-gates.md` for historical F00-F23 and W0-W6 context only.
6. `docs/qa-rubric.md` for QA tiers, unless a rebuild gate specifies stricter checks.

Older roadmap, BUILDOUT, audit, QA, and meeting docs are historical evidence unless they explicitly say `Status: Active`.

## Document Classes

| Class | Status label | Treatment |
| --- | --- | --- |
| Current product truth | `Active` | Keep accurate on every relevant session. |
| Current reset execution | `Active` | Must point to the right next feature and gate. |
| Historical plans | `Superseded` | Keep evidence, add banner, link to active control docs. |
| Audit/QA/report evidence | `Historical Record` | Preserve findings and screenshots; do not use as current instructions. |
| Bootstrap/reference docs | `Archived Reference` | Keep for context; link to active docs for execution. |

## High-Risk Drift Found

| Area | Problem | Remediation |
| --- | --- | --- |
| `docs/04-roadmap.md` | Said "Sprint 1 - Scaffold (current)" after rebuild work had replaced sprint execution. | Marked as superseded and removed the active-current wording. |
| `docs/08-agentic-buildout-plan.md` | Header still pointed at F03 despite STATUS saying F04 was next. | Updated header to F04. |
| W1 gate | F04 was ready even though no W1 gate report existed. | Added W1 gate report using F01-F03 evidence and fresh verification commands. |
| `docs/USER_GUIDE.md` | Told operators to use Scout/Full, recipes, batch, Friday review, and reset. | Replaced with red-gate Matt-only guide. |
| README/testing/package READMEs | Mixed current setup with old product framing or scaffold defaults. | Rewritten to point at the rebuild authority model and current setup. |
| Historical QA/audits | Read like current truth if opened directly. | Added historical banners. |

## Remediation Checklist

- [x] Add ADR-006 for documentation authority and archival policy.
- [x] Create this audit report.
- [x] Reconcile active control docs and W1 gate state.
- [x] Rewrite user-facing setup and testing docs.
- [x] Replace or banner operator guide and package READMEs.
- [x] Mark legacy planning docs as superseded or historical.
- [x] Add historical banners to audit, QA, and meeting reports.
- [x] Run doc hygiene checks.
- [x] Run W1 gate verification commands before keeping F04 ready.

## Verification Results

- `git diff --check` and `git diff --cached --check` passed. Git reported expected Windows line-ending warnings only before staging.
- Stale-string hygiene check found one allowed hit in `docs/03-decisions.md`: the old unresolved-host phrase inside locked ADR-002 history. ADR-006 says old ADR entries are not rewritten.
- W1 verification passed:
  - `cd apps/web && npm test -- --run` - 25 tests passed.
  - `cd packages/core && uv run pytest tests/test_query_guardrails.py -q` - 9 tests passed.
  - `cd apps/api && $env:DATABASE_URL='postgresql://white_rabbit:white_rabbit_dev@localhost:5432/white_rabbit'; uv run pytest tests/test_api.py -q -k "guardrail or sandbox or scout or full or batch"` - 22 tests passed, 12 deselected.
- First API W1 run without an explicit `DATABASE_URL` hit local credential drift for the DB-backed sandbox tests. The documented local Docker database accepted `white_rabbit_dev`, and the rerun above passed. The W1 gate report records this so future agents use the same boundary.

## Ongoing Rule

If a future doc update changes product truth, branch workflow, gate criteria, or launch status, update the relevant active authority doc in the same commit. Do not let a chat handoff become the only source of truth.
