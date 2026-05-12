import { chromium } from '@playwright/test';
import crypto from 'node:crypto';
import fs from 'node:fs/promises';
import path from 'node:path';

const baseUrl = process.env.WR_BROWSER_BASE_URL ?? 'http://localhost:3010';
const sessionSecret = process.env.WR_SESSION_SECRET ?? 'codex-test-session-secret';
const outDir = path.resolve('audits/raw/reset-2026-05-10/rg4');
const screenshotDir = path.join(outDir, 'screenshots');

function validation(label, status = 'supported', contact = false) {
  return {
    status,
    source_url: `https://evidence.example.org/${label}`,
    evidence_snippet: `${label} ${status} evidence snippet from public source.`,
    checked_at: '2026-05-12T22:00:00Z',
    notes: `${label} ${status} notes.`,
  };
}

function person(index, tier = 'high_trust_usable') {
  const ready = tier === 'high_trust_usable';
  return {
    id: `person-${index}`,
    candidate_category: 'person_lead',
    tier,
    primary_filter_reason: ready
      ? 'READY: public source evidence supports person, role, organization, and contact.'
      : 'REVIEW: person and organization are source-supported, but direct contact proof is missing.',
    name: `Source Person ${index}`,
    title: index % 2 === 0 ? 'Director of Technology' : 'IT Manager',
    organization: `New Mexico District ${index}`,
    email: ready ? `source.person${index}@district${index}.k12.nm.us` : 'Missing',
    email_status: ready ? 'Found' : 'Missing',
    source_url: `https://district${index}.k12.nm.us/staff/technology`,
    confidence: ready ? 0.91 : 0.68,
    why_target: 'Matches school district technology leadership persona with source support.',
    icebreaker: ready ? 'Recent district technology initiative is visible in public records.' : '',
    fit_score: ready ? 0.91 : 0.7,
    evidence_score: ready ? 0.86 : 0.74,
    contact_score: ready ? 0.81 : 0.2,
    gate_passed: ready,
    explanation: ready
      ? 'Ready with field-level evidence and usable contact proof.'
      : 'Useful for manual lookup, but not safe for CRM-ready export.',
    validation: {
      name: validation(`name-${index}`),
      title: validation(`title-${index}`),
      organization: validation(`organization-${index}`),
      email: validation(`email-${index}`, ready ? 'verified_found' : 'missing', true),
      phone: validation(`phone-${index}`, 'missing', true),
      source: validation(`source-${index}`),
    },
  };
}

const leads = [
  ...Array.from({ length: 12 }, (_, index) => person(index + 1)),
  ...Array.from({ length: 28 }, (_, index) => person(index + 13, 'review')),
  ...Array.from({ length: 10 }, (_, index) => ({
    id: `org-only-${index + 1}`,
    candidate_category: 'organization_only',
    tier: 'organization_only',
    primary_filter_reason: 'ORG-ONLY: district found, but no validated person is safe to treat as ready.',
    organization: `Rio Grande Public Schools ${index + 1}`,
    source_url: `https://riogrande-${index + 1}.example.org`,
    explanation: 'Official source was found, but a technology decision maker was not validated.',
    validation: {
      name: validation(`org-name-${index + 1}`, 'unsupported'),
      title: validation(`org-title-${index + 1}`, 'unsupported'),
      organization: validation(`org-organization-${index + 1}`),
      email: validation(`org-email-${index + 1}`, 'missing', true),
      phone: validation(`org-phone-${index + 1}`, 'missing', true),
      source: validation(`org-source-${index + 1}`),
    },
  })),
  {
    id: 'not-found-1',
    candidate_category: 'not_found',
    tier: 'not_found',
    primary_filter_reason: 'NOT FOUND: target searched, no acceptable contact was supported.',
    searched_target: 'Mesa Valley Schools technology director',
    organization: 'Mesa Valley Schools',
    source_url: 'https://mesavalley.example.org',
    explanation: 'No acceptable person or contact could be supported from available public sources.',
    validation: {
      name: validation('notfound-name', 'unsupported'),
      title: validation('notfound-title', 'unsupported'),
      organization: validation('notfound-organization', 'unsupported'),
      email: validation('notfound-email', 'missing', true),
      phone: validation('notfound-phone', 'missing', true),
      source: validation('notfound-source'),
    },
  },
];

const scoutResponse = {
  leads,
  metrics: {
    input_tokens: 1000,
    output_tokens: 2000,
    tavily_searches: 2,
    openai_web_searches: 0,
    elapsed_seconds: 3.42,
    estimated_cost_usd: 0.18,
    tier_distribution: {
      high_trust_usable: 12,
      review: 28,
      organization_only: 10,
      not_found: 1,
      failed: 0,
    },
    funnel_counts: {
      raw_vendor_hits: 30,
      deduped_sources: 18,
      source_snapshots: 61,
      extracted_candidates: 51,
      categorized_rows: 51,
      person_rows: 40,
      high_trust_usable_rows: 12,
      contact_quality_passes: 12,
    },
  },
};

await fs.mkdir(screenshotDir, { recursive: true });

const browser = await chromium.launch();
const context = await browser.newContext({ viewport: { width: 1440, height: 1200 } });
const page = await context.newPage();
const findings = [];

function base64UrlEncode(value) {
  return Buffer.from(value).toString('base64url');
}

