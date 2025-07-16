import { test, expect } from '@playwright/test';

test.describe('Authentication System', () => {
  test.beforeEach(async ({ page }) => {
    // Navigate to the app
    await page.goto('http://localhost:3000');
  });

  test.describe('Login Flow', () => {
    test('should display login page', async ({ page }) => {
      await page.goto('/auth/login');
      
      await expect(page.getByRole('heading', { name: 'Welcome back' })).toBeVisible();
      await expect(page.getByPlaceholder('Enter your username or email')).toBeVisible();
      await expect(page.getByPlaceholder('Enter your password')).toBeVisible();
      await expect(page.getByRole('button', { name: 'Sign in' })).toBeVisible();
    });

    test('should show validation errors for empty fields', async ({ page }) => {
      await page.goto('/auth/login');
      
      await page.getByRole('button', { name: 'Sign in' }).click();
      
      await expect(page.getByText('Username is required')).toBeVisible();
      await expect(page.getByText('Password is required')).toBeVisible();
    });

    test('should show validation error for invalid email', async ({ page }) => {
      await page.goto('/auth/login');
      
      await page.getByPlaceholder('Enter your username or email').fill('invalid-email');
      await page.getByPlaceholder('Enter your password').fill('password123');
      await page.getByRole('button', { name: 'Sign in' }).click();
      
      // Should not show email validation error since we accept username or email
      await expect(page.getByText('Username is required')).not.toBeVisible();
    });

    test('should toggle password visibility', async ({ page }) => {
      await page.goto('/auth/login');
      
      const passwordInput = page.getByPlaceholder('Enter your password');
      const toggleButton = page.locator('button[type="button"]').first();
      
      await passwordInput.fill('testpassword');
      await expect(passwordInput).toHaveAttribute('type', 'password');
      
      await toggleButton.click();
      await expect(passwordInput).toHaveAttribute('type', 'text');
      
      await toggleButton.click();
      await expect(passwordInput).toHaveAttribute('type', 'password');
    });

    test('should navigate to signup page', async ({ page }) => {
      await page.goto('/auth/login');
      
      await page.getByRole('link', { name: 'Sign up' }).click();
      await expect(page).toHaveURL('/auth/signup');
    });

    test('should navigate to forgot password page', async ({ page }) => {
      await page.goto('/auth/login');
      
      await page.getByRole('link', { name: 'Forgot password?' }).click();
      await expect(page).toHaveURL('/auth/forgot-password');
    });
  });

  test.describe('Signup Flow', () => {
    test('should display signup page', async ({ page }) => {
      await page.goto('/auth/signup');
      
      await expect(page.getByRole('heading', { name: 'Create your account' })).toBeVisible();
      await expect(page.getByPlaceholder('Choose a username')).toBeVisible();
      await expect(page.getByPlaceholder('Enter your email')).toBeVisible();
      await expect(page.getByPlaceholder('Create a strong password')).toBeVisible();
      await expect(page.getByPlaceholder('Confirm your password')).toBeVisible();
    });

    test('should show validation errors for invalid username', async ({ page }) => {
      await page.goto('/auth/signup');
      
      await page.getByPlaceholder('Choose a username').fill('ab');
      await page.getByPlaceholder('Enter your email').fill('test@example.com');
      await page.getByPlaceholder('Create a strong password').fill('Password123');
      await page.getByPlaceholder('Confirm your password').fill('Password123');
      await page.getByRole('button', { name: 'Create account' }).click();
      
      await expect(page.getByText('Username must be at least 3 characters')).toBeVisible();
    });

    test('should show validation errors for invalid email', async ({ page }) => {
      await page.goto('/auth/signup');
      
      await page.getByPlaceholder('Choose a username').fill('testuser');
      await page.getByPlaceholder('Enter your email').fill('invalid-email');
      await page.getByPlaceholder('Create a strong password').fill('Password123');
      await page.getByPlaceholder('Confirm your password').fill('Password123');
      await page.getByRole('button', { name: 'Create account' }).click();
      
      await expect(page.getByText('Please enter a valid email address')).toBeVisible();
    });

    test('should show validation errors for weak password', async ({ page }) => {
      await page.goto('/auth/signup');
      
      await page.getByPlaceholder('Choose a username').fill('testuser');
      await page.getByPlaceholder('Enter your email').fill('test@example.com');
      await page.getByPlaceholder('Create a strong password').fill('weak');
      await page.getByPlaceholder('Confirm your password').fill('weak');
      await page.getByRole('button', { name: 'Create account' }).click();
      
      await expect(page.getByText('Password must be at least 8 characters')).toBeVisible();
    });

    test('should show validation error for mismatched passwords', async ({ page }) => {
      await page.goto('/auth/signup');
      
      await page.getByPlaceholder('Choose a username').fill('testuser');
      await page.getByPlaceholder('Enter your email').fill('test@example.com');
      await page.getByPlaceholder('Create a strong password').fill('Password123');
      await page.getByPlaceholder('Confirm your password').fill('DifferentPassword123');
      await page.getByRole('button', { name: 'Create account' }).click();
      
      await expect(page.getByText("Passwords don't match")).toBeVisible();
    });

    test('should show password strength indicator', async ({ page }) => {
      await page.goto('/auth/signup');
      
      const passwordInput = page.getByPlaceholder('Create a strong password');
      
      // Weak password
      await passwordInput.fill('weak');
      await expect(page.getByText('Weak')).toBeVisible();
      
      // Strong password
      await passwordInput.fill('StrongPassword123!');
      await expect(page.getByText('Strong')).toBeVisible();
    });

    test('should show password requirements checklist', async ({ page }) => {
      await page.goto('/auth/signup');
      
      const passwordInput = page.getByPlaceholder('Create a strong password');
      
      // Initially all requirements should be gray
      await expect(page.getByText('8+ characters')).toHaveClass(/text-gray-400/);
      await expect(page.getByText('Uppercase')).toHaveClass(/text-gray-400/);
      await expect(page.getByText('Lowercase')).toHaveClass(/text-gray-400/);
      await expect(page.getByText('Number')).toHaveClass(/text-gray-400/);
      
      // Fill with strong password
      await passwordInput.fill('StrongPassword123');
      
      // All requirements should be green
      await expect(page.getByText('8+ characters')).toHaveClass(/text-green-600/);
      await expect(page.getByText('Uppercase')).toHaveClass(/text-green-600/);
      await expect(page.getByText('Lowercase')).toHaveClass(/text-green-600/);
      await expect(page.getByText('Number')).toHaveClass(/text-green-600/);
    });

    test('should navigate to login page', async ({ page }) => {
      await page.goto('/auth/signup');
      
      await page.getByRole('link', { name: 'Sign in' }).click();
      await expect(page).toHaveURL('/auth/login');
    });
  });

  test.describe('Forgot Password Flow', () => {
    test('should display forgot password page', async ({ page }) => {
      await page.goto('/auth/forgot-password');
      
      await expect(page.getByRole('heading', { name: 'Forgot your password?' })).toBeVisible();
      await expect(page.getByPlaceholder('Enter your email')).toBeVisible();
      await expect(page.getByRole('button', { name: 'Send reset link' })).toBeVisible();
    });

    test('should show validation error for invalid email', async ({ page }) => {
      await page.goto('/auth/forgot-password');
      
      await page.getByPlaceholder('Enter your email').fill('invalid-email');
      await page.getByRole('button', { name: 'Send reset link' }).click();
      
      await expect(page.getByText('Please enter a valid email address')).toBeVisible();
    });

    test('should show success message after submitting', async ({ page }) => {
      await page.goto('/auth/forgot-password');
      
      await page.getByPlaceholder('Enter your email').fill('test@example.com');
      await page.getByRole('button', { name: 'Send reset link' }).click();
      
      await expect(page.getByRole('heading', { name: 'Check your email' })).toBeVisible();
      await expect(page.getByText('We\'ve sent a password reset link to your email address')).toBeVisible();
    });

    test('should navigate back to login', async ({ page }) => {
      await page.goto('/auth/forgot-password');
      
      await page.getByRole('link', { name: 'Back to login' }).click();
      await expect(page).toHaveURL('/auth/login');
    });
  });

  test.describe('Social Login', () => {
    test('should display social login buttons', async ({ page }) => {
      await page.goto('/auth/login');
      
      await expect(page.getByRole('button', { name: 'Continue with Google' })).toBeVisible();
      await expect(page.getByRole('button', { name: 'Continue with GitHub' })).toBeVisible();
    });

    test('should show coming soon message for social login', async ({ page }) => {
      await page.goto('/auth/login');
      
      await page.getByRole('button', { name: 'Continue with Google' }).click();
      
      // Should show toast notification
      await expect(page.getByText('Coming Soon')).toBeVisible();
      await expect(page.getByText('Google login will be available soon!')).toBeVisible();
    });
  });

  test.describe('Mobile Responsiveness', () => {
    test('should be responsive on mobile devices', async ({ page }) => {
      await page.setViewportSize({ width: 375, height: 667 });
      await page.goto('/auth/login');
      
      // Check that all elements are visible and properly sized
      await expect(page.getByRole('heading', { name: 'Welcome back' })).toBeVisible();
      await expect(page.getByPlaceholder('Enter your username or email')).toBeVisible();
      await expect(page.getByPlaceholder('Enter your password')).toBeVisible();
      await expect(page.getByRole('button', { name: 'Sign in' })).toBeVisible();
      
      // Check that the card doesn't overflow
      const card = page.locator('div[class*="Card"]').first();
      const cardBox = await card.boundingBox();
      expect(cardBox?.width).toBeLessThanOrEqual(375);
    });
  });
}); 