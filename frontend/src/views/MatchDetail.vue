<template>
  <div class="max-w-4xl mx-auto">
    <div v-if="loading" class="text-center py-12">Loading match...</div>
    <div v-else-if="error" class="card bg-red-900/30 border border-red-500 text-red-200">{{ error }}</div>
    <div v-else-if="match">
      <!-- Header -->
      <div class="card mb-6">
        <div class="flex items-center justify-between mb-4">
          <div>
            <router-link :to="`/league/${match.league_id}`" class="text-squig-yellow hover:underline">
              {{ match.league_name }}
            </router-link>
            <span class="mx-2 text-gray-500">/</span>
            <span class="text-gray-300">
              {{ match.phase === 'knockout' ? formatKnockoutRound(match.knockout_round) : match.group_name }}
            </span>
          </div>
          <span :class="statusClass" class="px-3 py-1 rounded text-sm">{{ statusLabel }}</span>
        </div>

        <!-- Players -->
        <div class="grid md:grid-cols-2 gap-4">
          <!-- Player 1 -->
          <div class="bg-gray-900 p-4 rounded">
            <div class="flex items-center justify-between mb-2">
              <div class="flex items-center gap-3">
                <img
                  v-if="match.player1_avatar"
                  :src="match.player1_avatar"
                  class="w-10 h-10 rounded-full"
                  :alt="match.player1_username"
                />
                <div v-else class="w-10 h-10 rounded-full bg-gray-700 flex items-center justify-center text-gray-400">
                  <svg class="w-6 h-6" fill="currentColor" viewBox="0 0 24 24">
                    <path d="M12 12c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm0 2c-2.67 0-8 1.34-8 4v2h16v-2c0-2.66-5.33-4-8-4z"/>
                  </svg>
                </div>
                <router-link v-if="match.player1_user_id" :to="`/player/${match.player1_user_id}`" class="font-bold text-lg hover:text-squig-yellow">
                  {{ match.player1_username }}
                </router-link>
                <span v-else class="font-bold text-lg">{{ match.player1_username }}</span>
              </div>
              <span v-if="match.player1_army_faction" class="text-sm text-gray-400">{{ match.player1_army_faction }}</span>
            </div>
            <div v-if="match.status === 'confirmed'" class="text-3xl font-bold" :class="p1ScoreClass">
              {{ match.player1_score }}
            </div>
            <div v-if="match.player1_elo_after && match.status === 'confirmed'" class="text-sm mt-2">
              <span class="text-gray-400">ELO:</span>
              <span class="ml-1">{{ match.player1_elo_before }}</span>
              <span class="mx-1">→</span>
              <span :class="match.player1_elo_after > match.player1_elo_before ? 'text-green-400' : 'text-red-400'">
                {{ match.player1_elo_after }}
                ({{ match.player1_elo_after > match.player1_elo_before ? '+' : '' }}{{ match.player1_elo_after - match.player1_elo_before }})
              </span>
            </div>
            <div v-if="match.player1_league_points !== null && match.status === 'confirmed'" class="text-sm mt-1">
              <span class="text-gray-400">League Points:</span>
              <span class="ml-1 text-squig-yellow font-semibold">+{{ match.player1_league_points }}</span>
            </div>
          </div>

          <!-- Player 2 -->
          <div class="bg-gray-900 p-4 rounded">
            <div class="flex items-center justify-between mb-2">
              <div class="flex items-center gap-3">
                <img
                  v-if="match.player2_avatar"
                  :src="match.player2_avatar"
                  class="w-10 h-10 rounded-full"
                  :alt="match.player2_username"
                />
                <div v-else class="w-10 h-10 rounded-full bg-gray-700 flex items-center justify-center text-gray-400">
                  <svg class="w-6 h-6" fill="currentColor" viewBox="0 0 24 24">
                    <path d="M12 12c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm0 2c-2.67 0-8 1.34-8 4v2h16v-2c0-2.66-5.33-4-8-4z"/>
                  </svg>
                </div>
                <router-link v-if="match.player2_user_id" :to="`/player/${match.player2_user_id}`" class="font-bold text-lg hover:text-squig-yellow">
                  {{ match.player2_username }}
                </router-link>
                <span v-else class="font-bold text-lg">{{ match.player2_username }}</span>
              </div>
              <span v-if="match.player2_army_faction" class="text-sm text-gray-400">{{ match.player2_army_faction }}</span>
            </div>
            <div v-if="match.status === 'confirmed'" class="text-3xl font-bold" :class="p2ScoreClass">
              {{ match.player2_score }}
            </div>
            <div v-if="match.player2_elo_after && match.status === 'confirmed'" class="text-sm mt-2">
              <span class="text-gray-400">ELO:</span>
              <span class="ml-1">{{ match.player2_elo_before }}</span>
              <span class="mx-1">→</span>
              <span :class="match.player2_elo_after > match.player2_elo_before ? 'text-green-400' : 'text-red-400'">
                {{ match.player2_elo_after }}
                ({{ match.player2_elo_after > match.player2_elo_before ? '+' : '' }}{{ match.player2_elo_after - match.player2_elo_before }})
              </span>
            </div>
            <div v-if="match.player2_league_points !== null && match.status === 'confirmed'" class="text-sm mt-1">
              <span class="text-gray-400">League Points:</span>
              <span class="ml-1 text-squig-yellow font-semibold">+{{ match.player2_league_points }}</span>
            </div>
          </div>
        </div>
      </div>

      <!-- Map Section -->
      <div class="card mb-6">
        <h2 class="text-xl font-bold mb-4">Map</h2>
        <BattlePlanDisplay
          :map-name="match.map_name"
          :map-image="mapImage"
          :battle-plan="battlePlan"
        />

        <!-- Map controls (when can edit and not confirmed) -->
        <div v-if="match.can_set_map && match.status !== 'confirmed'" class="space-y-3 mt-4">
          <p class="text-sm text-gray-400">{{ match.map_name ? 'Change map:' : 'Select map:' }}</p>
          <div class="flex gap-3">
            <button @click="randomizeMap" :disabled="settingMap" class="btn-primary">
              {{ settingMap ? 'Rolling...' : 'Random Map' }}
            </button>
            <select v-model="selectedMap" class="flex-1 bg-gray-700 border border-gray-600 rounded px-4 py-2">
              <option value="">Select map...</option>
              <option v-for="m in availableMaps" :key="m" :value="m">{{ m }}</option>
            </select>
            <button @click="setMap" :disabled="!selectedMap || settingMap" class="btn-secondary">Set</button>
          </div>
        </div>
      </div>

      <!-- Army Lists -->
      <div v-if="match.player1_army_list || match.player2_army_list" class="card mb-6">
        <h2 class="text-xl font-bold mb-4">Army Lists</h2>
        <div class="grid md:grid-cols-2 gap-6">
          <div v-if="match.player1_army_list">
            <h3 class="font-semibold mb-2">{{ match.player1_username }}</h3>
            <div class="bg-gray-900 p-4 rounded max-h-96 overflow-y-auto">
              <pre class="whitespace-pre-wrap font-mono text-sm text-gray-300">{{ match.player1_army_list }}</pre>
            </div>
          </div>
          <div v-if="match.player2_army_list">
            <h3 class="font-semibold mb-2">{{ match.player2_username }}</h3>
            <div class="bg-gray-900 p-4 rounded max-h-96 overflow-y-auto">
              <pre class="whitespace-pre-wrap font-mono text-sm text-gray-300">{{ match.player2_army_list }}</pre>
            </div>
          </div>
        </div>
      </div>

      <!-- Submit Result (if can edit) -->
      <div v-if="match.can_edit && match.status !== 'confirmed'" class="card mb-6">
        <h2 class="text-xl font-bold mb-4">Submit Result</h2>
        <form @submit.prevent="submitResult" class="space-y-4">
          <div class="grid grid-cols-2 gap-4">
            <div>
              <label class="block text-sm text-gray-400 mb-1">{{ match.player1_username }} Score</label>
              <input v-model.number="resultForm.player1_score" type="number" min="0" required
                     class="w-full bg-gray-700 border border-gray-600 rounded px-4 py-2" />
            </div>
            <div>
              <label class="block text-sm text-gray-400 mb-1">{{ match.player2_username }} Score</label>
              <input v-model.number="resultForm.player2_score" type="number" min="0" required
                     class="w-full bg-gray-700 border border-gray-600 rounded px-4 py-2" />
            </div>
          </div>
          <div v-if="submitError" class="text-red-400 text-sm">{{ submitError }}</div>
          <button type="submit" :disabled="submitting" class="btn-primary w-full">
            {{ submitting ? 'Submitting...' : 'Submit Result' }}
          </button>
        </form>
      </div>

      <!-- Match Info -->
      <div class="card">
        <h2 class="text-xl font-bold mb-4">Match Info</h2>
        <div class="grid grid-cols-2 gap-4 text-sm">
          <div>
            <span class="text-gray-400">Phase:</span>
            <span class="ml-2">{{ match.phase === 'knockout' ? 'Knockout' : 'Group' }}</span>
          </div>
          <div v-if="match.deadline">
            <span class="text-gray-400">Deadline:</span>
            <span class="ml-2">{{ formatDate(match.deadline) }}</span>
          </div>
          <div v-if="match.submitted_at">
            <span class="text-gray-400">Result submitted:</span>
            <span class="ml-2">{{ formatDate(match.submitted_at) }}</span>
          </div>
          <div v-if="match.confirmed_at">
            <span class="text-gray-400">Confirmed:</span>
            <span class="ml-2">{{ formatDate(match.confirmed_at) }}</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import axios from 'axios'
