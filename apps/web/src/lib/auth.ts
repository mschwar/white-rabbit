const encoder = new TextEncoder();
const decoder = new TextDecoder();

export const SESSION_COOKIE_NAME = 'wr_session';
export const LOGIN_PATH = '/login';
export const LOGOUT_PATH = '/api/logout';
export const LOGIN_API_PATH = '/api/login';

const SESSION_VERSION = 1;
export const SESSION_MAX_AGE_MS = 7 * 24 * 60 * 60 * 1000;
const SESSION_CLOCK_SKEW_MS = 60 * 1000;

function bytesToBase64(bytes: Uint8Array): string {
  let binary = '';
  for (let index = 0; index < bytes.length; index += 1) {
    binary += String.fromCharCode(bytes[index]);
  }

  return btoa(binary);
}

function base64ToBytes(value: string): Uint8Array<ArrayBuffer> {
  const binary = atob(value);
  return Uint8Array.from(binary, (character) => character.charCodeAt(0)) as Uint8Array<ArrayBuffer>;
}

function base64UrlEncode(bytes: Uint8Array): string {
  return bytesToBase64(bytes).split('+').join('-').split('/').join('_').replace(/=+$/, '');
}

function base64UrlDecode(value: string): Uint8Array<ArrayBuffer> {
  const padded = value.split('-').join('+').split('_').join('/');
  const remainder = padded.length % 4;
  const normalized = remainder === 0 ? padded : `${padded}${'='.repeat(4 - remainder)}`;
  return base64ToBytes(normalized);
}

async function importSecret(secret: string): Promise<CryptoKey> {
  return crypto.subtle.importKey(
    'raw',
    encoder.encode(secret),
    { name: 'HMAC', hash: 'SHA-256' },
    false,
    ['sign', 'verify'],
  );
}

export function normalizeNextPath(candidate: string | null | undefined): string {
  if (!candidate) {
    return '/';
  }

  if (!candidate.startsWith('/') || candidate.startsWith('//')) {
    return '/';
  }

  return candidate;
}

export function isPublicPath(pathname: string): boolean {
  return (
    pathname === LOGIN_PATH ||
    pathname.startsWith(LOGIN_API_PATH) ||
    pathname.startsWith(LOGOUT_PATH)
  );
}

export async function createSessionToken(secret: string, issuedAt = Date.now()): Promise<string> {
  const payload = base64UrlEncode(
    encoder.encode(JSON.stringify({ v: SESSION_VERSION, iat: issuedAt })),
  );
  const key = await importSecret(secret);
  const signature = await crypto.subtle.sign('HMAC', key, encoder.encode(payload));
  return `${payload}.${base64UrlEncode(new Uint8Array(signature))}`;
}

export async function verifySessionToken(token: string, secret: string): Promise<boolean> {
  const [payload, signature] = token.split('.');
  if (!payload || !signature) {
    return false;
  }

  try {
    const parsed = JSON.parse(decoder.decode(base64UrlDecode(payload))) as {
      v?: number;
      iat?: number;
    };

    if (parsed.v !== SESSION_VERSION || typeof parsed.iat !== 'number') {
      return false;
    }

    const ageMs = Date.now() - parsed.iat;
    if (ageMs > SESSION_MAX_AGE_MS) {
      return false;
    }

    if (parsed.iat > Date.now() + SESSION_CLOCK_SKEW_MS) {
      return false;
    }

    const key = await importSecret(secret);
    const signatureBytes = base64UrlDecode(signature);
    return crypto.subtle.verify('HMAC', key, signatureBytes.buffer, encoder.encode(payload));
  } catch {
    return false;
  }
}
