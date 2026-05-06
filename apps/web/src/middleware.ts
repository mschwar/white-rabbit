import { NextRequest, NextResponse } from 'next/server';
import {
  isPublicPath,
  LOGIN_PATH,
  SESSION_COOKIE_NAME,
  verifySessionToken,
} from './lib/auth';

async function isAuthenticated(request: NextRequest): Promise<boolean> {
  const secret = process.env.WR_SESSION_SECRET;
  const token = request.cookies.get(SESSION_COOKIE_NAME)?.value;

  if (!secret || !token) {
    return false;
  }

  return verifySessionToken(token, secret);
}

export async function middleware(request: NextRequest) {
  const { pathname, search } = request.nextUrl;
  const authenticated = await isAuthenticated(request);

  if (pathname === LOGIN_PATH && authenticated) {
    return NextResponse.redirect(new URL('/', request.url));
  }

  if (isPublicPath(pathname)) {
    return NextResponse.next();
  }

  if (!authenticated) {
    if (pathname.startsWith('/api/')) {
      return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });
    }

    const redirect = new URL(LOGIN_PATH, request.url);
    redirect.searchParams.set('next', `${pathname}${search}`);
    return NextResponse.redirect(redirect);
  }

  return NextResponse.next();
}

export const config = {
  matcher: ['/((?!_next/static|_next/image|favicon.ico|robots.txt|sitemap.xml).*)'],
};
