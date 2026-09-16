---
title: "Lead Generation Brainstorm - Photo 06 - Original Workflow"
doc_type: "handwritten_note_transcription"
photo_index: 6
markdown_file: "06-original-workflow.md"
source_image: "06-original-workflow.heic"
original_photo_filename: "IMG_1059.HEIC"
transcription_source_image: "F30095C9-7B2A-4735-B301-AB51F02AF832.jpeg"
status: "raw_transcription_plus_expansion"
purpose: "Capture the original natural-language workflow and convert it into a reusable request template."
core_concept: "The system should transform a simple fill-in-the-blank request into a structured lead-generation search."
primary_fields:
  - coherent_request_template
  - role_slot_A
  - industry_slot_B
  - scope_slot_C
  - examples
data_quality_notes:
  - "This appears to be the original user-facing request format."
  - "The page contains A/B/C placeholders corresponding to role, industry, and geographic area."
---

# Lead Generation Brainstorm - Photo 06 - Original Workflow

## 1. Raw transcription

```text
Original workflow

Coherent requests:

Give me a CSV file / list of contact information for ______
in the ______ industry in the ______ area.

A:
IT director
Purchasers
Materials acquisition specialists
media buyers
trainers

B:
Retail
IT
shipping
textiles
agriculture

examples:

- Materials purchaser in the logging industry
- IT Directors in the education field
- Directors of marketing in retail sales.
```

---

# 2. Cleaned-up request template

```text
Give me a CSV file or list of contact information for [A: role/function/title] in the [B: industry] industry in the [C: geographic area].
```

Expanded version:

```text
Give me a CSV file of contact information for [A: role/function/title] and related titles with the same job function in the [B: industry/organization type] industry within [C: geography/scope]. Prefer contacts with decision-making authority and include source URLs for verification.
```

---

# 3. Embedded data fields

```yaml
original_workflow:
  request_template_short: "Give me a CSV file or list of contact information for [A] in the [B] industry in the [C] area."
  request_template_expanded: "Give me a CSV file of contact information for [A] and related titles with the same job function in the [B] industry within [C]. Prefer contacts with decision-making authority and include source URLs for verification."

  A_role_slot:
    description: "The title, role, job function, or decision-maker persona."
    raw_examples:
      - IT director
      - Purchasers
      - Materials acquisition specialists
      - media buyers
      - trainers

  B_industry_slot:
    description: "The industry, vertical, sector, or organization type."
    raw_examples:
      - Retail
      - IT
      - shipping
      - textiles
      - agriculture

  C_area_slot:
    description: "The geography, territory, region, or market area."
    raw_examples:
      - "[blank in original template]"
    expanded_examples:
      - Utah
      - New Mexico
      - Northwest USA
      - Texas
      - New Jersey
      - Sandoval County
      - nationwide
```

---

# 4. Data dictionary

|Field|Type|Required?|Description|Example|
|---|--:|--:|---|---|
|`A_role_slot`|string|Yes|Target person or function|`IT Director`|
|`A_related_titles`|list|No|Similar job titles to include|`Technology Director`, `CIO`|
|`B_industry_slot`|string|Yes|Target industry or organization type|`education`|
|`B_related_industries`|list|No|Adjacent industry labels|`universities`, `schools`, `EdTech`|
|`C_area_slot`|string|Yes|Geographic or market area|`New Mexico`|
|`output_format`|enum|No|Requested file/list format|`CSV`|
|`contact_fields`|list|No|Information to collect|`name`, `title`, `email`, `phone`, `source_url`|
|`include_source_urls`|boolean|Recommended|Preserve evidence for each lead|`true`|

---

# 5. Expanded A role seeds

```yaml
A_role_seed_expansions:
  IT_director:
    job_function: "technology leadership"
    expanded_titles:
      - IT Director
      - Director of IT
      - Director of Information Technology
      - Technology Director
      - CIO
      - Chief Information Officer
      - IT Manager
      - Systems Director
      - Network Director
      - Director of Technology Services

  purchasers:
    job_function: "purchasing and procurement"
    expanded_titles:
      - Purchaser
      - Buyer
      - Purchasing Manager
      - Procurement Manager
      - Procurement Director
      - Materials Buyer
      - Sourcing Specialist
      - Vendor Manager
      - Supply Chain Manager
      - Inventory Manager

  materials_acquisition_specialists:
    job_function: "materials sourcing and acquisition"
    expanded_titles:
      - Materials Acquisition Specialist
      - Materials Buyer
      - Materials Manager
      - Procurement Specialist
      - Purchasing Specialist
      - Supply Chain Specialist
      - Sourcing Specialist
      - Inventory Specialist
      - Category Manager

  media_buyers:
    job_function: "paid media and advertising acquisition"
    expanded_titles:
      - Media Buyer
      - Paid Media Manager
      - Advertising Manager
      - Digital Advertising Manager
      - Performance Marketing Manager
      - Demand Generation Manager
      - Growth Marketing Manager
      - User Acquisition Manager
      - Marketing Acquisition Manager

  trainers:
    job_function: "training, education, and enablement"
    expanded_titles:
      - Trainer
      - Training Manager
      - Training Director
      - Corporate Trainer
      - Learning and Development Manager
      - L&D Manager
      - Instructional Designer
      - Education Coordinator
      - Enablement Manager
      - Sales Enablement Manager
```

