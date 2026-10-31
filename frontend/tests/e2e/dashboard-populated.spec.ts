import { expect, test } from '@playwright/test'
test('dashboard charts reflect persisted isolated prospects and filters', async ({ page }) => {
  test.skip(process.env.ISOLATED_E2E !== '1', 'Run in an isolated Neon schema')
  const errors: string[] = []
  page.on('pageerror', error => errors.push(error.message))
  await page.setViewportSize({ width: 1440, height: 1100 })
  for (const label of ['education', 'software']) {
    const response = await page.request.post('/api/prospects', { data: { company_name: `Clearly synthetic ${label} dashboard fixture`, website_url: `https://${label}-dashboard.invalid`, industry: label } })
    expect(response.status()).toBe(201)
  }
  await page.goto('/')
  await expect(page.getByTestId('total-prospects')).toHaveText('2')
  await expect(page.locator('.status-legend')).toContainText('new')
  await expect(page.locator('.industry-list')).toContainText('education')
  await expect(page.locator('.pipeline-card .recharts-wrapper')).toBeVisible()
  await page.reload()
  await expect(page.getByTestId('total-prospects')).toHaveText('2')
  await page.screenshot({ path: '../artifacts/phase-7-dashboard-populated.png', fullPage: true })
  await page.getByLabel('Dashboard date range').selectOption('custom')
  await page.getByLabel('Start date').fill('2020-01-01')
  await page.getByLabel('End date').fill('2020-01-02')
  await expect(page.getByTestId('total-prospects')).toHaveText('0')
  expect(errors).toEqual([])
})
