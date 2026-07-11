import { useEffect } from 'react'

const SITE = 'Authenticate WFB'

export default function usePageMeta({ title, description }: { title?: string; description?: string } = {}) {
  useEffect(() => {
    document.title = title ? `${title} — ${SITE}` : SITE
    let meta: HTMLMetaElement | null = document.querySelector('meta[name="description"]')
    if (!meta) {
      meta = document.createElement('meta')
      meta.name = 'description'
      document.head.appendChild(meta)
    }
    meta.content = description || 'Shared authentication service with JWT, Google OAuth, and role-based access control.'

    let ogTitle: HTMLMetaElement | null = document.querySelector('meta[property="og:title"]')
    if (!ogTitle) { ogTitle = document.createElement('meta'); ogTitle.setAttribute('property', 'og:title'); document.head.appendChild(ogTitle) }
    ogTitle.content = document.title

    let ogDesc: HTMLMetaElement | null = document.querySelector('meta[property="og:description"]')
    if (!ogDesc) { ogDesc = document.createElement('meta'); ogDesc.setAttribute('property', 'og:description'); document.head.appendChild(ogDesc) }
    ogDesc.content = meta.content
  }, [title, description])
}
