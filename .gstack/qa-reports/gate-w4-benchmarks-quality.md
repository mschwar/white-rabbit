# Gate Review - W4 Benchmarks And Quality Reporting

**Branch:** rebuild/validated-leads-loop
**Integration branch:** rebuild/validated-leads-loop
**Date:** 2026-05-10
**Prepared recommendation:** advance
**Orchestrator decision:** advance
**Orchestrator acceptance:** Codex orchestrator / 2026-05-10
**Current product gate:** red
**QA rubric:** `docs/qa-rubric.md`; this non-UI wave gate uses benchmark/report verification before W5 browser/export tiers.

## Features Included

| Feature | Status | Commit/PR | QA report |
| --- | --- | --- | --- |
| F10 - Golden Arizona K-12 VoIP benchmark harness | merged_to_rebuild_branch | `f1c9eaf` merge / `168d0ad` feature | `.gstack/qa-reports/qa-report-f10-arizona-k12-benchmark-2026-05-10.md` |
| F11 - Required benchmark suite | merged_to_rebuild_branch | `3198d39` QA merge / `c7a730b` feature | `.gstack/qa-reports/qa-report-f11-required-benchmark-suite-2026-05-09.md` |
| F12 - Per-run quality report | merged_to_rebuild_branch | `1ecca8e` merge / `0892804` feature | `.gstack/qa-reports/qa-report-f12-run-quality-report-2026-05-10.md` |
| W4 gate remediation - quality threshold evaluation | accepted in this review | current gate commit | this report |

## Required Verification

| Check | Result | Evidence |
| --- | --- | --- |
| W4 required command | PASS | `cd packages/core && uv run pytest tests/test_arizona_k12_benchmark.py tests/test_benchmark_suite.py tests/test_quality_report.py -q` -> `11 passed, 1 skipped in 0.52s` |
| F12 remediation command | PASS | `cd packages/core && uv run pytest tests/test_quality_report.py -q` -> `5 passed in 0.12s` |
| Broader core regression | PASS with env isolation | `cd packages/core && $env:OPENAI_API_KEY=$null; uv run pytest -q` -> `94 passed, 6 skipped in 1.05s` |
| Broader core regression without env isolation | Known env-sensitive failure | `OPENAI_API_KEY` is set in this shell, so `test_scout_raises_on_missing_openai_key` reaches OpenAI instead of the missing-key branch. Recorded as pre-existing environment risk, not W4 blocker. |
| Optional live Arizona benchmark | SKIPPED | `RUN_LIVE=False`; `TAVILY_API_KEY` absent. Live verification is optional unless live keys are available. |

## Gate Criteria Assessment

| Criterion | Result | Evidence |
| --- | --- | --- |
| Arizona fixture includes Mesa, Chandler, Peoria, Gilbert, Deer Valley, Paradise Valley, Dysart, and Maricopa | PASS | `packages/core/tests/fixtures/arizona_k12_voip.json` lists all eight target districts. |
| Thomas workbook annotations are preserved without using GPT output as ground truth | PASS | Fixture source says annotations are preserved and GPT output is not ground truth; tests assert workbook annotations are present. |
| Required suite covers simple B2B, vertical/generalization, guardrail accept, and privacy rejection | PASS | `packages/core/tests/fixtures/benchmark_suite.json` includes six accepted B2B/vertical cases and one privacy rejection case. |
| Quality report computes precision, persona match, contact quality, source support, fake-email count, unsupported-email count, not-found count, and failed count | PASS | `tests/test_quality_report.py` asserts all required counts/rates and serialization fields. |
| Offline benchmark suite runs without live keys | PASS | W4 required command passes with one intentional live-key skip. |
| Yellow-candidacy thresholds are evaluated and recorded | PASS | `QualityReport` now serializes `quality_gate_passed`, `quality_gate_failures`, `quality_gate_thresholds`, `high_noise_count`, and `high_noise_rate`. |
| Zero-usable or high-noise runs are identified as failures | PASS | Added tests for zero-usable and high-noise reports; both fail the quality gate explicitly. |

## Northstar Assessment

- Query: W4 proves Thomas-style named-account queries can be represented in offline benchmarks without long vendor-query crashes.
- Validated leads: Arizona fixture requires at least 6 of 8 target districts to resolve to either usable person rows or explicit non-usable outcomes.
- Field-level evidence: F12 reports count validation statuses per field and contact/source status.
- Ranking: W4 inherits the W3 evidence gate; no ranking changes were made in this gate review.
- Export: Not yet rebuilt. Product remains red until W5 implements validation-aware export.
- False-confidence risk: Reduced by benchmark thresholds and quality-gate failures for fake email, unsupported email, zero usable rows, and high-noise runs.

## Decision Rationale

Advance W4 to W5. The offline gate passes, the Arizona benchmark rejects fake or unsupported emails in accepted rows, and the F12 report now records explicit pass/fail threshold evaluation instead of only passive metrics.

F13 was already merged before this W4 gate acceptance. The process break came from stale feature-level handoff text that said W5 UI could begin after F12 QA, while `docs/09-rebuild-phase-gates.md` requires W4 orchestrator acceptance. This review updates the control docs so additional W5 work is unlocked only by W4 acceptance. No rollback is recommended because W4 now passes and F13 satisfies only the first W5 UI slice; F14-F16 remain subject to the W5 gate.

## Next Pointer

F14 - Results Table With Validation Buckets is ready on `feat/f14-validation-results-table`.

## Follow-Ups

- Keep product gate red; do not dogfood with Thomas or Lee.
- Do not start W6 or deferred F18-F23 work until W5 and W6 gates pass.
- Fix the environment-sensitive `test_scout_raises_on_missing_openai_key` in a later scoped task so the full core suite does not depend on local shell secrets.
