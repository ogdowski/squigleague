<template>
  <div class="max-w-6xl mx-auto">
    <h1 class="text-3xl font-bold mb-6">My Matchups</h1>

    <div v-if="loading" class="text-center py-12">
      <p class="text-xl text-gray-300">Loading matchups...</p>
    </div>

    <div v-else-if="error" class="card">
      <div class="bg-red-900/30 border border-red-500 text-red-200 px-4 py-3 rounded">
        {{ error }}
      </div>
    </div>

    <div v-else-if="matchups.length === 0" class="card text-center py-12">
      <p class="text-xl text-gray-400 mb-4">No matchups yet</p>
      <router-link to="/matchup/create" class="btn-primary inline-block">
        Create Your First Matchup
      </router-link>
    </div>

    <div v-else class="space-y-4">
      <div
        v-for="matchup in matchups"
        :key="matchup.name"
        class="card hover:bg-gray-700 transition-colors cursor-pointer"
        @click="goToMatchup(matchup.name)"
      >
        <div class="flex items-center justify-between">
          <div class="flex-1">
            <h3 class="text-xl font-bold text-squig-yellow mb-2">
              {{ matchup.name }}
            </h3>
            <div class="flex gap-6 text-sm mb-2">
              <div>
                <span class="text-gray-400">Created:</span>
                <span class="text-white ml-2">{{ formatDate(matchup.created_at) }}</span>
              </div>
              <div>
                <span class="text-gray-400">Expires:</span>
                <span class="text-white ml-2">{{ formatDate(matchup.expires_at) }}</span>
              </div>
            </div>
            <div v-if="matchup.player1_username || matchup.player2_username" class="flex gap-4 text-sm">
              <div v-if="matchup.player1_username">
                <span class="text-gray-400">P1:</span>
                <span class="text-squig-yellow ml-1">{{ matchup.player1_username }}</span>
              </div>
              <div v-if="matchup.player2_username">
                <span class="text-gray-400">P2:</span>
                <span class="text-squig-yellow ml-1">{{ matchup.player2_username }}</span>
              </div>
            </div>
          </div>

          <div class="flex items-center gap-4">
            <div class="text-center">
              <div class="text-xs text-gray-400 mb-1">Player 1</div>
              <div :class="matchup.player1_submitted ? 'text-green-400' : 'text-gray-500'">
                {{ matchup.player1_submitted ? '✓' : '○' }}
              </div>
            </div>
            <div class="text-center">
              <div class="text-xs text-gray-400 mb-1">Player 2</div>
              <div :class="matchup.player2_submitted ? 'text-green-400' : 'text-gray-500'">
                {{ matchup.player2_submitted ? '✓' : '○' }}
              </div>
            </div>
            <div
              v-if="matchup.is_revealed"
              class="bg-green-900/30 border border-green-500 text-green-200 px-3 py-1 rounded text-sm"
            >
              Revealed
            </div>
            <div
              v-else
              class="bg-yellow-900/30 border border-yellow-500 text-yellow-200 px-3 py-1 rounded text-sm"
            >
              Pending
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'

const API_URL = import.meta.env.VITE_API_URL || '/api'
const router = useRouter()

const loading = ref(true)
const error = ref('')
const matchups = ref([])

const fetchMatchups = async () => {
  try {
    const response = await axios.get(`${API_URL}/matchup/my-matchups`)
    matchups.value = response.data
  } catch (err) {
    if (err.response?.status === 401) {
      error.value = 'Please log in to view your matchups'
      setTimeout(() => {
        router.push('/login')
      }, 2000)
    } else {
      error.value = 'Failed to load matchups'
    }
  } finally {
    loading.value = false
  }
}

const goToMatchup = (name) => {
  router.push(`/matchup/${name}`)
}

const formatDate = (dateString) => {
  const date = new Date(dateString)
  return date.toLocaleDateString() + ' ' + date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
}

onMounted(() => {
  fetchMatchups()
})
</script>
