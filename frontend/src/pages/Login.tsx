import { useState, type FormEvent } from 'react'
import { useLocation } from 'react-router-dom'
import { getAuthUrl } from '../api/client'
import { ConsentRequiredError, useAuth } from '../context/AuthContext'
import usePageMeta from '../hooks/usePageMeta'

function buildConsentUrl(groupId: string) {
  const redirectUri = `${window.location.origin}/consent-callback`
  return `${getAuthUrl()}/consent?group=${groupId}&redirect_uri=${encodeURIComponent(redirectUri)}`
}

function buildGoogleLoginUrl() {
  const redirectUri = `${window.location.origin}/oauth/callback`
  return `${getAuthUrl()}/auth/google?redirect_uri=${encodeURIComponent(redirectUri)}`
}

export default function Login() {
  usePageMeta({ title: 'Sign in', description: 'Sign in to your account.' })
  const { login } = useAuth()
  const location = useLocation()
  const [identifier, setIdentifier] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState<string | null>(
    (location.state as { flash?: string } | null)?.flash ?? null,
  )
  const [loading, setLoading] = useState(false)

  async function handleSubmit(e: FormEvent) {
    e.preventDefault()
    setError(null)
    setLoading(true)
    try {
      await login(identifier, password)
    } catch (err) {
      if (err instanceof ConsentRequiredError) {
        window.location.href = buildConsentUrl(err.groupId)
        return
      }
      setError(err instanceof Error ? err.message : 'Login failed')
      setLoading(false)
    }
  }

  return (
    <div className="mx-auto flex min-h-screen max-w-sm flex-col justify-center px-6 text-slate-100">
      <h1 className="mb-6 text-2xl font-semibold tracking-tight">Sign in</h1>

      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label htmlFor="identifier" className="mb-1 block text-sm text-slate-400">
            Email or username
          </label>
          <input
            id="identifier"
            type="text"
            value={identifier}
            onChange={(e) => setIdentifier(e.target.value)}
            required
            className="w-full rounded-lg border border-slate-800 bg-slate-900 px-3 py-2 text-slate-100"
          />
        </div>

        <div>
          <label htmlFor="password" className="mb-1 block text-sm text-slate-400">
            Password
          </label>
          <input
            id="password"
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
            className="w-full rounded-lg border border-slate-800 bg-slate-900 px-3 py-2 text-slate-100"
          />
        </div>

        {error && <p className="text-sm text-red-400">{error}</p>}

        <button
          type="submit"
          disabled={loading}
          className="w-full rounded-lg bg-slate-100 px-4 py-2 font-medium text-slate-900 disabled:opacity-50"
        >
          {loading ? 'Signing in…' : 'Sign in'}
        </button>
      </form>

      <div className="my-4 flex items-center gap-3 text-xs uppercase tracking-wide text-slate-500">
        <div className="h-px flex-1 bg-slate-800" />
        or
        <div className="h-px flex-1 bg-slate-800" />
      </div>

      <a
        href={buildGoogleLoginUrl()}
        className="w-full rounded-lg border border-slate-800 bg-slate-900 px-4 py-2 text-center font-medium text-slate-100"
      >
        Continue with Google
      </a>
    </div>
  )
}
