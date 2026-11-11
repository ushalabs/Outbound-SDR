import { expect, test } from '@playwright/test'
test('isolated Neon prospect persists after reload, then edits and deletes', async ({ page }) => {
  test.skip(process.env.ISOLATED_E2E !== '1', 'Run through the isolated Neon acceptance harness')
  const errors: string[] = []
  page.on('pageerror', (error) => errors.push(error.message))
  await page.goto('/prospects')
  await page.getByRole('button', { name: 'Add prospect', exact: true }).click()
  await page.getByLabel('Company name', { exact: true }).fill('Isolated E2E fixture')
  await page.getByLabel('Company website', { exact: true }).fill('https://fixture.invalid')
  await page.getByLabel('Contact name (if known)', { exact: true }).fill('Synthetic E2E contact')
  await page.getByRole('button', { name: 'Save prospect' }).click()
  await expect(
    page.getByRole('button', { name: 'Isolated E2E fixture', exact: true }),
  ).toBeVisible()
  await page.reload()
  await expect(page.getByText('Synthetic E2E contact', { exact: true })).toBeVisible()
  await page.getByRole('button', { name: 'Edit Synthetic E2E contact', exact: true }).click()
  await page.getByLabel('Notes', { exact: true }).fill('Persisted after browser reload')
  await page.getByRole('button', { name: 'Save prospect' }).click()
  await expect(page.getByRole('dialog')).not.toBeVisible()
  await page.getByRole('button', { name: 'Isolated E2E fixture', exact: true }).click()
  await expect(page.getByText('Associated prospects (1)')).toBeVisible()
  await page.keyboard.press('Escape')
  await page.getByRole('button', { name: 'Delete Synthetic E2E contact', exact: true }).click()
  await page.getByRole('button', { name: 'Confirm deletion' }).click()
  await expect(page.getByText('No prospects yet')).toBeVisible()
  expect(errors).toEqual([])
})
