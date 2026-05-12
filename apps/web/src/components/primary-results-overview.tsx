'use client';

import { useEffect, useState } from 'react';
import {
  buildTierDistribution,
  type LeadSortMode,
  LEAD_SORT_OPTIONS,
  type OutputTier,
  type ScoutResponse,
  type ScoutResultRow,
  TIER_LABELS,
  getOutputTier,
  isPersonLead,
} from '@/lib/scout';

type PrimaryResultFilter = 'all' | 'high_trust_usable' | 'review' | 'organization_only' | 'not_found';

type PrimaryResultsOverviewProps = {
  leadExport: {
    filename: string;
    csvDataUrl: string;
    generatedAtLabel: string;
    rowCount: number;
  } | null;
  results: ScoutResponse;
  rows: ScoutResultRow[];
  sortMode: LeadSortMode;
  onBuildExport: () => void;
  onOpenEvidence: (row: ScoutResultRow) => void;
  onSortChange: (mode: LeadSortMode) => void;
};

const FILTER_OPTIONS: Array<{ key: PrimaryResultFilter; label: string }> = [
  { key: 'all', label: 'ALL' },
  { key: 'high_trust_usable', label: 'READY' },
  { key: 'review', label: 'REVIEW' },
  { key: 'organization_only', label: 'ORG-ONLY' },
  { key: 'not_found', label: 'NOT FOUND' },
];

const COUNT_TILE_TONE: Record<PrimaryResultFilter, string> = {
  all: 'text-[#0a1226]',
  high_trust_usable: 'text-[#1f7a45]',
  review: 'text-[#a16207]',
  organization_only: 'text-[#536175]',
  not_found: 'text-[#60708a]',
};

const SECTION_ORDER: OutputTier[] = ['high_trust_usable', 'review', 'organization_only', 'not_found', 'failed'];

const SECTION_COPY: Record<OutputTier, { title: string; description: string }> = {
  high_trust_usable: {
    title: 'READY - contact proof present',
    description: 'These rows have source-backed person, company, and usable contact support.',
  },
  review: {
    title: 'REVIEW - source-supported, but not CRM-ready',
    description: 'These rows need a human check because contact proof, fit, or evidence is still incomplete.',
  },
  organization_only: {
    title: 'ORG-ONLY - account found, person missing',
    description: 'The account was found, but no validated person is safe to treat as ready.',
  },
  not_found: {
    title: 'NOT FOUND - target searched, no acceptable contact',
    description: 'The requested target was checked, but no acceptable person or contact could be supported.',
  },
  failed: {
    title: 'REVIEW - blocked or contradicted rows',
    description: 'These rows need review because the public evidence contradicted the claim or stayed unsupported.',
  },
};

const STATUS_TONE: Record<OutputTier, string> = {
  high_trust_usable: 'border-[#9fd5b5] bg-[#e8f5ec] text-[#1f7a45]',
  review: 'border-[#edc98f] bg-[#fff4e1] text-[#a16207]',
  organization_only: 'border-[#cbd5e1] bg-[#eef2f7] text-[#536175]',
  not_found: 'border-[#d7deea] bg-[#f5f7fb] text-[#60708a]',
  failed: 'border-[#edc98f] bg-[#fff4e1] text-[#a16207]',
};

const ROW_TONE: Record<OutputTier, string> = {
  high_trust_usable: 'bg-white',
  review: 'bg-[#fffaf4]',
  organization_only: 'bg-[#f7f9fc]',
  not_found: 'bg-[#f8fafc]',
  failed: 'bg-[#fffaf4]',
};

function formatContactStatus(status: string | undefined): string {
  switch (status) {
    case 'Found':
    case 'verified_found':
      return 'verified';
    case 'Deduced':
    case 'deduced_with_pattern_evidence':
      return 'deduced';
    case 'Missing':
    case 'missing':
      return 'missing';
    case 'failed':
      return 'failed';
    case 'unsupported':
      return 'unsupported';
    default:
      return 'not captured';
  }
}

function getFilterCount(
  filter: PrimaryResultFilter,
  distribution: Record<OutputTier, number>,
  totalRows: number,
): number {
  if (filter === 'all') {
    return totalRows;
  }

  if (filter === 'review') {
    return distribution.review + distribution.failed;
  }

  return distribution[filter];
}

function rowMatchesFilter(row: ScoutResultRow, filter: PrimaryResultFilter): boolean {
  if (filter === 'all') {
    return true;
  }

  const tier = getOutputTier(row);
  if (filter === 'review') {
    return tier === 'review' || tier === 'failed';
  }

  return tier === filter;
}

