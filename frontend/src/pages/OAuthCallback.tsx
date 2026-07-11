import { useEffect, useRef, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { setTokens } from '../api/client'
import { useAuth } from '../context/AuthContext'
import usePageMeta from '../hooks/usePageMeta'

export default function OAuthCallback() {
  usePageMeta({ title: 'Signing in…' })
  const navigate = useNavigate()
  const { loadUser } = useAuth()
  const [error, setError] = useState<string | null>(null)
  const ran = useRef(false)

  useEffect(() => {
    if (ran.current) return
    ran.current = true

    const params = new URLSearchParams(window.location.search)
    const accessToken = params.get('access_token')
    const refreshToken = params.get('refresh_token')
    const oauthError = params.get('error')

    if (oauthError || !accessToken || !refreshToken) {
      navigate('/login', { state: { flash: oauthError || 'Google sign-in failed. Please try again.' } })
      return
    }

    setTokens(accessToken, refreshToken)
    loadUser()
      .then(() => navigate('/', { replace: true }))
      .catch(() => setError('Signed in, but loading your profile failed.'))
  }, [navigate, loadUser])

  return (
    <div className="flex min-h-screen flex-col items-center justify-center gap-3 px-6 text-center text-slate-100">
      {error ? (
        <p className="text-sm text-red-400">{error}</p>
      ) : (
        <p className="text-sm text-slate-400">Signing in…</p>
      )}
    </div>
  )
}
