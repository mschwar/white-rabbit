---
title: "Lead Generation Brainstorm - Photo 03 - Data Sources"
doc_type: "handwritten_note_transcription"
photo_index: 3
markdown_file: "03-data-sources.md"
source_image: "03-data-sources.heic"
original_photo_filename: "IMG_1062.HEIC"
transcription_source_image: "2CB3AADF-9B4B-4B13-8411-4C1CE205515E.jpeg"
status: "raw_transcription_plus_expansion"
purpose: "Map possible public data sources for lead generation by content type and format."
core_concept: "Lead data can be discovered across websites, articles, social media, and multimedia sources, each with different file formats and extraction strategies."
primary_fields:
  - data_sources
  - file_formats
  - websites
  - articles
  - social_media
  - multimedia
data_quality_notes:
  - "The page appears to be a source matrix."
  - "Some entries are abbreviated; expansions are added below the raw transcription."
---

# Lead Generation Brainstorm - Photo 03 - Data Sources

## 1. Raw table transcription

| Data source category | Formats / notes | Examples |
|---|---|---|
| Websites | URL, HTML, CSV, TXT | org website, gov website, tax website, the org, conferences |
| Articles | PDF, TXT, MD, HTML | news, newsletters, magazines, publications, journals |
| Social media | URL | LinkedIn, FB/Insta, X |
| Multimedia | audio, video | YouTube |

---

# 2. Cleaned-up source matrix

```yaml
data_sources:
  websites:
    formats:
      - url
      - html
      - csv
      - txt
    examples:
      - organization_website
      - government_website
      - tax_website
      - company_website
      - conference_website
      - association_directory
      - staff_directory
      - chamber_of_commerce_directory
      - procurement_directory

  articles:
    formats:
      - pdf
      - txt
      - markdown
      - html
    examples:
      - news
      - newsletters
      - magazines
      - publications
      - journals
      - trade_publications
      - press_releases
      - case_studies
      - industry_reports

  social_media:
    formats:
      - url
      - public_profile
      - public_post
    examples:
      - LinkedIn
      - Facebook
      - Instagram
      - X
      - company_social_page
      - executive_profile
      - professional_announcement

  multimedia:
    formats:
      - audio
      - video
      - transcript
      - captions
      - description_text
    examples:
      - YouTube
      - webinars
      - podcasts
      - conference_recordings
      - product_demos
      - interviews
```

---

# 3. Data dictionary

|Field|Type|Description|Example|
|---|--:|---|---|
|`source_category`|string|Broad source class|`websites`|
|`source_format`|string/list|Format to parse|`html`, `pdf`, `csv`|
|`source_name`|string|Specific source or platform|`LinkedIn`|
|`source_url`|URL|URL where data was found|`https://example.com/team`|
|`source_reliability`|integer|Confidence in source, 1-5|`5`|
|`extraction_method`|string|How the data is extracted|`html_parse`, `pdf_parse`, `manual_review`|
|`lead_fields_available`|list|Fields likely available from source|`name`, `title`, `email`|
|`requires_login`|boolean|Whether source requires authentication|`false`|
|`allowed_for_mvp`|boolean|Whether to include in first version|`true`|

---

# 4. Expanded source hierarchy

The system should prioritize sources by reliability and ease of extraction.

```yaml
source_priority:
  tier_1_official_sources:
    reliability: 5
    description: "Official sources controlled by the target organization or public institution."
    examples:
      - company_team_page
      - company_contact_page
      - staff_directory
      - leadership_page
      - government_directory
      - procurement_office_page
      - university_department_directory

  tier_2_structured_directories:
    reliability: 4
    description: "Directories or listings maintained by recognized organizations."
    examples:
      - association_member_directory
      - chamber_of_commerce_directory
      - conference_speaker_directory
      - conference_sponsor_page
      - trade_group_directory
      - professional_license_directory

  tier_3_publications:
    reliability: 3
    description: "Mentions in articles, newsletters, journals, press releases, or trade publications."
    examples:
      - trade_magazine_article
      - local_news_article
      - press_release
      - journal_article
      - industry_report
      - company_case_study

  tier_4_social_profiles:
    reliability: 3
    description: "Public social media or professional profiles."
    examples:
      - LinkedIn_profile
      - LinkedIn_company_page
      - X_profile
      - Facebook_business_page
      - Instagram_business_page

  tier_5_multimedia:
    reliability: 2
    description: "Audio/video sources that may contain useful names, titles, or organizations but require transcription or manual review."
    examples:
      - YouTube_interview
      - podcast_episode
      - webinar
      - conference_recording
```

---

# 5. Source-specific extraction notes

## Websites

Best for:

- company names
    
- locations
    
- staff names
    
- titles
    
- phone numbers
    
- contact forms
    
- official email addresses
    

Common pages to search:

```yaml
website_pages_to_check:
  - /about
  - /team
  - /staff
  - /leadership
  - /contact
  - /directory
  - /procurement
  - /vendors
  - /locations
  - /departments
  - /management
```

Search patterns:

```text
site:example.com "Purchasing Manager"
site:example.com "Procurement"
site:example.com "Director of Operations"
site:example.com "Contact"
site:example.com "Staff"
```

---

## Articles

Best for:

- executive names
    
- company events
    
- expansions
    
- funding announcements
    
- hiring announcements
    
- conference participation
    
- thought leadership
    
- market context
    

Possible extraction fields:

```yaml
article_extractable_fields:
  - person_name
  - person_title
  - company_name
  - company_location
  - quote_context
  - article_date
  - source_publication
  - source_url
```

---

## Social media

Best for:

- title verification
    
- current employment
    
- role/function clues
    
- company activity
    
- contact routing
    

Caution:

```yaml
social_media_cautions:
  - "Avoid private personal information."
  - "Prefer business contact information."
  - "Do not rely on social profiles alone when official company sources exist."
  - "LinkedIn can help validate titles but may be difficult to scrape directly."
```

---

## Multimedia

Best for:

- founder-led companies
    
- niche industries
    
- podcasts and webinars
    
- conference speakers
    
- expert interviews
    

Later-stage use cases:

```yaml
multimedia_later_stage:
  - transcribe_youtube_video
  - extract_speaker_names
  - extract_company_names
  - extract_titles_from_descriptions
  - extract_emails_from_show_notes
  - identify_buying_signals_from_interviews
```

---

# 6. MVP source inclusion

For the first version, prioritize these:

```yaml
mvp_sources:
  include:
    - company_websites
    - staff_directories
    - leadership_pages
    - contact_pages
    - association_directories
    - conference_pages
    - government_directories
    - trade_publication_articles
    - press_releases

  defer:
    - LinkedIn_deep_scraping
    - Facebook_scraping
    - Instagram_scraping
    - X_scraping
    - YouTube_transcription
    - podcast_transcription
```

---

# 7. Output implications

Each lead should preserve source provenance.

```yaml
source_provenance_fields:
  - source_category
  - source_name
  - source_url
  - source_date
  - extraction_date
  - evidence_text
  - reliability_score
  - source_notes
```

---

# 8. This document should become

```yaml
recommended_next_docs:
  - SOURCE_STRATEGY.md
  - SCRAPING_SOURCE_MATRIX.md
  - SOURCE_RELIABILITY_SCORING.md
  - PUBLIC_DATA_COMPLIANCE_NOTES.md
```
