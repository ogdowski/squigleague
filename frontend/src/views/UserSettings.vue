<template>
  <div class="max-w-2xl mx-auto">
    <div class="card">
      <h1 class="text-3xl font-bold mb-6">{{ t('settings.title') }}</h1>

      <div v-if="loading" class="text-center py-12">
        <p class="text-xl text-gray-300">{{ t('common.loading') }}</p>
      </div>

      <div v-else>
        <form @submit.prevent="updateSettings" class="space-y-6">
          <!-- Avatar Section -->
          <div>
            <label class="block text-sm font-medium mb-2">{{ t('settings.avatar') }}</label>
            <div class="flex items-center gap-4">
              <!-- Avatar preview -->
              <div class="w-16 h-16 md:w-20 md:h-20 rounded-full bg-gray-700 overflow-hidden flex-shrink-0">
                <img
                  v-if="avatarPreview || formData.avatar_url"
                  :src="avatarPreview || formData.avatar_url"
                  alt="Avatar"
                  class="w-full h-full object-cover"
                  @error="handleAvatarError"
                />
                <div v-else class="w-full h-full flex items-center justify-center text-2xl text-gray-500">
                  {{ formData.username?.charAt(0)?.toUpperCase() || '?' }}
                </div>
              </div>
              <!-- Change button and info -->
              <div class="flex-1 min-w-0">
                <label class="btn-secondary text-sm cursor-pointer px-4 py-2 inline-flex items-center gap-2">
                  <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
                  </svg>
                  {{ t('settings.changeAvatar') }}
                  <input
                    type="file"
                    accept="image/jpeg,image/png,image/gif,image/webp"
                    @change="handleFileSelect"
                    class="hidden"
                  />
                </label>
                <div v-if="avatarFile" class="mt-2 flex items-center gap-2 text-sm">
                  <span class="text-green-400 truncate">{{ avatarFile.name }}</span>
                  <button type="button" @click="clearAvatarFile" class="text-red-400 hover:text-red-300 flex-shrink-0">
                    ✕
                  </button>
                </div>
                <div v-else-if="uploadingAvatar" class="mt-2 text-sm text-yellow-400">
                  {{ t('common.uploading') || 'Uploading...' }}
                </div>
                <p v-else class="mt-2 text-xs text-gray-500">
                  {{ t('settings.avatarUploadNote') }}
                </p>
              </div>
            </div>
            <!-- URL input (collapsed, optional) -->
            <div v-if="!isUploadedAvatar && !avatarFile" class="mt-3">
              <details class="text-sm">
                <summary class="text-gray-400 cursor-pointer hover:text-white">{{ t('settings.useUrlInstead') || 'Or use URL' }}</summary>
                <input
                  v-model="formData.avatar_url"
                  type="url"
                  class="input-field w-full mt-2"
                  placeholder="https://example.com/avatar.png"
                />
              </details>
            </div>
          </div>

          <div>
            <label class="block text-sm font-medium mb-2">
              {{ t('settings.email') }}
            </label>
            <input
              v-model="formData.email"
              type="email"
              class="input-field w-full"
              required
            />
          </div>

          <div>
            <label class="block text-sm font-medium mb-2">
              {{ t('settings.username') }}
            </label>
            <input
              v-model="formData.username"
              type="text"
              class="input-field w-full"
              minlength="3"
              maxlength="100"
              required
            />
          </div>

          <div>
            <label class="block text-sm font-medium mb-2">
              {{ t('settings.discordUsername') }}
              <span v-if="hasDiscordOAuth" class="text-gray-500 text-xs ml-2">{{ t('settings.managedByDiscord') }}</span>
            </label>
            <input
              v-model="formData.discord_username"
              type="text"
              class="input-field w-full"
              :disabled="hasDiscordOAuth"
              :class="{ 'opacity-50 cursor-not-allowed': hasDiscordOAuth }"
              maxlength="100"
              placeholder="e.g. johndoe"
            />
            <p v-if="hasDiscordOAuth" class="text-xs text-gray-500 mt-1">
              {{ t('settings.discordSyncNote') }}
            </p>
          </div>

          <!-- Location -->
          <div class="grid grid-cols-2 gap-4">
            <div>
              <label class="block text-sm font-medium mb-2">{{ t('settings.city') }}</label>
              <input
                v-model="formData.city"
                type="text"
                list="cities-list"
                class="input-field w-full"
                maxlength="100"
                :placeholder="t('settings.cityPlaceholder')"
              />
              <datalist id="cities-list">
                <option v-for="city in cities" :key="city" :value="city" />
              </datalist>
            </div>
            <div>
              <label class="block text-sm font-medium mb-2">{{ t('settings.country') }}</label>
              <input
                v-model="formData.country"
                type="text"
                list="countries-list"
                class="input-field w-full"
                maxlength="100"
                :placeholder="t('settings.countryPlaceholder')"
              />
              <datalist id="countries-list">
                <option v-for="country in countries" :key="country" :value="country" />
              </datalist>
            </div>
          </div>

          <div>
            <div class="flex items-center gap-3">
              <input
                type="checkbox"
                id="show_email"
                v-model="formData.show_email"
                class="w-4 h-4 rounded border-gray-600 bg-gray-700 text-squig-yellow focus:ring-squig-yellow"
              />
              <label for="show_email" class="text-sm">
                {{ t('settings.showEmailOnProfile') }}
              </label>
            </div>
            <p class="text-xs text-gray-500 mt-1">{{ t('settings.organizerEmailNote') }}</p>
          </div>

          <div v-if="!isAdmin" class="flex items-center gap-3">
            <input
              type="checkbox"
              id="wants_organizer"
              v-model="formData.wants_organizer"
              class="w-4 h-4 rounded border-gray-600 bg-gray-700 text-squig-yellow focus:ring-squig-yellow"
            />
            <label for="wants_organizer" class="text-sm">
              {{ t('settings.wantOrganizer') }}
              <span class="text-gray-500 text-xs ml-1">{{ t('settings.organizerNote') }}</span>
            </label>
          </div>

          <!-- Language Preference -->
          <div>
            <label class="block text-sm font-medium mb-2">
              {{ t('settings.language') }}
            </label>
            <div class="flex items-center gap-4">
              <button
                type="button"
                @click="handleLanguageChange('en')"
                class="flex items-center gap-2 px-4 py-2 rounded border transition-all"
                :class="formData.preferred_language === 'en'
                  ? 'border-squig-yellow bg-squig-yellow/10'
                  : 'border-gray-600 hover:border-gray-500'"
              >
                <!-- UK Flag -->
                <svg viewBox="0 0 60 30" class="w-6 h-4">
                  <clipPath id="uk-settings">
                    <path d="M0,0 v30 h60 v-30 z"/>
                  </clipPath>
                  <clipPath id="uk-diag-settings">
                    <path d="M30,15 h30 v15 z v15 h-30 z h-30 v-15 z v-15 h30 z"/>
                  </clipPath>
                  <g clip-path="url(#uk-settings)">
                    <path d="M0,0 v30 h60 v-30 z" fill="#012169"/>
                    <path d="M0,0 L60,30 M60,0 L0,30" stroke="#fff" stroke-width="6"/>
                    <path d="M0,0 L60,30 M60,0 L0,30" clip-path="url(#uk-diag-settings)" stroke="#C8102E" stroke-width="4"/>
                    <path d="M30,0 v30 M0,15 h60" stroke="#fff" stroke-width="10"/>
                    <path d="M30,0 v30 M0,15 h60" stroke="#C8102E" stroke-width="6"/>
                  </g>
                </svg>
                <span>English</span>
              </button>
              <button
                type="button"
                @click="handleLanguageChange('pl')"
                class="flex items-center gap-2 px-4 py-2 rounded border transition-all"
                :class="formData.preferred_language === 'pl'
                  ? 'border-squig-yellow bg-squig-yellow/10'
                  : 'border-gray-600 hover:border-gray-500'"
              >
                <!-- Polish Flag -->
                <svg viewBox="0 0 16 10" class="w-6 h-4">
                  <rect width="16" height="5" fill="#fff"/>
                  <rect y="5" width="16" height="5" fill="#dc143c"/>
                </svg>
                <span>Polski</span>
              </button>
            </div>
            <p class="text-xs text-gray-500 mt-1">
              {{ t('settings.languageNote') }}
            </p>
          </div>

          <div v-if="error" class="bg-red-900/30 border border-red-500 text-red-200 px-4 py-3 rounded">
            {{ error }}
          </div>

          <div v-if="success" class="bg-green-900/30 border border-green-500 text-green-200 px-4 py-3 rounded">
            {{ t('success.settingsUpdated') }}
          </div>

          <div class="flex gap-4">
            <button
              type="submit"
              :disabled="submitting || !hasChanges"
              class="btn-primary w-full py-3"
            >
              {{ submitting ? t('common.saving') : t('common.save') }}
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import { useAuthStore } from '../stores/auth'
import { useLanguageStore } from '../stores/language'
import axios from 'axios'

