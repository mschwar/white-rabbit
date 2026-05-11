'use client';

import {
  type FeedbackLabel,
  type ScoutResultRow,
  type ValidationBucket,
  TIER_LABELS,
  VALIDATION_BUCKETS,
  formatScore,
  getOutputTier,
  getValidationBucket,
  isPersonLead,
} from '@/lib/scout';

const BUCKET_TONES: Record<ValidationBucket, string> = {
  usable: 'border-emerald-400/20 bg-emerald-400/10 text-emerald-100',
  noisy_failed: 'border-amber-400/20 bg-amber-400/10 text-amber-100',
  organization_only: 'border-sky-400/20 bg-sky-400/10 text-sky-100',
  not_found: 'border-white/10 bg-white/5 text-zinc-200',
};

const ROW_TONES: Record<ValidationBucket, string> = {
  usable: 'border-emerald-400/15 bg-emerald-400/[0.06]',
  noisy_failed: 'border-amber-400/15 bg-amber-400/[0.06]',
  organization_only: 'border-sky-400/15 bg-sky-400/[0.06]',
  not_found: 'border-white/10 bg-white/[0.03]',
};

const STATUS_TONES: Record<string, string> = {
  supported: 'border-emerald-400/20 bg-emerald-400/10 text-emerald-100',
  verified_found: 'border-emerald-400/20 bg-emerald-400/10 text-emerald-100',
  deduced_with_pattern_evidence: 'border-cyan-400/20 bg-cyan-400/10 text-cyan-100',
  missing: 'border-amber-400/20 bg-amber-400/10 text-amber-100',
  unsupported: 'border-zinc-400/20 bg-zinc-400/10 text-zinc-100',
  failed: 'border-rose-400/20 bg-rose-400/10 text-rose-100',
};

const FEEDBACK_LABELS: FeedbackLabel[] = ['usable', 'wrong_persona', 'bad_source', 'bad_contact', 'duplicate'];

type ScoutResultsTableProps = {
  rows: ScoutResultRow[];
  feedbackState: Record<string, string | null>;
  onOpenEvidence: (row: ScoutResultRow) => void;
  onSubmitFeedback: (leadId: string, label: FeedbackLabel) => Promise<void>;
};

function toStatusLabel(status: string): string {
  switch (status) {
    case 'verified_found':
      return 'verified';
    case 'deduced_with_pattern_evidence':
      return 'deduced';
    default:
      return status.replaceAll('_', ' ');
  }
}

function bucketLabel(bucket: ValidationBucket): string {
  return VALIDATION_BUCKETS.find((item) => item.key === bucket)?.label ?? bucket;
}

function statusTone(status: string): string {
  return STATUS_TONES[status] ?? STATUS_TONES.unsupported;
}

function validationBadge(label: string, status: string) {
  return (
    <span
      className={`inline-flex items-center gap-1 rounded-full border px-2 py-1 text-[11px] font-semibold uppercase tracking-[0.16em] ${statusTone(
        status,
      )}`}
      key={label}
    >
      {label}
      <span className="normal-case tracking-normal">{toStatusLabel(status)}</span>
    </span>
  );
}

function bucketTone(bucket: ValidationBucket): string {
  return BUCKET_TONES[bucket];
}

function rowTone(bucket: ValidationBucket): string {
  return ROW_TONES[bucket];
}

function getIdentity(row: ScoutResultRow): string {
  switch (row.candidate_category ?? 'person_lead') {
    case 'organization_only':
      return row.organization ?? '—';
    case 'not_found':
    case 'failed':
      return 'searched_target' in row ? row.searched_target : '—';
    default:
      return isPersonLead(row) ? row.name : '—';
  }
}

function getContextLines(row: ScoutResultRow): Array<{ label: string; value: string }> {
  if (isPersonLead(row)) {
    return [
      { label: 'Title', value: row.title },
      { label: 'Organization', value: row.organization },
    ];
  }

  if (row.candidate_category === 'organization_only') {
    return [
      { label: 'Organization', value: row.organization },
      { label: 'Reason', value: row.explanation },
    ];
  }

  if (row.candidate_category === 'not_found') {
    return [
      { label: 'Search target', value: row.searched_target },
      { label: 'Organization', value: row.organization ?? '—' },
    ];
  }

  return [
    { label: 'Search target', value: row.searched_target },
    { label: 'Failure reason', value: row.failure_reason },
    { label: 'Organization', value: row.organization ?? '—' },
  ];
}

function getValidationSourceUrl(row: ScoutResultRow): string | null {
  return row.validation?.source.source_url ?? row.source_url ?? null;
}

function getNotes(row: ScoutResultRow): string[] {
  const reason = row.primary_filter_reason;
  if (isPersonLead(row)) {
    return [reason, row.why_target, row.explanation, row.icebreaker].filter(Boolean) as string[];
  }

  if (row.candidate_category === 'failed') {
    return [reason, row.failure_reason, row.explanation].filter(Boolean) as string[];
  }

  return [reason, row.explanation].filter(Boolean) as string[];
}

