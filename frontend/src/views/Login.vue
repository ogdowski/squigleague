<script setup>
import { ref } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useThemeStore } from '@/stores/theme'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()
const themeStore = useThemeStore()

const isLogin = ref(true)
const username = ref('')
const password = ref('')
const email = ref('')
const displayName = ref('')
const error = ref('')
const loading = ref(false)

async function handleLogin() {
  error.value = ''
  loading.value = true

  const result = await authStore.login({
    username: username.value,
    password: password.value
  })

  loading.value = false

  if (result.success) {
    const redirect = route.query.redirect || '/'
    router.push(redirect)
  } else {
    error.value = result.error
  }
}

async function handleRegister() {
  error.value = ''
  loading.value = true

  const result = await authStore.register({
    username: username.value,
    password: password.value,
    email: email.value,
    display_name: displayName.value
  })

  loading.value = false

  if (result.success) {
    error.value = ''
    isLogin.value = true
    username.value = ''
    password.value = ''
    email.value = ''
    displayName.value = ''
  } else {
    error.value = result.error
  }
}

function handleOAuthLogin(provider) {
  const redirectUri = `${window.location.origin}/auth/callback/${provider}`
  const clientId = provider === 'google' 
    ? import.meta.env.VITE_GOOGLE_CLIENT_ID 
    : import.meta.env.VITE_DISCORD_CLIENT_ID

  let authUrl = ''
  
  if (provider === 'google') {
    authUrl = `https://accounts.google.com/o/oauth2/v2/auth?client_id=${clientId}&redirect_uri=${redirectUri}&response_type=code&scope=openid%20email%20profile`
  } else if (provider === 'discord') {
    authUrl = `https://discord.com/api/oauth2/authorize?client_id=${clientId}&redirect_uri=${redirectUri}&response_type=code&scope=identify%20email`
  }

  window.location.href = authUrl
}

function toggleMode() {
  isLogin.value = !isLogin.value
  error.value = ''
}
</script>

