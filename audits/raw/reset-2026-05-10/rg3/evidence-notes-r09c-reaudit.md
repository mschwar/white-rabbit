# RG3 R09C Re-audit Evidence Notes

**Date:** 2026-05-11
**Branch:** `audit/reset-rg3-validation-semantics-r09c`
**Integration branch:** `rebuild/validated-leads-loop`
**Integration commit audited:** `df9e831`
**Decision:** `hold`

## State Proof

- `AGENTS.md`, `STATUS.md`, `docs/00-product-northstar.md`, `docs/12-reset-gated-implementation-plan-2026-05-10.md`, `docs/13-pipeline-orchestrator-contract-2026.md`, `DESIGN.md`, `docs/03-decisions.md`, and `audits/zero-trust-codebase-audit-2026-05-10.md` were read before auditing.
- `git status --short --branch` showed `rebuild/validated-leads-loop...origin/rebuild/validated-leads-loop` clean before branch creation.
- `git fetch origin --prune` refreshed remote refs.
- R07, R08, R09, R09A, R09B, and R09C feature refs are all ancestors of the audited integration commit.
- `docs/12-reset-gated-implementation-plan-2026-05-10.md` still marks RG3 as `in_progress / gate_hold`, RG4 as `blocked`, and R10-R15 as `blocked`.
- The prior RG3 report decision was `hold`; RG3 had not already advanced.

## Verification

- Required RG3/R09C core suite passed: `76 passed`.
- Required API suite passed: `45 passed`, with existing datetime deprecation warnings.
- `git diff --check` passed before audit report edits and again after final status/report updates.
- Local API started on `http://127.0.0.1:8017` with inherited `OPENAI_API_KEY`, `OPENAI_BASE_URL`, and `TAVILY_API_KEY` shell overrides unset so the API loaded its repo env normally.
- `curl -sS http://127.0.0.1:8017/health` returned `{"status":"ok"}`.

## Current Live Benchmark Evidence

Fresh live artifacts are under `audits/raw/reset-2026-05-10/rg3/live-r09c-reaudit/`.

The Scout live runner completed all six fixture cases and wrote per-case JSON/HTTP files plus `quality-summary.json`.

Current suite summary:

| Benchmark | HTTP | Categorized rows | Person rows | High trust | Contact-quality passes | Error/status |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
| Thomas Arizona K-12 | 200 | 10 | 0 | 0 | 0 | evaluated |
| Lee commodity buyers | 503 | 0 | 0 | 0 | 0 | `tavily_failed` |
| Healthcare IT Phoenix | 503 | 0 | 0 | 0 | 0 | `tavily_failed` |
| Finance CISOs New York | 503 | 0 | 0 | 0 | 0 | `tavily_failed` |
| Manufacturing ops Detroit | 503 | 0 | 0 | 0 | 0 | `tavily_failed` |
| B2C private phone guardrail | 422 | 0 | 0 | 0 | 0 | expected privacy refusal |

Current theme summary:

- `named_account`: 10 categorized rows, 0 person rows, 0 high-trust usable rows, 0 contact-quality passes, 0 contacts acquired.
- `broad_b2b`: 0 categorized rows because all four broad B2B cases failed at Tavily quota.
- `privacy_rejection`: correctly blocked, counted as expected privacy refusal.

The local API logs show Tavily API HTTP 432 plan-limit errors:

```text
Tavily API error: 432 - {"detail":{"error":"This request exceeds your plan's set usage limit. Please upgrade your plan or contact support@tavily.com"}}
```

This means RG3 cannot advance from current live evidence. From RG2 onward, the reset plan requires current live evidence; if services are unavailable, Prompt C must record `hold` with the blocker.

## Completed Live Case Details

The Thomas Arizona K-12 case did not crash and preserved all eight target-account obligations, but it produced no CRM-ready value:

- 56 raw vendor hits deduped to 50 sources.
- 9 extracted candidates became failed rows.
- 1 organization-only row was produced.
- 0 person rows, 0 high-trust rows, 0 review rows, 0 contact-quality passes.
- READY blockers were `source_inaccessible: 9` and `organization_only: 1`.
- Quality failures included `zero_usable_candidates`, `low_precision_rate`, `low_persona_match_rate`, `low_contact_quality_rate`, `low_source_support_rate`, `fake_emails_present`, and `high_noise_rate`.

No row with missing, unsupported, inaccessible, or conflicting contact evidence was labeled CRM-ready in the completed live case. That is safer than the May 10 audit baseline, but it is not enough operator value.

## R09C Replay Evidence

R09C replay artifacts remain useful as deterministic feature evidence, not as gate-advance evidence:

- `audits/raw/reset-2026-05-10/r09c/replay/deep-contact-evidence-pass.json`
- `audits/raw/reset-2026-05-10/r09c/replay/quality-summary.json`

Replay proves the new mechanics can:

- promote a review row to `high_trust_usable` only when direct person-contact evidence is present,
- keep a missing-contact row in `review`,
- downgrade stale/conflicting evidence to `failed`,
- avoid fake or unsupported emails.

Replay quality still failed the gate thresholds (`low_precision_rate`, `low_contact_quality_rate`) and cannot substitute for current live evidence.

## Gate Decision Rationale

Decision: `hold`.

Reasons:

- Current live broad B2B evidence is unavailable because the Tavily plan limit now returns 432/503 for four required cases.
- The one completed live case still produced 0 high-trust usable rows and 0 contact-quality passes.
- The gate requires at least one required live benchmark with nonzero high-trust usable output without unsupported contacts.
- The gate requires at least one required live benchmark with nonzero contact-quality passes, or a source-backed proof that public contact evidence is unavailable. The current run cannot prove that because the broad public-web search service was quota-blocked.
- RG4, refreshed mockups, R10-R12, R13-R15, export work, dogfood, and main sync remain blocked.

## Next Recommendation

Do not assign a downstream Prompt A feature.

Matt should first decide whether to:

- restore or upgrade Tavily/search quota and rerun the exact RG3 Prompt C live suite, or
- accept that RG3 still lacks public-web contact value and define another RG3 remediation/vendor-positioning slice.

Do not sync `main` from this audit branch.
