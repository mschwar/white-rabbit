import { NextRequest, NextResponse } from 'next/server';
import { buildInternalApiRequestInit, getApiBaseUrl } from '@/lib/internal-api';

export const runtime = 'nodejs';

export async function GET(_: NextRequest, { params }: { params: Promise<{ run_id: string }> }) {
  const { run_id } = await params;
  const apiUrl = `${getApiBaseUrl()}/runs/${run_id}/leads`;

  let upstreamResponse: Response;
  try {
    upstreamResponse = await fetch(apiUrl, buildInternalApiRequestInit('GET'));
  } catch (error) {
    const message = error instanceof Error ? error.message : 'Unable to reach API.';
    return NextResponse.json({ error: `Unable to reach API: ${message}` }, { status: 502 });
  }

  if (!upstreamResponse.ok) {
    return NextResponse.json({ error: 'Failed to fetch persisted run lead readback.' }, { status: upstreamResponse.status });
  }

  const responseBody = await upstreamResponse.json();
  return NextResponse.json(responseBody, { status: upstreamResponse.status });
}
