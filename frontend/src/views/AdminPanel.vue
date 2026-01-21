<template>
  <div class="max-w-6xl mx-auto">
    <h1 class="text-3xl font-bold mb-6">{{ t('admin.title') }}</h1>

    <!-- Tabs -->
    <div class="flex border-b border-gray-700 mb-6">
      <button
        v-for="tab in tabs"
        :key="tab.id"
        @click="activeTab = tab.id"
        :class="[
          'px-6 py-3 text-sm font-medium border-b-2 -mb-px transition-colors',
          activeTab === tab.id
            ? 'border-squig-yellow text-squig-yellow'
            : 'border-transparent text-gray-400 hover:text-gray-200'
        ]"
      >
        {{ t(tab.label) }}
      </button>
    </div>

    <div v-if="loading" class="text-center py-12">
      <p class="text-xl text-gray-300">{{ t('common.loading') }}</p>
    </div>

    <div v-else-if="error" class="card">
      <div class="bg-red-900/30 border border-red-500 text-red-200 px-4 py-3 rounded">
        {{ error }}
      </div>
    </div>

    <div v-else>
      <!-- Users Tab -->
      <div v-show="activeTab === 'users'">
        <!-- Stats -->
        <div class="grid md:grid-cols-4 gap-4 mb-8">
          <div class="card">
            <h3 class="text-sm text-gray-400 mb-1">{{ t('admin.totalUsers') }}</h3>
            <p class="text-2xl font-bold">{{ stats.total_users }}</p>
          </div>
          <div class="card">
            <h3 class="text-sm text-gray-400 mb-1">{{ t('admin.players') }}</h3>
            <p class="text-2xl font-bold text-blue-400">{{ stats.players }}</p>
          </div>
          <div class="card">
            <h3 class="text-sm text-gray-400 mb-1">{{ t('admin.organizers') }}</h3>
            <p class="text-2xl font-bold text-yellow-400">{{ stats.organizers }}</p>
          </div>
          <div class="card">
            <h3 class="text-sm text-gray-400 mb-1">{{ t('admin.admins') }}</h3>
            <p class="text-2xl font-bold text-red-400">{{ stats.admins }}</p>
          </div>
        </div>

        <!-- Role Error -->
        <div v-if="roleError" class="mb-4 bg-red-900/30 border border-red-500 text-red-200 px-4 py-3 rounded">
          {{ roleError }}
        </div>

        <!-- Users Table -->
        <div class="card">
          <div class="overflow-x-auto">
            <table class="w-full text-sm">
              <thead>
                <tr class="text-gray-400 border-b border-gray-700">
                  <th class="text-left py-3 px-4">{{ t('admin.id') }}</th>
                  <th class="text-left py-3 px-4">{{ t('admin.email') }}</th>
                  <th class="text-left py-3 px-4">{{ t('admin.username') }}</th>
                  <th class="text-center py-3 px-4">{{ t('admin.role') }}</th>
                  <th class="text-center py-3 px-4">{{ t('admin.status') }}</th>
                  <th class="text-right py-3 px-4">{{ t('admin.created') }}</th>
                  <th class="text-right py-3 px-4">{{ t('admin.lastLogin') }}</th>
                  <th class="text-center py-3 px-4">{{ t('admin.actions') }}</th>
                </tr>
              </thead>
              <tbody>
                <tr
                  v-for="user in users"
                  :key="user.id"
                  class="border-b border-gray-800 hover:bg-gray-700/50"
                >
                  <td class="py-3 px-4 text-gray-400">{{ user.id }}</td>
                  <td class="py-3 px-4">{{ user.email }}</td>
                  <td class="py-3 px-4">{{ user.username || '-' }}</td>
                  <td class="py-3 px-4 text-center">
                    <select
                      v-model="user.role"
                      @change="updateRole(user)"
                      :disabled="user.updating"
                      class="bg-gray-700 border border-gray-600 rounded px-2 py-1 text-sm focus:outline-none focus:border-squig-yellow"
                    >
                      <option value="player">{{ t('admin.rolePlayer') }}</option>
                      <option value="organizer">{{ t('admin.roleOrganizer') }}</option>
                      <option value="admin">{{ t('admin.roleAdmin') }}</option>
                    </select>
                  </td>
                  <td class="py-3 px-4 text-center">
                    <span v-if="user.is_active" class="text-green-400">{{ t('admin.active') }}</span>
                    <span v-else class="text-red-400">{{ t('admin.inactive') }}</span>
                  </td>
                  <td class="py-3 px-4 text-right text-gray-400">{{ formatDate(user.created_at) }}</td>
                  <td class="py-3 px-4 text-right text-gray-400">{{ user.last_login ? formatDate(user.last_login) : '-' }}</td>
                  <td class="py-3 px-4 text-center">
                    <span v-if="user.updating" class="text-yellow-400">{{ t('admin.saving') }}</span>
                    <span v-else-if="user.saved" class="text-green-400">{{ t('admin.saved') }}</span>
                    <button
                      v-else
                      @click="confirmDeleteUser(user)"
                      class="text-red-400 hover:text-red-300 text-sm"
                      :disabled="user.deleting"
                    >
                      {{ user.deleting ? t('admin.deleting') : t('admin.delete') }}
                    </button>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>

      <!-- Settings Tab -->
      <div v-show="activeTab === 'settings'" class="max-w-2xl">
        <div class="card">
          <h2 class="text-xl font-bold mb-4">{{ t('admin.eloSettings') }}</h2>

          <form @submit.prevent="saveEloSettings" class="space-y-4">
            <div>
              <label class="block text-sm font-medium text-gray-300 mb-2">
                {{ t('admin.globalKFactor') }}
              </label>
              <input
                v-model.number="eloSettings.k_factor"
                type="number"
                min="1"
                max="100"
                class="w-full bg-gray-700 border border-gray-600 rounded px-4 py-2 focus:outline-none focus:border-squig-yellow"
              />
              <p class="text-sm text-gray-500 mt-1">
                {{ t('admin.globalKFactorNote') }}
              </p>
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-300 mb-2">
                {{ t('admin.newPlayerKFactor') }}
              </label>
              <input
                v-model.number="eloSettings.new_player_k"
                type="number"
                min="1"
                max="100"
                class="w-full bg-gray-700 border border-gray-600 rounded px-4 py-2 focus:outline-none focus:border-squig-yellow"
              />
              <p class="text-sm text-gray-500 mt-1">
                {{ t('admin.newPlayerKFactorNote') }}
              </p>
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-300 mb-2">
                {{ t('admin.newPlayerGamesThreshold') }}
              </label>
              <input
                v-model.number="eloSettings.new_player_games"
                type="number"
                min="1"
                max="50"
                class="w-full bg-gray-700 border border-gray-600 rounded px-4 py-2 focus:outline-none focus:border-squig-yellow"
              />
              <p class="text-sm text-gray-500 mt-1">
                {{ t('admin.newPlayerGamesThresholdNote') }}
              </p>
            </div>

            <div v-if="saveError" class="bg-red-900/30 border border-red-500 text-red-200 px-4 py-3 rounded">
              {{ saveError }}
            </div>

            <div v-if="saveSuccess" class="bg-green-900/30 border border-green-500 text-green-200 px-4 py-3 rounded">
              {{ t('admin.settingsSaved') }}
            </div>

            <button
              type="submit"
              :disabled="saving"
              class="w-full btn-primary py-3"
            >
              {{ saving ? t('common.saving') : t('admin.saveSettings') }}
            </button>
          </form>
        </div>
      </div>

      <!-- Matchups Tab -->
      <div v-show="activeTab === 'matchups'">
        <!-- Filter -->
        <div class="card mb-6">
          <div class="flex gap-4 items-center">
            <label class="text-sm text-gray-400">{{ t('admin.filter') }}:</label>
            <select
              v-model="matchupFilter"
              @change="fetchMatchups"
              class="bg-gray-700 border border-gray-600 rounded px-3 py-2 text-sm focus:outline-none focus:border-squig-yellow"
            >
              <option value="all">{{ t('admin.allMatchups') }}</option>
              <option value="pending">{{ t('admin.pendingMatchups') }}</option>
              <option value="revealed">{{ t('admin.revealedMatchups') }}</option>
            </select>
          </div>
        </div>

        <!-- Matchups Table -->
        <div class="card">
          <div v-if="matchupsLoading" class="text-center py-8">
            <p class="text-gray-400">{{ t('common.loading') }}</p>
          </div>
          <div v-else-if="matchups.length === 0" class="text-center py-8">
            <p class="text-gray-400">{{ t('admin.noMatchups') }}</p>
          </div>
          <div v-else class="overflow-x-auto">
            <table class="w-full text-sm">
              <thead>
                <tr class="text-gray-400 border-b border-gray-700">
                  <th class="text-left py-3 px-4">{{ t('admin.matchupId') }}</th>
                  <th class="text-left py-3 px-4">{{ t('admin.player1') }}</th>
                  <th class="text-left py-3 px-4">{{ t('admin.player2') }}</th>
                  <th class="text-center py-3 px-4">{{ t('admin.status') }}</th>
                  <th class="text-center py-3 px-4">{{ t('admin.result') }}</th>
                  <th class="text-right py-3 px-4">{{ t('admin.created') }}</th>
                </tr>
              </thead>
              <tbody>
                <tr
                  v-for="matchup in matchups"
                  :key="matchup.id"
                  class="border-b border-gray-800 hover:bg-gray-700/50"
                >
                  <td class="py-3 px-4">
                    <router-link
                      :to="`/matchup/${matchup.name}`"
                      class="text-squig-yellow hover:underline"
                    >
                      {{ matchup.name }}
                    </router-link>
                    <div v-if="matchup.title" class="text-xs text-gray-500">{{ matchup.title }}</div>
                  </td>
                  <td class="py-3 px-4">
                    <div class="flex items-center gap-2">
                      <span :class="matchup.player1_submitted ? 'text-green-400' : 'text-yellow-400'">
                        {{ matchup.player1_submitted ? '✓' : '⏳' }}
                      </span>
                      {{ matchup.player1_username || t('admin.anonymous') }}
                      <span v-if="matchup.is_revealed && matchup.player1_army_faction" class="text-xs text-gray-500">
                        ({{ matchup.player1_army_faction }})
                      </span>
                    </div>
                  </td>
                  <td class="py-3 px-4">
                    <div class="flex items-center gap-2">
                      <span :class="matchup.player2_submitted ? 'text-green-400' : 'text-yellow-400'">
                        {{ matchup.player2_submitted ? '✓' : '⏳' }}
                      </span>
                      {{ matchup.player2_username || t('admin.anonymous') }}
                      <span v-if="matchup.is_revealed && matchup.player2_army_faction" class="text-xs text-gray-500">
                        ({{ matchup.player2_army_faction }})
                      </span>
                    </div>
                  </td>
                  <td class="py-3 px-4 text-center">
                    <span v-if="matchup.is_revealed" class="text-green-400">{{ t('admin.revealed') }}</span>
                    <span v-else class="text-yellow-400">{{ t('admin.pending') }}</span>
                    <span v-if="!matchup.is_public" class="ml-2 text-xs text-gray-500">({{ t('admin.private') }})</span>
                  </td>
                  <td class="py-3 px-4 text-center">
                    <span v-if="matchup.result_status === 'confirmed'" class="text-green-400">
                      {{ matchup.player1_score }} - {{ matchup.player2_score }}
                    </span>
                    <span v-else-if="matchup.result_status === 'pending_confirmation'" class="text-yellow-400">
                      {{ matchup.player1_score }} - {{ matchup.player2_score }} ({{ t('admin.awaitingConfirm') }})
                    </span>
                    <span v-else class="text-gray-500">-</span>
                  </td>
                  <td class="py-3 px-4 text-right text-gray-400">{{ formatDate(matchup.created_at) }}</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>

    <!-- Delete Confirmation Modal -->
    <div v-if="deleteModal.show" class="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
      <div class="card max-w-md mx-4">
        <h3 class="text-xl font-bold mb-4">{{ t('admin.confirmDelete') }}</h3>
        <p class="text-gray-300 mb-6">
          {{ t('admin.deleteUserConfirm', { username: deleteModal.user?.username || deleteModal.user?.email }) }}
        </p>
        <div class="flex gap-4">
          <button @click="deleteModal.show = false" class="flex-1 btn-secondary">
            {{ t('common.cancel') }}
          </button>
          <button @click="deleteUser" class="flex-1 bg-red-600 hover:bg-red-700 text-white py-2 px-4 rounded">
            {{ t('admin.delete') }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRoute, useRouter } from 'vue-router'
