<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'
import Navbar from '@/components/Navbar.vue'

const ratingType = ref('global')
const leaderboard = ref([])
const loading = ref(true)

const ratingTypes = [
  { value: 'global', label: 'Global ELO' },
  { value: 'league', label: 'League ELO' },
  { value: 'tournament', label: 'Tournament ELO' }
]

async function loadLeaderboard() {
  loading.value = true
  
  try {
    const response = await axios.get(`/api/elo/leaderboard/${ratingType.value}`)
    leaderboard.value = response.data
  } catch (error) {
    console.error('Failed to load leaderboard:', error)
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  loadLeaderboard()
})

function getRatingColor(rating) {
  if (rating >= 1400) return 'text-purple-500'
  if (rating >= 1200) return 'text-blue-500'
  if (rating >= 1000) return 'text-green-500'
  if (rating >= 800) return 'text-yellow-500'
  return 'text-gray-500'
}
</script>

<template>
  <div class="min-h-screen bg-background-light dark:bg-background-dark">
    <Navbar />
    
    <div class="max-w-5xl mx-auto px-4 py-8">
      <div class="card mb-6">
        <h1 class="text-3xl font-bold text-primary mb-4">Leaderboard</h1>
        
        <div class="flex gap-4">
          <button 
            v-for="type in ratingTypes" 
            :key="type.value"
            @click="ratingType = type.value; loadLeaderboard()"
            :class="[
              'px-4 py-2 rounded-lg transition-colors',
              ratingType === type.value 
                ? 'bg-primary text-gray-900 font-semibold' 
                : 'bg-surface-light dark:bg-surface-dark hover:bg-gray-300 dark:hover:bg-gray-700'
            ]"
          >
            {{ type.label }}
          </button>
        </div>
      </div>

      <div class="card">
        <div v-if="loading" class="text-center py-12">
          Loading leaderboard...
        </div>

        <div v-else-if="leaderboard.length === 0" class="text-center py-12 text-gray-600 dark:text-gray-400">
          No ratings yet for {{ ratingTypes.find(t => t.value === ratingType).label }}
        </div>

        <div v-else class="overflow-x-auto">
          <table class="w-full">
            <thead class="border-b-2 border-primary">
              <tr class="text-left">
                <th class="pb-3 font-semibold">Rank</th>
                <th class="pb-3 font-semibold">Player</th>
                <th class="pb-3 font-semibold text-center">Rating</th>
                <th class="pb-3 font-semibold text-center">Games</th>
                <th class="pb-3 font-semibold text-center">Wins</th>
                <th class="pb-3 font-semibold text-center">Draws</th>
                <th class="pb-3 font-semibold text-center">Losses</th>
                <th class="pb-3 font-semibold text-center">Win %</th>
              </tr>
            </thead>
            <tbody>
              <tr 
                v-for="(player, index) in leaderboard" 
                :key="player.user_id"
                class="border-b border-gray-200 dark:border-gray-700 hover:bg-surface-light dark:hover:bg-surface-dark"
              >
                <td class="py-4">
                  <span 
                    v-if="index < 3"
                    class="inline-flex items-center justify-center w-8 h-8 rounded-full font-bold"
                    :class="{
                      'bg-yellow-500 text-gray-900': index === 0,
                      'bg-gray-400 text-gray-900': index === 1,
                      'bg-orange-600 text-white': index === 2
                    }"
                  >
                    {{ index + 1 }}
                  </span>
                  <span v-else class="ml-2">{{ index + 1 }}</span>
                </td>
                <td class="py-4 font-medium">User #{{ player.user_id }}</td>
                <td class="py-4 text-center">
                  <span :class="getRatingColor(player.rating)" class="text-xl font-bold">
                    {{ player.rating }}
                  </span>
                </td>
                <td class="py-4 text-center">{{ player.games_played }}</td>
                <td class="py-4 text-center text-green-500">{{ player.wins }}</td>
                <td class="py-4 text-center text-yellow-500">{{ player.draws }}</td>
                <td class="py-4 text-center text-red-500">{{ player.losses }}</td>
                <td class="py-4 text-center">
                  {{ player.games_played > 0 ? ((player.wins / player.games_played) * 100).toFixed(1) : '0.0' }}%
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  </div>
</template>
