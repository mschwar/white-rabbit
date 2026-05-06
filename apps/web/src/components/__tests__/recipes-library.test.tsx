import { fireEvent, render, screen, waitFor } from '@testing-library/react';
import { afterEach, expect, test, vi } from 'vitest';
import RecipesLibrary from '../recipes-library';

afterEach(() => {
  vi.unstubAllGlobals();
});

test('loads recipes and shows the selected recipe runs', async () => {
  const fetchMock = vi.fn((input: RequestInfo | URL) => {
    const url = input.toString();

    if (url.endsWith('/api/recipes')) {
      return Promise.resolve(
        new Response(
          JSON.stringify([
            {
              id: 'recipe-1',
              name: 'K-12 IT directors',
              query: 'K-12 IT directors in Albuquerque',
              filters: { location: 'New Mexico' },
              created_at: '2026-05-06T12:00:00.000Z',
            },
          ]),
          { status: 200, headers: { 'content-type': 'application/json' } },
        ),
      );
    }

    if (url.endsWith('/api/recipes/recipe-1/runs')) {
      return Promise.resolve(
        new Response(
          JSON.stringify([
            {
              id: 'run-1',
              recipe_id: 'recipe-1',
              mode: 'full',
              started_at: '2026-05-06T12:10:00.000Z',
              ended_at: null,
              operator_minutes: null,
              lead_count: 3,
            },
          ]),
          { status: 200, headers: { 'content-type': 'application/json' } },
        ),
      );
    }

    return Promise.resolve(new Response('not found', { status: 404 }));
  });

  vi.stubGlobal('fetch', fetchMock);

  render(<RecipesLibrary />);

  expect(await screen.findByRole('heading', { name: /recipe library/i })).toBeDefined();
  expect(await screen.findByRole('button', { name: /k-12 it directors/i })).toBeDefined();
  expect(await screen.findByText(/3\s+leads/i)).toBeDefined();

  fireEvent.click(screen.getByRole('button', { name: /k-12 it directors/i }));
  await waitFor(() => expect(fetchMock).toHaveBeenCalledWith('/api/recipes/recipe-1/runs'));
});
