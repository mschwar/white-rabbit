---
title: "Lead Generation Brainstorm - Photo 04 - Request Formula"
doc_type: "handwritten_note_transcription"
photo_index: 4
markdown_file: "04-request-formula.md"
source_image: "04-request-formula.heic"
original_photo_filename: "IMG_1060.HEIC"
transcription_source_image: "41658215-C77B-474D-B2CC-A0C3E1EA8D66.jpeg"
status: "raw_transcription_plus_expansion"
purpose: "Define the lead-generation request as a structured formula: Request = A individual + B business + C scope."
core_formula: "R = Request = A(individual) + B(business/industry) + C(scope)"
primary_fields:
  - request
  - individual
  - business
  - scope
  - output_formats
  - parameters
data_quality_notes:
  - "This page is the clearest system architecture sketch."
  - "Some text in the business column appears crossed out or faint; uncertain entries are marked [unclear]."
---

# Lead Generation Brainstorm - Photo 04 - Request Formula

## 1. Raw transcription

```text
R =
Request
User input

A (individual) + B (Business) + C (Scope)

A:
decision makers
professional position
buying power

B:
Industry / vert
[unclear crossed-out notes]

C:
Geographic Area
Market

output:
csv, txt,
json

parameters:
min hits
min a+b+c
```

Example items circled under A:

```text
IT directors
Purchasers
Materials Acq spclt
media buyers
trainers
```

Example items circled under B:

```text
Retail
IT
shipping
textiles
agriculture
```

---

# 2. Cleaned-up interpretation

A user gives a rough lead-generation request. The system should parse it into three components:

```text
Request = A + B + C
```

Where:

- **A = Individual:** the person, title, role, function, or decision-maker type.
    
- **B = Business:** the industry, organization type, sector, or vertical.
    
- **C = Scope:** the geography, market, company size, revenue, or other constraint.
    

The output should be available as:

- CSV
    
- TXT
    
- JSON
    

The request should include parameters such as:

- minimum number of hits
    
- minimum acceptable fit across A+B+C
    

---

# 3. Embedded request schema

```yaml
request_formula:
  R:
    label: "Request"
    description: "The user's natural-language lead generation request."
    source: "user_input"

  A_individual:
    label: "Individual"
    description: "The person-level target: job title, role, function, seniority, and buying power."
    raw_terms:
      - decision makers
      - professional position
      - buying power
    example_seed_roles:
      - IT directors
      - Purchasers
      - Materials Acquisition Specialists
      - Media Buyers
      - Trainers

  B_business:
    label: "Business"
    description: "The target industry, vertical, organization type, or business category."
    raw_terms:
      - industry
      - vertical
      - business
    example_seed_industries:
      - Retail
      - IT
      - Shipping
      - Textiles
      - Agriculture

  C_scope:
    label: "Scope"
    description: "The geography, market, size, or constraint that narrows the search."
    raw_terms:
      - geographic area
      - market
    example_seed_scopes:
      - city
      - state
      - region
      - country
      - nationwide
      - employee count
      - revenue threshold
      - market segment

  outputs:
    - csv
    - txt
    - json

  parameters:
    - minimum_hits
    - minimum_A_B_C_fit
```

---

# 4. Data dictionary

|Field|Type|Required?|Description|Example|
|---|--:|--:|---|---|
|`request_text`|string|Yes|Original user request|`Find IT directors in education in New Mexico`|
|`A.individual`|object|Yes|Target person/function|`IT Director`|
|`A.related_titles`|list|No|Expanded equivalent titles|`Technology Director`, `CIO`|
|`A.buying_power`|enum|No|Estimated authority|`high`, `medium`, `low`|
|`B.business`|object|Yes|Target industry/vertical|`Education`|
|`B.related_industries`|list|No|Expanded industry terms|`Universities`, `K-12`, `EdTech`|
|`C.scope`|object|Yes|Geography or market filter|`New Mexico`|
|`C.constraints`|list|No|Other filters|`500+ employees`, `public institutions`|
|`output_format`|enum/list|No|Desired output|`csv`|
|`minimum_hits`|integer|No|Minimum target lead count|`100`|
|`minimum_fit_score`|integer|No|Minimum score across A+B+C|`75`|

---

# 5. Expanded role/function seeds from A

