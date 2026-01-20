<template>
  <div class="max-w-4xl mx-auto">
    <div v-if="loading" class="text-center py-12">
      <p class="text-xl text-gray-300">Loading matchup...</p>
    </div>

    <div v-else-if="error" class="card">
      <div class="bg-red-900/30 border border-red-500 text-red-200 px-4 py-3 rounded">
        {{ error }}
      </div>
    </div>

    <div v-else-if="matchup">
      <div class="card mb-6">
        <div class="flex items-center justify-between mb-4">
          <h1 class="text-3xl font-bold">Matchup: {{ matchup.name }}</h1>
          <span class="text-sm text-gray-400">
            Expires: {{ formatDate(matchup.expires_at) }}
          </span>
        </div>

        <div class="grid md:grid-cols-2 gap-4 mb-6">
          <div class="bg-gray-900 p-4 rounded">
            <div class="flex items-center gap-3 mb-2">
              <img
                v-if="matchup.player1_avatar"
                :src="matchup.player1_avatar"
                class="w-10 h-10 rounded-full"
                :alt="matchup.player1_username"
              />
              <div v-else class="w-10 h-10 rounded-full bg-gray-700 flex items-center justify-center text-gray-400">
                <svg class="w-6 h-6" fill="currentColor" viewBox="0 0 24 24">
                  <path d="M12 12c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm0 2c-2.67 0-8 1.34-8 4v2h16v-2c0-2.66-5.33-4-8-4z"/>
                </svg>
              </div>
              <h3 class="font-bold">
                {{ matchup.player1_username || 'Player 1' }}
              </h3>
            </div>
            <p :class="matchup.player1_submitted ? 'text-green-400' : 'text-gray-400'">
              {{ matchup.player1_submitted ? '✓ List submitted' : '○ Waiting for list' }}
            </p>
          </div>
          <div class="bg-gray-900 p-4 rounded">
            <div class="flex items-center gap-3 mb-2">
              <img
                v-if="matchup.player2_avatar"
                :src="matchup.player2_avatar"
                class="w-10 h-10 rounded-full"
                :alt="matchup.player2_username"
              />
              <div v-else class="w-10 h-10 rounded-full bg-gray-700 flex items-center justify-center text-gray-400">
                <svg class="w-6 h-6" fill="currentColor" viewBox="0 0 24 24">
                  <path d="M12 12c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm0 2c-2.67 0-8 1.34-8 4v2h16v-2c0-2.66-5.33-4-8-4z"/>
                </svg>
              </div>
              <h3 class="font-bold">
                {{ matchup.player2_username || 'Player 2' }}
              </h3>
            </div>
            <p :class="matchup.player2_submitted ? 'text-green-400' : 'text-gray-400'">
              {{ matchup.player2_submitted ? '✓ List submitted' : '○ Waiting for list' }}
            </p>
          </div>
        </div>
      </div>

      <div v-if="!matchup.is_revealed" class="card">
        <div class="mb-6">
          <div class="bg-blue-900/30 border border-blue-500 text-blue-200 px-4 py-3 rounded">
            Player 1 has submitted their army list. Submit yours to reveal both lists and the mission!
          </div>
        </div>

        <h2 class="text-2xl font-bold mb-4">Submit Your Army List</h2>

        <form @submit.prevent="submitList" class="space-y-4">
          <div>
            <label class="block text-sm font-medium mb-2">
              Paste your army list here
            </label>
            <textarea
              v-model="armyList"
              rows="15"
              class="input-field w-full font-mono text-sm"
              placeholder="Paste your army list here..."
              required
            ></textarea>
          </div>

          <div v-if="submitError" class="bg-red-900/30 border border-red-500 text-red-200 px-4 py-3 rounded">
            {{ submitError }}
          </div>

          <div v-if="submitSuccess" class="bg-green-900/30 border border-green-500 text-green-200 px-4 py-3 rounded">
            List submitted successfully!
            <span v-if="!matchup.is_revealed">Waiting for reveal...</span>
          </div>

          <button
            type="submit"
            :disabled="submitting"
            class="btn-primary w-full"
          >
            {{ submitting ? 'Submitting...' : 'Submit List' }}
          </button>
        </form>
      </div>

      <div v-else class="space-y-6">
        <div class="card">
          <div class="bg-green-900/30 border border-green-500 text-green-200 px-4 py-3 rounded mb-6">
            Both lists have been submitted! The matchup is revealed.
          </div>

          <div class="mb-8">
            <h2 class="text-2xl font-bold mb-4 text-squig-yellow">Map Assignment</h2>
            <BattlePlanDisplay
              :map-name="reveal.map_name"
              :map-image="reveal.map_image"
              :battle-plan="revealBattlePlan"
            />
          </div>

          <div class="grid md:grid-cols-2 gap-6">
            <div>
              <div class="flex items-center gap-3 mb-3">
                <img
                  v-if="reveal.player1_avatar"
                  :src="reveal.player1_avatar"
                  class="w-8 h-8 rounded-full"
                  :alt="reveal.player1_username"
                />
                <div v-else class="w-8 h-8 rounded-full bg-gray-700 flex items-center justify-center text-gray-400">
                  <svg class="w-5 h-5" fill="currentColor" viewBox="0 0 24 24">
                    <path d="M12 12c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm0 2c-2.67 0-8 1.34-8 4v2h16v-2c0-2.66-5.33-4-8-4z"/>
                  </svg>
                </div>
                <h3 class="text-xl font-bold">
                  {{ reveal.player1_username || 'Player 1' }}
                </h3>
              </div>
              <div class="bg-gray-900 p-4 rounded">
                <pre class="whitespace-pre-wrap font-mono text-sm text-gray-300">{{ reveal.player1_list }}</pre>
              </div>
            </div>

            <div>
              <div class="flex items-center gap-3 mb-3">
                <img
                  v-if="reveal.player2_avatar"
                  :src="reveal.player2_avatar"
                  class="w-8 h-8 rounded-full"
                  :alt="reveal.player2_username"
                />
                <div v-else class="w-8 h-8 rounded-full bg-gray-700 flex items-center justify-center text-gray-400">
                  <svg class="w-5 h-5" fill="currentColor" viewBox="0 0 24 24">
                    <path d="M12 12c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm0 2c-2.67 0-8 1.34-8 4v2h16v-2c0-2.66-5.33-4-8-4z"/>
                  </svg>
                </div>
                <h3 class="text-xl font-bold">
                  {{ reveal.player2_username || 'Player 2' }}
                </h3>
              </div>
              <div class="bg-gray-900 p-4 rounded">
                <pre class="whitespace-pre-wrap font-mono text-sm text-gray-300">{{ reveal.player2_list }}</pre>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import axios from 'axios'
