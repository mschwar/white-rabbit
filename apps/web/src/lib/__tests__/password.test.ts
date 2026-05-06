import { expect, test } from 'vitest';
import { matchesSharedPassword } from '../password';

test('matchesSharedPassword compares equal-length passwords safely', () => {
  expect(matchesSharedPassword('scout-pass', 'scout-pass')).toBe(true);
  expect(matchesSharedPassword('scout-pass', 'wrong-pass')).toBe(false);
  expect(matchesSharedPassword('short', 'much-longer')).toBe(false);
});
