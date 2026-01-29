<template>
  <div class="max-w-4xl mx-auto">
    <!-- Stats cards -->
    <div v-if="stats" class="space-y-4 mb-6">
      <!-- Numbers row -->
      <div class="grid grid-cols-2 gap-4">
        <div class="card text-center">
          <div class="text-3xl font-bold text-squig-yellow">{{ stats.total_players }}</div>
          <div class="text-sm text-gray-400">{{ t('ranking.activePlayers') }}</div>
        </div>
        <div class="card text-center">
          <div class="text-3xl font-bold text-squig-yellow">{{ stats.total_games }}</div>
          <div class="text-sm text-gray-400">{{ t('ranking.totalGames') }}</div>
        </div>
      </div>

      <!-- Top 5 Armies -->
      <div v-if="stats.top_armies && stats.top_armies.length > 0" class="card">
        <div class="text-sm text-gray-400 mb-4">{{ t('ranking.topArmies') }}</div>
        <div class="space-y-3">
          <div v-for="(army, index) in stats.top_armies.slice(0, 5)" :key="army.faction" class="flex items-center gap-3">
            <!-- Rank number -->
            <div class="w-5 md:w-6 text-center font-bold text-gray-500 text-xs md:text-base">#{{ index + 1 }}</div>

            <!-- Army name -->
            <div class="w-24 md:w-48 font-medium truncate text-sm md:text-base">{{ army.faction }}</div>

            <!-- Progress bar -->
            <div class="flex-1 h-6 md:h-7 bg-gray-700 rounded overflow-hidden relative">
              <div class="h-full flex" :style="{ width: Math.max(getArmyPercentage(army.count), 15) + '%' }">
                <div class="h-full bg-green-600" :style="{ width: getWinPercentage(army) + '%' }"></div>
                <div class="h-full bg-yellow-600" :style="{ width: getDrawPercentage(army) + '%' }"></div>
                <div class="h-full bg-red-600" :style="{ width: getLossPercentage(army) + '%' }"></div>
              </div>
              <!-- W/D/L overlay -->
              <div class="absolute inset-0 flex items-center px-1 md:px-2 text-[10px] md:text-xs font-medium whitespace-nowrap">
                <span class="text-white drop-shadow-md">
                  <span class="hidden sm:inline">{{ army.wins }}W / {{ army.draws }}D / {{ army.losses }}L</span>
                  <span class="sm:hidden">{{ army.wins }}/{{ army.draws }}/{{ army.losses }}</span>
                </span>
              </div>
            </div>

            <!-- Percentage -->
            <div class="w-10 md:w-12 text-right text-xs md:text-sm text-squig-yellow font-bold">{{ getArmyPercentage(army.count) }}%</div>
          </div>
        </div>
      </div>
    </div>

    <!-- Search -->
    <div class="mb-6">
      <input
        v-model="searchQuery"
        @input="debouncedSearch"
        type="text"
        class="input-field w-full"
        :placeholder="t('ranking.searchPlaceholder')"
      />
    </div>

    <!-- Loading -->
    <div v-if="loading" class="flex justify-center py-12">
      <div class="w-10 h-10 border-4 border-squig-yellow border-t-transparent rounded-full animate-spin"></div>
    </div>

    <!-- Error -->
    <div v-else-if="error" class="card">
      <div class="bg-red-900/30 border border-red-500 text-red-200 px-4 py-3 rounded">
        {{ error }}
      </div>
    </div>

    <div v-else class="space-y-8">
      <!-- Ranking list -->
      <div>
        <h2 v-if="ranking.length > 0" class="text-xl font-bold mb-4 text-squig-yellow">{{ t('ranking.leaderboard') }}</h2>
        <div v-if="ranking.length === 0 && newPlayers.length === 0" class="card text-center py-8">
          <p class="text-gray-400">{{ t('ranking.noPlayers') }}</p>
        </div>

        <div v-else class="space-y-2">
          <div
            v-for="player in ranking"
            :key="player.user_id"
            class="card hover:bg-gray-700 transition-colors cursor-pointer flex items-center gap-4"
            @click="goToPlayer(player.user_id)"
          >
            <!-- Rank -->
            <div class="w-10 text-center flex-shrink-0">
              <span
                :class="{
                  'text-yellow-400 font-bold text-xl': player.rank === 1,
                  'text-gray-300 font-bold text-lg': player.rank === 2,
                  'text-orange-400 font-bold text-lg': player.rank === 3,
                  'text-gray-500': player.rank > 3
                }"
              >
                #{{ player.rank }}
              </span>
            </div>

            <!-- Avatar -->
            <div class="flex-shrink-0">
              <img
                v-if="player.avatar_url"
                :src="player.avatar_url"
                :alt="player.username"
                class="w-10 h-10 rounded-full"
              />
              <div v-else class="w-10 h-10 rounded-full bg-gray-600 flex items-center justify-center text-lg">
                {{ player.username.charAt(0).toUpperCase() }}
              </div>
            </div>

            <!-- Name & Army -->
            <div class="flex-1 min-w-0">
              <div class="font-bold text-lg truncate">{{ player.username }}</div>
              <div class="text-sm text-gray-400 flex items-center gap-2">
                <span v-if="player.main_army" class="text-squig-yellow">{{ player.main_army }}</span>
                <span v-else class="text-gray-500">-</span>
              </div>
            </div>

            <!-- W/D/L -->
            <div class="text-center flex-shrink-0 hidden sm:block">
              <div class="text-sm">
                <span class="text-green-400">{{ player.wins }}W</span>
                <span class="text-gray-400 mx-1">/</span>
                <span class="text-yellow-400">{{ player.draws }}D</span>
                <span class="text-gray-400 mx-1">/</span>
                <span class="text-red-400">{{ player.losses }}L</span>
              </div>
              <div class="text-xs text-gray-500">{{ player.games_played }} {{ t('ranking.games') }}</div>
            </div>

            <!-- ELO -->
            <div class="text-right flex-shrink-0">
              <div class="text-2xl font-bold text-squig-yellow">{{ player.elo }}</div>
              <div class="text-xs text-gray-400">ELO</div>
            </div>
          </div>

          <!-- Load more button -->
          <div v-if="ranking.length < totalCount" class="text-center pt-4">
            <button @click="loadMore" :disabled="loadingMore" class="btn-secondary">
              {{ loadingMore ? t('common.loading') : t('ranking.loadMore') }}
            </button>
          </div>
        </div>
      </div>

      <!-- New players without games -->
      <div v-if="newPlayers.length > 0">
        <h2 class="text-xl font-bold mb-4">{{ t('ranking.newPlayers') }}</h2>
        <div class="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-3">
          <div
            v-for="player in newPlayers"
            :key="player.user_id"
            class="bg-gray-800 rounded-lg p-3 hover:bg-gray-700 transition-colors cursor-pointer flex items-center gap-3"
            @click="goToPlayer(player.user_id)"
          >
            <img
              v-if="player.avatar_url"
              :src="player.avatar_url"
              :alt="player.username"
              class="w-8 h-8 rounded-full"
            />
            <div v-else class="w-8 h-8 rounded-full bg-gray-600 flex items-center justify-center text-sm">
              {{ player.username.charAt(0).toUpperCase() }}
            </div>
            <span class="truncate">{{ player.username }}</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import axios from 'axios'

