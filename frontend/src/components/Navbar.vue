<script setup>
import { RouterLink, useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import ThemeToggle from './ThemeToggle.vue'

const router = useRouter()
const authStore = useAuthStore()

function handleLogout() {
  authStore.logout()
  router.push('/login')
}
</script>

<template>
  <nav class="bg-surface-light dark:bg-surface-dark shadow-lg">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
      <div class="flex justify-between h-16">
        <div class="flex">
          <div class="flex-shrink-0 flex items-center">
            <RouterLink to="/" class="text-2xl font-bold text-primary">
              SquigLeague
            </RouterLink>
          </div>
          <div class="hidden sm:ml-6 sm:flex sm:space-x-8">
            <RouterLink 
              to="/matchup" 
              class="inline-flex items-center px-1 pt-1 border-b-2 border-transparent hover:border-primary text-sm font-medium transition-colors"
              active-class="border-primary"
            >
              Matchup
            </RouterLink>
            <RouterLink 
              to="/leagues" 
              class="inline-flex items-center px-1 pt-1 border-b-2 border-transparent hover:border-primary text-sm font-medium transition-colors"
              active-class="border-primary"
            >
              Leagues
            </RouterLink>
            <RouterLink 
              to="/leaderboard" 
              class="inline-flex items-center px-1 pt-1 border-b-2 border-transparent hover:border-primary text-sm font-medium transition-colors"
              active-class="border-primary"
            >
              Leaderboard
            </RouterLink>
          </div>
        </div>
        <div class="flex items-center gap-4">
          <ThemeToggle />
          <RouterLink 
            to="/settings" 
            class="text-sm font-medium hover:text-primary transition-colors"
          >
            Settings
          </RouterLink>
          <button 
            @click="handleLogout"
            class="btn-secondary text-sm"
          >
            Logout
          </button>
        </div>
      </div>
    </div>
  </nav>
</template>
