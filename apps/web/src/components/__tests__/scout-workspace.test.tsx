import { fireEvent, render, screen, waitFor } from '@testing-library/react';
import { afterEach, expect, test, vi } from 'vitest';
import ScoutWorkspace from '../scout-workspace';

afterEach(() => {
  vi.unstubAllGlobals();
});

test('submits a scout query and renders ranked results', async () => {
  const fetchMock = vi.fn().mockResolvedValue(
    new Response(
      JSON.stringify({
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
      }),
      {
        status: 200,
        headers: { 'content-type': 'application/json' },
      },
    ),
  );
  vi.stubGlobal('fetch', fetchMock);

  render(<ScoutWorkspace />);

  fireEvent.change(screen.getByLabelText(/prospecting query/i), {
    target: { value: 'K-12 IT directors in Albuquerque' },
  });
  fireEvent.change(screen.getByLabelText(/location/i), {
    target: { value: 'New Mexico' },
  });
  fireEvent.click(screen.getByRole('button', { name: /run scout search/i }));

  await waitFor(() => expect(fetchMock).toHaveBeenCalledTimes(1));
  expect(screen.getByRole('heading', { name: /returned leads/i })).toBeDefined();
  expect(await screen.findByRole('heading', { name: /jane smith/i })).toBeDefined();
  expect(screen.getByText('91%')).toBeDefined();
  expect(screen.getByText('84%')).toBeDefined();
  expect(screen.getByText('79%')).toBeDefined();
});

test('shows a validation message for blank queries', async () => {
  vi.stubGlobal('fetch', vi.fn());

  render(<ScoutWorkspace />);

  fireEvent.change(screen.getByLabelText(/prospecting query/i), { target: { value: '   ' } });
  fireEvent.click(screen.getByRole('button', { name: /run scout search/i }));

  expect(await screen.findByText(/enter a query before searching/i)).toBeDefined();
});
