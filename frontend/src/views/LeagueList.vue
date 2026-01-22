<template>
  <div class="max-w-6xl mx-auto">
    <!-- Welcome Section (dismissible) -->
    <div v-if="!welcomeHidden" class="mb-8 relative">
      <button
        @click="hideWelcome"
        class="absolute top-2 right-2 text-gray-400 hover:text-white transition-colors p-1 z-10"
        aria-label="Close"
      >
        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
        </svg>
      </button>

      <!-- Hero -->
      <div class="text-center mb-6 md:mb-8">
        <h1 class="text-3xl md:text-4xl font-bold text-squig-yellow mb-2 md:mb-3">Squig League</h1>
        <p class="text-base md:text-lg text-gray-300 max-w-2xl mx-auto px-2">{{ t('home.subtitle') }}</p>
      </div>

      <!-- Feature Cards - single column on mobile -->
      <div class="grid grid-cols-1 md:grid-cols-3 gap-3 md:gap-4 mb-6">
        <a href="#leagues-section" @click.prevent="scrollToLeagues" class="card hover:bg-gray-700 transition-colors group p-4 cursor-pointer">
          <div class="flex items-center gap-3 mb-2">
            <svg class="w-8 h-8 text-squig-yellow" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
            </svg>
            <h2 class="text-lg font-bold group-hover:text-squig-yellow transition-colors">{{ t('home.leaguesTitle') }}</h2>
          </div>
          <p class="text-gray-400 text-sm">{{ t('home.leaguesDesc') }}</p>
        </a>

        <router-link to="/matchups" class="card hover:bg-gray-700 transition-colors group p-4">
          <div class="flex items-center gap-3 mb-2">
            <svg class="w-8 h-8 text-squig-yellow" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7h12m0 0l-4-4m4 4l-4 4m0 6H4m0 0l4 4m-4-4l4-4" />
            </svg>
            <h2 class="text-lg font-bold group-hover:text-squig-yellow transition-colors">{{ t('home.matchupsTitle') }}</h2>
          </div>
          <p class="text-gray-400 text-sm">{{ t('home.matchupsDesc') }}</p>
        </router-link>

        <div class="card bg-gray-800/50 border-dashed border-gray-600 p-4">
          <div class="flex items-center gap-3 mb-2">
            <svg class="w-8 h-8 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
            </svg>
            <h2 class="text-lg font-bold text-gray-500">{{ t('common.comingSoon') }}</h2>
          </div>
          <p class="text-gray-500 text-sm">{{ t('home.comingSoonDesc') }}</p>
        </div>
      </div>
    </div>

    <div id="leagues-section" class="flex flex-col sm:flex-row sm:justify-between sm:items-center gap-3 mb-6">
      <h1 class="text-2xl md:text-3xl font-bold">{{ t('leagues.title') }}</h1>
      <router-link
        v-if="canCreateLeague"
        to="/league/create"
        class="btn-primary text-center sm:w-auto"
      >
        {{ t('leagues.newLeague') }}
      </router-link>
    </div>

    <div v-if="loading" class="flex justify-center py-12">
      <div class="w-10 h-10 border-4 border-squig-yellow border-t-transparent rounded-full animate-spin"></div>
    </div>

    <div v-else-if="error" class="card">
      <div class="bg-red-900/30 border border-red-500 text-red-200 px-4 py-3 rounded">
        {{ error }}
      </div>
    </div>

    <div v-else-if="leagues.length === 0" class="card text-center py-12">
      <p class="text-xl text-gray-400 mb-4">{{ t('leagues.noLeagues') }}</p>
      <p class="text-gray-500">{{ t('leagues.noLeaguesDesc') }}</p>
    </div>

    <div v-else class="space-y-8">
      <!-- My Leagues -->
      <div v-if="myLeagues.length > 0">
        <h2 class="text-xl font-bold mb-4 text-squig-yellow">{{ t('leagues.myLeagues') }}</h2>
        <div class="space-y-4">
          <LeagueCard
            v-for="league in myLeagues"
            :key="league.id"
            :league="league"
            @click="goToLeague(league.id)"
          />
        </div>
      </div>

      <!-- Upcoming Leagues (Registration Open) -->
      <div v-if="upcomingLeagues.length > 0">
        <h2 class="text-xl font-bold mb-4 text-blue-400">{{ t('leagues.upcomingLeagues') }}</h2>
        <div class="space-y-4">
          <LeagueCard
            v-for="league in upcomingLeagues"
            :key="league.id"
            :league="league"
            @click="goToLeague(league.id)"
          />
        </div>
      </div>

      <!-- Ongoing Leagues -->
      <div v-if="ongoingLeagues.length > 0">
        <h2 class="text-xl font-bold mb-4 text-orange-400">{{ t('leagues.ongoingLeagues') }}</h2>
        <div class="space-y-4">
          <LeagueCard
            v-for="league in ongoingLeagues"
            :key="league.id"
            :league="league"
            @click="goToLeague(league.id)"
          />
        </div>
      </div>

      <!-- Finished Leagues -->
      <div v-if="finishedLeagues.length > 0">
        <h2 class="text-xl font-bold mb-4 text-green-400">{{ t('leagues.finishedLeagues') }}</h2>
        <div class="space-y-4">
          <LeagueCard
            v-for="league in finishedLeagues"
            :key="league.id"
            :league="league"
            @click="goToLeague(league.id)"
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
import LeagueCard from '../components/LeagueCard.vue'

const { t } = useI18n()
const API_URL = import.meta.env.VITE_API_URL || '/api'
const router = useRouter()
const authStore = useAuthStore()

const loading = ref(true)
const error = ref('')
const leagues = ref([])
const welcomeHidden = ref(localStorage.getItem('leagues_welcomeHidden') === 'true')

const hideWelcome = () => {
  welcomeHidden.value = true
  localStorage.setItem('leagues_welcomeHidden', 'true')
}

const scrollToLeagues = () => {
  document.getElementById('leagues-section')?.scrollIntoView({ behavior: 'smooth' })
}

const canCreateLeague = computed(() => {
  return authStore.user && ['organizer', 'admin'].includes(authStore.user.role)
})

// My leagues - where user is player or organizer (not in finished)
const myLeagues = computed(() => {
  return leagues.value.filter(l =>
    (l.is_player || l.is_organizer) && l.status !== 'finished'
  )
})

// Upcoming - registration status, not my league
const upcomingLeagues = computed(() => {
  return leagues.value.filter(l =>
    l.status === 'registration' && !l.is_player && !l.is_organizer
  )
})

// Ongoing - group_phase or knockout_phase, not my league
const ongoingLeagues = computed(() => {
  return leagues.value.filter(l =>
    ['group_phase', 'knockout_phase'].includes(l.status) && !l.is_player && !l.is_organizer
  )
})

// Finished
const finishedLeagues = computed(() => {
  return leagues.value.filter(l => l.status === 'finished')
})

const fetchLeagues = async () => {
  try {
    const response = await axios.get(`${API_URL}/league`)
    leagues.value = response.data
  } catch (err) {
    error.value = t('leagues.failedToLoad')
  } finally {
    loading.value = false
  }
}

const goToLeague = (id) => {
  router.push(`/league/${id}`)
}

onMounted(() => {
  fetchLeagues()
})
</script>
