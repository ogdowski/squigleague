<template>
  <div class="max-w-4xl mx-auto">
    <div v-if="loading" class="flex justify-center py-8">
      <div class="w-10 h-10 border-4 border-squig-yellow border-t-transparent rounded-full animate-spin"></div>
    </div>
    <div v-else-if="error" class="text-red-500 text-center py-8">{{ error }}</div>
    <div v-else-if="profile">
      <!-- Header -->
      <div class="card mb-6">
        <div class="flex items-start gap-4 mb-4">
          <div v-if="profile.avatar_url" class="w-20 h-20 rounded-full overflow-hidden flex-shrink-0">
            <img :src="profile.avatar_url" :alt="profile.username" class="w-full h-full object-cover" />
          </div>
          <div v-else class="w-20 h-20 rounded-full bg-gray-700 flex items-center justify-center text-3xl text-gray-400 flex-shrink-0">
            {{ profile.username?.charAt(0)?.toUpperCase() || '?' }}
          </div>
          <div class="flex-1">
            <h1 class="text-3xl font-bold mb-1">{{ profile.username }}</h1>
            <div v-if="profile.most_played_army" class="text-gray-400">
              {{ t('profile.main') }}: {{ profile.most_played_army }}
            </div>
          </div>
        </div>

        <!-- Contact Info & Location -->
        <div v-if="profile.email || profile.discord_username || profile.city || profile.country" class="flex flex-wrap gap-4 text-sm text-gray-400 mb-4">
          <a v-if="profile.email" :href="`mailto:${profile.email}`" class="flex items-center gap-1 hover:text-white">
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
            </svg>
            {{ profile.email }}
          </a>
          <span v-if="profile.discord_username" class="flex items-center gap-1">
            <svg class="w-4 h-4" viewBox="0 0 24 24" fill="currentColor">
              <path d="M20.317 4.3698a19.7913 19.7913 0 00-4.8851-1.5152.0741.0741 0 00-.0785.0371c-.211.3753-.4447.8648-.6083 1.2495-1.8447-.2762-3.68-.2762-5.4868 0-.1636-.3933-.4058-.8742-.6177-1.2495a.077.077 0 00-.0785-.037 19.7363 19.7363 0 00-4.8852 1.515.0699.0699 0 00-.0321.0277C.5334 9.0458-.319 13.5799.0992 18.0578a.0824.0824 0 00.0312.0561c2.0528 1.5076 4.0413 2.4228 5.9929 3.0294a.0777.0777 0 00.0842-.0276c.4616-.6304.8731-1.2952 1.226-1.9942a.076.076 0 00-.0416-.1057c-.6528-.2476-1.2743-.5495-1.8722-.8923a.077.077 0 01-.0076-.1277c.1258-.0943.2517-.1923.3718-.2914a.0743.0743 0 01.0776-.0105c3.9278 1.7933 8.18 1.7933 12.0614 0a.0739.0739 0 01.0785.0095c.1202.099.246.1981.3728.2924a.077.077 0 01-.0066.1276 12.2986 12.2986 0 01-1.873.8914.0766.0766 0 00-.0407.1067c.3604.698.7719 1.3628 1.225 1.9932a.076.076 0 00.0842.0286c1.961-.6067 3.9495-1.5219 6.0023-3.0294a.077.077 0 00.0313-.0552c.5004-5.177-.8382-9.6739-3.5485-13.6604a.061.061 0 00-.0312-.0286zM8.02 15.3312c-1.1825 0-2.1569-1.0857-2.1569-2.419 0-1.3332.9555-2.4189 2.157-2.4189 1.2108 0 2.1757 1.0952 2.1568 2.419 0 1.3332-.9555 2.4189-2.1569 2.4189zm7.9748 0c-1.1825 0-2.1569-1.0857-2.1569-2.419 0-1.3332.9554-2.4189 2.1569-2.4189 1.2108 0 2.1757 1.0952 2.1568 2.419 0 1.3332-.946 2.4189-2.1568 2.4189z"/>
            </svg>
            {{ profile.discord_username }}
          </span>
          <span v-if="profile.city || profile.country" class="flex items-center gap-1">
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z"/>
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 11a3 3 0 11-6 0 3 3 0 016 0z"/>
            </svg>
            {{ [profile.city, profile.country].filter(Boolean).join(', ') }}
          </span>
        </div>

        <!-- Stats Grid -->
        <div class="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
          <div class="bg-gray-700 rounded p-3 text-center">
            <div class="text-2xl font-bold text-squig-yellow">{{ profile.elo }}</div>
            <div class="text-xs text-gray-400">ELO</div>
          </div>
          <div class="bg-gray-700 rounded p-3 text-center">
            <div class="text-2xl font-bold">{{ profile.total_games }}</div>
            <div class="text-xs text-gray-400">{{ t('profile.games') }}</div>
          </div>
          <div class="bg-gray-700 rounded p-3 text-center">
            <div class="text-2xl font-bold text-green-400">{{ profile.win_rate }}%</div>
            <div class="text-xs text-gray-400">{{ t('profile.winRate') }}</div>
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
          <h3 class="text-lg font-semibold mb-3">{{ t('profile.armiesPlayed') }}</h3>
          <div class="space-y-3">
            <div v-for="stat in profile.army_stats" :key="stat.army_faction">
              <div class="flex items-center gap-3 mb-1">
                <div class="w-48 text-sm truncate" :title="stat.army_faction">{{ stat.army_faction }}</div>
                <div class="flex-1 text-xs text-gray-400 text-right">
                  <span class="text-green-400">{{ stat.wins }}W</span>
                  <span class="mx-1">/</span>
                  <span class="text-yellow-400">{{ stat.draws }}D</span>
                  <span class="mx-1">/</span>
                  <span class="text-red-400">{{ stat.losses }}L</span>
                </div>
                <div class="w-20 text-right text-sm text-gray-400">
                  {{ stat.games_played }} ({{ stat.percentage }}%)
                </div>
              </div>
              <!-- W/D/L Color Bar -->
              <div class="flex h-3 rounded-full overflow-hidden bg-gray-700">
                <div
                  v-if="stat.wins > 0"
                  class="bg-green-500"
                  :style="{ width: (stat.wins / stat.games_played * 100) + '%' }"
                  :title="`${stat.wins} wins`"
                ></div>
                <div
                  v-if="stat.draws > 0"
                  class="bg-yellow-500"
                  :style="{ width: (stat.draws / stat.games_played * 100) + '%' }"
                  :title="`${stat.draws} draws`"
                ></div>
                <div
                  v-if="stat.losses > 0"
                  class="bg-red-500"
                  :style="{ width: (stat.losses / stat.games_played * 100) + '%' }"
                  :title="`${stat.losses} losses`"
                ></div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Leagues -->
      <div v-for="league in sortedLeagues" :key="league.league_id" class="card mb-4">
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
            {{ league.total_points }} {{ t('profile.pts') }} ({{ t('profile.avg') }}: {{ league.average_points }})
          </div>
        </div>

        <!-- League Stats -->
        <div class="flex gap-4 text-sm mb-4">
          <span>{{ t('profile.played') }}: {{ league.games_played }}</span>
          <span class="text-green-400">W: {{ league.games_won }}</span>
          <span class="text-yellow-400">D: {{ league.games_drawn }}</span>
          <span class="text-red-400">L: {{ league.games_lost }}</span>
        </div>

        <!-- Matches -->
        <div v-if="league.matches.length > 0">
          <h4 class="text-sm font-medium text-gray-400 mb-2">{{ t('profile.recentMatches') }}</h4>
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
                <span>{{ t('profile.vs') }} {{ match.opponent_username || 'Unknown' }}</span>
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
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { useI18n } from 'vue-i18n'
import axios from 'axios'

