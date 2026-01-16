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

    <div v-else class="space-y-4">
      <div
        v-for="league in leagues"
        :key="league.id"
        class="card hover:bg-gray-700 transition-colors cursor-pointer"
        @click="goToLeague(league.id)"
      >
        <div class="flex items-center justify-between">
          <div class="flex-1">
            <h3 class="text-xl font-bold text-squig-yellow mb-2">
              {{ league.name }}
            </h3>
            <div class="flex gap-6 text-sm">
              <div>
                <span class="text-gray-400">Organizer:</span>
                <span class="text-white ml-2">{{ league.organizer_name || 'N/A' }}</span>
              </div>
              <div>
                <span class="text-gray-400">Players:</span>
                <span class="text-white ml-2">{{ league.player_count }}</span>
              </div>
              <div>
                <span class="text-gray-400">Registration ends:</span>
                <span class="text-white ml-2">{{ formatDate(league.registration_end) }}</span>
              </div>
            </div>
          </div>

          <div class="flex items-center gap-4">
            <div
              :class="statusClass(league.status)"
              class="px-3 py-1 rounded text-sm"
            >
              {{ statusText(league.status) }}
            </div>
          </div>
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

const API_URL = import.meta.env.VITE_API_URL || '/api'
const router = useRouter()
const authStore = useAuthStore()

const loading = ref(true)
const error = ref('')
const leagues = ref([])

const canCreateLeague = computed(() => {
  return authStore.user && ['organizer', 'admin'].includes(authStore.user.role)
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

const formatDate = (dateString) => {
  const date = new Date(dateString)
  return date.toLocaleDateString('pl-PL')
}

const statusClass = (status) => {
  switch (status) {
    case 'registration':
      return 'bg-blue-900/30 border border-blue-500 text-blue-200'
    case 'group_phase':
      return 'bg-yellow-900/30 border border-yellow-500 text-yellow-200'
    case 'knockout_phase':
      return 'bg-orange-900/30 border border-orange-500 text-orange-200'
    case 'finished':
      return 'bg-green-900/30 border border-green-500 text-green-200'
    default:
      return 'bg-gray-900/30 border border-gray-500 text-gray-200'
  }
}

const statusText = (status) => {
  switch (status) {
    case 'registration':
      return 'Registration'
    case 'group_phase':
      return 'Group Phase'
    case 'knockout_phase':
      return 'Knockout'
    case 'finished':
      return 'Finished'
    default:
      return status
  }
}

onMounted(() => {
  fetchLeagues()
})
</script>
