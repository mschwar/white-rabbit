import { NextRequest, NextResponse } from 'next/server';
import { resolveScoutApiUrl, type QueryGuardrailResult, type ScoutRequestPayload } from '@/lib/scout';
import { buildInternalApiRequestInit, getApiBaseUrl } from '@/lib/internal-api';

export const runtime = 'nodejs';

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

async function readErrorPayload(response: Response): Promise<Record<string, unknown>> {
  const contentType = response.headers.get('content-type') ?? '';
  if (contentType.includes('application/json')) {
    try {
      const body = (await response.json()) as {
        error?: string;
        detail?: unknown;
        query_guardrail?: QueryGuardrailResult;
      };

      if (body.query_guardrail || body.error) {
        return body as Record<string, unknown>;
      }

      if (body.detail && typeof body.detail === 'object') {
        return body.detail as Record<string, unknown>;
      }

      if (typeof body.detail === 'string') {
        return { error: body.detail };
      }
    } catch {
      return { error: `Scout API failed (${response.status}).` };
    }
  }

  const text = await response.text();
  return { error: text || `Scout API failed (${response.status}).` };
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
    upstreamResponse = await fetch(
      apiUrl,
      buildInternalApiRequestInit('POST', {
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      }),
    );
  } catch (error) {
    const message = error instanceof Error ? error.message : 'Unable to reach Scout API.';
    return NextResponse.json({ error: `Unable to reach Scout API: ${message}` }, { status: 502 });
  }

  if (!upstreamResponse.ok) {
    const payload = await readErrorPayload(upstreamResponse);
    return NextResponse.json(payload, { status: upstreamResponse.status });
  }

  const responseBody = await upstreamResponse.json();
  return NextResponse.json(responseBody, { status: upstreamResponse.status });
}
