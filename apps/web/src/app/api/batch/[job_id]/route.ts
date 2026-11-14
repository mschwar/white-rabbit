import { NextRequest, NextResponse } from 'next/server';
import { buildInternalApiRequestInit, getApiBaseUrl } from '@/lib/internal-api';

export const runtime = 'nodejs';

async function readErrorMessage(response: Response): Promise<string> {
  const contentType = response.headers.get('content-type') ?? '';
  if (contentType.includes('application/json')) {
    try {
      const body = (await response.json()) as { detail?: string; error?: string };
      return body.error ?? body.detail ?? `API failed (${response.status}).`;
    } catch {
      return `API failed (${response.status}).`;
    }
  }
  const text = await response.text();
  return text || `API failed (${response.status}).`;
}

export async function GET(_: NextRequest, { params }: { params: Promise<{ job_id: string }> }) {
  const { job_id } = await params;
  const trimmedId = (job_id ?? '').trim();
  if (!trimmedId || trimmedId.includes('/') || trimmedId.includes('..')) {
    return NextResponse.json({ error: 'Valid batch job ID is required.' }, { status: 400 });
  }

  let requestInit: RequestInit;
  try {
    requestInit = buildInternalApiRequestInit('GET');
  } catch (error) {
    const message = error instanceof Error ? error.message : 'Internal API configuration error.';
    return NextResponse.json({ error: message }, { status: 500 });
  }

  const apiUrl = `${getApiBaseUrl()}/batch/${encodeURIComponent(trimmedId)}`;

  let upstreamResponse: Response;
  try {
    upstreamResponse = await fetch(apiUrl, requestInit);
  } catch (error) {
    const message = error instanceof Error ? error.message : 'Unable to reach API.';
    return NextResponse.json({ error: `Unable to reach API: ${message}` }, { status: 502 });
  }

  if (!upstreamResponse.ok) {
    const message = await readErrorMessage(upstreamResponse);
    return NextResponse.json({ error: message }, { status: upstreamResponse.status });
  }

  const responseBody = await upstreamResponse.json();
  return NextResponse.json(responseBody, { status: upstreamResponse.status });
}
