<template>
  <div class="max-w-4xl mx-auto">
    <div v-if="loading" class="text-center py-8">Loading...</div>
    <div v-else-if="error" class="text-red-500 text-center py-8">{{ error }}</div>
    <div v-else-if="profile">
      <!-- Header -->
      <div class="card mb-6">
        <h1 class="text-3xl font-bold mb-2">{{ profile.username }}</h1>
        <div v-if="profile.most_played_army" class="text-gray-400 mb-4">
          Main: {{ profile.most_played_army }}
        </div>

        <!-- Stats Grid -->
        <div class="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
          <div class="bg-gray-700 rounded p-3 text-center">
            <div class="text-2xl font-bold text-squig-yellow">{{ profile.elo }}</div>
            <div class="text-xs text-gray-400">ELO</div>
          </div>
          <div class="bg-gray-700 rounded p-3 text-center">
            <div class="text-2xl font-bold">{{ profile.total_games }}</div>
            <div class="text-xs text-gray-400">Games</div>
          </div>
          <div class="bg-gray-700 rounded p-3 text-center">
            <div class="text-2xl font-bold text-green-400">{{ profile.win_rate }}%</div>
            <div class="text-xs text-gray-400">Win Rate</div>
          </div>
          <div class="bg-gray-700 rounded p-3 text-center">
            <div class="text-2xl font-bold">
              <span class="text-green-400">{{ profile.total_wins }}</span>
              <span class="text-gray-500">/</span>
              <span class="text-yellow-400">{{ profile.total_draws }}</span>
              <span class="text-gray-500">/</span>
              <span class="text-red-400">{{ profile.total_losses }}</span>
            </div>
            <div class="text-xs text-gray-400">W/D/L</div>
          </div>
        </div>

        <!-- Army Stats -->
        <div v-if="profile.army_stats.length > 0">
          <h3 class="text-lg font-semibold mb-3">Armies Played</h3>
          <div class="space-y-2">
            <div v-for="stat in profile.army_stats" :key="stat.army_faction" class="flex items-center gap-3">
              <div class="w-48 text-sm" :title="stat.army_faction">{{ stat.army_faction }}</div>
              <div class="flex-1 bg-gray-700 rounded-full h-4 overflow-hidden">
                <div
                  class="bg-squig-yellow h-full transition-all"
                  :style="{ width: stat.percentage + '%' }"
                ></div>
              </div>
              <div class="w-16 text-right text-sm text-gray-400">
                {{ stat.games_played }} ({{ stat.percentage }}%)
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Leagues -->
      <div v-for="league in profile.leagues" :key="league.league_id" class="card mb-4">
        <div class="flex justify-between items-start mb-4">
          <div class="flex items-center gap-2">
            <span v-if="league.knockout_placement && placementIcon(league.knockout_placement)" class="text-2xl" :title="placementTitle(league.knockout_placement)">
              {{ placementIcon(league.knockout_placement) }}
            </span>
            <div>
              <router-link :to="`/league/${league.league_id}`" class="text-xl font-semibold hover:text-squig-yellow">
                {{ league.league_name }}
              </router-link>
              <span :class="statusClass(league.league_status)" class="ml-2 text-xs px-2 py-1 rounded">
                {{ statusLabel(league.league_status) }}
              </span>
              <span class="ml-2 text-sm" :class="league.knockout_placement ? 'text-squig-yellow' : 'text-gray-500'">
                {{ getLeaguePlacementText(league) }}
              </span>
            </div>
          </div>
          <div class="text-right text-sm text-gray-400">
            {{ league.total_points }} pts (avg: {{ league.average_points }})
          </div>
        </div>

        <!-- League Stats -->
        <div class="flex gap-4 text-sm mb-4">
          <span>Played: {{ league.games_played }}</span>
          <span class="text-green-400">W: {{ league.games_won }}</span>
          <span class="text-yellow-400">D: {{ league.games_drawn }}</span>
          <span class="text-red-400">L: {{ league.games_lost }}</span>
        </div>

        <!-- Matches -->
        <div v-if="league.matches.length > 0">
          <h4 class="text-sm font-medium text-gray-400 mb-2">Recent Matches</h4>
          <div class="space-y-2">
            <router-link
              v-for="match in league.matches.slice(0, 5)"
              :key="match.match_id"
              :to="`/league/${league.league_id}/match/${match.match_id}`"
              class="flex items-center justify-between bg-gray-700 hover:bg-gray-600 rounded px-3 py-2 text-sm cursor-pointer transition-colors"
            >
              <div class="flex items-center gap-2">
                <span :class="resultClass(match.result)" class="w-6 text-center font-bold">
                  {{ resultLetter(match.result) }}
                </span>
                <span>vs {{ match.opponent_username || 'Unknown' }}</span>
                <span v-if="match.phase === 'knockout'" class="text-xs text-purple-400">
                  {{ match.knockout_round }}
                </span>
              </div>
              <div class="text-gray-400">
                <span v-if="match.player_score !== null">
                  {{ match.player_score }} - {{ match.opponent_score }}
                </span>
                <span v-else class="text-xs">{{ match.status }}</span>
              </div>
            </router-link>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import axios from 'axios'

