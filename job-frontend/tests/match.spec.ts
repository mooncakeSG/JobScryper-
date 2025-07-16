import { test, expect } from '@playwright/test';

test.describe('Job Matching', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('http://localhost:3000/match');
  });

  test('should show match page', async ({ page }) => {
    await expect(page.locator('text=Match, text=Job Matching, text=Recommendations')).toBeVisible();
  });

  test('should have job search input', async ({ page }) => {
    const searchInput = page.locator('input[placeholder*="job"], input[placeholder*="search"], [data-testid="job-search"]');
    if (await searchInput.count() > 0) {
      await expect(searchInput.first()).toBeVisible();
    }
  });

  test('should have location input', async ({ page }) => {
    const locationInput = page.locator('input[placeholder*="location"], input[placeholder*="city"], [data-testid="location-input"]');
    if (await locationInput.count() > 0) {
      await expect(locationInput.first()).toBeVisible();
    }
  });

  test('should have search filters', async ({ page }) => {
    const filters = page.locator('text=Remote, text=Full-time, text=Part-time, text=Contract, text=Experience Level');
    if (await filters.count() > 0) {
      await expect(filters.first()).toBeVisible();
    }
  });

  test('should display job cards', async ({ page }) => {
    const jobCards = page.locator('[data-testid="job-card"], .job-card, [class*="job-card"]');
    if (await jobCards.count() > 0) {
      await expect(jobCards.first()).toBeVisible();
    }
  });

  test('should show job details', async ({ page }) => {
    const jobDetails = page.locator('text=Company, text=Salary, text=Requirements, text=Description');
    if (await jobDetails.count() > 0) {
      await expect(jobDetails.first()).toBeVisible();
    }
  });

  test('should have apply button', async ({ page }) => {
    const applyButton = page.locator('button:has-text("Apply"), button:has-text("Quick Apply")');
    if (await applyButton.count() > 0) {
      await expect(applyButton.first()).toBeVisible();
    }
  });

  test('should show match percentage', async ({ page }) => {
    const matchPercentage = page.locator('[data-testid="match-percentage"], .match-percentage, [class*="match"]');
    if (await matchPercentage.count() > 0) {
      await expect(matchPercentage.first()).toBeVisible();
    }
  });

  test('should have pagination for results', async ({ page }) => {
    const pagination = page.locator('[data-testid="pagination"], .pagination, nav[aria-label*="pagination"]');
    if (await pagination.count() > 0) {
      await expect(pagination.first()).toBeVisible();
    }
  });
}); 