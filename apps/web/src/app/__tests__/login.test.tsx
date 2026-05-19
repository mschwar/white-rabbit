import { render, screen } from '@testing-library/react';
import { expect, test } from 'vitest';
import LoginPage from '../login/page';

test('renders the login form and next target', async () => {
  const element = await LoginPage({ searchParams: { next: '/scout' } });
  render(element);

  expect(screen.getByRole('heading', { name: /shared-password access/i })).toBeDefined();
  expect(screen.getByLabelText(/username/i)).toHaveValue('shared-workspace');
  expect(screen.getByLabelText(/password/i)).toBeDefined();
  expect(screen.getByRole('link', { name: /try the scout workspace after login/i })).toBeDefined();
});
