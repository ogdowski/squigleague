<template>
  <div class="max-w-6xl mx-auto">
    <div v-if="loading" class="text-center py-12">
      <p class="text-xl text-gray-300">Loading league...</p>
    </div>

    <div v-else-if="error" class="card">
      <div class="bg-red-900/30 border border-red-500 text-red-200 px-4 py-3 rounded">
        {{ error }}
      </div>
    </div>

    <div v-else-if="league">
      <!-- Header -->
      <div class="flex justify-between items-start mb-6">
        <div>
          <h1 class="text-3xl font-bold text-squig-yellow mb-2">{{ league.name }}</h1>
          <p v-if="league.description" class="text-gray-400">{{ league.description }}</p>
        </div>
        <div
          :class="statusClass(league.status)"
          class="px-4 py-2 rounded text-sm font-bold"
        >
          {{ statusText(league.status) }}
        </div>
      </div>

      <!-- Info Cards -->
      <div class="grid md:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
        <div class="card">
          <h3 class="text-sm text-gray-400 mb-1">Players</h3>
          <p class="text-2xl font-bold">{{ league.player_count }}</p>
          <p v-if="league.qualifying_spots_per_group" class="text-xs text-gray-500 mt-1">
            Top {{ league.qualifying_spots_per_group }} per group advance
          </p>
        </div>
        <div class="card">
          <h3 class="text-sm text-gray-400 mb-1">Scoring</h3>
          <p class="text-sm">W: {{ league.points_per_win }} / D: {{ league.points_per_draw }} / L: {{ league.points_per_loss }}</p>
        </div>
        <div v-if="league.group_phase_end" class="card">
          <h3 class="text-sm text-gray-400 mb-1">Group Phase Ends</h3>
          <p class="text-lg font-bold">{{ formatDateTime(league.group_phase_end) }}</p>
        </div>
        <div v-if="league.knockout_phase_end && league.has_knockout_phase" class="card">
          <h3 class="text-sm text-gray-400 mb-1">Knockout Ends</h3>
          <p class="text-lg font-bold">{{ formatDateTime(league.knockout_phase_end) }}</p>
        </div>
      </div>

      <!-- Action Error -->
      <div v-if="actionError" class="mb-4 bg-red-900/30 border border-red-500 text-red-200 px-4 py-3 rounded">
        {{ actionError }}
      </div>

      <!-- Actions -->
      <div class="flex gap-4 mb-8">
        <button
          v-if="league.is_registration_open && !isJoined"
          @click="joinLeague"
          class="btn-primary"
          :disabled="joining"
        >
          {{ joining ? 'Joining...' : 'Join League' }}
        </button>

        <template v-if="isOrganizer">
          <router-link
            :to="`/league/${league.id}/settings`"
            class="btn-secondary"
          >
            Settings
          </router-link>
          <button
            v-if="league.status === 'registration'"
            @click="showDrawGroupsModal = true"
            class="btn-secondary"
            :disabled="actionLoading"
          >
            Draw Groups
          </button>
          <button
            v-if="league.status === 'group_phase' && !groupPhaseEnded"
            @click="showEndGroupPhaseModal = true"
            class="btn-secondary"
            :disabled="actionLoading"
          >
            End Group Phase
          </button>
          <button
            v-if="league.status === 'group_phase' && groupPhaseEnded && league.has_knockout_phase"
            @click="showStartKnockoutModal = true"
            class="btn-secondary"
            :disabled="actionLoading"
          >
            Start Knockout
          </button>
          <button
            v-if="league.status === 'group_phase' && groupPhaseEnded && !league.has_knockout_phase"
            @click="showFinishLeagueModal = true"
            class="btn-secondary"
            :disabled="actionLoading"
          >
            Finish League
          </button>
          <button
            v-if="league.status === 'knockout_phase' && !league.knockout_lists_visible"
            @click="showRevealListsModal = true"
            class="btn-secondary"
            :disabled="actionLoading"
          >
            Reveal Lists
          </button>
        </template>
      </div>

      <!-- Tabs -->
      <div class="flex gap-2 mb-6 border-b border-gray-700">
        <button
          v-for="tab in tabs"
          :key="tab.id"
          @click="activeTab = tab.id"
          :class="activeTab === tab.id ? 'border-squig-yellow text-squig-yellow' : 'border-transparent text-gray-400'"
          class="px-4 py-2 border-b-2 transition-colors"
        >
          {{ tab.name }}
        </button>
      </div>

      <!-- Tab Content -->
      <div v-if="activeTab === 'standings'" class="space-y-6">
        <div v-for="group in standings" :key="group.group_id" class="card">
          <div class="flex justify-between items-center mb-4">
            <h3 class="text-xl font-bold">{{ group.group_name }}</h3>
            <span v-if="group.qualifying_spots" class="text-sm text-gray-400">
              Top {{ group.qualifying_spots }} advance
            </span>
          </div>
          <div class="overflow-x-auto">
            <table class="w-full text-sm">
              <thead>
                <tr class="text-gray-400 border-b border-gray-700">
                  <th class="text-left py-2 px-2">#</th>
                  <th class="text-left py-2 px-2">Player</th>
                  <th class="text-center py-2 px-2">P</th>
                  <th class="text-center py-2 px-2">W</th>
                  <th class="text-center py-2 px-2">D</th>
                  <th class="text-center py-2 px-2">L</th>
                  <th class="text-right py-2 px-2">Pts</th>
                  <th class="text-right py-2 px-2">Avg</th>
                </tr>
              </thead>
              <tbody>
                <tr
                  v-for="entry in group.standings"
                  :key="entry.player_id"
                  :class="[
                    'border-b',
                    entry.qualifies
                      ? 'border-green-800 bg-green-900/20'
                      : 'border-gray-800'
                  ]"
                >
                  <td class="py-2 px-2 font-bold">
                    <span v-if="entry.qualifies" class="text-green-400">{{ entry.position }}</span>
                    <span v-else>{{ entry.position }}</span>
                  </td>
                  <td class="py-2 px-2">{{ entry.username || entry.discord_username }}</td>
                  <td class="py-2 px-2 text-center">{{ entry.games_played }}</td>
                  <td class="py-2 px-2 text-center text-green-400">{{ entry.games_won }}</td>
                  <td class="py-2 px-2 text-center text-yellow-400">{{ entry.games_drawn }}</td>
                  <td class="py-2 px-2 text-center text-red-400">{{ entry.games_lost }}</td>
                  <td class="py-2 px-2 text-right font-bold text-squig-yellow">{{ entry.total_points }}</td>
                  <td class="py-2 px-2 text-right text-gray-400">{{ entry.average_points.toFixed(0) }}</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>

      <div v-if="activeTab === 'matches'" class="space-y-4">
        <div v-if="matches.length === 0" class="card text-center py-8">
          <p class="text-gray-400">No matches yet</p>
        </div>
        <div
          v-for="match in matches"
          :key="match.id"
          class="card"
        >
          <div class="flex items-center justify-between">
            <div class="flex-1">
              <div class="flex items-center gap-4">
                <span class="font-bold">{{ match.player1_username }}</span>
                <span v-if="match.is_completed" class="text-2xl font-bold text-squig-yellow">
                  {{ match.player1_score }} - {{ match.player2_score }}
                </span>
                <span v-else class="text-gray-500">vs</span>
                <span class="font-bold">{{ match.player2_username }}</span>
              </div>
              <div class="text-sm text-gray-400 mt-1">
                <span v-if="match.phase === 'knockout'">{{ knockoutRoundText(match.knockout_round) }}</span>
                <span v-if="match.map_name"> | Map: {{ match.map_name }}</span>
              </div>
            </div>
            <div
              :class="matchStatusClass(match.status)"
              class="px-3 py-1 rounded text-sm"
            >
              {{ matchStatusText(match.status) }}
            </div>
          </div>
        </div>
      </div>

      <div v-if="activeTab === 'players'" class="card">
        <div class="overflow-x-auto">
          <table class="w-full text-sm">
            <thead>
              <tr class="text-gray-400 border-b border-gray-700">
                <th class="text-left py-2 px-2">Player</th>
                <th class="text-left py-2 px-2">Group</th>
                <th class="text-center py-2 px-2">Status</th>
                <th class="text-right py-2 px-2">Joined</th>
              </tr>
            </thead>
            <tbody>
              <tr
                v-for="player in players"
                :key="player.id"
                class="border-b border-gray-800"
              >
                <td class="py-2 px-2">{{ player.username || player.discord_username }}</td>
                <td class="py-2 px-2">{{ player.group_name || '-' }}</td>
                <td class="py-2 px-2 text-center">
                  <span v-if="player.is_claimed" class="text-green-400">Verified</span>
                  <span v-else class="text-yellow-400">Pending</span>
                </td>
                <td class="py-2 px-2 text-right text-gray-400">{{ formatDate(player.joined_at) }}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <!-- Confirm Modals -->
    <ConfirmModal
      :show="showDrawGroupsModal"
      title="Draw Groups"
      message="Are you sure you want to draw groups? This action cannot be undone."
      confirmText="Draw Groups"
      :danger="true"
      @confirm="drawGroups"
      @cancel="showDrawGroupsModal = false"
    />

    <ConfirmModal
      :show="showStartKnockoutModal"
      title="Start Knockout Phase"
      message="Are you sure you want to start the knockout phase? Make sure all group matches are completed."
      confirmText="Start Knockout"
      :danger="true"
      @confirm="startKnockout"
      @cancel="showStartKnockoutModal = false"
    />

    <ConfirmModal
      :show="showRevealListsModal"
      title="Reveal Army Lists"
      message="Are you sure you want to reveal all army lists? Players will be able to see each other's lists."
      confirmText="Reveal Lists"
      @confirm="revealLists"
      @cancel="showRevealListsModal = false"
    />

    <ConfirmModal
      :show="showEndGroupPhaseModal"
      title="End Group Phase"
      message="Are you sure you want to end the group phase? Players will no longer be able to submit group match results."
      confirmText="End Group Phase"
      :danger="true"
      @confirm="endGroupPhase"
      @cancel="showEndGroupPhaseModal = false"
    />

    <ConfirmModal
      :show="showFinishLeagueModal"
      title="Finish League"
      message="Are you sure you want to finish this league? This will mark it as completed."
      confirmText="Finish League"
      :danger="true"
      @confirm="finishLeague"
      @cancel="showFinishLeagueModal = false"
    />
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import axios from 'axios'
import ConfirmModal from '../components/ConfirmModal.vue'

