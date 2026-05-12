import { fireEvent, render, screen, waitFor, within } from '@testing-library/react';
import { afterEach, expect, test, vi } from 'vitest';
import ScoutWorkspace from '../scout-workspace';

afterEach(() => {
  vi.unstubAllGlobals();
});

function makeFetchMock(scoutResponse: object) {
  return vi.fn((input: RequestInfo | URL) => {
    const url = input.toString();
    if (url.endsWith('/api/sandbox')) {
      return Promise.resolve(
        new Response(
          JSON.stringify({
            total_queries: 0,
            total_rows: 0,
            max_queries: 10,
            max_rows: 1000,
            remaining_queries: 10,
            remaining_rows: 1000,
            reset_at: new Date().toISOString(),
          }),
          { status: 200, headers: { 'content-type': 'application/json' } },
        ),
      );
    }
    return Promise.resolve(
      new Response(JSON.stringify(scoutResponse), {
        status: 200,
        headers: { 'content-type': 'application/json' },
      }),
    );
  });
}

function makeValidation(statuses: {
  name?: string;
  title?: string;
  organization?: string;
  email?: string;
  phone?: string;
  source?: string;
} = {}) {
  const field = (status: string, label: string) => ({
    status,
    source_url: `https://validation.example.com/${label}`,
    evidence_snippet: `${label} ${status} evidence`,
    checked_at: '2026-05-10T12:00:00Z',
    notes: `${label} ${status} notes`,
  });

  const contact = (status: string, label: string) => ({
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

test('renders validation buckets and badges for mixed scout results', async () => {
  const fetchMock = makeFetchMock({
    leads: [
      {
        candidate_category: 'person_lead',
        tier: 'high_trust_usable',
        primary_filter_reason: 'READY: supported person, organization, source, and usable contact cleared the evidence gate.',
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
        validation: makeValidation(),
      },
      {
        candidate_category: 'person_lead',
        tier: 'review',
        primary_filter_reason: 'REVIEW: contact is missing; row is not CRM-ready.',
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
          email: 'supported',
          phone: 'missing',
          source: 'supported',
        }),
      },
      {
        candidate_category: 'organization_only',
        tier: 'organization_only',
        primary_filter_reason: 'Organization was found, but no validated person was ready.',
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
        tier: 'not_found',
        primary_filter_reason: 'Target was searched, but no acceptable contact was found.',
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
        tier: 'failed',
        primary_filter_reason: 'Source was inaccessible.',
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
    ],
    metrics: {
      input_tokens: 123,
      output_tokens: 45,
      tavily_searches: 1,
      openai_web_searches: 0,
      elapsed_seconds: 1.23,
      estimated_cost_usd: 0.010123,
      tier_distribution: {
        high_trust_usable: 1,
        review: 1,
        organization_only: 1,
        not_found: 1,
        failed: 1,
      },
    },
  });
  vi.stubGlobal('fetch', fetchMock);

  render(<ScoutWorkspace />);

  fireEvent.change(screen.getByLabelText(/prospecting query/i), {
    target: { value: 'K-12 IT directors in Albuquerque' },
  });
  fireEvent.change(screen.getByLabelText(/location/i), {
    target: { value: 'New Mexico' },
  });
  fireEvent.click(screen.getByRole('button', { name: /run scout search/i }));

  await waitFor(() => expect(fetchMock).toHaveBeenCalledTimes(2));
  expect(screen.getByRole('heading', { name: /tier summary/i })).toBeDefined();
  expect(screen.getAllByText('READY').length).toBeGreaterThan(0);
  expect(screen.getAllByText('REVIEW').length).toBeGreaterThan(0);
  expect(screen.getAllByText('ORG-ONLY').length).toBeGreaterThan(0);
  expect(screen.getAllByText('NOT FOUND').length).toBeGreaterThan(0);

  const usableTable = screen.getByRole('table', { name: /ready results/i });
  const noisyTable = screen.getByRole('table', { name: /review results/i });
  const organizationOnlyTable = screen.getByRole('table', { name: /org-only results/i });
  const notFoundTable = screen.getByRole('table', { name: /not found results/i });

  expect(within(usableTable).getByText('Jane Smith')).toBeDefined();
  expect(
    within(usableTable).getByText((_, element) => {
      const text = element?.textContent?.replace(/\s+/g, '').toLowerCase() ?? '';
      return element?.tagName === 'SPAN' && text === 'namesupported';
    }),
  ).toBeDefined();
  expect(
    within(usableTable).getByText((_, element) => {
      const text = element?.textContent?.replace(/\s+/g, '').toLowerCase() ?? '';
      return element?.tagName === 'SPAN' && text === 'emailverified';
    }),
  ).toBeDefined();
  expect(
    within(usableTable).getByText((_, element) => {
      const text = element?.textContent?.replace(/\s+/g, '').toLowerCase() ?? '';
      return element?.tagName === 'SPAN' && text === 'sourcesupported';
    }),
  ).toBeDefined();

  expect(within(noisyTable).getByText('Noisy Lead')).toBeDefined();
  expect(
    within(organizationOnlyTable).getByText((_, element) => {
      return element?.tagName === 'P' && element.className.includes('text-lg') && element.textContent === 'Example Corp';
    }),
  ).toBeDefined();
  expect(
    within(notFoundTable).getByText((_, element) => {
      return element?.tagName === 'P' && element.className.includes('text-lg') && element.textContent === 'Ghost District';
    }),
  ).toBeDefined();
  expect(screen.getAllByText(/source was inaccessible/i).length).toBeGreaterThan(0);
  expect(screen.getAllByText(/contact is missing; row is not crm-ready/i).length).toBeGreaterThan(0);
  expect(screen.getAllByText(/the candidate could not be trusted/i).length).toBeGreaterThan(0);

  fireEvent.click(within(usableTable).getByRole('button', { name: /view evidence for jane smith/i }));
  const usableDrawer = screen.getByRole('dialog', { name: /jane smith/i });
  expect(within(usableDrawer).getByText(/evidence drawer/i)).toBeDefined();
  expect(within(usableDrawer).getByText(/verified found/i)).toBeDefined();
  expect(within(usableDrawer).getByRole('link', { name: 'https://validation.example.com/name' })).toBeDefined();
  expect(within(usableDrawer).getAllByText('2026-05-10T12:00:00Z').length).toBeGreaterThan(0);
  fireEvent.click(within(usableDrawer).getByRole('button', { name: /close/i }));
  expect(screen.queryByRole('dialog', { name: /jane smith/i })).toBeNull();

  fireEvent.click(screen.getByRole('button', { name: /view evidence for broken district/i }));
  const failedDrawer = screen.getByRole('dialog', { name: /broken district/i });
  expect(within(failedDrawer).getByText(/source was inaccessible/i)).toBeDefined();
  expect(within(failedDrawer).getAllByText(/^failed$/i).length).toBeGreaterThan(0);
  expect(within(failedDrawer).getByRole('link', { name: 'https://validation.example.com/source' })).toBeDefined();
});

test('renders lead-search copy without premature operator surfaces', async () => {
  render(<ScoutWorkspace />);

  expect(screen.getByRole('heading', { name: /find source-backed prospects/i })).toBeDefined();
  expect(screen.getByPlaceholderText('Healthcare IT directors in Phoenix')).toBeDefined();
  expect(screen.getByText('Search usage')).toBeDefined();
  expect(screen.queryByText(/fastapi/i)).toBeNull();
  expect(screen.queryByText(/\/api\/scout/i)).toBeNull();
  expect(screen.queryByText(/recipe storage/i)).toBeNull();
  expect(screen.queryByRole('button', { name: /reset sandbox/i })).toBeNull();
  expect(screen.queryByRole('link', { name: /recipe library/i })).toBeNull();

  fireEvent.click(screen.getByRole('button', { name: /^full$/i }));
  expect(screen.getByLabelText(/search label/i)).toBeDefined();
  expect(screen.getByPlaceholderText('Phoenix healthcare leaders')).toBeDefined();
  expect(screen.queryByLabelText(/recipe name/i)).toBeNull();
});

test('renders the primary search shell with one natural-language input', async () => {
  const fetchMock = makeFetchMock({
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
    metrics: {
      input_tokens: 123,
      output_tokens: 45,
      tavily_searches: 1,
      openai_web_searches: 0,
      elapsed_seconds: 1.23,
      estimated_cost_usd: 0.010123,
    },
  });
  vi.stubGlobal('fetch', fetchMock);

  render(<ScoutWorkspace primaryMode />);

  expect(screen.getByRole('heading', { name: /start with the target/i })).toBeDefined();
  expect(screen.getByLabelText(/target/i)).toBeDefined();
  expect(screen.getByLabelText(/source context/i)).toBeDefined();
  expect(screen.getByRole('button', { name: /find candidates/i })).toBeDefined();
  expect(screen.queryByRole('button', { name: /^scout$/i })).toBeNull();
  expect(screen.queryByRole('button', { name: /^full$/i })).toBeNull();
  expect(screen.queryByLabelText(/location/i)).toBeNull();
  expect(screen.queryByText(/search usage/i)).toBeNull();
  expect(screen.queryByRole('button', { name: /build lead export/i })).toBeNull();

  fireEvent.change(screen.getByLabelText(/target/i), {
    target: { value: 'K-12 IT directors in Albuquerque' },
  });
  fireEvent.click(screen.getByRole('button', { name: /find candidates/i }));

  await waitFor(() => expect(fetchMock).toHaveBeenCalledTimes(1));
  expect(fetchMock).toHaveBeenNthCalledWith(1, '/api/scout', expect.any(Object));
  expect(
    JSON.parse((fetchMock.mock.calls[0][1] as RequestInit).body as string),
  ).toEqual({ query: 'K-12 IT directors in Albuquerque' });
  const usableTable = await screen.findByRole('table', { name: /ready results/i });
  expect(within(usableTable).getByText('Jane Smith')).toBeDefined();
});

test('sorts scout results by validation signal and ready tier state', async () => {
const fetchMock = makeFetchMock({
leads: [
{
candidate_category: 'person_lead',
name: 'Alpha Lead',
title: 'Director of Technology',
organization: 'Alpha Schools',
email: 'alpha@example.com',
email_status: 'Found',
source_url: 'https://alpha.example.com',
confidence: 0.9,
why_target: 'Alpha owns the budget',
icebreaker: 'Alpha is expanding.',
fit_score: 0.51,
evidence_score: 0.72,
contact_score: 0.61,
gate_passed: true,
explanation: 'Alpha lead explanation.',
validation: makeValidation({ email: 'verified_found', phone: 'missing', source: 'supported' }),
},
{
candidate_category: 'person_lead',
name: 'Bravo Lead',
title: 'IT Director',
organization: 'Bravo Schools',
email: 'bravo@example.com',
email_status: 'Found',
source_url: 'https://bravo.example.com',
confidence: 0.92,
why_target: 'Bravo is a strong match',
icebreaker: 'Bravo is modernizing.',
fit_score: 0.84,
evidence_score: 0.31,
contact_score: 0.78,
gate_passed: true,
explanation: 'Bravo lead explanation.',
validation: makeValidation({ email: 'verified_found', phone: 'missing', source: 'supported' }),
},
],
metrics: {
input_tokens: 123,
output_tokens: 45,
tavily_searches: 1,
openai_web_searches: 0,
elapsed_seconds: 1.23,
estimated_cost_usd: 0.010123,
},
});
vi.stubGlobal('fetch', fetchMock);

render(<ScoutWorkspace />);

fireEvent.change(screen.getByLabelText(/prospecting query/i), {
target: { value: 'K-12 IT directors in Albuquerque' },
});
fireEvent.click(screen.getByRole('button', { name: /run scout search/i }));

await waitFor(() => expect(fetchMock).toHaveBeenCalledTimes(2));
const usableTable = await screen.findByRole('table', { name: /ready results/i });
let alphaLead = within(usableTable).getByText('Alpha Lead');
let bravoLead = within(usableTable).getByText('Bravo Lead');
expect(alphaLead.compareDocumentPosition(bravoLead) & Node.DOCUMENT_POSITION_FOLLOWING).toBeTruthy();

fireEvent.change(screen.getByLabelText(/sort results/i), { target: { value: 'fit' } });
alphaLead = within(usableTable).getByText('Alpha Lead');
bravoLead = within(usableTable).getByText('Bravo Lead');
expect(bravoLead.compareDocumentPosition(alphaLead) & Node.DOCUMENT_POSITION_FOLLOWING).toBeTruthy();
});

test('shows guardrail guidance for a lead query that needs more detail', async () => {
  const fetchMock = makeFetchMock({
    leads: [],
    metrics: {
      input_tokens: 0,
      output_tokens: 0,
      tavily_searches: 0,
      openai_web_searches: 0,
      elapsed_seconds: 0.12,
      estimated_cost_usd: 0,
    },
    query_guardrail: {
      status: 'needs_more_detail',
      message: 'This is a lead-generation query, but tighter results will come from adding a title, vertical/company type, and location.',
      suggestions: ['Add a title or role, such as director, manager, VP, or owner.'],
      missing_criteria: ['target title or role', 'company type or vertical', 'location'],
    },
  });
  vi.stubGlobal('fetch', fetchMock);

  render(<ScoutWorkspace />);

  fireEvent.change(screen.getByLabelText(/prospecting query/i), {
    target: { value: 'IT directors' },
  });
  fireEvent.click(screen.getByRole('button', { name: /run scout search/i }));

  await waitFor(() => expect(fetchMock).toHaveBeenCalledTimes(2));
  expect(await screen.findByText(/query could be tighter/i)).toBeDefined();
  expect(screen.getByText(/add a title or role/i)).toBeDefined();
});

test('builds a CSV export from a full run', async () => {
  const fetchMock = vi.fn((input: RequestInfo | URL) => {
    const url = input.toString();

    if (url.endsWith('/api/full')) {
      return Promise.resolve(
        new Response(
          JSON.stringify({
            run_id: 'qa-validation-buckets-run',
            recipe_id: 'recipe-1',
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
            metrics: {
              input_tokens: 123,
              output_tokens: 45,
              tavily_searches: 1,
              openai_web_searches: 0,
              elapsed_seconds: 1.23,
              estimated_cost_usd: 0.010123,
            },
            query_guardrail: null,
          }),
          { status: 200, headers: { 'content-type': 'application/json' } },
        ),
      );
    }

    return Promise.resolve(new Response('not found', { status: 404 }));
  });

  vi.stubGlobal('fetch', fetchMock);

  render(<ScoutWorkspace />);

  fireEvent.click(screen.getByRole('button', { name: /^full$/i }));
  fireEvent.change(screen.getByLabelText(/search label/i), {
    target: { value: 'District leadership' },
  });
  fireEvent.change(screen.getByLabelText(/prospecting query/i), {
    target: { value: 'K-12 IT directors in Albuquerque' },
  });
  fireEvent.change(screen.getByLabelText(/location/i), {
    target: { value: 'New Mexico' },
  });
  fireEvent.click(screen.getByRole('button', { name: /run full search/i }));

  await waitFor(() => expect(fetchMock).toHaveBeenCalledWith('/api/full', expect.any(Object)));
  expect(await screen.findByText(/full run saved for internal review/i)).toBeDefined();
  expect(screen.queryByRole('link', { name: /open recipe library/i })).toBeNull();

  fireEvent.click(screen.getByRole('button', { name: /build validation export/i }));

  expect(await screen.findByRole('link', { name: /download csv/i })).toHaveAttribute(
    'download',
    expect.stringMatching(/^white-rabbit-lead-export-\d{4}-\d{2}-\d{2}\.csv$/),
  );
  expect(
    screen.getByText(
      /includes candidate category, readiness tier, field and contact statuses, source support, validation signals, gate status, and validation notes/i,
    ),
  ).toBeDefined();
});

test('shows a validation message for blank queries', async () => {
  vi.stubGlobal('fetch', vi.fn());

  render(<ScoutWorkspace />);

  fireEvent.change(screen.getByLabelText(/prospecting query/i), { target: { value: '   ' } });
  fireEvent.click(screen.getByRole('button', { name: /run scout search/i }));

  expect(await screen.findByText(/enter a query before searching/i)).toBeDefined();
});

test('captures a correction and exposes the review queue export from the evidence drawer', async () => {
  const correctionRecord = {
    id: '44444444-4444-4444-4444-444444444444',
    lead_id: 'qa-usable-1',
    run_id: 'qa-validation-buckets-run',
    query: 'K-12 IT directors in Albuquerque',
    label: 'corrected_field',
    field_name: 'title',
    previous_value: 'Director of Technology',
    corrected_value: 'Director of IT',
    notes: 'Title was updated after a better source was found.',
    created_at: '2026-05-10T12:00:00Z',
  };
  const fetchMock = vi.fn((input: RequestInfo | URL, init?: RequestInit) => {
    const url = input.toString();
    if (url.endsWith('/api/sandbox')) {
      return Promise.resolve(
        new Response(
          JSON.stringify({
            total_queries: 0,
            total_rows: 0,
            max_queries: 10,
            max_rows: 1000,
            remaining_queries: 10,
            remaining_rows: 1000,
            reset_at: new Date().toISOString(),
          }),
          { status: 200, headers: { 'content-type': 'application/json' } },
        ),
      );
    }

    if (url.endsWith('/api/full')) {
      return Promise.resolve(
        new Response(
          JSON.stringify({
            run_id: 'qa-validation-buckets-run',
            recipe_id: 'recipe-1',
            leads: [
              {
                id: 'qa-usable-1',
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
                validation: makeValidation(),
              },
            ],
            metrics: {
              input_tokens: 123,
              output_tokens: 45,
              tavily_searches: 1,
              openai_web_searches: 0,
              elapsed_seconds: 1.23,
              estimated_cost_usd: 0.010123,
            },
            query_guardrail: null,
          }),
          { status: 200, headers: { 'content-type': 'application/json' } },
        ),
      );
    }

    if (url.endsWith('/api/leads/qa-usable-1/corrections') && init?.method === 'POST') {
      const body = JSON.parse(String(init.body ?? '{}'));
      correctionRecord.label = body.label;
      correctionRecord.field_name = body.field_name;
      correctionRecord.previous_value = body.previous_value;
      correctionRecord.corrected_value = body.corrected_value;
      correctionRecord.notes = body.notes;
      return Promise.resolve(
        new Response(JSON.stringify(correctionRecord), {
          status: 200,
          headers: { 'content-type': 'application/json' },
        }),
      );
    }

    if (url.endsWith('/api/runs/qa-validation-buckets-run/corrections')) {
      return Promise.resolve(
        new Response(JSON.stringify([correctionRecord]), {
          status: 200,
          headers: { 'content-type': 'application/json' },
        }),
      );
    }

    return Promise.resolve(new Response('not found', { status: 404 }));
  });

  vi.stubGlobal('fetch', fetchMock);

  render(<ScoutWorkspace />);

  fireEvent.click(screen.getByRole('button', { name: /^full$/i }));
  fireEvent.change(screen.getByLabelText(/search label/i), {
    target: { value: 'District leadership' },
  });
  fireEvent.change(screen.getByLabelText(/prospecting query/i), {
    target: { value: 'K-12 IT directors in Albuquerque' },
  });
  fireEvent.change(screen.getByLabelText(/location/i), {
    target: { value: 'New Mexico' },
  });
  fireEvent.click(screen.getByRole('button', { name: /run full search/i }));

  await waitFor(() => expect(fetchMock).toHaveBeenCalledWith('/api/full', expect.any(Object)));
  fireEvent.click(await screen.findByRole('button', { name: /view evidence for jane smith/i }));

  const drawer = await screen.findByRole('dialog', { name: /jane smith/i });
  fireEvent.change(within(drawer).getByLabelText(/correction type/i), { target: { value: 'corrected_field' } });
  fireEvent.change(within(drawer).getByLabelText(/corrected field/i), { target: { value: 'title' } });
  fireEvent.change(within(drawer).getByLabelText(/previous value/i), {
    target: { value: 'Director of Technology' },
  });
  fireEvent.change(within(drawer).getByLabelText(/corrected value/i), {
    target: { value: 'Director of IT' },
  });
  fireEvent.change(within(drawer).getByLabelText(/notes/i), {
    target: { value: 'Title was updated after a better source was found.' },
  });
  fireEvent.click(within(drawer).getByRole('button', { name: /save correction/i }));

  await waitFor(() =>
    expect(fetchMock).toHaveBeenCalledWith(
      '/api/leads/qa-usable-1/corrections',
      expect.objectContaining({ method: 'POST' }),
    ),
  );
  expect(await within(drawer).findByRole('link', { name: /download review queue json/i })).toHaveAttribute(
    'download',
    'white-rabbit-corrections-qa-validation-buckets-run.json',
  );
  expect(await within(drawer).findByText(/loaded 1 correction from the review queue/i)).toBeDefined();
});
