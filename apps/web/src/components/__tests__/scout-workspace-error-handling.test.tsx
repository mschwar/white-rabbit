import { fireEvent, render, screen, waitFor } from '@testing-library/react';
import { afterEach, expect, test, vi } from 'vitest';
import ScoutWorkspace from '../scout-workspace';

afterEach(() => {
  vi.unstubAllGlobals();
});

test('shows plain-text API errors without crashing the error reader', async () => {
  const fetchMock = vi.fn((input: RequestInfo | URL) => {
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
      new Response('Internal Server Error', {
        status: 500,
        headers: { 'content-type': 'text/plain' },
      }),
    );
  });
  vi.stubGlobal('fetch', fetchMock);

  render(<ScoutWorkspace />);

  fireEvent.click(screen.getByRole('button', { name: /run scout search/i }));

  await waitFor(() => expect(fetchMock).toHaveBeenCalledTimes(2));
  expect(await screen.findByText('Internal Server Error')).toBeDefined();
});
