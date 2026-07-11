import { createContext, useCallback, useContext, useEffect, useState } from 'react'
import { clearTokens, getRefreshToken, setTokens } from '../api/client'
import { apiFetch } from '../api/client'

export class ConsentRequiredError extends Error {
  groupId: string

  constructor(groupId: string) {
    super('consent_required')
    this.name = 'ConsentRequiredError'
    this.groupId = groupId
  }
}

interface AuthContextType {
  user: any | null
  loading: boolean
  login: (identifier: string, password: string) => Promise<void>
  logout: () => Promise<void>
  setUser: (user: any) => void
  loadUser: () => Promise<void>
}

const AuthContext = createContext<AuthContextType>({
  user: null,
  loading: true,
  login: async () => {},
  logout: async () => {},
  setUser: () => {},
  loadUser: async () => {},
})

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser]       = useState(null)
  const [loading, setLoading] = useState(true)

  const loadUser = useCallback(async () => {
    const resp = await apiFetch('/api/auth/me').catch(() => null)
    if (resp?.ok) {
      setUser(await resp.json())
    } else {
      clearTokens()
      setUser(null)
    }
  }, [])

  useEffect(() => {
    if (localStorage.getItem('access_token')) {
      loadUser().finally(() => setLoading(false))
    } else {
      setLoading(false)
    }
  }, [loadUser])

  async function login(identifier: string, password: string) {
    const resp = await apiFetch('/api/auth/login', {
      method: 'POST',
      body: JSON.stringify({ identifier, password }),
    })
    if (!resp.ok) {
      const err = await resp.json().catch(() => ({}))
      // err.detail is an object for consent_required ({consent_required, application_group_id}),
      // not a string - `new Error(err.detail)` would silently stringify it to "[object Object]".
      if (err.detail && typeof err.detail === 'object' && err.detail.consent_required) {
        throw new ConsentRequiredError(err.detail.application_group_id)
      }
      throw new Error(typeof err.detail === 'string' ? err.detail : 'Login failed')
    }
    const data = await resp.json()
    setTokens(data.access_token, data.refresh_token)
    await loadUser()
  }

  async function logout() {
    const rt = getRefreshToken()
    if (rt) {
      await apiFetch('/api/auth/logout', {
        method: 'POST',
        body: JSON.stringify({ refresh_token: rt }),
      }).catch(() => null)
    }
    clearTokens()
    setUser(null)
  }

  return (
    <AuthContext.Provider value={{ user, loading, login, logout, setUser, loadUser }}>
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  return useContext(AuthContext)
}

