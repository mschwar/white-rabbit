# 03 - Test Coverage

**Verdict:** mechanically broad, product-thin.

## Mechanical Baseline

| Suite | Result |
| --- | --- |
| Core isolated env | `94 passed, 6 skipped` |
| API with matching internal token | `43 passed` |
| Web Vitest | `13 files, 29 tests` |
| Web build | pass |

Those results prove the repo is buildable. They do not prove White Rabbit is usable.

## Coverage Gaps

The web tests use fake rows such as `Jane Smith`, `Noisy Lead`, `Example Corp`, and `Ghost District`. They validate rendering and bucket placement, not whether search output is correct. The export test only checks that a download link appears and copy says validation context is included.

The core tests make the new model contract pass in isolation, but the live benchmark still produced 0 usable leads and one 503 parse crash. That means the tests cover intended object shapes better than real query behavior.

The API tests are brittle around environment setup. A plain `uv run pytest tests -q` failed with blanket 401s until `WR_API_INTERNAL_TOKEN=test-internal-token` was set to match the test client's header. Core has a similar environment trap: if `OPENAI_API_KEY` is present, the missing-key test hits OpenAI instead of the missing-key branch.

## Missing Product Tests

- Thomas exact Arizona prompt as a live or replayable golden fixture with 8 target-account coverage.
- Lee commodity-buyer prompt with multiple account coverage and direct-person preference.
- A row-level duplicate/conflict test, e.g. same person assigned to incompatible organizations.
- A "role emitted as name" salvage test so one bad LLM candidate cannot 503 the whole run.
- Export ordering test against Lee's requested CRM-first column order.
- End-to-end query-to-export test that opens a real saved CSV and checks usable/noisy separation.

## Required Reset

Keep the current unit tests, but stop treating them as gate evidence. Add a golden replay harness that stores:

- input prompt,
- target accounts/persona,
- source snapshots or deterministic fixtures,
- expected category per target,
- accepted/rejected contact evidence,
- export rows.

Pass means the exported rows satisfy the operator task, not that React rendered cards.
