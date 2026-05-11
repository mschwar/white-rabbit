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

export type ValidationStatus = 'supported' | 'unsupported' | 'missing' | 'failed';

export type ContactStatus = 'verified_found' | 'deduced_with_pattern_evidence' | 'missing' | 'failed' | 'unsupported';

export type ValidationBucket = 'usable' | 'noisy_failed' | 'organization_only' | 'not_found';
export type OutputTier = 'high_trust_usable' | 'review' | 'organization_only' | 'not_found' | 'failed';

export const OUTPUT_TIERS: OutputTier[] = ['high_trust_usable', 'review', 'organization_only', 'not_found', 'failed'];

export const TIER_LABELS: Record<OutputTier, string> = {
  high_trust_usable: 'READY',
  review: 'REVIEW',
  organization_only: 'ORG-ONLY',
  not_found: 'NOT FOUND',
  failed: 'REVIEW',
};

export const VALIDATION_BUCKETS: Array<{
  key: ValidationBucket;
  label: string;
  description: string;
}> = [
  {
    key: 'usable',
    label: 'READY',
    description: 'Person leads with evidence-backed name, title, organization, and usable contact details.',
  },
  {
    key: 'noisy_failed',
    label: 'REVIEW',
    description: 'Rows that need human judgment because a blocker, conflict, or weak evidence prevents CRM-ready use.',
  },
  {
    key: 'organization_only',
    label: 'ORG-ONLY',
    description: 'The account was found, but no validated person was available to treat as CRM-ready.',
  },
  {
    key: 'not_found',
    label: 'NOT FOUND',
    description: 'The target was searched, but no acceptable contact was found.',
  },
];

