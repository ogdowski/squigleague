<template>
  <div class="max-w-2xl mx-auto">
    <div v-if="loading" class="text-center py-12">
      <p class="text-xl text-gray-300">{{ t('common.loading') }}</p>
    </div>

    <div v-else-if="!canEdit" class="card">
      <div class="bg-red-900/30 border border-red-500 text-red-200 px-4 py-3 rounded">
        {{ t('leagueSettings.noPermission') }}
      </div>
    </div>

    <div v-else>
      <div class="flex items-center justify-between mb-6">
        <h1 class="text-3xl font-bold">{{ t('leagueSettings.title') }}</h1>
        <router-link :to="`/league/${leagueId}`" class="text-gray-400 hover:text-white">
          {{ t('leagueSettings.backToLeague') }}
        </router-link>
      </div>

      <form @submit.prevent="saveSettings" class="card space-y-6">
        <div>
          <label class="block text-sm font-medium text-gray-300 mb-2">{{ t('leagueSettings.leagueName') }}</label>
          <input
            v-model="form.name"
            type="text"
            required
            class="w-full bg-gray-700 border border-gray-600 rounded px-4 py-2 focus:outline-none focus:border-squig-yellow"
          />
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-300 mb-2">{{ t('leagueSettings.description') }}</label>
          <textarea
            v-model="form.description"
            rows="3"
            class="w-full bg-gray-700 border border-gray-600 rounded px-4 py-2 focus:outline-none focus:border-squig-yellow"
          ></textarea>
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-300 mb-2">{{ t('leagueSettings.daysPerMatch') }}</label>
          <input
            v-model.number="form.days_per_match"
            type="number"
            min="1"
            max="60"
            class="w-full bg-gray-700 border border-gray-600 rounded px-4 py-2 focus:outline-none focus:border-squig-yellow"
          />
          <p class="text-xs text-gray-500 mt-1">{{ t('leagueSettings.daysPerMatchNote') }}</p>
        </div>

        <div v-if="league?.has_knockout_phase">
          <div class="flex items-center gap-2 mb-2">
            <label class="block text-sm font-medium text-gray-300">{{ t('leagueSettings.knockoutSize') }}</label>
            <div class="relative group">
              <svg class="w-4 h-4 text-gray-400 cursor-help" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <circle cx="12" cy="12" r="10" stroke-width="2"/>
                <path stroke-width="2" d="M12 16v-4m0-4h.01"/>
              </svg>
              <div class="absolute left-6 top-0 w-64 p-3 bg-gray-800 border border-gray-600 rounded shadow-lg text-xs text-gray-300 hidden group-hover:block z-10">
                <p class="font-semibold mb-2">{{ t('leagueSettings.knockoutSizeLimits') }}</p>
                <ul class="space-y-1">
                  <li>{{ t('leagueSettings.players4to7') }}</li>
                  <li>{{ t('leagueSettings.players8to15') }}</li>
                  <li>{{ t('leagueSettings.players16to47') }}</li>
                  <li>{{ t('leagueSettings.players48plus') }}</li>
                </ul>
              </div>
            </div>
          </div>
          <select
            v-model="form.knockout_size"
            class="w-full bg-gray-700 border border-gray-600 rounded px-4 py-2 focus:outline-none focus:border-squig-yellow"
          >
            <option :value="null">{{ t('leagueSettings.autoBasedOnPlayers') }}</option>
            <option :value="2">{{ t('leagueSettings.top2FinalOnly') }}</option>
            <option :value="4">{{ t('leagueSettings.top4') }}</option>
            <option :value="8">{{ t('leagueSettings.top8') }}</option>
            <option :value="16">{{ t('leagueSettings.top16') }}</option>
            <option :value="32">{{ t('leagueSettings.top32') }}</option>
          </select>
        </div>

        <!-- Status (for finishing league) -->
        <div v-if="league?.status !== 'registration'">
          <label class="block text-sm font-medium text-gray-300 mb-2">{{ t('leagueSettings.leagueStatus') }}</label>
          <select
            v-model="form.status"
            class="w-full bg-gray-700 border border-gray-600 rounded px-4 py-2 focus:outline-none focus:border-squig-yellow"
          >
            <option value="group_phase">{{ t('leagues.groupPhase') }}</option>
            <option value="knockout_phase">{{ t('leagues.knockoutPhase') }}</option>
            <option value="finished">{{ t('leagues.finished') }}</option>
          </select>
        </div>

        <!-- Phase Dates (editable) -->
        <div v-if="league?.status !== 'registration'" class="border-t border-gray-700 pt-6">
          <h3 class="text-lg font-semibold mb-3">{{ t('leagueSettings.phaseDates') }}</h3>
          <p class="text-xs text-gray-500 mb-4">{{ t('leagueSettings.phaseDatesNote') }}</p>

          <div class="grid grid-cols-2 gap-4 mb-4">
            <div>
              <label class="block text-sm font-medium text-gray-300 mb-2">{{ t('leagueSettings.groupPhaseEnds') }}</label>
              <DateHourPicker v-model="form.group_phase_end" />
            </div>
            <div v-if="league?.has_knockout_phase">
              <label class="block text-sm font-medium text-gray-300 mb-2">{{ t('leagueSettings.knockoutEnds') }}</label>
              <DateHourPicker v-model="form.knockout_phase_end" />
            </div>
          </div>

          <button
            type="button"
            @click="recalculateDates"
            :disabled="recalculating"
            class="btn-secondary text-sm"
          >
            {{ recalculating ? t('leagueSettings.recalculating') : t('leagueSettings.autoCalculate') }}
          </button>
        </div>

        <div v-if="error" class="bg-red-900/30 border border-red-500 text-red-200 px-4 py-3 rounded">
          {{ error }}
        </div>

        <div v-if="success" class="bg-green-900/30 border border-green-500 text-green-200 px-4 py-3 rounded">
          {{ success }}
        </div>

        <button
          type="submit"
          :disabled="saving"
          class="w-full btn-primary py-3"
        >
          {{ saving ? t('leagueSettings.saving') : t('leagueSettings.saveSettings') }}
        </button>
      </form>

      <!-- Danger Zone -->
      <div v-if="league?.status !== 'cancelled'" class="card mt-6 border-red-500/50">
        <h3 class="text-lg font-bold text-red-400 mb-4">{{ t('leagueSettings.dangerZone') }}</h3>
        <p class="text-sm text-gray-400 mb-4">
          {{ t('leagueSettings.cancelLeagueWarning') }}
        </p>
        <button
          @click="showCancelModal = true"
          class="btn-secondary border-red-500 text-red-400 hover:bg-red-900/30"
        >
          {{ t('leagueSettings.cancelLeague') }}
        </button>
      </div>

      <div v-else class="card mt-6 bg-red-900/20 border-red-500/50">
        <p class="text-red-400">{{ t('leagueSettings.leagueCancelled') }}</p>
      </div>
    </div>

    <!-- Cancel Confirmation Modal -->
    <div v-if="showCancelModal" class="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
      <div class="bg-gray-800 rounded-lg p-6 max-w-md w-full mx-4">
        <h3 class="text-xl font-bold text-red-400 mb-4">{{ t('leagueSettings.cancelLeague') }}</h3>
        <p class="text-gray-300 mb-6">
          {{ t('leagueSettings.cancelLeagueConfirm') }} <strong>{{ league?.name }}</strong>?
          {{ t('leagueSettings.cancelLeagueNote') }}
        </p>
        <div class="flex gap-3">
          <button
            @click="showCancelModal = false"
            class="flex-1 btn-secondary"
          >
            {{ t('leagueSettings.keepLeague') }}
          </button>
          <button
            @click="cancelLeague"
            :disabled="cancelling"
            class="flex-1 btn-primary bg-red-600 hover:bg-red-700"
          >
            {{ cancelling ? t('leagueSettings.cancelling') : t('leagueSettings.cancelLeague') }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { useAuthStore } from '../stores/auth'
import axios from 'axios'
import DateHourPicker from '@/components/DateHourPicker.vue'

const { t } = useI18n()
const API_URL = import.meta.env.VITE_API_URL || '/api'
const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()

const leagueId = computed(() => route.params.id)
const loading = ref(true)
const saving = ref(false)
const recalculating = ref(false)
const cancelling = ref(false)
const showCancelModal = ref(false)
const error = ref('')
const success = ref('')
const league = ref(null)

const form = ref({
  name: '',
  description: '',
  days_per_match: 14,
  knockout_size: null,
  status: '',
  group_phase_end: '',
  knockout_phase_end: '',
})

const canEdit = computed(() => {
  if (!authStore.user || !league.value) return false
  return league.value.organizer_id === authStore.user.id || authStore.user.role === 'admin'
})

const toLocalDatetime = (isoString) => {
  if (!isoString) return ''
  const date = new Date(isoString)
  return date.toISOString().slice(0, 16)
}

const fetchLeague = async () => {
  try {
    const response = await axios.get(`${API_URL}/league/${leagueId.value}`)
    league.value = response.data
    form.value = {
      name: response.data.name,
      description: response.data.description || '',
      days_per_match: response.data.days_per_match,
      knockout_size: response.data.knockout_size,
      status: response.data.status,
      group_phase_end: toLocalDatetime(response.data.group_phase_end),
      knockout_phase_end: toLocalDatetime(response.data.knockout_phase_end),
    }
  } catch (err) {
    error.value = t('leagueSettings.failedToLoad')
  } finally {
    loading.value = false
  }
}

const saveSettings = async () => {
  saving.value = true
  error.value = ''
  success.value = ''

  try {
    const payload = {
      name: form.value.name,
      description: form.value.description || null,
      days_per_match: form.value.days_per_match,
      knockout_size: form.value.knockout_size,
      status: form.value.status,
      group_phase_end: form.value.group_phase_end ? new Date(form.value.group_phase_end).toISOString() : null,
      knockout_phase_end: form.value.knockout_phase_end ? new Date(form.value.knockout_phase_end).toISOString() : null,
    }

    const response = await axios.patch(`${API_URL}/league/${leagueId.value}`, payload)
    league.value = response.data
    success.value = t('leagueSettings.settingsSaved')
  } catch (err) {
    error.value = err.response?.data?.detail || t('leagueSettings.failedToSave')
  } finally {
    saving.value = false
  }
}

const recalculateDates = async () => {
  recalculating.value = true
  error.value = ''
  success.value = ''

  try {
    await axios.post(`${API_URL}/league/${leagueId.value}/recalculate-dates`)
    await fetchLeague()
    success.value = t('leagueSettings.datesRecalculated')
  } catch (err) {
    error.value = err.response?.data?.detail || t('leagueSettings.failedToRecalculate')
  } finally {
    recalculating.value = false
  }
}

const formatDateTime = (dateString) => {
  const date = new Date(dateString)
  return date.toLocaleDateString() + ' ' + date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
}

const cancelLeague = async () => {
  cancelling.value = true
  error.value = ''

  try {
    await axios.patch(`${API_URL}/league/${leagueId.value}`, { status: 'cancelled' })
    showCancelModal.value = false
    router.push('/leagues')
  } catch (err) {
    error.value = err.response?.data?.detail || t('leagueSettings.failedToCancel')
    showCancelModal.value = false
  } finally {
    cancelling.value = false
  }
}

onMounted(() => {
  fetchLeague()
})
</script>
