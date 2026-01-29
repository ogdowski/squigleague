<template>
  <div class="max-w-4xl mx-auto">
    <div v-if="loading" class="flex justify-center py-12">
      <div class="w-10 h-10 border-4 border-squig-yellow border-t-transparent rounded-full animate-spin"></div>
    </div>
    <div v-else-if="error" class="card bg-red-900/30 border border-red-500 text-red-200">{{ error }}</div>
    <div v-else-if="match">
      <button
        @click="goBack"
        class="flex items-center gap-2 text-gray-400 hover:text-white mb-4 transition-colors"
      >
        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
        </svg>
        {{ t('common.back') }}
      </button>
      <!-- Header -->
      <div class="card mb-6">
        <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-2 mb-4">
          <div class="text-sm sm:text-base">
            <router-link :to="`/league/${match.league_id}`" class="text-squig-yellow hover:underline">
              {{ match.league_name }}
            </router-link>
            <span class="mx-2 text-gray-500">/</span>
            <span class="text-gray-300">
              {{ match.phase === 'knockout' ? formatKnockoutRound(match.knockout_round) : match.group_name }}
            </span>
          </div>
          <span :class="statusClass" class="px-3 py-1 rounded text-sm self-start sm:self-auto">{{ statusLabel }}</span>
        </div>

        <!-- Players -->
        <div class="grid md:grid-cols-2 gap-4">
          <!-- Player 1 -->
          <div class="bg-gray-900 p-4 rounded">
            <div class="flex items-center justify-between mb-2">
              <div class="flex items-center gap-3">
                <img
                  v-if="match.player1_avatar"
                  :src="match.player1_avatar"
                  class="w-10 h-10 rounded-full"
                  :alt="match.player1_username"
                />
                <div v-else class="w-10 h-10 rounded-full bg-gray-700 flex items-center justify-center text-gray-400">
                  <svg class="w-6 h-6" fill="currentColor" viewBox="0 0 24 24">
                    <path d="M12 12c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm0 2c-2.67 0-8 1.34-8 4v2h16v-2c0-2.66-5.33-4-8-4z"/>
                  </svg>
                </div>
                <router-link v-if="match.player1_user_id" :to="`/player/${match.player1_user_id}`" class="font-bold text-lg hover:text-squig-yellow">
                  {{ match.player1_username }}
                </router-link>
                <span v-else class="font-bold text-lg">{{ match.player1_username }}</span>
              </div>
              <span v-if="match.player1_army_faction" class="text-sm text-gray-400">{{ match.player1_army_faction }}</span>
            </div>
            <div v-if="match.status === 'confirmed'" class="text-3xl font-bold" :class="p1ScoreClass">
              {{ match.player1_score }}
            </div>
            <div v-if="match.player1_elo_after && match.status === 'confirmed'" class="text-sm mt-2">
              <span class="text-gray-400">ELO:</span>
              <span class="ml-1">{{ match.player1_elo_before }}</span>
              <span class="mx-1">→</span>
              <span :class="match.player1_elo_after > match.player1_elo_before ? 'text-green-400' : 'text-red-400'">
                {{ match.player1_elo_after }}
                ({{ match.player1_elo_after > match.player1_elo_before ? '+' : '' }}{{ match.player1_elo_after - match.player1_elo_before }})
              </span>
            </div>
            <div v-if="match.player1_league_points !== null && match.status === 'confirmed'" class="text-sm mt-1">
              <span class="text-gray-400">{{ t('matchDetail.leaguePoints') }}:</span>
              <span class="ml-1 text-squig-yellow font-semibold">+{{ match.player1_league_points }}</span>
            </div>
          </div>

          <!-- Player 2 -->
          <div class="bg-gray-900 p-4 rounded">
            <div class="flex items-center justify-between mb-2">
              <div class="flex items-center gap-3">
                <img
                  v-if="match.player2_avatar"
                  :src="match.player2_avatar"
                  class="w-10 h-10 rounded-full"
                  :alt="match.player2_username"
                />
                <div v-else class="w-10 h-10 rounded-full bg-gray-700 flex items-center justify-center text-gray-400">
                  <svg class="w-6 h-6" fill="currentColor" viewBox="0 0 24 24">
                    <path d="M12 12c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm0 2c-2.67 0-8 1.34-8 4v2h16v-2c0-2.66-5.33-4-8-4z"/>
                  </svg>
                </div>
                <router-link v-if="match.player2_user_id" :to="`/player/${match.player2_user_id}`" class="font-bold text-lg hover:text-squig-yellow">
                  {{ match.player2_username }}
                </router-link>
                <span v-else class="font-bold text-lg">{{ match.player2_username }}</span>
              </div>
              <span v-if="match.player2_army_faction" class="text-sm text-gray-400">{{ match.player2_army_faction }}</span>
            </div>
            <div v-if="match.status === 'confirmed'" class="text-3xl font-bold" :class="p2ScoreClass">
              {{ match.player2_score }}
            </div>
            <div v-if="match.player2_elo_after && match.status === 'confirmed'" class="text-sm mt-2">
              <span class="text-gray-400">ELO:</span>
              <span class="ml-1">{{ match.player2_elo_before }}</span>
              <span class="mx-1">→</span>
              <span :class="match.player2_elo_after > match.player2_elo_before ? 'text-green-400' : 'text-red-400'">
                {{ match.player2_elo_after }}
                ({{ match.player2_elo_after > match.player2_elo_before ? '+' : '' }}{{ match.player2_elo_after - match.player2_elo_before }})
              </span>
            </div>
            <div v-if="match.player2_league_points !== null && match.status === 'confirmed'" class="text-sm mt-1">
              <span class="text-gray-400">{{ t('matchDetail.leaguePoints') }}:</span>
              <span class="ml-1 text-squig-yellow font-semibold">+{{ match.player2_league_points }}</span>
            </div>
          </div>
        </div>
      </div>

      <!-- Map Section - collapsible on mobile -->
      <div class="card mb-6">
        <button
          @click="showMapSection = !showMapSection"
          class="w-full flex items-center justify-between text-left md:cursor-default"
        >
          <h2 class="text-lg md:text-xl font-bold">
            <span class="md:hidden">{{ match.map_name || t('matchDetail.map') }}</span>
            <span class="hidden md:inline">{{ t('matchDetail.map') }}</span>
          </h2>
          <svg
            class="w-5 h-5 text-gray-400 md:hidden transition-transform"
            :class="{ 'rotate-180': showMapSection }"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
          </svg>
        </button>
        <div :class="{ 'hidden md:block': !showMapSection }" class="mt-4">
          <BattlePlanDisplay
            :map-name="match.map_name"
            :map-image="mapImage"
            :battle-plan="battlePlan"
          />
        </div>

        <!-- Map controls (when can edit and not confirmed) -->
        <div v-if="match.can_set_map && match.status !== 'confirmed'" class="space-y-3 mt-4">
          <p class="text-sm text-gray-400">{{ match.map_name ? t('matchDetail.changeMap') : t('matchDetail.selectMap') }}</p>
          <div class="flex flex-col sm:flex-row gap-3">
            <button @click="randomizeMap" :disabled="settingMap" class="btn-primary py-3 sm:py-2">
              {{ settingMap ? t('matchDetail.rolling') : t('matchDetail.randomMap') }}
            </button>
            <div class="flex gap-2 flex-1">
              <select v-model="selectedMap" class="flex-1 bg-gray-700 border border-gray-600 rounded px-4 py-3 sm:py-2 text-base" style="font-size: 16px;">
                <option value="">{{ t('matchDetail.selectMapPlaceholder') }}</option>
                <option v-for="m in availableMaps" :key="m" :value="m">{{ m }}</option>
              </select>
              <button @click="setMap" :disabled="!selectedMap || settingMap" class="btn-secondary py-3 sm:py-2 px-6">{{ t('matchDetail.set') }}</button>
            </div>
          </div>
        </div>
      </div>

      <!-- Army List Submission (per-match, blind exchange) -->
      <div v-if="canSubmitArmyList && match.status !== 'confirmed'" class="card mb-6">
        <h2 class="text-xl font-bold mb-4">{{ t('matchDetail.submitArmyList') }}</h2>

        <!-- Submission status -->
        <div class="flex gap-4 mb-4 text-sm">
          <div class="flex items-center gap-2">
            <span :class="match.player1_list_submitted ? 'text-green-400' : 'text-gray-500'">
              {{ match.player1_list_submitted ? '✓' : '○' }}
            </span>
            <span>{{ match.player1_username }}</span>
          </div>
          <div class="flex items-center gap-2">
            <span :class="match.player2_list_submitted ? 'text-green-400' : 'text-gray-500'">
              {{ match.player2_list_submitted ? '✓' : '○' }}
            </span>
            <span>{{ match.player2_username }}</span>
          </div>
        </div>

        <div v-if="myListSubmitted" class="p-3 bg-green-900/20 border border-green-600 rounded mb-4">
          <p class="text-green-300 text-sm">{{ t('matchDetail.listSubmittedWaiting') }}</p>
        </div>

        <form v-else @submit.prevent="submitArmyList" class="space-y-4">
          <div>
            <label class="block text-sm text-gray-400 mb-1">{{ t('matchDetail.armyFaction') }} <span class="text-gray-500">({{ t('common.optional') }})</span></label>
            <select v-model="armyListForm.army_faction" class="w-full bg-gray-700 border border-gray-600 rounded px-4 py-2">
              <option value="">{{ t('matchDetail.autoDetect') }}</option>
              <option v-for="faction in armyFactions" :key="faction" :value="faction">{{ faction }}</option>
            </select>
          </div>
          <div>
            <label class="block text-sm text-gray-400 mb-1">{{ t('matchDetail.armyList') }}</label>
            <textarea
              v-model="armyListForm.army_list"
              rows="8"
              required
              class="w-full bg-gray-700 border border-gray-600 rounded px-4 py-2 font-mono text-sm"
              :placeholder="t('matchDetail.pasteArmyList')"
            ></textarea>
          </div>
          <p class="text-xs text-gray-500">{{ t('matchDetail.blindExchangeNote') }}</p>
          <div v-if="armyListError" class="text-red-400 text-sm">{{ armyListError }}</div>
          <button type="submit" :disabled="submittingList || !armyListForm.army_list.trim()" class="btn-primary">
            {{ submittingList ? t('matchDetail.submitting') : t('matchDetail.submitList') }}
          </button>
        </form>
      </div>

      <!-- Army Lists (shown when revealed or from league settings) - collapsible on mobile -->
      <div v-if="match.lists_revealed || match.player1_army_list || match.player2_army_list" class="card mb-6">
        <button
          @click="showListsSection = !showListsSection"
          class="w-full flex items-center justify-between text-left md:cursor-default"
        >
          <h2 class="text-lg md:text-xl font-bold">{{ t('matchDetail.armyLists') }}</h2>
          <svg
            class="w-5 h-5 text-gray-400 md:hidden transition-transform"
            :class="{ 'rotate-180': showListsSection }"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
          </svg>
        </button>
        <div :class="{ 'hidden md:block': !showListsSection }" class="mt-4 grid md:grid-cols-2 gap-4 md:gap-6">
          <div v-if="match.player1_army_list">
            <h3 class="font-semibold mb-2 text-sm md:text-base">
              {{ match.player1_username }}
              <span v-if="match.player1_army_faction" class="text-xs md:text-sm text-gray-400 font-normal ml-1">({{ match.player1_army_faction }})</span>
            </h3>
            <div class="bg-gray-900 p-3 md:p-4 rounded relative">
              <button
                @click="copyList(match.player1_army_list, 'p1')"
                class="absolute top-2 right-2 p-1.5 bg-gray-700 hover:bg-gray-600 rounded text-gray-400 hover:text-white transition-colors"
              >
                <svg v-if="copiedList !== 'p1'" class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" />
                </svg>
                <svg v-else class="w-4 h-4 text-green-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
                </svg>
              </button>
              <pre class="whitespace-pre-wrap font-mono text-xs md:text-sm text-gray-300 pr-8">{{ match.player1_army_list }}</pre>
            </div>
          </div>
          <div v-if="match.player2_army_list">
            <h3 class="font-semibold mb-2 text-sm md:text-base">
              {{ match.player2_username }}
              <span v-if="match.player2_army_faction" class="text-xs md:text-sm text-gray-400 font-normal ml-1">({{ match.player2_army_faction }})</span>
            </h3>
            <div class="bg-gray-900 p-3 md:p-4 rounded relative">
              <button
                @click="copyList(match.player2_army_list, 'p2')"
                class="absolute top-2 right-2 p-1.5 bg-gray-700 hover:bg-gray-600 rounded text-gray-400 hover:text-white transition-colors"
              >
                <svg v-if="copiedList !== 'p2'" class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" />
                </svg>
                <svg v-else class="w-4 h-4 text-green-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
                </svg>
              </button>
              <pre class="whitespace-pre-wrap font-mono text-xs md:text-sm text-gray-300 pr-8">{{ match.player2_army_list }}</pre>
            </div>
          </div>
        </div>
      </div>

      <!-- Submit Result (if can edit) -->
      <div v-if="match.can_edit && match.status !== 'confirmed'" class="card mb-6">
        <h2 class="text-xl font-bold mb-4">{{ t('matchDetail.submitResult') }}</h2>
        <form @submit.prevent="submitResult" class="space-y-4">
          <!-- Mobile-optimized score entry -->
          <div class="flex items-center justify-center gap-4 py-4">
            <div class="text-center flex-1 max-w-32">
              <label class="block text-sm text-gray-400 mb-2 truncate">{{ match.player1_username }}</label>
              <div class="relative group">
                <input
                  v-model.number="resultForm.player1_score"
                  type="number"
                  min="0"
                  inputmode="numeric"
                  pattern="[0-9]*"
                  required
                  class="score-input w-full bg-gray-700 border-2 border-gray-600 rounded-lg text-center font-bold py-4 focus:outline-none focus:border-squig-yellow transition-colors"
                  style="font-size: 28px; min-height: 70px;"
                />
                <button type="button" @click="resultForm.player1_score++" class="score-btn-up">
                  <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 15l7-7 7 7"/></svg>
                </button>
                <button type="button" @click="resultForm.player1_score = Math.max(0, resultForm.player1_score - 1)" class="score-btn-down">
                  <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"/></svg>
                </button>
              </div>
              <p v-if="calculatedPoints.player1 !== null" class="text-sm text-squig-yellow font-semibold mt-2">
                {{ calculatedPoints.player1 }} pts
              </p>
            </div>
            <div class="text-2xl text-gray-500 font-bold pt-6">:</div>
            <div class="text-center flex-1 max-w-32">
              <label class="block text-sm text-gray-400 mb-2 truncate">{{ match.player2_username }}</label>
              <div class="relative group">
                <input
                  v-model.number="resultForm.player2_score"
                  type="number"
                  min="0"
                  inputmode="numeric"
                  pattern="[0-9]*"
                  required
                  class="score-input w-full bg-gray-700 border-2 border-gray-600 rounded-lg text-center font-bold py-4 focus:outline-none focus:border-squig-yellow transition-colors"
                  style="font-size: 28px; min-height: 70px;"
                />
                <button type="button" @click="resultForm.player2_score++" class="score-btn-up">
                  <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 15l7-7 7 7"/></svg>
                </button>
                <button type="button" @click="resultForm.player2_score = Math.max(0, resultForm.player2_score - 1)" class="score-btn-down">
                  <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"/></svg>
                </button>
              </div>
              <p v-if="calculatedPoints.player2 !== null" class="text-sm text-squig-yellow font-semibold mt-2">
                {{ calculatedPoints.player2 }} pts
              </p>
            </div>
          </div>
          <div v-if="submitError" class="text-red-400 text-sm text-center">{{ submitError }}</div>
          <button type="submit" :disabled="submitting" class="btn-primary w-full py-4 text-lg">
            {{ submitting ? t('matchDetail.submitting') : t('matchDetail.submitResult') }}
          </button>
        </form>
      </div>

      <!-- Match Info -->
      <div class="card">
        <h2 class="text-xl font-bold mb-4">{{ t('matchDetail.matchInfo') }}</h2>
        <div class="grid grid-cols-2 gap-4 text-sm">
          <div>
            <span class="text-gray-400">{{ t('matchDetail.phase') }}:</span>
            <span class="ml-2">{{ match.phase === 'knockout' ? t('matchDetail.knockout') : t('matchDetail.group') }}</span>
          </div>
          <div v-if="match.deadline">
            <span class="text-gray-400">{{ t('matchDetail.deadline') }}:</span>
            <span class="ml-2">{{ formatDate(match.deadline) }}</span>
          </div>
          <div v-if="match.submitted_at">
            <span class="text-gray-400">{{ t('matchDetail.resultSubmitted') }}:</span>
            <span class="ml-2">{{ formatDate(match.submitted_at) }}</span>
          </div>
          <div v-if="match.confirmed_at">
            <span class="text-gray-400">{{ t('matchDetail.confirmed') }}:</span>
            <span class="ml-2">{{ formatDate(match.confirmed_at) }}</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import axios from 'axios'
