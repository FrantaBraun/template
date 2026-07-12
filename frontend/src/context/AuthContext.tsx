import { createContext, useCallback, useContext, useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { clearTokens, getRefreshToken, setTokens } from '../api/client'
import { apiFetch } from '../api/client'

interface AuthContextType {
  user: any | null
  loading: boolean
  login: (identifier: string, password: string) => Promise<void>
  logout: () => Promise<void>
  setUser: (user: any) => void
  loadUser: () => Promise<boolean>
}

const AuthContext = createContext<AuthContextType>({
  user: null,
  loading: true,
  login: async () => {},
  logout: async () => {},
  setUser: () => {},
  loadUser: async () => false,
})

// err.detail is an object for consent_required ({consent_required, application_group_id}),
// not a string - `new Error(err.detail)` would silently stringify it to "[object Object]".
function extractConsentGroupId(body: any): string | null {
  const detail = body?.detail
  if (detail && typeof detail === 'object' && detail.consent_required) {
    return detail.application_group_id ?? null
  }
  return null
}

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser]       = useState(null)
  const [loading, setLoading] = useState(true)
  const navigate = useNavigate()

  const redirectToConsent = useCallback(
    (groupId: string) => {
      const redirectTo = window.location.pathname + window.location.search
      navigate(`/consent?group=${groupId}&redirect=${encodeURIComponent(redirectTo)}`, { replace: true })
    },
    [navigate],
  )

  const loadUser = useCallback(async (): Promise<boolean> => {
    const resp = await apiFetch('/api/auth/me').catch(() => null)
    if (resp?.ok) {
      setUser(await resp.json())
      return true
    }
    if (resp?.status === 403) {
      const groupId = extractConsentGroupId(await resp.json().catch(() => ({})))
      if (groupId) {
        // The user IS validly authenticated, just missing consent - keep
        // their tokens so retrying /me after granting succeeds immediately.
        redirectToConsent(groupId)
        return false
      }
    }
    clearTokens()
    setUser(null)
    return false
  }, [redirectToConsent])

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
      const groupId = extractConsentGroupId(err)
      if (groupId) {
        redirectToConsent(groupId)
        return
      }
      throw new Error(typeof err.detail === 'string' ? err.detail : 'Login failed')
    }
    const data = await resp.json()
    setTokens(data.access_token, data.refresh_token)
    const loaded = await loadUser()
    if (loaded) {
      navigate('/', { replace: true })
    }
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
