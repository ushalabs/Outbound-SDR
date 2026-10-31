import { defineConfig } from '@playwright/test'
export default defineConfig({ testDir: './tests/e2e', use: { baseURL: process.env.E2E_BASE_URL || 'http://127.0.0.1:5173', channel: 'msedge', headless: true, actionTimeout: 15000 }, reporter: 'list' })
