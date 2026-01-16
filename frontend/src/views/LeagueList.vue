<template>
  <div class="max-w-6xl mx-auto">
    <div class="flex justify-between items-center mb-6">
      <h1 class="text-3xl font-bold">Leagues</h1>
      <router-link
        v-if="canCreateLeague"
        to="/league/create"
        class="btn-primary"
      >
        + New League
      </router-link>
    </div>

    <div v-if="loading" class="text-center py-12">
      <p class="text-xl text-gray-300">Loading leagues...</p>
    </div>

    <div v-else-if="error" class="card">
      <div class="bg-red-900/30 border border-red-500 text-red-200 px-4 py-3 rounded">
        {{ error }}
      </div>
    </div>

    <div v-else-if="leagues.length === 0" class="card text-center py-12">
      <p class="text-xl text-gray-400 mb-4">No leagues yet</p>
      <p class="text-gray-500">New leagues coming soon!</p>
    </div>

    <div v-else class="space-y-8">
      <!-- My Leagues -->
      <div v-if="myLeagues.length > 0">
        <h2 class="text-xl font-bold mb-4 text-squig-yellow">My Leagues</h2>
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
        <h2 class="text-xl font-bold mb-4 text-blue-400">Upcoming Leagues</h2>
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
        <h2 class="text-xl font-bold mb-4 text-orange-400">Ongoing Leagues</h2>
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
        <h2 class="text-xl font-bold mb-4 text-green-400">Finished Leagues</h2>
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
import { useAuthStore } from '../stores/auth'
import axios from 'axios'
import LeagueCard from '../components/LeagueCard.vue'

const API_URL = import.meta.env.VITE_API_URL || '/api'
const router = useRouter()
const authStore = useAuthStore()

const loading = ref(true)
const error = ref('')
const leagues = ref([])

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
    error.value = 'Failed to load leagues'
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