import BattlePlanDisplay from '@/components/BattlePlanDisplay.vue'
import { fetchMapsData } from '@/constants/maps'

const API_URL = import.meta.env.VITE_API_URL || '/api'
const route = useRoute()

const match = ref(null)
const loading = ref(true)
const error = ref('')

const selectedMap = ref('')
const settingMap = ref(false)

const resultForm = ref({ player1_score: 0, player2_score: 0 })
const submitting = ref(false)
const submitError = ref('')

// Maps data from API
const mapsData = ref(null)
const availableMaps = computed(() => mapsData.value?.maps || [])
const mapImage = computed(() => {
  if (!match.value?.map_name || !mapsData.value?.images) return null
  return mapsData.value.images[match.value.map_name]
})
const battlePlan = computed(() => {
  if (!match.value?.map_name || !mapsData.value?.battle_plans) return null
  return mapsData.value.battle_plans[match.value.map_name]
})

const fetchMatch = async () => {
  loading.value = true
  error.value = ''
  try {
    const res = await axios.get(`${API_URL}/league/${route.params.leagueId}/matches/${route.params.matchId}`)
    match.value = res.data
  } catch (err) {
    error.value = err.response?.data?.detail || 'Failed to load match'
  } finally {
    loading.value = false
  }
}

const statusClass = computed(() => {
  if (!match.value) return ''
  const s = match.value.status
  if (s === 'confirmed') return 'bg-green-900 text-green-300'
  if (s === 'pending_confirmation') return 'bg-yellow-900 text-yellow-300'
  return 'bg-gray-700 text-gray-300'
})

