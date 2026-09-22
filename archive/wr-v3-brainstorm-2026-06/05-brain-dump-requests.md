---
title: "Lead Generation Brainstorm - Photo 05 - Brain Dump Requests"
doc_type: "handwritten_note_transcription"
photo_index: 5
markdown_file: "05-brain-dump-requests.md"
source_image: "05-brain-dump-requests.heic"
original_photo_filename: "IMG_1058.HEIC"
transcription_source_image: "CED45E83-5FC3-489C-9A50-A66CBEA26BCB.jpeg"
status: "raw_transcription_plus_expansion"
purpose: "Capture raw example lead-generation requests and expand them into structured test cases."
core_concept: "These are seed examples that should become eval prompts for the automated lead-generation system."
primary_fields:
  - raw_requests
  - expanded_requests
  - A_individual
  - B_business
  - C_scope
  - ambiguity_notes
data_quality_notes:
  - "Some phrases are partially unclear; uncertain text is marked with [unclear]."
  - "Each raw request has been expanded into a structured A+B+C lead request."
---

# Lead Generation Brainstorm - Photo 05 - Brain Dump Requests

## 1. Raw transcription

```text
Brain dump requests:

- Social media managers in Utah

- Purchasers for irrigation and landscape materials
  supply stores in NW USA

- Directors of supply chain for pet food
  franchises on the [unclear]

- Construction materials fulfillment managers in
  commercial real estate

- accounting directors for [unclear]

- COO of a lead generation software SaaS
```

---

# 2. Cleaned-up request list

1. Social media managers in Utah.
    
2. Purchasers for irrigation and landscape materials supply stores in the Northwest USA.
    
3. Directors of supply chain for pet food franchises. Scope unclear.
    
4. Construction materials fulfillment managers in commercial real estate.
    
5. Accounting directors for an unclear target industry or geography.
    
6. COOs of lead-generation software SaaS companies.
    

---

# 3. Structured request seeds

## Request 01: Social media managers in Utah

```yaml
request_01:
  raw_request: "Social media managers in Utah"
  A_individual:
    primary_role: "Social Media Manager"
    job_function: "social media marketing"
    expanded_titles:
      - Social Media Manager
      - Social Media Director
      - Social Media Coordinator
      - Social Media Strategist
      - Digital Marketing Manager
      - Content Marketing Manager
      - Community Manager
      - Brand Manager
      - Marketing Manager
      - Communications Manager
  B_business:
    industry: "unspecified"
    possible_default_industries:
      - retail
      - restaurants
      - hospitality
      - consumer brands
      - agencies
      - local businesses
      - real estate
      - healthcare
      - fitness
      - tourism
  C_scope:
    geography:
      - Utah
    market_scope: "statewide"
  ambiguity_notes:
    - "Industry is not specified."
    - "Need to ask whether user wants all industries or a specific sector."
    - "Could default to local businesses and agencies if no industry is provided."
  canonical_request: "Give me a CSV of social media managers and related marketing contacts at businesses in Utah."
```

---

## Request 02: Purchasers for irrigation and landscape materials supply stores in NW USA

```yaml
request_02:
  raw_request: "Purchasers for irrigation and landscape materials supply stores in NW USA"
  A_individual:
    primary_role: "Purchaser"
    job_function: "purchasing/procurement"
    expanded_titles:
      - Purchaser
      - Buyer
      - Purchasing Manager
      - Procurement Manager
      - Materials Buyer
      - Inventory Manager
      - Supply Chain Manager
      - Operations Manager
      - General Manager
      - Owner
  B_business:
    industry: "irrigation and landscape materials supply"
    organization_types:
      - irrigation supply store
      - landscape supply store
      - hardscape supplier
      - nursery supply distributor
      - garden supply store
      - landscape materials distributor
      - outdoor materials supplier
      - contractor supply store
  C_scope:
    geography:
      - Northwest USA
    expanded_geographies:
      - Washington
      - Oregon
      - Idaho
      - Montana
      - Northern California
      - Alaska
    optional_geographies:
      - Wyoming
      - British Columbia
  ambiguity_notes:
    - "Northwest USA should be explicitly defined."
    - "For small local suppliers, owner or general manager may be the practical purchasing decision-maker."
  canonical_request: "Give me a CSV of purchasers, procurement managers, buyers, operations managers, and owners at irrigation and landscape materials supply stores in the Northwest USA."
```

