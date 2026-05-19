import { test, expect } from '@playwright/test';

test('redirects unauthenticated visitors to the shared-password gate', async ({ page }) => {
  const response = await page.goto('/');
  expect(response?.status()).toBe(200);
  expect(page.url()).toContain('/login?next=%2F');
  await expect(page.getByRole('heading', { name: /shared-password access/i })).toBeVisible();
});
