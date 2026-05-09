export const INTERNAL_API_TOKEN_HEADER = 'x-white-rabbit-internal-token';
export const INTERNAL_API_TOKEN_ENV = 'WR_API_INTERNAL_TOKEN';

export function getApiBaseUrl(): string {
  return process.env.WR_API_BASE_URL ?? 'http://localhost:8000';
}

export function buildInternalApiRequestInit(
  method: 'GET' | 'POST',
  options: { headers?: Record<string, string>; body?: BodyInit | null } = {},
): RequestInit {
  const token = process.env.WR_API_INTERNAL_TOKEN;
  if (!token) {
    throw new Error('Missing WR_API_INTERNAL_TOKEN. Set the internal API token in the web app environment.');
  }

  return {
    method,
    headers: {
      ...(options.headers ?? {}),
      [INTERNAL_API_TOKEN_HEADER]: token,
    },
    body: options.body ?? undefined,
  };
}