function renderFeedbackButtons(
  row: ScoutResultRow,
  feedbackState: Record<string, string | null>,
  onSubmitFeedback: (leadId: string, label: FeedbackLabel) => Promise<void>,
) {
  if (!isPersonLead(row) || !row.id) {
    return <span className="text-zinc-500">—</span>;
  }

  return (
    <div className="flex flex-wrap gap-2">
      {FEEDBACK_LABELS.map((label) => {
        const isSubmitted = feedbackState[row.id ?? ''] === label;
        return (
          <button
            key={label}
            disabled={!!feedbackState[row.id ?? '']}
            onClick={async () => {
              try {
                await onSubmitFeedback(row.id ?? '', label);
              } catch {
                alert('Failed to submit feedback.');
              }
            }}
            className={`rounded-full border px-3 py-1 text-xs font-medium transition ${
              isSubmitted
                ? 'border-emerald-400/50 bg-emerald-400/20 text-emerald-300'
                : 'border-white/10 bg-white/5 text-zinc-300 hover:bg-emerald-400/20 hover:text-emerald-300'
            } disabled:cursor-not-allowed disabled:opacity-50`}
            type="button"
          >
            {isSubmitted ? `✓ ${label.replace('_', ' ')}` : label.replace('_', ' ')}
          </button>
        );
      })}
    </div>
  );
}

