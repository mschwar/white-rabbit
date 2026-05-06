import { render, screen } from '@testing-library/react';
import { expect, test } from 'vitest';
import Page from '../page';

test('renders the protected workspace shell', () => {
  render(<Page />);

  expect(screen.getByRole('heading', { name: /scout workspace is gated/i })).toBeDefined();
  expect(screen.getByRole('link', { name: /open scout workspace/i })).toBeDefined();
});