import BattlePlanDisplay from '@/components/BattlePlanDisplay.vue'

const API_URL = import.meta.env.VITE_API_URL || '/api'
const route = useRoute()

const loading = ref(true)
const error = ref('')
const matchup = ref(null)
const reveal = ref(null)

const armyList = ref('')
const submitting = ref(false)
const submitError = ref('')
const submitSuccess = ref(false)

// Build battle plan object from reveal data (comes from API)
const revealBattlePlan = computed(() => {
  if (!reveal.value) return null
  return {
    objectives: reveal.value.objectives,
    scoring: reveal.value.scoring,
    underdog_ability: reveal.value.underdog_ability,
    objective_types: reveal.value.objective_types,
  }
})

const fetchMatchup = async () => {
  try {
    const response = await axios.get(`${API_URL}/matchup/${route.params.name}`)
    matchup.value = response.data

    if (response.data.is_revealed) {
      await fetchReveal()
    }
  } catch (err) {
    if (err.response?.status === 404) {
      error.value = 'Matchup not found'
    } else if (err.response?.status === 410) {
      error.value = 'This matchup has expired'
    } else {
      error.value = 'Failed to load matchup'
    }
  } finally {
    loading.value = false
  }
}

const fetchReveal = async () => {
  try {
    const response = await axios.get(`${API_URL}/matchup/${route.params.name}/reveal`)
    reveal.value = response.data
  } catch (err) {
    console.error('Failed to fetch reveal:', err)
  }
}

const submitList = async () => {
  submitError.value = ''
  submitSuccess.value = false
  submitting.value = true

  try {
    const response = await axios.post(
      `${API_URL}/matchup/${route.params.name}/submit`,
      { army_list: armyList.value }
    )

    submitSuccess.value = true
    armyList.value = ''

    if (response.data.is_revealed) {
      await fetchMatchup()
    } else {
      matchup.value.player1_submitted = true
    }
  } catch (err) {
    submitError.value = err.response?.data?.detail || 'Failed to submit list'
  } finally {
    submitting.value = false
  }
}

const formatDate = (dateString) => {
  return new Date(dateString).toLocaleString()
}

onMounted(() => {
  fetchMatchup()
})
</script>