---

## Request 03: Directors of supply chain for pet food franchises

```yaml
request_03:
  raw_request: "Directors of supply chain for pet food franchises on the [unclear]"
  A_individual:
    primary_role: "Director of Supply Chain"
    job_function: "supply chain leadership"
    expanded_titles:
      - Director of Supply Chain
      - Supply Chain Director
      - VP Supply Chain
      - Head of Supply Chain
      - Logistics Director
      - Procurement Director
      - Operations Director
      - Distribution Director
      - Inventory Director
      - Sourcing Director
  B_business:
    industry: "pet food franchises"
    organization_types:
      - pet food franchise
      - pet supply franchise
      - pet retail chain
      - pet food manufacturer
      - pet food distributor
      - specialty pet retailer
      - pet nutrition company
  C_scope:
    geography: "unclear"
    possible_scopes:
      - nationwide
      - United States
      - specific state or region needed
      - franchise systems only
      - companies with multiple locations
  ambiguity_notes:
    - "The phrase after 'on the' is unclear."
    - "Need clarification: is this nationwide, on the West Coast, on LinkedIn, or on a specific platform/source?"
    - "For small franchises, supply chain may be centralized at headquarters."
  canonical_request: "Give me a CSV of supply chain directors and related operations/procurement leaders at pet food franchises and pet supply chains in [GEOGRAPHY]."
```

---

## Request 04: Construction materials fulfillment managers in commercial real estate

```yaml
request_04:
  raw_request: "Construction materials fulfillment managers in commercial real estate"
  A_individual:
    primary_role: "Construction Materials Fulfillment Manager"
    job_function: "materials fulfillment, logistics, procurement, operations"
    expanded_titles:
      - Fulfillment Manager
      - Materials Manager
      - Construction Materials Manager
      - Logistics Manager
      - Procurement Manager
      - Purchasing Manager
      - Supply Chain Manager
      - Warehouse Manager
      - Operations Manager
      - Project Manager
      - Construction Operations Manager
  B_business:
    industry: "commercial real estate / construction materials"
    organization_types:
      - commercial real estate developer
      - commercial construction company
      - general contractor
      - construction materials supplier
      - building materials distributor
      - property development firm
      - facilities contractor
  C_scope:
    geography: "unspecified"
    market_scope:
      - commercial real estate
      - construction projects
      - materials logistics
  ambiguity_notes:
    - "The request mixes an industry with a supply-chain function."
    - "Need to clarify whether target organizations are commercial real estate firms, construction firms, or materials suppliers serving commercial real estate."
    - "Need geography."
  canonical_request: "Give me a CSV of fulfillment, materials, procurement, logistics, and operations managers at companies supplying construction materials to commercial real estate projects in [GEOGRAPHY]."
```

---

## Request 05: Accounting directors for [unclear]

```yaml
request_05:
  raw_request: "Accounting directors for [unclear]"
  A_individual:
    primary_role: "Accounting Director"
    job_function: "finance/accounting leadership"
    expanded_titles:
      - Accounting Director
      - Director of Accounting
      - Controller
      - Corporate Controller
      - Finance Director
      - Director of Finance
      - Accounting Manager
      - VP Finance
      - CFO
  B_business:
    industry: "unclear"
    possible_industries:
      - SaaS
      - healthcare
      - education
      - retail
      - real estate
      - nonprofit
      - construction
      - government contractors
  C_scope:
    geography: "unclear"
    possible_scopes:
      - local
      - statewide
      - regional
      - nationwide
      - company_size_threshold
  ambiguity_notes:
    - "This request is incomplete."
    - "Need target industry and geography."
    - "Could be transformed into a template prompt."
  canonical_request_template: "Give me a CSV of accounting directors, controllers, and finance directors in the [INDUSTRY] industry within [GEOGRAPHY]."
```

