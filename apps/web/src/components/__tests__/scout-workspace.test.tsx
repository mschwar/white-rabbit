import { fireEvent, render, screen, waitFor } from '@testing-library/react';
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

test('submits a scout query and renders ranked results', async () => {
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

  render(<ScoutWorkspace />);

  fireEvent.change(screen.getByLabelText(/prospecting query/i), {
    target: { value: 'K-12 IT directors in Albuquerque' },
  });
  fireEvent.change(screen.getByLabelText(/location/i), {
    target: { value: 'New Mexico' },
  });
  fireEvent.click(screen.getByRole('button', { name: /run scout search/i }));

  await waitFor(() => expect(fetchMock).toHaveBeenCalledTimes(2));
  expect(screen.getByRole('heading', { name: /returned leads/i })).toBeDefined();
  expect(await screen.findByRole('heading', { name: /jane smith/i })).toBeDefined();
  expect(screen.getByText('91%')).toBeDefined();
  expect(screen.getByText('84%')).toBeDefined();
  expect(screen.getByText('79%')).toBeDefined();
});

test('renders the debiased scout placeholders and export description', () => {
  render(<ScoutWorkspace />);

  expect(screen.getByText(/scout: quick preview \(up to 15 leads, no storage\)\. full: stored recipe with up to 100 leads\./i)).toBeDefined();
  expect(screen.getByPlaceholderText('Healthcare IT directors in Phoenix')).toBeDefined();

  fireEvent.click(screen.getByRole('button', { name: /^full$/i }));
  expect(screen.getByPlaceholderText('My prospect list')).toBeDefined();
});

test('sorts scout results by score and gate state', async () => {
const fetchMock = makeFetchMock({
leads: [
{
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
gate_passed: false,
explanation: 'Alpha lead explanation.',
},
{
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
expect(screen.getAllByRole('heading', { level: 3 }).map((heading) => heading.textContent)).toEqual([
'Alpha Lead',
'Bravo Lead',
]);

fireEvent.change(screen.getByLabelText(/sort leads/i), { target: { value: 'fit' } });
expect(screen.getAllByRole('heading', { level: 3 }).map((heading) => heading.textContent)).toEqual([
'Bravo Lead',
'Alpha Lead',
]);

fireEvent.change(screen.getByLabelText(/sort leads/i), { target: { value: 'gate' } });
expect(screen.getAllByRole('heading', { level: 3 }).map((heading) => heading.textContent)).toEqual([
'Bravo Lead',
'Alpha Lead',
]);
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
            run_id: 'run-1',
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
  fireEvent.change(screen.getByLabelText(/recipe name/i), {
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
  expect(await screen.findByText(/full run saved/i)).toBeDefined();

  fireEvent.click(screen.getByRole('button', { name: /build lead export/i }));

  expect(await screen.findByRole('link', { name: /download csv/i })).toHaveAttribute(
    'download',
    expect.stringMatching(/^white-rabbit-lead-export-\d{4}-\d{2}-\d{2}\.csv$/),
  );
  expect(
    screen.getByText(
      /includes query, location, recipe name, run ID, rank, lead name\/title\/org\/email, email status, source URL, fit\/evidence\/contact scores, gate status, icebreaker, why_target, explanation, and validation context/i,
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
