# Persistence Readback

Full-mode browser run:

- Query: `Healthcare IT directors in Phoenix`
- Location: `Phoenix`
- Export: `audits/raw/zero-trust-2026-05-10/live/full-export-healthcare.csv`
- Run ID: `fec62061-9da8-469a-9455-d62c20852f19`

Run/lead count check:

```text
fec62061-9da8-469a-9455-d62c20852f19|3|3
```

Lead scalar readback:

| name | title | organization | fit | evidence | contact | gate_passed |
| --- | --- | --- | ---: | ---: | ---: | --- |
| Susan Bunker | Executive VP/CTO | Phoenix MedCom | 1 | 1 | 0 | false |
| Terrence Johnson | President & CEO | Phoenix Health Care Management Services, Inc | 1 | 1 | 0 | false |
| Mike Mehta | President & CEO | Phoenix Healthcare Solutions, LLC | 1 | 1 | 0 | false |

Audit interpretation:

- Persistence matches the exported row count.
- The stored data proves the product can persist validation context.
- It also proves the current score semantics still create false confidence: all three rows show max fit/evidence despite being non-usable and mostly not the requested IT-director persona.
