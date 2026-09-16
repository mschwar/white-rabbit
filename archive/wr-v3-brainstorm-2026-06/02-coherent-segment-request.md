---
title: "Lead Generation Brainstorm - Photo 02 - Coherent Segment Request"
doc_type: "handwritten_note_transcription"
photo_index: 2
markdown_file: "02-coherent-segment-request.md"
source_image: "02-coherent-segment-request.heic"
original_photo_filename: "IMG_1061.HEIC"
transcription_source_image: "B055C50D-4EFF-475A-B670-1618D590E996.jpeg"
status: "raw_transcription_plus_expansion"
purpose: "Describe what a coherent lead-generation request should produce: an effective segment of professionals within an industry who have decision authority."
core_concept: "Create a coherent segment of professionals who have authority to make decisions, especially fast-buying-power contacts."
primary_fields:
  - segment_definition
  - contact_count
  - professional_position
  - industry
  - geography
  - contact_information
  - related_titles
data_quality_notes:
  - "Handwriting is partially difficult to read; uncertain words are marked with [unclear]."
  - "The phrase 'especially fast buying power' appears to mean priority should be given to contacts with clear authority and short decision paths."
---

# Lead Generation Brainstorm - Photo 02 - Coherent Segment Request

## 1. Raw transcription

```text
- Create a coherent segment to hone in on

an effective segment of professionals within an

industry who have the authority to make decisions

(especially fast buying power)

- number of desired contacts

- in a certain professional position

- within an industry

- within a geographic area

- looking for direct contact info currently in use

- open to similarly related titles/positions who
  likely have the same job function.
```

---

# 2. Cleaned-up version

Create a coherent lead-generation segment that narrows in on an effective group of professionals within a specific industry who have the authority to make decisions, especially people with clear and fast buying power.

A complete request should specify:

1. The number of desired contacts.
    
2. The target professional position or job function.
    
3. The target industry or business type.
    
4. The geographic area or market scope.
    
5. The desired type of direct contact information.
    
6. Whether related titles or equivalent job functions should be included.
    

---

# 3. Embedded data fields

```yaml
coherent_segment_request:
  objective: "Generate a focused list of professionals likely to have decision-making authority within a target industry and geography."
  required_inputs:
    contact_count:
      description: "How many leads or contacts the user wants."
      examples:
        - 25
        - 50
        - 100
        - 500

    professional_position:
      description: "The role, title, seniority, or job function to target."
      examples:
        - Purchaser
        - IT Director
        - Director of Marketing
        - COO
        - Social Media Manager
        - Materials Buyer

    industry:
      description: "The business vertical, sector, or organization type."
      examples:
        - retail
        - education
        - SaaS
        - healthcare
        - construction
        - agriculture
        - landscaping supply

    geographic_area:
      description: "The location or market boundary."
      examples:
        - Utah
        - Texas
        - Northwest USA
        - New Jersey
        - Sandoval County
        - nationwide

    contact_info_requirement:
      description: "The type of contact information requested."
      examples:
        - direct email
        - phone number
        - LinkedIn profile
        - contact page
        - company website
        - public staff directory listing

    related_titles_allowed:
      description: "Whether the system can include similar titles with the same job function."
      default: true
```

---

# 4. Data dictionary

|Field|Type|Required?|Description|Example|
|---|--:|--:|---|---|
|`contact_count`|integer|Yes|Desired number of contacts|`100`|
|`professional_position`|string|Yes|Target job title, role, or function|`Purchasing Manager`|
|`industry`|string|Yes|Target industry, sector, or vertical|`landscape supply`|
|`geographic_area`|string/list|Yes|Target market or region|`Northwest USA`|
|`contact_info_requirement`|list|No|Desired contact info fields|`email`, `phone`, `LinkedIn`|
|`related_titles_allowed`|boolean|No|Whether to include adjacent titles|`true`|
|`decision_authority_required`|boolean|No|Whether contact must plausibly influence buying|`true`|
|`freshness_required`|boolean|No|Whether info must appear current|`true`|

---

# 5. Expanded concept: decision authority

The note emphasizes people who have authority to make decisions. This should become an explicit lead-scoring dimension.

```yaml
decision_authority_levels:
  high:
    description: "Likely has direct buying or approval power."
    examples:
      - Owner
      - Founder
      - CEO
      - COO
      - CFO
      - President
      - General Manager
      - Director of Operations
      - Procurement Director

  medium:
    description: "Likely influences buying or can route the request internally."
    examples:
      - Purchasing Manager
      - Buyer
      - Department Manager
      - Facilities Manager
      - IT Manager
      - Marketing Manager
      - HR Manager

  low:
    description: "May be relevant but likely does not control budget."
    examples:
      - Coordinator
      - Assistant
      - Associate
      - Specialist
      - Analyst
      - Intern
```

---

# 6. Expanded concept: related titles

The system should not search only for exact user-provided titles. It should expand by job function.

```yaml
related_title_expansion_rules:
  purchaser:
    include:
      - Buyer
      - Purchasing Manager
      - Procurement Manager
      - Materials Buyer
      - Sourcing Specialist
      - Vendor Manager
      - Supply Chain Manager
      - Inventory Manager
      - Operations Manager
    exclude_unless_needed:
      - Sales Representative
      - Customer Service
      - Administrative Assistant

  it_director:
    include:
      - IT Director
      - Director of Information Technology
      - Technology Director
      - CIO
      - Chief Information Officer
      - IT Manager
      - Systems Manager
      - Network Administrator
    exclude_unless_needed:
      - Help Desk Technician
      - Junior Developer
      - Student Worker

  marketing_director:
    include:
      - Director of Marketing
      - Marketing Manager
      - VP Marketing
      - Head of Marketing
      - Growth Marketing Manager
      - Demand Generation Manager
      - Brand Manager
    exclude_unless_needed:
      - Marketing Assistant
      - Social Media Intern
```

---

# 7. Proposed canonical request format

```text
Give me [CONTACT_COUNT] contacts for [PROFESSIONAL_POSITION / JOB_FUNCTION] in the [INDUSTRY] industry within [GEOGRAPHIC_AREA]. Include related titles with the same job function. Prefer people with decision-making authority and currently available public contact information.
```

## Example

```text
Give me 100 contacts for purchasers and procurement managers in the landscape supply industry within the Northwest USA. Include related titles with the same job function. Prefer people with decision-making authority and currently available public contact information.
```

---

# 8. Suggested automation interpretation

```yaml
automation_interpretation:
  input_type: "natural_language_request"
  output_type: "structured_lead_segment"
  pipeline_steps:
    - parse_contact_count
    - extract_role_or_job_function
    - expand_related_titles
    - extract_industry
    - expand_industry_terms
    - extract_geography
    - expand_geography_terms
    - define_contact_info_requirements
    - set_decision_authority_filter
    - generate_search_queries
```

---

# 9. This document should become

```yaml
recommended_next_docs:
  - COHERENT_REQUEST_PATTERN.md
  - REQUEST_INTERPRETER_SPEC.md
  - TITLE_EXPANSION_RULES.md
  - DECISION_AUTHORITY_SCORING.md
```
