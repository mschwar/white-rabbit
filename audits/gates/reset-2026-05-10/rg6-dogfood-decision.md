# Reset Gate Review - RG6 Dogfood / Kill Decision

**Branch:** `feat/reset-r15-dogfood-decision-packet`
**Integration branch:** `main`
**Date:** 2026-05-22
**Decision:** hold
**Current product gate:** red

## Evidence Used

- Control docs: `AGENTS.md`, `STATUS.md`, `docs/reset-current-assignment.json`, `docs/00-product-northstar.md`, `docs/12-reset-gated-implementation-plan-2026-05-10.md`, `docs/13-pipeline-orchestrator-contract-2026.md`, and `docs/03-decisions.md`.
- RG5 input report: `audits/gates/reset-2026-05-10/rg5-export-persistence.md`.
- R15 raw evidence summary: `audits/raw/reset-2026-05-10/rg6/r15-evidence-summary.md`.
- R13 export evidence: `.gstack/qa-reports/csv/r13-sales-first-export-2026-05-12/primary-sales-first-export.csv` and `.gstack/qa-reports/csv/r13-sales-first-export-2026-05-12/browser-qa-summary.json`.
- R14 persistence/readback QA: `.gstack/qa-reports/qa-report-r14-persistence-quality-tieout-2026-05-12.md`.
- R14C deployment/operator smoke QA: `.gstack/qa-reports/qa-report-r14c-deployment-readiness-2026-05-19.md` and `.gstack/qa-reports/screenshots/r14c-prod-smoke/browser-qa-summary.json`.
- RG3/R09L source-assisted proof: `audits/gates/reset-2026-05-10/rg3-validation-semantics.md` and `audits/raw/reset-2026-05-10/r09l/live-source-assisted-proof.json`.
- RG4 operator UI gate report: `audits/gates/reset-2026-05-10/rg4-operator-ui.md`.

## Commands Run

```bash
git status --short --branch && git branch --show-current
date -u +%Y-%m-%dT%H:%M:%SZ
# inspected saved R13/R14C/R09L artifacts with Python during Prompt A evidence collection
# attempted fresh production probe of stable Vercel/Fly endpoints; blocked before execution by environment/user approval
git diff --check
```

The fresh production probe returned exactly: `BLOCKED: User denied. Do NOT retry.` No production probe artifact was created, and the denied command was not retried.

## Live Results

No fresh remote live result was captured for RG6 in this Prompt A session.

Saved live/replay evidence remains useful but limited:

| Evidence slice | Result | Dogfood implication |
| --- | --- | --- |
| R09L source-assisted proof | 17 candidates, 10 `high_trust_usable`, 7 `manual_lookup`, zero unsupported CRM-ready rows | Proves the source-assisted workbook shape for the April New Mexico benchmark, but not fresh production query-to-export dogfood. |
| R13 export artifact | 51 exported rows; 5 `READY` / `usable_candidate=yes`, 46 non-usable rows | Proves export transparency and high-volume fixture handling, but shows too few immediately usable rows for Thomas/Lee dogfood. |
| R14 persistence/readback QA | API tests and targeted persistence/readback smoke passed | Proves persistence/readback contracts, not live production DB readback from a fresh operator run. |
| R14C operator smoke | Local `next start` browser flow passed with mocked rows; CSV export downloaded | Proves mechanical UI/export flow; does not prove live API quality because API checks were skipped. |
| Fresh production endpoint proof | Missing; probe blocked before execution | Blocks any yellow/green claim that depends on current production behavior. |

## Screenshots And Artifacts

- R14C login gate screenshot: `.gstack/qa-reports/screenshots/r14c-prod-smoke/01-login-gate.png`.
- R14C results overview screenshot: `.gstack/qa-reports/screenshots/r14c-prod-smoke/03-results-overview.png`.
- R14C evidence drawer screenshot: `.gstack/qa-reports/screenshots/r14c-prod-smoke/04-evidence-drawer.png`.
- R14C export-ready screenshot: `.gstack/qa-reports/screenshots/r14c-prod-smoke/05-export-ready.png`.
- R13 CSV export artifact: `.gstack/qa-reports/csv/r13-sales-first-export-2026-05-12/primary-sales-first-export.csv`.
- R15 evidence summary: `audits/raw/reset-2026-05-10/rg6/r15-evidence-summary.md`.

## Internal Correction Review

The reset has corrected several original red-gate defects:

- The source-assisted compiler path can reproduce the accepted April New Mexico workbook pattern in saved R09L proof.
- The operator UI no longer exposes Scout/Full implementation chrome in the primary path.
- The export is sales-first and carries validation context instead of flattening uncertain data into confident rows.
- API persistence/readback contracts exist for persisted runs and leads.
- Local production-like browser smoke proves login, protected workspace, results review, evidence drawer, and export mechanics with deterministic rows.

The remaining corrections are still dogfood-blocking:

