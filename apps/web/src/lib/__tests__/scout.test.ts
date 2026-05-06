import { expect, test } from 'vitest';
import { buildScoutPayload, formatScore, resolveScoutApiUrl } from '../scout';

test('buildScoutPayload trims the query and includes location filters', () => {
  expect(buildScoutPayload('  K-12 IT directors in Albuquerque  ', '  New Mexico  ')).toEqual({
    query: 'K-12 IT directors in Albuquerque',
    filters: { location: 'New Mexico' },
  });
});

test('buildScoutPayload omits empty filters and rejects blank queries', () => {
  expect(buildScoutPayload('   ', 'New Mexico')).toBeNull();
  expect(buildScoutPayload('School districts', '   ')).toEqual({ query: 'School districts' });
});

test('resolveScoutApiUrl normalizes the upstream scout path', () => {
  expect(resolveScoutApiUrl('http://localhost:8000')).toBe('http://localhost:8000/scout');
  expect(resolveScoutApiUrl('http://localhost:8000/')).toBe('http://localhost:8000/scout');
});

test('formatScore renders percentages cleanly', () => {
  expect(formatScore(0.914)).toBe('91%');
  expect(formatScore(0.6)).toBe('60%');
});
