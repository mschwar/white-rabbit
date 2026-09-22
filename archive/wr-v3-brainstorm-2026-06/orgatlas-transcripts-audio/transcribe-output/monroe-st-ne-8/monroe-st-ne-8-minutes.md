# Meeting Minutes: Monroe St NE 8

- Source audio: `/Users/mschwar/Downloads/Monroe St NE 8.m4a`
- Duration: `00:21:26`
- Generated: `2026-05-06`
- Attendees: Lee Biby, Matt Schwartz, Thomas Gentry
- Note: These minutes were generated from an AI transcript. Review against the audio before treating wording as exact.

## Purpose

Align on how to package the lead-generation tool for the first demo/trial, especially sandbox limits, prompt guardrails, customer data separation, exports, pricing discovery, and access for Lee and Thomas.

## Decisions

- The initial product experience should be a constrained lead-generation sandbox, not an unrestricted general-purpose AI tool.
- Trial/demo usage should start with a hard cap of 10 queries and 100 leads/rows per query, for a total cap of 1,000 output rows/data points.
- The tool should reject or redirect prompts outside lead generation and steer users back toward lead-list criteria such as job title, vertical, industry, and related search parameters.
- The current UI can stay mostly as-is for the first pass, with improvements as time allows.
- The export should support practical sales workflows, including CSV/Excel-style output and validation/context columns that explain how data was checked.
- Customer data should not be laterally connected across clients. Data may flow in and out for each customer workflow, but not across customer boundaries.
- The first sprint should stay focused on B2B lead generation and the Scotty/demo use case.
- B2C use cases, such as property-refinance targeting or social-media-triggered consumer lists, are valid future possibilities but are phase two.
- Matt will get the guarded version into Lee and Thomas's hands by end of day Friday.
- Cost/pricing should be learned empirically from early usage rather than over-modeled before the first test runs.

## Action Items

- Matt: Add sandbox caps of 10 queries and 100 output rows per query.
- Matt: Add prompt/output guardrails so the tool only produces lead-generation outputs.
- Matt: Add or verify user-facing fallback messaging for out-of-scope prompts.
- Matt: Give Lee and Thomas access to the tool by end of day Friday.
- Matt: Confirm that exports are usable for outreach workflows and include validation/context fields.
- Lee and Thomas: Use the guarded tool and provide high-signal feedback on usability, lead quality, and sales fit.
- Thomas: Coordinate next steps around the Scotty demo once the guarded version is ready.
- Team: Run enough trial batches to understand cost, output consistency, and reset needs.
- Lee: Continue banking/payment setup so customer payments can be handled once sales conversations progress.

## Open Questions

- What exact subscription or package price should be offered after the sandbox/demo?
- What are the real unit costs after several capped runs?
- What reset/admin flow should internal users have when they exhaust their 1,000-row test cap?
- How should customer-facing limits differ from internal Lee/Thomas testing limits?
- What exact customer-data isolation guarantees need to be documented before broader sales?
- Which B2C use cases are realistic after the B2B demo path is stable?

## Discussion Notes

Thomas pushed for clear sandbox throttles so the product can be demoed without becoming an open-ended AI system. The proposed default is 10 queries, 100 rows per query, and 1,000 total output rows.

The group agreed the prompt surface needs guardrails. If a user asks for something unrelated to lead generation, the system should steer them back to lead-list inputs instead of behaving like a general AI assistant.

Matt agreed to implement the constraints and framed this as a strong starting formula, not a permanent contract. The early version should create a tight feedback loop and be adjusted after real use.

Thomas emphasized the sales value of a simple conversational workflow compared with tools like ZoomInfo or DiscoverOrg, where building lists can require too much manual filtering and setup.

The team discussed possible B2C extensions, including refinance/property targeting and social-media-based consumer targeting, but kept the immediate plan focused on B2B lead generation for the demo.

Matt invited direct feedback on future AI-generated information dumps and asked Lee and Thomas to request shorter or differently structured updates when needed.

The closing discussion covered payment operations. Thomas mentioned checks, ACH, and credit cards; Matt said payment handling should follow whatever banking setup Lee chooses.
