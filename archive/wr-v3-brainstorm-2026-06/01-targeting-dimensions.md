---
title: "Lead Generation Brainstorm - Photo 01 - Targeting Dimensions"
doc_type: "handwritten_note_transcription"
photo_index: 1
markdown_file: "01-targeting-dimensions.md"
source_image: "01-targeting-dimensions.heic"
original_photo_filename: "IMG_1063.HEIC"
transcription_source_image: "8DB249D8-0FE4-4252-91CB-08B8BBA622E5.jpeg"
status: "raw_transcription_plus_expansion"
purpose: "Define the three major targeting dimensions for automated lead generation: individuals, industries, and scope."
core_model:
  individuals: "The human/contact side of the lead request."
  industries: "The business/organization/vertical side of the lead request."
  scopes: "The geographic, market-size, revenue, employee-count, and pain-point constraints."
primary_fields:
  - individuals
  - industries
  - scopes
  - example_roles
  - example_industries
  - example_scopes
data_quality_notes:
  - "Some handwriting is uncertain; unclear phrases are marked with [unclear]."
  - "List seeds have been expanded with likely synonyms and related lead-generation terms."
---

# Lead Generation Brainstorm - Photo 01 - Targeting Dimensions

## 1. Raw visible structure

The page is organized into three top-level targeting categories:

| Category | Meaning |
|---|---|
| Individuals | People, titles, decision-makers, authority holders |
| Industries | Businesses, verticals, sectors |
| Scopes | Geographic areas, market size, employee count, revenue, pain points |

---

# 2. Individuals

## Raw notes

- decision makers
- professional positions
- buying power
- titles

## Expanded seed list

```yaml
individuals:
  definition: "The target human contacts who may have buying power, influence, operational responsibility, or decision authority."
  raw_terms:
    - decision makers
    - professional positions
    - buying power
    - titles
  expanded_terms:
    - decision maker
    - economic buyer
    - technical buyer
    - user buyer
    - influencer
    - recommender
    - approver
    - budget owner
    - department head
    - director
    - manager
    - owner
    - founder
    - executive
    - C-suite
    - procurement lead
    - purchasing lead
    - operations lead
    - finance lead
    - HR lead
    - IT lead
    - facilities lead
    - supply chain lead
```

## Possible individual/title fields

```yaml
individual_fields:
  - full_name
  - first_name
  - last_name
  - title
  - seniority
  - department
  - job_function
  - decision_authority_level
  - buying_power_estimate
  - role_confidence_score
  - email
  - phone
  - linkedin_url
  - source_url
```

---

# 3. Industries

## Raw notes

- businesses
    
- verticals
    
- government sectors
    

## Expanded seed list

```yaml
industries:
  definition: "The target organization type, business category, sector, or vertical where leads should be found."
  raw_terms:
    - businesses
    - verticals
    - government sectors
  expanded_terms:
    - industry
    - vertical
    - sector
    - market category
    - business type
    - organization type
    - public sector
    - private sector
    - nonprofit sector
    - government agency
    - education
    - healthcare
    - SaaS
    - retail
    - construction
    - real estate
    - agriculture
    - shipping
    - logistics
    - textiles
    - waste management
    - environmental services
```

## Possible industry fields

```yaml
industry_fields:
  - company_name
  - organization_type
  - industry
  - sub_industry
  - vertical
  - sector
  - NAICS_code
  - SIC_code
  - business_model
  - company_url
  - company_description
  - industry_confidence_score
```

---

# 4. Scopes

## Raw notes

- geographic areas
    
- total addressable markets
    
- # employees
    
- annual revenue
    
- pain points
    

## Expanded seed list

```yaml
scopes:
  definition: "The constraints that narrow the search universe by geography, size, revenue, market, operational conditions, or pain points."
  raw_terms:
    - geographic areas
    - total addressable markets
    - number of employees
    - annual revenue
    - pain points
  expanded_terms:
    - city
    - county
    - state
    - region
    - country
    - nationwide
    - international
    - market size
    - total addressable market
    - serviceable available market
    - number of locations
    - number of employees
    - annual revenue
    - transaction volume
    - customer volume
    - operational pain point
    - climate condition
    - regulatory condition
    - business maturity
    - franchise status
```

## Possible scope fields

```yaml
scope_fields:
  - city
  - county
  - state
  - region
  - country
  - geography_label
  - employee_count_min
  - employee_count_max
  - annual_revenue_min
  - annual_revenue_max
  - transaction_volume
  - company_size
  - market_scope
  - pain_points
  - scope_confidence_score
```

---

# 5. Example role list

## Raw notes

- Purchaser
    
- Buyer
    
- Fulfillment
    
- Director
    
- Owner
    
- C suite
    
- CEO, CFO, COO
    
- accountant
    
- HR
    

## Expanded role/title seed list