const API_URL = import.meta.env.VITE_API_URL || '/api'
const route = useRoute()
const authStore = useAuthStore()

const loading = ref(true)
const error = ref('')
const actionError = ref('')
const league = ref(null)
const standings = ref([])
const matches = ref([])
const players = ref([])
const activeTab = ref('standings')
const joining = ref(false)
const actionLoading = ref(false)

// Modal states
const showDrawGroupsModal = ref(false)
const showStartKnockoutModal = ref(false)
const showRevealListsModal = ref(false)
const showEndGroupPhaseModal = ref(false)
const showFinishLeagueModal = ref(false)

const showActionError = (message) => {
  actionError.value = message
  setTimeout(() => {
    actionError.value = ''
  }, 5000)
}

const tabs = [
  { id: 'standings', name: 'Standings' },
  { id: 'matches', name: 'Matches' },
  { id: 'players', name: 'Players' },
]

const isOrganizer = computed(() => {
  if (!authStore.user || !league.value) return false
  return league.value.organizer_id === authStore.user.id || authStore.user.role === 'admin'
})

const isJoined = computed(() => {
  if (!authStore.user) return false
  return players.value.some(p => p.user_id === authStore.user.id)
})

const groupPhaseEnded = computed(() => {
  if (!league.value) return false
  return league.value.group_phase_ended === true
})

