import { Link } from 'react-router-dom'
import usePageMeta from '../hooks/usePageMeta'

export default function ConsentRejected() {
  usePageMeta({ title: 'Přístup odepřen' })

  return (
    <div className="flex min-h-screen flex-col items-center justify-center gap-4 px-6 text-center text-slate-100">
      <h1 className="text-2xl font-semibold tracking-tight">Přístup odepřen</h1>
      <p className="max-w-md text-sm text-slate-400">
        Bez povolení přístupu k údajům v rámci této aplikace nemáte plnohodnotný přístup do šablony. Pokud jste se
        rozhodli omylem, můžete se{' '}
        <Link to="/login" className="text-slate-100 underline">
          přihlásit znovu
        </Link>{' '}
        a povolení udělit.
      </p>
    </div>
  )
}