---

## Request 06: COO of a lead generation software SaaS

```yaml
request_06:
  raw_request: "COO of a lead generation software SaaS"
  A_individual:
    primary_role: "COO"
    job_function: "executive operations leadership"
    expanded_titles:
      - COO
      - Chief Operating Officer
      - VP Operations
      - Head of Operations
      - General Manager
      - Co-Founder
      - Founder
      - President
      - Chief Revenue Officer
      - CRO
  B_business:
    industry: "lead generation software SaaS"
    organization_types:
      - lead generation software company
      - sales intelligence SaaS
      - B2B data provider
      - prospecting software
      - outbound sales platform
      - marketing automation SaaS
      - CRM enrichment platform
      - demand generation software
  C_scope:
    geography: "unspecified"
    possible_scopes:
      - United States
      - North America
      - global English-language companies
      - venture-backed SaaS companies
      - companies with 10-500 employees
  ambiguity_notes:
    - "Need geography or company-size scope."
    - "COO may not exist in early-stage SaaS companies; include founders/heads of operations if allowed."
  canonical_request: "Give me a CSV of COOs, heads of operations, and founders at lead-generation software SaaS companies in [GEOGRAPHY/SCOPE]."
```

---

# 4. Combined eval prompt list

These should become test cases for the request parser.

```yaml
eval_prompts:
  - id: "eval_001"
    prompt: "Find social media managers in Utah."
    missing_fields:
      - industry
      - desired_contact_count
      - required_contact_fields

  - id: "eval_002"
    prompt: "Find purchasers for irrigation and landscape materials supply stores in the Northwest USA."
    missing_fields:
      - desired_contact_count
      - exact_definition_of_Northwest_USA
      - required_contact_fields

  - id: "eval_003"
    prompt: "Find directors of supply chain for pet food franchises."
    missing_fields:
      - geography
      - desired_contact_count
      - whether_to_include_pet_supply_retailers

  - id: "eval_004"
    prompt: "Find construction materials fulfillment managers in commercial real estate."
    missing_fields:
      - geography
      - whether_target_is_supplier_or_real_estate_firm
      - desired_contact_count

  - id: "eval_005"
    prompt: "Find accounting directors in [industry] in [geography]."
    missing_fields:
      - industry
      - geography
      - desired_contact_count

  - id: "eval_006"
    prompt: "Find COOs of lead-generation software SaaS companies."
    missing_fields:
      - geography
      - company_size
      - whether_to_include_founders_or_operations_heads
```

---

# 5. Clarification question templates

```yaml
clarification_questions:
  missing_industry:
    question: "What industry or organization type should I target?"
    examples:
      - retail
      - healthcare
      - SaaS
      - education
      - construction

  missing_geography:
    question: "What geography should I search?"
    examples:
      - Utah
      - New Mexico
      - Northwest USA
      - United States
      - nationwide

  missing_contact_count:
    question: "How many leads do you want?"
    examples:
      - 25
      - 50
      - 100
      - 500

  ambiguous_role:
    question: "Should I search only for the exact title, or include related titles with the same job function?"

  ambiguous_company_type:
    question: "Should I target companies that buy this service, companies that sell this product, or both?"
```

---

# 6. This document should become

```yaml
recommended_next_docs:
  - EVAL_PROMPTS.md
  - SAMPLE_REQUESTS.md
  - REQUEST_CLARIFICATION_RULES.md
  - TARGET_SEGMENT_TEST_CASES.md
```