import BattlePlanDisplay from '@/components/BattlePlanDisplay.vue'
import { fetchMapsData } from '@/constants/maps'
import { useAuthStore } from '@/stores/auth'
import { ARMY_FACTIONS } from '@/constants/armies'

const { t } = useI18n()
const API_URL = import.meta.env.VITE_API_URL || '/api'
const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()

const goBack = () => {
  if (window.history.length > 1) {
    router.back()
  } else {
    router.push('/leagues')
  }
}

const match = ref(null)
const loading = ref(true)
const error = ref('')

const selectedMap = ref('')
const settingMap = ref(false)

const resultForm = ref({ player1_score: 0, player2_score: 0 })
const submitting = ref(false)
const submitError = ref('')

// Army list submission
const armyListForm = ref({ army_list: '', army_faction: '' })
const submittingList = ref(false)
const armyListError = ref('')
const armyFactions = ARMY_FACTIONS

// Mobile section toggles and copy
const showMapSection = ref(true)
const showListsSection = ref(true)
const copiedList = ref(null)
const copyList = async (text, listId) => {
  try {
    await navigator.clipboard.writeText(text)
    copiedList.value = listId
    setTimeout(() => { copiedList.value = null }, 2000)
  } catch (err) {
    console.error('Failed to copy:', err)
  }
}