const fetchLeague = async () => {
  try {
    const leagueId = route.params.id
    const [leagueRes, standingsRes, matchesRes, playersRes] = await Promise.all([
      axios.get(`${API_URL}/league/${leagueId}`),
      axios.get(`${API_URL}/league/${leagueId}/standings`).catch(() => ({ data: [] })),
      axios.get(`${API_URL}/league/${leagueId}/matches`).catch(() => ({ data: [] })),
      axios.get(`${API_URL}/league/${leagueId}/players`).catch(() => ({ data: [] })),
    ])

    league.value = leagueRes.data
    standings.value = standingsRes.data
    matches.value = matchesRes.data
    players.value = playersRes.data
  } catch (err) {
    error.value = 'Failed to load league'
  } finally {
    loading.value = false
  }
}

const joinLeague = async () => {
  joining.value = true
  actionError.value = ''
  try {
    await axios.post(`${API_URL}/league/${league.value.id}/join`)
    await fetchLeague()
  } catch (err) {
    showActionError(err.response?.data?.detail || 'Failed to join')
  } finally {
    joining.value = false
  }
}

const drawGroups = async () => {
  showDrawGroupsModal.value = false
  actionLoading.value = true
  actionError.value = ''
  try {
    await axios.post(`${API_URL}/league/${league.value.id}/draw-groups`)
    await fetchLeague()
  } catch (err) {
    showActionError(err.response?.data?.detail || 'Failed to draw groups')
  } finally {
    actionLoading.value = false
  }
}

