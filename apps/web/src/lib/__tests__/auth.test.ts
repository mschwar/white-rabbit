import { expect, test } from 'vitest';
import {
  createSessionToken,
  isPublicPath,
  normalizeNextPath,
  shouldUseSecureSessionCookie,
  verifySessionToken,
} from '../auth';

test('normalizeNextPath rejects external redirects', () => {
  expect(normalizeNextPath('https://evil.example')).toBe('/');
  expect(normalizeNextPath('//evil.example')).toBe('/');
  expect(normalizeNextPath('/scout?query=test')).toBe('/scout?query=test');
});

test('isPublicPath keeps login and auth routes public', () => {
  expect(isPublicPath('/login')).toBe(true);
  expect(isPublicPath('/api/login')).toBe(true);
  expect(isPublicPath('/api/logout')).toBe(true);
  expect(isPublicPath('/scout')).toBe(false);
});

test('shouldUseSecureSessionCookie honors override and forwarded proto', () => {
  expect(shouldUseSecureSessionCookie({ cookieMode: 'always', requestProtocol: 'http:' })).toBe(true);
  expect(shouldUseSecureSessionCookie({ cookieMode: 'never', requestProtocol: 'https:' })).toBe(false);
  expect(shouldUseSecureSessionCookie({ forwardedProto: 'https', requestProtocol: 'http:' })).toBe(true);
  expect(shouldUseSecureSessionCookie({ forwardedProto: 'http', requestProtocol: 'https:' })).toBe(false);
  expect(shouldUseSecureSessionCookie({ requestProtocol: 'https:' })).toBe(true);
  expect(shouldUseSecureSessionCookie({ requestProtocol: 'http:' })).toBe(false);
});

test('createSessionToken and verifySessionToken enforce max age and clock skew', async () => {
  const secret = 'test-session-secret';
  const now = Date.now();
  const freshToken = await createSessionToken(secret, now - 30_000);
  const staleToken = await createSessionToken(secret, now - 8 * 24 * 60 * 60 * 1000);
  const futureToken = await createSessionToken(secret, now + 2 * 60 * 60 * 1000);
  const skewTolerableToken = await createSessionToken(secret, now - 30_000);

  await expect(verifySessionToken(freshToken, secret)).resolves.toBe(true);
  await expect(verifySessionToken(`${freshToken}x`, secret)).resolves.toBe(false);
  await expect(verifySessionToken(freshToken, 'wrong-secret')).resolves.toBe(false);
  await expect(verifySessionToken(staleToken, secret)).resolves.toBe(false);
  await expect(verifySessionToken(futureToken, secret)).resolves.toBe(false);
  await expect(verifySessionToken(skewTolerableToken, secret)).resolves.toBe(true);
});
