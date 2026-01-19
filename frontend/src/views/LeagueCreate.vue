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

      <div>
        <label class="block text-sm font-medium text-gray-300 mb-2">Registration End</label>
        <DateHourPicker v-model="form.registration_end" required />
      </div>

      <!-- Player Limits -->
      <div class="grid grid-cols-2 gap-4">
        <div>
          <label class="block text-sm font-medium text-gray-300 mb-2">Min Players</label>
          <input
            v-model.number="form.min_players"
            type="number"
            min="4"
            required
            class="w-full bg-gray-700 border border-gray-600 rounded px-4 py-2 focus:outline-none focus:border-squig-yellow"
          />
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-300 mb-2">Max Players (optional)</label>
          <input
            v-model.number="form.max_players"
            type="number"
            min="4"
            :placeholder="'No limit'"
            class="w-full bg-gray-700 border border-gray-600 rounded px-4 py-2 focus:outline-none focus:border-squig-yellow"
          />
        </div>
      </div>

      <!-- Group Size -->
      <div class="grid grid-cols-2 gap-4">
        <div>
          <label class="block text-sm font-medium text-gray-300 mb-2">Min Group Size</label>
          <input
            v-model.number="form.min_group_size"
            type="number"
            min="2"
            max="10"
            class="w-full bg-gray-700 border border-gray-600 rounded px-4 py-2 focus:outline-none focus:border-squig-yellow"
          />
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-300 mb-2">Max Group Size</label>
          <input
            v-model.number="form.max_group_size"
            type="number"
            min="2"
            max="10"
            class="w-full bg-gray-700 border border-gray-600 rounded px-4 py-2 focus:outline-none focus:border-squig-yellow"
          />
        </div>
      </div>

      <!-- Scheduling -->
      <div>
        <label class="block text-sm font-medium text-gray-300 mb-2">Days per Match</label>
        <input
          v-model.number="form.days_per_match"
          type="number"
          min="1"
          max="60"
          class="w-full bg-gray-700 border border-gray-600 rounded px-4 py-2 focus:outline-none focus:border-squig-yellow"
        />
        <p class="text-xs text-gray-500 mt-1">Time allowed for each match round (group and knockout)</p>
      </div>

      <!-- Knockout Phase -->
      <div class="flex items-center gap-3">
        <input
          v-model="form.has_knockout_phase"
          type="checkbox"
          id="has_knockout"
          class="w-5 h-5 bg-gray-700 border-gray-600 rounded focus:ring-squig-yellow"
        />
        <label for="has_knockout" class="text-sm font-medium text-gray-300">Enable Knockout Phase</label>
      </div>

      <div v-if="form.has_knockout_phase">
        <div class="flex items-center gap-2 mb-2">
          <label class="block text-sm font-medium text-gray-300">Knockout Size</label>
          <div class="relative group">
            <svg class="w-4 h-4 text-gray-400 cursor-help" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <circle cx="12" cy="12" r="10" stroke-width="2"/>
              <path stroke-width="2" d="M12 16v-4m0-4h.01"/>
            </svg>
            <div class="absolute left-6 top-0 w-64 p-3 bg-gray-800 border border-gray-600 rounded shadow-lg text-xs text-gray-300 hidden group-hover:block z-10">
              <p class="font-semibold mb-2">Knockout size limits by player count:</p>
              <ul class="space-y-1">
                <li>4-7 players: Top 2 only (final)</li>
                <li>8-15 players: Default Top 4, max Top 8</li>
                <li>16-47 players: Default Top 8, max Top 16</li>
                <li>48+ players: Default Top 16, max Top 32</li>
              </ul>
            </div>
          </div>
        </div>
        <select
          v-model="form.knockout_size"
          class="w-full bg-gray-700 border border-gray-600 rounded px-4 py-2 focus:outline-none focus:border-squig-yellow"
        >
          <option :value="null">Auto (based on player count)</option>
          <option :value="2">Top 2 (Final only)</option>
          <option :value="4">Top 4</option>
          <option :value="8">Top 8</option>
          <option :value="16">Top 16</option>
          <option :value="32">Top 32</option>
        </select>
      </div>

      <!-- Army Lists -->
      <div class="border-t border-gray-700 pt-6">
        <h3 class="text-lg font-semibold mb-3">Army Lists</h3>
        <p class="text-xs text-gray-500 mb-4">Choose when players need to submit army lists.</p>

        <div class="space-y-3">
          <div class="flex items-center gap-3">
            <input
              v-model="form.has_group_phase_lists"
              @change="onGroupListsChange"
              type="checkbox"
              id="has_group_lists"
              class="w-5 h-5 bg-gray-700 border-gray-600 rounded focus:ring-squig-yellow"
            />
            <label for="has_group_lists" class="text-sm font-medium text-gray-300">
              Group Phase Lists
              <span class="text-xs text-gray-500 block">Players submit lists before league starts</span>
            </label>
          </div>

          <div v-if="form.has_knockout_phase" class="flex items-center gap-3">
            <input
              v-model="form.has_knockout_phase_lists"
              type="checkbox"
              id="has_knockout_lists"
              :disabled="form.has_group_phase_lists"
              class="w-5 h-5 bg-gray-700 border-gray-600 rounded focus:ring-squig-yellow disabled:opacity-50"
            />
            <label for="has_knockout_lists" class="text-sm font-medium text-gray-300">
              Knockout Phase Lists
              <span class="text-xs text-gray-500 block">
                {{ form.has_group_phase_lists ? 'Auto-enabled when group lists are on' : 'Players submit lists after group phase ends' }}
              </span>
            </label>
          </div>
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
import DateHourPicker from '@/components/DateHourPicker.vue'

const API_URL = import.meta.env.VITE_API_URL || '/api'
const router = useRouter()

const form = ref({
  name: '',
  description: '',
  registration_end: '',
  min_players: 8,
  max_players: null,
  min_group_size: 4,
  max_group_size: 6,
  days_per_match: 14,
  has_knockout_phase: true,
  knockout_size: null,
  has_group_phase_lists: false,
  has_knockout_phase_lists: true,
})

const submitting = ref(false)
const error = ref('')

const onGroupListsChange = () => {
  if (form.value.has_group_phase_lists) {
    form.value.has_knockout_phase_lists = true
  }
}

const createLeague = async () => {
  submitting.value = true
  error.value = ''

  try {
    const payload = {
      name: form.value.name,
      description: form.value.description || null,
      registration_end: new Date(form.value.registration_end).toISOString(),
      min_players: form.value.min_players,
      max_players: form.value.max_players || null,
      min_group_size: form.value.min_group_size,
      max_group_size: form.value.max_group_size,
      days_per_match: form.value.days_per_match,
      has_knockout_phase: form.value.has_knockout_phase,
      knockout_size: form.value.has_knockout_phase ? form.value.knockout_size : null,
      has_group_phase_lists: form.value.has_group_phase_lists,
      has_knockout_phase_lists: form.value.has_knockout_phase ? form.value.has_knockout_phase_lists : false,
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
