# RG6 Fresh Production Evidence - 2026-05-22

Source: live production probes against `https://white-rabbit-ten.vercel.app/` and `https://white-rabbit-api.fly.dev` run from `/Users/mschwar/Documents/white-rabbit` on branch `audit/reset-rg6-fresh-evidence`.

## Summary

Fresh evidence does not clear the RG6 red hold. It replaces the earlier missing-production-proof gap with concrete production results:

- Fly `/health` returned 200, but `/readiness` returned body status `degraded`.
- Direct tokenless protected routes returned 401 for `/scout` and `/source-assisted-proof`.
- Vercel shared-password login succeeded and authenticated home loaded.
- Production privacy/B2C guardrail blocked a consumer/private-person query with HTTP 422.
- Web `/api/source-assisted-proof` returned HTTP 404; the source-assisted proof route is not exposed through the operator web path.
- Fresh Arizona K-12 VoIP Scout run returned 13 categorized rows in 126.569 seconds at estimated API cost $0.355318, but 0 `high_trust_usable` rows and 0 source-backed contacts.
- The Scout response's inline persistence readback reported 13/13 rows persisted, but separate web `GET /api/runs/{run_id}/leads` returned HTTP 500.

## Key Metrics

| Metric | Result |
| --- | --- |
| Production API health | 200 |
| Production API readiness body | degraded |
| Tokenless `/scout` | 401 |
| Tokenless `/source-assisted-proof` | 401 |
| Vercel auth/login | 200 |
| Privacy guardrail | 422 |
| Web source-assisted proof route | 404 |
| Arizona K-12 run rows | 13 |
| Arizona K-12 tier distribution | `{"failed": 4, "not_found": 1, "organization_only": 2, "review": 6}` |
| Arizona K-12 candidate categories | `{"failed": 4, "not_found": 1, "organization_only": 2, "person_lead": 6}` |
| High-trust usable rows | 0 |
| Contact quality passes | 0 |
| Contacts acquired | 0 |
| Separate persisted run readback | 500 |

## Decision Impact

Decision remains: `hold`; product gate remains: `red`.

This fresh run improves confidence in some safeguards (auth boundary, privacy guardrail, visible non-ready tiering), but it also adds live blockers:

1. Arizona K-12 benchmark did not reach yellow criteria: 0 ready rows and 0 source-backed contacts.
2. Current production query-to-export/readback path is not fully proven because separate persisted run readback returned 500.
3. Web source-assisted proof is not available at `/api/source-assisted-proof`.
4. Readiness is degraded, not fully ready.
5. The broad-ish named-account query was flagged `needs_more_detail` for title/location despite containing both role and Arizona named districts.

## Raw Artifacts

- `audits/raw/reset-2026-05-10/rg6/fresh-2026-05-22/direct-api-health-readiness-and-protection.json`
- `audits/raw/reset-2026-05-10/rg6/fresh-2026-05-22/web-auth-flow.json`
- `audits/raw/reset-2026-05-10/rg6/fresh-2026-05-22/web-privacy-guardrail.json`
- `audits/raw/reset-2026-05-10/rg6/fresh-2026-05-22/web-source-assisted-proof-route.json`
- `audits/raw/reset-2026-05-10/rg6/fresh-2026-05-22/web-scout-arizona-k12.json`
- `audits/raw/reset-2026-05-10/rg6/fresh-2026-05-22/web-scout-arizona-k12-summary.json`
- `audits/raw/reset-2026-05-10/rg6/fresh-2026-05-22/web-scout-arizona-k12-readback.json`
- `audits/raw/reset-2026-05-10/rg6/fresh-2026-05-22/decision-inputs.json`