const { t, locale } = useI18n()
const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'
const authStore = useAuthStore()
const languageStore = useLanguageStore()

const loading = ref(true)
const submitting = ref(false)
const error = ref('')
const success = ref(false)
const hasDiscordOAuth = ref(false)

// Avatar upload
const avatarFile = ref(null)
const avatarPreview = ref('')
const uploadingAvatar = ref(false)

// Location autocomplete
const cities = ref([])
const countries = ref([])

const loadLocations = async () => {
  try {
    const [citiesRes, countriesRes] = await Promise.all([
      axios.get(`${API_URL}/auth/locations/cities`),
      axios.get(`${API_URL}/auth/locations/countries`),
    ])
    cities.value = citiesRes.data
    countries.value = countriesRes.data
  } catch (err) {
    // Silently fail - autocomplete is optional
  }
}

const formData = ref({
  email: '',
  username: '',
  discord_username: '',
  show_email: false,
  avatar_url: '',
  wants_organizer: false,
  preferred_language: 'en',
  city: '',
  country: '',
})

const originalData = ref({
  email: '',
  username: '',
  discord_username: '',
  show_email: false,
  avatar_url: '',
  wants_organizer: false,
  preferred_language: 'en',
  city: '',
  country: '',
})

const isAdmin = computed(() => authStore.user?.role === 'admin')

