<template>
  <div class="max-w-2xl mx-auto">
    <h1 class="text-3xl font-bold mb-6">{{ t('leagueCreate.title') }}</h1>

    <form @submit.prevent="createLeague" class="card space-y-6">
      <div>
        <label class="block text-sm font-medium text-gray-300 mb-2">{{ t('leagueCreate.leagueName') }}</label>
        <input
          v-model="form.name"
          type="text"
          required
          class="w-full bg-gray-700 border border-gray-600 rounded px-4 py-2 focus:outline-none focus:border-squig-yellow"
          :placeholder="t('leagueCreate.leagueNamePlaceholder')"
        />
      </div>

      <div>
        <label class="block text-sm font-medium text-gray-300 mb-2">{{ t('leagueCreate.descriptionOptional') }}</label>
        <textarea
          v-model="form.description"
          rows="6"
          maxlength="10000"
          class="w-full bg-gray-700 border border-gray-600 rounded px-4 py-2 focus:outline-none focus:border-squig-yellow"
          :placeholder="t('leagueCreate.descriptionPlaceholder')"
        ></textarea>
        <div class="text-xs text-gray-500 text-right mt-1">
          <span :class="form.description.length > 9000 ? 'text-yellow-400' : ''">{{ form.description.length }}</span> / 10000
        </div>
      </div>

      <div>
        <label class="block text-sm font-medium text-gray-300 mb-2">{{ t('leagueCreate.registrationEnd') }}</label>
        <DateHourPicker v-model="form.registration_end" required />
      </div>

      <!-- Player Limits -->
      <div class="grid grid-cols-2 gap-4">
        <div>
          <label class="block text-sm font-medium text-gray-300 mb-2">{{ t('leagueCreate.minPlayers') }}</label>
          <input
            v-model.number="form.min_players"
            type="number"
            min="4"
            required
            class="w-full bg-gray-700 border border-gray-600 rounded px-4 py-2 focus:outline-none focus:border-squig-yellow"
          />
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-300 mb-2">{{ t('leagueCreate.maxPlayersOptional') }}</label>
          <input
            v-model.number="form.max_players"
            type="number"
            min="4"
            :placeholder="t('leagueCreate.noLimit')"
            class="w-full bg-gray-700 border border-gray-600 rounded px-4 py-2 focus:outline-none focus:border-squig-yellow"
          />
        </div>
      </div>

      <!-- Group Size -->
      <div class="grid grid-cols-2 gap-4">
        <div>
          <label class="block text-sm font-medium text-gray-300 mb-2">{{ t('leagueCreate.minGroupSize') }}</label>
          <input
            v-model.number="form.min_group_size"
            type="number"
            min="2"
            max="10"
            class="w-full bg-gray-700 border border-gray-600 rounded px-4 py-2 focus:outline-none focus:border-squig-yellow"
          />
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-300 mb-2">{{ t('leagueCreate.maxGroupSize') }}</label>
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
        <label class="block text-sm font-medium text-gray-300 mb-2">{{ t('leagueCreate.daysPerMatch') }}</label>
        <input
          v-model.number="form.days_per_match"
          type="number"
          min="1"
          max="60"
          class="w-full bg-gray-700 border border-gray-600 rounded px-4 py-2 focus:outline-none focus:border-squig-yellow"
        />
        <p class="text-xs text-gray-500 mt-1">{{ t('leagueCreate.daysPerMatchNote') }}</p>
      </div>

      <!-- Knockout Phase -->
      <div class="flex items-center gap-3">
        <input
          v-model="form.has_knockout_phase"
          type="checkbox"
          id="has_knockout"
          class="w-5 h-5 bg-gray-700 border-gray-600 rounded focus:ring-squig-yellow"
        />
        <label for="has_knockout" class="text-sm font-medium text-gray-300">{{ t('leagueCreate.enableKnockout') }}</label>
      </div>

      <div v-if="form.has_knockout_phase">
        <div class="flex items-center gap-2 mb-2">
          <label class="block text-sm font-medium text-gray-300">{{ t('leagueCreate.knockoutSize') }}</label>
          <div class="relative group">
            <svg class="w-4 h-4 text-gray-400 cursor-help" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <circle cx="12" cy="12" r="10" stroke-width="2"/>
              <path stroke-width="2" d="M12 16v-4m0-4h.01"/>
            </svg>
            <div class="absolute left-6 top-0 w-64 p-3 bg-gray-800 border border-gray-600 rounded shadow-lg text-xs text-gray-300 hidden group-hover:block z-10">
              <p class="font-semibold mb-2">{{ t('leagueCreate.knockoutSizeLimits') }}</p>
              <ul class="space-y-1">
                <li>{{ t('leagueCreate.players4to7') }}</li>
                <li>{{ t('leagueCreate.players8to15') }}</li>
                <li>{{ t('leagueCreate.players16to47') }}</li>
                <li>{{ t('leagueCreate.players48plus') }}</li>
              </ul>
            </div>
          </div>
        </div>
        <div class="relative">
          <button
            type="button"
            @click="showKnockoutDropdown = !showKnockoutDropdown"
            class="w-full bg-gray-700 border border-gray-600 rounded px-4 py-2 focus:outline-none focus:border-squig-yellow flex items-center justify-between text-left"
          >
            <span>{{ getKnockoutLabel(form.knockout_size) }}</span>
            <svg
              class="w-5 h-5 text-gray-400 transition-transform"
              :class="{ 'rotate-180': showKnockoutDropdown }"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
            </svg>
          </button>
          <div
            v-if="showKnockoutDropdown"
            class="absolute left-0 right-0 top-full mt-1 bg-gray-800 border border-gray-700 rounded-lg shadow-xl z-30 max-h-60 overflow-y-auto"
          >
            <button
              v-for="option in knockoutOptions"
              :key="option.value"
              type="button"
              @click="selectKnockout(option.value)"
              :class="[
                'w-full text-left px-4 py-3 hover:bg-gray-700 first:rounded-t-lg last:rounded-b-lg',
                form.knockout_size === option.value ? 'text-squig-yellow bg-gray-700/50' : 'text-white'
              ]"
            >
              {{ t(option.labelKey) }}
            </button>
          </div>
        </div>
      </div>

      <!-- Army Lists -->
      <div class="border-t border-gray-700 pt-6">
        <h3 class="text-lg font-semibold mb-3">{{ t('leagueCreate.armyLists') }}</h3>
        <p class="text-xs text-gray-500 mb-4">{{ t('leagueCreate.armyListsNote') }}</p>

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
              {{ t('leagueCreate.groupPhaseLists') }}
              <span class="text-xs text-gray-500 block">{{ t('leagueCreate.groupPhaseListsNote') }}</span>
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
              {{ t('leagueCreate.knockoutPhaseLists') }}
              <span class="text-xs text-gray-500 block">
                {{ form.has_group_phase_lists ? t('leagueCreate.knockoutPhaseListsAutoEnabled') : t('leagueCreate.knockoutPhaseListsNote') }}
              </span>
            </label>
          </div>
        </div>
      </div>

      <!-- Voting -->
      <div class="border-t border-gray-700 pt-6">
        <h3 class="text-lg font-semibold mb-3">{{ t('leagueCreate.voting') }}</h3>
        <div class="flex items-center gap-3">
          <input
            v-model="form.voting_enabled"
            type="checkbox"
            id="voting_enabled"
            class="w-5 h-5 bg-gray-700 border-gray-600 rounded focus:ring-squig-yellow"
          />
          <label for="voting_enabled" class="text-sm font-medium text-gray-300">
            {{ t('leagueCreate.enableVoting') }}
            <span class="text-xs text-gray-500 block">{{ t('leagueCreate.enableVotingNote') }}</span>
          </label>
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
        {{ submitting ? t('leagueCreate.creating') : t('leagueCreate.createLeague') }}
      </button>
    </form>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import axios from 'axios'
