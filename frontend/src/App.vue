<template>
  <div id="app" class="min-h-screen">
    <nav class="bg-gray-800 border-b border-gray-700">
      <div class="container mx-auto px-4 py-4">
        <div class="flex items-center justify-between">
          <router-link to="/" class="text-2xl font-bold text-squig-yellow">
            Squig League
          </router-link>

          <div class="flex items-center gap-4">
            <router-link
              to="/matchup/create"
              class="btn-secondary"
            >
              Create Matchup
            </router-link>

            <div v-if="authStore.isAuthenticated" class="flex items-center gap-4">
              <router-link to="/my-matchups" class="btn-secondary">
                My Matchups
              </router-link>
              <router-link to="/settings" class="btn-secondary">
                Settings
              </router-link>
              <span class="text-gray-300">{{ authStore.user?.username }}</span>
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

    <main class="container mx-auto px-4 py-8">
      <router-view />
    </main>
  </div>
</template>

<script setup>
import { onMounted } from 'vue'
import { useAuthStore } from './stores/auth'

const authStore = useAuthStore()

onMounted(() => {
  authStore.initAuth()
})
</script>
