import { expect, test } from '@playwright/test'
test('prospect workspace supports forms, mapping and honest empty states', async ({ page }) => {
  await page.goto('/prospects')
  await expect(page.getByRole('heading', { name: 'Prospects', exact: true })).toBeVisible()
  await page.getByRole('button', { name: 'Add prospect', exact: true }).click()
  for (let index = 0; index < 20; index++) {
    await page.keyboard.press('Tab')
    expect(
      await page.getByRole('dialog').evaluate((dialog) => dialog.contains(document.activeElement)),
    ).toBeTruthy()
  }
  await page.getByRole('button', { name: 'Save prospect' }).click()
  await expect(page.getByText('Company name is required')).toBeVisible()
  await page.getByRole('button', { name: 'Cancel', exact: true }).click()
  await page.getByRole('button', { name: 'Import CSV', exact: true }).click()
  await page.getByLabel('CSV file').setInputFiles({
    name: 'fixture.csv',
    mimeType: 'text/csv',
    buffer: Buffer.from(
      'company,website,name\nIsolated browser fixture,fixture.invalid,Synthetic browser fixture',
    ),
  })
  await expect(page.getByRole('heading', { name: 'Match CSV columns' })).toBeVisible()
  await page.getByRole('button', { name: 'Preview import' }).click()
  await expect(page.getByText('1 rows · 1 ready · 0 duplicates · 0 invalid')).toBeVisible()
  // Preview does not persist the synthetic fixture in normal application data.
  await page.getByRole('button', { name: 'Cancel', exact: true }).click()
  await page.getByRole('button', { name: 'Discover', exact: true }).click()
  await expect(page.getByRole('dialog', { name: 'Discover from public sources' })).toBeVisible()
  await page.keyboard.press('Escape')
  await page.screenshot({ path: '../artifacts/phase-2-prospects-desktop.png', fullPage: true })
  await page.setViewportSize({ width: 390, height: 844 })
  await page.reload()
  await expect(page.getByRole('button', { name: 'Add prospect', exact: true })).toBeVisible()
  await expect(page.getByText('No prospects yet')).toBeVisible()
  expect(
    await page.evaluate(() => document.documentElement.scrollWidth <= window.innerWidth),
  ).toBeTruthy()
  await page.screenshot({ path: '../artifacts/phase-2-prospects-mobile.png', fullPage: true })
})
