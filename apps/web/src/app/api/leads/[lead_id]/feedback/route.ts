import { NextRequest, NextResponse } from 'next/server';

export const runtime = 'nodejs';

function getApiBaseUrl(): string {
  return process.env.WR_API_BASE_URL ?? 'http://localhost:8000';
}

export async function POST(request: NextRequest, { params }: { params: Promise<{ lead_id: string }> }) {
  const { lead_id } = await params;
  let payload: Record<string, unknown>;

  try {
    payload = (await request.json()) as Record<string, unknown>;
  } catch {
    return NextResponse.json({ error: 'Invalid request body.' }, { status: 400 });
  }

  const apiUrl = `${getApiBaseUrl()}/leads/${lead_id}/feedback`;

  let upstreamResponse: Response;
  try {
    upstreamResponse = await fetch(apiUrl, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });
  } catch (error) {
    const message = error instanceof Error ? error.message : 'Unable to reach API.';
    return NextResponse.json({ error: `Unable to reach API: ${message}` }, { status: 502 });
  }

  if (!upstreamResponse.ok) {
    return NextResponse.json({ error: 'Failed to submit feedback.' }, { status: upstreamResponse.status });
  }

  const responseBody = await upstreamResponse.json();
  return NextResponse.json(responseBody, { status: upstreamResponse.status });
}
