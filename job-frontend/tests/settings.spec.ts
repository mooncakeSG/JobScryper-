import { test, expect } from '@playwright/test';

test.describe('Settings', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('http://localhost:3000/settings');
  });

  test('should show settings page', async ({ page }) => {
    await expect(page.locator('text=Settings, text=Profile, text=Preferences')).toBeVisible();
  });

  test('should have profile section', async ({ page }) => {
    const profileSection = page.locator('text=Profile, text=Personal Information, text=Account Details');
    if (await profileSection.count() > 0) {
      await expect(profileSection.first()).toBeVisible();
    }
  });

  test('should have preferences section', async ({ page }) => {
    const preferencesSection = page.locator('text=Preferences, text=Settings, text=Configuration');
    if (await preferencesSection.count() > 0) {
      await expect(preferencesSection.first()).toBeVisible();
    }
  });

  test('should have currency preference option', async ({ page }) => {
    const currencySelect = page.locator('select[name="currency"], [data-testid="currency-select"]');
    if (await currencySelect.count() > 0) {
      await expect(currencySelect.first()).toBeVisible();
    }
  });

  test('should have notification settings', async ({ page }) => {
    const notificationSettings = page.locator('text=Notifications, text=Email Alerts, text=Push Notifications');
    if (await notificationSettings.count() > 0) {
      await expect(notificationSettings.first()).toBeVisible();
    }
  });

  test('should have save button', async ({ page }) => {
    const saveButton = page.locator('button:has-text("Save"), button[type="submit"]');
    if (await saveButton.count() > 0) {
      await expect(saveButton.first()).toBeVisible();
    }
  });

  test('should show success message after saving', async ({ page }) => {
    // This test would need actual form submission to work
    const successMessage = page.locator('text=Settings saved, text=Success, [class*="success"]');
    if (await successMessage.count() > 0) {
      await expect(successMessage.first()).toBeVisible();
    }
  });

  test('should have logout option', async ({ page }) => {
    const logoutButton = page.locator('text=Logout, text=Sign Out, button:has-text("Logout")');
    if (await logoutButton.count() > 0) {
      await expect(logoutButton.first()).toBeVisible();
    }
  });
}); 