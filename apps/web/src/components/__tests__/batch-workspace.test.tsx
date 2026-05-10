import { render, screen } from '@testing-library/react';
import { afterEach, expect, test, vi } from 'vitest';
import BatchWorkspace from '../batch-workspace';

afterEach(() => {
  vi.unstubAllGlobals();
});

test('renders the debiased batch defaults', async () => {
  vi.stubGlobal(
    'fetch',
    vi.fn(() =>
      Promise.resolve(
        new Response(JSON.stringify([]), {
          status: 200,
          headers: { 'content-type': 'application/json' },
        }),
      ),
    ),
  );

  render(<BatchWorkspace />);

  expect(screen.getByText(/internal evaluation only/i)).toBeDefined();
  expect(
    screen.getByText(/use it only for matt-run internal evaluation, not for thomas or lee daily prospecting/i),
  ).toBeDefined();
  expect(screen.getByPlaceholderText('Monday prospecting sweep')).toBeDefined();
  expect(screen.getByDisplayValue('Healthcare IT directors in Phoenix')).toBeDefined();
  expect(screen.getByDisplayValue('Arizona')).toBeDefined();
  expect(screen.getByDisplayValue('Financial services CISOs in New York')).toBeDefined();
  expect(screen.getByDisplayValue('New York')).toBeDefined();
  expect(await screen.findByText(/no batch jobs yet/i)).toBeDefined();
});