const hasChanges = computed(() => {
  return formData.value.username !== originalData.value.username ||
         formData.value.email !== originalData.value.email ||
         formData.value.discord_username !== originalData.value.discord_username ||
         formData.value.show_email !== originalData.value.show_email ||
         formData.value.avatar_url !== originalData.value.avatar_url ||
         formData.value.wants_organizer !== originalData.value.wants_organizer ||
         formData.value.preferred_language !== originalData.value.preferred_language ||
         formData.value.city !== originalData.value.city ||
         formData.value.country !== originalData.value.country ||
         avatarFile.value !== null
})

// Check if current avatar is an uploaded file (not external URL)
const isUploadedAvatar = computed(() => {
  return formData.value.avatar_url && formData.value.avatar_url.startsWith('/api/uploads/')
})

const handleLanguageChange = (newLocale) => {
  formData.value.preferred_language = newLocale
  locale.value = newLocale
  languageStore.setLocale(newLocale, false) // Don't persist yet - will happen on save
}

const handleFileSelect = (event) => {
  const file = event.target.files[0]
  if (!file) return

  // Validate file size (20MB - will be resized on server)
  if (file.size > 20 * 1024 * 1024) {
    error.value = t('errors.fileTooLarge')
    return
  }

  avatarFile.value = file
  avatarPreview.value = URL.createObjectURL(file)
}

const clearAvatarFile = () => {
  avatarFile.value = null
  avatarPreview.value = ''
}

const uploadAvatar = async () => {
  if (!avatarFile.value) return true

  uploadingAvatar.value = true
  try {
    const formDataUpload = new FormData()
    formDataUpload.append('file', avatarFile.value)

    const response = await axios.post(`${API_URL}/auth/avatar`, formDataUpload, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })

    // Update the avatar URL with the new one
    formData.value.avatar_url = response.data.avatar_url
    originalData.value.avatar_url = response.data.avatar_url
    clearAvatarFile()
    return true
  } catch (err) {
    error.value = err.response?.data?.detail || t('errors.failedToUploadAvatar')
    return false
  } finally {
    uploadingAvatar.value = false
  }
}