function getOrganization(row: ScoutResultRow): string {
  if (isPersonLead(row)) {
    return row.organization;
  }

  if (row.candidate_category === 'organization_only') {
    return row.organization;
  }

  return row.organization ?? row.searched_target;
}

function getPerson(row: ScoutResultRow): { primary: string; secondary: string } {
  if (isPersonLead(row)) {
    return {
      primary: row.name,
      secondary: row.validation?.name.status === 'supported' ? 'source-backed person' : 'person needs review',
    };
  }

  if (row.candidate_category === 'organization_only') {
    return { primary: 'No validated person', secondary: 'manual lookup required' };
  }

  if (row.candidate_category === 'not_found') {
    return { primary: row.searched_target, secondary: 'target searched' };
  }

  return { primary: row.searched_target, secondary: row.failure_reason };
}

function getRole(row: ScoutResultRow): { primary: string; secondary: string } {
  if (isPersonLead(row)) {
    return {
      primary: row.title,
      secondary: row.why_target || row.explanation,
    };
  }

  if (row.candidate_category === 'organization_only') {
    return { primary: 'No CRM-ready person', secondary: row.explanation };
  }

  if (row.candidate_category === 'not_found') {
    return { primary: 'No acceptable contact', secondary: row.explanation };
  }

  return { primary: row.failure_reason, secondary: row.explanation };
}

function getEmail(row: ScoutResultRow): { primary: string; secondary: string } {
  if (isPersonLead(row)) {
    return {
      primary: row.email && row.email.toLowerCase() !== 'missing' ? row.email : 'Missing',
      secondary: formatContactStatus(row.validation?.email.status ?? row.email_status),
    };
  }

  return { primary: 'Missing', secondary: 'no validated contact' };
}

function getPhone(row: ScoutResultRow): { primary: string; secondary: string } {
  const phoneStatus = row.validation?.phone.status;
  if (phoneStatus === 'verified_found') {
    return { primary: 'Captured', secondary: 'verified' };
  }

  if (phoneStatus === 'deduced_with_pattern_evidence') {
    return { primary: 'Captured', secondary: 'deduced' };
  }

  if (phoneStatus === 'failed') {
    return { primary: 'Blocked', secondary: 'failed' };
  }

  if (phoneStatus === 'missing') {
    return { primary: 'Not captured', secondary: 'missing' };
  }

  return { primary: 'Not captured', secondary: 'unsupported' };
}

function getSource(row: ScoutResultRow): { label: string; href: string | null; detail: string } {
  const sourceUrl = row.validation?.source.source_url ?? ('source_url' in row ? row.source_url ?? null : null);
  if (!sourceUrl) {
    return { label: 'No source', href: null, detail: 'no URL captured' };
  }

  try {
    const parsed = new URL(sourceUrl);
    const hostname = parsed.hostname.replace(/^www\./, '');
    const pathParts = parsed.pathname.split('/').filter(Boolean);
    const lastPart = pathParts[pathParts.length - 1];
    const label = lastPart ? lastPart.replace(/[-_]+/g, ' ') : hostname;
    return { label, href: sourceUrl, detail: hostname };
  } catch {
    return { label: sourceUrl, href: sourceUrl, detail: 'source URL' };
  }
}

function getReason(row: ScoutResultRow): { primary: string; secondary: string | null } {
  const primary = row.primary_filter_reason || (isPersonLead(row) ? row.why_target || row.explanation : row.explanation);
  if (isPersonLead(row)) {
    const secondary = row.explanation && row.explanation !== primary ? row.explanation : null;
    return { primary, secondary };
  }

  if (row.candidate_category === 'failed') {
    const secondary = row.failure_reason !== primary ? row.failure_reason : null;
    return { primary, secondary };
  }

  return { primary, secondary: null };
}

function getStatusContext(tier: OutputTier, reason: { primary: string; secondary: string | null }) {
  if (tier === 'high_trust_usable') {
    return { primary: 'Contact proof present.', secondary: null };
  }

  return reason;
}

function countSummary(results: ScoutResponse, distribution: Record<OutputTier, number>): string {
  const sourceCount = results.metrics.funnel_counts?.source_snapshots;
  const reviewCount = distribution.review + distribution.failed;
  const intro = sourceCount
    ? `${results.leads.length} categorized rows from ${sourceCount} source records.`
    : `${results.leads.length} categorized rows returned.`;
  return `${intro} ${distribution.high_trust_usable} are ready with contact proof; ${reviewCount} need manual review.`;
}

