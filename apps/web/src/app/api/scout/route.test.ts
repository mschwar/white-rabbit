import { afterEach, expect, test, vi } from 'vitest';
import { NextRequest } from 'next/server';
import { POST } from './route';

const INTERNAL_API_TOKEN = 'test-internal-token';

const responseBody = {
  leads: [
    {
      name: 'Jane Smith',
      title: 'Director of Technology',
      organization: 'Albuquerque Public Schools',
      email: 'jane.smith@aps.edu',
      email_status: 'Found',
      source_url: 'https://aps.edu/tech',
      confidence: 0.88,
      why_target: 'Owns district telecom decisions',
      icebreaker: 'I noticed APS is growing its classroom connectivity needs.',
      fit_score: 0.91,
      evidence_score: 0.84,
      contact_score: 0.79,
      gate_passed: true,
      explanation: 'Strong district fit with current leadership evidence and usable email.',
    },
  ],
  metrics: {
    input_tokens: 123,
    output_tokens: 45,
    tavily_searches: 1,
    openai_web_searches: 0,
    elapsed_seconds: 1.23,
    estimated_cost_usd: 0.010123,
  },
};

afterEach(() => {
  vi.unstubAllGlobals();
  delete process.env.WR_API_BASE_URL;
  delete process.env.WR_API_INTERNAL_TOKEN;
});

test('proxies a scout query to the API base url', async () => {
  process.env.WR_API_BASE_URL = 'http://api.example:8000';
  process.env.WR_API_INTERNAL_TOKEN = INTERNAL_API_TOKEN;
  const fetchMock = vi.fn().mockResolvedValue(
    new Response(JSON.stringify(responseBody), {
      status: 200,
      headers: { 'content-type': 'application/json' },
    }),
  );
  vi.stubGlobal('fetch', fetchMock);

  const request = new NextRequest('http://localhost/api/scout', {
    method: 'POST',
    headers: { 'content-type': 'application/json' },
    body: JSON.stringify({ query: 'K-12 IT directors in Albuquerque', filters: { location: 'New Mexico' } }),
  });

  const response = await POST(request);

  expect(fetchMock).toHaveBeenCalledWith('http://api.example:8000/scout', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'x-white-rabbit-internal-token': INTERNAL_API_TOKEN,
    },
    body: JSON.stringify({ query: 'K-12 IT directors in Albuquerque', filters: { location: 'New Mexico' } }),
  });
  expect(response.status).toBe(200);
  await expect(response.json()).resolves.toMatchObject(responseBody);
});

test('rejects blank scout queries before calling upstream', async () => {
  const fetchMock = vi.fn();
  vi.stubGlobal('fetch', fetchMock);

  const request = new NextRequest('http://localhost/api/scout', {
    method: 'POST',
    headers: { 'content-type': 'application/json' },
    body: JSON.stringify({ query: '   ' }),
  });

  const response = await POST(request);

  expect(response.status).toBe(400);
  expect(fetchMock).not.toHaveBeenCalled();
  await expect(response.json()).resolves.toMatchObject({ error: 'Query is required.' });
});

test('surfaces upstream guardrail responses without losing structured hints', async () => {
  process.env.WR_API_BASE_URL = 'http://api.example:8000';
  process.env.WR_API_INTERNAL_TOKEN = INTERNAL_API_TOKEN;
  vi.stubGlobal(
    'fetch',
    vi.fn().mockResolvedValue(
      new Response(
        JSON.stringify({
          error: 'White Rabbit only runs lead-generation queries.',
          query_guardrail: {
            status: 'blocked',
            message: 'White Rabbit only runs lead-generation queries.',
            suggestions: ['Try: IT directors at school districts in New Mexico'],
            missing_criteria: ['target people or organizations'],
          },
        }),
        {
          status: 422,
          headers: { 'content-type': 'application/json' },
        },
      ),
    ),
  );

  const request = new NextRequest('http://localhost/api/scout', {
    method: 'POST',
    headers: { 'content-type': 'application/json' },
    body: JSON.stringify({ query: 'supply chain advice' }),
  });

  const response = await POST(request);

  expect(response.status).toBe(422);
  await expect(response.json()).resolves.toMatchObject({
    error: 'White Rabbit only runs lead-generation queries.',
    query_guardrail: {
      status: 'blocked',
      message: 'White Rabbit only runs lead-generation queries.',
      suggestions: ['Try: IT directors at school districts in New Mexico'],
      missing_criteria: ['target people or organizations'],
    },
  });
});

