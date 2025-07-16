import { test, expect } from '@playwright/test';

test.describe('Navigation', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('http://localhost:3000');
  });

  test('should have working navigation menu', async ({ page }) => {
    // Check if navigation elements are present
    await expect(page.locator('nav')).toBeVisible();
    
    // Test navigation links (these might be hidden if not logged in)
    const navLinks = page.locator('nav a');
    await expect(navLinks).toHaveCount.greaterThan(0);
  });

  test('should navigate to applications page', async ({ page }) => {
    await page.click('text=Applications');
    await expect(page).toHaveURL(/.*applications/);
  });

  test('should navigate to analytics page', async ({ page }) => {
    await page.click('text=Analytics');
    await expect(page).toHaveURL(/.*analytics/);
  });

  test('should navigate to settings page', async ({ page }) => {
    await page.click('text=Settings');
    await expect(page).toHaveURL(/.*settings/);
  });

  test('should navigate to upload page', async ({ page }) => {
    await page.click('text=Upload');
    await expect(page).toHaveURL(/.*upload/);
  });

  test('should navigate to match page', async ({ page }) => {
    await page.click('text=Match');
    await expect(page).toHaveURL(/.*match/);
  });

  test('should have responsive navigation', async ({ page }) => {
    // Test mobile viewport
    await page.setViewportSize({ width: 375, height: 667 });
    
    // Check if mobile menu is accessible
    const mobileMenu = page.locator('button[aria-label="Menu"]');
    if (await mobileMenu.isVisible()) {
      await mobileMenu.click();
      await expect(page.locator('nav')).toBeVisible();
    }
  });
}); 