<!-- superskills-workflow-rule -->
## Superskills Developer Workflow

Read .gemini/superskills-repo/DEVELOPER_WORKFLOW.md to understand how to use superskills commands together effectively — parallel agents, vertical slices, quality pipeline, performance optimization, and shipping workflow.

## Testing

- Web unit tests: `cd apps/web && npm run test`
- Web E2E tests: `cd apps/web && npm run test:e2e`
- Reference: [TESTING.md](./TESTING.md)

Test expectations:
- 100% test coverage is the goal — tests make vibe coding safe.
- When writing new functions, write a corresponding test.
- When fixing a bug, write a regression test.
- Never commit code that makes existing tests fail.

<!-- repomap-rule -->
## REPOMAP.md

REPOMAP.md at the project root is a structural outline of the codebase (files, classes, functions, types). Read it when the task benefits from a map: broad exploration, "where does X live", cross-module refactors, onboarding to an unfamiliar area, or planning changes that touch multiple files. Skip it for narrow lookups where Grep or a known file path is faster — a single symbol search doesn't need the whole map.