```yaml
A_individual_seed_expansions:
  IT_directors:
    expanded_titles:
      - IT Director
      - Director of IT
      - Director of Information Technology
      - Technology Director
      - Chief Information Officer
      - CIO
      - IT Manager
      - Systems Director
      - Network Director
      - Director of Technology Services

  purchasers:
    expanded_titles:
      - Purchaser
      - Buyer
      - Purchasing Manager
      - Procurement Manager
      - Procurement Director
      - Sourcing Manager
      - Strategic Sourcing Manager
      - Vendor Manager
      - Category Manager

  materials_acquisition_specialists:
    expanded_titles:
      - Materials Acquisition Specialist
      - Materials Buyer
      - Materials Manager
      - Procurement Specialist
      - Supply Chain Specialist
      - Inventory Manager
      - Purchasing Specialist
      - Sourcing Specialist

  media_buyers:
    expanded_titles:
      - Media Buyer
      - Paid Media Manager
      - Advertising Buyer
      - Performance Marketing Manager
      - Digital Marketing Manager
      - Demand Generation Manager
      - Growth Marketing Manager
      - Marketing Acquisition Manager

  trainers:
    expanded_titles:
      - Trainer
      - Training Manager
      - Learning and Development Manager
      - Corporate Trainer
      - Instructional Designer
      - Workforce Development Manager
      - Education Coordinator
      - Training Director
```

---

# 6. Expanded industry seeds from B

```yaml
B_business_seed_expansions:
  retail:
    expanded_terms:
      - retail
      - specialty retail
      - ecommerce
      - consumer goods
      - brick-and-mortar retail
      - retail chains
      - independent retailers
      - wholesale retail

  IT:
    expanded_terms:
      - information technology
      - managed services
      - software
      - SaaS
      - cybersecurity
      - cloud services
      - IT consulting
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

  textiles:
    expanded_terms:
      - textiles
      - apparel manufacturing
      - fabric suppliers
      - garment production
      - industrial textiles
      - upholstery
      - textile distribution

  agriculture:
    expanded_terms:
      - agriculture
      - farming
      - agribusiness
      - crop production
      - irrigation
      - seed suppliers
      - farm equipment
      - agricultural supply
```

---

# 7. Expanded scope seeds from C

```yaml
C_scope_seed_expansions:
  geography:
    examples:
      - city
      - metro_area
      - county
      - state
      - region
      - country
      - nationwide
      - multi_state_region

  market:
    examples:
      - enterprise
      - small_business
      - mid_market
      - Fortune_500
      - public_sector
      - private_sector
      - nonprofit
      - franchise
      - multi_location

  size_constraints:
    examples:
      - employee_count_min
      - employee_count_max
      - annual_revenue_min
      - annual_revenue_max
      - transaction_volume
      - location_count
      - customer_count

  pain_point_constraints:
    examples:
      - high_growth
      - hiring
      - supply_chain_pressure
      - regulatory_pressure
      - climate_exposure
      - procurement_complexity
      - operational_inefficiency
```

---

# 8. Minimum A+B+C fit scoring

The note mentions:

```text
min a+b+c
```

This should become a fit score.

```yaml
minimum_fit_score:
  description: "A combined score that determines whether a lead sufficiently matches the requested role, industry, and scope."
  scoring:
    A_individual_match:
      max_points: 40
      examples:
        exact_title_match: 40
        related_title_match: 30
        same_department_lower_seniority: 20
        weak_role_match: 10
        no_match: 0

    B_business_match:
      max_points: 35
      examples:
        exact_industry_match: 35
        close_vertical_match: 25
        broad_sector_match: 15
        weak_industry_match: 5
        no_match: 0

    C_scope_match:
      max_points: 25
      examples:
        exact_geography_or_scope_match: 25
        nearby_region_match: 18
        broader_market_match: 10
        weak_scope_match: 5
        no_match: 0

  recommended_thresholds:
    excellent: 90
    good: 75
    review: 60
    reject: 59
```

---

# 9. Canonical request object

```json
{
  "request_text": "Find IT directors in the education field in New Mexico.",
  "A": {
    "target_function": "Information Technology leadership",
    "primary_titles": ["IT Director"],
    "expanded_titles": [
      "Director of IT",
      "Director of Information Technology",
      "Technology Director",
      "CIO",
      "IT Manager"
    ],
    "decision_authority": "medium_to_high"
  },
  "B": {
    "target_industry": "Education",
    "expanded_industries": [
      "Universities",
      "Colleges",
      "K-12 Schools",
      "School Districts",
      "Online Education",
      "EdTech"
    ]
  },
  "C": {
    "geography": ["New Mexico"],
    "market_scope": null,
    "constraints": []
  },
  "output": {
    "formats": ["csv", "json"],
    "minimum_hits": 100,
    "minimum_fit_score": 75
  }
}
```

---

# 10. This document should become

```yaml
recommended_next_docs:
  - REQUEST_FORMULA.md
  - REQUEST_OBJECT_SCHEMA.md
  - A_B_C_FIT_SCORING.md
  - QUERY_PLANNER_SPEC.md
```
