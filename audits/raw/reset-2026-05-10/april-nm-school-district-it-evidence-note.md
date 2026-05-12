# April NM School-District IT Evidence Note

**Status:** Historical operator evidence for ADR-019 and the RG3 source-assisted remediation pivot.
**Created:** 2026-05-11.
**Privacy posture:** Summarized private email evidence. Do not copy full private thread bodies into repo artifacts.

## Source IDs

- Gmail message `19db864cc6650c12`: Lee forwarded `Fwd: NM IT for school districts` to Matt on 2026-04-22, forwarding an original 2026-04-20 message to Thomas.
- Gmail message `19dc1d856824901a`: Lee follow-up on 2026-04-24 with larger state workbook attachments.
- Gmail message `19dc1e669a7ae2b1`: Matt asked Lee whether the full generating chat could be exported.
- Gmail message `19dc1e98abc1fb44`: Lee clarified the workbook was meant for Thomas and that Thomas had asked for it.
- Gmail message `19dc2658a797c50a`: Lee sent a transcript/document showing a local Codex-style workflow for IT directors in TX/AZ/NV.

## Attached Artifacts Reviewed

- `nm_school_district_it_contacts_public_emails.csv`
- `nm_school_district_it_contacts_needs_manual_lookup.csv`
- `nm_school_district_it_outreach_email.txt`
- `district_it_contacts_by_state_20260424_172807.xlsx`
- `district_it_contacts_by_state_20260424_171553.xlsx`
- `command for IT Directors in tx,az,nv.docx`

## Evidence Summary

The April package is the strongest known manual-oracle proof point. It shows that a human plus basic chatbot/Codex workflow produced a source-backed school-district IT workbook that was useful enough for Thomas to request and for Lee to forward.

The first New Mexico CSV contained 10 school-district IT rows with public emails, titles, phone numbers, source URLs, `last_verified=2026-04-20`, and verification notes. The rows included named technology leaders at Albuquerque Public Schools, Rio Rancho Public Schools, Los Alamos Public Schools, Hobbs Municipal Schools, Farmington Municipal Schools, Carlsbad Municipal School District, Taos Municipal Schools, Belen Consolidated Schools, Gadsden Independent School District, and Clovis Municipal School District.

The second New Mexico CSV contained 7 additional school-district IT rows that needed manual direct-email lookup. Those rows still preserved named people, titles, public contact/phone, source URLs, and explicit notes explaining the missing email blocker. This is product-relevant evidence that "missing direct email" should not erase useful research; it should become a clear `manual_lookup` or `review` row with a next action.

The later XLSX attachments expanded the pattern to TX/AZ/NV. The transcript/document attached on 2026-04-24 shows the workflow evolving into a local collector that used official education-agency rosters, crawled district technology pages, classified contacts as verified / likely named / not found, and wrote state workbooks.

## Product Implication

The winning pattern was not fully autonomous broad Scout search. It was targeted public-source collection plus structured extraction, validation, categorization, and export. White Rabbit should first beat this manual+chatbot workflow:

```text
operator target
-> authoritative/public source collection
-> extracted contacts and manual-lookup rows
-> field-level evidence and blockers
-> sales-first workbook/export
```

The RG3 remediation should use this April package as the benchmark for R09D-R09H. A future gate should ask whether the product can reproduce or improve the workbook faster and more honestly than the human workflow, with zero unsupported contacts marked CRM-ready.
