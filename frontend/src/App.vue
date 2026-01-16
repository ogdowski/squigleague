<template>
  <div id="app" class="min-h-screen flex flex-col">
    <nav class="bg-gray-800 border-b border-gray-700">
      <div class="container mx-auto px-4 py-4">
        <div class="flex items-center justify-between">
          <router-link to="/" class="text-2xl font-bold text-squig-yellow">
            Squig League
          </router-link>

          <div class="flex items-center gap-4">
            <router-link to="/leagues" class="btn-secondary">
              Leagues
            </router-link>
            <router-link to="/my-matchups" class="btn-secondary">
              Matchups
            </router-link>

            <div v-if="authStore.isAuthenticated" class="flex items-center gap-4">
              <router-link
                v-if="authStore.user?.role === 'admin'"
                to="/admin/users"
                class="btn-secondary bg-red-900/30 border-red-500 text-red-200"
              >
                Admin
              </router-link>
              <router-link to="/settings" class="btn-secondary">
                {{ authStore.user?.username }}
              </router-link>
              <button @click="authStore.logout()" class="btn-secondary">
                Logout
              </button>
            </div>

            <div v-else class="flex gap-2">
              <router-link to="/login" class="btn-secondary">
                Login
              </router-link>
              <router-link to="/register" class="btn-primary">
                Register
              </router-link>
            </div>
          </div>
        </div>
      </div>
    </nav>

    <main class="container mx-auto px-4 py-8 flex-1">
      <router-view />
    </main>

    <footer class="mt-auto border-t border-gray-700 bg-gray-800 sticky bottom-0">
      <div class="container mx-auto px-4 py-6">
        <div class="flex flex-col md:flex-row justify-between items-center gap-2 text-sm text-gray-400">
          <div>© 2025 Ariel Ogdowski. All Rights Reserved.</div>
          <div v-if="stats" class="flex gap-3">
            <span>v{{ stats.version }}</span>
            <span>•</span>
            <span>{{ stats.exchanges_completed }} exchanges complete</span>
            <span v-if="stats.exchanges_expired > 0">({{ stats.exchanges_expired }} expired)</span>
          </div>
          <div v-else class="flex gap-3">
            <span>Loading...</span>
          </div>
        </div>
      </div>
    </footer>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { useAuthStore } from './stores/auth'
import axios from 'axios'
import packageJson from '../package.json'

const authStore = useAuthStore()
const stats = ref(null)

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api'

const fetchStats = async () => {
  try {
    const response = await axios.get(`${API_URL}/matchup/stats`)
    stats.value = response.data
  } catch (error) {
    console.error('Failed to fetch stats:', error)
    // Fallback to package.json version
    stats.value = {
      version: packageJson.version,
      exchanges_completed: 0,
      exchanges_expired: 0
    }
  }
}

onMounted(() => {
  authStore.initAuth()
  fetchStats()
})
</script>
