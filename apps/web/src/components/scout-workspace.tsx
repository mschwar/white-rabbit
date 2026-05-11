'use client';

import { FormEvent, useEffect, useState } from 'react';
import ScoutResultsTable from '@/components/scout-results-table';
import {
  buildScoutPayload,
  buildFullPayload,
  buildTierDistribution,
  closeRecipeRun,
  DEFAULT_SCOUT_LOCATION,
  DEFAULT_SCOUT_QUERY,
  fetchSandboxUsage,
  LEAD_SORT_OPTIONS,
  isPersonLead,
  getValidationBucket,
  sortScoutResultRows,
  OUTPUT_TIERS,
  TIER_LABELS,
  CORRECTION_FIELD_OPTIONS,
  CORRECTION_LABEL_OPTIONS,
  fetchRunCorrections,
  submitLeadFeedback,
  submitLeadCorrection,
  type CandidateValidation,
  type CorrectionField,
  type CorrectionLabel,
  type FeedbackLabel,
  type LeadSortMode,
  type ContactStatus,
  type ScoutResultRow,
  type ScoutResponse,
  type ValidationStatus,
  type FullResponse,
} from '@/lib/scout';
import {
  buildFullLeadExportCsv,
  buildFullLeadExportFilename,
  buildFullLeadExportRows,
} from '@/lib/full-export';

function formatElapsedSeconds(seconds: number): string {
  return `${seconds.toFixed(2)}s`;
}

type Mode = 'scout' | 'full';

type ScoutWorkspaceProps = {
  primaryMode?: boolean;
};

function mapErrorCodeToMessage(errorCode: string | null, fallback: string): string {
  switch (errorCode) {
    case 'tavily_failed':
      return 'Search engine is rate-limited; try again in ~60s';
    case 'openai_failed':
      return 'AI extraction service is unavailable; try again in a moment';
    case 'llm_parse_failed':
      return 'AI response could not be parsed; try a simpler query';
    case 'orchestrator_error':
      return `Search service error: ${fallback}`;
    case 'internal_error':
      return 'An unexpected error occurred. Please try again later.';
    default:
      return fallback;
  }
}

type ValidationOverrides = {
  name?: ValidationStatus;
  title?: ValidationStatus;
  organization?: ValidationStatus;
  email?: ContactStatus;
  phone?: ContactStatus;
  source?: ValidationStatus;
};

function makeValidation(overrides: ValidationOverrides = {}): CandidateValidation {
  const field = (status: ValidationStatus, label: string) => ({
    status,
    source_url: `https://validation.example.com/${label}`,
    evidence_snippet: `${label} ${status} evidence`,
    checked_at: '2026-05-10T12:00:00Z',
    notes: `${label} ${status} notes`,
  });

  const contact = (status: ContactStatus, label: string) => ({
    status,
    source_url: `https://validation.example.com/${label}`,
    evidence_snippet: `${label} ${status} evidence`,
    checked_at: '2026-05-10T12:00:00Z',
    notes: `${label} ${status} notes`,
  });

  return {
    name: field(overrides.name ?? 'supported', 'name'),
    title: field(overrides.title ?? 'supported', 'title'),
    organization: field(overrides.organization ?? 'supported', 'organization'),
    email: contact(overrides.email ?? 'verified_found', 'email'),
    phone: contact(overrides.phone ?? 'missing', 'phone'),
    source: field(overrides.source ?? 'supported', 'source'),
  };
}

function formatEvidenceStatusLabel(status: string): string {
  switch (status) {
    case 'verified_found':
      return 'verified found';
    case 'deduced_with_pattern_evidence':
      return 'deduced with pattern evidence';
    default:
      return status.replaceAll('_', ' ');
  }
}

const EVIDENCE_STATUS_TONES: Record<string, string> = {
  supported: 'border-emerald-400/20 bg-emerald-400/10 text-emerald-100',
  verified_found: 'border-emerald-400/20 bg-emerald-400/10 text-emerald-100',
  deduced_with_pattern_evidence: 'border-cyan-400/20 bg-cyan-400/10 text-cyan-100',
  missing: 'border-amber-400/20 bg-amber-400/10 text-amber-100',
  unsupported: 'border-zinc-400/20 bg-zinc-400/10 text-zinc-100',
  failed: 'border-rose-400/20 bg-rose-400/10 text-rose-100',
};

function evidenceTone(status: string): string {
  return EVIDENCE_STATUS_TONES[status] ?? EVIDENCE_STATUS_TONES.unsupported;
}

function getEvidenceRowIdentity(row: ScoutResultRow): string {
  if (row.candidate_category === 'organization_only') {
    return row.organization ?? '—';
  }

  if (row.candidate_category === 'not_found' || row.candidate_category === 'failed') {
    return row.searched_target ?? '—';
  }

  return row.name;
}

function getEvidenceRowSummary(row: ScoutResultRow): string {
  if (isPersonLead(row)) {
    return row.title;
  }

  if (row.candidate_category === 'organization_only') {
    return row.explanation;
  }

  if (row.candidate_category === 'not_found') {
    return `${row.organization ?? row.searched_target} was searched, but no acceptable contact was found.`;
  }

  return `${row.failure_reason} ${row.explanation}`.trim();
}

function getCorrectionDefaultField(row: ScoutResultRow): CorrectionField {
  if (isPersonLead(row)) {
    return 'title';
  }

  if (row.candidate_category === 'organization_only') {
    return 'organization';
  }

  if (row.candidate_category === 'not_found') {
    return 'organization';
  }

  return 'source';
}

