import { NextRequest, NextResponse } from 'next/server';
import { resolveScoutApiUrl, type ScoutRequestPayload } from '@/lib/scout';

export const runtime = 'nodejs';

function getApiBaseUrl(): string {
  return process.env.WR_API_BASE_URL ?? 'http://localhost:8000';
}

function parseJsonBody(body: unknown): ScoutRequestPayload {
  if (!body || typeof body !== 'object') {
    throw new Error('Request body must be a JSON object.');
  }

  const candidate = body as Partial<ScoutRequestPayload>;
  const query = typeof candidate.query === 'string' ? candidate.query.trim() : '';
  if (!query) {
    throw new Error('Query is required.');
  }

  const filters =
    candidate.filters && typeof candidate.filters === 'object' ? candidate.filters : undefined;

  return filters ? { query, filters } : { query };
}

async function readErrorMessage(response: Response): Promise<string> {
  const contentType = response.headers.get('content-type') ?? '';
  if (contentType.includes('application/json')) {
    try {
      const body = (await response.json()) as { detail?: string; error?: string };
      return body.error ?? body.detail ?? `Scout API failed (${response.status}).`;
    } catch {
      return `Scout API failed (${response.status}).`;
    }
  }

  const text = await response.text();
  return text || `Scout API failed (${response.status}).`;
}

export async function POST(request: NextRequest) {
  let payload: ScoutRequestPayload;

  try {
    payload = parseJsonBody(await request.json());
  } catch (error) {
    const message = error instanceof Error ? error.message : 'Invalid scout request.';
    return NextResponse.json({ error: message }, { status: 400 });
  }

  const apiUrl = resolveScoutApiUrl(getApiBaseUrl());

  let upstreamResponse: Response;
  try {
    upstreamResponse = await fetch(apiUrl, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(payload),
    });
  } catch (error) {
    const message = error instanceof Error ? error.message : 'Unable to reach Scout API.';
    return NextResponse.json({ error: `Unable to reach Scout API: ${message}` }, { status: 502 });
  }

  if (!upstreamResponse.ok) {
    const message = await readErrorMessage(upstreamResponse);
    return NextResponse.json({ error: message }, { status: upstreamResponse.status });
  }

  const responseBody = await upstreamResponse.json();
  return NextResponse.json(responseBody, { status: upstreamResponse.status });
}
