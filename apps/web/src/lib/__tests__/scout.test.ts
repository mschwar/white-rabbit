import { expect, test } from 'vitest';
import { sortScoutLeads } from '../scout';

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