function getCorrectionFieldValue(row: ScoutResultRow, fieldName: CorrectionField): string {
  if (isPersonLead(row)) {
    switch (fieldName) {
      case 'name':
        return row.name;
      case 'title':
        return row.title;
      case 'organization':
        return row.organization;
      case 'email':
        return row.email;
      case 'phone':
        return '';
      case 'source':
        return row.source_url;
    }
  }

  if (row.candidate_category === 'organization_only') {
    switch (fieldName) {
      case 'name':
        return row.organization;
      case 'title':
        return row.explanation;
      case 'organization':
        return row.organization;
      case 'email':
        return 'missing';
      case 'phone':
        return 'missing';
      case 'source':
        return row.source_url ?? '';
    }
  }

  if (row.candidate_category === 'not_found') {
    switch (fieldName) {
      case 'name':
      case 'title':
        return row.searched_target;
      case 'organization':
        return row.organization ?? row.searched_target;
      case 'email':
      case 'phone':
        return 'missing';
      case 'source':
        return row.source_url ?? '';
    }
  }

  switch (fieldName) {
    case 'name':
    case 'title':
      return row.searched_target;
    case 'organization':
      return row.organization ?? row.searched_target;
      case 'email':
      case 'phone':
        return '';
      case 'source':
        return row.source_url ?? '';
  }
}

