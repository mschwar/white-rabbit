# RG3 Post-R09L Command Output Index

This directory keeps raw command outputs for the post-R09L RG3 Prompt C audit.

| File | Purpose |
| --- | --- |
| `git-status-initial.txt` | Initial branch and worktree state. |
| `merge-proof.txt` | `git merge-base --is-ancestor` proof for R07-R09L against `origin/rebuild/validated-leads-loop`. |
| `gate-state-proof.txt` | Gate table/status proof that RG3 was ready and not already advanced before this audit. |
| `git-diff-check-before-report.txt` | Whitespace check before audit report edits. |
| `core-rg3-suite.txt` | Core RG3 regression suite output. |
| `api-suite.txt` | API regression suite output. |
| `api-health-8027.*` | Live `/health` HTTP headers/body/status. |
| `api-readiness-8027.*` | Live `/readiness` HTTP headers/body/status and compact summary. |
| `source-assisted-proof-no-token.*` | Protected route rejection without internal token. |
| `source-assisted-proof-token.*` | Protected route success with internal token. |
| `source-assisted-proof-live-summary.json` | Compact source-assisted proof counts. |
| `source-assisted-proof-sampled-rows.json` | Ten ready row samples with field support. |
| `source-assisted-proof-manual-lookup-rows.json` | Manual-lookup row samples with blockers and next actions. |
| `private-contact-redaction-check.txt` | Redaction check for private contact values. |
| `r09a-live-summary.json` | Prior autonomous broad Scout caveat summary. |
| `r09j-readiness-summary.json` | R09J bounded-readiness artifact summary. |
| `r09k-sandbox-timeout-summary.json` | R09K structured timeout artifact summary. |
