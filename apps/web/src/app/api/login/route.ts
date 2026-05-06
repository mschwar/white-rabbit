import { NextRequest, NextResponse } from 'next/server';
import { createSessionToken, normalizeNextPath, SESSION_COOKIE_NAME } from '@/lib/auth';
import { matchesSharedPassword } from '@/lib/password';

export const runtime = 'nodejs';

function requireEnv(name: string): string {
  const value = process.env[name];
  if (!value) {
    throw new Error(`Missing ${name}`);
  }
  return value;
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
    const redirectUrl = new URL('/login', request.url);
    redirectUrl.searchParams.set('error', '1');
    redirectUrl.searchParams.set('next', nextPath);
    return NextResponse.redirect(redirectUrl);
  }

  const sessionSecret = requireEnv('WR_SESSION_SECRET');
  const response = NextResponse.redirect(new URL(nextPath, request.url));
  response.cookies.set({
    name: SESSION_COOKIE_NAME,
    value: await createSessionToken(sessionSecret),
    httpOnly: true,
    sameSite: 'lax',
    secure: process.env.NODE_ENV === 'production',
    path: '/',
    maxAge: 60 * 60 * 24 * 7,
  });

  return response;
}
