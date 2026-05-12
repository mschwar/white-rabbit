import {
  getOutputTier,
  getValidationBucket,
  isPersonLead,
  type CandidateValidation,
  type LeadSortMode,
  TIER_LABELS,
  type QueryGuardrailResult,
  type ScoutResultRow,
} from './scout';

export type FullLeadExportRow = {
  generatedAt: string;
  sortMode: string;
  recipeName: string;
  query: string;
  location: string;
  runId: string;
  rank: string;
  operatorLabel: string;
  candidateCategory: string;
  usableCandidate: string;
  leadName: string;
  title: string;
  organization: string;
  email: string;
  emailStatus: string;
  phone: string;
  phoneStatus: string;
  fitScore: string;
  evidenceScore: string;
  contactScore: string;
  rankingGate: string;
  sourceNameUrl: string;
  sourceTitleUrl: string;
  sourceOrgUrl: string;
  sourceEmailUrl: string;
  sourcePhoneUrl: string;
  sourceAccessStatus: string;
  validationNotes: string;
  checkedAt: string;
};

export type BuildFullLeadExportRowsInput = {
  query: string;
  location: string;
  recipeName: string;
  runId: string;
  sortMode: LeadSortMode;
  rows: ScoutResultRow[];
  guardrail: QueryGuardrailResult | null;
  generatedAt?: Date;
};

