# Attachment Extract - Retail IT Leads for REPO.docx

## Clean Source Facts

- Source file was a Codex terminal transcript pasted into DOCX.
- Connector parse reported 58 pages; XML extraction found 859 non-empty paragraphs.
- Initial ask: retail IT directors / technology contacts for Target, Walmart, and Lowes in Arizona, New Mexico, and North Carolina, with state-separated tabs/pages and fields such as name, email, phone, company, and title.
- Agent constraint recorded in transcript: no personal direct emails or cell numbers for individual employees; use public company leaders and official corporate channels where appropriate.
- Later pivot: broaden to public retail technology and digital leaders nationwide to approach 75 rows.
- Final national counts recorded: 77 total rows, 59 verified_current, 18 older_public.
- Workbook sheets recorded: Verified_Current, Older_Public, README.

## Output Shapes Visible In Transcript

State workbook shape: state, company, industry, contact scope, name, title, direct email, direct phone, public corporate phone/email, profile URL, corporate contact URL, state presence source, notes.

National retail leader shape: verification_tier, name, title, company, retail_segment, official_source_url, public_company_contact_url, public_company_phone, public_company_email, status_note.

## Public Row Examples Visible In Builder Additions

- Jason Bonfig - SEVP, Chief Customer, Product and Fulfillment Officer, Best Buy (verified_current); source: https://corporate.bestbuy.com/our-leadership/
- Arianne Parisi - Chief Digital Officer, Kohl's (verified_current); source: https://corporate.kohls.com/bio-arianneparisi
- Greg Fancher - Executive Vice President and Chief Information Technology Officer, PetSmart (verified_current); source: https://www.petsmartcorporate.com/our-leadership/greg-fancher/
- Guillaume Ledieu - Chief Technology Officer, REI Co-op (verified_current); source: https://www.rei.com/about-rei/leadership
- Rick Williams - Senior Vice President, Information Technology, Ace Hardware (verified_current); source: https://newsroom.acehardware.com/executive-bios/
- Bill Kiss - Vice President, Digital and Retail Strategy and Innovation, Ace Hardware (verified_current); source: https://newsroom.acehardware.com/executive-bios/
- Sarah Clarke - Executive Vice President, Chief Supply Chain, Technology & International Officer, American Eagle Outfitters (verified_current); source: https://www.aeo-inc.com/leadership/
- Varadheeswaran Chennakrishnan - Executive Vice President, Chief Information Officer, Burlington Stores (verified_current); source: https://www.burlingtoninvestors.com/static-files/6d1ae171-740c-41ef-a6b3-12e78ff4353c
- Larry Kraus - Senior Vice President, Chief Information Officer, Ollie's Bargain Outlet (verified_current); source: https://investors.ollies.us/executive-officers
- Carlo Pochintesta - Chief Information Officer, Barnes & Noble (verified_current); source: https://www.barnesandnobleinc.com/management-overview/
- Dave Hayne - Chief Technology Officer and President of Nuuly, Urban Outfitters (verified_current); source: https://www.urbn.com/who-we-are/senior-leadership
- Mike Hite - Chief Technology Officer, Saks Global (verified_current); source: https://www.saksglobal.com/operating-leadership?item=79
- Raghu Sagi - Executive Vice President, Chief Information & Technology Officer, Carter's (verified_current); source: https://ir.carters.com/management/raghu-sagi
- Martin Christopher - Chief Technology Officer, Lands' End (verified_current); source: https://investors.landsend.com/corporate-governance/management
- Karen Etzkorn - Chief Information Officer, QVC Group (verified_current); source: https://www.qvcgrp.com/newsroom/executive/karen-etzkorn/
- David Lauren - Chief Branding and Innovation Officer, Ralph Lauren (verified_current); source: https://corporate.ralphlauren.com/leadership
- Siobhan McFeeney - Chief Technology and Digital Officer, Kohl's (older_public); source: https://corporate.kohls.com/news/kohls-moves-to-cloud-centric-stores-it-model-to-drive-speed-and-efficiency
- Matt Francis - Chief Technology Officer, GameStop (older_public); source: https://investor.gamestop.com/news-releases/news-details/2021/GameStop-Appoints-Chief-Technology-Officer-02-03-2021/default.aspx
- Michael Kobayashi - Group Executive Vice President, Supply Chain, Merchant Operations, and Technology, Ross Stores (older_public); source: https://investors.rossstores.com/news-releases/news-release-details/ross-stores-announces-operational-leadership-changes

These examples are not asserted as current truth by this packet. They are extracted from the attachment transcript and should be revalidated before becoming executable benchmark rows. The transcript later records additional seed-row fixes, including the Caseys source-currency correction, that are represented in the report and fixture candidates.
