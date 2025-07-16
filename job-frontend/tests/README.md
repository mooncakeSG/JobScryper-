# Auto Applyer Frontend - Playwright Test Suite

This directory contains comprehensive end-to-end tests for the Auto Applyer frontend application using Playwright.

## Test Files Overview

### Core Tests
- **`example.spec.ts`** - Basic homepage and title verification
- **`auth.spec.ts`** - Authentication flows (login, signup, validation)
- **`navigation.spec.ts`** - Navigation menu and routing tests
- **`upload.spec.ts`** - Resume upload functionality
- **`applications.spec.ts`** - Job application tracking
- **`analytics.spec.ts`** - Dashboard and analytics features
- **`settings.spec.ts`** - User preferences and settings
- **`match.spec.ts`** - Job matching and recommendations

## Running Tests

### Quick Start
```bash
# Run all tests
npm run test

# Run tests with UI (interactive)
npm run test:ui

# Run tests in headed mode (see browser)
npm run test:headed

# Run tests in debug mode
npm run test:debug

# View test report
npm run test:report
```

### Running Specific Tests
```bash
# Run a specific test file
npx playwright test auth.spec.ts

# Run tests matching a pattern
npx playwright test --grep "login"

# Run tests in a specific browser
npx playwright test --project=chromium
```

### Test Configuration
- **Base URL**: `http://localhost:3000`
- **Browsers**: Chromium, Firefox, WebKit, Mobile Chrome, Mobile Safari
- **Retries**: 2 retries on CI, 0 locally
- **Screenshots**: On failure only
- **Videos**: Retained on failure
- **Traces**: On first retry

## Test Structure

Each test file follows this pattern:
```typescript
import { test, expect } from '@playwright/test';

test.describe('Feature Name', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/page-url');
  });

  test('should do something specific', async ({ page }) => {
    // Test implementation
    await expect(page.locator('selector')).toBeVisible();
  });
});
```

## Test Data

Tests are designed to work with:
- Empty database state
- Demo user accounts
- Sample job data
- Mock API responses

## Debugging Tests

### View Test Results
```bash
# Open HTML report
npm run test:report

# View test artifacts
ls .test-results/
```

### Debug Mode
```bash
# Run in debug mode with browser open
npm run test:debug
```

### Record New Tests
```bash
# Record interactions to create new tests
npx playwright codegen http://localhost:3000
```

## CI/CD Integration

The test suite is configured for CI/CD with:
- Parallel test execution
- Retry logic for flaky tests
- HTML report generation
- Screenshot and video capture on failure

## Troubleshooting

### Common Issues

1. **Frontend not running**
   ```bash
   # Start the frontend first
   npm run dev
   ```

2. **Database connection issues**
   - Check backend logs for SQLite Cloud errors
   - Verify environment variables are set

3. **Test timeouts**
   - Increase timeout in `playwright.config.ts`
   - Check for slow API responses

4. **Element not found**
   - Verify selectors match actual page elements
   - Check for dynamic content loading

### Getting Help
- Check Playwright documentation: https://playwright.dev/
- View test reports for detailed failure information
- Use debug mode to step through failing tests 