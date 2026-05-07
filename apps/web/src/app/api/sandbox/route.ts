import { NextRequest, NextResponse } from 'next/server';

export const runtime = 'nodejs';

function getApiBaseUrl(): string {
  return process.env.WR_API_BASE_URL ?? 'http://localhost:8000';
}

async function readErrorMessage(response: Response): Promise<string> {
  const contentType = response.headers.get('content-type') ?? '';
  if (contentType.includes('application/json')) {
    try {
      const body = (await response.json()) as { error?: string; detail?: unknown };
      if (typeof body.detail === 'string') {
        return body.detail;
      }
      if (body.error) {
        return body.error;
      }
      if (body.detail && typeof body.detail === 'object') {
        const detail = body.detail as { error?: string };
        return detail.error ?? `Sandbox API failed (${response.status}).`;
      }
    } catch {
      return `Sandbox API failed (${response.status}).`;
    }
  }

  const text = await response.text();
  return text || `Sandbox API failed (${response.status}).`;
}

async function proxyToSandbox(method: 'GET' | 'POST') {
  const path = method === 'GET' ? '/sandbox' : '/sandbox/reset';
  let upstreamResponse: Response;
  try {
    upstreamResponse = await fetch(`${getApiBaseUrl()}${path}`, {
      method,
      headers: method === 'POST' ? { 'Content-Type': 'application/json' } : undefined,
    });
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

export async function GET(_: NextRequest) {
  return proxyToSandbox('GET');
}

export async function POST(_: NextRequest) {
  return proxyToSandbox('POST');
}
