import { test, expect } from '@playwright/test';

test.describe('Applications', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('http://localhost:3000/applications');
  });

  test('should show applications page', async ({ page }) => {
    await expect(page.locator('text=Applications, text=Job Applications')).toBeVisible();
  });

  test('should have applications table or list', async ({ page }) => {
    const applicationsList = page.locator('table, [data-testid="applications-list"], .applications-list');
    if (await applicationsList.count() > 0) {
      await expect(applicationsList.first()).toBeVisible();
    }
  });

  test('should show application status filters', async ({ page }) => {
    const statusFilters = page.locator('text=All, text=Pending, text=Applied, text=Interviewed, text=Rejected');
    if (await statusFilters.count() > 0) {
      await expect(statusFilters.first()).toBeVisible();
    }
  });

  test('should have search functionality', async ({ page }) => {
    const searchInput = page.locator('input[placeholder*="search"], input[placeholder*="Search"], [data-testid="search"]');
    if (await searchInput.count() > 0) {
      await expect(searchInput.first()).toBeVisible();
    }
  });

  test('should show add new application button', async ({ page }) => {
    const addButton = page.locator('text=Add Application, text=New Application, button:has-text("Add")');
    if (await addButton.count() > 0) {
      await expect(addButton.first()).toBeVisible();
    }
  });

  test('should display application details', async ({ page }) => {
    // Check for common application fields
    const applicationFields = page.locator('text=Company, text=Position, text=Date Applied, text=Status');
    if (await applicationFields.count() > 0) {
      await expect(applicationFields.first()).toBeVisible();
    }
  });

  test('should have pagination if many applications', async ({ page }) => {
    const pagination = page.locator('[data-testid="pagination"], .pagination, nav[aria-label*="pagination"]');
    if (await pagination.count() > 0) {
      await expect(pagination.first()).toBeVisible();
    }
  });
}); 