# proxy-lead v1 Summary

Created: 2026-06-03

## Bottom Line

`/Users/mschwar/Documents/proxy-lead` is the frozen White Rabbit v1 reference. It is simpler than v2, closer to a sellable demo, and useful as evidence of what worked: a Streamlit app, demo mode, live Tavily/OpenAI extraction, lead table, dossier-style context, and CSV export.

This document is read-only analysis. Do not edit proxy-lead.

Sources: `/Users/mschwar/Documents/proxy-lead/README.md`, `/Users/mschwar/Documents/proxy-lead/PRD.md`, `/Users/mschwar/Documents/proxy-lead/AGENTS.md`, `/Users/mschwar/Documents/proxy-lead/BACKLOG.md`, `/Users/mschwar/Documents/proxy-lead/docs/demo/MEETING_SUMMARY_2026-04-30.md`, `/Users/mschwar/Documents/proxy-lead/docs/demo/LEE_THOMAS_SCOTTY_REPORT_2026-05-05.md`.

## Product Shape

proxy-lead describes itself as a B2B AI lead-generation tool for telecom/VoIP AEs and SDRs. It searches live web sources to surface IT directors and network managers at K-12 school districts and local governments, positioned as an "unfair advantage" against stale mass-market databases. Source: proxy-lead `README.md`.

The PRD calls the product "OrgAtlas (White Rabbit)" and frames the problem as niche B2B sales teams wasting hours manually scraping websites for the right IT/networking directors. The jobs to be done are targeted discovery, contact extraction, qualification, and export. Source: proxy-lead `PRD.md`.

## Stack

- Streamlit app entrypoint: `app.py`.
- Search/extraction: Tavily plus OpenAI through `agent.py`.
- Models: Pydantic `Lead` and `LeadList`.
- Export: HubSpot-compatible CRM CSV via `export.py`.
- Persistence: local SQLite search history via `history_store.py`.
- Config/auth: `.env`, Streamlit secrets, and Streamlit Authenticator.
- Optional logging/mirroring: structured local logging and Supabase client.
- Dependencies: Streamlit, LangChain/OpenAI, Tavily, pandas, python-dotenv, Pydantic, requests, streamlit-authenticator, PyYAML, bcrypt, pytest. Source: proxy-lead `README.md`, `requirements.txt`, `AGENTS.md`.

## Why It Was Easier to Sell

proxy-lead had demo discipline:

- Demo Mode was sacred and protected the high-stakes presentation path. Source: proxy-lead `AGENTS.md`.
- The deployed demo could be framed as a portfolio of completed briefings rather than a fully self-serve product. Source: proxy-lead `docs/demo/MEETING_SUMMARY_2026-04-30.md`.
- The customer offer was boutique service work, not unlimited self-serve software. Source: proxy-lead `docs/demo/MEETING_SUMMARY_2026-04-30.md`, `docs/demo/LEE_THOMAS_SCOTTY_REPORT_2026-05-05.md`.
- The demo artifact put concrete sales output on screen: leads, evidence/source fields, why-target context, icebreakers, and export. Source: proxy-lead `README.md`, `docs/demo/LEE_THOMAS_SCOTTY_REPORT_2026-05-05.md`.

The Scotty packet explicitly says White Rabbit should be sold as a boutique lead-intelligence service, not as an unlimited query box. That was a stronger commercial shape than v2's internal gate machinery. Source: proxy-lead `docs/demo/LEE_THOMAS_SCOTTY_REPORT_2026-05-05.md`.

## What proxy-lead Did Not Prove

proxy-lead did not prove a durable autonomous lead-finding engine. It relied on demo fixtures, live-mode caution, and local fallback. It also listed "Migration to production stack (Next.js + FastAPI + Supabase)" as a future milestone, which became the v2 path where complexity increased. Source: proxy-lead `PRD.md`, `README.md`.

## Useful Lessons for the Reset

1. Keep a safe demo/delivery path.
2. Lead with customer artifact quality, not internal validation machinery.
3. Make the operator workflow concrete: target, search, lead table, dossier/evidence, export.
4. Use concierge language until the product can actually run self-serve.
5. Do not migrate to a heavier stack before the workflow is proven.

## Current proxy-lead State

The active sprint worklist shows WR-S1 through WR-S7 shipped and WR-S8 still unchecked: internal POC-mode toggle for previewing custom briefings. Source: proxy-lead `BACKLOG.md`.

That remaining item reinforces the same reset direction: the most important unsolved v1 job was safe preview and delivery of custom customer-specific briefings, not a generalized SaaS shell.
