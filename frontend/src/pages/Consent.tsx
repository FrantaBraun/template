import { useEffect, useState } from 'react'
import { useNavigate, useSearchParams } from 'react-router-dom'
import { apiFetch } from '../api/client'
import usePageMeta from '../hooks/usePageMeta'

interface GroupInfo {
  id: string
  name: string
  description: string
  scopes: string[]
}

const SCOPE_LABELS: Record<string, string> = {
  email: 'E-mailová adresa',
  first_name: 'Křestní jméno',
  last_name: 'Příjmení',
  avatar_url: 'Profilový obrázek',
  birth_date: 'Datum narození',
  language_code: 'Jazykové preference',
  country_code: 'Země',
}

export default function Consent() {
  usePageMeta({ title: 'Povolení přístupu', description: 'Povolte nebo odmítněte přístup k vašim údajům.' })
  const [params] = useSearchParams()
  const navigate = useNavigate()
  const groupId = params.get('group')
  const redirectTo = params.get('redirect') || '/'

  const [group, setGroup] = useState<GroupInfo | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [loading, setLoading] = useState(true)
  const [submitting, setSubmitting] = useState(false)

  useEffect(() => {
    if (!groupId) {
      setError('Chybí identifikátor skupiny aplikace.')
      setLoading(false)
      return
    }
    apiFetch('/api/auth/group-info')
      .then((r) => (r.ok ? r.json() : Promise.reject()))
      .then(setGroup)
      .catch(() => setError('Nepodařilo se načíst informace o aplikaci.'))
      .finally(() => setLoading(false))
  }, [groupId])

  async function respond(action: 'grant' | 'reject') {
    if (!groupId) return
    setSubmitting(true)
    setError(null)
    try {
      const resp = await apiFetch(`/api/auth/consent/${groupId}/${action}`, { method: 'POST' })
      if (!resp.ok) throw new Error()
      if (action === 'grant') {
        navigate(redirectTo, { replace: true })
      } else {
        navigate('/consent-rejected', { replace: true })
      }
    } catch {
      setError('Akci se nepodařilo dokončit. Zkuste to prosím znovu.')
      setSubmitting(false)
    }
  }

  if (loading) {
    return (
      <div className="flex min-h-screen items-center justify-center text-slate-100">
        <p className="text-sm text-slate-400">Načítání…</p>
      </div>
    )
  }

  if (!group) {
    return (
      <div className="flex min-h-screen items-center justify-center px-6 text-center text-slate-100">
        <p className="text-sm text-red-400">{error || 'Aplikaci se nepodařilo najít.'}</p>
      </div>
    )
  }

  return (
    <div className="mx-auto flex min-h-screen max-w-md flex-col justify-center px-6 text-slate-100">
      <h1 className="mb-2 text-2xl font-semibold tracking-tight">Povolení přístupu</h1>
      <p className="mb-6 text-sm text-slate-400">
        <strong className="text-slate-200">{group.name}</strong> žádá o přístup k následujícím údajům z vašeho účtu.
      </p>

      {group.description && <p className="mb-4 text-sm text-slate-400">{group.description}</p>}

      <ul className="mb-6 space-y-2">
        {group.scopes.map((scope) => (
          <li key={scope} className="flex items-center gap-2 text-sm">
            <span className="text-emerald-400">✓</span>
            {SCOPE_LABELS[scope] || scope}
          </li>
        ))}
      </ul>

      {error && <p className="mb-4 text-sm text-red-400">{error}</p>}

      <div className="flex gap-3">
        <button
          onClick={() => respond('grant')}
          disabled={submitting}
          className="flex-1 rounded-lg bg-slate-100 px-4 py-2 font-medium text-slate-900 disabled:opacity-50"
        >
          Povolit
        </button>
        <button
          onClick={() => respond('reject')}
          disabled={submitting}
          className="flex-1 rounded-lg border border-slate-800 bg-slate-900 px-4 py-2 font-medium text-slate-100 disabled:opacity-50"
        >
          Odmítnout
        </button>
      </div>
    </div>
  )
}
