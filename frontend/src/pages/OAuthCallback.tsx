import { useEffect, useRef, useState } from 'react'
import { useTranslation } from 'react-i18next'
import { useNavigate } from 'react-router-dom'
import { setTokens } from '../api/client'
import { useAuth } from '../context/AuthContext'
import usePageMeta from '../hooks/usePageMeta'

export default function OAuthCallback() {
  const { t } = useTranslation()
  usePageMeta({ title: t('oauthCallback.pageTitle') })
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
      navigate('/login', { state: { flash: oauthError || t('oauthCallback.googleFailed') } })
      return
    }

    setTokens(accessToken, refreshToken)
    loadUser()
      .then((loaded) => {
        // If consent was required, loadUser() already redirected to
        // /consent internally - navigating to '/' here too would cancel it.
        if (loaded) navigate('/', { replace: true })
      })
      .catch(() => setError(t('oauthCallback.profileLoadError')))
  }, [navigate, loadUser, t])

  return (
    <div className="flex min-h-screen flex-col items-center justify-center gap-3 px-6 text-center text-slate-100">
      {error ? (
        <p className="text-sm text-red-400">{error}</p>
      ) : (
        <p className="text-sm text-slate-400">{t('oauthCallback.signingIn')}</p>
      )}
    </div>
  )
}
