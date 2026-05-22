# Reset Gate Review - RG6 Dogfood / Kill Decision

**Branch:** `audit/reset-rg6-fresh-evidence`
**Integration branch:** `main`
**Date:** 2026-05-22
**Decision:** hold
**Current product gate:** red
**Prompt C result:** accepted R15 red-hold/no-dogfood recommendation after confirming R15 merged to `main` at `6858047` (`docs: qa r15 dogfood decision packet (#31)`). Matt then authorized fresh RG6 evidence gathering on 2026-05-22; the fresh evidence confirms the red hold remains.

## Evidence Used

- Control docs: `AGENTS.md`, `STATUS.md`, `docs/reset-current-assignment.json`, `docs/00-product-northstar.md`, `docs/12-reset-gated-implementation-plan-2026-05-10.md`, `docs/13-pipeline-orchestrator-contract-2026.md`, and `docs/03-decisions.md`.
- RG5 input report: `audits/gates/reset-2026-05-10/rg5-export-persistence.md`.
- R15 raw evidence summary: `audits/raw/reset-2026-05-10/rg6/r15-evidence-summary.md`.
- R13 export evidence: `.gstack/qa-reports/csv/r13-sales-first-export-2026-05-12/primary-sales-first-export.csv` and `.gstack/qa-reports/csv/r13-sales-first-export-2026-05-12/browser-qa-summary.json`.
- R14 persistence/readback QA: `.gstack/qa-reports/qa-report-r14-persistence-quality-tieout-2026-05-12.md`.
- R14C deployment/operator smoke QA: `.gstack/qa-reports/qa-report-r14c-deployment-readiness-2026-05-19.md` and `.gstack/qa-reports/screenshots/r14c-prod-smoke/browser-qa-summary.json`.
- RG3/R09L source-assisted proof: `audits/gates/reset-2026-05-10/rg3-validation-semantics.md` and `audits/raw/reset-2026-05-10/r09l/live-source-assisted-proof.json`.
- RG4 operator UI gate report: `audits/gates/reset-2026-05-10/rg4-operator-ui.md`.
- Fresh production evidence addendum: `audits/raw/reset-2026-05-10/rg6/fresh-2026-05-22/fresh-evidence-summary.md` plus sanitized JSON artifacts in the same directory.

## Commands Run

```bash
git status --short --branch && git branch --show-current
date -u +%Y-%m-%dT%H:%M:%SZ
# inspected saved R13/R14C/R09L artifacts with Python during Prompt A evidence collection
# attempted fresh production probe of stable Vercel/Fly endpoints; blocked before execution by environment/user approval
git fetch origin && git status --short --branch && git branch --show-current && git merge-base --is-ancestor 6858047 origin/main && echo R15_HEAD_IS_ON_ORIGIN_MAIN && git show --stat --oneline --decorate -1 HEAD
# Prompt C counted northstar launch-gate bullets against this report and inspected R13 CSV counts; output saved to audits/raw/reset-2026-05-10/rg6/prompt-c-verification.txt
git diff --check
```

The original R15 production probe returned exactly: `BLOCKED: User denied. Do NOT retry.` No production probe artifact was created during R15, and Prompt C did not retry it.

Matt later authorized fresh RG6 evidence gathering on 2026-05-22. The fresh evidence run used a sanitized collection script and saved artifacts under `audits/raw/reset-2026-05-10/rg6/fresh-2026-05-22/`.

Prompt C confirmed R15 is merged to `main`: local `main` and `origin/main` both point at `6858047 docs: qa r15 dogfood decision packet (#31)`, and that commit contains the R15 QA report, screenshots, RG6 report, raw evidence summary, reset-plan update, assignment-lock update, and STATUS update.

## Live Results

Fresh remote live evidence was captured on 2026-05-22 after Matt explicitly authorized it.

