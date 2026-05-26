# 14 - Narrow Arizona Source Strategy Remediation Plan (RG6)

**Status:** RG6R3 completed by Prompt B on 2026-05-25. RG6R4 is implemented on `fix/rg6r4-required-suite-contact-precision` and waiting for Prompt B QA; use `STATUS.md`, `docs/reset-current-assignment.json`, and `docs/12-reset-gated-implementation-plan-2026-05-10.md` for the active RG6R4 lock.
**Created:** 2026-05-25
**Current gate:** RG6 - Dogfood / Kill Decision (held product-red)
**Scope:** Strictly limited source-planning + claim-grounding improvements for the Arizona K-12 named-account benchmark.
**Goal:** Move Arizona K-12 from "2 READY but not 6-of-8 proven" + sub-70% sampled precision toward the Yellow gate criteria in `docs/00-product-northstar.md` using only the existing reusable kernel.

## One-Sentence Mission

Improve the source planner and extraction grounding so that the existing Arizona K-12 query (the 8 districts + tech/IT decision-maker titles) reliably produces source-backed person rows or explicit not-found/manual rows for at least 6 of 8 districts, while lifting sampled persona / organization / source precision on the required suite.

This is not a full pipeline rewrite. It is a targeted remediation on the parts that the 2026-05-24 post-remediation artifacts proved are the current bottleneck.

## Diagnosis

The 2026-05-24 `thomas-arizona-k12` production run plus `sampled-precision-required-suite.json` showed:

- All 8 named accounts received explicit categories.
- Only 2 high-trust usable rows had contact evidence.
- Multiple districts fell back to weak sources instead of the best official staff/technology pages on known domains.
- Extraction and validation correctly marked many persona fields unsupported when fetched pages did not contain supporting evidence.
- Sampled precision remained below Yellow/Green floor: persona `0.158`, organization `0.421`, source `0.447`.

The reusable core already produces the right northstar-shaped output when it receives strong cited sources. The gap is upstream source targeting and claim citation strength for these 8 accounts.

## Strict Scope

Allowed changes only:

- `packages/core/src/core/query_planner.py`.
- `packages/core/src/core/k12_source_map.py` plus Arizona source-map data.
- Minimal extraction/claim logic needed for Arizona persona/title/org citation grounding.
- Tests and fixtures in `packages/core/tests/`.
- One new live run artifact plus precision packet after the change.

Forbidden:

- Main orchestrator flow, UI, API routes, export columns, auth, batch, recipes, scoreboards, sandbox, or web components.
- Public features or dogfood surfaces.
- Large `orchestrator.py` refactors.
- Changes outside `packages/core/`, except Prompt B evidence/control-doc updates.

## Reusable Primitives

- `ARIZONA_K12_TARGET_ACCOUNTS` and `_ARIZONA_K12_ACCOUNT_DOMAINS` in `query_planner.py`.
- `K12SourceFamily`, `K12DistrictTarget`, `ROSTER_FIRST_FAMILIES`, priority ordering, and the `nm_k12_source_map.json` pattern.
- `lead_quality_policy.py`.
- `models.py` candidate/lead validation records.
- Existing Arizona fixtures and `test_arizona_k12_benchmark.py`.
- `sampled_precision.py`.
- `research_workbook.py` / export helpers.

## Slice

**Slice name:** RG6R3 - Arizona official-domain source targeting + citation enforcement

Success criteria for Prompt B:

1. `cd packages/core && PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 uv run pytest tests/test_arizona_k12_benchmark.py -q --tb=line` passes with assertions that the planner emits high-priority official sources for the 8 districts.
2. A fresh production-style run of the exact Arizona K-12 query produces an artifact set under `audits/raw/reset-2026-05-10/rg6/rg6r3-arizona-source-remediation/` or equivalent showing at least 6 of 8 districts represented with either a source-backed person row or explicit blocker row, and measurable sampled precision improvement.
3. The new `timed-query-to-export.csv` plus JSON records show stronger evidence snippets and fewer unsupported persona fields on rows with good sources.
4. Full core tests pass.
5. Prompt B records a short QA report.
6. After merge to `main`, Prompt B updates `docs/reset-current-assignment.json` and `STATUS.md` so remaining narrow slices return to normal two-prompt A/B rhythm.

## For the Prompt A agent

1. Start on clean `main`. Create `fix/rg6r3-arizona-source-targeting`.
2. Read this plan, `docs/00-product-northstar.md`, the 2026-05-24 Arizona artifacts, `query_planner.py`, and `k12_source_map.py`.
3. Extend Arizona handling with source-family entries for all 8 districts, high-value official URLs or reliable search patterns, and planner preference for official families before generic Tavily.
4. Harden citation requirements for promoted persona fields.
5. Add or update Arizona/source-map tests.
6. Run the full core suite.
7. Commit and push the branch. Do not merge.

Required Prompt A commands:

```bash
git checkout main && git pull origin main
git checkout -b fix/rg6r3-arizona-source-targeting
cd packages/core
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 uv run pytest tests/test_arizona_k12_benchmark.py tests/test_k12_source_map.py -q --tb=line
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 uv run pytest tests -q
git add -A
git commit -m "fix: improve Arizona K-12 official-domain source targeting and citation grounding (RG6R3)"
git push origin fix/rg6r3-arizona-source-targeting
```

## For the Prompt B agent

1. Check out the feature branch and rebase on latest main if needed.
2. Re-run:

```bash
cd packages/core && PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 uv run pytest tests -q
```

3. Execute a fresh live Arizona K-12 run using the same query as the 2026-05-24 artifact and save full output, precision packet, and timed export under a new dated `audits/raw/.../rg6/` directory.
4. Sample the new precision packet, focusing on Arizona rows plus the overall required suite, and record whether persona/org/source numbers improved.
5. Verify the 6-of-8 coverage claim by inspecting the new export/JSON.
6. Write a short QA report.
7. Merge to `main` only after the criteria pass.
8. Update `docs/reset-current-assignment.json` and `STATUS.md` so the project is back in normal two-prompt A/B rhythm for any remaining narrow Arizona/precision slices under the same RG6 red-remediation authorization.

## Return To Two-Prompt Loop

After Prompt B completes, future work on this narrow remediation line uses:

```text
Prompt A: implement the single ready narrow feature in docs/reset-current-assignment.json
Prompt B: QA, merge, capture evidence, then assign the next narrow feature if one remains
```

No additional Prompt C is required until Matt decides the narrow remediation tranche is complete and wants a gate-level RG6 decision.