// Check if current user is one of the players
const isPlayer1 = computed(() => {
  return authStore.user && match.value && match.value.player1_user_id === authStore.user.id
})
const isPlayer2 = computed(() => {
  return authStore.user && match.value && match.value.player2_user_id === authStore.user.id
})
const isPlayer = computed(() => isPlayer1.value || isPlayer2.value)

// Check if current user can submit army list (per-match lists, not league-required)
const canSubmitArmyList = computed(() => {
  if (!isPlayer.value || !match.value) return false
  // Can't submit if lists are already revealed
  if (match.value.lists_revealed) return false
  // Backend determines if per-match lists are allowed (not required by league for this phase)
  if (!match.value.can_submit_army_list) return false
  return true
})

// Check if current user has already submitted
const myListSubmitted = computed(() => {
  if (!match.value) return false
  if (isPlayer1.value) return match.value.player1_list_submitted
  if (isPlayer2.value) return match.value.player2_list_submitted
  return false
})

const submitArmyList = async () => {
  submittingList.value = true
  armyListError.value = ''
  try {
    await axios.post(
      `${API_URL}/league/${route.params.leagueId}/matches/${route.params.matchId}/army-list`,
      armyListForm.value
    )
    await fetchMatch()
    armyListForm.value = { army_list: '', army_faction: '' }
  } catch (err) {
    armyListError.value = err.response?.data?.detail || t('matchDetail.failedToSubmitList')
  } finally {
    submittingList.value = false
  }
}

