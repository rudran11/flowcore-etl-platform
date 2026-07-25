import { test, expect } from '@playwright/test';

test.describe('Data Lineage & Catalog Flow', () => {
  // Login before all tests
  test.beforeEach(async ({ page }) => {
    await page.goto('/login');
    await page.fill('input[type="text"]', 'admin');
    await page.fill('input[type="password"]', 'admin');
    await page.click('button[type="submit"]');
    await expect(page).toHaveURL('/dashboard');
    
    // Select workspace if necessary
    const workspaceSelected = await page.evaluate(() => {
      const state = JSON.parse(localStorage.getItem('auth-storage') || '{}');
      return !!state?.state?.activeWorkspaceId;
    });

    if (!workspaceSelected) {
        // Just click the first workspace in the grid if available
        await page.click('div.grid > div:first-child');
    }
  });

  test('should load the data catalog', async ({ page }) => {
    await page.click('a[href="/datasets"]');
    await expect(page).toHaveURL('/datasets');
    
    // Check for the Data Catalog header
    await expect(page.locator('h1:has-text("Data Catalog")')).toBeVisible();
    
    // Verify either a dataset card exists or the empty state exists
    const hasDatasets = await page.locator('.grid > div.group').count() > 0;
    const hasEmptyState = await page.locator('text=No datasets found').isVisible();
    
    expect(hasDatasets || hasEmptyState).toBeTruthy();
  });

  test('should navigate to dataset details and view lineage', async ({ page }) => {
    await page.goto('/datasets');
    
    // Wait for datasets to load
    await page.waitForSelector('h1:has-text("Data Catalog")');

    // If there are datasets, click the first one
    const datasetsCount = await page.locator('.grid > div.group').count();
    if (datasetsCount > 0) {
      await page.click('.grid > div.group:first-child');
      
      // Verify Dataset Details page loaded
      await expect(page.locator('h1')).toBeVisible();
      
      // Check tabs
      await expect(page.locator('button:has-text("Overview")')).toBeVisible();
      await expect(page.locator('button:has-text("Lineage Graph")')).toBeVisible();
      
      // Navigate to Lineage Graph
      await page.click('button:has-text("Lineage Graph")');
      
      // Expect ReactFlow to render
      await expect(page.locator('.react-flow')).toBeVisible();
    } else {
      console.log('No datasets found to test lineage. Skipping lineage check.');
    }
  });
});
