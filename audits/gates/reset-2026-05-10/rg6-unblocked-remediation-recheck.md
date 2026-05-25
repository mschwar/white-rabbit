# Reset Gate Review - RG6 Unblocked Remediation Recheck

**Date:** 2026-05-24
**Branch:** `audit/reset-rg6-post-remediation`
**Decision:** hold
**Product gate:** red

## Scope

Matt authorized a narrow RG6 red-remediation push after the post-remediation Prompt C audit was blocked by the production sandbox cap. This recheck covers only:

- Fly runtime stability and readiness after the API/core deploy.
- Arizona K-12 named-account source/contact yield.
- Sampled precision over saved required-suite outputs.
- Primary query-to-export operator-minute capture.
- Browser QA for primary results, evidence review, export, and auto-close behavior.

It does not unlock public SaaS, accounts, orgs, billing, recipe/batch expansion, Thomas/Lee dogfood, or yellow/green claims.

## Evidence

Raw artifacts:

- `audits/raw/reset-2026-05-10/rg6/post-remediation-stable-rerun-2026-05-24/`
- `audits/raw/reset-2026-05-10/rg6/browser-qa-2026-05-24/`

Runtime:

- Deployed Fly API image: `white-rabbit-api:deployment-01KSDDWGE5A5Z40R91R8DMQFNZ`.
- Post-deploy `/health`: HTTP 200.
- Post-deploy `/readiness`: HTTP 200 with body `status=ready`.
- Direct tokenless `/scout`: HTTP 401.
- Fly has two started `shared-cpu-1x:1024MB` machines on the latest image.

Arizona K-12 production run:

- HTTP 200, 8 rows, `run_id=1448cb7b-9100-4d05-9fe6-4527f4f3f63e`.
- Tier distribution: 2 `high_trust_usable`, 2 `review`, 1 `organization_only`, 3 `failed`.
- Contact-quality passes: 2.
- Contact evidence acquired: 2.
- Persistence/readback matched 8 response rows to 8 DB rows.
- Timed query-to-export closed the run with `operator_minutes=3.755`; CSV export row count was 8.

Required-suite saved outputs:

- Passed cases: 2 of 6.
- Failed cases: 4 of 6.
- Mismatches: `thomas-arizona-k12: source`, `healthcare-it-phoenix: persona, contact, source`, `finance-cisos-new-york: persona, contact, source`, `manufacturing-ops-detroit: persona, contact, source, volume`.
- Manufacturing still lacks a valid product artifact in this folder: collector status `ERROR`, 0 rows, no run ID.

Sampled precision:

- Sampled row count: 38.
- Persona precision: 0.158.
- Organization precision: 0.421.
- Source-support precision: 0.447.
- Contact-support precision: 0.184.
- Unsupported email count: 0.
- Fake email count: 0.
- Green precision floor met: false.

Browser QA:

- Local production-mode Playwright smoke passed.
- Screenshots cover login, primary search results, evidence review, export-ready, and auto-close message.
- Browser smoke used mocked `/api/scout` rows and a mocked `/api/runs/qa-r14c-run/close`; it proves UI behavior only, not live lead quality.

## Acceptance Mapping

| Criterion | Result | Evidence |
| --- | --- | --- |
| Arizona run covers all 8 named districts with explicit categories | Pass | 8 rows returned and categorized. |
| At least 6 of 8 districts have correct technology decision-maker row or source-backed not-found/manual explanation | Not proven | 2 READY rows; 2 REVIEW rows; 1 ORG-ONLY row; 3 failed rows. This does not establish 6 source-backed usable/manual outcomes. |
| READY rows have zero unsupported/fake contacts | Pass | Sampled packet has 0 unsupported and 0 fake emails; READY contacts are source-backed email/phone. |
| At least one source-backed contact-quality pass | Pass | Arizona has 2 contact-quality passes and 2 contacts acquired. |
| Required-suite sampled precision reaches 70% on persona, organization, and source support | Fail | 0.158 persona, 0.421 organization, 0.447 source. |
| Operator minutes per usable lead captured from query to export | Pass but not sufficient alone | Arizona timed export closed at 3.755 minutes with 2 READY rows. |
| Broad required-suite outputs provide usable volume and precision | Fail | Healthcare and finance have 0 contact passes; manufacturing artifact failed; sampled precision remains below floor. |
| Production runtime remains protected and ready | Pass | Latest health/readiness/tokenless checks pass. |

## Value Prop Verdict

Hold. The product is better than the previous capped run: it can now produce a non-empty Arizona export, acquire source-backed public contacts, persist/read back the run, and capture operator minutes. But RG6 still does not prove that the operator loop is worth dogfooding. The required suite remains low precision, broad vertical outputs are dominated by failed/review rows, and Arizona still falls short of the 6-of-8 named-account quality target.

## Next Deployment Recommendation

Keep the product red. Do not unlock yellow/green, Thomas/Lee dogfood, public SaaS, accounts, orgs, billing, or recipe/batch expansion.

The next valid work is not another ceremony pass. It should be a Matt-authorized red remediation focused on source strategy and broad precision:

- Make official/named-account source ordering live for Arizona and rerun the Arizona benchmark from an authenticated production path.
- Decide whether public-web-only contact discovery is sufficient for the target markets; if not, explicitly scope a permitted source/vendor or concierge/manual lookup workflow.
- Reduce broad-output noise before re-running sampled precision; do not claim precision from failed placeholder rows.
- Rerun the full required suite only after the above changes are deployed and the auth/env path is stable enough to produce complete artifacts.

## Verification

- `cd packages/core && PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 uv run pytest tests -q` passed: 169 passed, 6 skipped.
- `cd apps/api && WR_API_INTERNAL_TOKEN=test-internal-token uv run pytest tests -q` passed: 57 passed, existing datetime warnings.
- `cd apps/web && npm test -- --run` passed: 15 files, 37 tests.
- `cd apps/web && npm run build` passed with the existing Next.js `middleware` deprecation warning.
- `cd apps/web && PORT=3100 WR_E2E_ARTIFACT_DIR=... WR_E2E_API_BASE_URL=https://white-rabbit-api.fly.dev npm run test:e2e:prod` passed: 2 Playwright tests.
- `flyctl deploy -a white-rabbit-api --remote-only` completed and post-deploy runtime checks passed.
