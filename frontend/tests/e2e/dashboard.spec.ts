import { expect, test } from '@playwright/test'
test('dashboard shows genuine zero states, working ranges and responsive cards', async ({
  page,
}) => {
  test.skip(process.env.ISOLATED_E2E === '1', 'Zero-state check targets the empty normal workspace')
  const errors: string[] = []
  page.on('pageerror', (error) => errors.push(error.message))
  await page.setViewportSize({ width: 1440, height: 1100 })
  await page.goto('/')
  await expect(page.getByTestId('total-prospects')).toHaveText('0')
  await expect(page.getByText('No prior-period baseline')).toBeVisible()
  await page.getByRole('button', { name: 'Last 7 days', exact: true }).click()
  await expect(page.getByText(/vs previous 7 days/)).toHaveCount(0)
  await expect(page.getByText('7 days', { exact: true })).toBeVisible()
  await page.screenshot({ path: '../artifacts/phase-7-dashboard-desktop.png', fullPage: true })
  await page.getByRole('button', { name: 'Custom range', exact: true }).click()
  await page.getByLabel('Start date').fill('2026-10-01')
  await page.getByLabel('End date').fill('2026-10-02')
  await expect(page.getByText('2 days', { exact: true })).toBeVisible()
  await page.getByRole('button', { name: 'Last 30 days', exact: true }).click()
  await page.setViewportSize({ width: 390, height: 844 })
  await expect(page.getByTestId('total-prospects')).toHaveText('0')
  expect(
    await page.evaluate(() => document.documentElement.scrollWidth <= window.innerWidth),
  ).toBeTruthy()
  await page.screenshot({ path: '../artifacts/phase-7-dashboard-mobile.png', fullPage: true })
  expect(errors).toEqual([])
})
