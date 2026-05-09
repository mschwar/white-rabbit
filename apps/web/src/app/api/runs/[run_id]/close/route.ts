import { NextRequest, NextResponse } from 'next/server';
import { buildInternalApiRequestInit, getApiBaseUrl } from '@/lib/internal-api';

export const runtime = 'nodejs';

export async function POST(request: NextRequest, { params }: { params: Promise<{ run_id: string }> }) {
  const { run_id } = await params;
  let payload: Record<string, unknown>;

  try {
    payload = (await request.json()) as Record<string, unknown>;
  } catch {
    return NextResponse.json({ error: 'Invalid request body.' }, { status: 400 });
  }

  const search = new URLSearchParams();
  if (typeof payload.operator_minutes === 'number') {
    search.set('operator_minutes', String(payload.operator_minutes));
  }

  const apiUrl = `${getApiBaseUrl()}/runs/${run_id}/close${search.toString() ? `?${search.toString()}` : ''}`;

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
    const message = error instanceof Error ? error.message : 'Unable to reach API.';
    return NextResponse.json({ error: `Unable to reach API: ${message}` }, { status: 502 });
  }

  if (!upstreamResponse.ok) {
    return NextResponse.json({ error: 'Failed to close run.' }, { status: upstreamResponse.status });
  }

  const responseBody = await upstreamResponse.json();
  return NextResponse.json(responseBody, { status: upstreamResponse.status });
}
