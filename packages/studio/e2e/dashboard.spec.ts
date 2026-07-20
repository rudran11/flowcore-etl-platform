import { test, expect } from '@playwright/test';

test.describe('Dashboard UI', () => {
  test('Dashboard loads properly', async ({ page }) => {
    await page.goto('http://localhost:5173/');
    
    // Wait for the loading state to finish
    await expect(page.locator('text=Loading dashboard...')).not.toBeVisible({ timeout: 10000 });
    
    // Verify system health
    await expect(page.locator('text=System Online')).toBeVisible();

    // Verify Dashboard Cards
    await expect(page.locator('text=Total Pipelines')).toBeVisible();
    await expect(page.locator('text=Total Executions')).toBeVisible();
    await expect(page.locator('text=Success Rate')).toBeVisible();
    await expect(page.locator('text=Avg. Duration')).toBeVisible();

    // Verify Charts & Tables
    await expect(page.locator('text=Execution Trends')).toBeVisible();
    await expect(page.locator('text=Recent Executions')).toBeVisible();
  });

  test('Sidebar navigation works', async ({ page }) => {
    await page.goto('http://localhost:5173/');
    
    // Verify Links
    await expect(page.locator('a', { hasText: 'Dashboard' })).toBeVisible();
    await expect(page.locator('a', { hasText: 'Pipelines' })).toBeVisible();
    
    await page.click('text=Pipelines');
    await expect(page.locator('text=Pipelines Page (Coming Soon)')).toBeVisible();
    
    await page.click('text=Dashboard');
    await expect(page.locator('text=Dashboard').first()).toBeVisible();
  });
});
