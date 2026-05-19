import { afterEach, expect, test, vi } from 'vitest';
import { NextRequest } from 'next/server';

vi.mock('@/lib/password', () => ({
  matchesSharedPassword: vi.fn(),
}));

vi.mock('@/lib/auth', async () => {
  const actual = await vi.importActual<typeof import('@/lib/auth')>('@/lib/auth');
  return {
    ...actual,
    createSessionToken: vi.fn().mockResolvedValue('signed-session-token'),
  };
});

import { POST } from './route';
import { matchesSharedPassword } from '@/lib/password';
import { SESSION_COOKIE_NAME } from '@/lib/auth';

afterEach(() => {
  vi.clearAllMocks();
  delete process.env.WR_SHARED_PASSWORD;
  delete process.env.WR_SESSION_SECRET;
  delete process.env.WR_SESSION_COOKIE_SECURE;
});

test('preserves the incoming host when issuing the post-login redirect', async () => {
  // Regression: ISSUE-001 — login redirect switched from 127.0.0.1 to localhost and dropped the session cookie
  // Found by /qa on 2026-05-19
  // Report: .gstack/qa-reports/qa-report-127.0.0.1-2026-05-19.md
  process.env.WR_SHARED_PASSWORD = 'correct-password';
  process.env.WR_SESSION_SECRET = 'session-secret';
  vi.mocked(matchesSharedPassword).mockReturnValue(true);

  const request = new NextRequest('http://localhost:3000/api/login', {
    method: 'POST',
    headers: {
      host: '127.0.0.1:3000',
    },
    body: new URLSearchParams({ password: 'correct-password', next: '/' }),
  });

  const response = await POST(request);

  expect(response.status).toBe(303);
  expect(response.headers.get('location')).toBe('http://127.0.0.1:3000/');
  expect(response.cookies.get(SESSION_COOKIE_NAME)?.secure).toBe(false);
});

test('preserves forwarded host and proto on failed login redirects', async () => {
  // Regression: ISSUE-001 — failed logins also bounced to the wrong origin under production-like hosts
  // Found by /qa on 2026-05-19
  // Report: .gstack/qa-reports/qa-report-127.0.0.1-2026-05-19.md
  process.env.WR_SHARED_PASSWORD = 'correct-password';
  vi.mocked(matchesSharedPassword).mockReturnValue(false);

  const request = new NextRequest('http://localhost:3000/api/login', {
    method: 'POST',
    headers: {
      host: 'internal-web:3000',
      'x-forwarded-host': 'app.whiterabbit.local',
      'x-forwarded-proto': 'https',
    },
    body: new URLSearchParams({ password: 'wrong-password', next: '/scout' }),
  });

  const response = await POST(request);

  expect(response.status).toBe(303);
  expect(response.headers.get('location')).toBe('https://app.whiterabbit.local/login?error=1&next=%2Fscout');
});