const payload = base64UrlEncode(JSON.stringify({ v: 1, iat: Date.now() }));
const signature = crypto.createHmac('sha256', sessionSecret).update(payload).digest('base64url');
const token = `${payload}.${signature}`;
const cookieUrl = new URL(baseUrl);
await context.addCookies([
  {
    name: 'wr_session',
    value: token,
    domain: cookieUrl.hostname,
    path: '/',
    httpOnly: true,
    sameSite: 'Lax',
    expires: Math.floor(Date.now() / 1000) + 7 * 24 * 60 * 60,
  },
]);

page.on('console', (message) => {
  if (message.type() === 'error') {
    findings.push(`console_error: ${message.text()}`);
  }
});

await page.route('**/api/scout', async (route, request) => {
  const body = request.postDataJSON();
  findings.push(`api_scout_query=${JSON.stringify(body.query)}`);
  await route.fulfill({
    status: 200,
    contentType: 'application/json',
    body: JSON.stringify(scoutResponse),
  });
});

await page.goto(`${baseUrl}/`);
await page.getByRole('heading', { name: /start with the target/i }).waitFor();

await page.screenshot({ path: path.join(screenshotDir, '01-primary-empty.png'), fullPage: true });

const target = page.locator('#query');
const sourceContext = page.getByLabel(/source context/i);
const sourceContextVisibleBeforeRun = (await sourceContext.count()) > 0 && await sourceContext.first().isVisible();
await target.fill('New Mexico school district IT leaders');
if (sourceContextVisibleBeforeRun) {
  await sourceContext.fill('Use official district staff directories, state roster pages, and public technology pages.');
}
await Promise.all([
  page.waitForResponse((response) => response.url().includes('/api/scout') && response.status() === 200),
  page.locator('form button[type="submit"]').click(),
]);
const resultsRendered = (await page.getByText(/results overview/i).count()) > 0;
if (!resultsRendered) {
  findings.push('results_overview_not_rendered_after_fixture_submit');
}
await page.screenshot({ path: path.join(screenshotDir, '02-primary-results.png'), fullPage: true });

await page.getByRole('button', { name: /inspect evidence/i }).first().click();
await page.getByRole('dialog', { name: /jane smith|source person 1/i }).waitFor();
await page.screenshot({ path: path.join(screenshotDir, '03-evidence-dossier.png'), fullPage: true });

const desktopEvidence = {
  targetInputVisible: await target.isVisible(),
  sourceContextVisible: sourceContextVisibleBeforeRun,
  scoutVisible: (await page.getByRole('button', { name: /^scout$/i }).count()) > 0,
  fullVisible: (await page.getByRole('button', { name: /^full$/i }).count()) > 0,
  quotaVisible: (await page.getByText(/search usage/i).count()) > 0,
  resultsOverviewVisible: (await page.getByText(/51 categorized rows from 61 source records/i).count()) > 0,
  readyCountVisible: (await page.getByText(/^12$/).count()) > 0,
  reviewLabelVisible: (await page.getByText(/^REVIEW$/).count()) > 0,
  orgOnlyLabelVisible: (await page.getByText(/^ORG-ONLY$/).count()) > 0,
  notFoundLabelVisible: (await page.getByText(/^NOT FOUND$/).count()) > 0,
  evidenceDossierVisible: (await page.getByText(/evidence dossier/i).count()) > 0,
  sourceTrailVisible: (await page.getByText(/source trail/i).count()) > 0,
  exportControlVisible: (await page.getByRole('button', { name: /export/i }).count()) > 0 || (await page.getByRole('link', { name: /export/i }).count()) > 0,
};

await page.setViewportSize({ width: 390, height: 844 });
await page.getByRole('button', { name: /close/i }).click();
await page.screenshot({ path: path.join(screenshotDir, '04-mobile-results.png'), fullPage: true });
const mobileResultsLayout = await page.evaluate(() => ({
  clientWidth: document.documentElement.clientWidth,
  scrollWidth: document.documentElement.scrollWidth,
  bodyScrollWidth: document.body.scrollWidth,
}));
await page.getByRole('button', { name: /inspect evidence/i }).first().click();
await page.getByRole('dialog', { name: /jane smith|source person 1/i }).waitFor();
await page.screenshot({ path: path.join(screenshotDir, '05-mobile-evidence-dossier.png'), fullPage: true });
const mobileDossierLayout = await page.evaluate(() => ({
  clientWidth: document.documentElement.clientWidth,
  scrollWidth: document.documentElement.scrollWidth,
  bodyScrollWidth: document.body.scrollWidth,
}));

const mobileEvidence = {
  resultsHorizontalOverflow: mobileResultsLayout.scrollWidth > mobileResultsLayout.clientWidth,
  dossierHorizontalOverflow: mobileDossierLayout.scrollWidth > mobileDossierLayout.clientWidth,
  mobileResultsLayout,
  mobileDossierLayout,
  inspectEvidenceVisible: (await page.getByRole('button', { name: /inspect evidence/i }).count()) > 0,
  dossierVisible: (await page.getByRole('dialog', { name: /jane smith|source person 1/i }).count()) > 0,
};

await browser.close();

const summary = {
  baseUrl,
  browserFixtureMode: 'mocked_api_scout_51_rows',
  mockLeadCount: leads.length,
  desktopEvidence,
  mobileEvidence,
  findings,
  screenshots: [
    'screenshots/01-primary-empty.png',
    'screenshots/02-primary-results.png',
    'screenshots/03-evidence-dossier.png',
    'screenshots/04-mobile-results.png',
    'screenshots/05-mobile-evidence-dossier.png',
  ],
};

await fs.writeFile(path.join(outDir, 'evidence/browser-audit-summary.json'), `${JSON.stringify(summary, null, 2)}\n`);
console.log(JSON.stringify(summary, null, 2));
