# White Rabbit zero-trust product audit - 2026-05-09

Auditor stance: every prior "works" claim was treated as untrusted. Rendered cards, screenshots, and successful API responses were not counted as evidence of product value. A lead only counted as usable if a salesperson could put it into a CRM and act without doing most of the research again.

## Executive verdict

**Do not ship. Do not put Thomas or Lee on this as a daily tool yet.**

The current app is a dressed-up demo with live plumbing, not a trustworthy sales tool. It has product screens, persistence, exports, and a deployed backend, but the decisive loop fails:

`natural-language target -> high-quality validated leads -> export`

The Arizona K-12 VoIP benchmark, the exact domain that generated the original product signal, failed twice: the full Thomas benchmark prompt crashed Tavily because the app submitted a query longer than 400 characters, and a compressed version returned **zero leads**. Across 18 returned leads from live search benchmarks, **0 were CRM-usable under the stated standard**. Several rows were companies presented as people, wrong personas, missing contacts, blocked/unsupported source URLs, or source links that did not support the claimed field.

The UI is not fatal by itself, but it is pointed at the wrong job. It exposes internal machinery ("FastAPI POST /scout", "Recipe storage", "Sandbox reset") and asks the operator to understand Scout/Full/recipes/batch before it proves it can return one good list.

## Scorecard

| Domain | Starting hypothesis | Audit score | Verdict |
|---|---:|---:|---|
| Features/functions | 3/10 | **2/10** | Screens exist, but core flows are unproven or unsafe. Backend is public, batch/recipes are premature, and reset makes quota toothless. |
| UI/UX/design | 3/10 | **3/10** | Visually coherent but generic admin software. It makes the operator think about implementation instead of prospects. |
| Actual search | 1/10 | **1/10** | Fatal. 0/18 returned sampled leads were CRM-usable. Arizona VoIP benchmark failed. |

Overall: **rebuild the search core before more product work.**

## Evidence base

- Gmail thread: May 8 "Compare GPT list" thread from Thomas Gentry, including `AZ_K12_VoIP_Targets.xlsx` and `Arizona-School-District-Technology-Contacts.pdf`.
- Meeting transcripts:
  - [Monroe St NE 7 transcript](<C:/Users/Matty/Documents/orgatlas/output/transcribe/monroe-st-ne-7/monroe-st-ne-7-transcript.md>)
  - [Monroe St NE 8 transcript](<C:/Users/Matty/Documents/orgatlas/output/transcribe/monroe-st-ne-8/monroe-st-ne-8-transcript.md>)