function shouldShowLowSignal(results: ScoutResponse, distribution: Record<OutputTier, number>): boolean {
  return results.leads.length < 10 || distribution.high_trust_usable === 0;
}

export default function PrimaryResultsOverview({
  leadExport,
  onBuildExport,
  results,
  rows,
  sortMode,
  onOpenEvidence,
  onSortChange,
}: PrimaryResultsOverviewProps) {
  const [activeFilter, setActiveFilter] = useState<PrimaryResultFilter>('all');
  const distribution = buildTierDistribution(results.leads, results.metrics.tier_distribution);

  useEffect(() => {
    setActiveFilter('all');
  }, [results]);

  const filteredRows = rows.filter((row) => rowMatchesFilter(row, activeFilter));
  const sectionRows = SECTION_ORDER.map((tier) => ({
    tier,
    rows: filteredRows.filter((row) => getOutputTier(row) === tier),
  })).filter((section) => section.rows.length > 0);

  const lowSignal = shouldShowLowSignal(results, distribution);

  return (
    <section className="mt-6 rounded-lg border border-[#d7deea] bg-white p-4 shadow-[0_18px_42px_rgba(10,18,38,0.07)] sm:p-5">
      <div className="grid overflow-hidden rounded-lg border border-[#d7deea] bg-[#d7deea] sm:grid-cols-2 xl:grid-cols-[minmax(250px,1.5fr)_repeat(5,minmax(112px,1fr))_minmax(168px,0.9fr)]">
        <div className="bg-white px-4 py-4">
          <p className="text-base font-semibold text-[#0a1226]">Source-assisted run</p>
          <p className="mt-2 text-sm leading-6 text-[#536175]">{countSummary(results, distribution)}</p>
        </div>
        {FILTER_OPTIONS.map((option) => {
          const count = getFilterCount(option.key, distribution, results.leads.length);

          return (
            <CountTile
              key={option.key}
              active={activeFilter === option.key}
              count={count}
              label={option.label}
              onClick={() => setActiveFilter(option.key)}
              tone={COUNT_TILE_TONE[option.key]}
            />
          );
        })}
        <div className="grid gap-2 bg-white px-4 py-4">
          <button
            className="inline-flex h-10 items-center justify-center rounded-md border border-[#2d7bff] bg-[#2d7bff] px-4 text-sm font-semibold text-white transition hover:bg-[#1f65d8]"
            onClick={onBuildExport}
            type="button"
          >
            {leadExport ? 'Rebuild CSV export' : 'Build CSV export'}
          </button>
          {leadExport ? (
            <a
              className="inline-flex h-10 items-center justify-center rounded-md border border-[#b7cffd] bg-white px-4 text-sm font-semibold text-[#0e3a8a] transition hover:border-[#2d7bff] hover:bg-[#f5f9ff]"
              download={leadExport.filename}
              href={leadExport.csvDataUrl}
            >
              Download CSV
            </a>
          ) : null}
        </div>
      </div>

      {leadExport ? (
        <p className="mt-3 text-sm leading-6 text-[#536175]">
          CSV ready: {leadExport.rowCount} row{leadExport.rowCount === 1 ? '' : 's'} generated {leadExport.generatedAtLabel}.
        </p>
      ) : null}

      {lowSignal ? (
        <div className="mt-4 rounded-lg border border-[#edc98f] bg-[#fff8ec] px-4 py-3">
          <p className="text-sm font-semibold text-[#7a4a05]">Low Public Signal</p>
          <p className="mt-1 text-sm leading-6 text-[#7a5a1d]">
            This market has a low public data footprint. Most candidates lack enough traceable contact evidence to mark READY.
          </p>
        </div>
      ) : null}

      <div className="mt-5 flex justify-end">
        <label className="flex items-center gap-3 text-sm text-[#536175]" htmlFor="primaryLeadSortMode">
          <span className="text-[11px] font-black uppercase tracking-[0.1em] text-[#60708a]">Review order</span>
          <select
            className="rounded-md border border-[#cbd5e1] bg-white px-3 py-2 text-sm text-[#0a1226] outline-none focus:border-[#2d7bff]"
            id="primaryLeadSortMode"
            name="primaryLeadSortMode"
            onChange={(event) => onSortChange(event.target.value as LeadSortMode)}
            value={sortMode}
          >
            {LEAD_SORT_OPTIONS.map((option) => (
              <option key={option.value} value={option.value}>
                {option.label}
              </option>
            ))}
          </select>
        </label>
      </div>

      <div className="mt-5 hidden overflow-x-auto md:block">
        <table className="w-full min-w-[980px] border-separate border-spacing-0 overflow-hidden rounded-lg border border-[#d7deea]" aria-label="Candidate review table">
          <thead className="bg-[#f1f4f8]">
            <tr className="text-left text-[11px] font-black uppercase tracking-[0.1em] text-[#60708a]">
              <th className="px-4 py-3">Organization</th>
              <th className="px-4 py-3">Person</th>
              <th className="px-4 py-3">Role</th>
              <th className="px-4 py-3">Email</th>
              <th className="px-4 py-3">Phone</th>
              <th className="px-4 py-3">Source</th>
              <th className="px-4 py-3">Status</th>
              <th className="px-4 py-3">Evidence</th>
            </tr>
          </thead>
          <tbody>
            {sectionRows.map((section) => (
              <FragmentRows
                key={section.tier}
                rows={section.rows}
                section={SECTION_COPY[section.tier]}
                tier={section.tier}
                onOpenEvidence={onOpenEvidence}
              />
            ))}
          </tbody>
        </table>
      </div>

      <div className="mt-5 grid gap-4 md:hidden">
        {sectionRows.map(({ tier, rows: tierRows }) => (
          <section key={tier} className="space-y-3">
            <div className="rounded-lg border border-[#d7deea] bg-[#f7f9fc] px-4 py-3">
              <p className="text-[11px] font-black uppercase tracking-[0.1em] text-[#60708a]">{SECTION_COPY[tier].title}</p>
              <p className="mt-1 text-sm leading-6 text-[#536175]">{SECTION_COPY[tier].description}</p>
            </div>
            {tierRows.map((row, index) => {
              const person = getPerson(row);
              const role = getRole(row);
              const email = getEmail(row);
              const phone = getPhone(row);
              const source = getSource(row);
              const reason = getReason(row);
              const rowTier = getOutputTier(row);

              return (
                <article key={`${getOrganization(row)}-${person.primary}-${index}`} className={`rounded-lg border border-[#d7deea] p-4 ${ROW_TONE[rowTier]}`}>
                  <div className="flex items-start justify-between gap-3">
                    <div>
                      <h3 className="text-lg font-semibold leading-tight text-[#0a1226]">{getOrganization(row)}</h3>
                      <p className="mt-1 text-sm leading-6 text-[#536175]">
                        {person.primary} - {role.primary}
                      </p>
                    </div>
                    <span className={`rounded-full border px-3 py-1 text-xs font-black uppercase tracking-[0.08em] ${STATUS_TONE[rowTier]}`}>
                      {TIER_LABELS[rowTier]}
                    </span>
                  </div>

                  <div className="mt-4 grid gap-3 sm:grid-cols-2">
                    <MobileDetailCard label="Email" primary={email.primary} secondary={email.secondary} />
                    <MobileDetailCard label="Phone" primary={phone.primary} secondary={phone.secondary} />
                    <MobileDetailCard label="Source" primary={source.label} secondary={source.detail} />
                    <MobileDetailCard label="Reason" primary={reason.primary} secondary={reason.secondary ?? person.secondary} />
                  </div>

                  <button
                    className="mt-4 inline-flex w-full items-center justify-center rounded-md border border-[#b7cffd] bg-white px-4 py-3 text-sm font-black text-[#0e3a8a] transition hover:border-[#2d7bff] hover:bg-[#f5f9ff]"
                    onClick={() => onOpenEvidence(row)}
                    type="button"
                  >
                    Inspect evidence
                  </button>
                </article>
              );
            })}
          </section>
        ))}
      </div>
    </section>
  );
}

