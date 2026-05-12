# R09C Prompt A Evidence Note - Deep Multi-Source Evidence And Tier Calibration

**Feature:** R09C - Deep multi-source evidence acquisition and tier calibration  
**Branch:** `feat/reset-r09c-deep-multisource-evidence-tier-calibration`  
**Date:** 2026-05-11  
**Scope:** Core-only evidence acquisition, cross-source verification, tier reason quality, and benchmark observability. No UI, export, persistence, dogfood, RG4, Prompt C, or `main` promotion work.

## What Changed

- Extended the R09B contact pass from one targeted query to a bounded multi-hop pass over page-type-aware public-web paths: exact person/org, site-scoped source-domain query, staff/directory/team pages, board/agenda/PDF paths, contact/email-format pages, and news/press paths.
- Added lightweight page-type detection for staff directory, leadership/team, department, contact, board/agenda PDF, news/press, about, and generic sources.
- Added cross-source support/conflict tracking. The pass records field corroborations, source page types, and stale-role conflict terms such as former/previously/retired/resigned/no longer.
- Tightened contact-quality counting so failed/non-person rows with a contact-looking artifact do not inflate contact-quality passes.
- Improved review reasons when the deep pass searched useful page types but still did not find a direct email or explicit domain-pattern source.
- Extended funnel reporting with contact-evidence search counts, contacts acquired, field corroborations, conflict signals, and review-to-high-trust movement. The live benchmark quality summary now aggregates contact acquisition and high-trust yield by benchmark theme.

## Replay Evidence

Saved artifacts:

- `audits/raw/reset-2026-05-10/r09c/replay/deep-contact-evidence-pass.json`
- `audits/raw/reset-2026-05-10/r09c/replay/quality-summary.json`

Deterministic replay scenario:

- `Jordan Lee` started as a review row with supported identity and missing contact. The first contact query missed, the site-scoped staff-directory hop found a direct person email, and the row became `high_trust_usable`.
- `Taylor Chen` stayed `review`: the pass found a leadership/team corroboration path but no direct person email or explicit domain-pattern source. The primary reason now says exactly that.
- `Morgan Ray` found a direct email on a leadership archive, but the source said the role was former. Cross-source conflict detection downgraded the row to `failed`; it did not become READY.

Replay metrics:

- `contact_evidence_candidates_searched`: 3
- `contact_evidence_searches`: 7
- `contact_evidence_contacts_acquired`: 2
- `contact_evidence_review_to_high_trust`: 1
- `contact_evidence_conflicting_signals`: 1
- `contact_quality_passes`: 1
- `tier_distribution`: 1 `high_trust_usable`, 1 `review`, 1 `failed`

## Precision Boundary

The `high_trust_usable` definition did not change. A row still requires supported name, title, organization, source, and usable contact status plus threshold scores. Direct emails and deduced emails still require source-backed public-web evidence; missing, unsupported, inaccessible, conflicting, or guessed contacts remain non-CRM-ready.

## Verification Run By Prompt A

- `cd packages/core && uv run pytest tests/test_query_planner.py tests/test_search.py tests/test_coverage.py tests/test_source_validation.py tests/test_contact_status.py tests/test_scoring.py tests/test_orchestrator.py tests/test_live_benchmark_runner.py tests/test_quality_report.py -q` - `76 passed`
- `cd apps/api && WR_API_INTERNAL_TOKEN=test-internal-token uv run pytest tests -q` - `45 passed`, existing datetime deprecation warnings
- `cd packages/core && uv run pytest -m integration -q` - `6 skipped`, no live integration credentials used
- `git diff --check` - passed

## Prompt B Handoff

QA `feat/reset-r09c-deep-multisource-evidence-tier-calibration`. Verify the branch contains only R09C scope, rerun the required R09C core/API suites plus `git diff --check`, inspect the R09C replay artifacts, confirm missing/unsupported/inaccessible/conflicting/guessed contacts do not become CRM-ready, confirm contact-quality counts do not include failed/non-person rows, confirm theme-level benchmark summaries expose contact acquisition success and high-trust yield, and confirm no RG4/UI/export/persistence/dogfood/main-sync scope landed. If QA passes, merge only to `rebuild/validated-leads-loop`; keep RG3 in `in_progress / gate_hold` and hand off a future RG3 Prompt C only after confirming R09B and R09C are both merged.
