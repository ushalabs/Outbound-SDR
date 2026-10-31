export class ApiError extends Error { constructor(public status: number, message: string) { super(message) } }
export async function api<T>(path: string, options: RequestInit = {}): Promise<T> {
  let response: Response
  try { response = await fetch(`/api${path}`, { ...options, headers: { ...(options.body instanceof FormData ? {} : { 'Content-Type': 'application/json' }), ...options.headers } }) }
  catch { throw new ApiError(0, 'The server could not be reached. Check that the backend is running.') }
  if (!response.ok) {
    const body = await response.json().catch(() => ({}))
    const detail = body.detail
    throw new ApiError(response.status, typeof detail === 'string' ? detail : Array.isArray(detail) ? detail.map((e: { message?: string }) => e.message ?? 'Invalid input').join('; ') : 'The request failed. Please try again.')
  }
  return response.status === 204 ? undefined as T : response.json()
}