import axios from 'axios'

const { t } = useI18n()
const route = useRoute()
const router = useRouter()
const API_URL = import.meta.env.VITE_API_URL || '/api'

const tabs = [
  { id: 'users', label: 'admin.usersTab' },
  { id: 'settings', label: 'admin.settingsTab' },
  { id: 'matchups', label: 'admin.matchupsTab' },
]

const activeTab = ref(route.params.tab || 'users')
const loading = ref(true)
const error = ref('')
const roleError = ref('')

// Users state
const users = ref([])
const stats = ref({
  total_users: 0,
  players: 0,
  organizers: 0,
  admins: 0,
})

// Settings state
const eloSettings = ref({
  k_factor: 32,
  new_player_k: 50,
  new_player_games: 5,
})
const saving = ref(false)
const saveError = ref('')
const saveSuccess = ref(false)

// Matchups state
const matchups = ref([])
const matchupsLoading = ref(false)
const matchupFilter = ref('all')

// Delete modal
const deleteModal = ref({
  show: false,
  user: null,
})

// Watch tab changes
watch(activeTab, (newTab) => {
  router.replace({ params: { tab: newTab } })
  if (newTab === 'matchups' && matchups.value.length === 0) {
    fetchMatchups()
  }
})

const fetchData = async () => {
  try {
    const [usersRes, statsRes, eloRes] = await Promise.all([
      axios.get(`${API_URL}/admin/users`),
      axios.get(`${API_URL}/admin/stats`),
      axios.get(`${API_URL}/admin/settings/elo`),
    ])

    users.value = usersRes.data.map(user => ({
      ...user,
      updating: false,
      saved: false,
      deleting: false,
      originalRole: user.role,
    }))
    stats.value = statsRes.data
    eloSettings.value = eloRes.data
  } catch (err) {
    if (err.response?.status === 403) {
      error.value = t('admin.accessDenied')
    } else {
      error.value = t('admin.failedToLoad')
    }
  } finally {
    loading.value = false
  }
}

