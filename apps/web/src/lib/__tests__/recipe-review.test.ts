import { expect, test } from 'vitest';
import {
  buildFridayRecipeReviewCsv,
  buildFridayRecipeReviewFilename,
  buildFridayRecipeReviewMarkdown,
  buildFridayRecipeReviewRows,
} from '../recipe-review';

test('builds a Friday recipe review export with readable markdown and escaped CSV', () => {
  const generatedAt = new Date('2026-05-06T12:34:00.000Z');
  const rows = buildFridayRecipeReviewRows(
    [
      {
        id: 'recipe-1',
        name: 'K-12 IT directors, West',
        query: 'K-12 IT directors in Albuquerque, NM',
        filters: { location: 'New Mexico' },
        created_at: '2026-05-05T18:00:00.000Z',
      },
      {
        id: 'recipe-2',
        name: 'General sweep',
        query: 'School districts',
        filters: {},
        created_at: '2026-05-05T19:00:00.000Z',
      },
    ],
    [
      {
        recipe_id: 'recipe-1',
        recipe_name: 'K-12 IT directors, West',
        total_api_cost_usd: 0.42,
        total_leads_returned: 3,
        usable_lead_count: 2,
        total_operator_minutes: 18.5,
        minutes_per_usable_lead: 9.25,
        api_cost_per_usable_lead: 0.21,
        feedback_counts: { usable: 2 },
      },
    ],
    generatedAt,
  );

  expect(rows).toEqual([
    {
      recipeName: 'K-12 IT directors, West',
      query: 'K-12 IT directors in Albuquerque, NM',
      location: 'New Mexico',
      createdAt: expect.any(String),
      totalLeadsReturned: '3',
      usableLeads: '2',
      totalApiCostUsd: '$0.42',
      totalOperatorMinutes: '18.5',
      minutesPerUsableLead: '9.25',
      apiCostPerUsableLead: '$0.21',
      validationContext: expect.stringContaining('Validated in-app on'),
    },
    {
      recipeName: 'General sweep',
      query: 'School districts',
      location: 'All locations',
      createdAt: expect.any(String),
      totalLeadsReturned: '0',
      usableLeads: '0',
      totalApiCostUsd: '$0.00',
      totalOperatorMinutes: '0.0',
      minutesPerUsableLead: 'n/a',
      apiCostPerUsableLead: 'n/a',
      validationContext: expect.stringContaining('Validated in-app on'),
    },
  ]);

  const markdown = buildFridayRecipeReviewMarkdown(rows, generatedAt);
  expect(markdown).toContain('# Friday recipe review');
  expect(markdown).toContain('Generated:');
  expect(markdown).toContain('| Recipe | Query | Location | Created at | Leads returned | Usable leads | API cost spent | Operator minutes | Minutes / usable lead | API cost / usable lead | Validation context |');
  expect(markdown).toContain('K-12 IT directors, West');

  const csv = buildFridayRecipeReviewCsv(rows);
  expect(csv).toContain('recipe_name,query,location,created_at,leads_returned,usable_leads,api_cost_spent_usd,operator_minutes,minutes_per_usable_lead,api_cost_per_usable_lead,validation_context');
  expect(csv).toContain('"K-12 IT directors, West"');
  expect(csv).toContain('"K-12 IT directors in Albuquerque, NM"');
  expect(buildFridayRecipeReviewFilename(generatedAt)).toBe('white-rabbit-friday-review-2026-05-06.csv');
});
