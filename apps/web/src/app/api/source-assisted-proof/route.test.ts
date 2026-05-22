import { afterEach, expect, test, vi } from 'vitest';
import { NextRequest } from 'next/server';
import { POST } from './route';

const INTERNAL_API_TOKEN = 'test-internal-token';

const proofBody = {
  feature_id: 'R09L - Live source-assisted product proof',
  request_summary: {
    query: 'NM IT for school districts',
    target: 'April 2026 New Mexico school-district IT',
  },
  source_assisted_replay: {
    candidate_count: 17,
    tier_distribution: { high_trust_usable: 10, manual_lookup: 7 },
  },
};

afterEach(() => {
  vi.unstubAllGlobals();
  delete process.env.WR_API_BASE_URL;
  delete process.env.WR_API_INTERNAL_TOKEN;
});

test('proxies source-assisted proof requests through the web API boundary', async () => {
  process.env.WR_API_BASE_URL = 'http://api.example:8000';
  process.env.WR_API_INTERNAL_TOKEN = INTERNAL_API_TOKEN;
  const fetchMock = vi.fn().mockResolvedValue(
    new Response(JSON.stringify(proofBody), {
      status: 200,
      headers: { 'content-type': 'application/json' },
    }),
  );
  vi.stubGlobal('fetch', fetchMock);

  const request = new NextRequest('http://localhost/api/source-assisted-proof', {
    method: 'POST',
    headers: { 'content-type': 'application/json' },
    body: JSON.stringify({ query: 'NM IT for school districts', target: 'April 2026 New Mexico school-district IT' }),
  });

  const response = await POST(request);

  expect(fetchMock).toHaveBeenCalledWith('http://api.example:8000/source-assisted-proof', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'x-white-rabbit-internal-token': INTERNAL_API_TOKEN,
    },
    body: JSON.stringify({ query: 'NM IT for school districts', target: 'April 2026 New Mexico school-district IT' }),
  });
  expect(response.status).toBe(200);
  await expect(response.json()).resolves.toMatchObject(proofBody);
});

test('rejects blank source-assisted proof queries before calling upstream', async () => {
  const fetchMock = vi.fn();
  vi.stubGlobal('fetch', fetchMock);

  const request = new NextRequest('http://localhost/api/source-assisted-proof', {
    method: 'POST',
    headers: { 'content-type': 'application/json' },
    body: JSON.stringify({ query: '   ' }),
  });

  const response = await POST(request);

  expect(response.status).toBe(400);
  expect(fetchMock).not.toHaveBeenCalled();
  await expect(response.json()).resolves.toMatchObject({ error: 'Query is required.' });
});
