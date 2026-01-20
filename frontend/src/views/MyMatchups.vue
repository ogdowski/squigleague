<template>
  <div class="max-w-6xl mx-auto">
    <div class="flex items-center justify-between mb-6">
      <h1 class="text-3xl font-bold">{{ t('matchups.title') }}</h1>
      <router-link v-if="authStore.isAuthenticated" to="/matchup/create" class="btn-primary">
        {{ t('matchups.createMatchup') }}
      </router-link>
    </div>

    <div v-if="!authStore.isAuthenticated" class="card text-center py-12">
      <p class="text-xl text-gray-400 mb-4">{{ t('matchups.createMatchupDesc') }}</p>
      <router-link to="/matchup/create" class="btn-primary inline-block">
        {{ t('matchups.createMatchup') }}
      </router-link>
    </div>

    <div v-else-if="loading" class="text-center py-12">
      <p class="text-xl text-gray-300">{{ t('matchups.loadingMatchups') }}</p>
    </div>

    <div v-else-if="error" class="card">
      <div class="bg-red-900/30 border border-red-500 text-red-200 px-4 py-3 rounded">
        {{ error }}
      </div>
    </div>

    <div v-else-if="matchups.length === 0" class="card text-center py-12">
      <p class="text-xl text-gray-400 mb-4">{{ t('matchups.noMatchups') }}</p>
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
                <span class="text-gray-400">{{ t('matchups.created') }}:</span>
                <span class="text-white ml-2">{{ formatDate(matchup.created_at) }}</span>
              </div>
              <div>
                <span class="text-gray-400">{{ t('matchups.expires') }}:</span>
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
              <div class="text-xs text-gray-400 mb-1">{{ t('matchups.player1') }}</div>
              <div :class="matchup.player1_submitted ? 'text-green-400' : 'text-gray-500'">
                {{ matchup.player1_submitted ? '✓' : '○' }}
              </div>
            </div>
            <div class="text-center">
              <div class="text-xs text-gray-400 mb-1">{{ t('matchups.player2') }}</div>
              <div :class="matchup.player2_submitted ? 'text-green-400' : 'text-gray-500'">
                {{ matchup.player2_submitted ? '✓' : '○' }}
              </div>
            </div>
            <div
              v-if="matchup.is_revealed"
              class="bg-green-900/30 border border-green-500 text-green-200 px-3 py-1 rounded text-sm"
            >
              {{ t('matchups.revealed') }}
            </div>
            <div
              v-else
              class="bg-yellow-900/30 border border-yellow-500 text-yellow-200 px-3 py-1 rounded text-sm"
            >
              {{ t('matchups.pending') }}
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
import { useI18n } from 'vue-i18n'
import { useAuthStore } from '../stores/auth'
import axios from 'axios'

const { t } = useI18n()
const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'
const router = useRouter()
const authStore = useAuthStore()

const loading = ref(true)
const error = ref('')
const matchups = ref([])

const fetchMatchups = async () => {
  if (!authStore.isAuthenticated) {
    loading.value = false
    return
  }
  try {
    const response = await axios.get(`${API_URL}/matchup/my-matchups`)
    matchups.value = response.data
  } catch (err) {
    if (err.response?.status === 401) {
      error.value = t('matchups.pleaseLogin')
    } else {
      error.value = t('matchups.failedToLoad')
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
