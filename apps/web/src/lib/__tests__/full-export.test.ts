import { expect, test } from 'vitest';
import { buildFullLeadExportCsv, buildFullLeadExportFilename, buildFullLeadExportRows } from '../full-export';
import type { CandidateValidation, ScoutResultRow } from '../scout';

function makeValidation(statuses: {
  name?: CandidateValidation['name']['status'];
  title?: CandidateValidation['title']['status'];
  organization?: CandidateValidation['organization']['status'];
  email?: CandidateValidation['email']['status'];
  phone?: CandidateValidation['phone']['status'];
  source?: CandidateValidation['source']['status'];
} = {}): CandidateValidation {
  const field = (status: CandidateValidation['name']['status'], label: string) => ({
    status,
    source_url: `https://validation.example.com/${label}`,
    evidence_snippet: `${label} ${status} evidence`,
    checked_at: '2026-05-10T12:00:00Z',
    notes: `${label} ${status} notes`,
  });

  const contact = (status: CandidateValidation['email']['status'], label: string) => ({
    status,
    source_url: `https://validation.example.com/${label}`,
    evidence_snippet: `${label} ${status} evidence`,
    checked_at: '2026-05-10T12:00:00Z',
    notes: `${label} ${status} notes`,
  });

  return {
    name: field(statuses.name ?? 'supported', 'name'),
    title: field(statuses.title ?? 'supported', 'title'),
    organization: field(statuses.organization ?? 'supported', 'organization'),
    email: contact(statuses.email ?? 'verified_found', 'email'),
    phone: contact(statuses.phone ?? 'missing', 'phone'),
    source: field(statuses.source ?? 'supported', 'source'),
  };
}

function parseCsv(csv: string): Array<Record<string, string>> {
  const [headerLine, ...lines] = csv.trim().split('\n');
  const headers = headerLine.split(',');

  return lines.map((line) => {
    const values = line.split(',');
    return Object.fromEntries(headers.map((header, index) => [header, values[index] ?? '']));
  });
}

test('builds a validation export csv with candidate categories and validation notes', () => {
  const rows: ScoutResultRow[] = [
    {
      candidate_category: 'person_lead',
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
      candidate_category: 'person_lead',
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
        email: 'failed',
        phone: 'missing',
        source: 'supported',
      }),
    },
    {
      candidate_category: 'organization_only',
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
  ];

  const exportRows = buildFullLeadExportRows({
    query: 'K-12 IT directors in Albuquerque',
    location: 'New Mexico',
    recipeName: 'District leadership',
    runId: 'run-1',
    sortMode: 'fit',
    rows: [rows[1], rows[0], rows[2], rows[3], rows[4]],
    guardrail: {
      status: 'clear',
      message: 'Query guardrail clear.',
      suggestions: [],
      missing_criteria: [],
    },
    generatedAt: new Date('2026-05-06T12:34:56.000Z'),
  });

  expect(exportRows).toHaveLength(5);
  expect(exportRows[0].candidateCategory).toBe('person_lead');
  expect(exportRows[0].usableCandidate).toBe('yes');
  expect(exportRows[0].leadName).toBe('Jane Smith');
  expect(exportRows[0].email).toBe('jane.smith@aps.edu');
  expect(exportRows[0].emailStatus).toBe('verified_found');
  expect(exportRows[0].phone).toBe('');
  expect(exportRows[0].phoneStatus).toBe('missing');
  expect(exportRows[0].operatorLabel).toBe('READY');
  expect(exportRows[0].rankingGate).toBe('usable');
  expect(exportRows[0].sourceAccessStatus).toBe('supported');
  expect(exportRows[0].validationNotes).toContain('Bucket: usable');
  expect(exportRows[0].validationNotes).toContain('Field statuses: name=supported; title=supported; organization=supported; email=verified_found; phone=missing; source=supported');
  expect(exportRows[0].checkedAt).toBe('2026-05-10T12:00:00Z');

  expect(exportRows[1].usableCandidate).toBe('no');
  expect(exportRows[1].email).toBe('');
  expect(exportRows[1].emailStatus).toBe('failed');
  expect(exportRows[1].rankingGate).toBe('noisy_failed');
  expect(exportRows[1].fitScore).toBe('0.31');

  expect(exportRows[2].candidateCategory).toBe('failed');
  expect(exportRows[2].usableCandidate).toBe('no');
  expect(exportRows[2].emailStatus).toBe('failed');
  expect(exportRows[2].rankingGate).toBe('noisy_failed');
  expect(exportRows[2].validationNotes).toContain('Failure: Source was inaccessible.');

  expect(exportRows[3].candidateCategory).toBe('organization_only');
  expect(exportRows[3].leadName).toBe('');
  expect(exportRows[3].title).toBe('');
  expect(exportRows[3].email).toBe('');
  expect(exportRows[3].emailStatus).toBe('missing');
  expect(exportRows[3].rankingGate).toBe('organization_only');

  expect(exportRows[4].candidateCategory).toBe('not_found');
  expect(exportRows[4].organization).toBe('Ghost District');
  expect(exportRows[4].rankingGate).toBe('not_found');

  const csv = buildFullLeadExportCsv(exportRows);
  const parsed = parseCsv(csv);

  expect(csv).toContain(
    'lead_name,title,organization,email,email_status,phone,phone_status,usable_candidate,operator_label,candidate_category,rank,query,run_id,fit_score,evidence_score,contact_score,ranking_gate,source_name_url,source_title_url,source_org_url,source_email_url,source_phone_url,source_access_status,validation_notes,checked_at,location,recipe_name,sort_mode,generated_at',
  );
  expect(parsed).toHaveLength(5);
  expect(parsed[0].candidate_category).toBe('person_lead');
  expect(parsed[0].lead_name).toBe('Jane Smith');
  expect(parsed[0].email).toBe('jane.smith@aps.edu');
  expect(parsed[0].phone).toBe('');
  expect(parsed[0].operator_label).toBe('READY');
  expect(parsed[2].candidate_category).toBe('failed');
  expect(parsed[2].email).toBe('');
  expect(parsed[2].validation_notes).toContain('Failure: Source was inaccessible.');
  expect(parsed[3].candidate_category).toBe('organization_only');
  expect(parsed[3].lead_name).toBe('');
  expect(parsed[3].email_status).toBe('missing');
  expect(parsed[3].ranking_gate).toBe('organization_only');
});

test('builds a stable lead export filename', () => {
  expect(buildFullLeadExportFilename(new Date('2026-05-06T12:34:56.000Z'))).toBe('white-rabbit-lead-export-2026-05-06.csv');
});
