# Reset Gate Re-Audit - RG6 Post-Remediation

**Branch:** `audit/reset-rg6-post-remediation`
**Integration branch:** `main`
**Base checked:** `7054574 docs: advance rg6 remediation to prompt c`
**Date:** 2026-05-24
**Decision:** hold
**Current product gate:** red
**Prompt C result:** RG6 remains held/product-red after the merged lead-quality/contact-yield remediation. The re-audit did not unlock yellow, green, public SaaS, accounts, orgs, billing, or Thomas/Lee dogfood expansion.

## Evidence Used

- Assignment lock: `docs/reset-current-assignment.json` confirmed `current_prompt: Prompt C`, `current_feature_status: merged_to_mainline`, and `current_audit_branch: audit/reset-rg6-post-remediation`.
- Product northstar: `docs/00-product-northstar.md`.
- Reset plan: `docs/12-reset-gated-implementation-plan-2026-05-10.md`.
- Prior RG6 gate report: `audits/gates/reset-2026-05-10/rg6-dogfood-decision.md`.
- Prompt B remediation QA: `.gstack/qa-reports/qa-report-rg6-lead-quality-contact-yield-2026-05-24.md`.
- New sanitized production evidence: `audits/raw/reset-2026-05-10/rg6/post-remediation-2026-05-24/`.

## Commands Run

```bash
git fetch origin && git switch main && git pull --ff-only origin main && git log --oneline -5
cat docs/reset-current-assignment.json
git switch -c audit/reset-rg6-post-remediation
WR_EXTERNAL_ENV_FILE=/Users/mschwar/Documents/white-rabbit.pre-hygiene-backup.20260522-225154/apps/web/.env.local python3 audits/raw/reset-2026-05-10/rg6/post-remediation-2026-05-24/collect_post_remediation_web_evidence.py
cd packages/core && uv run python -m core.sampled_precision ../../audits/raw/reset-2026-05-10/rg6/post-remediation-2026-05-24/live-required-benchmark --write-json ../../audits/raw/reset-2026-05-10/rg6/post-remediation-2026-05-24/sampled-precision-required-suite.json
git diff --check
```

Notes:

- The original local backup checkout hung during `git fetch`/`git pull`; a fresh current-main clone was created at `/tmp/white-rabbit-current-main`. `git ls-remote origin refs/heads/main` showed `7054574`, and the fresh clone log starts with `7054574 docs: advance rg6 remediation to prompt c`, so this audit did not run on stale `73860b5`.
- The attempted direct required-suite live benchmark command was blocked by the tool approval layer with `BLOCKED: User denied. Do NOT retry.` It was not retried. See `audits/raw/reset-2026-05-10/rg6/post-remediation-2026-05-24/evidence-command-log.md`.
- No secret values are preserved in the committed evidence.

## Fresh Production Results

| Evidence slice | Result | Gate implication |
| --- | --- | --- |
| Fly API health/readiness | `/health` returned 200 and `/readiness` returned HTTP 200 with body status `ready`. | Production liveness/readiness improved versus the 2026-05-22 degraded result. This alone does not clear product quality. |
| Direct API boundary | Tokenless direct `/scout` returned 401. | Supports the northstar backend-boundary requirement. |
| Vercel auth | Shared-password login and authenticated home returned 200. | Supports internal operator boundary. |
| Privacy/B2C guardrail | Authenticated web `/api/scout` returned 422 for a private-person/consumer medical-debt contact query. | Supports the red criterion that privacy-sensitive queries must be blocked. |
| Web source-assisted proof | Authenticated web `/api/source-assisted-proof` returned 200 and reproduced the saved R09L source-assisted proof packet: 17 candidates, 10 `high_trust_usable`, 7 `manual_lookup`, zero unsupported CRM-ready contacts. | This clears the previous web 404 blocker and supports the April NM source-assisted workbook shape, but it is not the required Arizona/live benchmark quality proof. |
| Arizona K-12 production primary scout | Authenticated web `/api/scout` returned HTTP 429: `Sandbox query cap reached. Reset the sandbox before running more queries.` Usage showed 10/10 queries consumed, 704 rows remaining. | The required live Arizona K-12 evidence did not run successfully. This is a red/hold blocker; it cannot prove the 6-of-8 target-district yellow criterion or Thomas/Lee readiness. |
| Sampled precision from required benchmark outputs | `sampled-precision-required-suite.json` was generated, but the required live benchmark output directory had no fresh case outputs because the direct required-suite run was blocked before execution. Packet: `sampled_row_count=0`, persona/source/org/contact precision all `0.0`, green floor false. | Does not clear yellow or green sampled-precision criteria. |
| Timed no-assistance query-to-export run | Scripted primary query-to-export captured `operator_minutes=0.011`, but the scout returned 429, produced no `run_id`, no persisted readback, no close response, and a 0-row CSV. | Mechanical timer ran, but the required no-assistance query-to-export operator run is not valid evidence because no usable production run/export was produced. |