| Evidence slice | Result | Dogfood implication |
| --- | --- | --- |
| Fly API health/readiness | `/health` returned 200; `/readiness` returned HTTP 200 with body status `degraded` | Production is reachable, but not fully ready. This does not clear yellow/green readiness. |
| Protected route boundary | Direct tokenless `/scout` and `/source-assisted-proof` returned 401 | Good boundary evidence; backend endpoints are not openly callable without the internal token. |
| Vercel auth | Anonymous `/` redirected to login; shared-password login and authenticated home returned 200 | Good operator boundary evidence for the stable production alias. |
| Privacy/B2C guardrail | Consumer/private-person query returned 422 with a privacy-safe B2B-only message | Red criterion for blocking privacy-sensitive queries is freshly supported. |
| Web source-assisted proof | Authenticated `POST /api/source-assisted-proof` returned 404 | Source-assisted proof is not exposed through the operator web path; April NM source-assisted value remains replay/API proof, not web production operator proof. |
| Fresh Arizona K-12 VoIP Scout | 13 categorized rows in 126.569s, estimated cost `$0.355318`; 6 `review`, 2 `organization_only`, 1 `not_found`, 4 `failed`, 0 `high_trust_usable`, 0 contact quality passes, 0 contacts acquired | Fails yellow Arizona K-12 criterion and does not support Thomas/Lee dogfood. |
| Production persistence/readback | Inline Scout `persistence_readback` claimed 13/13 persisted rows, but separate web `GET /api/runs/{run_id}/leads` returned 500 | Query-to-export/readback is not fully proven in production. |

Saved live/replay evidence remains useful but limited:

| Evidence slice | Result | Dogfood implication |
| --- | --- | --- |
| R09L source-assisted proof | 17 candidates, 10 `high_trust_usable`, 7 `manual_lookup`, zero unsupported CRM-ready rows | Proves the source-assisted workbook shape for the April New Mexico benchmark, but not fresh production query-to-export dogfood. |
| R13 export artifact | 51 exported rows; 5 `READY` / `usable_candidate=yes`, 46 non-usable rows | Proves export transparency and high-volume fixture handling, but shows too few immediately usable rows for Thomas/Lee dogfood. |
| R14 persistence/readback QA | API tests and targeted persistence/readback smoke passed | Proves persistence/readback contracts, but fresh production separate readback now returns 500. |
| R14C operator smoke | Local `next start` browser flow passed with mocked rows; CSV export downloaded | Proves mechanical UI/export flow; does not prove live API quality because API checks were skipped. |

## Screenshots And Artifacts

- R14C login gate screenshot: `.gstack/qa-reports/screenshots/r14c-prod-smoke/01-login-gate.png`.
- R14C results overview screenshot: `.gstack/qa-reports/screenshots/r14c-prod-smoke/03-results-overview.png`.
- R14C evidence drawer screenshot: `.gstack/qa-reports/screenshots/r14c-prod-smoke/04-evidence-drawer.png`.
- R14C export-ready screenshot: `.gstack/qa-reports/screenshots/r14c-prod-smoke/05-export-ready.png`.
- R13 CSV export artifact: `.gstack/qa-reports/csv/r13-sales-first-export-2026-05-12/primary-sales-first-export.csv`.
- R15 evidence summary: `audits/raw/reset-2026-05-10/rg6/r15-evidence-summary.md`.
- Fresh RG6 production evidence summary: `audits/raw/reset-2026-05-10/rg6/fresh-2026-05-22/fresh-evidence-summary.md`.

## Internal Correction Review

The reset has corrected several original red-gate defects:

- The source-assisted compiler path can reproduce the accepted April New Mexico workbook pattern in saved R09L proof.
- The operator UI no longer exposes Scout/Full implementation chrome in the primary path.
- The export is sales-first and carries validation context instead of flattening uncertain data into confident rows.
- API persistence/readback contracts exist for persisted runs and leads.
- Local production-like browser smoke proves login, protected workspace, results review, evidence drawer, and export mechanics with deterministic rows.

The remaining corrections are still dogfood-blocking:

