const API_BASE = 'https://dev.webbfarstun.shop/api'

function pickMessage(data: any, status: number) {
  const detail = data?.detail

  if (typeof detail === 'string') return detail
  if (detail?.errors && typeof detail.errors === 'object') return 'Validation error'
  if (typeof data?.message === 'string') return data.message

  return `HTTP Error ${status}`
}

async function request<T>(url: string, config: RequestInit = {}): Promise<T> {
  const response = await fetch(`${API_BASE}${url}`, {
    ...config,
    headers: {
      'Content-Type': 'application/json',
      ...config.headers,
    },
  })

  const text = await response.text()
  let data: any = null
  try {
    data = text ? JSON.parse(text) : null
  } catch {
    data = text
  }

  if (!response.ok) {
    const err: any = new Error(pickMessage(data, response.status))
    err.status = response.status
    err.data = data
    throw err
  }

  if (response.status === 204) return undefined as unknown as T

  return data as T
}

export const http = {
  get: <T>(url: string) => request<T>(url, { method: 'GET' }),
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