- Fresh production endpoint proof is missing.
- Fresh live query-to-export with DB readback is missing.
- Broad Thomas/Lee-style prompts are not proven to consistently return 50-500 categorized candidates.
- The R13 export artifact has only 5 usable/READY rows out of 51 total rows.
- Operator minutes per usable lead have not been measured from an unassisted Thomas/Lee run.
- The strongest data-quality proof is still the narrower April New Mexico source-assisted replay, not a current broad production dogfood run.

## Product Northstar Red / Yellow / Green Evaluation

### Red criteria

| Criterion from `docs/00-product-northstar.md` | R15 result | Evidence / note |
| --- | --- | --- |
| Any golden benchmark returns zero leads or crashes. | Not freshly re-proven in RG6. | No fresh full benchmark suite ran in this session; cannot use this to clear red. |
| Any broad Scout/Full benchmark returns fewer than 50 categorized candidates after high-volume mode lands, or fewer than 10 before it lands, without source-backed reason. | Not cleared. | Saved R13 fixture exports 51 rows, but broad Thomas/Lee-style live prompts were not freshly proven. |
| Source-assisted/manual-oracle benchmark cannot reproduce or improve April New Mexico workbook structure. | Cleared for saved R09L proof only. | R09L reproduced 17 rows: 10 ready-with-contact and 7 manual-lookup rows. |
| Backend lead-search endpoints are callable outside intended app boundary. | Not freshly re-proven for production. | R14/RG3 protected-route tests exist; fresh production endpoint probe was blocked. |
| B2C/privacy-sensitive queries are not explicitly blocked. | Not evaluated in R15. | No fresh privacy-sensitive query suite was run. |
| Sampled row contains fake, guessed, unsupported, or mismatched email without failed/deduced label. | No new violation found in saved artifacts; not enough for dogfood. | R09L reports zero unsupported CRM-ready rows; R13 export preserves contact statuses. |
| Export lacks validation context. | Cleared for saved R13/RG5 artifacts. | R13/RG5 show sales-first export with validation/run/source context. |
| Operator UI organizes/scales untrusted data before single-query loop works. | Still a risk, not a new violation. | UI/export mechanics work with deterministic rows; live data quality remains unproven, so product stays red. |

Conclusion: red cannot be cleared. At least production endpoint proof, broad live prompt consistency, privacy-sensitive blocking, and unassisted operator-minute evidence are missing.

### Yellow criteria - Matt-only internal evaluation

| Requirement | R15 result | Evidence / note |
| --- | --- | --- |
| Arizona K-12 VoIP benchmark returns at least 6 of 8 target districts with correct named decision maker or explicit `not_found`. | Not proven. | No fresh Arizona benchmark evidence was captured in RG6. |
| April New Mexico replay returns manual-oracle distribution with verified-contact rows, manual-lookup rows, and no unsupported contact marked ready. | Proven in saved R09L, not fresh production. | R09L: 10 ready-with-contact, 7 manual-lookup, zero unsupported CRM-ready rows. |
| Broad Scout/Full benchmarks return at least 50 categorized candidates where market supports it, with high-trust rows separated from other tiers. | Not proven. | R13 fixture has 51 categorized rows, but broad live consistency is not proven. |
| At least 50% sampled returned person rows are right persona and source-backed. | Not proven. | R15 did not have fresh sampling evidence across the required suite. |
| Contact status uses verified/deduced/missing/failed/unsupported; no unsupported `Found` emails. | Partially proven. | R09L/R13 artifacts preserve statuses, but no fresh full suite sampling. |
| Backend API boundary is protected or ingress-restricted. | Partially proven, not production-current. | Protected tests exist; fresh production probe blocked. |
| Operator UI hides recipes, batch, Friday review, scoreboards, sandbox reset, and implementation-detail copy from primary navigation. | Mechanically supported. | RG4/R14B/R14C reports show primary path hides implementation chrome. |
| Export includes validation-by-field columns. | Proven for saved R13/RG5 artifacts. | R13/RG5 export preserves validation/source/status/run context. |

Conclusion: yellow is not earned. The product should not be marked Matt-only yellow evaluation because benchmark coverage, production proof, and sampled precision evidence are incomplete.

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
| Thomas can run Arizona benchmark and one simple B2B query without re-researching most rows. | Not proven. | No Thomas unassisted run evidence exists. |

Conclusion: green is not earned. Thomas/Lee dogfood must stay blocked except for the existing Matt-directed red-gate internal-use exception recorded elsewhere.

## Value Prop Verdict

White Rabbit v2 has made meaningful progress toward the intended internal-first validated-leads loop, but the current evidence supports only a continued red hold.

The product is safer and more inspectable than the May 10 failure state: R09L proves a source-assisted workbook pattern, R13 proves sales-first CSV output, R14 proves persistence/readback contracts, and R14C proves local operator-path mechanics. However, R15 did not capture fresh production endpoint proof, fresh production query-to-export/DB readback, broad Thomas/Lee prompt consistency, sampled precision across the required suite, or operator minutes per usable lead.

The dogfood/kill decision is therefore:

- Do not kill the project outright; the source-assisted/manual-concierge wedge remains promising.
- Do not mark yellow.
- Do not mark green.
- Keep the product red.
- Continue Matt/agent-only correction work and manual concierge fulfillment until fresh production evidence and unassisted operator runs satisfy the northstar criteria.