## Product Northstar Mapping

### Red criteria

| Criterion from `docs/00-product-northstar.md` | Post-remediation result | Evidence / note |
| --- | --- | --- |
| Any golden benchmark returns zero leads or crashes. | Not cleared. | The required fresh Arizona K-12 run returned HTTP 429 before producing leads; sampled required-suite output has zero sampled rows because fresh outputs were unavailable. |
| Any broad Scout/Full benchmark returns fewer than 50 categorized candidates after high-volume mode lands, or fewer than 10 before it lands, without a source-backed reason. | Not cleared. | No fresh broad required-suite production outputs were captured; the only fresh primary scout returned 429. |
| Source-assisted/manual-oracle benchmark cannot reproduce or improve the April New Mexico workbook structure. | Cleared for the web source-assisted proof route. | `/api/source-assisted-proof` now returned 200 with R09L proof: 17 rows, 10 ready-with-contact, 7 manual-lookup, zero unsupported CRM-ready contacts. |
| Backend lead-search endpoints are callable outside intended app boundary. | Supported as protected for the probed route. | Direct tokenless `/scout` returned 401. |
| B2C/privacy-sensitive queries are not explicitly blocked. | Supported as blocked for the probed route. | Web `/api/scout` returned 422 with a B2B/privacy-safe guardrail message. |
| Any sampled row contains a fake, guessed, unsupported, or mismatched email without failed/deduced label. | Not freshly proven across required outputs. | The source-assisted proof has zero unsupported CRM-ready rows, but the required benchmark sample has 0 rows and cannot prove absence in live output. |
| Export lacks validation context. | Not cleared by the fresh primary run. | The timed export artifact has 0 rows because the scout was capped at 429; it cannot prove validation-context preservation for live Arizona output. Prior R13/R09L artifacts still support export shape only for saved/replay paths. |
| Operator UI organizes, beautifies, or scales untrusted data before the single-query loop works. | Still a live-quality risk. | Local/mock browser QA remains insufficient; the fresh primary production query did not complete. |

Conclusion: red cannot be cleared. Readiness, route boundary, privacy blocking, and source-assisted web proof improved, but the required live Arizona K-12 run and required-suite sampled precision were not successful.

### Yellow criteria - Matt-only internal evaluation

| Requirement | Post-remediation result | Evidence / note |
| --- | --- | --- |
| Arizona K-12 VoIP benchmark returns at least 6 of 8 target districts with correct named decision maker or explicit `not_found`. | Not met. | Fresh Arizona K-12 returned HTTP 429 before producing rows. |
| April New Mexico school-district IT replay returns manual-oracle distribution as categorized rows with no unsupported ready contacts. | Met for the source-assisted proof route. | Web `/api/source-assisted-proof` returned the R09L packet with 10 verified-contact/ready rows and 7 manual-lookup rows. |
| Broad Scout/Full benchmarks return at least 50 categorized candidates where market supports it, with high-trust rows separated. | Not proven. | Required-suite live benchmark was blocked before execution; no broad fresh outputs. |
| At least 50% of sampled returned person rows are right persona and source-backed. | Not proven. | Sampled-precision packet has 0 rows. |
| Contact status uses verified/deduced/missing/failed/unsupported; no unsupported `Found` emails. | Not proven across fresh required outputs. | Source-assisted proof is clean, but required suite did not run. |
| Backend API boundary is protected or ingress-restricted. | Supported. | Direct tokenless scout returned 401. |
| Operator UI hides recipes, batch, Friday review, scoreboards, sandbox reset, and implementation-detail copy from primary navigation. | Not re-tested in this re-audit. | Prompt B browser QA covered local mocked flow only; this re-audit did not use local UI screenshots as product-quality clearance. |
| Export includes validation-by-field columns. | Not proven by the fresh primary run. | The 429 run produced only a 0-row scripted CSV; prior saved artifacts still support export shape, but they do not clear this live gate. |