<template>
  <div class="min-h-screen flex items-center justify-center bg-background-light dark:bg-background-dark">
    <div class="card w-full max-w-md">
      <div class="flex justify-between items-center mb-6">
        <h1 class="text-3xl font-bold text-primary">SquigLeague</h1>
        <button 
          @click="themeStore.toggleTheme" 
          class="p-2 rounded-lg hover:bg-gray-200 dark:hover:bg-gray-700 transition-colors"
          :title="themeStore.isDark ? 'Switch to Light Mode' : 'Switch to Dark Mode'"
        >
          <svg v-if="themeStore.isDark" class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 3v1m0 16v1m9-9h-1M4 12H3m15.364 6.364l-.707-.707M6.343 6.343l-.707-.707m12.728 0l-.707.707M6.343 17.657l-.707.707M16 12a4 4 0 11-8 0 4 4 0 018 0z" />
          </svg>
          <svg v-else class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20.354 15.354A9 9 0 018.646 3.646 9.003 9.003 0 0012 21a9.003 9.003 0 008.354-5.646z" />
          </svg>
        </button>
      </div>

      <h2 class="text-2xl font-semibold mb-6">
        {{ isLogin ? 'Login' : 'Register' }}
      </h2>

      <div v-if="error" class="bg-red-500 bg-opacity-10 border border-red-500 text-red-500 px-4 py-3 rounded-lg mb-4">
        {{ error }}
      </div>

      <form @submit.prevent="isLogin ? handleLogin() : handleRegister()" class="space-y-4">
        <div v-if="!isLogin">
          <label class="block text-sm font-medium mb-2">Display Name</label>
          <input 
            v-model="displayName" 
            type="text" 
            required 
            class="input-field w-full"
            placeholder="Enter your display name"
          />
        </div>

        <div v-if="!isLogin">
          <label class="block text-sm font-medium mb-2">Email</label>
          <input 
            v-model="email" 
            type="email" 
            required 
            class="input-field w-full"
            placeholder="Enter your email"
          />
        </div>

        <div>
          <label class="block text-sm font-medium mb-2">Username</label>
          <input 
            v-model="username" 
            type="text" 
            required 
            class="input-field w-full"
            placeholder="Enter your username"
          />
        </div>

        <div>
          <label class="block text-sm font-medium mb-2">Password</label>
          <input 
            v-model="password" 
            type="password" 
            required 
            class="input-field w-full"
            placeholder="Enter your password"
          />
        </div>

        <button 
          type="submit" 
          :disabled="loading"
          class="btn-primary w-full"
        >
          {{ loading ? 'Processing...' : (isLogin ? 'Login' : 'Register') }}
        </button>
      </form>

      <div class="mt-6">
        <div class="relative">
          <div class="absolute inset-0 flex items-center">
            <div class="w-full border-t border-gray-300 dark:border-gray-600"></div>
          </div>
          <div class="relative flex justify-center text-sm">
            <span class="px-2 bg-surface-light dark:bg-surface-dark">Or continue with</span>
          </div>
        </div>

        <div class="mt-4 grid grid-cols-2 gap-3">
          <button 
            @click="handleOAuthLogin('google')"
            class="btn-secondary flex items-center justify-center gap-2"
          >
            <svg class="w-5 h-5" viewBox="0 0 24 24">
              <path fill="currentColor" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"/>
              <path fill="currentColor" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"/>
              <path fill="currentColor" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"/>
              <path fill="currentColor" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"/>
            </svg>
            Google
          </button>

          <button 
            @click="handleOAuthLogin('discord')"
            class="btn-secondary flex items-center justify-center gap-2"
          >
            <svg class="w-5 h-5" viewBox="0 0 24 24">
              <path fill="currentColor" d="M20.317 4.37a19.791 19.791 0 0 0-4.885-1.515a.074.074 0 0 0-.079.037c-.21.375-.444.864-.608 1.25a18.27 18.27 0 0 0-5.487 0a12.64 12.64 0 0 0-.617-1.25a.077.077 0 0 0-.079-.037A19.736 19.736 0 0 0 3.677 4.37a.07.07 0 0 0-.032.027C.533 9.046-.32 13.58.099 18.057a.082.082 0 0 0 .031.057a19.9 19.9 0 0 0 5.993 3.03a.078.078 0 0 0 .084-.028a14.09 14.09 0 0 0 1.226-1.994a.076.076 0 0 0-.041-.106a13.107 13.107 0 0 1-1.872-.892a.077.077 0 0 1-.008-.128a10.2 10.2 0 0 0 .372-.292a.074.074 0 0 1 .077-.01c3.928 1.793 8.18 1.793 12.062 0a.074.074 0 0 1 .078.01c.12.098.246.198.373.292a.077.077 0 0 1-.006.127a12.299 12.299 0 0 1-1.873.892a.077.077 0 0 0-.041.107c.36.698.772 1.362 1.225 1.993a.076.076 0 0 0 .084.028a19.839 19.839 0 0 0 6.002-3.03a.077.077 0 0 0 .032-.054c.5-5.177-.838-9.674-3.549-13.66a.061.061 0 0 0-.031-.03zM8.02 15.33c-1.183 0-2.157-1.085-2.157-2.419c0-1.333.956-2.419 2.157-2.419c1.21 0 2.176 1.096 2.157 2.42c0 1.333-.956 2.418-2.157 2.418zm7.975 0c-1.183 0-2.157-1.085-2.157-2.419c0-1.333.955-2.419 2.157-2.419c1.21 0 2.176 1.096 2.157 2.42c0 1.333-.946 2.418-2.157 2.418z"/>
            </svg>
            Discord
          </button>
        </div>
      </div>

      <div class="mt-6 text-center">
        <button 
          @click="toggleMode" 
          class="text-primary hover:text-primary-dark transition-colors"
        >
          {{ isLogin ? "Don't have an account? Register" : "Already have an account? Login" }}
        </button>
      </div>
    </div>
  </div>
</template>
