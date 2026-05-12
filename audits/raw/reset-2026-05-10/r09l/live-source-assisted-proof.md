# R09L Live Source-Assisted Product Proof

**Feature:** R09L - Live source-assisted product proof
**Packet:** r09l_live_source_assisted_product_proof
**Generated at:** 2026-05-11T00:00:00Z
**Packet pass:** yes

## Request

- Target: April 2026 New Mexico school-district IT
- Query: NM IT for school districts
- Run ID: r09l-april-nm-live-source-assisted-proof
- Source map: nm_k12_source_map_r09e
- Manual-oracle fixture: april_nm_school_district_it_manual_oracle
- Source map seeds: 13
- Manual-oracle rows: 17

## Source Map Replay

- Source map reproduced: yes
- Districts: 7
- Seeds: 13
- Official seeds: 13
- State roster seeds: 1
- Generic search sources: 0

## Source-Assisted Replay

- Source-assisted compiler rows: 17
- Compiler blocked generic source URLs: 0
- READY/high-trust rows: 10
- MANUAL_LOOKUP rows: 7
- Manual-oracle structure reproduced: yes

## Workbook Proof

- Workbook rows: 17
- READY_WITH_CONTACT: 10
- MANUAL_LOOKUP: 7
- Downgraded ready rows: 0
- Sales-first export headers: query, run_id, rank, workbook_tier, operator_label, candidate_category, crm_ready, lead_name
- Unsupported CRM-ready rows: 0
- Manual-lookup CRM-ready rows: 0
- Missing source rows: 0
- Missing next action rows: 0
- Private contact values redacted: yes

## Service Boundary

- Route: /source-assisted-proof
- Method: POST
- Protected route: yes
- Internal token required: yes
- Internal token checked: yes
- Sanitized input: yes
- Response status: 200

## Prompt B Handoff

- Ready after Prompt B merge: yes
- Required branch: rebuild/validated-leads-loop
- Required report: audits/gates/reset-2026-05-10/rg3-validation-semantics.md
- Keep downstream blocked: yes
- Blocked scope: RG4, refreshed mockups, R10-R12, export work, dogfood, main promotion
