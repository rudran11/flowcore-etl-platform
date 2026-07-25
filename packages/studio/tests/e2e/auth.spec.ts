import { test, expect } from '@playwright/test';

test.describe('Authentication & Workspace Flow', () => {
  test.beforeEach(async ({ page }) => {
    // Navigate to the app (Playwright config should set baseURL)
    await page.goto('/login');
  });

  test('should login successfully with valid credentials', async ({ page }) => {
    // Fill login form
    await page.fill('input[type="text"]', 'admin');
    await page.fill('input[type="password"]', 'admin');
    await page.click('button[type="submit"]');

    // Wait for navigation to dashboard
    await expect(page).toHaveURL('/dashboard');
    
    // Verify successful login UI elements
    await expect(page.locator('text=FlowCore Dashboard')).toBeVisible();
  });

  test('should show error with invalid credentials', async ({ page }) => {
    await page.fill('input[type="text"]', 'wrong');
    await page.fill('input[type="password"]', 'wrong');
    await page.click('button[type="submit"]');

    // Verify error message
    await expect(page.locator('text=Invalid credentials')).toBeVisible();
    await expect(page).toHaveURL('/login');
  });

  test('should handle missing workspace gracefully (Error Boundary redirect)', async ({ page }) => {
    // Login first
    await page.fill('input[type="text"]', 'admin');
    await page.fill('input[type="password"]', 'admin');
    await page.click('button[type="submit"]');
    await expect(page).toHaveURL('/dashboard');

    // Clear workspace from local storage to simulate 422
    await page.evaluate(() => {
      const state = JSON.parse(localStorage.getItem('auth-storage') || '{}');
      state.state.activeWorkspaceId = null;
      localStorage.setItem('auth-storage', JSON.stringify(state));
    });

    // Navigate to datasets page, which should trigger a 422 if workspace is missing
    await page.goto('/datasets');

    // Expect the ErrorBoundary to catch it and show "Workspace Required"
    await expect(page.locator('text=Workspace Required')).toBeVisible();
    
    // Click Go Home
    await page.click('button:has-text("Go Home")');
    await expect(page).toHaveURL('/dashboard');
  });
});
