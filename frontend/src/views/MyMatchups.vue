<template>
  <div class="max-w-6xl mx-auto">
    <h1 class="text-2xl md:text-3xl font-bold mb-6">{{ t('matchups.title') }}</h1>

    <!-- How It Works section -->
    <div v-if="!howItWorksHidden" class="mb-6 relative">
      <div class="flex items-center justify-between mb-4">
        <h2 class="text-xl font-bold">{{ t('matchups.howItWorks') }}</h2>
        <button
          @click="hideHowItWorks"
          class="text-gray-400 hover:text-white transition-colors p-1"
          aria-label="Close"
        >
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      </div>
      <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3 mb-4">
        <div class="bg-gray-800 rounded-lg p-4 border border-gray-700 flex sm:block items-center gap-4">
          <div class="text-2xl font-bold text-squig-yellow sm:mb-2 flex-shrink-0">1</div>
          <p class="text-sm text-gray-300">{{ t('matchups.howItWorksStep1') }}</p>
        </div>
        <div class="bg-gray-800 rounded-lg p-4 border border-gray-700 flex sm:block items-center gap-4">
          <div class="text-2xl font-bold text-squig-yellow sm:mb-2 flex-shrink-0">2</div>
          <p class="text-sm text-gray-300">{{ t('matchups.howItWorksStep2') }}</p>
        </div>
        <div class="bg-gray-800 rounded-lg p-4 border border-gray-700 flex sm:block items-center gap-4">
          <div class="text-2xl font-bold text-squig-yellow sm:mb-2 flex-shrink-0">3</div>
          <p class="text-sm text-gray-300">{{ t('matchups.howItWorksStep3') }}</p>
        </div>
        <div class="bg-gray-800 rounded-lg p-4 border border-gray-700 flex sm:block items-center gap-4">
          <div class="text-2xl font-bold text-squig-yellow sm:mb-2 flex-shrink-0">4</div>
          <p class="text-sm text-gray-300">{{ t('matchups.howItWorksStep4') }}</p>
        </div>
      </div>
      <!-- Create Matchup button under the welcome tile -->
      <router-link to="/matchup/create" class="btn-primary w-full sm:w-auto text-center py-3">
        {{ t('matchups.createMatchup') }}
      </router-link>
    </div>

    <!-- Create button when welcome is hidden -->
    <div v-if="howItWorksHidden" class="mb-6">
      <router-link to="/matchup/create" class="btn-primary text-center">
        {{ t('matchups.createMatchup') }}
      </router-link>
    </div>

    <div v-if="loading" class="text-center py-12">
      <p class="text-xl text-gray-300">{{ t('matchups.loadingMatchups') }}</p>
    </div>

    <div v-else-if="error" class="card">
      <div class="bg-red-900/30 border border-red-500 text-red-200 px-4 py-3 rounded">
        {{ error }}
      </div>
    </div>

    <div v-else class="space-y-8">
      <!-- My Matchups Section -->
      <div v-if="authStore.isAuthenticated">
        <h2 class="text-xl font-bold mb-4 text-squig-yellow">{{ t('matchups.myMatchups') }}</h2>
        <div v-if="myMatchups.length === 0" class="card text-center py-8">
          <p class="text-gray-400">{{ t('matchups.noMatchups') }}</p>
        </div>
        <div v-else class="space-y-3">
          <MatchupCard
            v-for="matchup in myMatchups"
            :key="matchup.name"
            :matchup="matchup"
            @click="goToMatchup(matchup.name)"
            @submit-result="(m) => goToMatchup(m.name)"
            @confirm-result="(m) => goToMatchup(m.name)"
            @edit-result="(m) => goToMatchup(m.name)"
          />
        </div>
      </div>

      <!-- Public Matchups Section -->
      <div>
        <h2 class="text-xl font-bold mb-4">{{ t('matchups.publicMatchups') }}</h2>
        <div v-if="publicMatchups.length === 0" class="card text-center py-8">
          <p class="text-gray-400">{{ t('matchups.noPublicMatchups') }}</p>
        </div>
        <div v-else class="space-y-3">
          <MatchupCard
            v-for="matchup in publicMatchups"
            :key="matchup.name"
            :matchup="matchup"
            @click="goToMatchup(matchup.name)"
          />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { useAuthStore } from '../stores/auth'
import axios from 'axios'
import MatchupCard from '../components/MatchupCard.vue'

const { t } = useI18n()
const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'
const router = useRouter()
const authStore = useAuthStore()

const loading = ref(true)
const error = ref('')
const myMatchups = ref([])
const allPublicMatchups = ref([])
const howItWorksHidden = ref(localStorage.getItem('matchups_howItWorksHidden') === 'true')

// Filter public matchups to exclude user's own matchups
const publicMatchups = computed(() => {
  if (!authStore.isAuthenticated || !authStore.user) {
    return allPublicMatchups.value
  }
  const username = authStore.user.username
  return allPublicMatchups.value.filter(
    m => m.player1_username !== username && m.player2_username !== username
  )
})

const hideHowItWorks = () => {
  howItWorksHidden.value = true
  localStorage.setItem('matchups_howItWorksHidden', 'true')
}

const fetchData = async () => {
  try {
    // Fetch public matchups always
    const publicResponse = await axios.get(`${API_URL}/matchup/public`)
    allPublicMatchups.value = publicResponse.data

    // Fetch user's matchups if authenticated
    if (authStore.isAuthenticated) {
      try {
        const myResponse = await axios.get(`${API_URL}/matchup/my-matchups`)
        myMatchups.value = myResponse.data
      } catch (err) {
        if (err.response?.status !== 401) {
          console.error('Failed to load my matchups:', err)
        }
      }
    }
  } catch (err) {
    error.value = t('matchups.failedToLoad')
  } finally {
    loading.value = false
  }
}

const goToMatchup = (name) => {
  router.push(`/matchup/${name}`)
}

onMounted(() => {
  fetchData()
})
</script>
