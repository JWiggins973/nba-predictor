// @ts-check
import { test, expect } from '@playwright/test';

test('has title', async ({ page }) => {
  await page.goto('https://jwiggins973.github.io/nba-predictor/');

  // Expect a title "to contain" a substring.
  await expect(page).toHaveTitle(/NBA Predictor/);
});

test('search for a player', async ({ page }) => {
  await page.goto('https://jwiggins973.github.io/nba-predictor/');
  
  const playerName = 'LeBron James';
  const searchInput = page.getByPlaceholder('Search player...');

  // Type a player's name into the search input.
  await searchInput.fill(playerName);
  await expect(searchInput).toHaveValue(playerName);

  // Click the predict button.
  const predictButton = page.getByRole('button', { name: 'Predict' });
  await predictButton.click();

  // Expect the page to display the predicted results after website loads.
  await expect(page.getByText('Loading...')).not.toBeVisible({ timeout: 15000 });
  await expect(page.getByRole('heading', { name: playerName })).toBeVisible();
  await expect(page.getByRole('heading', { name: 'Prediction' })).toBeVisible();
  await expect(page.getByRole('heading', { name: 'Scoring History' })).toBeVisible();

});