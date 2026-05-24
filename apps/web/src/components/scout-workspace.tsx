'use client';

import { FormEvent, useEffect, useState } from 'react';
import { BrandSignal, BrandWordmark } from '@/components/brand-identity';
import PrimaryResultsOverview from '@/components/primary-results-overview';
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
  getOutputTier,
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

function RailGlyph({ active = false, kind }: { active?: boolean; kind: 'target' | 'evidence' }) {
  return (
    <div
      aria-hidden="true"
      className={`grid h-9 w-9 place-items-center rounded-lg border ${
        active
          ? 'border-[#2d7bff]/70 bg-[#2d7bff]/15 text-white'
          : 'border-white/10 bg-white/[0.03] text-white/55'
      }`}
    >
      {kind === 'target' ? (
        <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24">
          <circle cx="12" cy="12" r="6.5" stroke="currentColor" strokeWidth="1.8" />
          <path d="M12 3v3M12 18v3M3 12h3M18 12h3" stroke="currentColor" strokeLinecap="round" strokeWidth="1.8" />
          <circle cx="12" cy="12" r="1.5" fill="currentColor" />
        </svg>
      ) : (
        <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24">
          <path d="M7 5h10M7 12h10M7 19h6" stroke="currentColor" strokeLinecap="round" strokeWidth="1.8" />
          <circle cx="4" cy="5" r="1" fill="currentColor" />
          <circle cx="4" cy="12" r="1" fill="currentColor" />
          <circle cx="4" cy="19" r="1" fill="currentColor" />
        </svg>
      )}
    </div>
  );
}

const PRIMARY_LOADING_STAGES = [
  { label: 'Reading sources', count: '18' },
  { label: 'Matching people', count: '17' },
  { label: 'Checking contact evidence', count: '10' },
  { label: 'Preparing review table', count: '--' },
] as const;

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
  supported: 'border-[#9fd5b5] bg-[#f3fbf6] text-[#1f7a45]',
  verified_found: 'border-[#9fd5b5] bg-[#f3fbf6] text-[#1f7a45]',
  deduced_with_pattern_evidence: 'border-[#b7cffd] bg-[#f5f9ff] text-[#0e3a8a]',
  missing: 'border-[#edc98f] bg-[#fff8ec] text-[#8a5707]',
  unsupported: 'border-[#cbd5e1] bg-[#f7f9fc] text-[#536175]',
  failed: 'border-[#e8a6a6] bg-[#fdf0f0] text-[#a13c3c]',
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

function getEvidenceDossierStatus(row: ScoutResultRow): string {
  return TIER_LABELS[getOutputTier(row)];
}

function getEvidencePrimaryBlocker(row: ScoutResultRow): string {
  if (row.candidate_category === 'failed') {
    return row.failure_reason || row.explanation || 'The row was blocked by inaccessible or contradictory evidence.';
  }

  if (row.candidate_category === 'organization_only') {
    return row.explanation || 'No validated person was found for this organization.';
  }

  if (row.candidate_category === 'not_found') {
    return row.explanation || 'The target was searched, but no acceptable contact was found.';
  }

  const validation = getEvidenceValidation(row);
  if (validation.email.status === 'verified_found') {
    return row.primary_filter_reason || 'No blocker. The row is supported well enough for CRM-ready review.';
  }

  if (validation.email.status === 'deduced_with_pattern_evidence') {
    return 'Contact proof is deduced from pattern evidence and still needs human review.';
  }

  if (validation.email.status === 'missing') {
    return 'Direct contact proof is missing.';
  }

  if (validation.email.status === 'failed') {
    return 'Contact evidence could not be verified.';
  }

  return row.primary_filter_reason || row.explanation || 'The row still needs evidence review.';
}

