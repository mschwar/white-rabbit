# 2026-09-16: retire white-rabbit-rg6-remediation checkout + Developer worktrees

## What was true before cleanup

- Canonical checkout: `/Users/mschwar/Developer/white-rabbit` (dirty in-progress work on `fix/rg6-lead-quality-contact-yield` left untouched; stashed only for this archive branch cut).
- Satellite: `/Users/mschwar/Developer/white-rabbit-rg6-remediation` on `fix/rg6-source-quality-required-suite-remediation` at `ae0559d` (already ancestor of `origin/main`) with **uncommitted** core/search/coverage residue.
- Worktrees:
  - `worktrees/white-rabbit-rg6-source-quality` @ `01c0572` — local-only tip not on origin
  - `worktrees/white-rabbit-lee-reset-worktree` @ `47bc96a` — local-only tip not on origin

## What this PR preserves

1. Uncommitted remediation residue (6 core/test files) applied onto `origin/main`.
2. Audit packet from `01c0572`: `audits/raw/reset-2026-05-10/rg6/source-quality-remediation-2026-05-25/`.
3. Lee first-principles docs from `47bc96a`: `docs/first-principles-reset/`.
4. Tip branches also pushed for full commit reachability:
   - `fix/rg6-source-quality-required-suite-remediation` → `01c0572`
   - `codex/first-principles-lee-reset` → `47bc96a`

## Intentionally not merged from those tips

- `STATUS.md` / assignment JSON rewrites from the divergent tips (would fight current main / RG6R3 truth).
- No force-push; no hard reset of in-progress operator work.