const startKnockout = async () => {
  showStartKnockoutModal.value = false
  actionLoading.value = true
  actionError.value = ''
  try {
    await axios.post(`${API_URL}/league/${league.value.id}/start-knockout`)
    await fetchLeague()
  } catch (err) {
    showActionError(err.response?.data?.detail || 'Failed to start knockout')
  } finally {
    actionLoading.value = false
  }
}

const revealLists = async () => {
  showRevealListsModal.value = false
  actionLoading.value = true
  actionError.value = ''
  try {
    await axios.post(`${API_URL}/league/${league.value.id}/reveal-lists`)
    await fetchLeague()
  } catch (err) {
    showActionError(err.response?.data?.detail || 'Failed to reveal lists')
  } finally {
    actionLoading.value = false
  }
}

const endGroupPhase = async () => {
  showEndGroupPhaseModal.value = false
  actionLoading.value = true
  actionError.value = ''
  try {
    await axios.post(`${API_URL}/league/${league.value.id}/end-group-phase`)
    await fetchLeague()
  } catch (err) {
    showActionError(err.response?.data?.detail || 'Failed to end group phase')
  } finally {
    actionLoading.value = false
  }
}

const finishLeague = async () => {
  showFinishLeagueModal.value = false
  actionLoading.value = true
  actionError.value = ''
  try {
    await axios.patch(`${API_URL}/league/${league.value.id}`, { status: 'finished' })
    await fetchLeague()
  } catch (err) {
    showActionError(err.response?.data?.detail || 'Failed to finish league')
  } finally {
    actionLoading.value = false
  }
}

const formatDate = (dateString) => {
  return new Date(dateString).toLocaleDateString()
}

const formatDateTime = (dateString) => {
  const date = new Date(dateString)
  return date.toLocaleDateString() + ' ' + date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
}

const statusClass = (status) => {
  switch (status) {
    case 'registration': return 'bg-blue-900/30 border border-blue-500 text-blue-200'
    case 'group_phase': return 'bg-yellow-900/30 border border-yellow-500 text-yellow-200'
    case 'knockout_phase': return 'bg-orange-900/30 border border-orange-500 text-orange-200'
    case 'finished': return 'bg-green-900/30 border border-green-500 text-green-200'
    default: return 'bg-gray-900/30 border border-gray-500 text-gray-200'
  }
}

const statusText = (status) => {
  switch (status) {
    case 'registration': return 'Registration'
    case 'group_phase': return 'Group Phase'
    case 'knockout_phase': return 'Knockout'
    case 'finished': return 'Finished'
    default: return status
  }
}

const matchStatusClass = (status) => {
  switch (status) {
    case 'scheduled': return 'bg-gray-900/30 border border-gray-500 text-gray-200'
    case 'pending_confirmation': return 'bg-yellow-900/30 border border-yellow-500 text-yellow-200'
    case 'confirmed': return 'bg-green-900/30 border border-green-500 text-green-200'
    default: return 'bg-gray-900/30 border border-gray-500 text-gray-200'
  }
}

const matchStatusText = (status) => {
  switch (status) {
    case 'scheduled': return 'Scheduled'
    case 'pending_confirmation': return 'Pending'
    case 'confirmed': return 'Completed'
    default: return status
  }
}

const knockoutRoundText = (round) => {
  switch (round) {
    case 'round_of_32': return 'Round of 32'
    case 'round_of_16': return 'Round of 16'
    case 'quarter': return 'Quarter-final'
    case 'semi': return 'Semi-final'
    case 'final': return 'Final'
    default: return round
  }
}

onMounted(() => {
  fetchLeague()
})
</script>
