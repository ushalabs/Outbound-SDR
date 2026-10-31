import { expect, test } from '@playwright/test'
test('health and six workspace routes are available', async ({ page, request }) => {
  const health = await request.get('http://127.0.0.1:8000/api/health')
  expect(health.ok()).toBeTruthy()
  const errors: string[] = []
  page.on('pageerror', (e) => errors.push(e.message))
  await page.goto('/')
  for (const label of ['Prospects', 'Research', 'Outreach', 'Approvals', 'Activity', 'Overview']) {
    await page.getByRole('link', { name: label, exact: true }).click()
    await expect(page.getByRole('heading', { level: 1 })).toBeVisible()
  }
  await expect(page.getByText('Backend online')).toBeVisible()
  await expect(page.getByText('Neon connected')).toBeVisible()
  expect(errors).toEqual([])
  await page.screenshot({ path: '../artifacts/phase-0-desktop.png', fullPage: true })
})