export type FullResponse = {
  run_id: string;
  recipe_id: string | null;
  leads: ScoutResultRow[];
  metrics: ScoutRunMetrics;
  query_guardrail?: QueryGuardrailResult | null;
  sandbox_usage?: SandboxUsage | null;
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
  candidate_category?: 'person_lead';
  tier?: OutputTier;
  primary_filter_reason?: string;
  validation?: CandidateValidation;
  name: string;
  title: string;
  organization: string;
  email: string;
  email_status: 'Found' | 'Deduced' | 'Missing' | ContactStatus;
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

export type FieldValidationRecord = {
  status: ValidationStatus;
  source_url: string | null;
  evidence_snippet: string | null;
  checked_at: string | null;
  notes: string;
};

export type ContactValidationRecord = {
  status: ContactStatus;
  source_url: string | null;
  evidence_snippet: string | null;
  checked_at: string | null;
  notes: string;
};

export type CandidateValidation = {
  name: FieldValidationRecord;
  title: FieldValidationRecord;
  organization: FieldValidationRecord;
  email: ContactValidationRecord;
  phone: ContactValidationRecord;
  source: FieldValidationRecord;
};

export type OrganizationOnlyResultRow = {
  id?: string;
  candidate_category: 'organization_only';
  tier?: OutputTier;
  primary_filter_reason?: string;
  organization: string;
  source_url?: string | null;
  explanation: string;
  validation?: CandidateValidation;
};

export type NotFoundResultRow = {
  id?: string;
  candidate_category: 'not_found';
  tier?: OutputTier;
  primary_filter_reason?: string;
  searched_target: string;
  organization?: string | null;
  source_url?: string | null;
  explanation: string;
  validation?: CandidateValidation;
};

export type FailedResultRow = {
  id?: string;
  candidate_category: 'failed';
  tier?: OutputTier;
  primary_filter_reason?: string;
  searched_target: string;
  failure_reason: string;
  organization?: string | null;
  source_url?: string | null;
  explanation: string;
  validation?: CandidateValidation;
};

export type ScoutResultRow = ScoutLead | OrganizationOnlyResultRow | NotFoundResultRow | FailedResultRow;

export type ScoutRunMetrics = {
  input_tokens: number;
  output_tokens: number;
  tavily_searches: number;
  openai_web_searches?: number;
  elapsed_seconds: number;
  estimated_cost_usd: number;
  tier_distribution?: Partial<Record<OutputTier, number>>;
};

export type QueryGuardrailResult = {
  status: 'clear' | 'needs_more_detail' | 'blocked';
  message: string;
  suggestions: string[];
  missing_criteria: string[];
};

export type SandboxUsage = {
  total_queries: number;
  total_rows: number;
  max_queries: number;
  max_rows: number;
  remaining_queries: number;
  remaining_rows: number;
  reset_at: string;
};

export type ScoutResponse = {
  leads: ScoutResultRow[];
  metrics: ScoutRunMetrics;
  query_guardrail?: QueryGuardrailResult | null;
  sandbox_usage?: SandboxUsage | null;
};

export const DEFAULT_SCOUT_QUERY = 'Healthcare IT directors in Phoenix';
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

export type LeadSortMode = 'rank' | 'fit' | 'evidence' | 'contact' | 'gate';

export const LEAD_SORT_OPTIONS: Array<{ value: LeadSortMode; label: string }> = [
  { value: 'rank', label: 'Original rank' },
  { value: 'fit', label: 'Fit signal' },
  { value: 'evidence', label: 'Evidence support' },
  { value: 'contact', label: 'Contact readiness' },
  { value: 'gate', label: 'Ready tier first' },
];

export function sortScoutLeads(leads: ScoutLead[], sortMode: LeadSortMode): ScoutLead[] {
  return leads
    .map((lead, index) => ({ lead, index }))
    .sort((left, right) => {
      if (sortMode === 'rank') {
        return left.index - right.index;
      }

      if (sortMode === 'gate') {
        const gateDelta = Number(right.lead.gate_passed) - Number(left.lead.gate_passed);
        if (gateDelta !== 0) {
          return gateDelta;
        }
      } else {
        const leftScore =
          sortMode === 'fit'
            ? left.lead.fit_score
            : sortMode === 'evidence'
              ? left.lead.evidence_score
              : left.lead.contact_score;
        const rightScore =
          sortMode === 'fit'
            ? right.lead.fit_score
            : sortMode === 'evidence'
              ? right.lead.evidence_score
              : right.lead.contact_score;
        const scoreDelta = (rightScore ?? 0) - (leftScore ?? 0);
        if (scoreDelta !== 0) {
          return scoreDelta;
        }
      }

      return left.index - right.index;
    })
    .map(({ lead }) => lead);
}

const VALIDATION_BUCKET_ORDER: Record<ValidationBucket, number> = {
  usable: 0,
  noisy_failed: 1,
  organization_only: 2,
  not_found: 3,
};

export function isPersonLead(row: ScoutResultRow): row is ScoutLead {
  return row.candidate_category === undefined || row.candidate_category === 'person_lead';
}

export function getOutputTier(row: ScoutResultRow): OutputTier {
  if (row.tier) {
    return row.tier;
  }

  if (row.candidate_category === 'organization_only') {
    return 'organization_only';
  }

  if (row.candidate_category === 'not_found') {
    return 'not_found';
  }

  if (row.candidate_category === 'failed') {
    return 'failed';
  }

  return 'gate_passed' in row && row.gate_passed ? 'high_trust_usable' : 'review';
}

export function getValidationBucket(row: ScoutResultRow): ValidationBucket {
  const tier = getOutputTier(row);
  if (tier === 'organization_only') {
    return 'organization_only';
  }

  if (tier === 'not_found') {
    return 'not_found';
  }

  if (tier === 'failed' || tier === 'review') {
    return 'noisy_failed';
  }

  return 'usable';
}

export function buildTierDistribution(
  rows: ScoutResultRow[],
  metricsDistribution?: Partial<Record<OutputTier, number>>,
): Record<OutputTier, number> {
  const distribution = OUTPUT_TIERS.reduce(
    (acc, tier) => {
      acc[tier] = metricsDistribution?.[tier] ?? 0;
      return acc;
    },
    {} as Record<OutputTier, number>,
  );

  if (metricsDistribution) {
    return distribution;
  }

  for (const row of rows) {
    distribution[getOutputTier(row)] += 1;
  }

  return distribution;
}

function getResultRowScore(row: ScoutResultRow, sortMode: LeadSortMode): number {
  if (sortMode === 'fit') {
    return 'fit_score' in row ? row.fit_score ?? 0 : 0;
  }

  if (sortMode === 'evidence') {
    return 'evidence_score' in row ? row.evidence_score ?? 0 : 0;
  }

  if (sortMode === 'contact') {
    return 'contact_score' in row ? row.contact_score ?? 0 : 0;
  }

  if (sortMode === 'gate') {
    return 'gate_passed' in row && row.gate_passed ? 1 : 0;
  }

  return 0;
}

export function sortScoutResultRows(rows: ScoutResultRow[], sortMode: LeadSortMode): ScoutResultRow[] {
  return rows
    .map((row, index) => ({ row, index }))
    .sort((left, right) => {
      const bucketDelta =
        VALIDATION_BUCKET_ORDER[getValidationBucket(left.row)] - VALIDATION_BUCKET_ORDER[getValidationBucket(right.row)];
      if (bucketDelta !== 0) {
        return bucketDelta;
      }

      if (sortMode !== 'rank') {
        const scoreDelta = getResultRowScore(right.row, sortMode) - getResultRowScore(left.row, sortMode);
        if (scoreDelta !== 0) {
          return scoreDelta;
        }
      }

      return left.index - right.index;
    })
    .map(({ row }) => row);
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

export type CorrectionLabel = FeedbackLabel | 'corrected_field';

export type CorrectionField = 'name' | 'title' | 'organization' | 'email' | 'phone' | 'source';

export const CORRECTION_LABEL_OPTIONS: Array<{ value: CorrectionLabel; label: string }> = [
  { value: 'wrong_persona', label: 'Wrong persona' },
  { value: 'bad_contact', label: 'Bad contact' },
  { value: 'bad_source', label: 'Bad source' },
  { value: 'duplicate', label: 'Duplicate' },
  { value: 'corrected_field', label: 'Corrected field' },
  { value: 'usable', label: 'Usable' },
];

export const CORRECTION_FIELD_OPTIONS: Array<{ value: CorrectionField; label: string }> = [
  { value: 'name', label: 'Name' },
  { value: 'title', label: 'Title' },
  { value: 'organization', label: 'Organization' },
  { value: 'email', label: 'Email' },
  { value: 'phone', label: 'Phone' },
  { value: 'source', label: 'Source' },
];

export type LeadCorrectionRequest = {
  run_id: string;
  query: string;
  label: CorrectionLabel;
  field_name: CorrectionField;
  previous_value?: string;
  corrected_value?: string;
  notes?: string;
};

export type LeadCorrectionRecord = {
  id: string;
  lead_id: string;
  run_id: string;
  query: string;
  label: CorrectionLabel;
  field_name: CorrectionField;
  previous_value: string | null;
  corrected_value: string | null;
  notes: string | null;
  created_at: string;
};

export async function submitLeadCorrection(leadId: string, payload: LeadCorrectionRequest): Promise<LeadCorrectionRecord> {
  const response = await fetch(`/api/leads/${leadId}/corrections`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  });
  if (!response.ok) {
    throw new Error('Failed to submit correction.');
  }
  return response.json();
}

export async function fetchRunCorrections(runId: string): Promise<LeadCorrectionRecord[]> {
  const response = await fetch(`/api/runs/${runId}/corrections`);
  if (!response.ok) {
    throw new Error('Failed to fetch correction queue.');
  }
  return response.json();
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

export async function fetchSandboxUsage(): Promise<SandboxUsage> {
  const response = await fetch('/api/sandbox');
  if (!response.ok) {
    throw new Error('Failed to fetch sandbox usage.');
  }
  return response.json();
}

export async function resetSandboxUsage(): Promise<SandboxUsage> {
  const response = await fetch('/api/sandbox', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
  });
  if (!response.ok) {
    throw new Error('Failed to reset sandbox usage.');
  }
  const body = (await response.json()) as { sandbox_usage?: SandboxUsage };
  return body.sandbox_usage ?? (body as SandboxUsage);
}
