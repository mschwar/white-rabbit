# Arizona K-12 Workbook Readback

**Local artifact:** `/Users/mschwar/Downloads/district_it_contacts_by_state_20260424_172807.xlsx`
**Sheets:** `Texas`, `Arizona`, `Nevada`
**Use:** corroborating local artifact only. This workbook is not treated as complete ground truth.

Selected Arizona target rows:

| District | Website | Main Phone | Primary Contact Name | Primary Contact Title | Primary Contact Email | Primary Contact Phone | Status | Source |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Mesa Unified District | `http://www.mpsaz.org/` | `480-472-0200` |  | Technology Department |  | `480-472-0200` | likely_department | `http://www.mpsaz.org/technology` |
| Chandler Unified District #80 | `http://www.cusd80.com` | `480-812-7000` |  | Technology Department |  | `480-812-7000` | likely_department | `https://www.cusd80.com/departments/technology/student-and-parent-links` |
| Peoria Unified School District | `https://www.peoriaunified.org` | `623-486-6000` |  |  |  | `623-486-6000` | not_found | `https://www.peoriaunified.org` |
| Gilbert Unified District | `http://www.gilbertschools.net` | `480-497-3300` |  | Chief Technology Officer |  | `480-497-3300` | likely_named | `https://www.gilbertschools.net/contact` |
| Deer Valley Unified District | `https://dvusd.org` | `623-445-5000` | Brian Boone | Chief Information Officer | Brian Boone | `602-467-5152` | verified | `https://www.dvusd.org/departments/information-services-and-technology` |
| Paradise Valley Unified District | `http://www.pvschools.net/` | `602-449-2000` |  |  |  | `602-449-2000` | not_found | `http://www.pvschools.net/` |
| Dysart Unified District | `http://www.dysart.org/` | `623-876-7000` |  |  |  | `623-876-7000` | not_found | `http://www.dysart.org/` |
| Maricopa Unified School District | `http://www.musd20.org` | `520-568-5100` |  | Technology Department |  | `(520) 568-5100 x1090` | likely_named | `https://www.musd20.org/departments/technology` |

Audit interpretation:

- The local workbook itself contains mixed-quality rows and department/main-line fallbacks.
- A correct product must represent this uncertainty directly as `person_lead`, `organization_only`, `not_found`, or `failed`, not force every named account into a person row.
- The live v2 benchmark returned only 3 of the 8 named districts and did not produce CRM-usable contact detail.