const API_URL = import.meta.env.VITE_API_URL || '/api'
const route = useRoute()

const profile = ref(null)
const loading = ref(true)
const error = ref('')

const fetchProfile = async () => {
  loading.value = true
  error.value = ''
  try {
    const res = await axios.get(`${API_URL}/player/${route.params.userId}/profile`)
    profile.value = res.data
  } catch (err) {
    error.value = err.response?.data?.detail || 'Failed to load profile'
  } finally {
    loading.value = false
  }
}

const statusClass = (status) => ({
  'bg-green-900 text-green-300': status === 'active' || status === 'group_phase',
  'bg-purple-900 text-purple-300': status === 'knockout_phase',
  'bg-yellow-900 text-yellow-300': status === 'registration',
  'bg-gray-700 text-gray-300': status === 'finished',
})

const statusLabel = (status) => {
  const labels = {
    registration: 'Registration',
    active: 'Active',
    group_phase: 'Group Phase',
    knockout_phase: 'Knockout',
    finished: 'Finished',
  }
  return labels[status] || status
}

const resultClass = (result) => ({
  'text-green-400': result === 'win',
  'text-yellow-400': result === 'draw',
  'text-red-400': result === 'loss',
  'text-gray-500': !result,
})

const resultLetter = (result) => {
  if (result === 'win') return 'W'
  if (result === 'draw') return 'D'
  if (result === 'loss') return 'L'
  return '-'
}

// Placement icons - medals only for top 4
const placementIcon = (placement) => {
  if (placement === '1') return '🥇'
  if (placement === '2') return '🥈'
  if (placement === 'top_4') return '🥉'
  return null
}

const placementTitle = (placement) => {
  if (placement === '1') return 'Champion'
  if (placement === '2') return 'Finalist'
  if (placement === 'top_4') return 'Semi-finalist'
  return formatPlacement(placement)
}

const formatPlacement = (placement) => {
  if (placement === '1') return '1st Place'
  if (placement === '2') return '2nd Place'
  if (placement === 'top_4') return 'Top 4'
  if (placement === 'top_8') return 'Top 8'
  if (placement === 'top_16') return 'Top 16'
  if (placement === 'top_32') return 'Top 32'
  return placement
}

const getLeaguePlacementText = (league) => {
  if (league.knockout_placement) {
    return formatPlacement(league.knockout_placement)
  }
  // Show "Group Phase" only for finished leagues without knockout placement
  if (league.league_status === 'finished') {
    return 'Group Phase'
  }
  return ''
}

onMounted(fetchProfile)
</script>
