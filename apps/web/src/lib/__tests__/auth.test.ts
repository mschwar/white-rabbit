import { expect, test } from 'vitest';
import {
  createSessionToken,
  isPublicPath,
  normalizeNextPath,
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

test('createSessionToken and verifySessionToken round trip', async () => {
  const secret = 'test-session-secret';
  const token = await createSessionToken(secret, 1234567890);

  await expect(verifySessionToken(token, secret)).resolves.toBe(true);
  await expect(verifySessionToken(`${token}x`, secret)).resolves.toBe(false);
  await expect(verifySessionToken(token, 'wrong-secret')).resolves.toBe(false);
});
