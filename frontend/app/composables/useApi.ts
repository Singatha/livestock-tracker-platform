type HttpMethod = 'GET' | 'POST' | 'PUT' | 'PATCH' | 'DELETE'

interface ApiOptions {
  method?: HttpMethod
  body?: Record<string, unknown>
  headers?: HeadersInit
}

export function useApi() {
  const config = useRuntimeConfig()
  const selectedFarmId = useCookie<string | null>('selected-farm-id', {
    default: () => null,
    sameSite: 'lax',
  })
  const csrfToken = useState<string | null>('csrf-token', () => null)

  async function ensureCsrfToken(): Promise<string> {
    if (csrfToken.value) return csrfToken.value
    const response = await $fetch<{ csrfToken: string }>(`${config.public.apiBase}/auth/csrf/`, {
      credentials: 'include',
    })
    csrfToken.value = response.csrfToken
    return response.csrfToken
  }

  function resetCsrfToken() {
    csrfToken.value = null
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

  async function download(path: string, filename: string): Promise<void> {
    const headers = new Headers({ Accept: 'text/csv' })
    if (selectedFarmId.value) headers.set('X-Farm-ID', selectedFarmId.value)
    const response = await fetch(`${config.public.apiBase}${path}`, {
      headers,
      credentials: 'include',
    })
    if (!response.ok) throw new Error('Download failed')
    const url = URL.createObjectURL(await response.blob())
    const anchor = document.createElement('a')
    anchor.href = url
    anchor.download = filename
    anchor.click()
    URL.revokeObjectURL(url)
  }

  return { download, request, resetCsrfToken, selectedFarmId }
}
