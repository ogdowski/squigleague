<template>
  <div class="max-w-2xl mx-auto">
    <div class="card">
      <h1 class="text-3xl font-bold mb-6">Settings</h1>

      <div v-if="loading" class="text-center py-12">
        <p class="text-xl text-gray-300">Loading...</p>
      </div>

      <div v-else>
        <form @submit.prevent="updateSettings" class="space-y-6">
          <!-- Avatar Section -->
          <div>
            <label class="block text-sm font-medium mb-2">Avatar</label>
            <div class="flex items-start gap-4">
              <div class="flex flex-col items-center gap-2">
                <div class="w-20 h-20 rounded-full bg-gray-700 overflow-hidden flex-shrink-0">
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
                <label class="btn-secondary text-xs cursor-pointer px-3 py-1">
                  {{ isUploadedAvatar ? 'Change' : 'Upload' }}
                  <input
                    type="file"
                    accept="image/jpeg,image/png,image/gif,image/webp"
                    @change="handleFileSelect"
                    class="hidden"
                  />
                </label>
              </div>
              <div class="flex-1">
                <!-- Show URL input only for external URLs, not for uploaded avatars -->
                <template v-if="!isUploadedAvatar">
                  <input
                    v-model="formData.avatar_url"
                    type="url"
                    class="input-field w-full mb-2"
                    placeholder="https://example.com/avatar.png"
                    :disabled="avatarFile"
                  />
                  <p class="text-xs text-gray-500">
                    Upload an image (max 5MB) or enter a URL.
                    <span v-if="hasDiscordOAuth">Your Discord avatar is used by default.</span>
                  </p>
                </template>
                <template v-else>
                  <p class="text-xs text-gray-500 mb-2">
                    Avatar uploaded. Click "Change" to upload a new one.
                  </p>
                </template>
                <div v-if="avatarFile" class="mt-2 flex items-center gap-2">
                  <span class="text-xs text-green-400">{{ avatarFile.name }}</span>
                  <button type="button" @click="clearAvatarFile" class="text-xs text-red-400 hover:text-red-300">
                    Cancel
                  </button>
                </div>
                <div v-if="uploadingAvatar" class="mt-2 text-xs text-yellow-400">
                  Uploading...
                </div>
              </div>
            </div>
          </div>

          <div>
            <label class="block text-sm font-medium mb-2">
              Email
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
              Username
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
              Discord Username
              <span v-if="hasDiscordOAuth" class="text-gray-500 text-xs ml-2">(managed by Discord)</span>
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
              Your Discord username is automatically synced from your Discord account.
            </p>
          </div>

          <div class="flex items-center gap-3">
            <input
              type="checkbox"
              id="show_email"
              v-model="formData.show_email"
              class="w-4 h-4 rounded border-gray-600 bg-gray-700 text-squig-yellow focus:ring-squig-yellow"
            />
            <label for="show_email" class="text-sm">
              Show email on my public profile
            </label>
          </div>

          <div v-if="error" class="bg-red-900/30 border border-red-500 text-red-200 px-4 py-3 rounded">
            {{ error }}
          </div>

          <div v-if="success" class="bg-green-900/30 border border-green-500 text-green-200 px-4 py-3 rounded">
            Settings updated successfully!
          </div>

          <div class="flex gap-4">
            <button
              type="submit"
              :disabled="submitting || !hasChanges"
              class="btn-primary flex-1"
            >
              {{ submitting ? 'Saving...' : 'Save Changes' }}
            </button>
            <button
              type="button"
              @click="resetForm"
              class="btn-secondary flex-1"
            >
              Reset
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useAuthStore } from '../stores/auth'
import axios from 'axios'

const API_URL = import.meta.env.VITE_API_URL || '/api'
const authStore = useAuthStore()

const loading = ref(true)
const submitting = ref(false)
const error = ref('')
const success = ref(false)
const hasDiscordOAuth = ref(false)

// Avatar upload
const avatarFile = ref(null)
const avatarPreview = ref('')
const uploadingAvatar = ref(false)

const formData = ref({
  email: '',
  username: '',
  discord_username: '',
  show_email: false,
  avatar_url: '',
})

const originalData = ref({
  email: '',
  username: '',
  discord_username: '',
  show_email: false,
  avatar_url: '',
})

const hasChanges = computed(() => {
  return formData.value.username !== originalData.value.username ||
         formData.value.email !== originalData.value.email ||
         formData.value.discord_username !== originalData.value.discord_username ||
         formData.value.show_email !== originalData.value.show_email ||
         formData.value.avatar_url !== originalData.value.avatar_url ||
         avatarFile.value !== null
})

// Check if current avatar is an uploaded file (not external URL)
const isUploadedAvatar = computed(() => {
  return formData.value.avatar_url && formData.value.avatar_url.startsWith('/api/uploads/')
})

const handleFileSelect = (event) => {
  const file = event.target.files[0]
  if (!file) return

  // Validate file size (5MB)
  if (file.size > 5 * 1024 * 1024) {
    error.value = 'File too large. Maximum size is 5MB.'
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
    error.value = err.response?.data?.detail || 'Failed to upload avatar'
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
    hasDiscordOAuth.value = response.data.has_discord_oauth || false
    originalData.value = { ...formData.value }
  } catch (err) {
    error.value = 'Failed to load user data'
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

    // Only make the PATCH request if there are other changes
    if (Object.keys(updateData).length > 0) {
      const response = await axios.patch(`${API_URL}/auth/me`, updateData)
      authStore.user.username = response.data.username
      authStore.user.email = response.data.email
      originalData.value.username = response.data.username
      originalData.value.email = response.data.email
      originalData.value.discord_username = response.data.discord_username || ''
      originalData.value.show_email = response.data.show_email
      originalData.value.avatar_url = response.data.avatar_url || ''
      formData.value.discord_username = response.data.discord_username || ''
      formData.value.show_email = response.data.show_email
      formData.value.avatar_url = response.data.avatar_url || ''
    }

    success.value = true
    setTimeout(() => {
      success.value = false
    }, 3000)
  } catch (err) {
    error.value = err.response?.data?.detail || 'Failed to update settings'
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
})
</script>
