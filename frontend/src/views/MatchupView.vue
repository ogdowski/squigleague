<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import axios from 'axios'
import Navbar from '@/components/Navbar.vue'

const route = useRoute()
const authStore = useAuthStore()

const matchupId = route.params.id
const matchupData = ref(null)
const loading = ref(true)
const submitting = ref(false)
const error = ref('')

const playerName = ref('')
const armyList = ref('')

const isRevealed = computed(() => matchupData.value?.is_complete)
const canSubmit = computed(() => !isRevealed.value && playerName.value && armyList.value)

async function loadMatchup() {
  loading.value = true
  error.value = ''
  
  try {
    const response = await axios.get(`/api/matchup/${matchupId}`, {
      headers: { Authorization: `Bearer ${authStore.token}` }
    })
    matchupData.value = response.data
  } catch (err) {
    console.error('Failed to load matchup:', err)
    error.value = err.response?.data?.detail || 'Failed to load matchup'
  } finally {
    loading.value = false
  }
}

async function submitList() {
  if (!canSubmit.value) return
  
  submitting.value = true
  error.value = ''
  
  try {
    await axios.post(`/api/matchup/${matchupId}/submit`, {
      player_name: playerName.value,
      army_list: armyList.value
    }, {
      headers: { Authorization: `Bearer ${authStore.token}` }
    })
    
    await loadMatchup()
    
    playerName.value = ''
    armyList.value = ''
  } catch (err) {
    console.error('Failed to submit list:', err)
    error.value = err.response?.data?.detail || 'Failed to submit list'
  } finally {
    submitting.value = false
  }
}

function copyShareUrl() {
  const url = `${window.location.origin}/matchup/${matchupId}`
  navigator.clipboard.writeText(url)
  alert('Share URL copied to clipboard!')
}

onMounted(() => {
  loadMatchup()
})

function formatDate(dateString) {
  return new Date(dateString).toLocaleString()
}
</script>

<template>
  <div class="min-h-screen bg-background-light dark:bg-background-dark">
    <Navbar />
    
    <div class="max-w-6xl mx-auto px-4 py-8">
      <div v-if="loading" class="text-center py-12">
        <div class="text-xl">Loading matchup...</div>
      </div>

      <div v-else-if="error" class="card">
        <div class="text-red-500 text-center py-8">{{ error }}</div>
      </div>

      <div v-else>
        <div class="card mb-6">
          <div class="flex justify-between items-start mb-4">
            <div>
              <h1 class="text-3xl font-bold text-primary mb-2">Matchup</h1>
              <div class="text-gray-600 dark:text-gray-400">
                {{ matchupData.game_system.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase()) }}
              </div>
            </div>
            <button @click="copyShareUrl" class="btn-secondary">
              Copy Share URL
            </button>
          </div>

          <div class="grid grid-cols-2 gap-4 text-sm">
            <div>
              <span class="font-medium">Created:</span> {{ formatDate(matchupData.created_at) }}
            </div>
            <div>
              <span class="font-medium">Expires:</span> {{ formatDate(matchupData.expires_at) }}
            </div>
          </div>

          <div class="mt-4 flex gap-4">
            <div class="flex-1">
              <div class="font-medium mb-1">Player 1</div>
              <span 
                :class="matchupData.player1_submitted ? 'text-green-500' : 'text-gray-400'"
              >
                {{ matchupData.player1_submitted ? '✓ Submitted' : '○ Waiting' }}
              </span>
            </div>
            <div class="flex-1">
              <div class="font-medium mb-1">Player 2</div>
              <span 
                :class="matchupData.player2_submitted ? 'text-green-500' : 'text-gray-400'"
              >
                {{ matchupData.player2_submitted ? '✓ Submitted' : '○ Waiting' }}
              </span>
            </div>
          </div>
        </div>

        <div v-if="!isRevealed" class="card">
          <h2 class="text-2xl font-bold mb-4">Submit Your List</h2>
          
          <div class="space-y-4">
            <div>
              <label class="block text-sm font-medium mb-2">Player Name</label>
              <input 
                v-model="playerName" 
                type="text" 
                class="input-field w-full"
                placeholder="Enter your name"
              />
            </div>

            <div>
              <label class="block text-sm font-medium mb-2">Army List</label>
              <textarea 
                v-model="armyList" 
                rows="10"
                class="input-field w-full font-mono text-sm"
                placeholder="Paste your army list here..."
              ></textarea>
            </div>

            <button 
              @click="submitList"
              :disabled="!canSubmit || submitting"
              class="btn-primary w-full"
            >
              {{ submitting ? 'Submitting...' : 'Submit List' }}
            </button>
          </div>
        </div>

        <div v-else class="space-y-6">
          <div class="card">
            <h2 class="text-2xl font-bold mb-4">Battle Plan</h2>
            <div class="space-y-3">
              <div>
                <span class="font-medium">Map:</span> {{ matchupData.map_name }}
              </div>
              <div>
                <span class="font-medium">Battle Plan:</span> {{ matchupData.battle_plan.name }}
              </div>
              <div>
                <span class="font-medium">Deployment:</span> {{ matchupData.battle_plan.deployment }}
              </div>
              <div class="text-sm text-gray-600 dark:text-gray-400">
                {{ matchupData.battle_plan.deployment_description }}
              </div>
              <div>
                <span class="font-medium">Primary Objective:</span> {{ matchupData.battle_plan.primary_objective }}
              </div>
              <div>
                <span class="font-medium">Turn Limit:</span> {{ matchupData.battle_plan.turn_limit }}
              </div>
            </div>
          </div>

          <div class="grid md:grid-cols-2 gap-6">
            <div class="card">
              <h3 class="text-xl font-bold mb-3">{{ matchupData.player1_name }}</h3>
              <div class="text-sm text-gray-600 dark:text-gray-400 mb-2">
                Submitted: {{ formatDate(matchupData.player1_submitted_at) }}
              </div>
              <pre class="bg-background-light dark:bg-background-dark p-4 rounded-lg overflow-auto text-sm whitespace-pre-wrap">{{ matchupData.player1_list }}</pre>
            </div>

            <div class="card">
              <h3 class="text-xl font-bold mb-3">{{ matchupData.player2_name }}</h3>
              <div class="text-sm text-gray-600 dark:text-gray-400 mb-2">
                Submitted: {{ formatDate(matchupData.player2_submitted_at) }}
              </div>
              <pre class="bg-background-light dark:bg-background-dark p-4 rounded-lg overflow-auto text-sm whitespace-pre-wrap">{{ matchupData.player2_list }}</pre>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