function getEvidenceTrailEntries(row: ScoutResultRow) {
  const validation = getEvidenceValidation(row);

  return [
    { label: 'Name', record: validation.name },
    { label: 'Role', record: validation.title },
    { label: 'Org', record: validation.organization },
    { label: 'Email', record: validation.email },
    { label: 'Phone', record: validation.phone },
    { label: 'Source', record: validation.source },
  ].map(({ label, record }) => ({
    label,
    status: formatEvidenceStatusLabel(record.status),
    detail: record.evidence_snippet || record.notes || 'No evidence snippet captured.',
    href: record.source_url,
    checkedAt: record.checked_at,
  }));
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
    <article key={label} className={`rounded-lg border p-4 ${evidenceTone(record.status)}`}>
      <div className="flex items-start justify-between gap-3">
        <div>
          <p className="text-sm font-semibold text-[#0a1226]">{label}</p>
          <p className="mt-1 text-xs uppercase tracking-[0.16em] text-current/80">Status</p>
        </div>
        <span className="rounded-full border border-current/20 bg-white/60 px-2 py-1 text-[11px] font-semibold uppercase tracking-[0.12em]">
          {formatEvidenceStatusLabel(record.status)}
        </span>
      </div>

      <dl className="mt-4 space-y-3 text-sm text-[#0a1226]">
        <div className="space-y-1">
          <dt className="text-[11px] font-semibold uppercase tracking-[0.16em] text-[#60708a]">Source URL</dt>
          <dd className="break-all leading-6 text-[#0a1226]">
            {record.source_url ? (
              <a className="text-[#0e3a8a] underline decoration-[#b7cffd] underline-offset-4" href={record.source_url} rel="noreferrer" target="_blank">
                {record.source_url}
              </a>
            ) : (
              <span className="text-[#60708a]">No source URL captured</span>
            )}
          </dd>
        </div>
        <div className="space-y-1">
          <dt className="text-[11px] font-semibold uppercase tracking-[0.16em] text-[#60708a]">Checked at</dt>
          <dd className="leading-6 text-[#0a1226]">{record.checked_at ?? '—'}</dd>
        </div>
        <div className="space-y-1">
          <dt className="text-[11px] font-semibold uppercase tracking-[0.16em] text-[#60708a]">Notes</dt>
          <dd className="leading-6 text-[#0a1226]">{record.notes || '—'}</dd>
        </div>
        <div className="space-y-1">
          <dt className="text-[11px] font-semibold uppercase tracking-[0.16em] text-[#60708a]">Evidence snippet</dt>
          <dd className="leading-6 text-[#0a1226]">{record.evidence_snippet || '—'}</dd>
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
  const trailEntries = getEvidenceTrailEntries(currentRow);
  const dossierStatus = getEvidenceDossierStatus(currentRow);
  const primaryBlocker = getEvidencePrimaryBlocker(currentRow);
  const dossierTitle = isPersonLead(currentRow)
    ? `${currentRow.name} @ ${currentRow.organization}`
    : getEvidenceRowIdentity(currentRow);
  const dossierSummary = getEvidenceRowSummary(currentRow);
  const dossierRationale = isPersonLead(currentRow)
    ? currentRow.why_target || currentRow.explanation || dossierSummary
    : currentRow.explanation || dossierSummary;

  async function refreshCorrectionQueueExport(prefixMessage?: string) {
    if (!runId) {
      setCorrectionMessage('Run a saved search to export the correction queue.');
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
      setCorrectionMessage('Run a saved search first so this correction is tied to a saved run.');
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
      className="fixed inset-0 z-50 flex items-stretch justify-end bg-[#050916]/35 p-0 backdrop-blur-sm sm:p-6"
      onClick={onClose}
    >
      <div
        aria-describedby="evidence-drawer-summary"
        aria-labelledby="evidence-drawer-title"
        aria-modal="true"
        className="flex h-full w-full max-w-2xl flex-col overflow-hidden border border-[#d7deea] bg-[#fbfcfd] shadow-2xl shadow-[#0a1226]/20 sm:rounded-lg"
        onClick={(event) => event.stopPropagation()}
        role="dialog"
      >
        <div className="flex items-start justify-between gap-4 border-b border-[#d7deea] bg-white p-5">
          <div>
            <p className="text-xs font-semibold uppercase tracking-[0.16em] text-[#60708a]">Evidence dossier</p>
            <h3 id="evidence-drawer-title" className="mt-2 text-2xl font-semibold tracking-normal text-[#0a1226]">
              {dossierTitle}
            </h3>
            <p id="evidence-drawer-summary" className="mt-2 text-sm leading-6 text-[#536175]">
              {dossierSummary}
            </p>
          </div>
          <button
            className="rounded-md border border-[#cbd5e1] bg-white px-4 py-2 text-sm font-semibold text-[#0a1226] transition hover:border-[#2d7bff] hover:bg-[#f5f9ff]"
            onClick={onClose}
            type="button"
          >
            Close
          </button>
        </div>

        <div className="flex-1 overflow-y-auto p-5">
          <div className="flex flex-wrap items-center gap-2">
            <span className="rounded-full border border-[#d7deea] bg-white px-3 py-1 text-xs font-semibold uppercase tracking-[0.12em] text-[#536175]">
              {currentRow.candidate_category ?? 'person_lead'}
            </span>
            <span className="rounded-full border border-[#d7deea] bg-white px-3 py-1 text-xs font-semibold uppercase tracking-[0.12em] text-[#536175]">
              {getValidationBucket(currentRow)}
            </span>
            <span className="rounded-full border border-[#b7cffd] bg-[#e8f1ff] px-3 py-1 text-xs font-semibold uppercase tracking-[0.12em] text-[#0e3a8a]">
              {dossierStatus}
            </span>
          </div>

          <div className="mt-5 grid gap-4 rounded-lg border border-[#d7deea] bg-white p-5">
            <div className="grid gap-4 sm:grid-cols-2">
              <div className="rounded-lg border border-[#d7deea] bg-[#fbfcfd] p-4">
                <p className="text-[11px] font-semibold uppercase tracking-[0.16em] text-[#60708a]">Status</p>
                <p className="mt-2 text-lg font-semibold text-[#0a1226]">{dossierStatus}</p>
                <p className="mt-1 text-sm leading-6 text-[#536175]">{dossierSummary}</p>
              </div>
              <div className="rounded-lg border border-[#edc98f] bg-[#fff8ec] p-4">
                <p className="text-[11px] font-semibold uppercase tracking-[0.16em] text-[#8a5707]">Primary blocker</p>
                <p className="mt-2 text-lg font-semibold text-[#0a1226]">{primaryBlocker}</p>
                <p className="mt-1 text-sm leading-6 text-[#7a5a1d]">Review this row before treating it as CRM-ready.</p>
              </div>
            </div>

            <div>
              <p className="text-[11px] font-semibold uppercase tracking-[0.16em] text-[#60708a]">Rationale</p>
              <p className="mt-2 text-sm leading-6 text-[#0a1226]">{dossierRationale}</p>
            </div>
          </div>

          <div className="mt-5 grid gap-4 md:grid-cols-2">
            {fields.map(({ label, record }) => renderEvidenceField(label, record))}
          </div>

          <div className="mt-5 rounded-lg border border-[#d7deea] bg-white p-5">
            <p className="text-xs font-semibold uppercase tracking-[0.16em] text-[#60708a]">Source trail</p>
            <ol className="mt-4 space-y-3">
              {trailEntries.map((entry, index) => (
                <li key={`${entry.label}-${index}`} className="flex items-start gap-3 rounded-lg border border-[#d7deea] bg-[#fbfcfd] p-4">
                  <span className="grid h-7 w-7 shrink-0 place-items-center rounded-full border border-[#b7cffd] bg-[#e8f1ff] text-xs font-semibold text-[#0e3a8a]">
                    {index + 1}
                  </span>
                  <div className="min-w-0 flex-1">
                    <div className="flex flex-wrap items-center gap-2">
                      <strong className="text-sm text-[#0a1226]">{entry.label}</strong>
                      <span className="rounded-full border border-[#d7deea] bg-white px-2 py-0.5 text-[10px] font-semibold uppercase tracking-[0.12em] text-[#536175]">
                        {entry.status}
                      </span>
                    </div>
                    <p className="mt-1 text-sm leading-6 text-[#536175]">{entry.detail}</p>
                    {entry.checkedAt ? <p className="mt-1 text-xs text-[#60708a]">{entry.checkedAt}</p> : null}
                  </div>
                  {entry.href ? (
                    <a
                      className="rounded-md border border-[#b7cffd] bg-white px-3 py-1.5 text-xs font-semibold uppercase tracking-[0.12em] text-[#0e3a8a] transition hover:border-[#2d7bff] hover:bg-[#f5f9ff]"
                      href={entry.href}
                      rel="noreferrer"
                      target="_blank"
                    >
                      Source
                    </a>
                  ) : null}
                </li>
              ))}
            </ol>
          </div>

          <div className="mt-6 rounded-lg border border-[#d7deea] bg-white p-5">
            <div className="flex flex-col gap-2 sm:flex-row sm:items-end sm:justify-between">
              <div>
                <p className="text-xs font-semibold uppercase tracking-[0.16em] text-[#60708a]">Review actions</p>
                <h4 className="mt-2 text-lg font-semibold text-[#0a1226]">Record a field-level correction</h4>
                <p className="mt-1 text-sm leading-6 text-[#536175]">
                  Save the operator correction against this saved run, then export the review queue as JSON.
                </p>
              </div>
              {runId ? (
                <button
                  className="rounded-md border border-[#cbd5e1] bg-white px-4 py-2 text-xs font-semibold uppercase tracking-[0.12em] text-[#0a1226] transition hover:border-[#2d7bff] hover:bg-[#f5f9ff] disabled:cursor-not-allowed disabled:opacity-60"
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
                  <label className="flex flex-col gap-2 text-sm text-[#0a1226]" htmlFor="correctionLabel">
                    Correction type
                    <select
                      className="rounded-lg border border-[#cbd5e1] bg-[#fbfcfd] px-4 py-3 text-[#0a1226] outline-none focus:border-[#2d7bff] focus:ring-2 focus:ring-[#2d7bff]/20"
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
                  <label className="flex flex-col gap-2 text-sm text-[#0a1226]" htmlFor="correctionField">
                    Corrected field
                    <select
                      className="rounded-lg border border-[#cbd5e1] bg-[#fbfcfd] px-4 py-3 text-[#0a1226] outline-none focus:border-[#2d7bff] focus:ring-2 focus:ring-[#2d7bff]/20"
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
                  <label className="flex flex-col gap-2 text-sm text-[#0a1226]" htmlFor="correctionPreviousValue">
                    Previous value
                    <input
                      className="rounded-lg border border-[#cbd5e1] bg-[#fbfcfd] px-4 py-3 text-[#0a1226] outline-none placeholder:text-[#60708a] focus:border-[#2d7bff] focus:ring-2 focus:ring-[#2d7bff]/20"
                      id="correctionPreviousValue"
                      onChange={(event) => setCorrectionPreviousValue(event.target.value)}
                      placeholder="Value before correction"
                      value={correctionPreviousValue}
                    />
                  </label>
                  <label className="flex flex-col gap-2 text-sm text-[#0a1226]" htmlFor="correctionCorrectedValue">
                    Corrected value
                    <input
                      className="rounded-lg border border-[#cbd5e1] bg-[#fbfcfd] px-4 py-3 text-[#0a1226] outline-none placeholder:text-[#60708a] focus:border-[#2d7bff] focus:ring-2 focus:ring-[#2d7bff]/20"
                      id="correctionCorrectedValue"
                      onChange={(event) => setCorrectionCorrectedValue(event.target.value)}
                      placeholder="Value after correction"
                      value={correctionCorrectedValue}
                    />
                  </label>
                </div>
                <label className="flex flex-col gap-2 text-sm text-[#0a1226]" htmlFor="correctionNotes">
                  Notes
                  <textarea
                    className="min-h-28 rounded-lg border border-[#cbd5e1] bg-[#fbfcfd] px-4 py-3 text-[#0a1226] outline-none placeholder:text-[#60708a] focus:border-[#2d7bff] focus:ring-2 focus:ring-[#2d7bff]/20"
                    id="correctionNotes"
                    onChange={(event) => setCorrectionNotes(event.target.value)}
                    placeholder="Why this row needs to be corrected"
                    value={correctionNotes}
                  />
                </label>

                <div className="flex flex-wrap items-center gap-3">
                  <button
                    className="rounded-md bg-[#2d7bff] px-4 py-2 text-sm font-semibold text-white transition hover:bg-[#1f65d8] disabled:cursor-not-allowed disabled:bg-[#2d7bff]/60"
                    disabled={isSubmittingCorrection}
                    type="submit"
                  >
                    {isSubmittingCorrection ? 'Saving…' : 'Save correction'}
                  </button>
                  {correctionExport ? (
                    <a
                      className="rounded-md border border-[#b7cffd] bg-white px-4 py-2 text-sm font-semibold text-[#0e3a8a] transition hover:border-[#2d7bff] hover:bg-[#f5f9ff]"
                      download={correctionExport.filename}
                      href={correctionExport.dataUrl}
                    >
                      Download review queue JSON
                    </a>
                  ) : null}
                </div>
              </form>
            ) : (
              <p className="mt-4 text-sm leading-6 text-[#536175]">
                Run a saved search first so corrections are stored against a saved run and query snapshot.
              </p>
            )}

            {correctionMessage ? <p className="mt-4 text-sm leading-6 text-[#0e3a8a]">{correctionMessage}</p> : null}
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
  const [query, setQuery] = useState(primaryMode ? '' : DEFAULT_SCOUT_QUERY);
  const [sourceContext, setSourceContext] = useState('');
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
  const [isQaLoading, setIsQaLoading] = useState(false);
  const [sortMode, setSortMode] = useState<LeadSortMode>('rank');
  const [isClosing, setIsClosing] = useState(false);
  const [leadExport, setLeadExport] = useState<{
    filename: string;
    csvDataUrl: string;
    generatedAtLabel: string;
    rowCount: number;
  } | null>(null);
  const [runStartedAtMs, setRunStartedAtMs] = useState<number | null>(null);
  const [closedExportRunIds, setClosedExportRunIds] = useState<Record<string, true>>({});
  const [selectedEvidenceRow, setSelectedEvidenceRow] = useState<ScoutResultRow | null>(null);
  const [submittedQuery, setSubmittedQuery] = useState<string | null>(null);
  const [submittedLocation, setSubmittedLocation] = useState<string | null>(null);
  const [submittedRecipeName, setSubmittedRecipeName] = useState<string | null>(null);
  const [feedbackState, setFeedbackState] = useState<Record<string, string | null>>({});
  const queryLabel = primaryMode ? 'Lead search' : 'Prospecting query';

  useEffect(() => {
    if (primaryMode) {
      return undefined;
    }

    fetchSandboxUsage()
      .then(setSandboxUsage)
      .catch(() => undefined);
    return undefined;
  }, [primaryMode]);

  useEffect(() => {
    if (process.env.NODE_ENV !== 'production' && window.location.search.includes('qa=validation-buckets')) {
      setMode('full');
    }
  }, []);

  useEffect(() => {
    if (process.env.NODE_ENV !== 'production' && window.location.search.includes('qa=loading')) {
      setIsQaLoading(true);
    }
  }, []);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();

    const effectiveQuery =
      primaryMode && sourceContext.trim()
        ? `${query.trim()}\n\nSource context:\n${sourceContext.trim()}`
        : query;
    const payload = primaryMode || mode === 'scout'
      ? buildScoutPayload(effectiveQuery, location)
      : buildFullPayload(effectiveQuery, location, recipeName);

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
    setRunStartedAtMs(Date.now());
    setClosedExportRunIds({});
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
        if (primaryMode || mode === 'scout') {
          setSubmittedQuery(submittedQuery);
          setSubmittedLocation(submittedLocation);
          setSubmittedRecipeName(submittedRecipeName);
        }
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

      const endpoint = primaryMode || mode === 'scout' ? '/api/scout' : '/api/full';
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

      if (primaryMode || mode === 'scout') {
        const data = (await response.json()) as ScoutResponse;
        setResults(data);
        setQueryGuardrail(data.query_guardrail ?? null);
        setSandboxUsage(data.sandbox_usage ?? null);
        setSubmittedQuery(submittedQuery);
        setSubmittedLocation(submittedLocation);
        setSubmittedRecipeName(submittedRecipeName);
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
    if (!displayedResults || displayedRows.length === 0) {
      return;
    }

    const generatedAt = new Date();
    const persistedRunId = fullResult?.run_id ?? displayedResults.run_id ?? null;
    const exportRunId = persistedRunId ?? `scout-${generatedAt.toISOString()}`;
    const exportRows = buildFullLeadExportRows({
      query: submittedQuery ?? query,
      location: submittedLocation ?? location,
      recipeName: submittedRecipeName ?? (recipeName || query),
      runId: exportRunId,
      sortMode,
      rows: displayedRows,
      guardrail: fullResult?.query_guardrail ?? displayedResults.query_guardrail ?? null,
      generatedAt,
    });

    const csv = buildFullLeadExportCsv(exportRows);
    setLeadExport({
      filename: buildFullLeadExportFilename(generatedAt),
      csvDataUrl: `data:text/csv;charset=utf-8,${encodeURIComponent(csv)}`,
      generatedAtLabel: generatedAt.toLocaleString(),
      rowCount: exportRows.length,
    });

    if (primaryMode && persistedRunId && !closedExportRunIds[persistedRunId]) {
      const elapsedMinutes = Math.max((Date.now() - (runStartedAtMs ?? Date.now())) / 60000, 0.01);
      setIsClosing(true);
      try {
        await closeRecipeRun(persistedRunId, Number(elapsedMinutes.toFixed(2)));
        setClosedExportRunIds((prev) => ({ ...prev, [persistedRunId]: true }));
        setCloseMessage(`Run closed with ${elapsedMinutes.toFixed(2)} operator minutes.`);
      } catch (err) {
        setCloseMessage(err instanceof Error ? err.message : 'Failed to close run.');
      } finally {
        setIsClosing(false);
      }
    }
  }

  const displayedResults = results;
  const displayedRows = displayedResults ? sortScoutResultRows(displayedResults.leads, sortMode) : [];
  const tierDistribution = displayedResults
    ? buildTierDistribution(displayedResults.leads, displayedResults.metrics.tier_distribution)
    : null;
  const showPrimaryLoading = primaryMode && (isLoading || isQaLoading);
  const showPrimaryResultsOverview = primaryMode && !!displayedResults && !showPrimaryLoading;
  const readyCount = tierDistribution?.high_trust_usable ?? 0;

  if (primaryMode) {
    return (
      <main className="min-h-screen bg-[#050916] text-[#0a1226]">
        <div className="min-h-screen lg:grid lg:grid-cols-[76px_minmax(0,1fr)] lg:grid-rows-[64px_minmax(0,1fr)]">
          <header className="flex min-h-16 items-center border-b border-white/10 bg-[#050916] text-white lg:col-span-2">
            <div className="grid h-16 w-16 place-items-center border-r border-white/10 lg:w-[76px]">
              <BrandSignal className="h-9 w-9" />
            </div>
            <div className="min-w-0 px-4">
              <BrandWordmark caption="Evidence categorization" inverted />
            </div>
            <div className="ml-auto hidden items-center gap-2 px-4 sm:flex">
              {showPrimaryResultsOverview ? (
                <>
                  <span className="rounded-full border border-[#2d7bff]/50 bg-[#0d1938] px-3 py-1 text-xs font-semibold text-white">
                    {displayedResults.leads.length} categorized
                  </span>
                  <span className="rounded-full border border-[#9fd5b5]/50 bg-[#123224] px-3 py-1 text-xs font-semibold text-[#d9f3e4]">
                    {readyCount} READY
                  </span>
                </>
              ) : (
                <>
                  <span className="rounded-full border border-white/10 px-3 py-1 text-xs text-white/70">READY / REVIEW</span>
                  <span className="rounded-full border border-[#2d7bff]/50 bg-[#2d7bff]/15 px-3 py-1 text-xs text-white">Evidence first</span>
                </>
              )}
            </div>
          </header>

          <aside className="hidden border-r border-white/10 bg-[#0a1226] px-5 py-5 lg:flex lg:flex-col lg:items-center lg:justify-between">
            <div className="grid gap-3">
              <RailGlyph active kind="target" />
              <RailGlyph kind="evidence" />
            </div>
            <p className="[writing-mode:vertical-rl] rotate-180 text-[10px] font-semibold uppercase tracking-[0.16em] text-white/35">
              Review
            </p>
          </aside>

          <section className="min-h-[calc(100vh-64px)] bg-[#fbfcfd]">
            {!showPrimaryResultsOverview ? (
              <div className="grid min-h-[52vh] gap-10 bg-[#050916] px-5 py-12 text-white sm:px-8 lg:px-14">
                <div>
                  <BrandWordmark
                    caption="Prospects sorted by readiness, blockers, and source proof."
                    className="mb-8"
                    inverted
                    size="hero"
                  />
                  <h1 className="max-w-4xl text-5xl font-semibold leading-[0.98] tracking-normal sm:text-6xl lg:text-7xl">
                    Start with the target. Keep the proof beside it.
                  </h1>
                  <p className="mt-6 max-w-2xl text-lg leading-8 text-white/70">
                    Review the market clearly, keep blockers visible, and open evidence when a row needs proof.
                  </p>
                </div>
              </div>
            ) : null}

            <div className={`px-5 ${showPrimaryResultsOverview ? 'py-6' : 'py-8'} sm:px-8 lg:px-14`}>
              {showPrimaryResultsOverview ? (
                <div className="mb-6 flex flex-col gap-4 lg:flex-row lg:items-end lg:justify-between">
                  <div>
                    <p className="text-[11px] font-black uppercase tracking-[0.1em] text-[#60708a]">Candidate review</p>
                    <h1 className="mt-1 text-3xl font-semibold tracking-normal text-[#0a1226] sm:text-4xl">
                      {query.trim() || 'Candidate review'}
                    </h1>
                    <p className="mt-2 max-w-3xl text-sm leading-6 text-[#536175]">
                      Review CRM-first fields, keep uncertain rows visible, and open evidence only when a row needs proof.
                    </p>
                  </div>
                  <div className="rounded-lg border border-[#d7deea] bg-white px-4 py-3 text-sm leading-6 text-[#536175] shadow-[0_14px_30px_rgba(10,18,38,0.05)]">
                    Refine the target here to rerun without leaving the review surface.
                  </div>
                </div>
              ) : null}

              <form
                className={`grid gap-4 rounded-lg border border-[#cbd5e1] bg-white p-4 shadow-[0_18px_42px_rgba(10,18,38,0.08)] ${
                  primaryMode ? 'lg:grid-cols-[minmax(0,1fr)_auto]' : 'lg:grid-cols-[minmax(0,1fr)_minmax(300px,0.7fr)_auto]'
                } lg:items-end`}
                onSubmit={handleSubmit}
              >
                <label className="grid gap-2" htmlFor="query">
                  <span className="text-[11px] font-black uppercase tracking-[0.1em] text-[#60708a]">Target</span>
                  <textarea
                    className="min-h-12 w-full resize-none rounded-md border border-[#cbd5e1] bg-[#fbfcfd] px-3 py-3 text-base font-semibold leading-6 text-[#0a1226] outline-none placeholder:text-[#60708a] focus:border-[#2d7bff] focus:ring-2 focus:ring-[#2d7bff]/25"
                    id="query"
                    name="query"
                    onChange={(event) => setQuery(event.target.value)}
                    placeholder="VP Sales at Series B SaaS companies in NY"
                    value={query}
                  />
                </label>
                {primaryMode ? null : (
                  <label className="grid gap-2" htmlFor="sourceContext">
                    <span className="text-[11px] font-black uppercase tracking-[0.1em] text-[#60708a]">Source context</span>
                    <textarea
                      className="min-h-12 w-full resize-none rounded-md border border-[#cbd5e1] bg-[#fbfcfd] px-3 py-3 text-sm font-medium text-[#0a1226] outline-none placeholder:text-[#60708a] focus:border-[#2d7bff] focus:ring-2 focus:ring-[#2d7bff]/25"
                      id="sourceContext"
                      name="sourceContext"
                      onChange={(event) => setSourceContext(event.target.value)}
                      placeholder="Staff pages, rosters, trusted URLs, seed notes"
                      value={sourceContext}
                    />
                  </label>
                )}
                <button
                  className="inline-flex h-12 items-center justify-center rounded-md bg-[#2d7bff] px-5 text-sm font-black text-white transition hover:bg-[#1f65d8] disabled:cursor-not-allowed disabled:bg-[#2d7bff]/60"
                  disabled={isLoading}
                  type="submit"
                >
                  {isLoading ? 'Finding Candidates...' : 'Find Candidates'}
                </button>
              </form>
              <p className="mt-4 max-w-3xl text-sm leading-6 text-[#60708a]">
                {showPrimaryResultsOverview
                  ? 'Broad targets should surface the market clearly. Tight targets should make blockers and missing contacts obvious.'
                  : 'Broad targets return a categorized market view. Narrow targets return a tighter review set.'}
              </p>

              {error ? (
                <p className="mt-5 rounded-lg border border-[#a13c3c]/30 bg-[#fcebeb] px-4 py-3 text-sm text-[#8f3434]">
                  {error}
                </p>
              ) : null}

              {queryGuardrail && queryGuardrail.status !== 'clear' ? (
                <div
                  className={`mt-5 rounded-lg border px-4 py-3 text-sm ${
                    queryGuardrail.status === 'blocked'
                      ? 'border-[#a13c3c]/30 bg-[#fcebeb] text-[#8f3434]'
                      : 'border-[#a16207]/30 bg-[#fff4e1] text-[#8a5707]'
                  }`}
                >
                  <p className="font-semibold">
                    {queryGuardrail.status === 'blocked' ? 'Target blocked' : 'Target could be tighter'}
                  </p>
                  <p className="mt-1 leading-6">{queryGuardrail.message}</p>
                  {queryGuardrail.suggestions.length > 0 ? (
                    <ul className="mt-2 list-disc space-y-1 pl-5 leading-6">
                      {queryGuardrail.suggestions.map((suggestion) => (
                        <li key={suggestion}>{suggestion}</li>
                      ))}
                    </ul>
                  ) : null}
                </div>
              ) : null}

              {showPrimaryLoading ? (
                <section aria-live="polite" className="mt-8 grid gap-5 rounded-lg border border-[#e2e7ef] bg-white p-5">
                  <div className="flex flex-col gap-2 sm:flex-row sm:items-end sm:justify-between">
                    <div>
                      <p className="text-[11px] font-black uppercase tracking-[0.1em] text-[#60708a]">Evidence forming</p>
                      <h2 className="mt-1 text-2xl font-semibold tracking-normal text-[#0a1226]">
                        {query.trim() || 'Candidate review'}
                      </h2>
                    </div>
                    <span className="w-fit rounded-full border border-[#2d7bff]/30 bg-[#e8f1ff] px-3 py-1 text-xs font-bold text-[#0e3a8a]">
                      Checking fields
                    </span>
                  </div>
                  <div className="grid gap-3 lg:grid-cols-4">
                    {PRIMARY_LOADING_STAGES.map((stage, index) => (
                      <div key={stage.label} className="rounded-lg border border-[#e2e7ef] bg-[#f6f7f9] px-4 py-3">
                        <div className="flex items-center justify-between gap-3">
                          <span className={`h-2.5 w-2.5 rounded-full ${index < 3 ? 'bg-[#2d7bff]' : 'bg-[#cbd5e1]'}`} />
                          <span className="text-xs font-semibold text-[#60708a]">{stage.count}</span>
                        </div>
                        <p className="mt-3 text-sm font-semibold text-[#0a1226]">{stage.label}</p>
                      </div>
                    ))}
                  </div>
                  <div className="overflow-hidden rounded-lg border border-[#e2e7ef]">
                    <div className="grid grid-cols-[1fr_0.8fr_0.8fr_0.7fr] bg-[#f1f4f8] px-4 py-3 text-[10px] font-black uppercase tracking-[0.08em] text-[#60708a]">
                      <span>Company</span>
                      <span>Person</span>
                      <span>Source</span>
                      <span>Status</span>
                    </div>
                    {[0, 1, 2, 3].map((item) => (
                      <div key={item} className="grid grid-cols-[1fr_0.8fr_0.8fr_0.7fr] gap-4 border-t border-[#e2e7ef] px-4 py-3">
                        <span className="h-3 rounded bg-[#e2e7ef]" />
                        <span className="h-3 rounded bg-[#e2e7ef]" />
                        <span className="h-3 rounded bg-[#e8f1ff]" />
                        <span className="h-3 rounded bg-[#fff4e1]" />
                      </div>
                    ))}
                  </div>
                </section>
              ) : null}

              {displayedResults && !showPrimaryLoading ? (
                showPrimaryResultsOverview ? (
                  <>
                    <PrimaryResultsOverview
                      leadExport={leadExport}
                      onBuildExport={handleBuildLeadExport}
                      onOpenEvidence={handleOpenEvidence}
                      onSortChange={setSortMode}
                      results={displayedResults}
                      rows={displayedRows}
                      sortMode={sortMode}
                    />
                  </>
                ) : (
                  <section className="mt-8 rounded-lg border border-[#e2e7ef] bg-white p-5">
                    <div className="flex flex-col gap-4 sm:flex-row sm:items-end sm:justify-between">
                      <div>
                        <p className="text-[11px] font-black uppercase tracking-[0.1em] text-[#60708a]">Candidate review</p>
                        <h2 className="mt-1 text-2xl font-semibold tracking-normal text-[#0a1226]">Tier summary</h2>
                      </div>
                      <div className="flex flex-col gap-2 sm:items-end">
                        <label className="text-[11px] font-black uppercase tracking-[0.1em] text-[#60708a]" htmlFor="leadSortMode">
                          Sort results
                        </label>
                        <select
                          className="rounded-md border border-[#cbd5e1] bg-[#fbfcfd] px-3 py-2 text-sm text-[#0a1226] outline-none focus:border-[#2d7bff]"
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
                        <p className="text-sm text-[#60708a]">
                          {displayedResults.leads.length} rows · {formatElapsedSeconds(displayedResults.metrics.elapsed_seconds)} · $
                          {displayedResults.metrics.estimated_cost_usd.toFixed(4)}
                        </p>
                      </div>
                    </div>

                    {tierDistribution ? (
                      <div className="mt-5 grid gap-px overflow-hidden rounded-lg border border-[#e2e7ef] bg-[#e2e7ef] sm:grid-cols-5">
                        {OUTPUT_TIERS.map((tier) => (
                          <div key={tier} className="bg-white px-4 py-3">
                            <p className="text-[11px] font-black uppercase tracking-[0.1em] text-[#60708a]">{TIER_LABELS[tier]}</p>
                            <p className="mt-2 text-2xl font-semibold text-[#0a1226]">{tierDistribution[tier]}</p>
                          </div>
                        ))}
                      </div>
                    ) : null}

                    <div className="mt-2 rounded-lg bg-[#0a1226] p-1">
                      <ScoutResultsTable
                        feedbackState={feedbackState}
                        onOpenEvidence={handleOpenEvidence}
                        onSubmitFeedback={handleLeadFeedback}
                        rows={displayedRows}
                      />
                    </div>
                  </section>
                )
              ) : null}

              {!displayedResults && !showPrimaryLoading ? (
                <section className="mt-8 rounded-lg border border-dashed border-[#cbd5e1] bg-white px-5 py-8 text-sm leading-6 text-[#60708a]">
                  The review table forms here after candidates are checked.
                </section>
              ) : null}
            </div>
          </section>
        </div>
        <ScoutEvidenceDrawer
          onClose={() => setSelectedEvidenceRow(null)}
          query={submittedQuery ?? query}
          runId={fullResult?.run_id ?? null}
          row={selectedEvidenceRow}
        />
      </main>
    );
  }

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
                    ? 'Find candidates'
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
