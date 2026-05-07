export type BatchQueryItem = {
  query: string;
  filters?: { location?: string };
  recipe_name?: string;
};

export type BatchRequestPayload = {
  name: string;
  queries: BatchQueryItem[];
  cap_queries?: number;
  cap_max_leads?: number;
  cap_max_spend_usd?: number;
};

export type BatchRunItem = {
  id: string;
  query: string;
  status: string;
  lead_count: number;
  cost_usd: number;
  error_message?: string | null;
  recipe_id?: string | null;
  started_at?: string | null;
  ended_at?: string | null;
};

export type BatchJobItem = {
  id: string;
  name: string;
  status: string;
  cap_queries: number;
  cap_max_leads: number;
  cap_max_spend_usd: number;
  created_at: string;
  started_at?: string | null;
  ended_at?: string | null;
  total_cost_usd: number;
  total_leads: number;
  runs: BatchRunItem[];
};

export function buildBatchPayload(
  name: string,
  queries: BatchQueryItem[],
  caps?: { cap_queries?: number; cap_max_leads?: number; cap_max_spend_usd?: number },
): BatchRequestPayload {
  return {
    name,
    queries,
    cap_queries: caps?.cap_queries ?? 10,
    cap_max_leads: caps?.cap_max_leads ?? 1000,
    cap_max_spend_usd: caps?.cap_max_spend_usd ?? 10.0,
  };
}

export async function submitBatch(payload: BatchRequestPayload): Promise<BatchJobItem> {
  const response = await fetch('/api/batch', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  });
  if (!response.ok) {
    const body = await response.json().catch(() => ({} as Record<string, unknown>));
    throw new Error(String(body.error ?? body.detail ?? 'Batch submission failed.'));
  }
  return response.json();
}

export async function fetchBatchJobs(): Promise<BatchJobItem[]> {
  const response = await fetch('/api/batch');
  if (!response.ok) {
    throw new Error('Failed to fetch batch jobs.');
  }
  return response.json();
}

export function parseBatchCsv(text: string): BatchQueryItem[] {
  const lines = text.trim().split(/\r?\n/);
  if (lines.length === 0) return [];

  const headers = lines[0].split(',').map((h) => h.trim().toLowerCase());
  const queryIdx = headers.indexOf('query');
  const locationIdx = headers.indexOf('location');
  const recipeNameIdx = headers.indexOf('recipe_name');

  const out: BatchQueryItem[] = [];
  for (let i = 1; i < lines.length; i++) {
    const row = lines[i];
    if (!row.trim()) continue;
    const cells = row.split(',');
    const query = queryIdx >= 0 ? cells[queryIdx]?.trim() : undefined;
    if (!query) continue;
    const item: BatchQueryItem = { query };
    if (locationIdx >= 0) {
      const loc = cells[locationIdx]?.trim();
      if (loc) item.filters = { location: loc };
    }
    if (recipeNameIdx >= 0) {
      const rn = cells[recipeNameIdx]?.trim();
      if (rn) item.recipe_name = rn;
    }
    out.push(item);
  }
  return out;
}
