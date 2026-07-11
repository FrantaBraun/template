import { createContext, useCallback, useEffect, useState } from 'react'
import { clearTokens, getRefreshToken, setTokens } from '../api/client'
import { apiFetch } from '../api/client'

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
      throw new Error(err.detail || 'Login failed')
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

