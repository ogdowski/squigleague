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
            <h3 class="font-bold mb-2">
              Player 1
              <span v-if="matchup.player1_username" class="text-squig-yellow ml-2">
                ({{ matchup.player1_username }})
              </span>
            </h3>
            <p :class="matchup.player1_submitted ? 'text-green-400' : 'text-gray-400'">
              {{ matchup.player1_submitted ? '✓ List submitted' : '○ Waiting for list' }}
            </p>
          </div>
          <div class="bg-gray-900 p-4 rounded">
            <h3 class="font-bold mb-2">
              Player 2
              <span v-if="matchup.player2_username" class="text-squig-yellow ml-2">
                ({{ matchup.player2_username }})
              </span>
            </h3>
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
            <div class="bg-gray-900 p-6 rounded text-center">
              <p class="text-3xl font-bold">{{ reveal.map_name }}</p>
            </div>
          </div>

          <div class="grid md:grid-cols-2 gap-6">
            <div>
              <h3 class="text-xl font-bold mb-3">
                Player 1 List
                <span v-if="reveal.player1_username" class="text-squig-yellow text-base ml-2">
                  ({{ reveal.player1_username }})
                </span>
              </h3>
              <div class="bg-gray-900 p-4 rounded">
                <pre class="whitespace-pre-wrap font-mono text-sm text-gray-300">{{ reveal.player1_list }}</pre>
              </div>
            </div>

            <div>
              <h3 class="text-xl font-bold mb-3">
                Player 2 List
                <span v-if="reveal.player2_username" class="text-squig-yellow text-base ml-2">
                  ({{ reveal.player2_username }})
                </span>
              </h3>
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
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import axios from 'axios'

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
