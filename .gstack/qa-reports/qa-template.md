# QA Report Template

**Branch:** `feat/buildout-NN-short-slug`
**Date:** YYYY-MM-DD
**Agent:** <model name>
**Required tiers:** <e.g., 1–4, 5–6, 1–6>
**Rubric:** `docs/qa-rubric.md`

---

## Tier 1 — Multi-vertical content check

> Required for any change touching `orchestrator.py`, `models.py`, prompts, or scoring.
> Skip with justification if N/A.

### Vertical A: <query>
- [ ] Lead 1 name:
- [ ] Lead 1 email:
- [ ] Lead 1 explanation:
- [ ] Lead 2 name:
- [ ] Lead 2 email:
- [ ] Lead 2 explanation:

### Vertical B: <query>
- [ ] Lead 1 name:
- [ ] Lead 1 email:
- [ ] Lead 1 explanation:
- [ ] Lead 2 name:
- [ ] Lead 2 email:
- [ ] Lead 2 explanation:

### Vertical C: <query>
- [ ] Lead 1 name:
- [ ] Lead 1 email:
- [ ] Lead 1 explanation:
- [ ] Lead 2 name:
- [ ] Lead 2 email:
- [ ] Lead 2 explanation:

### Regression: K-12 Albuquerque (if prompt changed)
- [ ] Leads still return
- [ ] Explanation may contain VoIP (allowed for this vertical)

---

## Tier 2 — Persistence read-back

> Required for Full / Batch / storage changes.

- [ ] Run ID:
- [ ] SQL lead count:
- [ ] UI lead count:
- [ ] Counts match:
- [ ] Scalar scores match UI:
- [ ] FK integrity verified:

```sql
-- Paste truncated SQL output (first 3 rows)
```

---

## Tier 3 — CSV export inspection

> Required if export logic changed.

- [ ] Header row matches schema:
- [ ] Row count > 0:
- [ ] `not_available` absent:
- [ ] No escape errors:
- [ ] Dates parseable:

```csv
-- Paste first 3 lines of CSV
```

---

## Tier 4 — Prompt validation

> Required if `orchestrator.py` or prompts changed.

- [ ] Diff reviewed — no vertical re-introduction:
- [ ] Integration tests pass (or skipped with reason):
- [ ] Cross-vertical responses clean:

```diff
-- Paste first 20 lines of prompt diff
```

---

## Tier 5 — Failure modes

> Required weekly.

- [ ] Tavily down → specific error_code and friendly message:
- [ ] OpenAI rate-limited → specific error_code and friendly message:
- [ ] Sandbox cap hit → 429 with preserved partial state:

---

## Tier 6 — UI smoke

> Required every run.

- [ ] Zero console errors:
- [ ] Buttons clickable:
- [ ] Empty states render:
- [ ] Loading states show progress:
- [ ] Responsive at 1280×800:

### Screenshots

| Page | Path |
|------|------|
| Login | `.gstack/qa-reports/screenshots/buildout-NN-login.png` |
| Scout | `.gstack/qa-reports/screenshots/buildout-NN-scout.png` |
| Recipes | `.gstack/qa-reports/screenshots/buildout-NN-recipes.png` |
| Batch | `.gstack/qa-reports/screenshots/buildout-NN-batch.png` |

---

## What we tried to break

> Adversarial section — describe negative-result scenarios attempted.

- <scenario 1>
- <scenario 2>

---

## Sign-off

- [ ] All required tiers pass.
- [ ] Screenshots saved to `.gstack/qa-reports/screenshots/`.
- [ ] This report committed on the feature branch.