- Current app: [https://white-rabbit-ten.vercel.app/](https://white-rabbit-ten.vercel.app/)
- First iteration demo: [https://white-rabbit.streamlit.app/?wr_demo=1](https://white-rabbit.streamlit.app/?wr_demo=1)
- Repos:
  - [mschwar/white-rabbit](https://github.com/mschwar/white-rabbit)
  - [mschwar/proxy-lead](https://github.com/mschwar/proxy-lead)
- Raw live API outputs:
  - [summary.json](<C:/Users/Matty/Documents/white-rabbit/audits/raw/zero-trust-2026-05-09/summary.json>)
  - [source-url-validation.json](<C:/Users/Matty/Documents/white-rabbit/audits/raw/zero-trust-2026-05-09/source-url-validation.json>)
  - [raw output directory](<C:/Users/Matty/Documents/white-rabbit/audits/raw/zero-trust-2026-05-09>)
- Browser screenshots:
  - ![Current app login](C:/Users/Matty/Documents/white-rabbit/audits/raw/zero-trust-2026-05-09/screenshots/current-app-login.png)
  - ![First iteration Streamlit check](C:/Users/Matty/Documents/white-rabbit/audits/raw/zero-trust-2026-05-09/screenshots/first-iteration-streamlit.png)

Screenshots are included only as UI evidence. They are not lead-quality evidence.

## Customer truth from Thomas and Lee

From Monroe 7 and Monroe 8, the product thesis is narrower than the app currently behaves:

- Thomas explicitly values **data quality over volume**: he would rather have around 80 right contacts than thousands of wrong dials and bouncebacks.
- Thomas disliked GPT/ZoomInfo-style assumption chains. He called out bad domains, guessed emails, and generic main lines as SDR time-wasters.
- Thomas wants a **single search bar** with natural-language target inputs: job title, revenue/company size, vertical, location.
- Thomas asked for a CSV/Excel export with a **validation column** showing how the information was checked.
- Thomas wants guardrails: off-topic prompts should redirect to lead-search inputs.
- The Arizona K-12/VoIP list was the benchmark because Scotty reacted to correct phone/contact data.

The current app does not meet that bar.

## Top 10 failures by customer harm

1. **The decisive Arizona K-12 VoIP benchmark failed.** The full benchmark prompt returned `503` with: `Tavily search failed... Query is too long. Max query length is 400 characters.` A compressed Arizona K-12 VoIP query returned zero leads. This is the original product signal failing in production.
2. **0/18 returned sampled leads were CRM-usable.** Missing contacts dominated. The app returned some real names, but not enough verified person/title/org/contact evidence for an SDR to act without re-researching.
3. **The backend is publicly callable.** The Vercel UI is password-gated, but `https://white-rabbit-api.fly.dev/scout`, `/full`, `/batch`, and `/sandbox/reset` are reachable directly. I ran the audit without the shared UI password. Shared-password auth is not the product boundary.
4. **False confidence fields are shown as if they are validated.** Example: `Raquel Burton | Director of Technology | Queen Creek Unified District | rburton@qsd4.org` mixes an email domain that points to Quartzsite with a Queen Creek organization claim. That is worse than missing data.
5. **The app returns organizations as leads.** `Sjostrom & Sons`, `F.H. Paschen`, and `Kankakee Valley Construction` were returned in the `name` field for "contractors in Illinois." Those are not people.
6. **Source links often do not support the claimed field.** LinkedIn returned HTTP 999 for one lead; AZED PDF source URLs returned 403 during validation; `Troy Throne` was not found on the returned source page.
7. **The guardrail misses real sales language and privacy risk.** `financial services CISOs in New York` was flagged as missing a target role/company type. B2C/privacy queries were not blocked; they ran and returned zero leads.
8. **UI makes users think about internals.** The Scout page literally lists `Next.js proxy routes`, `FastAPI POST /scout`, `Sandbox reset`, and `Recipe storage`.
9. **Premature product surface hides the broken core.** Recipe library, Friday review export, and bulk workspace add ceremony around bad data. They make the app feel more complete while the core output is not trustworthy.
10. **First iteration comparison is not a win.** The Streamlit app is more aligned to the operator loop, but repo inspection shows it was demo/fixture/VoIP-oriented. Current v2 replaced focus with admin apparatus without proving better search.

## Kill / keep / rebuild matrix

| Feature/function | Classification | Evidence and rationale |
|---|---|---|
| Shared-password auth | **Rebuild boundary** | Next middleware protects Vercel routes, but the Fly backend is public. Password-gating the UI is not enough. |
| Scout search | **Rebuild** | It returns too few leads, wrong shapes, missing contacts, and bad query handling. |
| Full search | **Hide/internalize until Scout works** | It stores bad search results as recipes, creating durable false confidence. |
| Sandbox quota | **Rebuild/internalize** | Shared global quota is easy to reset via public backend. It is not an operator-safe quota model. |
| Sandbox reset | **Hide/internalize** | Thomas asked for reset, but public `/sandbox/reset` makes caps meaningless. |
| Recipe name | **Hide** | It is internal bookkeeping before any repeatable recipe has proven value. |
| Recipe library | **Kill now** | No evidence it improves the core sales job. It organizes untrusted outputs. |
| Recipe scoreboard | **Hide/internalize** | Useful later for Matt's evaluation loop, not for Thomas under sales pressure. |
| Operator minutes / close run | **Keep, simplify later** | This is a real KPI, but it should be captured after export/review, not shown as product ceremony. |
| Feedback buttons | **Rebuild** | Useful if feedback trains evaluation, but labels on untrusted Scout cards do not make data better. |
| Lead export | **Keep, rebuild** | Export is required. It must include validation-by-field and should default to only usable or clearly flagged rows. |
| Friday recipe review export | **Kill** | Premature. Weekly recipe review is not the core loop. |
| Bulk/batch workspace | **Kill now** | Bulk bad data is worse than single-query bad data. |
| CSV upload for batch | **Kill now** | Same reason as batch. |
| Guardrails | **Rebuild** | Off-topic blocking works for three samples, but B2C/privacy boundary fails and common sales terms are missed. |
| Error messages | **Rebuild** | A user-caused long query is surfaced as "Search engine is rate-limited"; that is wrong and not actionable. |
| Sort controls | **Hide/deprioritize** | Sorting bad leads by scores does not produce usable leads. Keep only after scoring is proven. |
| Source links | **Keep, rebuild hard** | Must show which exact fields each source supports. A naked URL is not evidence. |
| First-iteration Streamlit features missing from v2 | **Rebuild selectively** | Bring back single search bar, source-checked validation context, and HubSpot/CRM CSV. Do not bring back demo fixtures or VoIP hardcoding. |

## Benchmark results table

Phone fields are `n/a` because the current API response does not return phone numbers.

| Query | Rank | Name returned | Title returned | Organization returned | Email returned | Email status returned | Phone returned | Source URL returned | Independent source checked | Name verified? | Title verified? | Organization verified? | Email verified | Right persona? | Notes | Verdict |
|---|---:|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Arizona K-12 VoIP/telecom benchmark from Thomas email | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a | Live API response | n/a | n/a | n/a | failed | no | Full Thomas-style prompt failed with Tavily 400: query longer than 400 characters. | failed |
| Arizona K-12 VoIP compressed target districts | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a | Live API response | n/a | n/a | n/a | missing | no | Returned 0 leads. Guardrail incorrectly said missing title/location despite `Arizona`, `IT decision makers`, and named districts. | failed |
| contractors in Illinois | 1 | Sjostrom & Sons |  | Sjostrom & Sons |  | Missing | n/a | https://gobridgit.com/blog/top-construction-companies-in-illinois/ | Returned source fetched HTTP 200 | yes | n/a | yes | missing | no | Company returned as `name`; not a person/contact. | wrong persona |
| contractors in Illinois | 2 | F.H. Paschen |  | F.H. Paschen |  | Missing | n/a | https://gobridgit.com/blog/top-construction-companies-in-illinois/ | Returned source fetched HTTP 200 | yes | n/a | yes | missing | no | Company returned as `name`; not a person/contact. | wrong persona |
| contractors in Illinois | 3 | Kankakee Valley Construction |  | Kankakee Valley Construction |  | Missing | n/a | https://ivcontractors.org/general-contractors/ | Returned source fetched HTTP 200 | yes | n/a | yes | missing | no | Company returned as `name`; not a person/contact. | wrong persona |
| contractors in Illinois | 4 | Melissa Muskopf | General Contractor | R.A. Cullinan & Son, Inc. |  | Missing | n/a | https://web.agcil.org/Active | Returned source fetched HTTP 200 | partial | partial | partial | missing | weak | Source page appears directory-like; field adjacency is not strong enough to trust person/title/org without rechecking. | unverified |
| contractors in Illinois | 5 | Troy Throne |  | Thorne Associates, Inc. |  | Missing | n/a | https://members.chicagolandagc.org/activememberdirectory/FindStartsWith?term=T | Returned source fetched HTTP 200 | no | n/a | yes | missing | no | Returned name not found on source page. Organization spelling suggests extraction drift. | bad source |
| IT directors at school districts in Arizona | 1 | David Griffis | IT Director | Toltec School District No. 22 |  | Missing | n/a | https://www.toltecsd.org/admin.aspx | Returned source fetched HTTP 200 | yes | yes | partial | missing | yes | Real person/title likely, but not one of target districts and no email/phone. | bad contact |
| IT directors at school districts in Arizona | 2 | Raquel Burton | Director of Technology | Queen Creek Unified District | rburton@qsd4.org | Found | n/a | https://www.azed.gov/sites/default/files/2023/07/FY23%20District%20Charter%20Contact%20List.pdf | Source fetch returned 403; independent email search points to Quartzsite domain, not Queen Creek | partial | no | no | failed | no | Exact failed field: `Queen Creek Unified District` paired with `rburton@qsd4.org`. | hallucinated |
| IT directors at school districts in Arizona | 3 | Maria Silva | IT Director | Queen Creek Unified District | msilva@qcusd.org | Found | n/a | https://www.azed.gov/sites/default/files/2023/07/FY23%20District%20Charter%20Contact%20List.pdf | Source fetch returned 403; independent search found Queen Creek association but not IT Director | yes | no | yes | failed | no | Email domain matches Queen Creek, but title/persona not independently supported. | wrong persona |
| IT directors at school districts in Arizona | 4 | Kristine Harrington | Chief Communications & Information Officer | Scottsdale Unified School District |  | Missing | n/a | https://www.susd.org/departments/information-technology | Returned source fetched HTTP 200 | yes | yes | yes | missing | yes | Source-backed leader, but not a target district and no contact. | bad contact |
| IT directors at school districts in Arizona | 5 | Brett Dahl | Superintendent | Humboldt Unified School District | brett.dahl@humboldtunified.com | Found | n/a | https://yavapaicoesa.gov/schools-and-charters/directory-of-yavapai-county-school-districts-2/ | Returned source fetched HTTP 200 | yes | yes | yes | found | no | Verified contact, wrong persona. Superintendent is not IT director/telecom buyer. | wrong persona |
| food and beverage operations leaders in Texas | 1 | Stephan Fitz | Director of Food and Beverage | The Adolphus |  | Missing | n/a | https://www.hotel-online.com/press_releases/release/the-adolphus-in-dallas-announces-new-leadership-to-head-up-food-and-beverage-operation/ | Returned source fetched HTTP 200 | yes | yes | yes | missing | yes | Good person/title/org, but no contact. Not CRM-usable without research. | bad contact |
| food and beverage operations leaders in Texas | 2 | Dave Hermann | Director, Food & Beverage | Wildflower Country Club |  | Missing | n/a | https://www.linkedin.com/in/dave-hermann-8922621a | LinkedIn returned HTTP 999 | no | no | no | missing | uncertain | Source not accessible enough to validate. | bad source |
| healthcare IT directors in Phoenix | 1 | Vincent Moore | Director, IT | Phoenix Health Care Management Services, Inc |  | Missing | n/a | https://www.phoenix-healthcare.com/who-we-are/ | Returned source fetched HTTP 200 | yes | yes | yes | missing | weak | App appears to match `Phoenix` company name, not necessarily Phoenix, Arizona location. No contact. | bad contact |
| healthcare IT directors in Phoenix | 2 | Jean Bondurant | VP, Phoenix Health Care | Phoenix Health Care Management Services, Inc |  | Missing | n/a | https://www.phoenix-healthcare.com/who-we-are/ | Returned source fetched HTTP 200 | yes | yes | yes | missing | no | Not healthcare IT director. Same location ambiguity. | wrong persona |
| healthcare IT directors in Phoenix | 3 | Michael McLemore | Senior Director, Networks | Phoenix Health Care Management Services, Inc |  | Missing | n/a | https://www.phoenix-healthcare.com/who-we-are/ | Returned source fetched HTTP 200 | yes | yes | yes | missing | weak | IT-adjacent, but no contact and Phoenix-location ambiguity. | bad contact |
| financial services CISOs in New York | 1 | Khalil Jackson | CISO | Federal Reserve Bank of New York |  | Missing | n/a | https://www.fairinstitute.org/blog/meet-a-member-khalil-jackson-federal-reserve-bank-of-new-york | Returned source fetched HTTP 200 | yes | yes | yes | missing | yes | Strong person/title/org match, but no email/phone. Not CRM-usable as returned. | bad contact |
| manufacturing operations leaders in Detroit | 1 | Sylvester Hester | President and CEO | LM Manufacturing, LLC |  | Missing | n/a | https://michauto.org/transforming-lives-and-communities-the-impact-of-lm-manufacturing/ | Returned source fetched HTTP 200 | yes | yes | yes | missing | no | Executive, not operations leader; no contact. | wrong persona |
| manufacturing operations leaders in Detroit | 2 | Bruce Smith | Senior Leadership | Detroit Manufacturing Systems LLC |  | Missing | n/a | https://www.linkedin.com/in/bruce-smith-0900b37 | LinkedIn source fetched but did not support title/org | yes | no | no | missing | no | Source did not verify the claimed organization/title. | bad source |

## Guardrail benchmark

| Query | Expected | Actual | Verdict |
|---|---|---|---|
| how do I reformulate our supply line | Block/redirect to lead query | 422 blocked with lead-generation message | Pass |
| write a cold email sequence for me | Block/redirect to lead query | 422 blocked with lead-generation message | Pass |
| build me a nuclear missile | Block/refuse | 422 blocked with lead-generation message | Pass, but generic |
| everyone who refinanced their house in Corrales in the last six months | Block B2C/privacy targeting | 200 OK, zero leads, `needs_more_detail` | Fail |
| people who posted vacation photos on public social media in the last 30 days with emails | Block B2C/privacy targeting | 200 OK, zero leads, `needs_more_detail` | Fail |

## Search-quality analysis

**Precision:** 0/18 usable leads. Some person/title/org triples were real, but a CRM-usable lead requires contact and field-level support. Missing email/phone means the operator still does the work.

**Persona match:** weak. Contractors returned companies. Manufacturing returned a CEO and an unsupported LinkedIn profile. Healthcare overfit to a company named Phoenix instead of Phoenix, Arizona. Arizona school queries produced non-target districts and a superintendent.

**Contact quality:** fatal. 3/18 rows had an email. Of those, 1 was a verified email attached to the wrong persona, and 2 were wrong/unsupported against the claimed org/title. 0/18 had a verified actionable email for the right persona.

**Source quality:** mixed at best. Several source URLs supported basic person/title/org claims, but the app treats source URL presence as stronger evidence than it is. LinkedIn blocking and 403 PDFs were not handled. The source URL does not tell the operator which fields it supports.

**Recency:** not controlled. The app does not show when the source was published, when a title was last verified, or whether the contact is current.

**Specificity:** poor. The Arizona benchmark named eight districts; the app either crashed or returned zero. Simple queries returned 1-5 leads, far below useful volume, while still being noisy.

**Query fidelity:** poor. The guardrail flags clear sales phrases as incomplete because phrase lists omit terms like `CISO`, `operations leader`, `financial services`, `manufacturing`, and `food and beverage`.

**Comparison to Thomas's GPT/manual benchmark:** Thomas already disliked a GPT list that at least included named contacts, phone numbers, and possible emails for the target districts. Current White Rabbit v2 returned nothing for the target benchmark. It is worse on the decisive test.

## UI/UX/design critique

The app does not answer "what do I do in the first 5 seconds?" with sufficient clarity. The first meaningful screen after auth is not a weapon for prospecting; it is a workspace with modes, quota, implementation details, recipes, and internal concepts.

Specific evidence:

- [scout-workspace.tsx](<C:/Users/Matty/Documents/white-rabbit/apps/web/src/components/scout-workspace.tsx:277>) explains Scout vs Full as "quick preview" vs "stored recipe." That is product-internal language.
- [scout-workspace.tsx](<C:/Users/Matty/Documents/white-rabbit/apps/web/src/components/scout-workspace.tsx:405>) displays `Next.js proxy routes`, `FastAPI`, `Sandbox reset`, and `Recipe storage` to the operator. This should never be on Thomas's screen.
- [scout.ts](<C:/Users/Matty/Documents/white-rabbit/apps/web/src/lib/scout.ts:107>) defaults the query to `Healthcare IT directors in Phoenix`, while [scout.ts](<C:/Users/Matty/Documents/white-rabbit/apps/web/src/lib/scout.ts:108>) defaults location to `New Mexico`. The default state is contradictory.
- The cards put Fit/Evidence/Contact scores on equal footing with raw fields, but the scores do not protect against obvious wrong-persona or bad-contact output.
- Source evidence is too shallow. "View source" is not enough. The UI needs field-level validation: name source, title source, org source, email source/pattern, date checked.
- Export is buried behind Full mode and a "Build lead export" step. Thomas asked for CSV/Excel output as a core path, not as a post-recipe ritual.

The visual theme is acceptable. The product framing is not.

## Code and architecture findings

- The web middleware returns `401` for unauthenticated `/api/*` under Vercel ([middleware.ts](<C:/Users/Matty/Documents/white-rabbit/apps/web/src/middleware.ts:34>)), but the deployed FastAPI backend has no equivalent auth and was directly callable during this audit.
- `/sandbox/reset` is public on the backend ([main.py](<C:/Users/Matty/Documents/white-rabbit/apps/api/api/main.py:407>)).
- `/batch` is public on the backend ([main.py](<C:/Users/Matty/Documents/white-rabbit/apps/api/api/main.py:475>)).
- The guardrail is phrase-list based ([query_guardrails.py](<C:/Users/Matty/Documents/white-rabbit/packages/core/src/core/query_guardrails.py:10>) and [query_guardrails.py](<C:/Users/Matty/Documents/white-rabbit/packages/core/src/core/query_guardrails.py:26>)); it misses normal sales terms and privacy-sensitive consumer targeting.
- The app does not preflight or rewrite long user prompts before Tavily. The most important benchmark crashed at the search-vendor limit.
- Batch spend caps are evaluated after search work inside the sequential batch path, so they are not a true preflight cost control.

## First iteration vs current app

The first iteration Streamlit demo at [https://white-rabbit.streamlit.app/?wr_demo=1](https://white-rabbit.streamlit.app/?wr_demo=1) did not render usable app content in the audit browser; the observed DOM was iframe shell plus Streamlit chrome, and the screenshot is archived above. I therefore did not count the live first-iteration demo as proof of functionality.

Repo inspection still shows useful comparison points:

- First iteration was closer to the operator story: "Find Your Target," B2B intelligence, CRM CSV export, side dossier, source checked / validation language, and search history.
- First iteration was not production-trustworthy either: it used demo bypasses/fixtures and was originally hardcoded around telecom/VoIP behavior.
- Current v2 has more infrastructure but less product focus. It adds auth, persistence, recipes, scoreboard, batch, quota, and exports, but none of that matters while the search output is bad.

Net: **v1 had a clearer product shape; v2 has more app surface. Neither currently proves the "better data than ZoomInfo/DiscoverOrg" claim.**

## Recommended 72-hour triage plan

1. **Freeze feature work.** No more recipe/batch/scoreboard/UI polish until search passes a real benchmark.
2. **Hide recipe library, Friday review, and batch from the operator UI.** Keep only a single search-to-results-to-export path.
3. **Put auth on the backend or restrict backend ingress.** Vercel auth without API auth is not a boundary.
4. **Implement query compilation before Tavily.** Convert long natural-language requests into bounded vendor queries under 400 chars. Decompose named-account benchmarks instead of sending the full prompt.
5. **Build a golden benchmark harness for the Arizona K-12 list.** The target districts are Mesa, Chandler, Peoria, Gilbert, Deer Valley, Paradise Valley, Dysart, and Maricopa. Store expected acceptable contacts and known bad GPT outputs.
6. **Replace "source URL" with field-level validation.** For each field: `name`, `title`, `org`, `email`, `phone`, record source, source quote/snippet hash, checked timestamp, and status.
7. **Disallow company-as-person rows.** If no named person is found, return an account row explicitly labeled `organization only`, not a lead.
8. **Block B2C/privacy queries explicitly.** Consumer home-refinance and social-media email targeting should never run a search.
9. **Export only validated/flagged data.** CSV should have `validation_notes`, `email_status`, `source_name`, `source_title`, `source_org`, `source_email`, and `usable_candidate`.
10. **Retest with Thomas's exact benchmark and simple queries.** Do not declare success from rendered cards.

72-hour pass condition: Arizona compressed benchmark returns at least 6 of 8 target districts with a correct named technology/IT/telecom decision maker or an explicit "not found" reason, and 0 fake/unsupported emails.

## Recommended 2-week rebuild plan

1. **Search pipeline, not one-shot extraction.**
   - Query planner: parse persona, vertical, geography, target accounts, constraints.
   - Source gathering: targeted searches per account/persona, not one broad query.
   - Candidate extraction: people and organizations separated.
   - Independent validation: verify person/title/org/contact from separate evidence when possible.
   - Contact handling: found, deduced-with-domain-pattern-evidence, missing, or failed. No silent guessing.
   - Ranking: rank by validated signal, not LLM confidence text.
2. **Evaluation harness.**
   - Golden tests for Arizona K-12 VoIP.
   - Simple-query tests for contractors, school IT, food/beverage ops.
   - Vertical tests for healthcare, finance, manufacturing.
   - Guardrail tests for off-topic and B2C/privacy.
   - Every build produces precision/persona/contact/source metrics.
3. **Operator UI rebuild.**
   - Single search bar first.
   - Results table first, cards second if needed.
   - Validation badges by field.
   - One-click export.
   - No internal API/recipe/quota language on the main screen.
4. **Internal evaluation surfaces.**
   - Keep recipe/scoreboard/operator-minutes for Matt behind an internal route after search quality passes.
   - Remove bulk workspace until single-query precision is reliable.
5. **Thomas/Lee dogfood protocol.**
   - Thomas tests B2B only with pre-agreed pass/fail rubric.
   - Lee tests generalization only after B2B benchmark clears.
   - Every operator correction becomes a benchmark fixture.

## Exact questions Matt should ask Thomas and Lee

Ask Thomas:

1. For school districts, is a district main phone acceptable if the person is correct, or does a lead require direct dial/email?
2. Are deduced emails acceptable if clearly labeled and supported by a verified domain pattern, or should export exclude them by default?
3. For "contractors in Illinois," do you want owners/executives at contractor companies, or are company/account rows useful without a person?
4. What is the minimum useful output for one query: 5 excellent leads, 25 mixed leads, or 100 flagged leads?
5. Which matters more in ranking: exact title match, target account fit, direct contact availability, or source recency?
6. What fields make a row CRM-ready in your workflow: name, title, org, email, phone, LinkedIn, source URL, validation note?
7. For Arizona K-12, which GPT rows were wrong because of person/title vs wrong email vs already-in-CRM?
8. How many minutes of manual verification are acceptable per usable lead?
9. Would you rather see "not found" for a target district or a lower-confidence adjacent contact?
10. What is the next single vertical after K-12 VoIP that should prove generalization?

Ask Lee:

1. Are you evaluating White Rabbit as a B2B lead tool, a demo narrative for Scotty, or a broader prospecting assistant?
2. What B2C/private-person targeting should be categorically out of bounds?
3. Does the current UI help you explain the data-quality story, or does it distract with app mechanics?
4. Which export format would you actually use in a live workflow?
5. What would make you trust a noisy result list instead of dismissing it?

## Red / yellow / green launch gate

**Red: do not ship / do not dogfood**

- Any golden benchmark returns zero leads or crashes.
- Any sampled row contains a fake or unsupported email without being labeled as failed/deduced.
- Backend search endpoints are callable without the app boundary.
- B2C/privacy queries are not explicitly blocked.
- Export lacks validation context.

Current state: **Red.**

**Yellow: internal Matt-only evaluation**

- Arizona K-12 benchmark returns at least 6/8 target accounts with correct named technology contacts or explicit "not found" reasons.
- At least 50% of sampled returned rows are right persona and source-backed.
- Contact field is either verified, deduced-with-evidence, or missing; no unsupported "Found" emails.
- UI hides recipe/batch/internal implementation from operator.
- Export works with validation-by-field.

**Green: Thomas/Lee operator dogfood**

- At least 70% sampled precision on right persona + organization + source support across the required benchmark set.
- At least 50% of usable rows have verified or explicitly deduced contacts.
- 0 fake emails in sampled output.
- Query-to-export can be completed in under 5 minutes without Matt explaining the UI.
- Operator minutes per usable lead is tracked without extra ceremony.

## Bottom line

White Rabbit v2 has engineering activity, not product proof. The current search output would waste Thomas's time and damage trust faster than a blank screen. Kill recipe library and bulk workspace from the operator surface now. Rebuild search validation around the Arizona K-12 benchmark, then earn back the rest of the product surface.
