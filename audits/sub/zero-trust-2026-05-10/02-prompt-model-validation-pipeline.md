# 02 - Prompt / Model / Validation Pipeline

**Verdict:** partially rebuilt, still untrustworthy.

## What Is Real

The current code has a better contract than the original sprint code:

- Candidate categories exist in `packages/core/src/core/models.py`.
- Field-level validation records exist for name, title, organization, email, phone, and source.
- The server recomputes `gate_passed` in `packages/core/src/core/orchestrator.py`.
- Guardrails can block consumer/privacy-sensitive queries.

## What Is Still Not Real Enough

Validation is mostly literal single-source text matching. `packages/core/src/core/source_validation.py` fetches one `source_url`, normalizes text, and checks whether each claimed field string appears. It does not prove current employment, does not reconcile multiple sources, does not validate a district/account roster, and does not derive or verify phone numbers. A LinkedIn page can support a name and organization from metadata while leaving the title unsupported.

The pipeline still depends on an LLM to convert search-result snippets into structured candidates in one shot. When the model emits a bad union candidate, as in the manufacturing Detroit run, response parsing fails and the API returns 503 instead of salvaging valid candidates or returning a `failed` row.

The scores are still largely model optimism. In the Full-mode healthcare export, three rows had `fit_score=1.00` and `evidence_score=1.00`, while every row was non-usable and contact score was zero. UI labels then displayed those as Evidence 100%, which is technically non-gated but product-misleading.

## Live Contradictions

- Lee commodity row Erik Davis: `email_status=verified_found`, but validation for name/title/org/email/source all failed because the source returned 403.
- Healthcare Full export: Mike Mehta and Terrence Johnson are CEOs, not IT directors, but fit/evidence remained maxed.
- Finance benchmark: Khalil Jackson appears twice with conflicting organizations, which the validator did not reconcile.
- Manufacturing benchmark: role-as-name caused a whole-query `LeadList` validation exception.

## Code Smells

- `apps/web/src/lib/scout.ts` still types `ScoutLead.email_status` as legacy `Found | Deduced | Missing`.
- Frontend tests still feed `email_status: 'Found'` and fake `Jane Smith` rows.
- Phone exists in validation shape but there is no real phone field on `Lead`; export always emits blank phone.
- `source_url` is a single string on a candidate, but real validation needs source-per-field and cross-source disagreement handling.

## Required Reset

Move from "LLM extracts final leads" to "system collects target-account evidence, then validates fields":

1. Planner decomposes named accounts and simple vertical queries.
2. Source collector stores candidate pages/snippets per account.
3. Candidate builder proposes rows but cannot pass them.
4. Validator owns person/title/org/contact evidence and can emit explicit `not_found`.
5. LLM may summarize evidence, but must not be the source of truth for scores or gate status.
