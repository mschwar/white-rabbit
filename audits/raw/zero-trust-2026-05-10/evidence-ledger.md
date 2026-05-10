# Evidence Ledger - Zero-Trust Audit 2026-05-10

**Branch:** `audit/zero-trust-2026-05-10`
**Base:** `rebuild/validated-leads-loop` at `bc1270d` (`merge: f19 batch internal-only`)
**Product-code edit policy:** read/report only. No product source files changed.

## Operator Evidence

| Source ID | Source | Location / ID | Audit Use |
| --- | --- | --- | --- |
| OP-MONROE-7 | Monroe 7 transcript | `/Users/mschwar/Documents/orgatlas/output/transcribe/monroe-st-ne-7/monroe-st-ne-7-transcript.md` | Thomas/Lee north star: quality over volume, visible validation trail, search-bar simplicity, garbage leads create downstream debt. |
| OP-MONROE-8 | Monroe 8 transcript and summary | `docs/meeting-notes/monroe-st-ne-8-transcript.md`; `docs/meeting-notes/monroe-st-ne-8-minutes.md`; `docs/meeting-notes/monroe-st-ne-8-executive-summary.md` | Product shape: lead tool, not generic assistant; 10 queries / 1000 rows; CSV/Excel export; validation trail per row. |
| GMAIL-THOMAS-01 | Thomas "Compare GPT list" initial email | Gmail message ID `19e08ef2c7c42bf6` | Exact Arizona K-12 prompt and GPT comparison list. Used as live benchmark prompt source. |
| GMAIL-THOMAS-02 | Thomas "Compare GPT list" follow-up | Gmail message ID `19e08fb5a55a240d` | Thomas says GPT list looked stronger than expected; attached `Arizona-School-District-Technology-Contacts.pdf`. |
| GMAIL-THOMAS-03 | Thomas "Compare GPT list" data-quality follow-up | Gmail message ID `19e092b5ad3e10a1` | Thomas says GPT data was not great and asks Matt to run comparable list; attached `AZ_K12_VoIP_Targets.xlsx`. |
| GMAIL-LEE-01 | Lee "GPT vs tool search" | Gmail message ID `19e0e8dcf8ad1322` | Exact commodity-buyer prompt; Lee says direct person contact is more useful than company-only results. |
| GMAIL-LEE-02 | Lee "Ask Lee:" | Gmail message ID `19e0eb0b801090da` | CSV/export preference: CRM-facing columns first, then report/run/status/evidence/audit columns later. Also B2C/privacy caution. |
| IMESSAGE-01 | Targeted iMessage product search | `~/Library/Messages/chat.db` targeted keyword count only | Targeted Lee/Thomas/product keyword search returned zero matching message text. No private message dump performed. |

## Local Artifacts

| Source ID | Path | Audit Use |
| --- | --- | --- |
| WB-AZ-01 | `/Users/mschwar/Downloads/district_it_contacts_by_state_20260424_172807.xlsx` | Existing Arizona/Texas/Nevada district workbook. Used only as corroborating local artifact, not as complete ground truth. |
| V1-APP | `/Users/mschwar/Documents/proxy-lead/app.py` | Frozen v1 reference. Read only. Compared single-search/table/dossier/export flow. |
| V1-STYLE | `/Users/mschwar/Documents/proxy-lead/style.css` | Frozen v1 visual reference. Read only. Compared restraint, console layout, and lime accent usage. |
| V1-DEMO | `/Users/mschwar/Documents/proxy-lead/demo_data.py` | Frozen v1 fixture evidence. Read only. Confirms v1 was demo/fixture-backed even when the interaction model was clearer. |
| SCREEN-USER-01 | User-provided screenshots on 2026-05-10 | Current v2 localhost and old Streamlit v1 screenshots | Visual comparison: v2 is card-heavy and noisy; v1 was also noisy but closer to operator workflow. |

## Live Verification Artifacts

| Artifact | Path |
| --- | --- |
| Live benchmark JSON + HTTP status files | `audits/raw/zero-trust-2026-05-10/live/` |
| Browser screenshots | `audits/raw/zero-trust-2026-05-10/screenshots/` |
| Full-mode CSV export sample | `audits/raw/zero-trust-2026-05-10/live/full-export-healthcare.csv` |
| Verification command log | `audits/raw/zero-trust-2026-05-10/commands/verification-log.md` |
| iMessage targeted search note | `audits/raw/zero-trust-2026-05-10/imessage-targeted-search.md` |
| Arizona workbook readback | `audits/raw/zero-trust-2026-05-10/workbook-arizona-k12-readback.md` |
| Persistence readback | `audits/raw/zero-trust-2026-05-10/db-readback.md` |

## Evidence Limits

- Gmail evidence is summarized and cited by message ID. The audit does not quote unnecessary private content.
- Gmail attachments were not re-exported into the repo during this audit. The ledger records the message IDs and attachment names observed through the Gmail connector.
- iMessage access was limited to targeted keyword counts against `chat.db`; no broad message-history export was performed.
- Live verification used local services at `localhost:3000` and `localhost:8000`. API keys were available through app `.env` files; shell-level `TAVILY_API_KEY` was absent.
- Audit spend was below the requested `$5` cap. The saved live runs show per-run estimated costs around one cent.
