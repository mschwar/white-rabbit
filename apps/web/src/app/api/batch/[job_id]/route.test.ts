import { afterEach, expect, test, vi } from 'vitest';
import { NextRequest } from 'next/server';
import { GET } from './route';

const INTERNAL_API_TOKEN = 'test-internal-token';
const JOB_ID = '22222222-2222-2222-2222-222222222222';

const sampleJob = {
  id: JOB_ID,
  name: 'Monday prospecting sweep',
  status: 'running',
  cap_queries: 10,
  cap_max_leads: 100,
  cap_max_spend_usd: 5.0,
  created_at: '2026-11-11T17:00:00Z',
  started_at: '2026-11-11T17:00:01Z',
  ended_at: null,
  total_cost_usd: 0.04,
  total_leads: 3,
  runs: [
    {
      id: '33333333-3333-3333-3333-333333333333',
      query: 'IT directors at school districts in Albuquerque NM',
      status: 'completed',
      lead_count: 3,
      cost_usd: 0.04,
      error_message: null,
      recipe_id: '44444444-4444-4444-4444-444444444444',
      started_at: '2026-11-11T17:00:01Z',
      ended_at: '2026-11-11T17:00:10Z',
    },
  ],
};

afterEach(() => {
  vi.unstubAllGlobals();
  delete process.env.WR_API_BASE_URL;
  delete process.env.WR_API_INTERNAL_TOKEN;
});

test('proxies GET /api/batch/[job_id] with internal API token header', async () => {
  process.env.WR_API_BASE_URL = 'http://api.example:8000';
  process.env.WR_API_INTERNAL_TOKEN = INTERNAL_API_TOKEN;
  const fetchMock = vi.fn().mockResolvedValue(
    new Response(JSON.stringify(sampleJob), {
      status: 200,
      headers: { 'content-type': 'application/json' },
    }),
  );
  vi.stubGlobal('fetch', fetchMock);

  const request = new NextRequest(`http://localhost/api/batch/${JOB_ID}`);
  const response = await GET(request, { params: Promise.resolve({ job_id: JOB_ID }) });

  expect(fetchMock).toHaveBeenCalledWith(`http://api.example:8000/batch/${JOB_ID}`, {
    method: 'GET',
    headers: {
      'x-white-rabbit-internal-token': INTERNAL_API_TOKEN,
    },
    body: undefined,
  });
  expect(response.status).toBe(200);
  await expect(response.json()).resolves.toMatchObject(sampleJob);
});

test('propagates upstream 404 when batch job is missing', async () => {
  process.env.WR_API_BASE_URL = 'http://api.example:8000';
  process.env.WR_API_INTERNAL_TOKEN = INTERNAL_API_TOKEN;
  vi.stubGlobal(
    'fetch',
    vi.fn().mockResolvedValue(
      new Response(JSON.stringify({ detail: 'Batch job not found' }), {
        status: 404,
        headers: { 'content-type': 'application/json' },
      }),
    ),
  );

  const request = new NextRequest(`http://localhost/api/batch/${JOB_ID}`);
  const response = await GET(request, { params: Promise.resolve({ job_id: JOB_ID }) });

  expect(response.status).toBe(404);
  await expect(response.json()).resolves.toEqual({ error: 'Batch job not found' });
});

test('rejects invalid job_id or missing internal token cleanly', async () => {
  const fetchMock = vi.fn();
  vi.stubGlobal('fetch', fetchMock);

  const badRequest = new NextRequest('http://localhost/api/batch/..');
  const badResponse = await GET(badRequest, { params: Promise.resolve({ job_id: '..' }) });
  expect(badResponse.status).toBe(400);
  expect(fetchMock).not.toHaveBeenCalled();

  const noTokenRequest = new NextRequest(`http://localhost/api/batch/${JOB_ID}`);
  const noTokenResponse = await GET(noTokenRequest, { params: Promise.resolve({ job_id: JOB_ID }) });
  expect(noTokenResponse.status).toBe(500);
  expect(fetchMock).not.toHaveBeenCalled();
});
