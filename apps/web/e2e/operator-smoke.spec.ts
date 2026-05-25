import { test, expect, type Page } from '@playwright/test';
import * as fs from 'node:fs/promises';
import * as path from 'node:path';

type ValidationStatus = 'supported' | 'verified_found' | 'missing' | 'unsupported' | 'failed';

function makeValidation(statuses: {
  name?: ValidationStatus;
  title?: ValidationStatus;
  organization?: ValidationStatus;
  email?: ValidationStatus;
  phone?: ValidationStatus;
  source?: ValidationStatus;
} = {}) {
  const field = (status: ValidationStatus, label: string) => ({
    status,
    source_url: `https://validation.example.com/${label}`,
    evidence_snippet: `${label} ${status} evidence`,
    checked_at: '2026-05-19T15:00:00Z',
    notes: `${label} ${status} notes`,
  });

  return {
    name: field(statuses.name ?? 'supported', 'name'),
    title: field(statuses.title ?? 'supported', 'title'),
    organization: field(statuses.organization ?? 'supported', 'organization'),
    email: field(statuses.email ?? 'verified_found', 'email'),
    phone: field(statuses.phone ?? 'missing', 'phone'),
    source: field(statuses.source ?? 'supported', 'source'),
  };
}

const scoutResponse = {
  leads: [
    {
      id: 'lead-ready-1',
      candidate_category: 'person_lead',
      tier: 'high_trust_usable',
      primary_filter_reason: 'READY: supported person, organization, source, and usable contact cleared the evidence gate.',
      name: 'Jane Smith',
      title: 'Director of Technology',
      organization: 'Albuquerque Public Schools',
      email: 'jane.smith@district.example',
      email_status: 'Found',
      phone: '(505) 555-0101',
      phone_status: 'Found',
      source_url: 'https://aps.edu/technology',
      confidence: 0.91,
      why_target: 'Owns district technology decisions.',
      icebreaker: 'APS is expanding classroom connectivity this year.',
      fit_score: 0.91,
      evidence_score: 0.87,
      contact_score: 0.82,
      gate_passed: true,
      explanation: 'Strong district fit with current leadership evidence and usable contact details.',
      validation: makeValidation(),
    },
    {
      id: 'lead-review-1',
      candidate_category: 'person_lead',
      tier: 'review',
      primary_filter_reason: 'REVIEW: contact is missing; row is not CRM-ready.',
      name: 'Daniel Yazzie',
      title: 'Technology Coordinator',
      organization: 'Gallup-McKinley Schools',
      email: '',
      email_status: 'Missing',
      phone: '',
      phone_status: 'Missing',
      source_url: 'https://gmcs.k12.nm.us/technology',
      confidence: 0.71,
      why_target: 'Relevant district technology role, but contact proof is incomplete.',
      icebreaker: 'District device refresh project is publicly visible.',
      fit_score: 0.76,
      evidence_score: 0.72,
      contact_score: 0.21,
      gate_passed: false,
      explanation: 'Useful for manual lookup, but not safe for CRM-ready export.',
      validation: makeValidation({ email: 'missing', phone: 'missing' }),
    },
    {
      id: 'lead-org-1',
      candidate_category: 'organization_only',
      tier: 'organization_only',
      primary_filter_reason: 'ORG-ONLY: district found, but no validated person is safe to treat as ready.',
      organization: 'Santa Fe Public Schools',
      source_url: 'https://www.sfps.info/',
      explanation: 'Organization found, but no validated person is ready.',
      validation: makeValidation({
        name: 'unsupported',
        title: 'unsupported',
        organization: 'supported',
        email: 'missing',
        phone: 'missing',
      }),
    },
  ],
  metrics: {
    input_tokens: 120,
    output_tokens: 240,
    tavily_searches: 2,
    openai_web_searches: 0,
    elapsed_seconds: 1.42,
    estimated_cost_usd: 0.0231,
    tier_distribution: {
      high_trust_usable: 1,
      review: 1,
      organization_only: 1,
      not_found: 0,
      failed: 0,
    },
    funnel_counts: {
      raw_vendor_hits: 5,
      deduped_sources: 4,
      source_snapshots: 6,
      extracted_candidates: 3,
      categorized_rows: 3,
      person_rows: 2,
      high_trust_usable_rows: 1,
      contact_quality_passes: 1,
    },
  },
  run_id: 'qa-r14c-run',
  recipe_id: 'qa-r14c-recipe',
  persistence_readback: {
    run_id: 'qa-r14c-run',
    recipe_id: 'qa-r14c-recipe',
    response_row_count: 3,
    persisted_lead_count: 3,
    db_readback_row_count: 3,
    exportable_row_count: 3,
    row_count_matches: true,
    first_response_lead_ids: ['lead-ready-1', 'lead-review-1', 'lead-org-1'],
    first_db_lead_ids: ['lead-ready-1', 'lead-review-1', 'lead-org-1'],
    tier_distribution: {
      high_trust_usable: 1,
      review: 1,
      organization_only: 1,
      not_found: 0,
      failed: 0,
    },
    candidate_category_distribution: {
      person_lead: 2,
      organization_only: 1,
      not_found: 0,
      failed: 0,
    },
  },
  query_guardrail: null,
  sandbox_usage: null,
};

const artifactDir = process.env.WR_E2E_ARTIFACT_DIR ? path.resolve(process.env.WR_E2E_ARTIFACT_DIR) : null;

async function ensureArtifactDir() {
  if (artifactDir) {
    await fs.mkdir(artifactDir, { recursive: true });
  }
}

