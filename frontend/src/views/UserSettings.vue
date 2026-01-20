<template>
  <div class="max-w-2xl mx-auto">
    <div class="card">
      <h1 class="text-3xl font-bold mb-6">Settings</h1>

      <div v-if="loading" class="text-center py-12">
        <p class="text-xl text-gray-300">Loading...</p>
      </div>

      <div v-else>
        <form @submit.prevent="updateSettings" class="space-y-6">
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

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'
const authStore = useAuthStore()

const loading = ref(true)
const submitting = ref(false)
const error = ref('')
const success = ref(false)

const formData = ref({
  email: '',
  username: '',
})

const originalData = ref({
  email: '',
  username: '',
})

const hasChanges = computed(() => {
  return formData.value.username !== originalData.value.username ||
         formData.value.email !== originalData.value.email
})

const loadUserData = async () => {
  try {
    const response = await axios.get(`${API_URL}/auth/me`)
    formData.value.email = response.data.email
    formData.value.username = response.data.username
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
    const updateData = {}
    if (formData.value.username !== originalData.value.username) {
      updateData.username = formData.value.username
    }
    if (formData.value.email !== originalData.value.email) {
      updateData.email = formData.value.email
    }

    const response = await axios.patch(`${API_URL}/auth/me`, updateData)

    authStore.user.username = response.data.username
    authStore.user.email = response.data.email
    originalData.value.username = response.data.username
    originalData.value.email = response.data.email
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
  error.value = ''
  success.value = false
}

onMounted(() => {
  loadUserData()
})
</script>