function getEvidenceValidation(row: ScoutResultRow): CandidateValidation {
  if (row.validation) {
    return row.validation;
  }

  const sourceUrl = 'source_url' in row ? row.source_url ?? null : null;
  const notes = sourceUrl
    ? 'Field-level validation was not captured for this row.'
    : 'No source URL was captured for this row.';
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

function renderEvidenceField(
  label: string,
  record: CandidateValidation[keyof CandidateValidation],
) {
  return (
    <article key={label} className={`rounded-3xl border p-4 ${evidenceTone(record.status)}`}>
      <div className="flex items-start justify-between gap-3">
        <div>
          <p className="text-sm font-semibold text-zinc-50">{label}</p>
          <p className="mt-1 text-xs uppercase tracking-[0.18em] text-current/80">Status</p>
        </div>
        <span className="rounded-full border px-2 py-1 text-[11px] font-semibold uppercase tracking-[0.16em]">
          {formatEvidenceStatusLabel(record.status)}
        </span>
      </div>

      <dl className="mt-4 space-y-3 text-sm text-zinc-200">
        <div className="space-y-1">
          <dt className="text-[11px] font-semibold uppercase tracking-[0.18em] text-zinc-500">Source URL</dt>
          <dd className="break-all leading-6 text-zinc-100">
            {record.source_url ? (
              <a className="text-emerald-300 underline decoration-emerald-300/30 underline-offset-4" href={record.source_url} rel="noreferrer" target="_blank">
                {record.source_url}
              </a>
            ) : (
              <span className="text-zinc-500">No source URL captured</span>
            )}
          </dd>
        </div>
        <div className="space-y-1">
          <dt className="text-[11px] font-semibold uppercase tracking-[0.18em] text-zinc-500">Checked at</dt>
          <dd className="leading-6 text-zinc-100">{record.checked_at ?? '—'}</dd>
        </div>
        <div className="space-y-1">
          <dt className="text-[11px] font-semibold uppercase tracking-[0.18em] text-zinc-500">Notes</dt>
          <dd className="leading-6 text-zinc-100">{record.notes || '—'}</dd>
        </div>
        <div className="space-y-1">
          <dt className="text-[11px] font-semibold uppercase tracking-[0.18em] text-zinc-500">Evidence snippet</dt>
          <dd className="leading-6 text-zinc-100">{record.evidence_snippet || '—'}</dd>
        </div>
      </dl>
    </article>
  );
}

function ScoutEvidenceDrawer({
  row,
  runId,
  query,
  onClose,
}: {
  row: ScoutResultRow | null;
  runId: string | null;
  query: string | null;
  onClose: () => void;
}) {
  const [correctionLabel, setCorrectionLabel] = useState<CorrectionLabel>('wrong_persona');
  const [correctionField, setCorrectionField] = useState<CorrectionField>(row ? getCorrectionDefaultField(row) : 'title');
  const [correctionPreviousValue, setCorrectionPreviousValue] = useState('');
  const [correctionCorrectedValue, setCorrectionCorrectedValue] = useState('');
  const [correctionNotes, setCorrectionNotes] = useState('');
  const [correctionMessage, setCorrectionMessage] = useState<string | null>(null);
  const [isSubmittingCorrection, setIsSubmittingCorrection] = useState(false);
  const [isLoadingQueue, setIsLoadingQueue] = useState(false);
  const [correctionExport, setCorrectionExport] = useState<{
    filename: string;
    dataUrl: string;
    rowCount: number;
  } | null>(null);

  useEffect(() => {
    if (!row) {
      return undefined;
    }

    const defaultField = getCorrectionDefaultField(row);
    setCorrectionLabel('wrong_persona');
    setCorrectionField(defaultField);
    setCorrectionPreviousValue(getCorrectionFieldValue(row, defaultField));
    setCorrectionCorrectedValue('');
    setCorrectionNotes('');
    setCorrectionMessage(null);
    setCorrectionExport(null);

    const handleKeyDown = (event: KeyboardEvent) => {
      if (event.key === 'Escape') {
        onClose();
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [onClose, row]);

  useEffect(() => {
    if (!row) {
      return;
    }

    setCorrectionPreviousValue(getCorrectionFieldValue(row, correctionField));
  }, [correctionField, row]);

  if (!row) {
    return null;
  }

  const currentRow = row;

  const validation = getEvidenceValidation(currentRow);
  const fields = [
    { label: 'Name', record: validation.name },
    { label: 'Title', record: validation.title },
    { label: 'Organization', record: validation.organization },
    { label: 'Email', record: validation.email },
    { label: 'Phone', record: validation.phone },
    { label: 'Source', record: validation.source },
  ] as const;

  async function refreshCorrectionQueueExport(prefixMessage?: string) {
    if (!runId) {
      setCorrectionMessage('Run Full to export the correction queue.');
      return;
    }

    setIsLoadingQueue(true);
    setCorrectionMessage(null);
    try {
      const queue = await fetchRunCorrections(runId);
      const json = JSON.stringify(queue, null, 2);
      setCorrectionExport({
        filename: `white-rabbit-corrections-${runId}.json`,
        dataUrl: `data:application/json;charset=utf-8,${encodeURIComponent(json)}`,
        rowCount: queue.length,
      });
      const queueMessage =
        queue.length > 0
          ? `Loaded ${queue.length} correction${queue.length === 1 ? '' : 's'} from the review queue.`
          : 'Review queue is empty.';
      setCorrectionMessage(prefixMessage ? `${prefixMessage} ${queueMessage}` : queueMessage);
    } catch (error) {
      setCorrectionMessage(error instanceof Error ? error.message : 'Failed to fetch correction queue.');
    } finally {
      setIsLoadingQueue(false);
    }
  }

  async function handleSubmitCorrection(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();

    if (!currentRow.id || !runId || !query) {
      setCorrectionMessage('Run a Full search first so this correction is tied to a saved run.');
      return;
    }

    setIsSubmittingCorrection(true);
    setCorrectionMessage(null);
    try {
      const correction = await submitLeadCorrection(currentRow.id, {
        run_id: runId,
        query,
        label: correctionLabel,
        field_name: correctionField,
        previous_value: correctionPreviousValue.trim() || undefined,
        corrected_value: correctionCorrectedValue.trim() || undefined,
        notes: correctionNotes.trim() || undefined,
      });

      setCorrectionCorrectedValue('');
      setCorrectionNotes('');
      await refreshCorrectionQueueExport(`Saved ${correction.label.replaceAll('_', ' ')} correction for ${correction.field_name}.`);
    } catch (error) {
      setCorrectionMessage(error instanceof Error ? error.message : 'Failed to save correction.');
    } finally {
      setIsSubmittingCorrection(false);
    }
  }

  return (
    <div
      className="fixed inset-0 z-50 flex items-stretch justify-end bg-black/70 p-4 backdrop-blur-sm sm:p-6"
      onClick={onClose}
    >
      <div
        aria-describedby="evidence-drawer-summary"
        aria-labelledby="evidence-drawer-title"
        aria-modal="true"
        className="flex h-full w-full max-w-3xl flex-col overflow-hidden rounded-[2rem] border border-white/10 bg-zinc-950 shadow-2xl shadow-black/60"
        onClick={(event) => event.stopPropagation()}
        role="dialog"
      >
        <div className="flex items-start justify-between gap-4 border-b border-white/10 p-6">
          <div>
            <p className="text-xs font-semibold uppercase tracking-[0.22em] text-emerald-300">Evidence drawer</p>
            <h3 id="evidence-drawer-title" className="mt-2 text-2xl font-semibold tracking-tight text-zinc-50">
              {getEvidenceRowIdentity(row)}
            </h3>
            <p id="evidence-drawer-summary" className="mt-2 text-sm leading-6 text-zinc-400">
              {getEvidenceRowSummary(row)}
            </p>
          </div>
          <button
            className="rounded-full border border-white/10 bg-white/5 px-4 py-2 text-sm font-semibold text-zinc-200 transition hover:bg-white/10"
            onClick={onClose}
            type="button"
          >
            Close
          </button>
        </div>

        <div className="flex-1 overflow-y-auto p-6">
          <div className="mb-4 flex flex-wrap items-center gap-2">
            <span className="rounded-full border border-white/10 bg-white/5 px-3 py-1 text-xs font-semibold uppercase tracking-[0.16em] text-zinc-200">
              {row.candidate_category ?? 'person_lead'}
            </span>
            <span className="rounded-full border border-white/10 bg-white/5 px-3 py-1 text-xs font-semibold uppercase tracking-[0.16em] text-zinc-200">
              {getValidationBucket(row)}
            </span>
          </div>

          <div className="grid gap-4 md:grid-cols-2">
            {fields.map(({ label, record }) => renderEvidenceField(label, record))}
          </div>

          <div className="mt-6 rounded-3xl border border-white/10 bg-white/5 p-5">
            <div className="flex flex-col gap-2 sm:flex-row sm:items-end sm:justify-between">
              <div>
                <p className="text-xs font-semibold uppercase tracking-[0.22em] text-emerald-300">Correction loop</p>
                <h4 className="mt-2 text-lg font-semibold text-zinc-50">Record a field-level correction</h4>
                <p className="mt-1 text-sm leading-6 text-zinc-400">
                  Save the operator correction against this Full run, then export the queue as JSON for benchmark review.
                </p>
              </div>
              {runId ? (
                <button
                  className="rounded-full border border-white/10 bg-white/5 px-4 py-2 text-xs font-semibold uppercase tracking-[0.18em] text-zinc-200 transition hover:bg-white/10 disabled:cursor-not-allowed disabled:opacity-60"
                  disabled={isLoadingQueue}
                  onClick={() => {
                    void refreshCorrectionQueueExport();
                  }}
                  type="button"
                >
                  {isLoadingQueue ? 'Loading queue…' : 'Download review queue'}
                </button>
              ) : null}
            </div>

            {runId && query ? (
              <form className="mt-4 grid gap-4" onSubmit={handleSubmitCorrection}>
                <div className="grid gap-4 sm:grid-cols-2">
                  <label className="flex flex-col gap-2 text-sm text-zinc-200" htmlFor="correctionLabel">
                    Correction type
                    <select
                      className="rounded-2xl border border-white/10 bg-zinc-950/70 px-4 py-3 text-zinc-50 outline-none focus:border-emerald-400"
                      id="correctionLabel"
                      onChange={(event) => setCorrectionLabel(event.target.value as CorrectionLabel)}
                      value={correctionLabel}
                    >
                      {CORRECTION_LABEL_OPTIONS.map((option) => (
                        <option key={option.value} value={option.value}>
                          {option.label}
                        </option>
                      ))}
                    </select>
                  </label>
                  <label className="flex flex-col gap-2 text-sm text-zinc-200" htmlFor="correctionField">
                    Corrected field
                    <select
                      className="rounded-2xl border border-white/10 bg-zinc-950/70 px-4 py-3 text-zinc-50 outline-none focus:border-emerald-400"
                      id="correctionField"
                      onChange={(event) => setCorrectionField(event.target.value as CorrectionField)}
                      value={correctionField}
                    >
                      {CORRECTION_FIELD_OPTIONS.map((option) => (
                        <option key={option.value} value={option.value}>
                          {option.label}
                        </option>
                      ))}
                    </select>
                  </label>
                </div>
                <div className="grid gap-4 sm:grid-cols-2">
                  <label className="flex flex-col gap-2 text-sm text-zinc-200" htmlFor="correctionPreviousValue">
                    Previous value
                    <input
                      className="rounded-2xl border border-white/10 bg-zinc-950/70 px-4 py-3 text-zinc-50 outline-none placeholder:text-zinc-500 focus:border-emerald-400"
                      id="correctionPreviousValue"
                      onChange={(event) => setCorrectionPreviousValue(event.target.value)}
                      placeholder="Value before correction"
                      value={correctionPreviousValue}
                    />
                  </label>
                  <label className="flex flex-col gap-2 text-sm text-zinc-200" htmlFor="correctionCorrectedValue">
                    Corrected value
                    <input
                      className="rounded-2xl border border-white/10 bg-zinc-950/70 px-4 py-3 text-zinc-50 outline-none placeholder:text-zinc-500 focus:border-emerald-400"
                      id="correctionCorrectedValue"
                      onChange={(event) => setCorrectionCorrectedValue(event.target.value)}
                      placeholder="Value after correction"
                      value={correctionCorrectedValue}
                    />
                  </label>
                </div>
                <label className="flex flex-col gap-2 text-sm text-zinc-200" htmlFor="correctionNotes">
                  Notes
                  <textarea
                    className="min-h-28 rounded-2xl border border-white/10 bg-zinc-950/70 px-4 py-3 text-zinc-50 outline-none placeholder:text-zinc-500 focus:border-emerald-400"
                    id="correctionNotes"
                    onChange={(event) => setCorrectionNotes(event.target.value)}
                    placeholder="Why this row needs to be corrected"
                    value={correctionNotes}
                  />
                </label>

                <div className="flex flex-wrap items-center gap-3">
                  <button
                    className="rounded-full bg-emerald-400 px-4 py-2 text-sm font-semibold text-emerald-950 transition hover:bg-emerald-300 disabled:cursor-not-allowed disabled:bg-emerald-300/60"
                    disabled={isSubmittingCorrection}
                    type="submit"
                  >
                    {isSubmittingCorrection ? 'Saving…' : 'Save correction'}
                  </button>
                  {correctionExport ? (
                    <a
                      className="rounded-full border border-emerald-300/30 bg-white/5 px-4 py-2 text-sm font-semibold text-emerald-100 transition hover:bg-emerald-400/10"
                      download={correctionExport.filename}
                      href={correctionExport.dataUrl}
                    >
                      Download review queue JSON
                    </a>
                  ) : null}
                </div>
              </form>
            ) : (
              <p className="mt-4 text-sm leading-6 text-zinc-400">
                Run Full first so corrections are stored against a saved run and query snapshot.
              </p>
            )}

            {correctionMessage ? <p className="mt-4 text-sm leading-6 text-emerald-200">{correctionMessage}</p> : null}
          </div>
        </div>
      </div>
    </div>
  );
}

const QA_VALIDATION_BUCKETS_FIXTURE: ScoutResponse = {
  leads: [
    {
      id: 'qa-usable-1',
      candidate_category: 'person_lead',
      tier: 'high_trust_usable',
      primary_filter_reason: 'READY: supported person, organization, source, and usable contact cleared the evidence gate.',
      name: 'Jane Smith',
      title: 'Director of Technology',
      organization: 'Albuquerque Public Schools',
      email: 'jane.smith@aps.edu',
      email_status: 'Found',
      source_url: 'https://aps.edu/jane-smith',
      confidence: 0.92,
      why_target: 'Strong district fit with current leadership evidence and usable email.',
      icebreaker: 'Mentioned in a district technology initiative note.',
      fit_score: 0.91,
      evidence_score: 0.84,
      contact_score: 0.79,
      gate_passed: true,
      explanation: 'Strong district fit with current leadership evidence and usable email.',
      validation: makeValidation(),
    },
    {
      id: 'qa-noisy-1',
      candidate_category: 'person_lead',
      tier: 'review',
      primary_filter_reason: 'REVIEW: contact is missing; row is not CRM-ready.',
      name: 'Noisy Lead',
      title: 'Director of Operations',
      organization: 'Noisy Schools',
      email: 'noisy@example.com',
      email_status: 'Found',
      source_url: 'https://noisy.example.com',
      confidence: 0.44,
      why_target: 'Weak fit',
      icebreaker: 'Weak fit',
      fit_score: 0.31,
      evidence_score: 0.24,
      contact_score: 0.2,
      gate_passed: false,
      explanation: 'Person lead that did not clear the gate.',
      validation: makeValidation({
        name: 'supported',
        title: 'supported',
        organization: 'supported',
        email: 'verified_found',
        phone: 'missing',
        source: 'supported',
      }),
    },
    {
      candidate_category: 'organization_only',
      tier: 'organization_only',
      primary_filter_reason: 'Organization was found, but no validated person was ready.',
      organization: 'Example Corp',
      source_url: 'https://example.com',
      explanation: 'Organization-only row.',
      validation: makeValidation({
        name: 'unsupported',
        title: 'unsupported',
        organization: 'supported',
        email: 'missing',
        phone: 'missing',
        source: 'supported',
      }),
    },
    {
      candidate_category: 'not_found',
      tier: 'not_found',
      primary_filter_reason: 'Target was searched, but no acceptable contact was found.',
      searched_target: 'Ghost District',
      organization: 'Ghost District',
      source_url: 'https://ghost.example.com',
      explanation: 'No acceptable contact was found.',
      validation: makeValidation({
        name: 'unsupported',
        title: 'unsupported',
        organization: 'unsupported',
        email: 'missing',
        phone: 'missing',
        source: 'supported',
      }),
    },
    {
      candidate_category: 'failed',
      tier: 'failed',
      primary_filter_reason: 'Source was inaccessible.',
      searched_target: 'Broken District',
      failure_reason: 'Source was inaccessible.',
      organization: 'Broken District',
      source_url: 'https://broken.example.com',
      explanation: 'The candidate could not be trusted.',
      validation: makeValidation({
        name: 'unsupported',
        title: 'unsupported',
        organization: 'unsupported',
        email: 'failed',
        phone: 'failed',
        source: 'failed',
      }),
    },
  ],
  metrics: {
    input_tokens: 820,
    output_tokens: 420,
    tavily_searches: 3,
    elapsed_seconds: 9.84,
    estimated_cost_usd: 0.1234,
    tier_distribution: {
      high_trust_usable: 1,
      review: 1,
      organization_only: 1,
      not_found: 1,
      failed: 1,
    },
  },
  query_guardrail: null,
  sandbox_usage: null,
};

export default function ScoutWorkspace({ primaryMode = false }: ScoutWorkspaceProps) {
  const [query, setQuery] = useState(DEFAULT_SCOUT_QUERY);
  const [location, setLocation] = useState(primaryMode ? '' : DEFAULT_SCOUT_LOCATION);
  const [recipeName, setRecipeName] = useState('');
  const [mode, setMode] = useState<Mode>('scout');
  const [results, setResults] = useState<ScoutResponse | null>(null);
  const [fullResult, setFullResult] = useState<FullResponse | null>(null);
  const [queryGuardrail, setQueryGuardrail] = useState<ScoutResponse['query_guardrail']>(null);
  const [sandboxUsage, setSandboxUsage] = useState<ScoutResponse['sandbox_usage']>(null);
  const [operatorMinutes, setOperatorMinutes] = useState('');
  const [closeMessage, setCloseMessage] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [sortMode, setSortMode] = useState<LeadSortMode>('rank');
  const [isClosing, setIsClosing] = useState(false);
  const [leadExport, setLeadExport] = useState<{
    filename: string;
    csvDataUrl: string;
    generatedAtLabel: string;
    rowCount: number;
  } | null>(null);
  const [selectedEvidenceRow, setSelectedEvidenceRow] = useState<ScoutResultRow | null>(null);
  const [submittedQuery, setSubmittedQuery] = useState<string | null>(null);
  const [submittedLocation, setSubmittedLocation] = useState<string | null>(null);
  const [submittedRecipeName, setSubmittedRecipeName] = useState<string | null>(null);
  const [feedbackState, setFeedbackState] = useState<Record<string, string | null>>({});
  const queryLabel = primaryMode ? 'Lead search' : 'Prospecting query';

  useEffect(() => {
    fetchSandboxUsage()
      .then(setSandboxUsage)
      .catch(() => undefined);
  }, []);

  useEffect(() => {
    if (process.env.NODE_ENV !== 'production' && window.location.search.includes('qa=validation-buckets')) {
      setMode('full');
    }
  }, []);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();

    const payload = primaryMode || mode === 'scout'
      ? buildScoutPayload(query, location)
      : buildFullPayload(query, location, recipeName);

    if (!payload) {
      setError('Enter a query before searching.');
      setResults(null);
      setFullResult(null);
      return;
    }

    const submittedQuery = payload.query;
    const submittedLocation = payload.filters?.location ?? '';
    const submittedRecipeName = payload.recipe_name ?? payload.query;

    setIsLoading(true);
    setError(null);
    setResults(null);
    setFullResult(null);
    setLeadExport(null);
    setSelectedEvidenceRow(null);
    setSubmittedQuery(null);
    setSubmittedLocation(null);
    setSubmittedRecipeName(null);
    setQueryGuardrail(null);

    try {
      if (process.env.NODE_ENV !== 'production' && window.location.search.includes('qa=validation-buckets')) {
        const fixtureResult: FullResponse = {
          run_id: 'qa-validation-buckets-run',
          recipe_id: 'qa-validation-buckets-recipe',
          leads: QA_VALIDATION_BUCKETS_FIXTURE.leads,
          metrics: QA_VALIDATION_BUCKETS_FIXTURE.metrics,
          query_guardrail: null,
          sandbox_usage: null,
        };

        setResults(QA_VALIDATION_BUCKETS_FIXTURE);
        if (!primaryMode && mode === 'full') {
          setFullResult(fixtureResult);
          setSubmittedQuery(submittedQuery);
          setSubmittedLocation(submittedLocation);
          setSubmittedRecipeName(submittedRecipeName);
        }
        setQueryGuardrail(null);
        setSandboxUsage(null);
        return;
      }

      const endpoint = mode === 'scout' ? '/api/scout' : '/api/full';
      const response = await fetch(endpoint, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(payload),
      });

      if (!response.ok) {
        const bodyText = await response.text();
        let message = `Search failed (${response.status}).`;
        let guardrail: ScoutResponse['query_guardrail'] = null;
        let usage: ScoutResponse['sandbox_usage'] = null;
        let errorCode: string | null = null;
        let requestId: string | null = null;

        if (bodyText) {
          try {
            const body = JSON.parse(bodyText) as {
              error?: string;
              detail?: unknown;
              query_guardrail?: ScoutResponse['query_guardrail'];
              sandbox_usage?: ScoutResponse['sandbox_usage'];
              error_code?: string;
              request_id?: string;
            };
            guardrail = body.query_guardrail ?? null;
            usage = body.sandbox_usage ?? null;
            errorCode = body.error_code ?? null;
            requestId = body.request_id ?? null;
            if (typeof body.detail === 'string') {
              message = body.detail;
            } else if (body.detail && typeof body.detail === 'object') {
              const detail = body.detail as { error?: string; detail?: unknown; sandbox_usage?: ScoutResponse['sandbox_usage']; error_code?: string; request_id?: string };
              message = detail.error ?? message;
              usage = detail.sandbox_usage ?? usage;
              errorCode = detail.error_code ?? errorCode;
              requestId = detail.request_id ?? requestId;
            }
            message = body.error ?? message;
          } catch {
            message = bodyText;
          }
        }

        setQueryGuardrail(guardrail);
        if (usage) {
          setSandboxUsage(usage);
        }
        throw new Error(JSON.stringify({ message, errorCode, requestId }));
      }

      if (mode === 'scout') {
        const data = (await response.json()) as ScoutResponse;
        setResults(data);
        setQueryGuardrail(data.query_guardrail ?? null);
        setSandboxUsage(data.sandbox_usage ?? null);
      } else {
        const data = (await response.json()) as FullResponse;
        setFullResult(data);
        setResults({ leads: data.leads, metrics: data.metrics, query_guardrail: data.query_guardrail ?? null });
        setQueryGuardrail(data.query_guardrail ?? null);
        setSandboxUsage(data.sandbox_usage ?? null);
        setCloseMessage(null);
        setSubmittedQuery(submittedQuery);
        setSubmittedLocation(submittedLocation);
        setSubmittedRecipeName(submittedRecipeName);
      }
    } catch (err) {
      let message = err instanceof Error ? err.message : 'Search failed.';
      let errorCode: string | null = null;
      let requestId: string | null = null;
      try {
        const parsed = JSON.parse(message);
        if (parsed && typeof parsed === 'object') {
          message = parsed.message ?? message;
          errorCode = parsed.errorCode ?? null;
          requestId = parsed.requestId ?? null;
        }
      } catch {
        // Not JSON — keep raw message
      }

      const userMessage = mapErrorCodeToMessage(errorCode, message);
      setError(userMessage);
      setResults(null);
      setFullResult(null);
    } finally {
      setIsLoading(false);
    }
  }

  async function handleCloseRun() {
    if (!fullResult) {
      return;
    }

    const parsed = Number.parseFloat(operatorMinutes);
    if (!Number.isFinite(parsed) || parsed <= 0) {
      setCloseMessage('Enter operator minutes greater than 0.');
      return;
    }

    setIsClosing(true);
    setCloseMessage(null);
    try {
      await closeRecipeRun(fullResult.run_id, parsed);
      setCloseMessage(`Run closed with ${parsed.toFixed(1)} operator minutes.`);
    } catch (err) {
      setCloseMessage(err instanceof Error ? err.message : 'Failed to close run.');
    } finally {
      setIsClosing(false);
    }
  }

  async function handleLeadFeedback(leadId: string, label: FeedbackLabel) {
    await submitLeadFeedback(leadId, label);
    setFeedbackState((prev) => ({ ...prev, [leadId]: label }));
  }

  function handleOpenEvidence(row: ScoutResultRow) {
    setSelectedEvidenceRow(row);
  }

  async function handleBuildLeadExport() {
    if (!fullResult || !displayedResults) {
      return;
    }

    const generatedAt = new Date();
    const exportRows = buildFullLeadExportRows({
      query: submittedQuery ?? query,
      location: submittedLocation ?? location,
      recipeName: submittedRecipeName ?? (recipeName || query),
      runId: fullResult.run_id,
      sortMode,
      rows: displayedRows,
      guardrail: fullResult.query_guardrail ?? null,
      generatedAt,
    });

    const csv = buildFullLeadExportCsv(exportRows);
    setLeadExport({
      filename: buildFullLeadExportFilename(generatedAt),
      csvDataUrl: `data:text/csv;charset=utf-8,${encodeURIComponent(csv)}`,
      generatedAtLabel: generatedAt.toLocaleString(),
      rowCount: exportRows.length,
    });
  }

  const displayedResults = results;
  const displayedRows = displayedResults ? sortScoutResultRows(displayedResults.leads, sortMode) : [];
  const tierDistribution = displayedResults
    ? buildTierDistribution(displayedResults.leads, displayedResults.metrics.tier_distribution)
    : null;

  return (
    <main className="min-h-screen bg-zinc-950 px-6 py-10 text-zinc-50">
      <section className="mx-auto flex w-full max-w-6xl flex-col gap-8 rounded-[2rem] border border-white/10 bg-white/5 p-8 shadow-2xl shadow-black/20 backdrop-blur sm:p-10">
        <div className="space-y-3">
          <p className="text-sm font-medium uppercase tracking-[0.22em] text-emerald-300">Lead search</p>
          <h1 className="text-4xl font-semibold tracking-tight sm:text-5xl">Find source-backed prospects</h1>
          <p className="max-w-3xl text-base leading-7 text-zinc-300 sm:text-lg">
            Run a focused B2B target query and review returned rows by readiness tier, evidence support, and contact readiness.
          </p>
        </div>

        <div className="grid gap-4 lg:grid-cols-[1.1fr_0.9fr]">
          <section className="rounded-3xl border border-white/10 bg-zinc-950/70 p-6">
            <p className="text-sm font-medium uppercase tracking-[0.18em] text-zinc-400">
              {primaryMode ? 'Start a lead search' : 'Start a query'}
            </p>
            <form className="mt-4 grid gap-5" onSubmit={handleSubmit}>
              {!primaryMode && (
                <div className="flex gap-2">
                  <button
                    type="button"
                    onClick={() => setMode('scout')}
                    className={`flex-1 rounded-full px-4 py-2 text-sm font-semibold transition ${
                      mode === 'scout'
                        ? 'bg-emerald-400 text-emerald-950'
                        : 'bg-white/5 text-zinc-300 hover:bg-white/10'
                    }`}
                  >
                    Scout
                  </button>
                  <button
                    type="button"
                    onClick={() => setMode('full')}
                    className={`flex-1 rounded-full px-4 py-2 text-sm font-semibold transition ${
                      mode === 'full'
                        ? 'bg-emerald-400 text-emerald-950'
                        : 'bg-white/5 text-zinc-300 hover:bg-white/10'
                    }`}
                  >
                    Full
                  </button>
                </div>
              )}

              {!primaryMode && mode === 'full' && (
                <div className="flex flex-col gap-3 text-sm text-zinc-200">
                  <label className="block font-medium" htmlFor="recipeName">
                    Search label
                  </label>
                  <input
                    className="w-full rounded-2xl border border-white/10 bg-white/5 px-4 py-3 text-zinc-50 outline-none ring-0 placeholder:text-zinc-500 focus:border-emerald-400"
                    id="recipeName"
                    name="recipeName"
                    onChange={(event) => setRecipeName(event.target.value)}
                    placeholder="Phoenix healthcare leaders"
                    value={recipeName}
                  />
                </div>
              )}

              <div className="flex flex-col gap-3 text-sm text-zinc-200">
                <label className="block font-medium" htmlFor="query">
                  {queryLabel}
                </label>
                <input
                  className="w-full rounded-2xl border border-white/10 bg-white/5 px-4 py-3 text-zinc-50 outline-none ring-0 placeholder:text-zinc-500 focus:border-emerald-400"
                  id="query"
                  name="query"
                  onChange={(event) => setQuery(event.target.value)}
                  placeholder="Healthcare IT directors in Phoenix"
                  value={query}
                />
              </div>
              {!primaryMode && (
                <div className="flex flex-col gap-3 text-sm text-zinc-200">
                  <label className="block font-medium" htmlFor="location">
                    Location / filter
                  </label>
                  <input
                    className="w-full rounded-2xl border border-white/10 bg-white/5 px-4 py-3 text-zinc-50 outline-none ring-0 placeholder:text-zinc-500 focus:border-emerald-400"
                    id="location"
                    name="location"
                    onChange={(event) => setLocation(event.target.value)}
                    placeholder="New Mexico"
                    value={location}
                  />
                </div>
              )}
              {error ? (
                <p className="rounded-2xl border border-rose-500/30 bg-rose-500/10 px-4 py-3 text-sm text-rose-200">
                  {error}
                </p>
              ) : null}
              <button
                className="inline-flex h-12 items-center justify-center rounded-full bg-emerald-400 px-6 text-sm font-semibold text-emerald-950 transition hover:bg-emerald-300 disabled:cursor-not-allowed disabled:bg-emerald-300/60"
                disabled={isLoading}
                type="submit"
              >
                {isLoading
                  ? 'Searching…'
                  : primaryMode
                    ? 'Search leads'
                    : mode === 'scout'
                      ? 'Run Scout search'
                      : 'Run Full search'}
              </button>
            </form>
          </section>

          <aside className="rounded-3xl border border-emerald-400/20 bg-emerald-400/10 p-6">
            <p className="text-sm font-medium uppercase tracking-[0.18em] text-emerald-200">Search usage</p>
            <div className="mt-4 space-y-4 text-sm text-zinc-200">
              {sandboxUsage ? (
                <>
                  <div className="grid gap-3 sm:grid-cols-2">
                    <div className="rounded-2xl border border-white/10 bg-zinc-950/70 px-4 py-3">
                      <p className="text-xs uppercase tracking-[0.16em] text-zinc-500">Queries</p>
                      <p className="mt-1 font-semibold text-zinc-50">
                        {sandboxUsage.total_queries}/{sandboxUsage.max_queries} used
                      </p>
                      <p className="text-xs text-zinc-400">{sandboxUsage.remaining_queries} remaining</p>
                    </div>
                    <div className="rounded-2xl border border-white/10 bg-zinc-950/70 px-4 py-3">
                      <p className="text-xs uppercase tracking-[0.16em] text-zinc-500">Rows</p>
                      <p className="mt-1 font-semibold text-zinc-50">
                        {sandboxUsage.total_rows}/{sandboxUsage.max_rows} used
                      </p>
                      <p className="text-xs text-zinc-400">{sandboxUsage.remaining_rows} remaining</p>
                    </div>
                  </div>
                  <p className="text-xs uppercase tracking-[0.18em] text-zinc-400">
                    Renews {new Date(sandboxUsage.reset_at).toLocaleString()}
                  </p>
                </>
              ) : (
                <p className="text-zinc-300">Loading search usage…</p>
              )}
            </div>
          </aside>
        </div>

        {queryGuardrail && queryGuardrail.status !== 'clear' ? (
          <div
            className={`rounded-2xl border px-4 py-3 text-sm ${
              queryGuardrail.status === 'blocked'
                ? 'border-rose-500/30 bg-rose-500/10 text-rose-100'
                : 'border-amber-500/30 bg-amber-500/10 text-amber-100'
            }`}
          >
            <p className="font-semibold">
              {queryGuardrail.status === 'blocked' ? 'Lead-list guardrail' : 'Query could be tighter'}
            </p>
            <p className="mt-1 leading-6">{queryGuardrail.message}</p>
            {queryGuardrail.missing_criteria.length > 0 ? (
              <p className="mt-2 text-xs uppercase tracking-[0.18em] text-current/80">
                Missing: {queryGuardrail.missing_criteria.join(', ')}
              </p>
            ) : null}
            {queryGuardrail.suggestions.length > 0 ? (
              <ul className="mt-2 list-disc space-y-1 pl-5 text-sm leading-6">
                {queryGuardrail.suggestions.map((suggestion) => (
                  <li key={suggestion}>{suggestion}</li>
                ))}
              </ul>
            ) : null}
          </div>
        ) : null}

        {!primaryMode && fullResult && (
          <div className="space-y-3 rounded-2xl border border-emerald-400/30 bg-emerald-400/10 px-4 py-3 text-sm text-emerald-200">
            <p>
              Full run saved for internal review.
            </p>
            <div className="flex flex-wrap items-end gap-3">
              <label className="flex flex-col gap-1 text-xs uppercase tracking-[0.18em] text-emerald-100" htmlFor="operatorMinutes">
                Operator minutes
                <input
                  className="w-40 rounded-2xl border border-white/10 bg-zinc-950/70 px-3 py-2 text-sm text-zinc-50 outline-none placeholder:text-zinc-500"
                  id="operatorMinutes"
                  inputMode="decimal"
                  onChange={(event) => setOperatorMinutes(event.target.value)}
                  placeholder="18.5"
                  value={operatorMinutes}
                />
              </label>
              <button
                className="rounded-full bg-emerald-300 px-4 py-2 text-sm font-semibold text-emerald-950 transition hover:bg-emerald-200 disabled:cursor-not-allowed disabled:bg-emerald-200/60"
                disabled={isClosing}
                onClick={handleCloseRun}
                type="button"
              >
                {isClosing ? 'Closing…' : 'Close run'}
              </button>
              <button
                className="rounded-full border border-emerald-300/30 bg-white/5 px-4 py-2 text-sm font-semibold text-emerald-100 transition hover:bg-emerald-400/10"
                onClick={handleBuildLeadExport}
                type="button"
              >
                {leadExport ? 'Rebuild validation export' : 'Build validation export'}
              </button>
            </div>
            {closeMessage ? <p className="text-xs text-emerald-100">{closeMessage}</p> : null}
            {leadExport ? (
              <div className="rounded-2xl border border-white/10 bg-zinc-950/70 px-4 py-3 text-sm text-zinc-200">
                <p className="font-semibold text-zinc-50">Validation export ready</p>
                <p className="mt-1 text-zinc-300">
                  {leadExport.rowCount} row{leadExport.rowCount === 1 ? '' : 's'} · generated {leadExport.generatedAtLabel}
                </p>
                <a
                  className="mt-3 inline-flex rounded-full border border-white/10 px-4 py-2 text-xs font-semibold uppercase tracking-[0.18em] text-zinc-50 transition hover:bg-white/10"
                  download={leadExport.filename}
                  href={leadExport.csvDataUrl}
                >
                  Download CSV
                </a>
                <p className="mt-2 text-xs leading-6 text-zinc-400">
                  Includes candidate category, readiness tier, field and contact statuses, source support, validation signals, gate status, and validation notes.
                </p>
              </div>
            ) : null}
          </div>
        )}

        <section className="rounded-3xl border border-white/10 bg-zinc-950/70 p-6">
          <div className="flex flex-col gap-4 sm:flex-row sm:items-end sm:justify-between">
            <div>
              <p className="text-sm font-medium uppercase tracking-[0.18em] text-zinc-400">Results</p>
              <h2 className="mt-1 text-2xl font-semibold tracking-tight">Tier summary</h2>
            </div>
            {displayedResults ? (
              <div className="flex flex-col gap-2 sm:items-end">
                <label className="text-xs font-medium uppercase tracking-[0.18em] text-zinc-400" htmlFor="leadSortMode">
                  Sort results
                </label>
                <select
                  className="rounded-2xl border border-white/10 bg-white/5 px-3 py-2 text-sm text-zinc-50 outline-none focus:border-emerald-400"
                  id="leadSortMode"
                  name="leadSortMode"
                  onChange={(event) => setSortMode(event.target.value as LeadSortMode)}
                  value={sortMode}
                >
                  {LEAD_SORT_OPTIONS.map((option) => (
                    <option key={option.value} value={option.value}>
                      {option.label}
                    </option>
                  ))}
                </select>
                <p className="text-sm text-zinc-400">
                  {displayedResults.leads.length} rows · {formatElapsedSeconds(displayedResults.metrics.elapsed_seconds)} · $
                  {displayedResults.metrics.estimated_cost_usd.toFixed(4)}
                </p>
              </div>
            ) : null}
          </div>

          {tierDistribution ? (
            <div className="mt-5 grid gap-3 sm:grid-cols-5">
              {OUTPUT_TIERS.map((tier) => (
                <div key={tier} className="rounded-2xl border border-white/10 bg-white/[0.03] px-4 py-3">
                  <p className="text-xs font-semibold uppercase tracking-[0.18em] text-zinc-500">{TIER_LABELS[tier]}</p>
                  <p className="mt-2 text-2xl font-semibold text-zinc-50">{tierDistribution[tier]}</p>
                </div>
              ))}
            </div>
          ) : null}

          {displayedResults ? (
            <ScoutResultsTable
              feedbackState={feedbackState}
              onOpenEvidence={handleOpenEvidence}
              onSubmitFeedback={handleLeadFeedback}
              rows={displayedRows}
            />
          ) : (
            <p className="mt-6 text-sm leading-6 text-zinc-400">
              Run a query to see readiness tiers, validation signals, and source checks here.
            </p>
          )}
        </section>
      </section>
      <ScoutEvidenceDrawer
        onClose={() => setSelectedEvidenceRow(null)}
        query={submittedQuery ?? query}
        runId={fullResult?.run_id ?? null}
        row={selectedEvidenceRow}
      />
    </main>
  );
}
