# RG4 Raw Evidence Notes

Date: 2026-05-12
Branch: `audit/reset-rg4-operator-ui`
Integration base: `origin/rebuild/validated-leads-loop`

## State Proof

- `docs/12-reset-gated-implementation-plan-2026-05-10.md` marks RG4 as `in_progress` and R10-R12 as `merged_to_rebuild_branch`.
- `audits/gates/reset-2026-05-10/rg4-operator-ui.md` did not exist before this audit; existing gate reports stop at RG3.
- `git merge-base --is-ancestor` returned success for R10, R11, and R12 against `origin/rebuild/validated-leads-loop`.
- `git status --short --branch` showed the new audit branch tracking `origin/rebuild/validated-leads-loop` with only RG4 raw evidence untracked after audit artifact creation.

## Commands

Command output is saved under `audits/raw/reset-2026-05-10/rg4/commands/`.

- `git-status-short-branch.txt`
- `git-log-origin-rebuild.txt`
- `r10-merge-proof.txt`
- `r11-merge-proof.txt`
- `r12-merge-proof.txt`
- `existing-gate-reports.txt`
- `web-vitest.txt`
- `web-build.txt`
- `git-diff-check.txt`
- `web-next-start.txt`
- `curl-login.txt`
- `curl-root-before-auth.txt`
- `web-next-dev.txt`
- `browser-audit-dev.txt`

## Browser Evidence

The browser audit script is `audits/raw/reset-2026-05-10/rg4/evidence/browser-audit.mjs`.

Screenshots are saved under `audits/raw/reset-2026-05-10/rg4/screenshots/`:

- `01-primary-empty.png`
- `02-primary-results.png`
- `03-evidence-dossier.png`
- `04-mobile-results.png`
- `05-mobile-evidence-dossier.png`

Summary JSON: `audits/raw/reset-2026-05-10/rg4/evidence/browser-audit-summary.json`.

Key result: the primary operator UI exposes one target input and hides Scout/Full/quota/export chrome. `sourceContextVisible=false` is intentional after Matt clarified that source context should stay backend/internal and not become daily-operator UI.

## Gate-Relevant Interpretation

RG4 can advance after ADR-023 because the missing source-context input is an intentional product simplification, not a bug.

The evidence dossier and mobile review affordances render from a 51-row browser fixture. Export controls are not visible in the primary operator path and remain correctly blocked for RG5.

Residual risk: the 390px mobile run reports a small horizontal overflow (`scrollWidth=407`, `clientWidth=390`). The screenshot remains usable, so this was recorded as an RG5/RG6 follow-up risk rather than an RG4 hold condition.
