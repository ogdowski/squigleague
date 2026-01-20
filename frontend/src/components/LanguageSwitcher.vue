<template>
  <button
    @click="toggleLanguage"
    class="w-7 h-5 rounded overflow-hidden border border-gray-600 hover:border-gray-400 transition-all"
    :title="currentLocale === 'pl' ? 'Switch to English' : 'Przełącz na Polski'"
  >
    <!-- Show current language flag -->
    <svg v-if="currentLocale === 'pl'" viewBox="0 0 16 10" class="w-full h-full">
      <!-- Polish Flag - current language is Polish -->
      <rect width="16" height="5" fill="#fff"/>
      <rect y="5" width="16" height="5" fill="#dc143c"/>
    </svg>
    <svg v-else viewBox="0 0 60 30" class="w-full h-full">
      <!-- UK Flag - current language is English -->
      <clipPath id="uk-clip">
        <path d="M0,0 v30 h60 v-30 z"/>
      </clipPath>
      <clipPath id="uk-diag">
        <path d="M30,15 h30 v15 z v15 h-30 z h-30 v-15 z v-15 h30 z"/>
      </clipPath>
      <g clip-path="url(#uk-clip)">
        <path d="M0,0 v30 h60 v-30 z" fill="#012169"/>
        <path d="M0,0 L60,30 M60,0 L0,30" stroke="#fff" stroke-width="6"/>
        <path d="M0,0 L60,30 M60,0 L0,30" clip-path="url(#uk-diag)" stroke="#C8102E" stroke-width="4"/>
        <path d="M30,0 v30 M0,15 h60" stroke="#fff" stroke-width="10"/>
        <path d="M30,0 v30 M0,15 h60" stroke="#C8102E" stroke-width="6"/>
      </g>
    </svg>
  </button>
</template>

<script setup>
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import { useLanguageStore } from '../stores/language'
import { useAuthStore } from '../stores/auth'

const { locale } = useI18n()
const languageStore = useLanguageStore()
const authStore = useAuthStore()

const currentLocale = computed(() => languageStore.currentLocale)

const toggleLanguage = async () => {
  const newLocale = currentLocale.value === 'en' ? 'pl' : 'en'
  locale.value = newLocale
  await languageStore.setLocale(newLocale, authStore.isAuthenticated)
}
</script>