const fetchMatchups = async () => {
  matchupsLoading.value = true
  try {
    const params = matchupFilter.value !== 'all' ? { status_filter: matchupFilter.value } : {}
    const response = await axios.get(`${API_URL}/admin/matchups`, { params })
    matchups.value = response.data
  } catch (err) {
    console.error('Failed to fetch matchups:', err)
  } finally {
    matchupsLoading.value = false
  }
}

const updateRole = async (user) => {
  if (user.role === user.originalRole) return

  user.updating = true
  user.saved = false
  roleError.value = ''

  try {
    await axios.patch(`${API_URL}/admin/users/${user.id}/role`, {
      role: user.role,
    })
    user.originalRole = user.role
    user.saved = true

    const statsRes = await axios.get(`${API_URL}/admin/stats`)
    stats.value = statsRes.data

    setTimeout(() => {
      user.saved = false
    }, 2000)
  } catch (err) {
    roleError.value = err.response?.data?.detail || t('admin.failedToUpdateRole')
    user.role = user.originalRole
    setTimeout(() => {
      roleError.value = ''
    }, 5000)
  } finally {
    user.updating = false
  }
}

const confirmDeleteUser = (user) => {
  deleteModal.value = {
    show: true,
    user,
  }
}

const deleteUser = async () => {
  const user = deleteModal.value.user
  if (!user) return

  user.deleting = true
  deleteModal.value.show = false

  try {
    await axios.delete(`${API_URL}/admin/users/${user.id}`)
    users.value = users.value.filter(u => u.id !== user.id)

    const statsRes = await axios.get(`${API_URL}/admin/stats`)
    stats.value = statsRes.data
  } catch (err) {
    roleError.value = err.response?.data?.detail || t('admin.failedToDelete')
    setTimeout(() => {
      roleError.value = ''
    }, 5000)
  } finally {
    user.deleting = false
  }
}

const saveEloSettings = async () => {
  saving.value = true
  saveError.value = ''
  saveSuccess.value = false

  try {
    await axios.patch(`${API_URL}/admin/settings/elo`, eloSettings.value)
    saveSuccess.value = true
    setTimeout(() => {
      saveSuccess.value = false
    }, 3000)
  } catch (err) {
    saveError.value = err.response?.data?.detail || t('admin.failedToSave')
  } finally {
    saving.value = false
  }
}

const formatDate = (dateString) => {
  return new Date(dateString).toLocaleDateString()
}

onMounted(() => {
  fetchData()
  if (activeTab.value === 'matchups') {
    fetchMatchups()
  }
})
</script>
