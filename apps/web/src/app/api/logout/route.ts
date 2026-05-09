import { NextRequest, NextResponse } from 'next/server';
import { LOGIN_PATH, SESSION_COOKIE_NAME } from '@/lib/auth';

export const runtime = 'nodejs';

export async function POST(request: NextRequest) {
  const response = NextResponse.redirect(new URL(LOGIN_PATH, request.url), { status: 303 });
  response.cookies.set({
    name: SESSION_COOKIE_NAME,
    value: '',
    httpOnly: true,
    sameSite: 'lax',
    secure: process.env.NODE_ENV === 'production',
    path: '/',
    maxAge: 0,
  });

  return response;
}

export async function GET(request: NextRequest) {
  return POST(request);
}