import DateHourPicker from '@/components/DateHourPicker.vue'

const { t } = useI18n()
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
  voting_enabled: false,
})

const submitting = ref(false)
const error = ref('')
const showKnockoutDropdown = ref(false)

const knockoutOptions = [
  { value: null, labelKey: 'leagueCreate.autoBasedOnPlayers' },
  { value: 2, labelKey: 'leagueCreate.top2FinalOnly' },
  { value: 4, labelKey: 'leagueCreate.top4' },
  { value: 8, labelKey: 'leagueCreate.top8' },
  { value: 16, labelKey: 'leagueCreate.top16' },
  { value: 32, labelKey: 'leagueCreate.top32' },
]

const getKnockoutLabel = (value) => {
  const option = knockoutOptions.find(o => o.value === value)
  return option ? t(option.labelKey) : value
}

const selectKnockout = (value) => {
  form.value.knockout_size = value
  showKnockoutDropdown.value = false
}

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
      registration_end: form.value.registration_end + ':00',
      min_players: form.value.min_players,
      max_players: form.value.max_players || null,
      min_group_size: form.value.min_group_size,
      max_group_size: form.value.max_group_size,
      days_per_match: form.value.days_per_match,
      has_knockout_phase: form.value.has_knockout_phase,
      knockout_size: form.value.has_knockout_phase ? form.value.knockout_size : null,
      has_group_phase_lists: form.value.has_group_phase_lists,
      has_knockout_phase_lists: form.value.has_knockout_phase ? form.value.has_knockout_phase_lists : false,
      voting_enabled: form.value.voting_enabled,
    }

    const response = await axios.post(`${API_URL}/league`, payload)
    router.push(`/league/${response.data.id}`)
  } catch (err) {
    error.value = err.response?.data?.detail || t('leagueCreate.failedToCreate')
  } finally {
    submitting.value = false
  }
}
</script>