const loadUserData = async () => {
  try {
    const response = await axios.get(`${API_URL}/auth/me`)
    formData.value.email = response.data.email
    formData.value.username = response.data.username
    formData.value.discord_username = response.data.discord_username || ''
    formData.value.show_email = response.data.show_email || false
    formData.value.avatar_url = response.data.avatar_url || ''
    formData.value.wants_organizer = response.data.role === 'organizer'
    formData.value.preferred_language = response.data.preferred_language || 'en'
    formData.value.city = response.data.city || ''
    formData.value.country = response.data.country || ''
    hasDiscordOAuth.value = response.data.has_discord_oauth || false
    originalData.value = { ...formData.value }
    // Sync vue-i18n locale
    locale.value = formData.value.preferred_language
  } catch (err) {
    error.value = t('errors.failedToLoad')
  } finally {
    loading.value = false
  }
}

const updateSettings = async () => {
  if (!hasChanges.value) return

  submitting.value = true
  error.value = ''
  success.value = false

  try {
    // First, upload avatar if a file is selected
    if (avatarFile.value) {
      const uploadSuccess = await uploadAvatar()
      if (!uploadSuccess) {
        submitting.value = false
        return
      }
    }

    const updateData = {}
    if (formData.value.username !== originalData.value.username) {
      updateData.username = formData.value.username
    }
    if (formData.value.email !== originalData.value.email) {
      updateData.email = formData.value.email
    }
    if (!hasDiscordOAuth.value && formData.value.discord_username !== originalData.value.discord_username) {
      updateData.discord_username = formData.value.discord_username || null
    }
    if (formData.value.show_email !== originalData.value.show_email) {
      updateData.show_email = formData.value.show_email
    }
    if (!avatarFile.value && formData.value.avatar_url !== originalData.value.avatar_url) {
      // Only update avatar_url if we didn't just upload a file
      updateData.avatar_url = formData.value.avatar_url || null
    }

    // Add wants_organizer if changed
    if (formData.value.wants_organizer !== originalData.value.wants_organizer) {
      updateData.wants_organizer = formData.value.wants_organizer
    }

    // Add preferred_language if changed
    if (formData.value.preferred_language !== originalData.value.preferred_language) {
      updateData.preferred_language = formData.value.preferred_language
    }

    // Add city and country if changed
    if (formData.value.city !== originalData.value.city) {
      updateData.city = formData.value.city || null
    }
    if (formData.value.country !== originalData.value.country) {
      updateData.country = formData.value.country || null
    }

    // Only make the PATCH request if there are other changes
    if (Object.keys(updateData).length > 0) {
      const response = await axios.patch(`${API_URL}/auth/me`, updateData)
      authStore.user.username = response.data.username
      authStore.user.email = response.data.email
      authStore.user.role = response.data.role
      originalData.value.username = response.data.username
      originalData.value.email = response.data.email
      originalData.value.discord_username = response.data.discord_username || ''
      originalData.value.show_email = response.data.show_email
      originalData.value.avatar_url = response.data.avatar_url || ''
      originalData.value.wants_organizer = response.data.role === 'organizer'
      originalData.value.preferred_language = response.data.preferred_language || 'en'
      originalData.value.city = response.data.city || ''
      originalData.value.country = response.data.country || ''
      formData.value.discord_username = response.data.discord_username || ''
      formData.value.show_email = response.data.show_email
      formData.value.avatar_url = response.data.avatar_url || ''
      formData.value.wants_organizer = response.data.role === 'organizer'
      formData.value.preferred_language = response.data.preferred_language || 'en'
      formData.value.city = response.data.city || ''
      formData.value.country = response.data.country || ''
      // Update language store with saved preference
      languageStore.initFromUser(response.data.preferred_language)
    }

    success.value = true
    setTimeout(() => {
      success.value = false
    }, 3000)
  } catch (err) {
    error.value = err.response?.data?.detail || t('errors.failedToUpdate')
  } finally {
    submitting.value = false
  }
}

const resetForm = () => {
  formData.value = { ...originalData.value }
  clearAvatarFile()
  error.value = ''
  success.value = false
}

const handleAvatarError = (e) => {
  // If image fails to load, clear it
  e.target.style.display = 'none'
}

onMounted(() => {
  loadUserData()
  loadLocations()
})
</script>
