import { fireEvent, render, screen, waitFor } from '@testing-library/react';
import { afterEach, expect, test, vi } from 'vitest';
import ScoutWorkspace from '../scout-workspace';

afterEach(() => {
  vi.unstubAllGlobals();
});

test('shows plain-text API errors without crashing the error reader', async () => {
  const fetchMock = vi.fn().mockResolvedValue(
    new Response('Internal Server Error', {
      status: 500,
      headers: { 'content-type': 'text/plain' },
    }),
  );
  vi.stubGlobal('fetch', fetchMock);

  render(<ScoutWorkspace />);

  fireEvent.click(screen.getByRole('button', { name: /run scout search/i }));

  await waitFor(() => expect(fetchMock).toHaveBeenCalledTimes(1));
  expect(await screen.findByText('Internal Server Error')).toBeDefined();
});
