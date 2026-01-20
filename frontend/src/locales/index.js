import { createI18n } from 'vue-i18n'
import en from './en.json'
import pl from './pl.json'

const STORAGE_KEY = 'squig_league_language'
const SUPPORTED_LOCALES = ['en', 'pl']
const DEFAULT_LOCALE = 'en'

function getInitialLocale() {
  // Check localStorage first (for guests and initial load before auth)
  const stored = localStorage.getItem(STORAGE_KEY)
  if (stored && SUPPORTED_LOCALES.includes(stored)) {
    return stored
  }

  // Fall back to browser language
  const browserLang = navigator.language.split('-')[0]
  if (SUPPORTED_LOCALES.includes(browserLang)) {
    return browserLang
  }

  return DEFAULT_LOCALE
}

const i18n = createI18n({
  legacy: false, // Use Composition API
  locale: getInitialLocale(),
  fallbackLocale: DEFAULT_LOCALE,
  messages: { en, pl }
})

export { STORAGE_KEY, SUPPORTED_LOCALES, DEFAULT_LOCALE }
export default i18n
