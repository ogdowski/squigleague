<template>
  <div class="max-w-2xl mx-auto">
    <h1 class="text-3xl font-bold mb-6">Admin Panel - Settings</h1>

    <div v-if="loading" class="text-center py-12">
      <p class="text-xl text-gray-300">Loading...</p>
    </div>

    <div v-else-if="error" class="card">
      <div class="bg-red-900/30 border border-red-500 text-red-200 px-4 py-3 rounded">
        {{ error }}
      </div>
    </div>

    <div v-else class="space-y-6">
      <!-- ELO Settings -->
      <div class="card">
        <h2 class="text-xl font-bold mb-4">ELO Settings</h2>

        <form @submit.prevent="saveEloSettings" class="space-y-4">
          <div>
            <label class="block text-sm font-medium text-gray-300 mb-2">
              Global K-Factor
            </label>
            <input
              v-model.number="eloSettings.k_factor"
              type="number"
              min="1"
              max="100"
              class="w-full bg-gray-700 border border-gray-600 rounded px-4 py-2 focus:outline-none focus:border-squig-yellow"
            />
            <p class="text-sm text-gray-500 mt-1">
              K-factor for experienced players (default: 32)
            </p>
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-300 mb-2">
              New Player K-Factor
            </label>
            <input
              v-model.number="eloSettings.new_player_k"
              type="number"
              min="1"
              max="100"
              class="w-full bg-gray-700 border border-gray-600 rounded px-4 py-2 focus:outline-none focus:border-squig-yellow"
            />
            <p class="text-sm text-gray-500 mt-1">
              Higher K-factor for new players (default: 50)
            </p>
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-300 mb-2">
              New Player Games Threshold
            </label>
            <input
              v-model.number="eloSettings.new_player_games"
              type="number"
              min="1"
              max="50"
              class="w-full bg-gray-700 border border-gray-600 rounded px-4 py-2 focus:outline-none focus:border-squig-yellow"
            />
            <p class="text-sm text-gray-500 mt-1">
              Number of games before switching to global K-factor (default: 5)
            </p>
          </div>

          <div v-if="saveError" class="bg-red-900/30 border border-red-500 text-red-200 px-4 py-3 rounded">
            {{ saveError }}
          </div>

          <div v-if="saveSuccess" class="bg-green-900/30 border border-green-500 text-green-200 px-4 py-3 rounded">
            Settings saved successfully
          </div>

          <button
            type="submit"
            :disabled="saving"
            class="w-full btn-primary py-3"
          >
            {{ saving ? 'Saving...' : 'Save Settings' }}
          </button>
        </form>
      </div>

      <!-- Navigation -->
      <div class="card">
        <h3 class="text-lg font-medium mb-3">Admin Navigation</h3>
        <div class="flex gap-4">
          <router-link to="/admin/users" class="btn-secondary">
            Manage Users
          </router-link>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'

const API_URL = import.meta.env.VITE_API_URL || '/api'

const loading = ref(true)
const error = ref('')
const saving = ref(false)
const saveError = ref('')
const saveSuccess = ref(false)

const eloSettings = ref({
  k_factor: 32,
  new_player_k: 50,
  new_player_games: 5,
})

const fetchSettings = async () => {
  try {
    const response = await axios.get(`${API_URL}/admin/settings/elo`)
    eloSettings.value = response.data
  } catch (err) {
    if (err.response?.status === 403) {
      error.value = 'Access denied. Only admins can access this page.'
    } else {
      error.value = 'Failed to load settings'
    }
  } finally {
    loading.value = false
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
    saveError.value = err.response?.data?.detail || 'Failed to save settings'
  } finally {
    saving.value = false
  }
}

onMounted(() => {
  fetchSettings()
})
</script>
