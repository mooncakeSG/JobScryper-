import { test, expect } from '@playwright/test';

test('homepage loads and displays title', async ({ page }) => {
  await page.goto('http://localhost:3000');
  await expect(page).toHaveTitle(/JobScryper/i);
}); 