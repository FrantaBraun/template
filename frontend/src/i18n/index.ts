/**
 * Part of the With FBraun project template.
 * Author: František Braun <frantisek.braun95@gmail.com>
 * Freely available as a template for building custom applications.
 */

import i18n from 'i18next'
import LanguageDetector from 'i18next-browser-languagedetector'
import { initReactI18next } from 'react-i18next'
import cs from './locales/cs.json'
import en from './locales/en.json'

i18n
  .use(LanguageDetector)
  .use(initReactI18next)
  .init({
    resources: {
      cs: { translation: cs },
      en: { translation: en },
    },
    // cs is the fallback (not the more conventional en) since this template
    // originates from a Czech-first product; supportedLngs pins detection to
    // exactly these two so an unrecognized browser locale falls back cleanly
    // instead of resolving to a partial/missing resource bundle.
    fallbackLng: 'cs',
    supportedLngs: ['cs', 'en'],
    // Detection order: a previously-saved choice (localStorage) always wins
    // over the browser's own language (navigator) on repeat visits; caches
    // writes the resolved language back to localStorage so the choice sticks.
    detection: {
      order: ['localStorage', 'navigator'],
      caches: ['localStorage'],
    },
    interpolation: {
      escapeValue: false,
    },
  })

export default i18n
