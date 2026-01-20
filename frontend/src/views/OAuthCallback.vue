<template>
  <div class="max-w-md mx-auto">
    <div class="card text-center">
      <div v-if="loading" class="py-12">
        <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-squig-yellow mx-auto mb-4"></div>
        <h2 class="text-xl font-bold mb-2">Completing {{ provider }} login...</h2>
        <p class="text-gray-400">Please wait</p>
      </div>

      <div v-else-if="error" class="py-12">
        <div class="text-red-500 mb-4">
          <svg class="w-16 h-16 mx-auto" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
          </svg>
        </div>
        <h2 class="text-xl font-bold mb-2">Login Failed</h2>
        <p class="text-gray-400 mb-6">{{ error }}</p>
        <router-link to="/login" class="btn-primary inline-block">
          Back to Login
        </router-link>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()

const loading = ref(true)
const error = ref('')
const provider = ref('')

onMounted(async () => {
  try {
    const token = route.query.token
    provider.value = route.query.provider || 'OAuth'

    if (!token) {
      throw new Error('No authentication token received')
    }

    // Store the token and fetch user info
    localStorage.setItem('token', token)

    // Set token in auth store
    authStore.token = token

    // Initialize auth (sets axios headers)
    authStore.initAuth()

    // Check for stored redirect URL
    const redirectUrl = sessionStorage.getItem('auth_redirect') || '/'
    sessionStorage.removeItem('auth_redirect')

    // Redirect to stored URL or home
    setTimeout(() => {
      router.push(redirectUrl)
    }, 500)
  } catch (err) {
    loading.value = false
    error.value = err.message || 'Failed to complete OAuth login'
  }
})
</script>
