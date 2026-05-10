# 08 - Docs / Status / Decision Drift

**Verdict:** docs are better than before, but now contradict live reality.

## Accurate Docs

- `docs/00-product-northstar.md` is still the right product standard.
- ADR-003/005 correctly describe shared password plus internal web-to-API token.
- ADR-004 correctly freezes `/Users/mschwar/Documents/proxy-lead`; this audit read it only.
- `docs/09-rebuild-phase-gates.md` correctly states W5/W6 gate criteria.

## Drift

`STATUS.md` says W5 operator loop and export gate remains in motion and F15-F19 are merged. That is true mechanically, but the status surface underplays the most important fact: live operator benchmarks still produce 0 usable leads.

`docs/08-agentic-buildout-plan.md` says no additional ready feature is unlocked, but the feature table shows W6-adjacent and deferred-policy work already merged without a W5 or W6 gate report.

`docs/09-rebuild-phase-gates.md` requires W5 browser query-to-export and CSV inspection. No W5 gate report exists.

`docs/qa-rubric.md` lists expected CSV columns that differ from the northstar and current export. Lee's Gmail feedback wants CRM-facing columns first, then report/run/audit fields. Current export starts with generated/run metadata.

The northstar says "source URL alone is not evidence." Current validation is better than source URL alone, but still too close to single-source literal text matching. Live results prove the doc standard is not met.

## Required Doc Actions

- Update `STATUS.md` to say this audit keeps the product red and recommends a W5 hold.
- Add `docs/11-product-reset-plan-2026-05-10.md` as the active recommendation artifact.
- Do not append an ADR yet. Recommendations are not decisions until Matt accepts them.
- Do not update old audit claims as if they were false. Keep them historical, but make the current handoff point to this audit.