// Maps data from API
const mapsData = ref(null)
const availableMaps = computed(() => mapsData.value?.maps || [])
const mapImage = computed(() => {
  if (!match.value?.map_name || !mapsData.value?.images) return null
  return mapsData.value.images[match.value.map_name]
})
const battlePlan = computed(() => {
  if (!match.value?.map_name || !mapsData.value?.battle_plans) return null
  return mapsData.value.battle_plans[match.value.map_name]
})

const fetchMatch = async () => {
  loading.value = true
  error.value = ''
  try {
    const res = await axios.get(`${API_URL}/league/${route.params.leagueId}/matches/${route.params.matchId}`)
    match.value = res.data
  } catch (err) {
    error.value = err.response?.data?.detail || t('matchDetail.failedToLoad')
  } finally {
    loading.value = false
  }
}

const statusClass = computed(() => {
  if (!match.value) return ''
  const s = match.value.status
  if (s === 'confirmed') return 'bg-green-900 text-green-300'
  if (s === 'pending_confirmation') return 'bg-yellow-900 text-yellow-300'
  return 'bg-gray-700 text-gray-300'
})

const statusLabel = computed(() => {
  if (!match.value) return ''
  const labels = {
    scheduled: t('matchDetail.statusScheduled'),
    pending_confirmation: t('matchDetail.statusPendingConfirmation'),
    confirmed: t('matchDetail.statusConfirmed'),
    disputed: t('matchDetail.statusDisputed'),
  }
  return labels[match.value.status] || match.value.status
})

