import { render, screen } from '@testing-library/react';
import { expect, test } from 'vitest';
import Page from '../page';

test('renders the primary lead-search workspace', () => {
  render(<Page />);

  expect(screen.getByRole('heading', { name: /start with the target/i })).toBeDefined();
  expect(screen.getByLabelText(/target/i)).toBeDefined();
  expect(screen.getByRole('button', { name: /find candidates/i })).toBeDefined();
  expect(screen.getAllByRole('textbox')).toHaveLength(1);
  expect(screen.queryByRole('button', { name: /^scout$/i })).toBeNull();
  expect(screen.queryByRole('button', { name: /^full$/i })).toBeNull();
  expect(screen.queryByText(/search usage/i)).toBeNull();
  expect(screen.queryByRole('link', { name: /open lead search/i })).toBeNull();
  expect(screen.queryByRole('link', { name: /recipe/i })).toBeNull();
  expect(screen.queryByRole('link', { name: /bulk|batch/i })).toBeNull();
});