```yaml
example_roles:
  purchasing:
    raw:
      - Purchaser
      - Buyer
    expanded:
      - Purchaser
      - Buyer
      - Purchasing Manager
      - Procurement Manager
      - Procurement Director
      - Sourcing Manager
      - Strategic Sourcing Manager
      - Materials Buyer
      - Category Manager
      - Vendor Manager
      - Supply Chain Buyer

  fulfillment_operations:
    raw:
      - Fulfillment
      - Director
      - Owner
    expanded:
      - Fulfillment Manager
      - Fulfillment Director
      - Operations Manager
      - Director of Operations
      - Warehouse Manager
      - Logistics Manager
      - Distribution Manager
      - General Manager
      - Owner
      - Founder
      - President

  executive:
    raw:
      - C suite
      - CEO
      - CFO
      - COO
    expanded:
      - CEO
      - Chief Executive Officer
      - CFO
      - Chief Financial Officer
      - COO
      - Chief Operating Officer
      - President
      - Founder
      - Managing Partner
      - General Manager
      - VP Operations
      - VP Finance
      - VP Sales

  finance_hr:
    raw:
      - accountant
      - HR
    expanded:
      - Accountant
      - Accounting Manager
      - Controller
      - Finance Director
      - HR Manager
      - Human Resources Manager
      - People Operations Manager
      - Talent Manager
      - Benefits Manager
```

---

# 6. Example industry list

## Raw notes

- IT
    
- Sales / SaaS
    
- Hospitals / Healthcare
    
- Univ. / Education
    
- Sports - golf / tennis
    
- Online Education
    
- Construction
    
- Real Estate
    
- Waste Management
    
- Environmental
    
- Gov't.
    
- Research
    
- Retail
    

## Expanded industry seed list

```yaml
example_industries:
  technology:
    raw:
      - IT
      - Sales / SaaS
    expanded:
      - Information Technology
      - Managed IT Services
      - SaaS
      - B2B SaaS
      - Sales Software
      - Lead Generation Software
      - CRM Software
      - Marketing Automation
      - Cybersecurity
      - Cloud Services

  healthcare:
    raw:
      - Hospitals / Healthcare
    expanded:
      - Hospitals
      - Healthcare Systems
      - Clinics
      - Medical Practices
      - Behavioral Health
      - Senior Care
      - Healthcare Administration
      - Medical Device
      - Health IT

  education:
    raw:
      - Univ. / Education
      - Online Education
    expanded:
      - Universities
      - Colleges
      - K-12 Schools
      - School Districts
      - Online Education
      - EdTech
      - Training Providers
      - Continuing Education
      - Workforce Development

  sports_recreation:
    raw:
      - Sports - golf / tennis
    expanded:
      - Golf Clubs
      - Tennis Clubs
      - Country Clubs
      - Athletic Facilities
      - Sports Training Facilities
      - Recreation Centers
      - Fitness Clubs

  built_environment:
    raw:
      - Construction
      - Real Estate
    expanded:
      - Construction
      - Commercial Real Estate
      - Property Management
      - Building Materials
      - Contractors
      - Developers
      - Facilities Management
      - Architecture
      - Engineering

  environmental_public_sector:
    raw:
      - Waste Management
      - Environmental
      - Gov't.
    expanded:
      - Waste Management
      - Recycling
      - Environmental Services
      - Water Management
      - Municipal Services
      - Government Agencies
      - Public Works
      - Utilities
      - Sustainability

  knowledge_retail:
    raw:
      - Research
      - Retail
    expanded:
      - Research Organizations
      - Academic Research
      - Market Research
      - Retail Stores
      - E-commerce
      - Specialty Retail
      - Consumer Goods
      - Wholesale Distribution
```

---

# 7. Example scope list

## Raw notes

- $500k+ yearly revenue
    
- 100 transactions/mo
    
- ave/lunch average? [unclear]
    
- in the Fortune 500
    
- in Texas
    
- has 300+ days of sun
    
- Nationwide
    
- New Jersey
    
- Sandoval County
    

## Expanded scope seed list

```yaml
example_scopes:
  revenue_and_volume:
    raw:
      - "$500k+ yearly revenue"
      - "100 transactions/mo"
      - "ave/lunch average? [unclear]"
    expanded:
      - annual_revenue_minimum
      - monthly_transaction_minimum
      - average_ticket_size
      - average_order_value
      - customer_volume
      - location_volume
      - purchasing_volume

  company_size:
    raw:
      - "in the Fortune 500"
    expanded:
      - Fortune 500
      - enterprise
      - mid-market
      - small business
      - franchise
      - multi-location
      - employee_count_threshold
      - revenue_threshold

  geography:
    raw:
      - Texas
      - Nationwide
      - New Jersey
      - Sandoval County
    expanded:
      - city
      - county
      - state
      - region
      - national
      - nationwide
      - local market
      - metro area
      - rural area
      - service territory

  environmental_conditions:
    raw:
      - "has 300+ days of sun"
    expanded:
      - climate condition
      - high sun exposure
      - arid region
      - high heat
      - water scarcity
      - seasonal demand
      - weather-dependent market
```

---

# 8. Structured interpretation

This note defines the earliest version of a targeting taxonomy.

The system should treat a lead-generation request as a combination of:

```yaml
lead_request_components:
  A_individual:
    description: "Who should be contacted?"
    examples:
      - buyer
      - purchaser
      - HR manager
      - COO
      - IT director

  B_industry:
    description: "What type of organization should they work for?"
    examples:
      - SaaS
      - healthcare
      - education
      - construction
      - retail

  C_scope:
    description: "Where and under what constraints should they be found?"
    examples:
      - Texas
      - Sandoval County
      - Fortune 500
      - $500k+ annual revenue
      - 100 transactions/month
```

---

# 9. Useful next transformation

This page should become the foundation for:

```yaml
recommended_next_docs:
  - REQUEST_SCHEMA.md
  - LEAD_TARGETING_TAXONOMY.md
  - ROLE_EXPANSION_DICTIONARY.md
  - INDUSTRY_EXPANSION_DICTIONARY.md
  - SCOPE_FILTER_DICTIONARY.md
```