const { t } = useI18n()
const API_URL = import.meta.env.VITE_API_URL || '/api'
const route = useRoute()

const profile = ref(null)
const loading = ref(true)
const error = ref('')

// Sort leagues - newest first (by league_id descending, active/knockout first)
const sortedLeagues = computed(() => {
  if (!profile.value?.leagues) return []
  return [...profile.value.leagues].sort((a, b) => {
    // Active leagues first
    const statusOrder = { knockout_phase: 0, group_phase: 1, registration: 2, finished: 3 }
    const statusDiff = (statusOrder[a.league_status] ?? 4) - (statusOrder[b.league_status] ?? 4)
    if (statusDiff !== 0) return statusDiff
    // Then by league_id descending (newer = higher id)
    return b.league_id - a.league_id
  })
})

const fetchProfile = async () => {
  loading.value = true
  error.value = ''
  try {
    const res = await axios.get(`${API_URL}/player/${route.params.userId}/profile`)
    profile.value = res.data
  } catch (err) {
    error.value = err.response?.data?.detail || t('profile.failedToLoad')
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
    registration: t('leagues.registration'),
    active: t('leagues.groupPhase'),
    group_phase: t('leagues.groupPhase'),
    knockout_phase: t('leagues.knockoutPhase'),
    finished: t('leagues.finished'),
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
  if (placement === '1') return t('profile.champion')
  if (placement === '2') return t('profile.finalist')
  if (placement === 'top_4') return t('profile.semiFinalist')
  return formatPlacement(placement)
}

const formatPlacement = (placement) => {
  if (placement === '1') return t('profile.firstPlace')
  if (placement === '2') return t('profile.secondPlace')
  if (placement === 'top_4') return t('profile.top4')
  if (placement === 'top_8') return t('profile.top8')
  if (placement === 'top_16') return t('profile.top16')
  if (placement === 'top_32') return t('profile.top32')
  return placement
}

const getLeaguePlacementText = (league) => {
  if (league.knockout_placement) {
    return formatPlacement(league.knockout_placement)
  }
  // Show "Group Phase" only for finished leagues without knockout placement
  if (league.league_status === 'finished') {
    return t('leagues.groupPhase')
  }
  return ''
}

onMounted(fetchProfile)
</script>