function CountTile({
  active,
  count,
  label,
  onClick,
  tone,
}: {
  active: boolean;
  count: number;
  label: string;
  onClick: () => void;
  tone: string;
}) {
  return (
    <button
      aria-label={`${label} ${count}`}
      aria-pressed={active}
      className={`bg-white px-4 py-4 text-left transition focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-[-2px] focus-visible:outline-[#2d7bff] ${
        active ? 'relative z-10 ring-2 ring-inset ring-[#2d7bff]' : 'hover:bg-[#f5f9ff]'
      }`}
      onClick={onClick}
      type="button"
    >
      <span className="block text-[11px] font-black uppercase tracking-[0.1em] text-[#60708a]">{label}</span>
      <span className={`mt-2 block text-3xl font-semibold ${tone}`}>{count}</span>
    </button>
  );
}

function FragmentRows({
  onOpenEvidence,
  rows,
  section,
  tier,
}: {
  onOpenEvidence: (row: ScoutResultRow) => void;
  rows: ScoutResultRow[];
  section: { title: string; description: string };
  tier: OutputTier;
}) {
  return (
    <>
      <tr className="bg-[#f7f9fc]">
        <th className="border-y border-[#d7deea] px-4 py-3 text-left" colSpan={8}>
          <p className="text-[11px] font-black uppercase tracking-[0.1em] text-[#60708a]">{section.title}</p>
          <p className="mt-1 text-sm font-medium text-[#536175]">{section.description}</p>
        </th>
      </tr>
      {rows.map((row, index) => {
        const organization = getOrganization(row);
        const person = getPerson(row);
        const role = getRole(row);
        const email = getEmail(row);
        const phone = getPhone(row);
        const source = getSource(row);
        const reason = getReason(row);
        const rowTier = getOutputTier(row);
        const statusContext = getStatusContext(rowTier, reason);

        return (
          <tr key={`${organization}-${person.primary}-${index}`} className={`${ROW_TONE[rowTier]} text-sm text-[#0a1226]`}>
            <td className="border-t border-[#d7deea] px-4 py-3 align-top">
              <p className="font-semibold">{organization}</p>
            </td>
            <td className="border-t border-[#d7deea] px-4 py-3 align-top">
              <p className="font-semibold">{person.primary}</p>
              <p className="mt-1 text-xs text-[#60708a]">{person.secondary}</p>
            </td>
            <td className="border-t border-[#d7deea] px-4 py-3 align-top">
              <p className="font-medium">{role.primary}</p>
            </td>
            <td className="border-t border-[#d7deea] px-4 py-3 align-top">
              <p className="font-medium">{email.primary}</p>
              <p className="mt-1 text-xs text-[#60708a]">{email.secondary}</p>
            </td>
            <td className="border-t border-[#d7deea] px-4 py-3 align-top">
              <p className="font-medium">{phone.primary}</p>
              <p className="mt-1 text-xs text-[#60708a]">{phone.secondary}</p>
            </td>
            <td className="border-t border-[#d7deea] px-4 py-3 align-top">
              {source.href ? (
                <a className="font-semibold text-[#0e3a8a] underline decoration-[#b7cffd] underline-offset-4" href={source.href} rel="noreferrer" target="_blank">
                  {source.label}
                </a>
              ) : (
                <p className="font-medium text-[#60708a]">{source.label}</p>
              )}
              <p className="mt-1 text-xs text-[#60708a]">{source.detail}</p>
            </td>
            <td className="border-t border-[#d7deea] px-4 py-3 align-top">
              <span className={`inline-flex rounded-full border px-3 py-1 text-xs font-black uppercase tracking-[0.08em] ${STATUS_TONE[tier]}`}>
                {TIER_LABELS[rowTier]}
              </span>
              <p className="mt-2 max-w-[15rem] text-xs leading-5 text-[#536175]">{statusContext.primary}</p>
              {statusContext.secondary ? <p className="mt-1 text-xs leading-5 text-[#60708a]">{statusContext.secondary}</p> : null}
            </td>
            <td className="border-t border-[#d7deea] px-4 py-3 align-top">
              <button
                aria-label={`Inspect evidence for ${person.primary}`}
                className="inline-flex rounded-md border border-[#b7cffd] bg-white px-3 py-2 text-xs font-black uppercase tracking-[0.08em] text-[#0e3a8a] transition hover:border-[#2d7bff] hover:bg-[#f5f9ff]"
                onClick={() => onOpenEvidence(row)}
                type="button"
              >
                Evidence
              </button>
            </td>
          </tr>
        );
      })}
    </>
  );
}

function MobileDetailCard({
  label,
  primary,
  secondary,
}: {
  label: string;
  primary: string;
  secondary: string | null;
}) {
  return (
    <div className="rounded-lg border border-[#d7deea] bg-white px-4 py-3">
      <p className="text-[11px] font-black uppercase tracking-[0.1em] text-[#60708a]">{label}</p>
      <p className="mt-2 font-semibold text-[#0a1226]">{primary}</p>
      {secondary ? <p className="mt-1 text-sm leading-6 text-[#536175]">{secondary}</p> : null}
    </div>
  );
}