- Fresh production endpoint proof is now captured, but it confirms `degraded` readiness rather than a clean pass.
- Fresh live query-to-export with DB readback is not cleared because separate web run-lead readback returned 500.
- Broad Thomas/Lee-style prompts are not proven to consistently return 50-500 categorized candidates.
- The R13 export artifact has only 5 usable/READY rows out of 51 total rows.
- Operator minutes per usable lead have not been measured from an unassisted Thomas/Lee run.
- The strongest data-quality proof is still the narrower April New Mexico source-assisted replay, not a current broad production dogfood run.

## Product Northstar Red / Yellow / Green Evaluation

### Red criteria

| Criterion from `docs/00-product-northstar.md` | R15 result | Evidence / note |
| --- | --- | --- |
| Any golden benchmark returns zero leads or crashes. | Still not fully cleared. | Fresh Arizona K-12 returned 13 rows and did not crash, but only one benchmark slice ran and it returned 0 high-trust usable rows. |
| Any broad Scout/Full benchmark returns fewer than 50 categorized candidates after high-volume mode lands, or fewer than 10 before it lands, without source-backed reason. | Not cleared. | Fresh Arizona named-account run returned 13 categorized rows; no broad 50+ production consistency proof exists. |
| Source-assisted/manual-oracle benchmark cannot reproduce or improve April New Mexico workbook structure. | Cleared for saved R09L proof only. | R09L reproduced 17 rows: 10 ready-with-contact and 7 manual-lookup rows. |
| Backend lead-search endpoints are callable outside intended app boundary. | Freshly supported as protected. | Direct tokenless production `/scout` and `/source-assisted-proof` returned 401. |
| B2C/privacy-sensitive queries are not explicitly blocked. | Freshly supported for one probe. | Production web `/api/scout` returned 422 for a consumer/private-person medical-debt contact query. |
| Sampled row contains fake, guessed, unsupported, or mismatched email without failed/deduced label. | No new violation found in saved artifacts; not enough for dogfood. | R09L reports zero unsupported CRM-ready rows; R13 export preserves contact statuses. |
| Export lacks validation context. | Cleared for saved R13/RG5 artifacts. | R13/RG5 show sales-first export with validation/run/source context. |
| Operator UI organizes, beautifies, or scales untrusted data before the single-query loop works. | Still a risk, not a new violation. | UI/export mechanics work with deterministic rows; live data quality remains unproven, so product stays red. |

Conclusion: red cannot be cleared. Fresh production proof now exists, but it confirms degraded readiness, Arizona benchmark quality/contact failure, web source-assisted proof 404, separate run-lead readback 500, missing broad live consistency, and missing unassisted operator-minute evidence. Prompt C accepts this red/hold finding because the report maps all 8 red criteria from `docs/00-product-northstar.md` and no fresh evidence was available to clear the unresolved rows.

### Yellow criteria - Matt-only internal evaluation

| Requirement | R15 result | Evidence / note |
| --- | --- | --- |
| Arizona K-12 VoIP benchmark returns at least 6 of 8 target districts with correct named decision maker or explicit `not_found`. | Not met. | Fresh Arizona K-12 run returned 13 categorized rows but 0 high-trust usable, 0 contact quality passes, and 0 contacts acquired. |
| April New Mexico school-district IT replay returns the manual-oracle distribution as categorized rows: verified-contact rows where public evidence supports them, manual-lookup rows where direct contact is missing, and no unsupported contact marked ready. | Proven in saved R09L, not fresh production. | R09L: 10 ready-with-contact, 7 manual-lookup, zero unsupported CRM-ready rows. |
| Broad Scout/Full benchmarks return at least 50 categorized candidates where market supports it, with high-trust rows separated from other tiers. | Not proven. | R13 fixture has 51 categorized rows, but broad live consistency is not proven. |
| At least 50% sampled returned person rows are right persona and source-backed. | Not proven. | R15 did not have fresh sampling evidence across the required suite. |
| Contact status uses verified/deduced/missing/failed/unsupported; no unsupported `Found` emails. | Partially proven. | R09L/R13 artifacts preserve statuses, but no fresh full suite sampling. |
| Backend API boundary is protected or ingress-restricted. | Freshly supported. | Direct tokenless production `/scout` and `/source-assisted-proof` returned 401. |
| Operator UI hides recipes, batch, Friday review, scoreboards, sandbox reset, and implementation-detail copy from primary navigation. | Mechanically supported. | RG4/R14B/R14C reports show primary path hides implementation chrome. |
| Export includes validation-by-field columns. | Proven for saved R13/RG5 artifacts. | R13/RG5 export preserves validation/source/status/run context. |

