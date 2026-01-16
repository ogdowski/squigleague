<template>
  <div class="max-w-2xl mx-auto">
    <h1 class="text-3xl font-bold mb-6">New League</h1>

    <form @submit.prevent="createLeague" class="card space-y-6">
      <div>
        <label class="block text-sm font-medium text-gray-300 mb-2">League Name</label>
        <input
          v-model="form.name"
          type="text"
          required
          class="w-full bg-gray-700 border border-gray-600 rounded px-4 py-2 focus:outline-none focus:border-squig-yellow"
          placeholder="e.g. AoS League Season 1"
        />
      </div>

      <div>
        <label class="block text-sm font-medium text-gray-300 mb-2">Description (optional)</label>
        <textarea
          v-model="form.description"
          rows="3"
          class="w-full bg-gray-700 border border-gray-600 rounded px-4 py-2 focus:outline-none focus:border-squig-yellow"
          placeholder="League description..."
        ></textarea>
      </div>

      <div class="grid grid-cols-2 gap-4">
        <div>
          <label class="block text-sm font-medium text-gray-300 mb-2">Registration Start</label>
          <input
            v-model="form.registration_start"
            type="datetime-local"
            required
            class="w-full bg-gray-700 border border-gray-600 rounded px-4 py-2 focus:outline-none focus:border-squig-yellow"
          />
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-300 mb-2">Registration End</label>
          <input
            v-model="form.registration_end"
            type="datetime-local"
            required
            class="w-full bg-gray-700 border border-gray-600 rounded px-4 py-2 focus:outline-none focus:border-squig-yellow"
          />
        </div>
      </div>

      <div class="grid grid-cols-3 gap-4">
        <div>
          <label class="block text-sm font-medium text-gray-300 mb-2">Win Points</label>
          <input
            v-model.number="form.points_per_win"
            type="number"
            min="0"
            class="w-full bg-gray-700 border border-gray-600 rounded px-4 py-2 focus:outline-none focus:border-squig-yellow"
          />
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-300 mb-2">Draw Points</label>
          <input
            v-model.number="form.points_per_draw"
            type="number"
            min="0"
            class="w-full bg-gray-700 border border-gray-600 rounded px-4 py-2 focus:outline-none focus:border-squig-yellow"
          />
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-300 mb-2">Loss Points</label>
          <input
            v-model.number="form.points_per_loss"
            type="number"
            min="0"
            class="w-full bg-gray-700 border border-gray-600 rounded px-4 py-2 focus:outline-none focus:border-squig-yellow"
          />
        </div>
      </div>

      <div v-if="error" class="bg-red-900/30 border border-red-500 text-red-200 px-4 py-3 rounded">
        {{ error }}
      </div>

      <button
        type="submit"
        :disabled="submitting"
        class="w-full btn-primary py-3"
      >
        {{ submitting ? 'Creating...' : 'Create League' }}
      </button>
    </form>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'

const API_URL = import.meta.env.VITE_API_URL || '/api'
const router = useRouter()

const form = ref({
  name: '',
  description: '',
  registration_start: '',
  registration_end: '',
  points_per_win: 1000,
  points_per_draw: 600,
  points_per_loss: 200,
})

const submitting = ref(false)
const error = ref('')

const createLeague = async () => {
  submitting.value = true
  error.value = ''

  try {
    const payload = {
      ...form.value,
      registration_start: new Date(form.value.registration_start).toISOString(),
      registration_end: new Date(form.value.registration_end).toISOString(),
    }

    const response = await axios.post(`${API_URL}/league`, payload)
    router.push(`/league/${response.data.id}`)
  } catch (err) {
    error.value = err.response?.data?.detail || 'Failed to create league'
  } finally {
    submitting.value = false
  }
}
</script>
