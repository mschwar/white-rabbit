import { defineConfig, devices } from '@playwright/test';

const port = Number(process.env.PORT ?? 3000);
const sharedPassword = process.env.WR_SHARED_PASSWORD ?? 'codex-test-password';
const sessionSecret = process.env.WR_SESSION_SECRET ?? 'codex-test-session-secret';
const apiInternalToken = process.env.WR_API_INTERNAL_TOKEN ?? 'test-internal-token';

export default defineConfig({
  testDir: './e2e',
  fullyParallel: false,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  workers: 1,
  reporter: 'html',
  use: {
    baseURL: `http://127.0.0.1:${port}`,
    trace: 'on-first-retry',
  },
  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] },
    },
  ],
  webServer: {
    command: `WR_SHARED_PASSWORD=${sharedPassword} WR_SESSION_SECRET=${sessionSecret} WR_API_INTERNAL_TOKEN=${apiInternalToken} sh -c "npm run build && npm run start -- --hostname 127.0.0.1 --port ${port}"`,
    url: `http://127.0.0.1:${port}/login`,
    reuseExistingServer: false,
    stdout: 'pipe',
    stderr: 'pipe',
    timeout: 120_000,
  },
});