## Findings

1. **Hold - RG6 cannot advance without fresh live evidence.** The reset plan requires current live evidence from RG2 onward; RG6 lacks fresh production endpoint and query-to-export proof.
2. **Hold - RG5 mechanics are real but insufficient for dogfood.** Export, persistence, and UI smoke evidence prove mechanics, not live lead quality.
3. **Hold - R13 export quality is transparent but not dogfood-ready.** Only 5 of 51 rows are `usable_candidate=yes` / `READY`.
4. **Pass - uncertain data is still visibly labeled.** REVIEW, ORG-ONLY, NOT FOUND, failed/contact statuses, source URLs, and validation notes remain visible in saved export evidence.
5. **Pass - source-assisted replay remains the strongest wedge.** R09L's 17-row proof shows a credible manual-concierge/source-assisted path.
6. **Caveat - denied production probing is an evidence gap, not a product pass or fail.** It prevents yellow/green claims and must be resolved in an approved environment.

## What Worked

- Saved R13 export artifact has 51 rows and sales-first headers.
- Saved R13 export preserves validation context and labels uncertain rows.
- R14 persistence/readback QA proves API contracts for persisted run/lead readback.
- R14C browser smoke proves the login-to-export operator path mechanically with deterministic rows.
- R09L source-assisted proof reproduces the April New Mexico workbook structure with zero unsupported CRM-ready rows.

## What Did Not Work

- Fresh production Vercel/Fly endpoint probing was blocked and could not be retried.
- No fresh production query-to-export/DB readback evidence was captured.
- No fresh broad Thomas/Lee-style prompt benchmark suite was captured.
- No unassisted operator-minute run was captured.
- R15 could not prove yellow or green criteria from saved evidence alone.

## New Gaps Found

- Need an approved, repeatable RG6 live-smoke environment that can safely hit `https://white-rabbit-ten.vercel.app/`, the Fly API health/readiness endpoints, protected query routes, export, and DB readback without leaking secrets.
- Need a current benchmark-suite sample that includes Arizona K-12 VoIP, April New Mexico replay, and broad Thomas/Lee-style prompts.
- Need an operator-minute measurement for query-to-export and minutes per usable lead.
- Need a documented privacy-sensitive/B2C refusal check in the current production path.
- Need live broad prompt proof that high-volume categorized output is consistent, not just available in a saved fixture.

## Recommended Scope Change For Next Gate

Do not expand into public SaaS, accounts, billing, recipe library, batch, scoreboards, or external self-serve work.

Recommended next scope is a narrow red-hold remediation packet:

1. Build or document an approved production smoke harness for endpoint health/readiness, protected login, query, CSV export, and DB readback.
2. Re-run the required benchmark suite with sanitized artifacts and sampled precision notes.
3. Capture one timed, unassisted Matt run before asking Thomas/Lee to dogfood.
4. Keep manual concierge fulfillment as the customer-facing path while product evidence remains red.

## Next Deployment Recommendation

Do not deploy or promote from this branch.

R15 is report/control-plane work. The stable operator-use deployment line remains `main`, and the stable production alias remains `https://white-rabbit-ten.vercel.app/`. Because production proof was blocked in this session, no deployment or dogfood expansion should be made from this evidence packet.

## Next Prompt A Assignment

None until Prompt B QA reviews this R15 packet and merges it to `main`.

Prompt B handoff:

```text
You are Prompt B for the White Rabbit reset queue.

Work in /Users/mschwar/Documents/white-rabbit. QA `feat/reset-r15-dogfood-decision-packet` against `main`.

First prove current state:
- fetch origin
- read AGENTS.md
- read STATUS.md
- read docs/reset-current-assignment.json
- read docs/00-product-northstar.md
- read docs/12-reset-gated-implementation-plan-2026-05-10.md
- read audits/gates/reset-2026-05-10/rg5-export-persistence.md
- read audits/gates/reset-2026-05-10/rg6-dogfood-decision.md
- run git status --short --branch

Before QA, confirm `docs/reset-current-assignment.json` names Prompt B/R15 on `feat/reset-r15-dogfood-decision-packet`. If it does not, stop without editing, committing, merging, or pushing.

Required QA:
- confirm R15 is docs/report-only and does not change product code;
- verify the packet evaluates every red/yellow/green criterion from `docs/00-product-northstar.md` line by line;
- verify it does not claim yellow, green, Thomas/Lee dogfood readiness, public launch, or fresh production endpoint proof;
- verify the blocked production probe is documented as missing evidence and was not retried;
- run `git diff --check`;
- because R15 is docs-only, no browser QA is required unless Prompt B chooses to capture additional non-destructive evidence in an approved environment.

If QA passes:
- write a QA report under `.gstack/qa-reports/`;
- mark R15 `merged_to_mainline` after merge;
- keep RG6 `gate_hold` / product red unless a separate Prompt C audit with fresh evidence changes it;
- merge only to `main` and push.
```
