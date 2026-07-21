type HttpMethod = 'GET' | 'POST' | 'PUT' | 'PATCH' | 'DELETE'

interface ApiOptions {
  method?: HttpMethod
  body?: Record<string, unknown>
  headers?: HeadersInit
}

export function useApi() {
  const config = useRuntimeConfig()
  const selectedFarmId = useState<string | null>('selected-farm-id', () => null)
  const csrfToken = useState<string | null>('csrf-token', () => null)

  async function ensureCsrfToken(): Promise<string> {
    if (csrfToken.value) return csrfToken.value
    const response = await $fetch<{ csrfToken: string }>(`${config.public.apiBase}/auth/csrf/`, {
      credentials: 'include',
    })
    csrfToken.value = response.csrfToken
    return response.csrfToken
  }

  async function request<T>(path: string, options: ApiOptions = {}): Promise<T> {
    const method: HttpMethod = options.method || 'GET'
    const headers = new Headers(options.headers)
    headers.set('Accept', 'application/json')
    if (selectedFarmId.value) headers.set('X-Farm-ID', selectedFarmId.value)
    if (!['GET', 'HEAD', 'OPTIONS'].includes(method)) {
      headers.set('X-CSRFToken', await ensureCsrfToken())
    }
    return await $fetch<T>(`${config.public.apiBase}${path}`, {
      ...options,
      method,
      headers,
      credentials: 'include',
    })
  }

  return { request, selectedFarmId }
}
