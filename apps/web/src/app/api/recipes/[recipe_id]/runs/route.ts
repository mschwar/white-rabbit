import { NextRequest, NextResponse } from 'next/server';

export const runtime = 'nodejs';

function getApiBaseUrl(): string {
  return process.env.WR_API_BASE_URL ?? 'http://localhost:8000';
}

export async function GET(request: NextRequest, { params }: { params: Promise<{ recipe_id: string }> }) {
  const { recipe_id } = await params;
  const apiUrl = `${getApiBaseUrl()}/recipes/${recipe_id}/runs`;

  let upstreamResponse: Response;
  try {
    upstreamResponse = await fetch(apiUrl, { method: 'GET' });
  } catch (error) {
    const message = error instanceof Error ? error.message : 'Unable to reach API.';
    return NextResponse.json({ error: `Unable to reach API: ${message}` }, { status: 502 });
  }

  if (!upstreamResponse.ok) {
    return NextResponse.json({ error: 'Failed to fetch runs.' }, { status: upstreamResponse.status });
  }

  const responseBody = await upstreamResponse.json();
  return NextResponse.json(responseBody, { status: upstreamResponse.status });
}
