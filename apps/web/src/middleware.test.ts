import { afterEach, expect, test } from 'vitest';
import { NextRequest } from 'next/server';
import { middleware } from './middleware';
import { createSessionToken, SESSION_COOKIE_NAME } from './lib/auth';

afterEach(() => {
  delete process.env.WR_SESSION_SECRET;
});

test('returns a 401 json response for unauthenticated protected api calls', async () => {
  process.env.WR_SESSION_SECRET = 'session-secret';

  const request = new NextRequest('http://localhost/api/scout', {
    method: 'POST',
  });

  const response = await middleware(request);

  expect(response.status).toBe(401);
  await expect(response.json()).resolves.toMatchObject({ error: 'Unauthorized' });
});

test('allows protected api calls when the shared-password session cookie is valid', async () => {
  process.env.WR_SESSION_SECRET = 'session-secret';
  const token = await createSessionToken('session-secret');
  const request = new NextRequest('http://localhost/api/source-assisted-proof', {
    method: 'POST',
    headers: {
      cookie: `${SESSION_COOKIE_NAME}=${token}`,
    },
  });

  const response = await middleware(request);

  expect(response.status).toBe(200);
  expect(response.headers.get('x-middleware-next')).toBe('1');
});
