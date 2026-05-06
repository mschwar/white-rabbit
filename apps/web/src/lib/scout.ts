export type ScoutFilters = {
  location?: string;
};

export type ScoutRequestPayload = {
  query: string;
  filters?: ScoutFilters;
};

export type ScoutLead = {
  name: string;
  title: string;
  organization: string;
  email: string;
  email_status: 'Found' | 'Deduced' | 'Missing';
  source_url: string;
  confidence: number;
  why_target: string;
  icebreaker: string;
  fit_score: number;
  evidence_score: number;
  contact_score: number;
  gate_passed: boolean;
  explanation: string;
};

export type ScoutRunMetrics = {
  input_tokens: number;
  output_tokens: number;
  tavily_searches: number;
  openai_web_searches?: number;
  elapsed_seconds: number;
  estimated_cost_usd: number;
};

export type ScoutResponse = {
  leads: ScoutLead[];
  metrics: ScoutRunMetrics;
};

export const DEFAULT_SCOUT_QUERY = 'K-12 IT directors in Albuquerque';
export const DEFAULT_SCOUT_LOCATION = 'New Mexico';

export function buildScoutPayload(query: string, location: string): ScoutRequestPayload | null {
  const trimmedQuery = query.trim();
  if (!trimmedQuery) {
    return null;
  }

  const trimmedLocation = location.trim();
  const payload: ScoutRequestPayload = { query: trimmedQuery };

  if (trimmedLocation) {
    payload.filters = { location: trimmedLocation };
  }

  return payload;
}

export function resolveScoutApiUrl(baseUrl: string): string {
  return new URL('/scout', baseUrl).toString();
}

export function formatScore(value: number): string {
  return `${Math.round(value * 100)}%`;
}