async function maybeScreenshot(page: Page, filename: string) {
  if (!artifactDir) {
    return;
  }
  await ensureArtifactDir();
  await page.screenshot({ path: path.join(artifactDir, filename), fullPage: true });
}

test('production-like operator smoke covers login, readiness, and csv export', async ({ page, request, baseURL }) => {
  const smokeSummary: Record<string, unknown> = {
    baseURL,
    artifactDir,
    apiChecks: 'skipped',
  };

  const apiBaseUrl = process.env.WR_E2E_API_BASE_URL;
  if (apiBaseUrl) {
    const healthResponse = await request.get(`${apiBaseUrl}/health`);
    const readinessResponse = await request.get(`${apiBaseUrl}/readiness`);
    const readinessJson = await readinessResponse.json();
    smokeSummary.apiChecks = {
      apiBaseUrl,
      healthStatus: healthResponse.status(),
      healthBody: await healthResponse.json(),
      readinessStatus: readinessResponse.status(),
      readinessBody: readinessJson,
    };
    expect(healthResponse.ok()).toBeTruthy();
    expect((smokeSummary.apiChecks as { healthBody: { status: string } }).healthBody.status).toBe('ok');
    expect(readinessResponse.ok()).toBeTruthy();
    expect(readinessJson).toHaveProperty('status');
  }

  await page.route('**/api/scout', async (route) => {
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify(scoutResponse),
    });
  });
  await page.route('**/api/runs/qa-r14c-run/close', async (route) => {
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({ status: 'ok', ended_at: '2026-05-24T12:00:00Z' }),
    });
  });

  const homeResponse = await page.goto('/');
  expect(homeResponse?.status()).toBe(200);
  expect(page.url()).toContain('/login?next=%2F');
  await expect(page.getByRole('heading', { name: /shared-password access/i })).toBeVisible();
  await maybeScreenshot(page, '01-login-gate.png');

  await page.getByLabel(/password/i).fill(process.env.WR_SHARED_PASSWORD ?? 'codex-test-password');
  await Promise.all([
    page.waitForResponse((response) => response.url().includes('/api/login') && response.status() === 303),
    page.waitForURL((url) => url.pathname === '/'),
    page.getByRole('button', { name: /unlock workspace/i }).click(),
  ]);
  await expect(page).toHaveURL(/\/$/);
  await expect(page.getByRole('heading', { name: /start with the target/i })).toBeVisible();
  await maybeScreenshot(page, '02-home-after-login.png');

  await page.getByLabel(/target/i).fill('New Mexico school district IT leaders');
  await Promise.all([
    page.waitForResponse((response) => response.url().includes('/api/scout') && response.status() === 200),
    page.getByRole('button', { name: /find candidates/i }).click(),
  ]);

  await expect(page.getByRole('button', { name: /build csv export/i })).toBeVisible();
  await expect(page.getByText(/candidate review/i)).toBeVisible();
  const candidateTable = page.getByLabel('Candidate review table');
  await expect(candidateTable.getByText('READY', { exact: true })).toBeVisible();
  await expect(candidateTable.getByText('REVIEW', { exact: true })).toBeVisible();
  await expect(candidateTable.getByText('ORG-ONLY', { exact: true })).toBeVisible();
  await maybeScreenshot(page, '03-results-overview.png');

  await page.getByRole('button', { name: /inspect evidence/i }).first().click();
  await expect(page.getByRole('dialog')).toBeVisible();
  await maybeScreenshot(page, '04-evidence-drawer.png');
  await page.getByRole('button', { name: /close/i }).click();

  await page.getByRole('button', { name: /build csv export/i }).click();
  const csvLink = page.getByRole('link', { name: /download csv/i });
  await expect(csvLink).toBeVisible();
  const downloadName = await csvLink.getAttribute('download');
  const href = await csvLink.getAttribute('href');
  expect(downloadName).toMatch(/^white-rabbit-lead-export-\d{4}-\d{2}-\d{2}\.csv$/);
  expect(href).toMatch(/^data:text\/csv;charset=utf-8,/);

  const csvText = decodeURIComponent((href ?? '').replace('data:text/csv;charset=utf-8,', ''));
  const csvLines = csvText.trim().split('\n');
  expect(csvLines[0]).toContain('lead_name,title,organization,email,email_status,phone,phone_status');
  expect(csvLines[1]).toContain('Jane Smith,Director of Technology,Albuquerque Public Schools,jane.smith@district.example');
  await expect(page.getByText(/run closed with \d+\.\d{2} operator minutes/i)).toBeVisible();
  smokeSummary.export = {
    downloadName,
    firstTwoLines: csvLines.slice(0, 2),
    lineCount: csvLines.length,
  };
  smokeSummary.autoClose = {
    runId: scoutResponse.run_id,
    routeMocked: true,
  };
  await maybeScreenshot(page, '05-export-ready.png');
  await maybeScreenshot(page, '06-auto-close.png');

  const scoutToggle = page.getByRole('button', { name: /^scout$/i });
  const fullToggle = page.getByRole('button', { name: /^full$/i });
  smokeSummary.primaryModeChrome = {
    scoutVisible: await scoutToggle.count(),
    fullVisible: await fullToggle.count(),
  };
  expect(await scoutToggle.count()).toBe(0);
  expect(await fullToggle.count()).toBe(0);

  if (artifactDir) {
    await ensureArtifactDir();
    await fs.writeFile(path.join(artifactDir, 'browser-qa-summary.json'), `${JSON.stringify(smokeSummary, null, 2)}\n`);
  }
});
