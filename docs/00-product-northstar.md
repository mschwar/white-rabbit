# 00 - Product Northstar

**Status:** Active anti-drift source of truth for the validated-leads rebuild.
**Created:** 2026-05-09.
**Current launch gate:** Red with Matt-directed internal operator-use exception. See ADR-010.

This document supersedes older optimistic "works" claims when product quality is in question. Treat the 2026-05-09 zero-trust audit as the current product reality until the benchmark suite proves otherwise.

## One-Sentence Product Definition

White Rabbit is an internal-first B2B lead research tool that turns a natural-language sales target into a small, exportable list of field-validated leads with transparent evidence.

## Core Loop

```text
natural-language query
  -> high-quality validated leads
  -> transparent field-level evidence
  -> ranked results
  -> export
```

Everything in the product either improves this loop or stays out of the operator path.

## Non-Negotiable Value Proposition

White Rabbit does not win by returning more leads than ZoomInfo, DiscoverOrg, Apollo, or generic GPT research. It wins by returning better data: real scraped and cross-validated contacts, clear source support, explicit missing/failure states, and exports that do not make SDRs or AEs waste time on bad dials, bouncebacks, guessed domains, fake emails, wrong personas, or unsupported claims.

Low volume is acceptable. Noisy raw candidates are acceptable only when they are checked, visibly annotated, and clearly separated from usable leads. Bad data shown confidently is worse than no data.

## Target User

Primary user: Thomas, a working B2B sales rep using White Rabbit in his own daily prospecting.

Secondary users:

- Matt, who fulfills paid customer briefings and uses the tool to reduce manual research time.
- Lee, who tests generalization and helps present the Scotty demo, but does not define the first B2B quality bar.

The app is not an external self-serve SaaS, not a public signup product, and not a multi-tenant customer system. Until the launch gate reaches green, it is an internal tool for the three operators.

## Usable Lead

A usable lead is a row that a salesperson can put into a CRM and act on without doing most of the research again.

Minimum usable-lead requirements:

- `name`: a real person, not a company, department, title, or generic role.
- `title`: current or clearly source-supported role aligned with the query persona.
- `organization`: source-supported account or employer aligned with the query.
- `contact`: verified email/phone, or a deduced contact explicitly supported by a validated domain pattern. Missing contact can appear only if the row is not presented as CRM-ready.
- `source_support`: field-level evidence for name, title, organization, and contact status.
- `validation_status`: clear enough that the operator knows whether the row is ready, noisy, organization-only, not-found, or failed.
- `checked_at`: timestamp for validation work.

## Failed Lead

A failed lead is any row that would create false confidence or push research burden back onto the operator.

Examples:

- Company or organization name in the person-name field.
- Wrong persona for the query, even when the person is real.
- Correct organization but unsupported title.
- Email marked found when it was guessed, mismatched, blocked, stale, or unsupported.
- Source URL that resolves but does not support the claimed field.
- LinkedIn/blocked/PDF/403 source treated as validation without accessible supporting content.
- Generic main line or missing contact presented as CRM-usable.
- Named-account query returning adjacent accounts without an explicit not-target label.
- Consumer/privacy-sensitive targeting query that runs instead of being refused.

## Validation-By-Field Model

Every returned candidate should be represented as a set of fields, not a blob of confidence.

Required field validation shape:

| Field | Required validation data |
| --- | --- |
| `name` | status, supporting source URL, evidence snippet or extracted text reference, checked_at, notes |
| `title` | status, supporting source URL, evidence snippet or extracted text reference, checked_at, notes |
| `organization` | status, supporting source URL, evidence snippet or extracted text reference, checked_at, notes |
| `email` | contact status, source or domain-pattern evidence, checked_at, notes |
| `phone` | contact status, source evidence, checked_at, notes |
| `source` | resolved URL, HTTP/access status, whether it supports each field |

Allowed candidate categories:

- `person_lead`: a named person with source-supported title and organization.
- `organization_only`: a target account was found but no usable person was validated.
- `not_found`: a named target account/persona was searched and no acceptable contact was found.
- `failed`: a candidate was rejected because evidence contradicted or did not support the claim.

Allowed contact statuses:

- `verified_found`: contact is directly present in source evidence.
- `deduced_with_pattern_evidence`: contact is inferred only after a verified domain/email pattern supports it.
- `missing`: no contact found; row is not CRM-ready by default.
- `failed`: contact was checked and found wrong, unsupported, bounced, mismatched, or inaccessible.
- `unsupported`: insufficient evidence to claim status.