export default function ScoutResultsTable({ rows, feedbackState, onOpenEvidence, onSubmitFeedback }: ScoutResultsTableProps) {
  const groupedRows = VALIDATION_BUCKETS.reduce(
    (acc, bucket) => {
      acc[bucket.key] = [];
      return acc;
    },
    {} as Record<ValidationBucket, Array<{ row: ScoutResultRow; rank: number }>>,
  );

  rows.forEach((row, index) => {
    groupedRows[getValidationBucket(row)].push({ row, rank: index + 1 });
  });

  return (
    <div className="mt-6 space-y-5">
      <div className="grid gap-3 lg:grid-cols-4">
        {VALIDATION_BUCKETS.map((bucket) => {
          const items = groupedRows[bucket.key];
          return (
            <div key={bucket.key} className={`rounded-2xl border p-4 ${bucketTone(bucket.key)}`}>
              <div className="flex items-center justify-between gap-3">
                <p className="text-xs font-semibold uppercase tracking-[0.18em]">{bucket.label}</p>
                <p className="text-sm font-semibold">{items.length}</p>
              </div>
              <p className="mt-2 text-sm leading-6 text-current/80">{bucket.description}</p>
            </div>
          );
        })}
      </div>

      {VALIDATION_BUCKETS.map((bucket) => {
        const items = groupedRows[bucket.key];
        const headingId = `validation-bucket-${bucket.key}`;

        return (
          <section key={bucket.key} className={`rounded-3xl border p-5 ${rowTone(bucket.key)}`}>
            <div className="flex flex-col gap-2 sm:flex-row sm:items-end sm:justify-between">
              <div>
                <div className="flex flex-wrap items-center gap-2">
                  <p id={headingId} className="text-sm font-semibold uppercase tracking-[0.18em] text-zinc-200">
                    {bucket.label}
                  </p>
                  <span className={`rounded-full border px-3 py-1 text-xs font-semibold uppercase tracking-[0.18em] ${bucketTone(bucket.key)}`}>
                    {items.length} row{items.length === 1 ? '' : 's'}
                  </span>
                </div>
                <p className="mt-1 text-sm leading-6 text-zinc-400">{bucket.description}</p>
              </div>
              <p className="text-xs uppercase tracking-[0.18em] text-zinc-500">
                Validation bucketed results
              </p>
            </div>

            {items.length > 0 ? (
              <div className="mt-4 overflow-x-auto">
                <table className="min-w-full border-separate border-spacing-y-3" aria-label={`${bucket.label} results`}>
                  <thead>
                    <tr className="text-left text-xs uppercase tracking-[0.18em] text-zinc-500">
                      <th className="px-3 py-2">Identity</th>
                      <th className="px-3 py-2">Context</th>
                      <th className="px-3 py-2">Validation</th>
                      <th className="px-3 py-2">Signals</th>
                      <th className="px-3 py-2">Source / notes</th>
                      <th className="px-3 py-2">Feedback</th>
                    </tr>
                  </thead>
                  <tbody>
                    {items.map(({ row, rank }) => {
                      const rowBucket = getValidationBucket(row);
                      const rowTier = getOutputTier(row);
                      const sourceUrl = getValidationSourceUrl(row);
                      const validation = row.validation;
                      return (
                        <tr
                          key={`${row.id ?? getIdentity(row)}-${rank}`}
                          className={`rounded-3xl border ${rowTone(rowBucket)}`}
                        >
                          <td className="align-top rounded-l-3xl px-3 py-4">
                            <div className="space-y-3">
                              <div className="flex flex-wrap items-center gap-2">
                                <span className={`rounded-full border px-2 py-1 text-[11px] font-semibold uppercase tracking-[0.16em] ${bucketTone(rowBucket)}`}>
                                  Rank {rank}
                                </span>
                                <span className="rounded-full border border-white/10 bg-white/5 px-2 py-1 text-[11px] font-semibold uppercase tracking-[0.16em] text-zinc-200">
                                  {TIER_LABELS[rowTier] ?? bucketLabel(rowBucket)}
                                </span>
                              </div>
                              <p className="text-lg font-semibold text-zinc-50">{getIdentity(row)}</p>
                              {isPersonLead(row) ? <p className="text-sm text-zinc-300">{row.title}</p> : null}
                            </div>
                          </td>
                          <td className="align-top px-3 py-4">
                            <div className="space-y-2 text-sm text-zinc-300">
                              {getContextLines(row).map((line) => (
                                <div key={`${line.label}-${line.value}`} className="space-y-1">
                                  <p className="text-[11px] font-semibold uppercase tracking-[0.18em] text-zinc-500">
                                    {line.label}
                                  </p>
                                  <p className="leading-6 text-zinc-100">{line.value}</p>
                                </div>
                              ))}
                            </div>
                          </td>
                          <td className="align-top px-3 py-4">
                            <div className="flex flex-wrap gap-2">
                              {validationBadge('Name', validation?.name.status ?? 'unsupported')}
                              {validationBadge('Title', validation?.title.status ?? 'unsupported')}
                              {validationBadge('Org', validation?.organization.status ?? 'unsupported')}
                              {validationBadge('Email', validation?.email.status ?? 'unsupported')}
                              {validationBadge('Phone', validation?.phone.status ?? 'unsupported')}
                              {validationBadge('Source', validation?.source.status ?? 'unsupported')}
                            </div>
                          </td>
                          <td className="align-top px-3 py-4">
                            {isPersonLead(row) ? (
                              <div className="flex flex-wrap gap-2 text-sm text-zinc-200">
                                <span className="rounded-full border border-white/10 bg-zinc-950/70 px-3 py-1">
                                  Fit signal {formatScore(row.fit_score)}
                                </span>
                                <span className="rounded-full border border-white/10 bg-zinc-950/70 px-3 py-1">
                                  Evidence support {formatScore(row.evidence_score)}
                                </span>
                                <span className="rounded-full border border-white/10 bg-zinc-950/70 px-3 py-1">
                                  Contact readiness {formatScore(row.contact_score)}
                                </span>
                                <span
                                  className={`rounded-full border px-3 py-1 ${
                                    rowTier === 'high_trust_usable'
                                      ? 'border-emerald-400/30 bg-emerald-400/10 text-emerald-100'
                                      : 'border-amber-400/30 bg-amber-400/10 text-amber-100'
                                  }`}
                                >
                                  {TIER_LABELS[rowTier] ?? 'REVIEW'}
                                </span>
                              </div>
                            ) : (
                              <p className="text-sm text-zinc-500">—</p>
                            )}
                          </td>
                          <td className="align-top px-3 py-4">
                            <div className="space-y-3 text-sm text-zinc-200">
                              {sourceUrl ? (
                                <a
                                  className="inline-flex text-sm font-medium text-emerald-300 underline decoration-emerald-300/30 underline-offset-4"
                                  href={sourceUrl}
                                  rel="noreferrer"
                                  target="_blank"
                                >
                                  View source
                                </a>
                              ) : (
                                <p className="text-zinc-500">No source URL</p>
                              )}
                              {getNotes(row).map((note, index) => (
                                <p key={`${index}-${note}`} className="text-sm leading-6 text-zinc-300">
                                  {note}
                                </p>
                              ))}
                              <button
                                aria-label={`View evidence for ${getIdentity(row)}`}
                                className="inline-flex rounded-full border border-emerald-400/20 bg-emerald-400/10 px-3 py-1 text-xs font-semibold uppercase tracking-[0.16em] text-emerald-100 transition hover:border-emerald-300/40 hover:bg-emerald-300/15 hover:text-emerald-50"
                                onClick={() => onOpenEvidence(row)}
                                type="button"
                              >
                                View evidence
                              </button>
                            </div>
                          </td>
                          <td className="align-top rounded-r-3xl px-3 py-4">
                            {renderFeedbackButtons(row, feedbackState, onSubmitFeedback)}
                          </td>
                        </tr>
                      );
                    })}
                  </tbody>
                </table>
              </div>
            ) : (
              <p className="mt-4 rounded-2xl border border-dashed border-white/10 bg-zinc-950/50 px-4 py-3 text-sm text-zinc-400">
                No rows in this bucket.
              </p>
            )}
          </section>
        );
      })}
    </div>
  );
}
