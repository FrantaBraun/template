/**
 * Part of the With FBraun project template.
 * Author: František Braun <frantisek.braun95@gmail.com>
 * Freely available as a template for building custom applications.
 */

import { useTranslation } from 'react-i18next'
import { Link } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import { SUPPORTED_LANGUAGES } from '../i18n'

/** Small control to switch the active i18next language between the supported locales. */
function LanguageSwitcher() {
  const { i18n } = useTranslation()

  return (
    <div className="flex items-center gap-1 text-xs uppercase tracking-wide text-slate-500">
      {SUPPORTED_LANGUAGES.map((lng) => (
        <button
          key={lng}
          onClick={() => i18n.changeLanguage(lng)}
          className={`rounded px-1.5 py-0.5 ${
            i18n.resolvedLanguage === lng ? 'bg-slate-800 text-slate-100' : 'hover:text-slate-300'
          }`}
        >
          {lng}
        </button>
      ))}
    </div>
  )
}

/** Top navigation bar: brand link plus auth-aware links (account/logout when signed in, login/register otherwise). */
function Nav() {
  const { t } = useTranslation()
  const { user, logout } = useAuth()

  return (
    <header className="border-b border-slate-800 bg-slate-950">
      <div className="mx-auto flex max-w-4xl items-center justify-between px-6 py-3 text-sm text-slate-300">
        <Link to="/" className="font-semibold tracking-tight text-slate-100">
          {t('nav.brand')}
        </Link>

        <nav className="flex items-center gap-4">
          {user ? (
            <>
              <Link to="/account" className="hover:text-slate-100">
                {t('common.account')}
              </Link>
              <button onClick={() => logout()} className="hover:text-slate-100">
                {t('common.logout')}
              </button>
            </>
          ) : (
            <>
              <Link to="/login" className="hover:text-slate-100">
                {t('common.login')}
              </Link>
              <Link to="/register" className="hover:text-slate-100">
                {t('common.register')}
              </Link>
            </>
          )}
          <LanguageSwitcher />
        </nav>
      </div>
    </header>
  )
}

/** Page chrome shared by every route: renders Nav above the routed page content. */
export default function Layout({ children }: { children: React.ReactNode }) {
  return (
    <>
      <Nav />
      <main className="page">{children}</main>
    </>
  )
}