const p1ScoreClass = computed(() => {
  if (!match.value || match.value.player1_score === null) return ''
  if (match.value.player1_score > match.value.player2_score) return 'text-green-400'
  if (match.value.player1_score < match.value.player2_score) return 'text-red-400'
  return 'text-yellow-400'
})

const p2ScoreClass = computed(() => {
  if (!match.value || match.value.player2_score === null) return ''
  if (match.value.player2_score > match.value.player1_score) return 'text-green-400'
  if (match.value.player2_score < match.value.player1_score) return 'text-red-400'
  return 'text-yellow-400'
})

// Calculate league points from game scores (live preview)
const calculatedPoints = computed(() => {
  const p1 = resultForm.value.player1_score
  const p2 = resultForm.value.player2_score
  // Both scores must be valid numbers
  const p1Valid = typeof p1 === 'number' && !Number.isNaN(p1)
  const p2Valid = typeof p2 === 'number' && !Number.isNaN(p2)
  if (!p1Valid || !p2Valid || !match.value) {
    return { player1: null, player2: null }
  }
  return {
    player1: calculateLeaguePoints(p1, p2),
    player2: calculateLeaguePoints(p2, p1),
  }
})

const calculateLeaguePoints = (playerScore, opponentScore) => {
  if (!match.value) return 0
  const { points_per_win, points_per_draw, points_per_loss } = match.value
  let base
  if (playerScore > opponentScore) {
    base = points_per_win
  } else if (playerScore < opponentScore) {
    base = points_per_loss
  } else {
    base = points_per_draw
  }
  const diff = playerScore - opponentScore
  const bonus = Math.min(100, Math.max(0, diff + 50))
  return base + bonus
}

