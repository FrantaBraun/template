const BASE_URL = (import.meta.env.VITE_API_URL || 'http://localhost:8000').replace(/\/$/, '')

let _access  = localStorage.getItem('access_token')  || null
let _refresh = localStorage.getItem('refresh_token') || null

export function setTokens(access: string, refresh: string) {
  _access  = access
  _refresh = refresh
  localStorage.setItem('access_token',  access)
  localStorage.setItem('refresh_token', refresh)
}

export function clearTokens() {
  _access  = null
  _refresh = null
  localStorage.removeItem('access_token')
  localStorage.removeItem('refresh_token')
}

export function getAccessToken()  { return _access }
export function getRefreshToken() { return _refresh }
export function getApiUrl()       { return BASE_URL }

async function doRefresh() {
  if (!_refresh) throw new Error('no_refresh')
  const resp = await fetch(`${BASE_URL}/api/auth/refresh`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ refresh_token: _refresh }),
  })
  if (!resp.ok) { clearTokens(); throw new Error('session_expired') }
  const data = await resp.json()
  setTokens(data.access_token, data.refresh_token)
  return data.access_token
}

export async function apiFetch(path: string, options: { method?: string; headers?: {Authorization?: string}, [key: string]: any } = { headers: {}, method: 'GET' }) {
  const url = `${BASE_URL}${path}`
  const headers = { 'Content-Type': 'application/json', ...options.headers }
  if (_access) headers.Authorization = `Bearer ${_access}`

  let resp = await fetch(url, { ...options, headers })

  if (resp.status === 401 && _refresh) {
    try {
      const fresh = await doRefresh()
      headers.Authorization = `Bearer ${fresh}`
      resp = await fetch(url, { ...options, headers })
    } catch {
      clearTokens()
      window.location.href = '/login'
      throw new Error('Session expired')
    }
  }

  return resp
}

export function decodeJwt(token: string) {
  try {
    return JSON.parse(atob(token.split('.')[1].replace(/-/g, '+').replace(/_/g, '/')))
  } catch { return null }
}
