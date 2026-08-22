import { afterEach, describe, expect, it, vi } from 'vitest'
import { ApiError, apiRequest } from '../../src/api/client'

function mockFetchOnce(response: { ok: boolean; status: number; json: () => Promise<unknown> }) {
  global.fetch = vi.fn().mockResolvedValue(response) as unknown as typeof fetch
}

describe('apiRequest', () => {
  afterEach(() => {
    vi.restoreAllMocks()
  })

  it('returns parsed JSON on a successful response', async () => {
    mockFetchOnce({ ok: true, status: 200, json: async () => ({ hello: 'world' }) })

    const result = await apiRequest('/test')

    expect(result).toEqual({ hello: 'world' })
  })

  it('sends an Authorization header when a token is provided', async () => {
    mockFetchOnce({ ok: true, status: 200, json: async () => ({}) })

    await apiRequest('/test', { token: 'abc123' })

    const [, options] = (fetch as ReturnType<typeof vi.fn>).mock.calls[0]
    expect((options.headers as Record<string, string>).Authorization).toBe('Bearer abc123')
  })

  it('returns undefined for a 204 response without attempting to parse a body', async () => {
    const json = vi.fn()
    mockFetchOnce({ ok: true, status: 204, json })

    const result = await apiRequest('/test', { method: 'DELETE' })

    expect(result).toBeUndefined()
    expect(json).not.toHaveBeenCalled()
  })

  it('throws an ApiError with the backend-provided error message on failure', async () => {
    mockFetchOnce({ ok: false, status: 404, json: async () => ({ error: 'Article not found' }) })

    await expect(apiRequest('/test')).rejects.toThrow('Article not found')
  })

  it('throws an ApiError carrying the real HTTP status code', async () => {
    mockFetchOnce({
      ok: false,
      status: 401,
      json: async () => ({ error: 'Invalid or expired token' }),
    })

    await expect(apiRequest('/test')).rejects.toMatchObject({ status: 401 })
    await expect(apiRequest('/test')).rejects.toBeInstanceOf(ApiError)
  })

  it('stringifies Marshmallow-style validation errors', async () => {
    mockFetchOnce({
      ok: false,
      status: 400,
      json: async () => ({ errors: { password: ['Shorter than minimum length 8.'] } }),
    })

    await expect(apiRequest('/test')).rejects.toThrow(/password/)
  })
})