const EXPORT_BUCKET_ORDER = {
  usable: 0,
  noisy_failed: 1,
  organization_only: 2,
  not_found: 3,
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

function createFallbackValidation(row: ScoutResultRow): CandidateValidation {
  const sourceUrl = 'source_url' in row ? row.source_url ?? null : null;
  const notes = sourceUrl ? 'Field-level validation was not captured for this row.' : 'No source URL was captured for this row.';
  const record = {
    status: 'unsupported' as const,
    source_url: sourceUrl,
    evidence_snippet: null,
    checked_at: null,
    notes,
  };

  return {
    name: record,
    title: record,
    organization: record,
    email: record,
    phone: record,
    source: record,
  };
}

function getValidation(row: ScoutResultRow): CandidateValidation {
  return row.validation ?? createFallbackValidation(row);
}

function getSourceUrl(record: CandidateValidation[keyof CandidateValidation], fallback: string | null): string {
  return record.source_url ?? fallback ?? '';
}

function getCheckedAt(validation: CandidateValidation): string {
  return (
    validation.source.checked_at ??
    validation.name.checked_at ??
    validation.title.checked_at ??
    validation.organization.checked_at ??
    validation.email.checked_at ??
    validation.phone.checked_at ??
    ''
  );
}

function getLeadName(row: ScoutResultRow): string {
  return isPersonLead(row) ? row.name : '';
}

function getTitle(row: ScoutResultRow): string {
  return isPersonLead(row) ? row.title : '';
}

function getOrganization(row: ScoutResultRow): string {
  if (isPersonLead(row)) {
    return row.organization;
  }

  if ('organization' in row && row.organization) {
    return row.organization;
  }

  if (row.candidate_category === 'not_found' || row.candidate_category === 'failed') {
    return row.searched_target;
  }

  return '';
}

function getEmail(row: ScoutResultRow, validation: CandidateValidation): string {
  if (!isPersonLead(row)) {
    return '';
  }

  if (validation.email.status === 'verified_found' || validation.email.status === 'deduced_with_pattern_evidence') {
    return row.email;
  }

  return '';
}

function getPhone(_row: ScoutResultRow): string {
  return '';
}

function getScore(row: ScoutResultRow, scoreKey: 'fit_score' | 'evidence_score' | 'contact_score'): string {
  if (!isPersonLead(row)) {
    return '';
  }

  return formatScore(row[scoreKey]);
}

function getValidationNotes(row: ScoutResultRow, validation: CandidateValidation, rankingGate: string): string {
  const category = row.candidate_category ?? 'person_lead';
  const fieldStatuses = [
    `name=${validation.name.status}`,
    `title=${validation.title.status}`,
    `organization=${validation.organization.status}`,
    `email=${validation.email.status}`,
    `phone=${validation.phone.status}`,
    `source=${validation.source.status}`,
  ].join('; ');

  const parts = [`Category: ${category}`, `Bucket: ${rankingGate}`];

  if (isPersonLead(row)) {
    parts.push(`Gate passed: ${row.gate_passed ? 'yes' : 'no'}`);
    parts.push(`Summary: ${row.explanation}`);
    parts.push(`Why target: ${row.why_target}`);
  } else if (row.candidate_category === 'organization_only') {
    parts.push(`Summary: ${row.explanation}`);
  } else if (row.candidate_category === 'not_found') {
    parts.push(`Summary: ${row.explanation}`);
  } else if (row.candidate_category === 'failed') {
    parts.push(`Failure: ${row.failure_reason}`);
    parts.push(`Summary: ${row.explanation}`);
  }

  if (!row.validation) {
    parts.push('Field-level validation was not captured for this row.');
  }

  parts.push(`Field statuses: ${fieldStatuses}`);
  parts.push(`Source note: ${validation.source.notes}`);

  return parts.join(' | ');
}

export function buildFullLeadExportRows({
  query,
  location,
  recipeName,
  runId,
  sortMode,
  rows,
  guardrail,
  generatedAt = new Date(),
}: BuildFullLeadExportRowsInput): FullLeadExportRow[] {
  const generatedAtLabel = generatedAt.toISOString();
  const guardrailContext = describeGuardrail(guardrail);

  return rows
    .map((row, index) => ({ row, index }))
    .sort((left, right) => {
      const bucketDelta =
        EXPORT_BUCKET_ORDER[getValidationBucket(left.row)] - EXPORT_BUCKET_ORDER[getValidationBucket(right.row)];
      if (bucketDelta !== 0) {
        return bucketDelta;
      }

      return left.index - right.index;
    })
    .map(({ row }, index) => {
      const validation = getValidation(row);
      const rankingGate = getValidationBucket(row);
      const sourceFallback = 'source_url' in row ? row.source_url ?? null : null;

      return {
        generatedAt: generatedAtLabel,
        sortMode,
        recipeName,
        query,
        location,
        runId,
        rank: String(index + 1),
        operatorLabel: TIER_LABELS[getOutputTier(row)],
        candidateCategory: row.candidate_category ?? 'person_lead',
        usableCandidate: isPersonLead(row) && rankingGate === 'usable' ? 'yes' : 'no',
        leadName: getLeadName(row),
        title: getTitle(row),
        organization: getOrganization(row),
        email: getEmail(row, validation),
        emailStatus: validation.email.status,
        phone: getPhone(row),
        phoneStatus: validation.phone.status,
        fitScore: getScore(row, 'fit_score'),
        evidenceScore: getScore(row, 'evidence_score'),
        contactScore: getScore(row, 'contact_score'),
        rankingGate,
        sourceNameUrl: getSourceUrl(validation.name, sourceFallback),
        sourceTitleUrl: getSourceUrl(validation.title, sourceFallback),
        sourceOrgUrl: getSourceUrl(validation.organization, sourceFallback),
        sourceEmailUrl: getSourceUrl(validation.email, sourceFallback),
        sourcePhoneUrl: getSourceUrl(validation.phone, sourceFallback),
        sourceAccessStatus: validation.source.status,
        validationNotes: [
          `Generated ${generatedAtLabel}.`,
          `Sort mode: ${sortMode}.`,
          guardrailContext,
          getValidationNotes(row, validation, rankingGate),
        ].join(' '),
        checkedAt: getCheckedAt(validation),
      };
    });
}

export function buildFullLeadExportCsv(rows: FullLeadExportRow[]): string {
  const headers = [
    'lead_name',
    'title',
    'organization',
    'email',
    'email_status',
    'phone',
    'phone_status',
    'usable_candidate',
    'operator_label',
    'candidate_category',
    'rank',
    'query',
    'run_id',
    'fit_score',
    'evidence_score',
    'contact_score',
    'ranking_gate',
    'source_name_url',
    'source_title_url',
    'source_org_url',
    'source_email_url',
    'source_phone_url',
    'source_access_status',
    'validation_notes',
    'checked_at',
    'location',
    'recipe_name',
    'sort_mode',
    'generated_at',
  ];

  const body = rows.map((row) =>
    [
      row.leadName,
      row.title,
      row.organization,
      row.email,
      row.emailStatus,
      row.phone,
      row.phoneStatus,
      row.usableCandidate,
      row.operatorLabel,
      row.candidateCategory,
      row.rank,
      row.query,
      row.runId,
      row.fitScore,
      row.evidenceScore,
      row.contactScore,
      row.rankingGate,
      row.sourceNameUrl,
      row.sourceTitleUrl,
      row.sourceOrgUrl,
      row.sourceEmailUrl,
      row.sourcePhoneUrl,
      row.sourceAccessStatus,
      row.validationNotes,
      row.checkedAt,
      row.location,
      row.recipeName,
      row.sortMode,
      row.generatedAt,
    ]
      .map(escapeCsvCell)
      .join(','),
  );

  return [headers.join(','), ...body].join('\n');
}

export function buildFullLeadExportFilename(generatedAt = new Date()): string {
  return `white-rabbit-lead-export-${generatedAt.toISOString().slice(0, 10)}.csv`;
}
