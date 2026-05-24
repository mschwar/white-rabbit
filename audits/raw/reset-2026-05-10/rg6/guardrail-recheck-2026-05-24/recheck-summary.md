# RG6 Guardrail False-Positive Production Recheck

**Collected at:** 2026-05-24T01:11:10Z  
**Production alias:** https://white-rabbit-ten.vercel.app/  
**Scope:** Ops/recheck only; no Prompt A/B/C feature work.

## Query

Arizona K-12 VoIP and network technology decision makers: Mesa Public Schools; Chandler Unified School District; Peoria Unified School District; Gilbert Public Schools; Deer Valley Unified School District; Paradise Valley Unified School District

## Result

PASS for the narrow guardrail remediation recheck.

The production `/api/scout` response returned HTTP 200 and omitted `query_guardrail` for the remediation query.

Expected pass condition was met because the response either omits `query_guardrail` or reports `query_guardrail.status=clear`.

## Evidence

- Local `main` HEAD: `73860b59b64c214d92664c8e8d72a5f1f9bb6c1d`.
- `73860b5` is an ancestor of local `HEAD`.
- `origin/main` advertised `73860b59b64c` by `git ls-remote`.
- `docs/reset-current-assignment.json` still had `current_prompt: none` before the recheck and no downstream Prompt A/B/C assignment was valid.
- Production auth succeeded: login status 200, authenticated home status 200.
- Production Scout response: HTTP 200, 104.301 seconds, 11 rows, run ID `5f560f5f-fbfe-43f3-868c-6d0cd055bd27`.
- Guardrail field: `query_guardrail_present=false`, `query_guardrail=null`.

## Product Gate Note

RG6 remains held/product-red. This recheck clears only the narrow guardrail false-positive blocker. It does not clear remaining RG6 northstar blockers around lead quality/contact yield, sampled precision, or timed unassisted operator evidence.

## Files

- `metadata.json`
- `web-auth-flow.json`
- `web-scout-arizona-k12-guardrail-recheck.json`
- `decision-inputs.json`
- `local-main-and-assignment-proof.txt`
- `collect_rg6_guardrail_recheck.py`