Conclusion: yellow is not earned.

### Green criteria - Thomas/Lee operator dogfood

| Requirement | Post-remediation result | Evidence / note |
| --- | --- | --- |
| At least 70% sampled precision on right persona, organization, and source support across required benchmark suite. | Not met. | Required-suite sampled precision has 0 sampled rows and precision values of 0.0. |
| Source-assisted April New Mexico replay reproduces/improves manual oracle with lower operator burden and zero unsupported CRM-ready contacts. | Partially met, but not lower-burden proven. | Web source-assisted proof reproduces R09L and has zero unsupported CRM-ready contacts; no valid timed operator burden proof for that flow was captured. |
| Broad Thomas/Lee Scout-style prompts consistently return 50-500+ categorized candidates where supported, with 10+ high-trust/review-worthy person candidates. | Not proven. | Required-suite live benchmark did not run; Arizona primary scout returned 429. |
| At least 50% of usable rows have verified or explicitly deduced contacts. | Not proven. | Fresh primary run produced no usable rows. |
| Zero fake or unsupported emails in sampled output. | Not proven across required suite. | Sampled output has zero rows, not a valid pass. |
| Query-to-export can be completed in under 5 minutes without Matt explaining the UI. | Not met as product evidence. | Timer recorded 0.011 minutes, but the product returned 429 with no run ID, readback, close, or valid export rows. |
| Operator minutes per usable lead can be tracked without extra ceremony. | Not met. | No usable leads were produced, so minutes per usable lead cannot be computed. |
| Thomas can run the Arizona benchmark and one simple B2B query without re-researching most rows. | Not proven. | Arizona run was blocked by sandbox cap; no Thomas/Lee run evidence. |

Conclusion: green is not earned.

## Findings

1. **Hold - sandbox query cap blocks the required Arizona production evidence.** The stable web `/api/scout` path returned 429 before producing any Arizona K-12 rows.
2. **Hold - sampled precision still cannot clear RG6.** The deterministic packet was generated, but fresh required-suite outputs were unavailable, yielding 0 sampled rows.
3. **Hold - timed query-to-export evidence is invalid for gate clearance.** The timer ran, but the capped scout produced no run ID, readback, close call, or non-empty export.
4. **Pass - production readiness is now clean in the probed slice.** `/readiness` returned `ready`, improving over the prior degraded result.
5. **Pass - web source-assisted proof route is repaired.** Authenticated `/api/source-assisted-proof` returned 200 and reproduced the R09L packet.
6. **Pass - boundary and privacy guardrails remain supported.** Direct tokenless scout returned 401 and B2C/private-person targeting returned 422.

## Decision

Keep RG6 held and keep the product red.

Do not unlock:

- yellow/green launch gate,
- Thomas/Lee dogfood expansion beyond already documented exceptions,
- public SaaS,
- accounts,
- orgs,
- billing,
- recipe/batch/scoreboard expansion as a primary operator path.

## Recommended Next Action

Narrow red remediation only:

1. Explicitly reset or raise the production sandbox query cap through an approved operational path, then rerun the required Arizona K-12 primary scout and required-suite live benchmark.
2. Re-run sampled precision only after fresh required benchmark outputs exist.
3. Capture a valid timed no-assistance query-to-export run that returns a `run_id`, persists/readbacks rows, exports validation-bearing rows, and closes the run with operator minutes.
4. Re-open Prompt C only after those fresh live artifacts exist.
