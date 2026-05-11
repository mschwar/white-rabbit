import { expect, test } from 'vitest';
import { buildTierDistribution, getValidationBucket, sortScoutLeads, sortScoutResultRows } from '../scout';

test('sortScoutLeads orders leads by fit, evidence, contact, and gate', () => {
  const leads = [
    {
      name: 'Alpha',
      title: 'Director',
      organization: 'Alpha Schools',
      email: 'alpha@example.com',
      email_status: 'Found' as const,
      source_url: 'https://alpha.example.com',
      confidence: 0.9,
      why_target: 'Alpha',
      icebreaker: 'Alpha',
      fit_score: 0.2,
      evidence_score: 0.8,
      contact_score: 0.4,
      gate_passed: false,
      explanation: 'Alpha',
    },
    {
      name: 'Bravo',
      title: 'Director',
      organization: 'Bravo Schools',
      email: 'bravo@example.com',
      email_status: 'Found' as const,
      source_url: 'https://bravo.example.com',
      confidence: 0.9,
      why_target: 'Bravo',
      icebreaker: 'Bravo',
      fit_score: 0.9,
      evidence_score: 0.1,
      contact_score: 0.7,
      gate_passed: true,
      explanation: 'Bravo',
    },
    {
      name: 'Charlie',
      title: 'Director',
      organization: 'Charlie Schools',
      email: 'charlie@example.com',
      email_status: 'Found' as const,
      source_url: 'https://charlie.example.com',
      confidence: 0.9,
      why_target: 'Charlie',
      icebreaker: 'Charlie',
      fit_score: 0.6,
      evidence_score: 0.6,
      contact_score: 0.95,
      gate_passed: true,
      explanation: 'Charlie',
    },
  ];

  expect(sortScoutLeads(leads, 'rank').map((lead) => lead.name)).toEqual(['Alpha', 'Bravo', 'Charlie']);
  expect(sortScoutLeads(leads, 'fit').map((lead) => lead.name)).toEqual(['Bravo', 'Charlie', 'Alpha']);
  expect(sortScoutLeads(leads, 'evidence').map((lead) => lead.name)).toEqual(['Alpha', 'Charlie', 'Bravo']);
  expect(sortScoutLeads(leads, 'contact').map((lead) => lead.name)).toEqual(['Charlie', 'Bravo', 'Alpha']);
  expect(sortScoutLeads(leads, 'gate').map((lead) => lead.name)).toEqual(['Bravo', 'Charlie', 'Alpha']);
});

test('validation buckets separate ready, review, organization-only, and not-found rows', () => {
  const rows = [
    {
      candidate_category: 'person_lead' as const,
      tier: 'high_trust_usable' as const,
      name: 'Usable Lead',
      title: 'Director',
      organization: 'Usable Schools',
      email: 'usable@example.com',
      email_status: 'Found' as const,
      source_url: 'https://usable.example.com',
      confidence: 0.9,
      why_target: 'Usable',
      icebreaker: 'Usable',
      fit_score: 0.9,
      evidence_score: 0.8,
      contact_score: 0.7,
      gate_passed: true,
      explanation: 'Usable',
    },
    {
      candidate_category: 'person_lead' as const,
      tier: 'review' as const,
      name: 'Noisy Lead',
      title: 'Director',
      organization: 'Noisy Schools',
      email: 'noisy@example.com',
      email_status: 'Found' as const,
      source_url: 'https://noisy.example.com',
      confidence: 0.9,
      why_target: 'Noisy',
      icebreaker: 'Noisy',
      fit_score: 0.3,
      evidence_score: 0.2,
      contact_score: 0.1,
      gate_passed: false,
      explanation: 'Noisy',
    },
    {
      candidate_category: 'organization_only' as const,
      tier: 'organization_only' as const,
      organization: 'Example Corp',
      explanation: 'Organization-only',
    },
    {
      candidate_category: 'not_found' as const,
      tier: 'not_found' as const,
      searched_target: 'Ghost District',
      organization: 'Ghost District',
      explanation: 'Not found',
    },
    {
      candidate_category: 'failed' as const,
      tier: 'failed' as const,
      searched_target: 'Broken District',
      failure_reason: 'Source failed',
      explanation: 'Failed',
    },
  ];

  expect(rows.map((row) => getValidationBucket(row))).toEqual([
    'usable',
    'noisy_failed',
    'organization_only',
    'not_found',
    'noisy_failed',
  ]);
});

