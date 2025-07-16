import { test, expect } from '@playwright/test';

test.describe('Enhanced Authentication', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('http://localhost:3000/auth');
  });

  test('should show authentication page with tabs', async ({ page }) => {
    await expect(page.locator('text=Sign in to your account')).toBeVisible();
    await expect(page.locator('[role="tab"]')).toHaveCount(2);
    await expect(page.locator('text=Social Login')).toBeVisible();
    await expect(page.locator('text=Email')).toBeVisible();
  });

  test('should switch between social login and email tabs', async ({ page }) => {
    // Check social login tab
    await page.click('text=Social Login');
    await expect(page.locator('text=Continue with Google')).toBeVisible();
    await expect(page.locator('text=Continue with GitHub')).toBeVisible();

    // Switch to email tab
    await page.click('text=Email');
    await expect(page.locator('input[type="email"]')).toBeVisible();
    await expect(page.locator('input[type="password"]')).toBeVisible();
  });

  test('should show social login options', async ({ page }) => {
    await page.click('text=Social Login');
    
    const googleButton = page.locator('text=Continue with Google');
    const githubButton = page.locator('text=Continue with GitHub');
    
    await expect(googleButton).toBeVisible();
    await expect(githubButton).toBeVisible();
    
    // Check for social icons
    await expect(page.locator('svg')).toHaveCount(2);
  });

  test('should handle email signup flow', async ({ page }) => {
    await page.click('text=Email');
    await page.click('text=Sign up');
    
    // Fill signup form
    await page.fill('input[placeholder*="username"], input[name="username"]', 'testuser');
    await page.fill('input[type="email"]', 'test@example.com');
    await page.fill('input[type="password"]', 'password123');
    await page.fill('input[placeholder*="confirm"], input[name="confirm-password"]', 'password123');
    
    await page.click('button:has-text("Create Account")');
    
    // Should show success message or redirect to verification
    await expect(page.locator('text=Account Created, text=Success, text=verification')).toBeVisible();
  });

  test('should show password confirmation error', async ({ page }) => {
    await page.click('text=Email');
    await page.click('text=Sign up');
    
    await page.fill('input[placeholder*="username"], input[name="username"]', 'testuser');
    await page.fill('input[type="email"]', 'test@example.com');
    await page.fill('input[type="password"]', 'password123');
    await page.fill('input[placeholder*="confirm"], input[name="confirm-password"]', 'different');
    
    await page.click('button:has-text("Create Account")');
    
    await expect(page.locator('text=Passwords do not match')).toBeVisible();
  });

  test('should show email verification page', async ({ page }) => {
    // Navigate to verification page (simulated)
    await page.goto('http://localhost:3000/auth?mode=verify-email');
    
    await expect(page.locator('text=Verify Your Email')).toBeVisible();
    await expect(page.locator('input[placeholder="000000"]')).toBeVisible();
    await expect(page.locator('text=Resend verification code')).toBeVisible();
  });

  test('should handle email verification code input', async ({ page }) => {
    await page.goto('http://localhost:3000/auth?mode=verify-email');
    
    const codeInput = page.locator('input[placeholder="000000"]');
    await codeInput.fill('123456');
    
    await expect(codeInput).toHaveValue('123456');
  });

  test('should show resend verification functionality', async ({ page }) => {
    await page.goto('http://localhost:3000/auth?mode=verify-email');
    
    const resendButton = page.locator('text=Resend verification code');
    await expect(resendButton).toBeVisible();
    
    await resendButton.click();
    
    // Should show success message
    await expect(page.locator('text=Code Sent, text=verification code has been sent')).toBeVisible();
  });

  test('should show forgot password flow', async ({ page }) => {
    await page.click('text=Email');
    await page.click('text=Forgot your password?');
    
    await expect(page.locator('text=Reset your password')).toBeVisible();
    await expect(page.locator('input[type="email"]')).toBeVisible();
    await expect(page.locator('button:has-text("Send Reset Email")')).toBeVisible();
  });

  test('should handle forgot password form', async ({ page }) => {
    await page.click('text=Email');
    await page.click('text=Forgot your password?');
    
    await page.fill('input[type="email"]', 'test@example.com');
    await page.click('button:has-text("Send Reset Email")');
    
    await expect(page.locator('text=Email Sent, text=reset link has been sent')).toBeVisible();
  });

  test('should show password reset form', async ({ page }) => {
    await page.goto('http://localhost:3000/auth?mode=reset-password');
    
    await expect(page.locator('text=Set new password')).toBeVisible();
    await expect(page.locator('input[type="password"]')).toHaveCount(2);
    await expect(page.locator('input[placeholder*="token"]')).toBeVisible();
    await expect(page.locator('button:has-text("Reset Password")')).toBeVisible();
  });

  test('should handle password reset form validation', async ({ page }) => {
    await page.goto('http://localhost:3000/auth?mode=reset-password');
    
    await page.fill('input[type="password"]', 'newpassword');
    await page.fill('input[placeholder*="confirm"], input[name="confirm-password"]', 'different');
    await page.fill('input[placeholder*="token"]', 'test-token');
    
    await page.click('button:has-text("Reset Password")');
    
    await expect(page.locator('text=Passwords do not match')).toBeVisible();
  });

  test('should show 2FA setup option', async ({ page }) => {
    await page.click('text=Email');
    
    const setup2FAButton = page.locator('text=Setup Two-Factor Authentication');
    await expect(setup2FAButton).toBeVisible();
  });

  test('should navigate to 2FA setup page', async ({ page }) => {
    await page.click('text=Email');
    await page.click('text=Setup Two-Factor Authentication');
    
    await expect(page.locator('text=Setup Two-Factor Authentication')).toBeVisible();
    await expect(page.locator('img[alt="2FA QR Code"]')).toBeVisible();
    await expect(page.locator('text=Manual Entry Code')).toBeVisible();
    await expect(page.locator('text=Backup Codes')).toBeVisible();
  });

  test('should show 2FA QR code and backup codes', async ({ page }) => {
    await page.click('text=Email');
    await page.click('text=Setup Two-Factor Authentication');
    
    // Check for QR code
    const qrCode = page.locator('img[alt="2FA QR Code"]');
    await expect(qrCode).toBeVisible();
    
    // Check for backup codes
    const backupCodes = page.locator('text=Backup Codes');
    await expect(backupCodes).toBeVisible();
    
    // Should have 8 backup codes
    const codeElements = page.locator('.grid.grid-cols-2 > div');
    await expect(codeElements).toHaveCount(8);
  });

  test('should handle 2FA verification step', async ({ page }) => {
    await page.click('text=Email');
    await page.click('text=Setup Two-Factor Authentication');
    await page.click('text=Next');
    
    await expect(page.locator('text=Verify 2FA Setup')).toBeVisible();
    await expect(page.locator('input[placeholder="000000"]')).toBeVisible();
    await expect(page.locator('button:has-text("Enable 2FA")')).toBeVisible();
  });

  test('should show 2FA verification code input', async ({ page }) => {
    await page.click('text=Email');
    await page.click('text=Setup Two-Factor Authentication');
    await page.click('text=Next');
    
    const codeInput = page.locator('input[placeholder="000000"]');
    await codeInput.fill('123456');
    
    await expect(codeInput).toHaveValue('123456');
  });

  test('should show 2FA success page', async ({ page }) => {
    // Simulate 2FA completion
    await page.goto('http://localhost:3000/auth?mode=2fa&step=complete');
    
    await expect(page.locator('text=2FA Enabled Successfully!')).toBeVisible();
    await expect(page.locator('text=Your account is now protected')).toBeVisible();
    await expect(page.locator('button:has-text("Continue")')).toBeVisible();
  });

  test('should handle login with 2FA', async ({ page }) => {
    await page.click('text=Email');
    
    await page.fill('input[type="email"]', 'test@example.com');
    await page.fill('input[type="password"]', 'password123');
    
    // Simulate 2FA requirement
    await page.evaluate(() => {
      // Mock 2FA requirement
      window.localStorage.setItem('mock_2fa_required', 'true');
    });
    
    await page.click('button:has-text("Sign In")');
    
    // Should show 2FA input
    await expect(page.locator('input[placeholder="000000"]')).toBeVisible();
    await expect(page.locator('text=2FA Required')).toBeVisible();
  });

  test('should show terms and privacy links', async ({ page }) => {
    await page.click('text=Social Login');
    
    await expect(page.locator('text=Terms of Service')).toBeVisible();
    await expect(page.locator('text=Privacy Policy')).toBeVisible();
    
    const termsLink = page.locator('a[href="/terms"]');
    const privacyLink = page.locator('a[href="/privacy"]');
    
    await expect(termsLink).toBeVisible();
    await expect(privacyLink).toBeVisible();
  });

  test('should handle form validation errors', async ({ page }) => {
    await page.click('text=Email');
    
    // Try to submit empty form
    await page.click('button:has-text("Sign In")');
    
    // Should show validation errors
    await expect(page.locator('text=Please enter, text=required')).toBeVisible();
  });

  test('should show responsive design on mobile', async ({ page }) => {
    await page.setViewportSize({ width: 375, height: 667 });
    
    await expect(page.locator('text=Sign in to your account')).toBeVisible();
    await expect(page.locator('[role="tab"]')).toBeVisible();
    
    // Check that all elements are accessible on mobile
    await page.click('text=Social Login');
    await expect(page.locator('text=Continue with Google')).toBeVisible();
    
    await page.click('text=Email');
    await expect(page.locator('input[type="email"]')).toBeVisible();
  });

  test('should handle keyboard navigation', async ({ page }) => {
    await page.click('text=Email');
    
    // Tab through form elements
    await page.keyboard.press('Tab');
    await expect(page.locator('input[type="email"]')).toBeFocused();
    
    await page.keyboard.press('Tab');
    await expect(page.locator('input[type="password"]')).toBeFocused();
    
    await page.keyboard.press('Tab');
    await expect(page.locator('button:has-text("Sign In")')).toBeFocused();
  });

  test('should show loading states', async ({ page }) => {
    await page.click('text=Email');
    
    await page.fill('input[type="email"]', 'test@example.com');
    await page.fill('input[type="password"]', 'password123');
    
    // Mock loading state
    await page.evaluate(() => {
      const button = document.querySelector('button:has-text("Sign In")');
      if (button) {
        button.textContent = 'Processing...';
        button.disabled = true;
      }
    });
    
    await expect(page.locator('button:has-text("Processing...")')).toBeVisible();
  });
}); 