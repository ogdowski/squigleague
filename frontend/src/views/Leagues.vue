<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import axios from 'axios'
import Navbar from '@/components/Navbar.vue'

const router = useRouter()
const authStore = useAuthStore()

const leagues = ref([])
const loading = ref(true)

async function loadLeagues() {
  loading.value = true
  
  try {
    const response = await axios.get('/api/leagues')
    leagues.value = response.data
  } catch (error) {
    console.error('Failed to load leagues:', error)
  } finally {
    loading.value = false
  }
}

function viewLeague(leagueId) {
  router.push(`/leagues/${leagueId}`)
}

onMounted(() => {
  loadLeagues()
})

function formatDate(dateString) {
  if (!dateString) return 'TBD'
  return new Date(dateString).toLocaleDateString()
}
</script>

<template>
  <div class="min-h-screen bg-background-light dark:bg-background-dark">
    <Navbar />
    
    <div class="max-w-6xl mx-auto px-4 py-8">
      <div class="card mb-8">
        <h1 class="text-3xl font-bold text-primary mb-4">Leagues</h1>
        <p class="text-gray-600 dark:text-gray-400">
          Join or create competitive leagues with group phase and playoff formats
        </p>
      </div>

      <div v-if="loading" class="text-center py-12">
        <div class="text-xl">Loading leagues...</div>
      </div>

      <div v-else-if="leagues.length === 0" class="card text-center py-12 text-gray-600 dark:text-gray-400">
        No leagues available yet
      </div>

      <div v-else class="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
        <div 
          v-for="league in leagues" 
          :key="league.id"
          class="card hover:shadow-xl transition-shadow cursor-pointer"
          @click="viewLeague(league.id)"
        >
          <div class="mb-4">
            <h3 class="text-xl font-bold mb-2">{{ league.name }}</h3>
            <div class="text-sm text-gray-600 dark:text-gray-400">
              Season {{ league.season }}
            </div>
          </div>

          <div class="space-y-2 text-sm">
            <div class="flex justify-between">
              <span class="text-gray-600 dark:text-gray-400">Format:</span>
              <span class="font-medium">{{ league.format_type.replace(/_/g, ' ') }}</span>
            </div>
            <div class="flex justify-between">
              <span class="text-gray-600 dark:text-gray-400">Status:</span>
              <span 
                :class="{
                  'text-green-500': league.status === 'active',
                  'text-yellow-500': league.status === 'registration',
                  'text-blue-500': league.status === 'group_phase',
                  'text-purple-500': league.status === 'playoffs',
                  'text-gray-500': league.status === 'completed'
                }"
                class="font-medium capitalize"
              >
                {{ league.status.replace(/_/g, ' ') }}
              </span>
            </div>
            <div class="flex justify-between">
              <span class="text-gray-600 dark:text-gray-400">Starts:</span>
              <span class="font-medium">{{ formatDate(league.start_date) }}</span>
            </div>
          </div>

          <div class="mt-4 pt-4 border-t border-gray-300 dark:border-gray-600">
            <button class="btn-primary w-full text-sm">
              View Details
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
