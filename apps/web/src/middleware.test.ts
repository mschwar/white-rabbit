import { afterEach, expect, test } from 'vitest';
import { NextRequest } from 'next/server';
import { middleware } from './middleware';
import { createSessionToken, SESSION_COOKIE_NAME } from './lib/auth';
import { INTERNAL_API_TOKEN_HEADER } from './lib/internal-api';

const INTERNAL_API_TOKEN = 'test-internal-token';

afterEach(() => {
  delete process.env.WR_API_INTERNAL_TOKEN;
  delete process.env.WR_SESSION_SECRET;
});

test('returns a 401 json response for unauthenticated protected api calls', async () => {
  process.env.WR_SESSION_SECRET = 'session-secret';
  process.env.WR_API_INTERNAL_TOKEN = INTERNAL_API_TOKEN;

  const response = await middleware(
    new NextRequest('http://localhost/api/scout', {
      method: 'POST',
    }),
  );

  expect(response.status).toBe(401);
  await expect(response.json()).resolves.toMatchObject({ error: 'Unauthorized' });
});

test('allows protected api calls when the shared-password session cookie is valid', async () => {
  process.env.WR_SESSION_SECRET = 'session-secret';
  const token = await createSessionToken('session-secret');

  const response = await middleware(
    new NextRequest('http://localhost/api/source-assisted-proof', {
      method: 'POST',
      headers: {
        cookie: `${SESSION_COOKIE_NAME}=${token}`,
      },
    }),
  );

  expect(response.status).toBe(200);
  expect(response.headers.get('x-middleware-next')).toBe('1');
});

test('allows server-to-server API collectors with the internal token', async () => {
  process.env.WR_SESSION_SECRET = 'session-secret';
  process.env.WR_API_INTERNAL_TOKEN = INTERNAL_API_TOKEN;

  const response = await middleware(
    new NextRequest('http://localhost/api/source-assisted-proof', {
      method: 'POST',
      headers: { [INTERNAL_API_TOKEN_HEADER]: INTERNAL_API_TOKEN },
    }),
  );

  expect(response.status).toBe(200);
  expect(response.headers.get('x-middleware-next')).toBe('1');
});

test('does not let the internal token bypass page login', async () => {
  process.env.WR_SESSION_SECRET = 'session-secret';
  process.env.WR_API_INTERNAL_TOKEN = INTERNAL_API_TOKEN;

  const response = await middleware(
    new NextRequest('http://localhost/', {
      headers: { [INTERNAL_API_TOKEN_HEADER]: INTERNAL_API_TOKEN },
    }),
  );

  expect(response.status).toBe(307);
  expect(response.headers.get('location')).toBe('http://localhost/login?next=%2F');
});