Conclusion: yellow is not earned. The product should not be marked Matt-only yellow evaluation because the fresh Arizona benchmark failed the usable/contact threshold, production readback returned 500, source-assisted proof is not exposed through the web path, and sampled precision/operator-minute evidence remain incomplete. Prompt C accepts this finding; no Matt-only yellow evaluation is unlocked.

### Green criteria - Thomas/Lee operator dogfood

| Requirement | R15 result | Evidence / note |
| --- | --- | --- |
| At least 70% sampled precision on right persona, organization, and source support across required benchmark suite. | Not proven. | No fresh benchmark-suite precision sample was captured. |
| Source-assisted April New Mexico replay reproduces/improves manual oracle with lower operator burden and zero unsupported CRM-ready contacts. | Partially proven. | R09L proves structure and zero unsupported CRM-ready contacts, but lower operator burden and production query-to-export are not measured. |
| Broad Thomas/Lee Scout-style prompts consistently return 50-500+ categorized candidates with 10+ high-trust or review-worthy person candidates where supported. | Not proven. | R13 artifact has 25 person_lead rows and 23 REVIEW rows but only 5 READY rows; consistency across live prompts is missing. |
| At least 50% of usable rows have verified or explicitly deduced contacts. | Not proven for current suite. | Only 5 usable rows exist in the R13 export artifact; no fresh contact-quality sample. |
| Zero fake or unsupported emails in sampled output. | Not freshly proven. | Saved R09L has zero unsupported CRM-ready rows, but no fresh RG6 sample. |
| Query-to-export can be completed in under 5 minutes without Matt explaining the UI. | Not proven. | R14C proves mechanical flow with automation/mocks, not an unassisted Thomas/Lee timed run. |
| Operator minutes per usable lead can be tracked without extra ceremony. | Not proven. | No operator-minute measurement artifact exists. |
| Thomas can run Arizona benchmark and one simple B2B query without re-researching most rows. | Not proven and contradicted by fresh Arizona output quality. | Fresh Arizona run returned 0 high-trust usable/contact rows, and no Thomas unassisted run evidence exists. |

Conclusion: green is not earned. Thomas/Lee dogfood must stay blocked except for the existing Matt-directed red-gate internal-use exception recorded elsewhere. Prompt C accepts this finding; no Thomas/Lee dogfood expansion is unlocked.

## Value Prop Verdict

White Rabbit v2 has made meaningful progress toward the intended internal-first validated-leads loop, but the current evidence supports only a continued red hold.

The product is safer and more inspectable than the May 10 failure state: R09L proves a source-assisted workbook pattern, R13 proves sales-first CSV output, R14 proves persistence/readback contracts, and R14C proves local operator-path mechanics. The fresh 2026-05-22 evidence captures production proof, but it does not improve the decision: production readiness is degraded, web source-assisted proof is missing, separate production readback fails, Arizona K-12 quality/contact yield is too low, broad Thomas/Lee prompt consistency is still unproven, sampled precision across the required suite is still missing, and operator minutes per usable lead are still unmeasured.

The dogfood/kill decision is therefore:

- Do not kill the project outright; the source-assisted/manual-concierge wedge remains promising.
- Do not mark yellow.
- Do not mark green.
- Keep the product red.
- Continue Matt/agent-only correction work and manual concierge fulfillment until fresh production evidence and unassisted operator runs satisfy the northstar criteria.

## Findings

