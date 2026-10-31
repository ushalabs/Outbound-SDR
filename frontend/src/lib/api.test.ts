import { afterEach, describe, expect, it, vi } from 'vitest'
import { api, ApiError } from './api'

afterEach(() => vi.unstubAllGlobals())
describe('API client', () => {
  it('returns server validation messages without discarding the status', async () => {
    vi.stubGlobal('fetch', vi.fn().mockResolvedValue(new Response(JSON.stringify({ detail: [{ message: 'Email is invalid' }] }), { status: 422 })))
    await expect(api('/prospects')).rejects.toMatchObject({ status: 422, message: 'Email is invalid' })
  })
  it('reports unreachable backend as a useful error', async () => {
    vi.stubGlobal('fetch', vi.fn().mockRejectedValue(new TypeError('Failed to fetch')))
    await expect(api('/health')).rejects.toBeInstanceOf(ApiError)
  })
  it('handles no-content deletes', async () => {
    vi.stubGlobal('fetch', vi.fn().mockResolvedValue(new Response(null, { status: 204 })))
    expect(await api('/prospects/id', { method: 'DELETE' })).toBeUndefined()
  })
})