No silent guessing. No placeholder emails. No "Found" status without evidence.

## Export Requirements

Export is part of the core loop, not a bonus surface.

Default export behavior:

- Export usable leads first.
- Include noisy, organization-only, not-found, and failed rows only when explicitly included and clearly flagged.
- Preserve the query, run ID, candidate category, rank, scores, validation status, evidence, and checked timestamp.
- Include enough validation data for a salesperson or manager to understand why each row is safe or unsafe.

Required export columns:

- `query`
- `run_id`
- `rank`
- `candidate_category`
- `usable_candidate`
- `lead_name`
- `title`
- `organization`
- `email`
- `email_status`
- `phone`
- `phone_status`
- `fit_score`
- `evidence_score`
- `contact_score`
- `ranking_gate`
- `source_name_url`
- `source_title_url`
- `source_org_url`
- `source_email_url`
- `source_phone_url`
- `source_access_status`
- `validation_notes`
- `checked_at`

Export must never flatten uncertain data into confident raw rows. Validation status and evidence travel with the data.

## Red / Yellow / Green Launch Gate

### Red - Do Not Ship Or Dogfood

Current state: red.

Red if any of these are true:

- Any golden benchmark returns zero leads or crashes.
- Backend lead-search endpoints are callable outside the intended app boundary.
- B2C/privacy-sensitive queries are not explicitly blocked.
- Any sampled row contains a fake, guessed, unsupported, or mismatched email without a failed/deduced label.
- Export lacks validation context.
- Operator UI organizes, beautifies, or scales untrusted data before the single-query loop works.

Allowed users in red by default: Matt and agents only. ADR-010 records a 2026-05-10 Matt-directed exception that permits Thomas and Lee to use the internal deployment without treating the product as green or public-ready.

### Yellow - Matt-Only Internal Evaluation

Yellow requires all of these:

- Arizona K-12 VoIP benchmark returns at least 6 of 8 target districts with either a correct named technology/IT/telecom decision maker or an explicit `not_found` reason.
- At least 50% of sampled returned person rows are right persona and source-backed.
- Contact status is one of verified, deduced-with-evidence, missing, failed, or unsupported. No unsupported "Found" emails.
- Backend API boundary is protected or ingress-restricted.
- Operator UI hides recipes, batch, Friday review, scoreboards, sandbox reset, and implementation-detail copy from primary navigation.
- Export includes validation-by-field columns.

Allowed users in yellow: Matt only, with benchmark evidence captured in repo docs.

### Green - Thomas/Lee Operator Dogfood

Green requires all of these:

- At least 70% sampled precision on right persona, organization, and source support across the required benchmark suite.
- At least 50% of usable rows have verified or explicitly deduced contacts.
- Zero fake or unsupported emails in sampled output.
- Query-to-export can be completed in under 5 minutes without Matt explaining the UI.
- Operator minutes per usable lead can be tracked without extra ceremony.
- Thomas can run the Arizona benchmark and one simple B2B query without re-researching most rows.

Allowed users in green: Thomas and Lee can dogfood under the documented rubric.

## Kill / Hide / Keep Policy

Primary navigation while red:

| Surface | Policy while red | Reason |
| --- | --- | --- |
| Recipe library | Hide from primary operator navigation | It organizes untrusted outputs before repeatability is proven. |
| Batch workspace | Hide from primary operator navigation | Bulk bad data is worse than single-query bad data. |
| Friday review export | Hide or remove | It adds review ceremony around untrusted data. |
| Scoreboards | Hide from primary operator navigation | Metrics are useful only after validation quality exists. |
| Sandbox reset UI | Hide from primary operator navigation | Reset controls are implementation machinery and weaken quota trust if exposed. |
| Operator minutes UI | Keep internally, simplify later | Minutes per usable lead is the headline KPI, but it should not distract from query-to-export. |

Keep internally after yellow:

- Recipes may remain as stored run artifacts and evaluation inputs.
- Scoreboards may be available to Matt for quality review.
- Operator minutes may be captured after export or review.
- Batch may return only after single-query precision is reliable and field validation scales.

Do not expose these as primary operator surfaces while the product is red.

## Anti-Drift Rules

- Source URL alone is not evidence.
- Composite confidence is not a rank.
- Fit, Evidence, and Contact scores must reflect server-side validation, not LLM optimism.
- A person row needs a person. If only the account is known, call it `organization_only`.
- A named-account search should prefer explicit `not_found` over adjacent filler.
- Export must carry validation status and evidence.
- A beautiful UI around bad data is product harm.
- Bad data shown confidently is worse than no data.
