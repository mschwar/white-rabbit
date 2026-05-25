# RG6R3 Arizona Source Remediation Evidence Summary

**Collected:** 2026-05-25
**API image:** `white-rabbit-api:deployment-01KSGJT21PZYH4A3V3WTHS55JY`
**Path:** `audits/raw/reset-2026-05-10/rg6/rg6r3-arizona-source-remediation-2026-05-25-direct/`

## Files

- `thomas-arizona-k12.json` / `.http`: fresh Arizona K-12 live run.
- `quality-summary.json`: required-suite summary from the direct protected Fly API run.
- `sampled-precision-required-suite.json`: deterministic precision packet from saved outputs.
- `sampled-precision-delta.json`: before/after deltas against the 2026-05-24 packet.
- `coverage-evidence.json`: row-level 6-of-8 coverage evidence.
- `timed-query-to-export.csv` and `timed-query-to-export.json`: exported Arizona rows and operator-minute close proof.
- `timed-query-readback.json` and `timed-query-close.json`: persisted readback and `/runs/{run_id}/close` proof.

## Arizona Result

- HTTP status: `200`.
- Rows: `8`.
- Expected target coverage: `8/8`, missing `0`.
- High-trust usable rows: `2`.
- Person rows: `4`.
- Source-supported rows: `6`.
- Source-backed person or explicit blocker rows: `6/8`.
- Contact quality passes: `3`.
- Timed export close: `operator_minutes=3.034`, readback `200`, close `200`.

## Sampled Precision Delta

| Slice | Persona | Organization | Source | Contact |
| --- | ---: | ---: | ---: | ---: |
| Arizona before | 0.250 | 0.625 | 0.625 | 0.250 |
| Arizona after | 0.500 | 0.750 | 0.750 | 0.375 |
| Arizona delta | +0.250 | +0.125 | +0.125 | +0.125 |
| Required-suite before | 0.158 | 0.421 | 0.447 | 0.184 |
| Required-suite after | 0.250 | 0.562 | 0.604 | 0.146 |
| Required-suite delta | +0.092 | +0.141 | +0.157 | -0.038 |

## Residual Blockers

- RG6 remains product-red.
- Arizona still has only `2` high-trust usable rows and does not clear the green sampled-precision floor.
- Required-suite sampled contact support regressed from `0.184` to `0.146`.
- The separate web-boundary attempt in `../rg6r3-arizona-source-remediation-2026-05-25/` returned 401 for `/api/scout` and `/api/source-assisted-proof`; the direct protected Fly API run is the passing live evidence for this slice.
