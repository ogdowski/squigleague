<template>
  <div class="flex gap-1">
    <!-- English Flag -->
    <button
      @click="setLanguage('en')"
      class="w-7 h-5 rounded overflow-hidden transition-all"
      :class="currentLocale === 'en' ? 'opacity-100' : 'opacity-40 hover:opacity-70'"
      title="English"
    >
      <svg viewBox="0 0 60 30" class="w-full h-full">
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

    <!-- Polish Flag -->
    <button
      @click="setLanguage('pl')"
      class="w-7 h-5 rounded overflow-hidden transition-all"
      :class="currentLocale === 'pl' ? 'opacity-100' : 'opacity-40 hover:opacity-70'"
      title="Polski"
    >
      <svg viewBox="0 0 16 10" class="w-full h-full">
        <rect width="16" height="5" fill="#fff"/>
        <rect y="5" width="16" height="5" fill="#dc143c"/>
      </svg>
    </button>
  </div>
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

const setLanguage = async (newLocale) => {
  if (newLocale === currentLocale.value) return
  locale.value = newLocale
  await languageStore.setLocale(newLocale, authStore.isAuthenticated)
}
</script>
