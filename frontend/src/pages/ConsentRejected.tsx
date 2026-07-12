import { Trans, useTranslation } from 'react-i18next'
import { Link } from 'react-router-dom'
import usePageMeta from '../hooks/usePageMeta'

export default function ConsentRejected() {
  const { t } = useTranslation()
  usePageMeta({ title: t('consentRejected.pageTitle') })

  return (
    <div className="flex min-h-screen flex-col items-center justify-center gap-4 px-6 text-center text-slate-100">
      <h1 className="text-2xl font-semibold tracking-tight">{t('consentRejected.title')}</h1>
      <p className="max-w-md text-sm text-slate-400">
        <Trans
          i18nKey="consentRejected.message"
          components={{ link: <Link to="/login" className="text-slate-100 underline" /> }}
        />
      </p>
    </div>
  )
}
