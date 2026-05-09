import { render, screen } from '@testing-library/react';
import { expect, test } from 'vitest';
import Page from '../page';

test('renders the protected workspace shell', () => {
  render(<Page />);

  expect(screen.getByRole('heading', { name: /source-backed lead search/i })).toBeDefined();
  expect(screen.getByRole('link', { name: /open lead search/i })).toHaveAttribute('href', '/scout');
  expect(screen.getAllByRole('link')).toHaveLength(1);
  expect(screen.queryByRole('link', { name: /recipe/i })).toBeNull();
  expect(screen.queryByRole('link', { name: /bulk|batch/i })).toBeNull();
});
