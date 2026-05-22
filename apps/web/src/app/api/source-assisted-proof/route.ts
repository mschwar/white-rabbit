import { NextRequest, NextResponse } from 'next/server';
import { buildInternalApiRequestInit, getApiBaseUrl } from '@/lib/internal-api';

export const runtime = 'nodejs';

type SourceAssistedProofPayload = {
  query: string;
  target?: string;
  run_id?: string;
};

function parseJsonBody(body: unknown): SourceAssistedProofPayload {
  if (!body || typeof body !== 'object') {
    throw new Error('Request body must be a JSON object.');
  }

  const candidate = body as Partial<SourceAssistedProofPayload>;
  const query = typeof candidate.query === 'string' ? candidate.query.trim() : '';
  if (!query) {
    throw new Error('Query is required.');
  }

  const payload: SourceAssistedProofPayload = { query };
  if (typeof candidate.target === 'string' && candidate.target.trim()) {
    payload.target = candidate.target.trim();
  }
  if (typeof candidate.run_id === 'string' && candidate.run_id.trim()) {
    payload.run_id = candidate.run_id.trim();
  }
  return payload;
}

async function readErrorPayload(response: Response): Promise<Record<string, unknown>> {
  const contentType = response.headers.get('content-type') ?? '';
  if (contentType.includes('application/json')) {
    try {
      const body = (await response.json()) as { error?: string; detail?: unknown };
      if (body.error) {
        return body as Record<string, unknown>;
      }
      if (body.detail && typeof body.detail === 'object') {
        return body.detail as Record<string, unknown>;
      }
      if (typeof body.detail === 'string') {
        return { error: body.detail };
      }
    } catch {
      return { error: `Source-assisted proof API failed (${response.status}).` };
    }
  }

  const text = await response.text();
  return { error: text || `Source-assisted proof API failed (${response.status}).` };
}

export async function POST(request: NextRequest) {
  let payload: SourceAssistedProofPayload;

  try {
    payload = parseJsonBody(await request.json());
  } catch (error) {
    const message = error instanceof Error ? error.message : 'Invalid source-assisted proof request.';
    return NextResponse.json({ error: message }, { status: 400 });
  }

  const apiUrl = `${getApiBaseUrl()}/source-assisted-proof`;

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
    const message = error instanceof Error ? error.message : 'Unable to reach source-assisted proof API.';
    return NextResponse.json({ error: `Unable to reach source-assisted proof API: ${message}` }, { status: 502 });
  }

  if (!upstreamResponse.ok) {
    const payload = await readErrorPayload(upstreamResponse);
    return NextResponse.json(payload, { status: upstreamResponse.status });
  }

  const responseBody = await upstreamResponse.json();
  return NextResponse.json(responseBody, { status: upstreamResponse.status });
}
