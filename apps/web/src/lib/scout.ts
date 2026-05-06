export type ScoutFilters = {
  location?: string;
};

export type ScoutRequestPayload = {
  query: string;
  filters?: ScoutFilters;
  recipe_name?: string;
};

export type FullRequestPayload = {
  query: string;
  filters?: ScoutFilters;
  recipe_name?: string;
};

export type FullResponse = {
  run_id: string;
  recipe_id: string | null;
  leads: ScoutLead[];
  metrics: ScoutRunMetrics;
};

export type RecipeItem = {
  id: string;
  name: string;
  query: string;
  filters: Record<string, unknown>;
  created_at: string;
};

export type RecipeRunItem = {
  id: string;
  recipe_id: string | null;
  mode: string;
  started_at: string;
  ended_at: string | null;
  operator_minutes: number | null;
  lead_count: number;
};

export type RecipeScoreboardItem = {
  recipe_id: string;
  recipe_name: string;
  total_api_cost_usd: number;
  total_leads_returned: number;
  usable_lead_count: number;
  total_operator_minutes: number;
  minutes_per_usable_lead: number | null;
  api_cost_per_usable_lead: number | null;
  feedback_counts: Record<string, number>;
};

export type ScoutLead = {
  id?: string;
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

export function buildFullPayload(query: string, location: string, recipeName?: string): FullRequestPayload | null {
  const trimmedQuery = query.trim();
  if (!trimmedQuery) {
    return null;
  }

  const trimmedLocation = location.trim();
  const payload: FullRequestPayload = { query: trimmedQuery };

  if (trimmedLocation) {
    payload.filters = { location: trimmedLocation };
  }

  if (recipeName?.trim()) {
    payload.recipe_name = recipeName.trim();
  }

  return payload;
}

export function resolveScoutApiUrl(baseUrl: string): string {
  return new URL('/scout', baseUrl).toString();
}

export function formatScore(value: number): string {
  return `${Math.round(value * 100)}%`;
}

export async function fetchRecipes(): Promise<RecipeItem[]> {
  const response = await fetch('/api/recipes');
  if (!response.ok) {
    throw new Error('Failed to fetch recipes.');
  }
  return response.json();
}

export async function fetchRecipeRuns(recipeId: string): Promise<RecipeRunItem[]> {
  const response = await fetch(`/api/recipes/${recipeId}/runs`);
  if (!response.ok) {
    throw new Error('Failed to fetch recipe runs.');
  }
  return response.json();
}

export async function fetchRecipeScoreboard(recipeId: string): Promise<RecipeScoreboardItem> {
  const response = await fetch(`/api/recipes/${recipeId}/scoreboard`);
  if (!response.ok) {
    throw new Error('Failed to fetch recipe scoreboard.');
  }
  return response.json();
}

export type FeedbackLabel = 'usable' | 'wrong_persona' | 'bad_source' | 'bad_contact' | 'duplicate';

export async function submitLeadFeedback(leadId: string, label: FeedbackLabel): Promise<void> {
  const response = await fetch(`/api/leads/${leadId}/feedback`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ label }),
  });
  if (!response.ok) {
    throw new Error('Failed to submit feedback.');
  }
}

export async function closeRecipeRun(runId: string, operatorMinutes: number): Promise<void> {
  const response = await fetch(`/api/runs/${runId}/close`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ operator_minutes: operatorMinutes }),
  });
  if (!response.ok) {
    throw new Error('Failed to close run.');
  }
}
