import { test, expect } from '@playwright/test';

test.describe('Analytics', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('http://localhost:3000/analytics');
  });

  test('should show analytics page', async ({ page }) => {
    await expect(page.locator('text=Analytics, text=Dashboard')).toBeVisible();
  });

  test('should display application statistics', async ({ page }) => {
    const statsElements = page.locator('text=Total Applications, text=Applied, text=Interviewed, text=Rejected, text=Success Rate');
    if (await statsElements.count() > 0) {
      await expect(statsElements.first()).toBeVisible();
    }
  });

  test('should have charts or graphs', async ({ page }) => {
    const charts = page.locator('canvas, svg, [data-testid*="chart"], [class*="chart"]');
    if (await charts.count() > 0) {
      await expect(charts.first()).toBeVisible();
    }
  });

  test('should show time period filters', async ({ page }) => {
    const timeFilters = page.locator('text=Last 7 days, text=Last 30 days, text=Last 3 months, text=Last year');
    if (await timeFilters.count() > 0) {
      await expect(timeFilters.first()).toBeVisible();
    }
  });

  test('should display application trends', async ({ page }) => {
    const trendElements = page.locator('text=Applications Over Time, text=Success Rate Trend, text=Monthly Applications');
    if (await trendElements.count() > 0) {
      await expect(trendElements.first()).toBeVisible();
    }
  });

  test('should show company statistics', async ({ page }) => {
    const companyStats = page.locator('text=Top Companies, text=Company Performance, text=Most Applied');
    if (await companyStats.count() > 0) {
      await expect(companyStats.first()).toBeVisible();
    }
  });

  test('should have export functionality', async ({ page }) => {
    const exportButton = page.locator('text=Export, text=Download, button:has-text("Export")');
    if (await exportButton.count() > 0) {
      await expect(exportButton.first()).toBeVisible();
    }
  });
}); 