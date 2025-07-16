import { test, expect } from '@playwright/test';

test.describe('Authentication', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('http://localhost:3000');
  });

  test('should show login page when not authenticated', async ({ page }) => {
    await expect(page.locator('text=Please log in to view your dashboard')).toBeVisible();
  });

  test('should navigate to login page', async ({ page }) => {
    await page.click('text=Login');
    await expect(page).toHaveURL(/.*login/);
    await expect(page.locator('input[name="username"]')).toBeVisible();
    await expect(page.locator('input[name="password"]')).toBeVisible();
  });

  test('should navigate to signup page', async ({ page }) => {
    await page.click('text=Sign Up');
    await expect(page).toHaveURL(/.*signup/);
    await expect(page.locator('input[name="username"]')).toBeVisible();
    await expect(page.locator('input[name="email"]')).toBeVisible();
    await expect(page.locator('input[name="password"]')).toBeVisible();
  });

  test('should show validation errors for empty login form', async ({ page }) => {
    await page.click('text=Login');
    await page.click('button[type="submit"]');
    
    // Wait for validation errors
    await expect(page.locator('text=Username is required')).toBeVisible();
    await expect(page.locator('text=Password is required')).toBeVisible();
  });

  test('should show validation errors for empty signup form', async ({ page }) => {
    await page.click('text=Sign Up');
    await page.click('button[type="submit"]');
    
    // Wait for validation errors
    await expect(page.locator('text=Username is required')).toBeVisible();
    await expect(page.locator('text=Email is required')).toBeVisible();
    await expect(page.locator('text=Password is required')).toBeVisible();
  });
}); 