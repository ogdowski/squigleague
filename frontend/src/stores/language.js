import { defineStore } from 'pinia'
import axios from 'axios'
import { STORAGE_KEY, SUPPORTED_LOCALES, DEFAULT_LOCALE } from '../locales'

const API_URL = import.meta.env.VITE_API_URL || '/api'

export const useLanguageStore = defineStore('language', {
  state: () => ({
    currentLocale: localStorage.getItem(STORAGE_KEY) || DEFAULT_LOCALE,
    supportedLocales: SUPPORTED_LOCALES
  }),

  actions: {
    async setLocale(locale, isAuthenticated = false) {
      if (!SUPPORTED_LOCALES.includes(locale)) {
        console.warn(`Unsupported locale: ${locale}`)
        return
      }

      this.currentLocale = locale
      localStorage.setItem(STORAGE_KEY, locale)

      // If authenticated, persist to backend
      if (isAuthenticated) {
        try {
          await axios.patch(`${API_URL}/auth/me`, {
            preferred_language: locale
          })
        } catch (error) {
          console.error('Failed to save language preference:', error)
        }
      }
    },

    initFromUser(preferredLanguage) {
      if (preferredLanguage && SUPPORTED_LOCALES.includes(preferredLanguage)) {
        this.currentLocale = preferredLanguage
        localStorage.setItem(STORAGE_KEY, preferredLanguage)
      }
    }
  }
})
