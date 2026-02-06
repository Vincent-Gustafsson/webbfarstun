const API_BASE = 'http://localhost:5173'

async function request<T>(url: string, config: RequestInit = {}): Promise<T> {
  const response = await fetch(`${API_BASE}${url}`, {
    ...config,
    headers: {
      'Content-Type': 'application/json',
      ...config.headers,
    },
  })

  // 1. Handle 4xx/5xx errors manually (Fetch doesn't do this)
  if (!response.ok) {
    // Try to parse the FastAPI error detail
    const errorBody = await response.json().catch(() => ({}))
    throw new Error(errorBody.detail || `HTTP Error ${response.status}`)
  }

  // 2. Auto-return JSON (if applicable)
  // Check if content-type is json, otherwise return text or blob
  return response.json()
}

export const http = {
  get: <T>(url: string) => request<T>(url, { method: 'GET' }),

  // Helper to handle query params
  getWithParams: <T>(url: string, params: Record<string, any>) => {
    const queryString = new URLSearchParams(params).toString()
    return request<T>(`${url}?${queryString}`, { method: 'GET' })
  },

  post: <T>(url: string, body: any) =>
    request<T>(url, { method: 'POST', body: JSON.stringify(body) }),

  patch: <T>(url: string, body: any) =>
    request<T>(url, { method: 'PATCH', body: JSON.stringify(body) }),

  delete: <T>(url: string) => request<T>(url, { method: 'DELETE' }),
}
