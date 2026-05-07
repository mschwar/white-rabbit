import type { QueryGuardrailResult, LeadSortMode, ScoutLead } from './scout';

export type FullLeadExportRow = {
  generatedAt: string;
  sortMode: string;
  recipeName: string;
  query: string;
  location: string;
  runId: string;
  rank: string;
  name: string;
  title: string;
  organization: string;
  email: string;
  emailStatus: string;
  sourceUrl: string;
  fitScore: string;
  evidenceScore: string;
  contactScore: string;
  gatePassed: string;
  whyTarget: string;
  explanation: string;
  icebreaker: string;
  validationContext: string;
};

export type BuildFullLeadExportRowsInput = {
  query: string;
  location: string;
  recipeName: string;
  runId: string;
  sortMode: LeadSortMode;
  leads: ScoutLead[];
  guardrail: QueryGuardrailResult | null;
  generatedAt?: Date;
};

function escapeCsvCell(value: string): string {
  if (/[,"\n\r]/.test(value)) {
    return `"${value.replaceAll('"', '""')}"`;
  }
  return value;
}

function formatScore(value: number): string {
  return value.toFixed(2);
}

function describeGuardrail(guardrail: QueryGuardrailResult | null): string {
  if (!guardrail) {
    return 'No query guardrail result returned.';
  }

  if (guardrail.status === 'clear') {
    return 'Query guardrail clear.';
  }

  const missing = guardrail.missing_criteria.length > 0 ? ` Missing: ${guardrail.missing_criteria.join(', ')}.` : '';
  return `Query guardrail ${guardrail.status}. ${guardrail.message}${missing}`;
}

export function buildFullLeadExportRows({
  query,
  location,
  recipeName,
  runId,
  sortMode,
  leads,
  guardrail,
  generatedAt = new Date(),
}: BuildFullLeadExportRowsInput): FullLeadExportRow[] {
  const generatedAtLabel = generatedAt.toISOString();
  const guardrailContext = describeGuardrail(guardrail);

  return leads.map((lead, index) => ({
    generatedAt: generatedAtLabel,
    sortMode,
    recipeName,
    query,
    location,
    runId,
    rank: String(index + 1),
    name: lead.name,
    title: lead.title,
    organization: lead.organization,
    email: lead.email || 'n/a',
    emailStatus: lead.email_status,
    sourceUrl: lead.source_url,
    fitScore: formatScore(lead.fit_score),
    evidenceScore: formatScore(lead.evidence_score),
    contactScore: formatScore(lead.contact_score),
    gatePassed: lead.gate_passed ? 'yes' : 'no',
    whyTarget: lead.why_target,
    explanation: lead.explanation,
    icebreaker: lead.icebreaker,
    validationContext: [
      `Generated ${generatedAtLabel}.`,
      `Sort mode: ${sortMode}.`,
      guardrailContext,
      `Validated from source ${lead.source_url}.`,
      `Ranked by fit/evidence/contact scores.`,
    ].join(' '),
  }));
}

export function buildFullLeadExportCsv(rows: FullLeadExportRow[]): string {
  const headers = [
    'generated_at',
    'sort_mode',
    'recipe_name',
    'query',
    'location',
    'run_id',
    'rank',
    'name',
    'title',
    'organization',
    'email',
    'email_status',
    'source_url',
    'fit_score',
    'evidence_score',
    'contact_score',
    'gate_passed',
    'why_target',
    'explanation',
    'icebreaker',
    'validation_context',
  ];

  const body = rows.map((row) =>
    [
      row.generatedAt,
      row.sortMode,
      row.recipeName,
      row.query,
      row.location,
      row.runId,
      row.rank,
      row.name,
      row.title,
      row.organization,
      row.email,
      row.emailStatus,
      row.sourceUrl,
      row.fitScore,
      row.evidenceScore,
      row.contactScore,
      row.gatePassed,
      row.whyTarget,
      row.explanation,
      row.icebreaker,
      row.validationContext,
    ]
      .map(escapeCsvCell)
      .join(','),
  );

  return [headers.join(','), ...body].join('\n');
}

export function buildFullLeadExportFilename(generatedAt = new Date()): string {
  return `white-rabbit-lead-export-${generatedAt.toISOString().slice(0, 10)}.csv`;
}
