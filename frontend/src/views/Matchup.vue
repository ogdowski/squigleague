<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import axios from 'axios'
import Navbar from '@/components/Navbar.vue'

const router = useRouter()
const authStore = useAuthStore()

const gameSystem = ref('age_of_sigmar')
const loading = ref(false)
const recentMatchups = ref([])

const gameSystems = [
  { value: 'age_of_sigmar', label: 'Age of Sigmar' },
  { value: 'warhammer_40k', label: 'Warhammer 40,000' },
  { value: 'the_old_world', label: 'The Old World' }
]

async function createMatchup() {
  loading.value = true
  
  try {
    const response = await axios.post('/api/matchup/create', {
      game_system: gameSystem.value
    }, {
      headers: { Authorization: `Bearer ${authStore.token}` }
    })

    router.push(`/matchup/${response.data.uuid}`)
  } catch (error) {
    console.error('Failed to create matchup:', error)
    alert('Failed to create matchup. Please try again.')
  } finally {
    loading.value = false
  }
}

async function loadRecentMatchups() {
  try {
    const response = await axios.get('/api/matchup/my-matchups', {
      headers: { Authorization: `Bearer ${authStore.token}` }
    })
    recentMatchups.value = response.data
  } catch (error) {
    console.error('Failed to load recent matchups:', error)
  }
}

onMounted(() => {
  loadRecentMatchups()
})

function formatDate(dateString) {
  return new Date(dateString).toLocaleString()
}
</script>

<template>
  <div class="min-h-screen bg-background-light dark:bg-background-dark">
    <Navbar />
    
    <div class="max-w-4xl mx-auto px-4 py-8">
      <div class="card mb-8">
        <h1 class="text-3xl font-bold text-primary mb-4">Create New Matchup</h1>
        <p class="text-gray-600 dark:text-gray-400 mb-6">
          Generate a blind matchup with randomized battle plan and deployment
        </p>

        <div class="space-y-4">
          <div>
            <label class="block text-sm font-medium mb-2">Game System</label>
            <select v-model="gameSystem" class="input-field w-full">
              <option v-for="system in gameSystems" :key="system.value" :value="system.value">
                {{ system.label }}
              </option>
            </select>
          </div>

          <button 
            @click="createMatchup"
            :disabled="loading"
            class="btn-primary w-full"
          >
            {{ loading ? 'Creating...' : 'Create Matchup' }}
          </button>
        </div>
      </div>

      <div class="card">
        <h2 class="text-2xl font-bold mb-4">Recent Matchups</h2>
        
        <div v-if="recentMatchups.length === 0" class="text-gray-600 dark:text-gray-400 text-center py-8">
          No matchups yet. Create your first one above!
        </div>

        <div v-else class="space-y-3">
          <div 
            v-for="matchup in recentMatchups" 
            :key="matchup.uuid"
            class="p-4 bg-background-light dark:bg-background-dark rounded-lg hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors cursor-pointer"
            @click="router.push(`/matchup/${matchup.uuid}`)"
          >
            <div class="flex justify-between items-start">
              <div>
                <div class="font-semibold">
                  {{ matchup.game_system.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase()) }}
                </div>
                <div class="text-sm text-gray-600 dark:text-gray-400">
                  {{ formatDate(matchup.created_at) }}
                </div>
                <div v-if="matchup.opponent_name" class="text-sm text-primary mt-1">
                  vs {{ matchup.opponent_name }}
                </div>
              </div>
              <div>
                <span 
                  v-if="matchup.is_complete" 
                  class="px-3 py-1 bg-green-500 bg-opacity-20 text-green-500 rounded-full text-sm"
                >
                  Complete
                </span>
                <span 
                  v-else 
                  class="px-3 py-1 bg-yellow-500 bg-opacity-20 text-yellow-500 rounded-full text-sm"
                >
                  Waiting
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
