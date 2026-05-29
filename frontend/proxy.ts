import { NextResponse } from 'next/server';
import type { NextRequest } from 'next/server';

export default function examiddleware(request: NextRequest) {
  const token = request.cookies.get('ciap_access')?.value;
  const { pathname } = request.nextUrl;

  const isApiProxy = pathname.startsWith('/api-proxy');

  const isOnboardingPage = pathname.startsWith('/onboarding');
  const isAuthPage = pathname.startsWith('/login') || pathname.startsWith('/signup') || isOnboardingPage || pathname.startsWith('/welcome');
  const isCallbackPage = pathname.startsWith('/callback');
  const isLandingPage = pathname === '/';
  
  // Always allow API proxy calls through; only inject auth header when a token exists.
  if (isApiProxy) {
    if (token) {
      const headers = new Headers(request.headers);
      if (!headers.get('authorization')) {
        headers.set('authorization', `Bearer ${token}`);
      }
      return NextResponse.next({ request: { headers } });
    }
    return NextResponse.next();
  }

  // Allow landing/auth pages and API proxy requests without tokens
  if (!token && !isAuthPage && !isCallbackPage && !isLandingPage && !isApiProxy) {
    return NextResponse.redirect(new URL('/login', request.url));
  }

  // If already logged in, redirect auth pages to dashboard
  if (token && ((isAuthPage && !isOnboardingPage) || isCallbackPage)) {
    return NextResponse.redirect(new URL('/dashboard', request.url));
  }

  return NextResponse.next();
}

export const config = {
  // Exclude static assets (jpg, png, svg, etc.) so they load via public/
  matcher: [
    '/api-proxy/:path*',
    '/((?!api|_next/static|_next/image|favicon.ico|.*\\.jpg$|.*\\.png$|.*\\.svg$).*)',
  ],
};
