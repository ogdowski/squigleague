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
              <!-- User dropdown -->
              <div class="relative">
                <button
                  @click="showUserMenu = !showUserMenu"
                  class="btn-secondary flex items-center gap-2"
                >
                  <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                  </svg>
                  {{ authStore.user?.username }}
                  <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
                  </svg>
                </button>
                <div
                  v-if="showUserMenu"
                  class="absolute right-0 top-full mt-2 w-48 bg-gray-800 border border-gray-700 rounded-lg shadow-xl z-30"
                >
                  <router-link
                    :to="`/player/${authStore.user?.id}`"
                    @click="showUserMenu = false"
                    class="flex items-center gap-2 px-4 py-2 hover:bg-gray-700 rounded-t-lg"
                  >
                    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                    </svg>
                    Profile
                  </router-link>
                  <router-link
                    to="/settings"
                    @click="showUserMenu = false"
                    class="flex items-center gap-2 px-4 py-2 hover:bg-gray-700"
                  >
                    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                    </svg>
                    Settings
                  </router-link>
                  <button
                    @click="authStore.logout(); showUserMenu = false"
                    class="flex items-center gap-2 w-full text-left px-4 py-2 hover:bg-gray-700 rounded-b-lg text-red-400"
                  >
                    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
                    </svg>
                    Logout
                  </button>
                </div>
              </div>
              <!-- Click outside to close -->
              <div v-if="showUserMenu" @click="showUserMenu = false" class="fixed inset-0 z-20"></div>
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
            <span>{{ stats.leagues_created }} leagues</span>
            <span>•</span>
            <span>{{ stats.exchanges_completed }} exchanges</span>
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
const showUserMenu = ref(false)

const API_URL = import.meta.env.VITE_API_URL || '/api'

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
