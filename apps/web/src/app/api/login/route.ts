import { NextRequest, NextResponse } from 'next/server';
import {
  createSessionToken,
  normalizeNextPath,
  SESSION_COOKIE_NAME,
  SESSION_MAX_AGE_MS,
  shouldUseSecureSessionCookie,
} from '@/lib/auth';
import { matchesSharedPassword } from '@/lib/password';

export const runtime = 'nodejs';

function requireEnv(name: string): string {
  const value = process.env[name];
  if (!value) {
    throw new Error(`Missing ${name}`);
  }
  return value;
}

function resolveRequestOrigin(request: NextRequest): string {
  const forwardedProto = request.headers.get('x-forwarded-proto')?.split(',')[0]?.trim();
  const forwardedHost = request.headers.get('x-forwarded-host')?.split(',')[0]?.trim();
  const host = forwardedHost || request.headers.get('host')?.trim();

  if (!host) {
    return request.nextUrl.origin;
  }

  const protocol = forwardedProto || request.nextUrl.protocol.replace(/:$/, '');
  return `${protocol}://${host}`;
}

export async function POST(request: NextRequest) {
  const formData = await request.formData();
  const password = String(formData.get('password') ?? '');
  const nextPath = normalizeNextPath(String(formData.get('next') ?? '/'));
  const expectedPassword = process.env.WR_SHARED_PASSWORD ?? '';

  if (!expectedPassword) {
    return NextResponse.json({ error: 'Shared password is not configured.' }, { status: 500 });
  }

  if (!matchesSharedPassword(password, expectedPassword)) {
    const redirectUrl = new URL('/login', resolveRequestOrigin(request));
    redirectUrl.searchParams.set('error', '1');
    redirectUrl.searchParams.set('next', nextPath);
    return NextResponse.redirect(redirectUrl, { status: 303 });
  }

  const sessionSecret = requireEnv('WR_SESSION_SECRET');
  const response = NextResponse.redirect(new URL(nextPath, resolveRequestOrigin(request)), { status: 303 });
  response.cookies.set({
    name: SESSION_COOKIE_NAME,
    value: await createSessionToken(sessionSecret),
    httpOnly: true,
    sameSite: 'lax',
    secure: shouldUseSecureSessionCookie({
      cookieMode: process.env.WR_SESSION_COOKIE_SECURE,
      forwardedProto: request.headers.get('x-forwarded-proto'),
      requestProtocol: request.nextUrl.protocol,
    }),
    path: '/',
    maxAge: SESSION_MAX_AGE_MS / 1000,
  });

  return response;
}
