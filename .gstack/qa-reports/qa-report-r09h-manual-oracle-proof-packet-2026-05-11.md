# QA Report - R09H Manual-Oracle Proof Replay Gate Packet

**Date:** 2026-05-11
**Prompt:** Prompt B
**Branch:** `feat/reset-r09h-manual-oracle-proof-packet`
**Target merge branch:** `rebuild/validated-leads-loop` only
**Decision:** pass

## State Proof

- Read `AGENTS.md`, `STATUS.md`, `docs/00-product-northstar.md`, `docs/12-reset-gated-implementation-plan-2026-05-10.md`, latest ADR entries in `docs/03-decisions.md`, and `docs/13-pipeline-orchestrator-contract-2026.md`.
- `STATUS.md` and `docs/12-reset-gated-implementation-plan-2026-05-10.md` identify one QA candidate: `R09H - Manual-oracle proof replay gate packet` on `feat/reset-r09h-manual-oracle-proof-packet`.
- `git status --short --branch` reported `## feat/reset-r09h-manual-oracle-proof-packet...origin/feat/reset-r09h-manual-oracle-proof-packet`.
- `git branch -r --contains HEAD` reported `origin/feat/reset-r09h-manual-oracle-proof-packet`; `origin/rebuild/validated-leads-loop` did not yet contain R09H before merge.
- `git diff --name-status origin/rebuild/validated-leads-loop...HEAD` showed only R09H scope:
  - `STATUS.md`
  - `docs/12-reset-gated-implementation-plan-2026-05-10.md`
  - `packages/core/src/core/manual_oracle_proof_packet.py`
  - `packages/core/tests/test_manual_oracle_proof_packet.py`
  - `audits/raw/reset-2026-05-10/r09h/manual-oracle-proof-packet.json`
  - `audits/raw/reset-2026-05-10/r09h/manual-oracle-proof-packet.md`

## Verification

- `git diff --check` passed.
- `cd packages/core && uv run pytest tests/test_manual_oracle_proof_packet.py tests/test_research_workbook.py tests/test_source_assisted_compiler.py tests/test_manual_oracle.py tests/test_k12_source_map.py -q` passed: `18 passed`.
- `cd packages/core && uv run pytest tests/test_source_validation.py tests/test_contact_status.py -q` passed: `21 passed`.
- Non-UI artifact regeneration check passed: `build_manual_oracle_proof_packet(...).to_payload()` matched `audits/raw/reset-2026-05-10/r09h/manual-oracle-proof-packet.json`.

## Artifact Tie-Out

Inspected `audits/raw/reset-2026-05-10/r09h/manual-oracle-proof-packet.json` and `.md`.

- Packet pass: `true`.
- Manual-oracle observed rows: `17`.
- Verified-contact rows: `10`.
- Manual-lookup rows: `7`.
- Source-assisted compiler rows: `17`.
- Generic blocked source URLs: `0`.
- Workbook rows: `17`.
- `READY_WITH_CONTACT`: `10`.
- `MANUAL_LOOKUP`: `7`.
- Unsupported CRM-ready rows: `0`.
- Manual-lookup CRM-ready rows: `0`.
- Missing source rows: `0`.
- Missing next-action rows: `0`.
- Private contact values redacted: `true`.
- Credentials present: `true`.
- API health status recorded in the packet: `000`.
- Fresh live benchmark run: `false`.
- Latest saved live high-trust usable rows: `0`.
- Latest saved live contact-quality passes: `0`.
- Prompt C handoff keeps `RG4`, refreshed mockups, `R10-R12`, export work, dogfood, and main promotion blocked.

## Northstar Drift Check

R09H aligns with `docs/00-product-northstar.md` because it verifies the source-assisted April New Mexico workbook pattern without weakening the strict usable-lead definition. The proof packet keeps missing-contact rows in `MANUAL_LOOKUP`, requires source and next-action support, preserves zero unsupported CRM-ready rows, and does not claim that stale live evidence advances RG3.

## Scope Check

R09H is non-UI. No browser QA or screenshots were required. The branch did not implement RG4, refreshed mockups, R10-R12, product API changes, persistence, production export surfaces, dogfood packet work, Prompt C gate audit work, or any `main` sync. Because R09H is the last same-gate feature, the correct next step after merge is Prompt C for RG3 from `rebuild/validated-leads-loop`, not unlocking RG4.