const { t } = useI18n()
const router = useRouter()
const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

const loading = ref(true)
const loadingMore = ref(false)
const error = ref('')
const ranking = ref([])
const newPlayers = ref([])
const stats = ref(null)
const totalCount = ref(0)
const searchQuery = ref('')
const offset = ref(0)
const limit = 50

let searchTimeout = null

const fetchRanking = async (append = false) => {
  if (!append) {
    loading.value = true
    offset.value = 0
  } else {
    loadingMore.value = true
  }
  error.value = ''

  try {
    const params = { limit, offset: offset.value }
    if (searchQuery.value) {
      params.search = searchQuery.value
    }

    const response = await axios.get(`${API_URL}/player/ranking`, { params })

    if (append) {
      ranking.value = [...ranking.value, ...response.data.ranking]
    } else {
      ranking.value = response.data.ranking
      newPlayers.value = response.data.new_players || []
      stats.value = response.data.stats
    }
    totalCount.value = response.data.total_count
  } catch (err) {
    error.value = t('ranking.failedToLoad')
  } finally {
    loading.value = false
    loadingMore.value = false
  }
}

const debouncedSearch = () => {
  if (searchTimeout) clearTimeout(searchTimeout)
  searchTimeout = setTimeout(() => {
    fetchRanking()
  }, 300)
}

const loadMore = () => {
  offset.value += limit
  fetchRanking(true)
}

const goToPlayer = (userId) => {
  router.push(`/player/${userId}`)
}

// Calculate total games across all top armies
const getTotalArmyGames = () => {
  if (!stats.value?.top_armies) return 0
  return stats.value.top_armies.reduce((sum, army) => sum + army.count, 0)
}

const getArmyPercentage = (count) => {
  const total = getTotalArmyGames()
  if (total === 0) return 0
  return Math.round((count / total) * 100)
}

const getWinPercentage = (army) => {
  if (army.count === 0) return 0
  return Math.round((army.wins / army.count) * 100)
}

const getDrawPercentage = (army) => {
  if (army.count === 0) return 0
  return Math.round((army.draws / army.count) * 100)
}

const getLossPercentage = (army) => {
  if (army.count === 0) return 0
  return Math.round((army.losses / army.count) * 100)
}

onMounted(() => {
  fetchRanking()
})
</script>
