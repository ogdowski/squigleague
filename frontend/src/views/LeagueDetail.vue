<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import axios from 'axios'
import Navbar from '@/components/Navbar.vue'

const route = useRoute()
const authStore = useAuthStore()

const leagueId = route.params.id
const league = ref(null)
const standings = ref([])
const loading = ref(true)

async function loadLeague() {
  loading.value = true
  
  try {
    const [leagueRes, standingsRes] = await Promise.all([
      axios.get(`/api/leagues/${leagueId}`),
      axios.get(`/api/leagues/${leagueId}/standings`)
    ])
    
    league.value = leagueRes.data
    standings.value = standingsRes.data
  } catch (error) {
    console.error('Failed to load league:', error)
  } finally {
    loading.value = false
  }
}

async function joinLeague() {
  try {
    await axios.post(`/api/leagues/${leagueId}/join`, {}, {
      headers: { Authorization: `Bearer ${authStore.token}` }
    })
    
    await loadLeague()
    alert('Successfully joined league!')
  } catch (error) {
    console.error('Failed to join league:', error)
    alert(error.response?.data?.detail || 'Failed to join league')
  }
}

onMounted(() => {
  loadLeague()
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
      <div v-if="loading" class="text-center py-12">
        <div class="text-xl">Loading league...</div>
      </div>

      <div v-else-if="league">
        <div class="card mb-6">
          <div class="flex justify-between items-start mb-4">
            <div>
              <h1 class="text-3xl font-bold text-primary mb-2">{{ league.name }}</h1>
              <div class="text-gray-600 dark:text-gray-400">Season {{ league.season }}</div>
            </div>
            <button 
              v-if="league.status === 'registration'"
              @click="joinLeague"
              class="btn-primary"
            >
              Join League
            </button>
          </div>

          <div class="grid md:grid-cols-3 gap-4 text-sm">
            <div>
              <span class="font-medium">Format:</span> {{ league.format_type.replace(/_/g, ' ') }}
            </div>
            <div>
              <span class="font-medium">Status:</span> 
              <span class="capitalize ml-2">{{ league.status.replace(/_/g, ' ') }}</span>
            </div>
            <div>
              <span class="font-medium">Start Date:</span> {{ formatDate(league.start_date) }}
            </div>
          </div>
        </div>

        <div class="card">
          <h2 class="text-2xl font-bold mb-4">Standings</h2>
          
          <div v-if="standings.length === 0" class="text-center py-8 text-gray-600 dark:text-gray-400">
            No standings yet. League has not started.
          </div>

          <div v-else class="overflow-x-auto">
            <table class="w-full">
              <thead class="border-b border-gray-300 dark:border-gray-600">
                <tr class="text-left">
                  <th class="pb-3 font-semibold">Pos</th>
                  <th class="pb-3 font-semibold">Player</th>
                  <th class="pb-3 font-semibold text-center">GP</th>
                  <th class="pb-3 font-semibold text-center">W</th>
                  <th class="pb-3 font-semibold text-center">D</th>
                  <th class="pb-3 font-semibold text-center">L</th>
                  <th class="pb-3 font-semibold text-center">Pts</th>
                </tr>
              </thead>
              <tbody>
                <tr 
                  v-for="(standing, index) in standings" 
                  :key="standing.user_id"
                  class="border-b border-gray-200 dark:border-gray-700 hover:bg-surface-light dark:hover:bg-surface-dark"
                >
                  <td class="py-3">{{ index + 1 }}</td>
                  <td class="py-3 font-medium">User #{{ standing.user_id }}</td>
                  <td class="py-3 text-center">{{ standing.games_played }}</td>
                  <td class="py-3 text-center text-green-500">{{ standing.wins }}</td>
                  <td class="py-3 text-center text-yellow-500">{{ standing.draws }}</td>
                  <td class="py-3 text-center text-red-500">{{ standing.losses }}</td>
                  <td class="py-3 text-center font-bold text-primary">{{ standing.points }}</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
