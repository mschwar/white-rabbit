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
import { createSessionToken, SESSION_COOKIE_NAME } from '@/lib/auth';

afterEach(() => {
  vi.clearAllMocks();
  delete process.env.WR_SHARED_PASSWORD;
  delete process.env.WR_SESSION_SECRET;
  delete process.env.WR_SESSION_COOKIE_SECURE;
  delete process.env.NODE_ENV;
});

test('successful login redirects with 303 so the browser follows with GET', async () => {
  process.env.WR_SHARED_PASSWORD = 'correct-password';
  process.env.WR_SESSION_SECRET = 'session-secret';
  vi.mocked(matchesSharedPassword).mockReturnValue(true);

  const request = new NextRequest('http://localhost/api/login', {
    method: 'POST',
    body: new URLSearchParams({ password: 'correct-password', next: '/scout' }),
  });

  const response = await POST(request);

  expect(response.status).toBe(303);
  expect(response.headers.get('location')).toBe('http://localhost/scout');
  expect(createSessionToken).toHaveBeenCalledWith('session-secret');
  expect(response.cookies.get(SESSION_COOKIE_NAME)?.value).toBe('signed-session-token');
  expect(response.cookies.get(SESSION_COOKIE_NAME)?.secure).toBe(false);
});

test('successful login keeps secure cookies for forwarded https traffic', async () => {
  process.env.WR_SHARED_PASSWORD = 'correct-password';
  process.env.WR_SESSION_SECRET = 'session-secret';
  vi.mocked(matchesSharedPassword).mockReturnValue(true);

  const request = new NextRequest('http://localhost/api/login', {
    method: 'POST',
    headers: { 'x-forwarded-proto': 'https' },
    body: new URLSearchParams({ password: 'correct-password', next: '/scout' }),
  });

  const response = await POST(request);

  expect(response.cookies.get(SESSION_COOKIE_NAME)?.secure).toBe(true);
});

test('failed login redirects back to login with 303 and preserves next', async () => {
  process.env.WR_SHARED_PASSWORD = 'correct-password';
  vi.mocked(matchesSharedPassword).mockReturnValue(false);

  const request = new NextRequest('http://localhost/api/login', {
    method: 'POST',
    body: new URLSearchParams({ password: 'wrong-password', next: '/scout' }),
  });

  const response = await POST(request);

  expect(response.status).toBe(303);
  expect(response.headers.get('location')).toBe('http://localhost/login?error=1&next=%2Fscout');
});
