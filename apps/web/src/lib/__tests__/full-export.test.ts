import { expect, test } from 'vitest';
import { buildFullLeadExportCsv, buildFullLeadExportFilename, buildFullLeadExportRows } from '../full-export';

test('builds a lead export csv with validation context and metadata', () => {
  const rows = buildFullLeadExportRows({
    query: 'K-12 IT directors in Albuquerque',
    location: 'New Mexico',
    recipeName: 'District leadership',
    runId: 'run-1',
    sortMode: 'fit',
    leads: [
      {
        name: 'Jane Smith',
        title: 'Director of Technology',
        organization: 'Albuquerque Public Schools',
        email: 'jane.smith@aps.edu',
        email_status: 'Found',
        source_url: 'https://aps.edu/tech',
        confidence: 0.88,
        why_target: 'Owns district telecom decisions',
        icebreaker: 'I noticed APS is growing its classroom connectivity needs.',
        fit_score: 0.91,
        evidence_score: 0.84,
        contact_score: 0.79,
        gate_passed: true,
        explanation: 'Strong district fit with current leadership evidence and usable email.',
      },
    ],
    guardrail: {
      status: 'clear',
      message: 'Query guardrail clear.',
      suggestions: [],
      missing_criteria: [],
    },
    generatedAt: new Date('2026-05-06T12:34:56.000Z'),
  });

  expect(rows).toHaveLength(1);
  expect(rows[0].recipeName).toBe('District leadership');
  expect(rows[0].validationContext).toContain('Query guardrail clear.');
  expect(rows[0].validationContext).toContain('Sort mode: fit.');
  expect(rows[0].validationContext).toContain('Validated from source https://aps.edu/tech.');

  const csv = buildFullLeadExportCsv(rows);
  expect(csv).toContain('generated_at,sort_mode,recipe_name,query,location,run_id,rank,name,title,organization,email,email_status,source_url,fit_score,evidence_score,contact_score,gate_passed,why_target,explanation,icebreaker,validation_context');
  expect(csv).toContain('District leadership');
  expect(csv).toContain('Jane Smith');
  expect(csv).toContain('yes');
});

test('builds a stable lead export filename', () => {
  expect(buildFullLeadExportFilename(new Date('2026-05-06T12:34:56.000Z'))).toBe('white-rabbit-lead-export-2026-05-06.csv');
});
