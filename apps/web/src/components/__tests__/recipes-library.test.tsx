import { fireEvent, render, screen, waitFor } from '@testing-library/react';
import { afterEach, expect, test, vi } from 'vitest';
import RecipesLibrary from '../recipes-library';

afterEach(() => {
  vi.unstubAllGlobals();
});

test('loads recipes, scoreboard, and shows the selected recipe runs', async () => {
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

    if (url.endsWith('/api/recipes/recipe-1/scoreboard')) {
      return Promise.resolve(
        new Response(
          JSON.stringify({
            recipe_id: 'recipe-1',
            recipe_name: 'K-12 IT directors',
            total_api_cost_usd: 0.42,
            total_leads_returned: 3,
            usable_lead_count: 2,
            total_operator_minutes: 18.5,
            minutes_per_usable_lead: 9.25,
            api_cost_per_usable_lead: 0.21,
            feedback_counts: {
              usable: 2,
              wrong_persona: 0,
              bad_source: 0,
              bad_contact: 0,
              duplicate: 0,
            },
          }),
          { status: 200, headers: { 'content-type': 'application/json' } },
        ),
      );
    }

    return Promise.resolve(new Response('not found', { status: 404 }));
  });

  vi.stubGlobal('fetch', fetchMock);

  render(<RecipesLibrary />);

  expect(await screen.findByRole('heading', { name: /recipe library/i })).toBeDefined();
  expect(await screen.findByText(/internal evaluation only/i)).toBeDefined();
  expect(
    await screen.findByText(/not for Thomas or Lee daily prospecting/i),
  ).toBeDefined();
  expect(await screen.findByRole('button', { name: /k-12 it directors/i })).toBeDefined();
  expect(await screen.findByText(/usable leads/i)).toBeDefined();
  expect(await screen.findByText(/minutes \/ usable lead/i)).toBeDefined();
  expect(await screen.findByText(/api cost \/ usable lead/i)).toBeDefined();

  fireEvent.click(screen.getByRole('button', { name: /k-12 it directors/i }));
  await waitFor(() => expect(fetchMock).toHaveBeenCalledWith('/api/recipes/recipe-1/runs'));
});

test('builds the Friday review export for all recipes', async () => {
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
            {
              id: 'recipe-2',
              name: 'District leadership',
              query: 'School district leadership in New Mexico',
              filters: { location: 'New Mexico' },
              created_at: '2026-05-06T13:00:00.000Z',
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

    if (url.endsWith('/api/recipes/recipe-1/scoreboard')) {
      return Promise.resolve(
        new Response(
          JSON.stringify({
            recipe_id: 'recipe-1',
            recipe_name: 'K-12 IT directors',
            total_api_cost_usd: 0.42,
            total_leads_returned: 3,
            usable_lead_count: 2,
            total_operator_minutes: 18.5,
            minutes_per_usable_lead: 9.25,
            api_cost_per_usable_lead: 0.21,
            feedback_counts: {
              usable: 2,
              wrong_persona: 0,
              bad_source: 0,
              bad_contact: 0,
              duplicate: 0,
            },
          }),
          { status: 200, headers: { 'content-type': 'application/json' } },
        ),
      );
    }

    if (url.endsWith('/api/recipes/recipe-2/scoreboard')) {
      return Promise.resolve(
        new Response(
          JSON.stringify({
            recipe_id: 'recipe-2',
            recipe_name: 'District leadership',
            total_api_cost_usd: 0.33,
            total_leads_returned: 2,
            usable_lead_count: 1,
            total_operator_minutes: 11,
            minutes_per_usable_lead: 11,
            api_cost_per_usable_lead: 0.33,
            feedback_counts: {
              usable: 1,
              wrong_persona: 0,
              bad_source: 0,
              bad_contact: 0,
              duplicate: 0,
            },
          }),
          { status: 200, headers: { 'content-type': 'application/json' } },
        ),
      );
    }

    return Promise.resolve(new Response('not found', { status: 404 }));
  });

  vi.stubGlobal('fetch', fetchMock);

  render(<RecipesLibrary />);

  expect(await screen.findByRole('heading', { name: /recipe library/i })).toBeDefined();
  expect(await screen.findByText(/internal evaluation only/i)).toBeDefined();
  expect(await screen.findByRole('button', { name: /k-12 it directors/i })).toBeDefined();
  expect(await screen.findByText(/usable leads/i)).toBeDefined();
  expect(await screen.findByText(/minutes \/ usable lead/i)).toBeDefined();
  expect(await screen.findByText(/api cost \/ usable lead/i)).toBeDefined();

  fireEvent.click(screen.getByRole('button', { name: /build export/i }));

  await waitFor(() => expect(fetchMock).toHaveBeenCalledWith('/api/recipes/recipe-2/scoreboard'));
  expect(await screen.findByText(/2 recipes · generated/i)).toBeDefined();
  expect(screen.getByRole('link', { name: /download csv/i })).toHaveAttribute(
    'download',
    expect.stringMatching(/^white-rabbit-friday-review-\d{4}-\d{2}-\d{2}\.csv$/),
  );
  expect(screen.getByRole('heading', { name: /shareable csv \+ printable preview/i })).toBeDefined();
});