test('sortScoutResultRows keeps validation buckets grouped while sorting person rows by signal', () => {
  const rows = [
    {
      candidate_category: 'person_lead' as const,
      tier: 'high_trust_usable' as const,
      name: 'Alpha',
      title: 'Director',
      organization: 'Alpha Schools',
      email: 'alpha@example.com',
      email_status: 'Found' as const,
      source_url: 'https://alpha.example.com',
      confidence: 0.9,
      why_target: 'Alpha',
      icebreaker: 'Alpha',
      fit_score: 0.2,
      evidence_score: 0.8,
      contact_score: 0.4,
      gate_passed: true,
      explanation: 'Alpha',
    },
    {
      candidate_category: 'organization_only' as const,
      tier: 'organization_only' as const,
      organization: 'Example Corp',
      explanation: 'Example Corp',
    },
    {
      candidate_category: 'person_lead' as const,
      tier: 'review' as const,
      name: 'Bravo',
      title: 'Director',
      organization: 'Bravo Schools',
      email: 'bravo@example.com',
      email_status: 'Found' as const,
      source_url: 'https://bravo.example.com',
      confidence: 0.9,
      why_target: 'Bravo',
      icebreaker: 'Bravo',
      fit_score: 0.9,
      evidence_score: 0.1,
      contact_score: 0.7,
      gate_passed: false,
      explanation: 'Bravo',
    },
    {
      candidate_category: 'not_found' as const,
      tier: 'not_found' as const,
      searched_target: 'Ghost District',
      organization: 'Ghost District',
      explanation: 'Ghost District',
    },
  ];

  expect(sortScoutResultRows(rows, 'fit').map((row) => row.candidate_category ?? 'person_lead')).toEqual([
    'person_lead',
    'person_lead',
    'organization_only',
    'not_found',
  ]);
  expect(
    sortScoutResultRows(rows, 'fit').map((row) => {
      if ('name' in row) {
        return row.name;
      }

      if (row.candidate_category === 'organization_only') {
        return row.organization;
      }

      return row.searched_target;
    }),
  ).toEqual(['Alpha', 'Bravo', 'Example Corp', 'Ghost District']);
});

test('buildTierDistribution uses API metrics when provided and falls back to rows', () => {
  const rows = [
    {
      candidate_category: 'person_lead' as const,
      tier: 'high_trust_usable' as const,
      name: 'Ready Lead',
      title: 'Director',
      organization: 'Ready Schools',
      email: 'ready@example.com',
      email_status: 'verified_found' as const,
      source_url: 'https://ready.example.com',
      confidence: 0.9,
      why_target: 'Ready',
      icebreaker: 'Ready',
      fit_score: 0.9,
      evidence_score: 0.8,
      contact_score: 0.7,
      gate_passed: true,
      explanation: 'Ready',
    },
    {
      candidate_category: 'failed' as const,
      tier: 'failed' as const,
      searched_target: 'Blocked District',
      failure_reason: 'Source contradicted the row.',
      explanation: 'Blocked',
    },
  ];

  expect(buildTierDistribution(rows).high_trust_usable).toBe(1);
  expect(buildTierDistribution(rows).failed).toBe(1);
  expect(buildTierDistribution(rows, { review: 3 })).toEqual({
    high_trust_usable: 0,
    review: 3,
    organization_only: 0,
    not_found: 0,
    failed: 0,
  });
});