1. **Hold - RG6 cannot advance after fresh live evidence.** The fresh 2026-05-22 production run confirms the product remains red: degraded readiness, Arizona K-12 0 usable/contact rows, web source-assisted proof 404, and separate readback 500.
2. **Hold - RG5 mechanics are real but insufficient for dogfood.** Export, persistence, and UI smoke evidence prove mechanics, not live lead quality.
3. **Hold - R13 export quality is transparent but not dogfood-ready.** Only 5 of 51 rows are `usable_candidate=yes` / `READY`.
4. **Pass - uncertain data is still visibly labeled.** REVIEW, ORG-ONLY, NOT FOUND, failed/contact statuses, source URLs, and validation notes remain visible in saved export evidence.
5. **Pass - source-assisted replay remains the strongest wedge.** R09L's 17-row proof shows a credible manual-concierge/source-assisted path.
6. **Fresh evidence correction - the denied production probe gap is resolved, but the result is still red.** Production proof now exists and supports continued remediation rather than yellow/green promotion.

## What Worked

- Saved R13 export artifact has 51 rows and sales-first headers.
- Saved R13 export preserves validation context and labels uncertain rows.
- R14 persistence/readback QA proves API contracts for persisted run/lead readback.
- R14C browser smoke proves the login-to-export operator path mechanically with deterministic rows.
- R09L source-assisted proof reproduces the April New Mexico workbook structure with zero unsupported CRM-ready rows.

## What Did Not Work

- Fresh production Vercel/Fly endpoint probing now ran, but readiness is degraded.
- Fresh production query/readback evidence now exists, but separate web DB readback returned 500.
- No fresh broad Thomas/Lee-style prompt benchmark suite was captured.
- No unassisted operator-minute run was captured.
- R15 could not prove yellow or green criteria from saved evidence alone.

## New Gaps Found

- Need remediation for the production web persisted-run readback 500.
- Need remediation or an intentional route decision for authenticated web `/api/source-assisted-proof` returning 404.
- Need readiness to return a non-degraded production status or explicitly document why `tavily` degraded is acceptable.
- Need a current benchmark-suite sample that includes Arizona K-12 VoIP, April New Mexico replay, and broad Thomas/Lee-style prompts after remediation.
- Need an operator-minute measurement for query-to-export and minutes per usable lead.
- Need a documented privacy-sensitive/B2C refusal check in the current production path.
- Need live broad prompt proof that high-volume categorized output is consistent, not just available in a saved fixture.

## Recommended Scope Change For Next Gate

Do not expand into public SaaS, accounts, billing, recipe library, batch, scoreboards, or external self-serve work.

Recommended next scope is a narrow red-hold remediation packet:

1. Fix or explicitly scope the production readback 500 for `GET /api/runs/{run_id}/leads` through the web proxy.
2. Decide whether source-assisted proof must be available in the authenticated web path; if yes, add/fix `/api/source-assisted-proof`.
3. Re-run the required benchmark suite with sanitized artifacts and sampled precision notes after the live blockers are fixed.
4. Capture one timed, unassisted Matt run before asking Thomas/Lee to dogfood.
5. Keep manual concierge fulfillment as the customer-facing path while product evidence remains red.

## Next Deployment Recommendation

Do not deploy or promote from this branch.

This branch is evidence/control-plane work. The stable operator-use deployment line remains `main`, and the stable production alias remains `https://white-rabbit-ten.vercel.app/`. Because fresh production proof confirms live blockers, no deployment promotion or dogfood expansion should be made from this evidence packet.

## Next Prompt A Assignment

None from this gate hold.

Prompt C accepts the R15 recommendation as the RG6 gate decision: `hold`, product gate `red`. Matt authorized fresh evidence gathering on 2026-05-22, and that evidence confirms the red hold remains. No downstream Prompt A assignment is valid from this branch. Public SaaS, accounts, orgs, billing, yellow/green promotion, and Thomas/Lee dogfood expansion remain blocked.

Any future Prompt A must be explicitly authorized by Matt as red remediation against the fresh live blockers, then followed by a later gate record that maps the new evidence line by line to `docs/00-product-northstar.md`.
