// @ts-check
const { test, expect } = require('@playwright/test');

test.describe('User Profile & Navigation', () => {
  
  test.beforeEach(async ({ page }) => {
    // Navigate to home page
    await page.goto('/');
    await page.waitForLoadState('networkidle');
  });

  test('should show login/register links when not logged in', async ({ page }) => {
    // Check that login and register links are visible
    const loginLink = page.locator('a[href="/squire/login"]').filter({ hasText: 'Login' });
    const registerLink = page.locator('a[href="/squire/register"]').filter({ hasText: 'Register' });
    
    await expect(loginLink).toBeVisible();
    await expect(registerLink).toBeVisible();
    
    // User menu should not be visible
    const userMenu = page.locator('[x-show="isLoggedIn"]');
    await expect(userMenu).not.toBeVisible();
  });

  test('should show user menu after login', async ({ page }) => {
    // Go to login page
    await page.goto('/squire/login');
    await page.waitForLoadState('networkidle');
    
    // Login with valid credentials
    await page.locator('input[type="text"]').fill('alakkhaine');
    await page.locator('input[type="password"]').fill('FinFan11');
    await page.locator('button[type="submit"]').click();
    
    // Wait for redirect and auth check
    await page.waitForTimeout(2000);
    
    // Check that user menu is visible by finding the user icon button
    const userMenuButton = page.locator('[x-show="isLoggedIn"] button').first();
    await expect(userMenuButton).toBeVisible();
    
    // Get username text - wait for it to populate
    await page.waitForTimeout(1000);
    const username = await page.locator('[x-show="isLoggedIn"] span.font-semibold').first().textContent();
    console.log('Logged in as:', username);
    
    expect(username).toBe('alakkhaine');
    
    // Login/Register links should not be visible
    const loginLinks = page.locator('[x-show="!isLoggedIn"]');
    await expect(loginLinks).not.toBeVisible();
  });

  test('should navigate to profile page', async ({ page }) => {
    // Login first
    await page.goto('/squire/login');
    await page.locator('input[type="text"]').fill('alakkhaine');
    await page.locator('input[type="password"]').fill('FinFan11');
    await page.locator('button[type="submit"]').click();
    await page.waitForTimeout(2000);
    
    // Open user menu - click the first button (the dropdown trigger)
    await page.locator('[x-show="isLoggedIn"] button').first().click();
    await page.waitForTimeout(500);
    
    // Click profile link
    await page.locator('a[href="/squire/profile"]').click();
    await page.waitForTimeout(1000);
    
    // Verify we're on the profile page
    await expect(page.locator('h1')).toContainText('User Profile');
    
    // Check that profile data loads - look for Account Information heading
    const profileHeading = page.locator('h2:has-text("Account Information")');
    await expect(profileHeading).toBeVisible();
    // Look for username text directly
    const username = page.locator('p.font-semibold:has-text("alakkhaine")');
    await expect(username).toBeVisible();
  });

  test('should navigate to matchup history', async ({ page }) => {
    // Login first
    await page.goto('/squire/login');
    await page.locator('input[type="text"]').fill('alakkhaine');
    await page.locator('input[type="password"]').fill('FinFan11');
    await page.locator('button[type="submit"]').click();
    await page.waitForTimeout(2000);
    
    // Open user menu
    await page.locator('[x-show="isLoggedIn"] button').first().click();
    await page.waitForTimeout(500);
    
    // Click history link
    await page.locator('a[href="/squire/history"]').click();
    await page.waitForTimeout(1000);
    
    // Verify we're on the history page
    await expect(page.locator('h1')).toContainText('Matchup History');
  });

  test('should navigate to settings', async ({ page }) => {
    // Login first
    await page.goto('/squire/login');
    await page.locator('input[type="text"]').fill('alakkhaine');
    await page.locator('input[type="password"]').fill('FinFan11');
    await page.locator('button[type="submit"]').click();
    await page.waitForTimeout(2000);
    
    // Open user menu
    await page.locator('[x-show="isLoggedIn"] button').first().click();
    await page.waitForTimeout(500);
    
    // Click settings link
    await page.locator('a[href="/squire/settings"]').click();
    await page.waitForTimeout(1000);
    
    // Verify we're on the settings page
    await expect(page.locator('h1')).toContainText('Account Settings');
  });

  test('should logout successfully', async ({ page }) => {
    // Login first
    await page.goto('/squire/login');
    await page.locator('input[type="text"]').fill('alakkhaine');
    await page.locator('input[type="password"]').fill('FinFan11');
    await page.locator('button[type="submit"]').click();
    await page.waitForTimeout(2000);
    
    // Open user menu
    await page.locator('[x-show="isLoggedIn"] button').first().click();
    await page.waitForTimeout(500);
    
    // Click logout
    await page.locator('button:has-text("Logout")').click();
    await page.waitForTimeout(1000);
    
    // Should be redirected to home
    expect(page.url()).toContain('/');
    
    // Login/Register links should be visible again
    const loginLink = page.locator('a[href="/squire/login"]').filter({ hasText: 'Login' });
    await expect(loginLink).toBeVisible();
    
    // User menu should not be visible
    const userMenu = page.locator('[x-show="isLoggedIn"]');
    await expect(userMenu).not.toBeVisible();
  });
});
