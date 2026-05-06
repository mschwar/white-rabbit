# Testing — White Rabbit

100% test coverage is the key to great vibe coding. Tests let you move fast, trust your instincts, and ship with confidence — without them, vibe coding is just yolo coding. With tests, it's a superpower.

## Frameworks

### Web (`apps/web`)
- **Unit/Integration:** [Vitest](https://vitest.dev/) + [React Testing Library](https://testing-library.com/docs/react-testing-library/intro/)
- **E2E:** [Playwright](https://playwright.dev/)

## Commands

### Web (`apps/web`)
```bash
cd apps/web
npm run test      # Run unit tests
npm run test:e2e  # Run E2E tests
```

## Conventions

- **Unit tests:** Place in `__tests__` directories adjacent to the code they test. Use `.test.tsx` or `.test.ts`.
- **E2E tests:** Place in the `e2e` directory at the app root. Use `.spec.ts`.
- **Naming:** Match the component or module name (e.g., `page.tsx` -> `page.test.tsx`).
- **Assertions:** Use `expect` from Vitest (globals enabled) or Playwright.
