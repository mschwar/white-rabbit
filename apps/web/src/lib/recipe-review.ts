import type { RecipeItem, RecipeScoreboardItem } from './scout';

export type FridayRecipeReviewRow = {
  recipeName: string;
  query: string;
  location: string;
  createdAt: string;
  totalLeadsReturned: string;
  usableLeads: string;
  totalApiCostUsd: string;
  totalOperatorMinutes: string;
  minutesPerUsableLead: string;
  apiCostPerUsableLead: string;
  validationContext: string;
};

const sharedDateFormatter = new Intl.DateTimeFormat('en-US', {
  dateStyle: 'medium',
  timeStyle: 'short',
});

function formatUsd(value: number): string {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  }).format(value);
}

function formatOptionalUsd(value: number | null): string {
  return value == null ? 'n/a' : formatUsd(value);
}

function formatOptionalNumber(value: number | null): string {
  return value == null ? 'n/a' : value.toFixed(2);
}

function escapeCsvCell(value: string): string {
  if (/[,"\n]/.test(value)) {
    return `"${value.replaceAll('"', '""')}"`;
  }
  return value;
}

function escapeMarkdownCell(value: string): string {
  return value.replaceAll('|', '\\|').replaceAll('\n', ' ');
}

function extractLocation(filters: RecipeItem['filters']): string {
  const location = filters.location;
  return typeof location === 'string' && location.trim() ? location.trim() : 'All locations';
}

export function buildFridayRecipeReviewRows(
  recipes: RecipeItem[],
  scoreboards: RecipeScoreboardItem[],
  generatedAt = new Date(),
): FridayRecipeReviewRow[] {
  const scoreboardByRecipeId = new Map(scoreboards.map((scoreboard) => [scoreboard.recipe_id, scoreboard] as const));

  return recipes.map((recipe) => {
    const scoreboard = scoreboardByRecipeId.get(recipe.id);
    return {
      recipeName: recipe.name,
      query: recipe.query,
      location: extractLocation(recipe.filters),
      createdAt: sharedDateFormatter.format(new Date(recipe.created_at)),
      totalLeadsReturned: String(scoreboard?.total_leads_returned ?? 0),
      usableLeads: String(scoreboard?.usable_lead_count ?? 0),
      totalApiCostUsd: formatUsd(scoreboard?.total_api_cost_usd ?? 0),
      totalOperatorMinutes: (scoreboard?.total_operator_minutes ?? 0).toFixed(1),
      minutesPerUsableLead: formatOptionalNumber(scoreboard?.minutes_per_usable_lead ?? null),
      apiCostPerUsableLead: formatOptionalUsd(scoreboard?.api_cost_per_usable_lead ?? null),
      validationContext: `Validated in-app on ${sharedDateFormatter.format(generatedAt)} using the saved recipe and scoreboard totals.`,
    };
  });
}

export function buildFridayRecipeReviewMarkdown(rows: FridayRecipeReviewRow[], generatedAt = new Date()): string {
  const headers = [
    'Recipe',
    'Query',
    'Location',
    'Created at',
    'Leads returned',
    'Usable leads',
    'API cost spent',
    'Operator minutes',
    'Minutes / usable lead',
    'API cost / usable lead',
    'Validation context',
  ];

  const lines = [
    '# Friday recipe review',
    '',
    `Generated: ${sharedDateFormatter.format(generatedAt)}`,
    '',
    '| ' + headers.join(' | ') + ' |',
    '| ' + headers.map(() => '---').join(' | ') + ' |',
    ...rows.map((row) =>
      '| ' +
      [
        row.recipeName,
        row.query,
        row.location,
        row.createdAt,
        row.totalLeadsReturned,
        row.usableLeads,
        row.totalApiCostUsd,
        row.totalOperatorMinutes,
        row.minutesPerUsableLead,
        row.apiCostPerUsableLead,
        row.validationContext,
      ]
        .map(escapeMarkdownCell)
        .join(' | ') +
      ' |',
    ),
  ];

  return lines.join('\n');
}

export function buildFridayRecipeReviewCsv(rows: FridayRecipeReviewRow[]): string {
  const headers = [
    'recipe_name',
    'query',
    'location',
    'created_at',
    'leads_returned',
    'usable_leads',
    'api_cost_spent_usd',
    'operator_minutes',
    'minutes_per_usable_lead',
    'api_cost_per_usable_lead',
    'validation_context',
  ];

  const body = rows.map((row) =>
    [
      row.recipeName,
      row.query,
      row.location,
      row.createdAt,
      row.totalLeadsReturned,
      row.usableLeads,
      row.totalApiCostUsd,
      row.totalOperatorMinutes,
      row.minutesPerUsableLead,
      row.apiCostPerUsableLead,
      row.validationContext,
    ]
      .map(escapeCsvCell)
      .join(','),
  );

  return [headers.join(','), ...body].join('\n');
}

export function buildFridayRecipeReviewFilename(generatedAt = new Date()): string {
  return `white-rabbit-friday-review-${generatedAt.toISOString().slice(0, 10)}.csv`;
}