const statusLabel = computed(() => {
  if (!match.value) return ''
  const labels = {
    scheduled: 'Scheduled',
    pending_confirmation: 'Pending Confirmation',
    confirmed: 'Confirmed',
    disputed: 'Disputed',
  }
  return labels[match.value.status] || match.value.status
})

const p1ScoreClass = computed(() => {
  if (!match.value || match.value.player1_score === null) return ''
  if (match.value.player1_score > match.value.player2_score) return 'text-green-400'
  if (match.value.player1_score < match.value.player2_score) return 'text-red-400'
  return 'text-yellow-400'
})

const p2ScoreClass = computed(() => {
  if (!match.value || match.value.player2_score === null) return ''
  if (match.value.player2_score > match.value.player1_score) return 'text-green-400'
  if (match.value.player2_score < match.value.player1_score) return 'text-red-400'
  return 'text-yellow-400'
})

const formatKnockoutRound = (round) => {
  const labels = {
    final: 'Final',
    semi: 'Semi-Final',
    quarter: 'Quarter-Final',
    round_of_16: 'Round of 16',
    round_of_32: 'Round of 32',
  }
  return labels[round] || round
}

const formatDate = (dateStr) => {
  if (!dateStr) return ''
  return new Date(dateStr).toLocaleString()
}

const randomizeMap = async () => {
  settingMap.value = true
  try {
    const res = await axios.post(`${API_URL}/league/${route.params.leagueId}/matches/${route.params.matchId}/map`, { random: true })
    match.value.map_name = res.data.map_name
  } catch (err) {
    console.error('Failed to randomize map:', err)
  } finally {
    settingMap.value = false
  }
}

const setMap = async () => {
  if (!selectedMap.value) return
  settingMap.value = true
  try {
    const res = await axios.post(`${API_URL}/league/${route.params.leagueId}/matches/${route.params.matchId}/map`, { map_name: selectedMap.value })
    match.value.map_name = res.data.map_name
    selectedMap.value = ''
  } catch (err) {
    console.error('Failed to set map:', err)
  } finally {
    settingMap.value = false
  }
}

const submitResult = async () => {
  submitting.value = true
  submitError.value = ''
  try {
    await axios.post(`${API_URL}/league/${route.params.leagueId}/matches/${route.params.matchId}/result`, resultForm.value)
    await fetchMatch()
  } catch (err) {
    submitError.value = err.response?.data?.detail || 'Failed to submit result'
  } finally {
    submitting.value = false
  }
}

onMounted(async () => {
  mapsData.value = await fetchMapsData()
  await fetchMatch()
})
</script>