const formatKnockoutRound = (round) => {
  const labels = {
    final: t('matchDetail.final'),
    semi: t('matchDetail.semiFinal'),
    quarter: t('matchDetail.quarterFinal'),
    round_of_16: t('matchDetail.roundOf16'),
    round_of_32: t('matchDetail.roundOf32'),
  }
  return labels[round] || round
}

const formatDate = (dateStr) => {
  if (!dateStr) return ''
  return new Date(dateStr).toLocaleString()
}

const randomizeMap = async () => {
  settingMap.value = true
  try {
    const res = await axios.post(`${API_URL}/league/${route.params.leagueId}/matches/${route.params.matchId}/map`, { random: true })
    match.value.map_name = res.data.map_name
  } catch (err) {
    console.error('Failed to randomize map:', err)
  } finally {
    settingMap.value = false
  }
}

const setMap = async () => {
  if (!selectedMap.value) return
  settingMap.value = true
  try {
    const res = await axios.post(`${API_URL}/league/${route.params.leagueId}/matches/${route.params.matchId}/map`, { map_name: selectedMap.value })
    match.value.map_name = res.data.map_name
    selectedMap.value = ''
  } catch (err) {
    console.error('Failed to set map:', err)
  } finally {
    settingMap.value = false
  }
}

const submitResult = async () => {
  submitting.value = true
  submitError.value = ''
  try {
    await axios.post(`${API_URL}/league/${route.params.leagueId}/matches/${route.params.matchId}/result`, resultForm.value)
    await fetchMatch()
  } catch (err) {
    submitError.value = err.response?.data?.detail || t('matchDetail.failedToSubmit')
  } finally {
    submitting.value = false
  }
}

onMounted(async () => {
  mapsData.value = await fetchMapsData()
  await fetchMatch()
})
</script>

<style scoped>
.score-input::-webkit-inner-spin-button,
.score-input::-webkit-outer-spin-button {
  -webkit-appearance: none;
  margin: 0;
}
.score-input {
  -moz-appearance: textfield;
}

.score-btn-up,
.score-btn-down {
  position: absolute;
  right: 4px;
  width: 36px;
  height: 36px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #4b5563;
  border-radius: 8px;
  color: #d1d5db;
  opacity: 1;
  transition: background 0.15s;
}
.score-btn-up:hover,
.score-btn-down:hover,
.score-btn-up:active,
.score-btn-down:active {
  background: #f59e0b;
  color: #000;
}
.score-btn-up {
  top: 4px;
}
.score-btn-down {
  bottom: 4px;
}
.score-btn-up svg,
.score-btn-down svg {
  width: 20px;
  height: 20px;
}

@media (min-width: 768px) {
  .score-btn-up,
  .score-btn-down {
    width: 28px;
    height: 28px;
    opacity: 0;
  }
  .score-btn-up svg,
  .score-btn-down svg {
    width: 16px;
    height: 16px;
  }
  .group:hover .score-btn-up,
  .group:hover .score-btn-down {
    opacity: 1;
  }
}
</style>
