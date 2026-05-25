# Retail IT Leads Benchmark Packet - Lee Gmail Thread 2026-05-20

## Source And Scope

Source: Gmail thread `REPO for Retail IT leads`, Lee Biby to Matt, sent 2026-05-20 18:26 Mountain. The email body was empty; the useful source material is the attached `Retail IT leads for REPO.docx`. Matt replied at 18:38 Mountain that the material was useful and asked Lee to send future material as Markdown, JSON, or plain text rather than DOCX.

This is read/report work only. It creates a benchmark packet from the attachment; it does not change product code, schemas, tests, prompts, or gate status. RG6 remains product-red/held.

## What The Attachment Actually Contains

The DOCX is a pasted Codex terminal transcript, not a finished CSV/XLSX. The transcript shows two related but different jobs:

1. Initial ask: build a contact file for retail IT directors for Target, Walmart, and Lowes in Arizona, New Mexico, and North Carolina, organized by state tabs/pages, with normal contact fields.
2. Pivoted output: broaden from literal state-level IT directors to publicly listed retail technology and digital leaders nationwide to get near 75 rows while avoiding personal direct emails and cell numbers.

The final national-output facts recorded in the transcript are: 77 total contacts, 59 `verified_current`, 18 `older_public`, and workbook sheets `Verified_Current`, `Older_Public`, and `README`. The final simplified files named in Lee's workspace were `retail_contacts_by_state.xlsx`, state CSVs for AZ/NM/NC, `retail_tech_leaders_public.xlsx`, `retail_tech_leaders_public.csv`, and `retail_tech_leaders_verified_current.csv`.

## Current Product Fit

White Rabbit already has the right conceptual shape for this packet: natural-language target, source-assisted public-web research, categorized rows, field-level validation, source-backed evidence, and sales-first export. The national retail leader output also fits the high-volume transparency direction because it produces a broad candidate universe rather than a tiny three-row list.

The attachment also matches the source-assisted/manual-oracle pattern better than autonomous search. It starts from official leadership pages, investor pages, state/store presence pages, and explicit method notes. That is exactly the kind of source-pack evidence the current northstar says White Rabbit should compile into READY, REVIEW, ORG-ONLY, NOT FOUND, and export rows.

## What Would Break

The original target was state-specific retail IT directors for three companies across three states. The generated work pivoted to national corporate retail technology leaders. That pivot may be operationally useful, but the product must not hide the mismatch. White Rabbit should represent each requested account/state pair as a row, even when the honest result is `organization_only` or `not_found`.

The final workbook's `verified_current` label is not equivalent to White Rabbit `READY`. It means the source looked current, not that a person has verified direct contact evidence. Corporate main phones, media emails, investor emails, and contact-us URLs are organization context; they should not populate person-level `email` or `phone` as verified contact fields.

The attachment does not provide enough field-level validation for the current output contract. White Rabbit needs per-field status, source URL, evidence snippet or extracted reference, checked timestamp, and notes for name, title, organization, email, phone, and source. The transcript has status notes and official URLs, but not a complete validation graph.

Older public rows are valuable but should remain REVIEW until refreshed. Official press releases and filings can support historical claims, but they are not current-role proof without a newer source.

## Benchmark Fixtures To Add Later

The strongest future fixtures are documented in `benchmark-fixture-candidates.json`:

- `retail_state_presence_public_contact_az_nm_nc`: nine requested account/state combinations, with explicit ORG-ONLY/NOT FOUND behavior when state-level IT leaders are unavailable.
- `retail_national_technology_leaders_public_profiles`: 50+ official-source retail technology leaders, separating source-current rows from contact-ready rows.
- `retail_contact_privacy_negative`: direct personal email/cell-number ask should be constrained, not satisfied with guesses or non-public data.
- `retail_source_currency_and_misattribution_regression`: regressions for misattribution, malformed URLs, and stale official sources.
- `retail_workbook_export_shape`: state tabs plus current/older public split while preserving White Rabbit export/evidence columns.

## Bottom Line

This packet should become benchmark source material, not a product-readiness claim. It is especially useful because it exposes the exact trap RG6 is already failing on: broad volume can improve while source precision, target fidelity, and contact readiness remain below the gate.
