const BASE_URL = import.meta.env.VITE_API_BASE_URL

export class ApiError extends Error {
  status: number

  constructor(status: number, message: string) {
    super(message)
    this.status = status
  }
}

interface RequestOptions {
  method?: string
  body?: unknown
  token?: string | null
}

export async function apiRequest<T>(
  path: string,
  { method = 'GET', body, token }: RequestOptions = {},
): Promise<T> {
  const headers: HeadersInit = {}
  if (body !== undefined) headers['Content-Type'] = 'application/json'
  if (token) headers['Authorization'] = `Bearer ${token}`

  const response = await fetch(`${BASE_URL}${path}`, {
    method,
    headers,
    body: body !== undefined ? JSON.stringify(body) : undefined,
  })

  if (response.status === 204) {
    return undefined as T
  }

  const data = await response.json().catch(() => null)

  if (!response.ok) {
    const message =
      data?.error ?? (data?.errors ? JSON.stringify(data.errors) : null) ?? `Request failed with status ${response.status}`
    throw new ApiError(response.status, message)
  }

  return data as T
}
