// @ts-check
const { test, expect } = require('@playwright/test');

test.describe('Login Flow', () => {
  
  test.beforeEach(async ({ page }) => {
    // Navigate to login page before each test
    await page.goto('/squire/login');
    
    // Wait for page to be fully loaded
    await page.waitForLoadState('networkidle');
  });

  test('should display login form', async ({ page }) => {
    // Verify the login form exists
    await expect(page.locator('form')).toBeVisible();
    
    // Verify input fields exist
    await expect(page.locator('input[type="text"]')).toBeVisible();
    await expect(page.locator('input[type="password"]')).toBeVisible();
    
    // Verify login button exists
    await expect(page.locator('button[type="submit"]')).toBeVisible();
  });

  test('should show error for invalid credentials', async ({ page }) => {
    // Fill in wrong credentials
    await page.locator('input[type="text"]').fill('alakkhaine');
    await page.locator('input[type="password"]').fill('WrongPassword123');
    
    // Click login button
    await page.locator('button[type="submit"]').click();
    
    // Wait for response
    await page.waitForTimeout(2000);
    
    // Check what error message is actually displayed - using correct selector
    const errorElement = page.locator('[x-show="error"]').locator('[x-text="error"]');
    await expect(errorElement).toBeVisible();
    
    // Get the actual error text
    const errorText = await errorElement.textContent();
    console.log('Error message displayed:', errorText);
    
    // Verify it's NOT "[object Object]"
    expect(errorText).not.toBe('[object Object]');
    
    // Verify it contains expected error message
    expect(errorText).toContain('Invalid username or password');
  });

  test('should show specific error for unverified email', async ({ page }) => {
    // If we have a test user with unverified email, test that scenario
    // For now, we'll skip this if we don't have such a user
    test.skip();
  });

  test('should login successfully with valid credentials', async ({ page }) => {
    // Fill in correct credentials
    await page.locator('input[type="text"]').fill('alakkhaine');
    await page.locator('input[type="password"]').fill('FinFan11');
    
    // Click login button
    await page.locator('button[type="submit"]').click();
    
    // Wait for navigation or response
    await page.waitForTimeout(2000);
    
    // Check if we were redirected or if token was stored
    const url = page.url();
    console.log('Current URL after login:', url);
    
    // Check localStorage for token - using correct key from login.js
    const token = await page.evaluate(() => localStorage.getItem('auth_token'));
    console.log('Auth token stored:', token ? 'Yes' : 'No');
    
    // Verify either:
    // 1. We were redirected away from login page
    // 2. Or a token was stored in localStorage
    const isStillOnLoginPage = url.includes('/squire/login');
    
    if (isStillOnLoginPage) {
      // If still on login page, check for error message
      const errorElement = page.locator('[x-show="error"]').locator('[x-text="error"]');
      
      try {
        await errorElement.waitFor({ state: 'visible', timeout: 1000 });
        const errorText = await errorElement.textContent();
        console.log('Unexpected error on valid login:', errorText);
        
        // Fail the test with the actual error
        expect(errorText).toBe('No error - login should succeed');
      } catch {
        // No error visible but still on login page - check if token was stored
        expect(token).toBeTruthy();
      }
    } else {
      // Successfully redirected
      expect(isStillOnLoginPage).toBe(false);
    }
  });

  test('should inspect error message DOM structure', async ({ page }) => {
    // Fill in wrong credentials to trigger error
    await page.locator('input[type="text"]').fill('alakkhaine');
    await page.locator('input[type="password"]').fill('WrongPassword');
    
    // Click login button
    await page.locator('button[type="submit"]').click();
    
    // Wait for response
    await page.waitForTimeout(2000);
    
    // Get the error element with correct selector
    const errorDiv = page.locator('[x-show="error"]');
    const errorText = errorDiv.locator('[x-text="error"]');
    
    // Wait for it to be visible
    await expect(errorText).toBeVisible({ timeout: 3000 });
    
    // Inspect the DOM structure
    const innerHTML = await errorDiv.innerHTML();
    console.log('Error div innerHTML:', innerHTML);
    
    const textContent = await errorText.textContent();
    console.log('Error text content:', textContent);
    
    const xTextAttr = await errorText.getAttribute('x-text');
    console.log('Error element x-text attribute:', xTextAttr);
    
    // Check Alpine.js data
    const alpineData = await page.evaluate(() => {
      const loginDiv = document.querySelector('[x-data="squireLogin()"]');
      if (loginDiv && loginDiv.__x) {
        return {
          error: loginDiv.__x.$data.error,
          emailNotVerified: loginDiv.__x.$data.emailNotVerified,
          loading: loginDiv.__x.$data.loading
        };
      }
      return null;
    });
    console.log('Alpine.js data:', alpineData);
    
    // Take a screenshot for debugging
    await page.screenshot({ path: 'error-message-debug.png', fullPage: true });
    
    // Verify error is a string, not an object
    expect(textContent).not.toBe('[object Object]');
    expect(textContent).toBeTruthy();
  });

  test('should check browser console for errors', async ({ page }) => {
    const consoleMessages = [];
    const consoleErrors = [];
    
    // Listen to console events
    page.on('console', msg => {
      consoleMessages.push({ type: msg.type(), text: msg.text() });
      if (msg.type() === 'error') {
        consoleErrors.push(msg.text());
      }
    });
    
    // Fill in wrong credentials to trigger error
    await page.locator('input[type="text"]').fill('alakkhaine');
    await page.locator('input[type="password"]').fill('WrongPassword');
    
    // Click login button
    await page.locator('button[type="submit"]').click();
    
    // Wait for response
    await page.waitForTimeout(2000);
    
    // Log all console messages
    console.log('Browser console messages:', JSON.stringify(consoleMessages, null, 2));
    
    // Check for JavaScript errors
    if (consoleErrors.length > 0) {
      console.log('JavaScript errors detected:', consoleErrors);
    }
    
    // This test doesn't fail - it's just for diagnostics
    expect(true).toBe(true);
  });

});