---

# 6. Expanded B industry seeds

```yaml
B_industry_seed_expansions:
  retail:
    expanded_terms:
      - retail
      - retail sales
      - specialty retail
      - ecommerce
      - consumer goods
      - retail chain
      - independent retailer
      - brick-and-mortar retail
      - wholesale retail

  IT:
    expanded_terms:
      - information technology
      - managed IT services
      - software
      - SaaS
      - cybersecurity
      - cloud infrastructure
      - IT consulting
      - systems integration
      - data services

  shipping:
    expanded_terms:
      - shipping
      - logistics
      - freight
      - transportation
      - distribution
      - warehousing
      - fulfillment
      - supply chain
      - courier services

  textiles:
    expanded_terms:
      - textiles
      - fabric
      - apparel manufacturing
      - garment production
      - textile distribution
      - industrial textiles
      - upholstery
      - soft goods
      - textile import/export

  agriculture:
    expanded_terms:
      - agriculture
      - agribusiness
      - farming
      - crop production
      - farm supply
      - irrigation
      - agricultural equipment
      - seed supplier
      - fertilizer supplier
      - livestock supply
```

---

# 7. Example request expansions

## Example 01: Materials purchaser in the logging industry

```yaml
example_01:
  raw_example: "Materials purchaser in the logging industry"
  canonical_request: "Give me a CSV of materials purchasers, buyers, procurement managers, and sourcing specialists in the logging industry within [GEOGRAPHY]."
  A:
    role: "materials purchaser"
    expanded_titles:
      - Materials Purchaser
      - Materials Buyer
      - Procurement Manager
      - Purchasing Manager
      - Sourcing Specialist
      - Supply Chain Manager
      - Inventory Manager
  B:
    industry: "logging"
    expanded_industries:
      - logging
      - forestry
      - timber
      - lumber
      - wood products
      - forest products
      - sawmills
      - timber harvesting
  C:
    geography: "missing"
    clarification_needed: true
```

---

## Example 02: IT directors in the education field

```yaml
example_02:
  raw_example: "IT Directors in the education field"
  canonical_request: "Give me a CSV of IT directors, technology directors, CIOs, and IT managers in the education field within [GEOGRAPHY]."
  A:
    role: "IT Director"
    expanded_titles:
      - IT Director
      - Director of IT
      - Director of Information Technology
      - Technology Director
      - CIO
      - IT Manager
      - Systems Director
  B:
    industry: "education"
    expanded_industries:
      - education
      - universities
      - colleges
      - K-12 schools
      - school districts
      - charter schools
      - online education
      - EdTech
      - continuing education
  C:
    geography: "missing"
    clarification_needed: true
```

---

## Example 03: Directors of marketing in retail sales

```yaml
example_03:
  raw_example: "Directors of marketing in retail sales"
  canonical_request: "Give me a CSV of directors of marketing, marketing managers, heads of marketing, and growth marketing leaders in retail sales within [GEOGRAPHY]."
  A:
    role: "Director of Marketing"
    expanded_titles:
      - Director of Marketing
      - Marketing Director
      - VP Marketing
      - Head of Marketing
      - Marketing Manager
      - Brand Manager
      - Growth Marketing Manager
      - Demand Generation Manager
      - Digital Marketing Manager
  B:
    industry: "retail sales"
    expanded_industries:
      - retail
      - retail sales
      - specialty retail
      - ecommerce
      - consumer goods
      - retail chains
      - independent retailers
      - brick-and-mortar stores
  C:
    geography: "missing"
    clarification_needed: true
```

---

# 8. Recommended final user-facing prompt format

```text
Give me a [CSV/list/JSON] of [NUMBER] contacts for [ROLE OR JOB FUNCTION] in the [INDUSTRY OR ORGANIZATION TYPE] industry within [GEOGRAPHY OR MARKET SCOPE]. Include related titles with the same job function. Prefer people with buying power or decision authority. Include source URLs and a confidence score for each lead.
```

## Example filled prompt

```text
Give me a CSV of 100 contacts for purchasing managers and related procurement roles in the irrigation and landscape supply industry within the Northwest USA. Include related titles with the same job function. Prefer people with buying power or decision authority. Include source URLs and a confidence score for each lead.
```

---

# 9. This document should become

```yaml
recommended_next_docs:
  - ORIGINAL_WORKFLOW.md
  - USER_REQUEST_TEMPLATE.md
  - EXAMPLE_REQUEST_EXPANSIONS.md
  - CANONICAL_PROMPT_FORMAT.md
```
