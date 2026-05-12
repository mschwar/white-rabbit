# Control Plane Frontier Audit 2026-05-10

**Status:** Completed control-plane hardening pass.
**Branch:** `rebuild/validated-leads-loop`
**Scope:** Documentation authority, reset queue, Prompt A/B/C kickoff workflow, historical QA logs, and repo-state blockers.
**Product code changed:** No.

## Verdict

The Prompt A stop was a real orchestration bug, not an agent misunderstanding. The reset queue had been corrected in `STATUS.md` and `docs/12-reset-gated-implementation-plan-2026-05-10.md`, but several higher-level authority surfaces still told agents to use historical docs or historical QA conclusions. A top-level orchestrator should have caught that because the control plane had multiple plausible "current" sources.

The repo is now hardened so the next agent should resolve the same answer from every active surface:

- current integration branch: `rebuild/validated-leads-loop`
- current reset gate: `RG1 - Operator Benchmark Harness`
- next Prompt A feature: `R02 - Golden benchmark replay harness`
- active queue and prompt authority: `docs/12-reset-gated-implementation-plan-2026-05-10.md`
- product state: red, internal-only, high-volume transparent tiering reset in progress

## Findings Fixed

| ID | Severity | Problem | Fix |
| --- | --- | --- | --- |
| CP-01 | P0 | `AGENTS.md` still ranked `docs/08` and `docs/09` as active rebuild control docs, so fresh agents could ignore the reset queue. | Updated read order, project rules, rebuild protocol, anti-drift rules, and session protocol to route reset work through `docs/12`. |
| CP-02 | P0 | `docs/08-agentic-buildout-plan.md` looked active and said R02 was not unlocked. | Reclassified it as historical F00-F23 context and pointed the next feature to R02 in `docs/12`. |
| CP-03 | P0 | `docs/12` contained duplicate Prompt A/B/C blocks: old hard-coded blocks plus the newer reusable prompts. | Removed the stale prompt blocks and made the reusable Prompt A/B/C section the only active prompt authority. |
| CP-04 | P1 | `docs/09-rebuild-phase-gates.md` still described the May 10 reset as beginning at R00. | Updated the reset banner to the current state: RG0 advanced, RG1 in progress, R01 merged, R02 ready. |
| CP-05 | P1 | ADR-006 still listed `docs/08` and `docs/09` as active execution authorities. | Added ADR-014, which locks `docs/12` as the active reset execution authority while the May 10 reset is active. |
| CP-06 | P1 | Archived reference docs still had live-looking banners pointing agents to `docs/08` and `docs/09`. | Updated banners in `docs/00`, `docs/01`, `docs/04`, `docs/05`, `docs/06`, `docs/07`, and `docs/10` to point to `docs/12` or mark their authority as historical. |
| CP-07 | P1 | Historical QA logs still contained stale next-step language saying downstream reset work stayed blocked after R01 or that R01 was still blocked after RG0. | Added supersession notes to the relevant tracked QA reports while preserving their original findings. |
| CP-08 | P2 | Local `.obsidian/` metadata dirtied the integration branch and triggered Prompt A's dirty-worktree stop rule. | Already fixed in `ab90c32` by ignoring `.obsidian/` and recording the correction in STATUS. |

## Kickoff Workflow Check

Prompt A is now intentionally agnostic. It must not be given a hard-coded feature unless Matt explicitly overrides the queue. The next Prompt A run should:

1. Read the active docs.
2. Run `git status --short --branch`.
3. Resolve exactly one ready feature from STATUS plus `docs/12`.
4. Select `R02 - Golden benchmark replay harness`.
5. Create or resume `feat/reset-r02-benchmark-replay-harness`.
6. Implement only R02 and push the feature branch without merging.

Prompt B remains similarly agnostic: it resolves the single pushed branch awaiting QA, writes the QA report, and merges only into `rebuild/validated-leads-loop`. Prompt C runs only after all features in the current gate are merged and is the only prompt that can advance the next gate.

## Remaining Guardrails

- Do not execute reset work from `docs/08` or `docs/09`.
- Do not unlock R03 until R02 passes Prompt B.
- Do not unlock RG2 until RG1 passes Prompt C.
- Do not sync `main` unless Matt explicitly asks after reviewing the gate decision.
- Do not treat historical QA reports as current next-step authority when they conflict with STATUS and `docs/12`.

## Verification

The hardening pass should be considered valid only if these checks pass:

```bash
git diff --check
rg -n "None unlocked|Do not start R02|Do not unlock the next feature|Prompt A - Build Next Reset Feature|Prompt B - QA And Merge Reset Feature|Prompt C - Gate Evaluation And Audit|Current execution plan.*docs/08|Current rebuild execution.*docs/08|active rebuild feature queue|active rebuild wave|docs/08-agentic-buildout-plan.md.*active|docs/09-rebuild-phase-gates.md.*active" AGENTS.md STATUS.md docs .gstack
rg -n "docs/12-reset-gated-implementation-plan-2026-05-10.md|R02 - Golden benchmark replay harness|Reusable Copy-Paste Prompt A|Copy-Paste Prompt Authority|\\.obsidian/" AGENTS.md STATUS.md docs .gstack .gitignore
```

The first grep may still show historical prose where the string is intentionally preserved as evidence. Those remaining hits must be in locked ADR history, superseded historical docs, or this audit report, not in active execution instructions.
