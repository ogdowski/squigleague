<template>
  <div class="max-w-2xl mx-auto">
    <div class="card">
      <h1 class="text-3xl font-bold mb-6 text-center">{{ t('matchups.createNewMatchup') }}</h1>

      <div v-if="!created">
        <p class="text-gray-300 mb-6">
          {{ t('matchups.createMatchupInfo') }}
        </p>

        <form @submit.prevent="createMatchup" class="space-y-4">
          <!-- Optional title -->
          <div>
            <label class="block text-sm font-medium mb-2">
              {{ t('matchups.matchupTitle') }}
              <span class="text-gray-400 font-normal ml-1">({{ t('matchups.optional') }})</span>
            </label>
            <input
              v-model="matchupTitle"
              type="text"
              maxlength="100"
              class="input-field w-full"
              :placeholder="t('matchups.matchupTitlePlaceholder')"
            />
          </div>

          <!-- Army faction dropdown -->
          <div>
            <label class="block text-sm font-medium mb-2">
              {{ t('matchups.armyFaction') }}
              <span class="text-gray-400 font-normal ml-1">({{ t('matchups.autoDetected') }})</span>
            </label>
            <select
              v-model="armyFaction"
              class="input-field w-full"
            >
              <option value="">{{ t('matchups.selectOrAutoDetect') }}</option>
              <option v-for="army in armies" :key="army" :value="army">{{ army }}</option>
            </select>
          </div>

          <div>
            <label class="block text-sm font-medium mb-2">
              {{ t('matchups.yourArmyList') }}
            </label>
            <textarea
              v-model="armyList"
              rows="15"
              class="input-field w-full font-mono text-sm"
              placeholder="Ooops All Rats! 2000/2000 pts

Skaven
Claw-horde
General's Handbook 2025-26
Drops: 2
Wounds: 220

Battle Tactic Cards: Scouting Force, Restless Energy

General's Regiment
Vizzik Skour, Prophet of the Horned Rat (380)
• General
Clanrats (300)
• Reinforced
...

Created with Sigdex: sigdex.io"
              required
            ></textarea>
          </div>

          <!-- Player 2 search (only for logged in users) -->
          <div v-if="authStore.isAuthenticated">
            <label class="block text-sm font-medium mb-2">
              {{ t('matchups.assignOpponent') }}
              <span class="text-gray-400 font-normal ml-1">({{ t('matchups.optional') }})</span>
            </label>
            <div class="relative">
              <input
                v-model="player2Search"
                @input="searchUsers"
                type="text"
                class="input-field w-full"
                :placeholder="t('matchups.searchByUsername')"
              />
              <!-- Search results dropdown -->
              <div
                v-if="searchResults.length > 0 && player2Search && !selectedPlayer2"
                class="absolute z-10 w-full mt-1 bg-gray-800 border border-gray-600 rounded-lg shadow-lg max-h-48 overflow-y-auto"
              >
                <button
                  v-for="user in searchResults"
                  :key="user.id"
                  type="button"
                  @click="selectPlayer2(user)"
                  class="w-full px-4 py-2 text-left hover:bg-gray-700 flex items-center gap-3"
                >
                  <img
                    v-if="user.avatar_url"
                    :src="user.avatar_url"
                    class="w-8 h-8 rounded-full"
                    alt=""
                  />
                  <div v-else class="w-8 h-8 rounded-full bg-gray-600 flex items-center justify-center">
                    {{ user.username.charAt(0).toUpperCase() }}
                  </div>
                  <span>{{ user.username }}</span>
                </button>
              </div>
            </div>
            <!-- Selected player -->
            <div v-if="selectedPlayer2" class="mt-2 flex items-center gap-2 bg-gray-700 rounded px-3 py-2">
              <img
                v-if="selectedPlayer2.avatar_url"
                :src="selectedPlayer2.avatar_url"
                class="w-6 h-6 rounded-full"
                alt=""
              />
              <span class="text-squig-yellow">{{ selectedPlayer2.username }}</span>
              <button type="button" @click="clearPlayer2" class="ml-auto text-gray-400 hover:text-white">
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>
          </div>

          <!-- Public checkbox -->
          <div class="flex items-center gap-3">
            <input
              type="checkbox"
              id="isPublic"
              v-model="isPublic"
              class="w-4 h-4 rounded border-gray-600 bg-gray-700 text-squig-yellow focus:ring-squig-yellow"
            />
            <label for="isPublic" class="text-sm text-gray-300">
              {{ t('matchups.publishAfterCompletion') }}
            </label>
          </div>

          <button
            type="submit"
            :disabled="loading"
            class="btn-primary w-full text-xl px-8 py-4"
          >
            {{ loading ? t('matchups.creating') : t('matchups.createMatchup') }}
          </button>

          <div v-if="error" class="bg-red-900/30 border border-red-500 text-red-200 px-4 py-3 rounded">
            {{ error }}
          </div>
        </form>
      </div>

      <div v-else class="space-y-6">
        <div class="bg-green-900/30 border border-green-500 text-green-200 px-4 py-3 rounded">
          {{ t('matchups.matchupCreated') }}
        </div>

        <div>
          <h2 class="text-xl font-bold mb-3">{{ t('matchups.matchupId') }}</h2>
          <div class="bg-gray-900 px-4 py-3 rounded font-mono text-squig-yellow text-xl">
            {{ matchup.name }}
          </div>
        </div>

        <div>
          <h2 class="text-xl font-bold mb-3">{{ t('matchups.shareThisLink') }}</h2>
          <div class="flex gap-2">
            <input
              :value="matchupUrl"
              readonly
              class="input-field flex-1 font-mono text-sm"
            />
            <button
              @click="copyLink"
              class="btn-secondary whitespace-nowrap"
            >
              {{ copied ? t('matchups.copied') : t('matchups.copy') }}
            </button>
          </div>
        </div>

        <div>
          <h2 class="text-xl font-bold mb-3">{{ t('matchups.expires') }}</h2>
          <p class="text-gray-300">
            {{ formatDate(matchup.expires_at) }}
          </p>
        </div>

        <div class="flex gap-4">
          <router-link
            :to="`/matchup/${matchup.name}`"
            class="btn-primary flex-1 text-center"
          >
            {{ t('matchups.goToMatchup') }}
          </router-link>
          <button
            @click="reset"
            class="btn-secondary flex-1"
          >
            {{ t('matchups.createAnother') }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import { useAuthStore } from '../stores/auth'
import { ARMY_FACTIONS } from '../constants/armies'
import axios from 'axios'

const { t } = useI18n()
const authStore = useAuthStore()
const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

const armyList = ref('')
const loading = ref(false)
const error = ref('')
const created = ref(false)
const matchup = ref(null)
const copied = ref(false)
const matchupUrl = ref('')

// New fields
const matchupTitle = ref('')
const armyFaction = ref('')
const armies = ref(ARMY_FACTIONS)
const isPublic = ref(true)
const player2Search = ref('')
const searchResults = ref([])
const selectedPlayer2 = ref(null)
let searchTimeout = null

const searchUsers = () => {
  if (searchTimeout) clearTimeout(searchTimeout)

  if (player2Search.value.length < 2) {
    searchResults.value = []
    return
  }

  // Clear selection when typing
  if (selectedPlayer2.value) {
    selectedPlayer2.value = null
  }

  searchTimeout = setTimeout(async () => {
    try {
      const response = await axios.get(`${API_URL}/matchup/search-users`, {
        params: { q: player2Search.value }
      })
      searchResults.value = response.data
    } catch (err) {
      searchResults.value = []
    }
  }, 300)
}

const selectPlayer2 = (user) => {
  selectedPlayer2.value = user
  player2Search.value = user.username
  searchResults.value = []
}

const clearPlayer2 = () => {
  selectedPlayer2.value = null
  player2Search.value = ''
  searchResults.value = []
}

const createMatchup = async () => {
  loading.value = true
  error.value = ''

  try {
    const payload = {
      army_list: armyList.value,
      is_public: isPublic.value
    }

    if (matchupTitle.value) {
      payload.title = matchupTitle.value
    }

    if (armyFaction.value) {
      payload.army_faction = armyFaction.value
    }

    if (selectedPlayer2.value) {
      payload.player2_username = selectedPlayer2.value.username
    }

    const response = await axios.post(`${API_URL}/matchup`, payload)
    matchup.value = response.data
    matchupUrl.value = `${window.location.origin}/matchup/${response.data.name}`
    created.value = true
  } catch (err) {
    error.value = t('matchups.failedToCreate')
  } finally {
    loading.value = false
  }
}

const copyLink = async () => {
  try {
    await navigator.clipboard.writeText(matchupUrl.value)
    copied.value = true
    setTimeout(() => {
      copied.value = false
    }, 2000)
  } catch (err) {
    console.error('Failed to copy:', err)
  }
}

const reset = () => {
  created.value = false
  matchup.value = null
  matchupUrl.value = ''
  copied.value = false
  armyList.value = ''
  matchupTitle.value = ''
  armyFaction.value = ''
  isPublic.value = true
  player2Search.value = ''
  selectedPlayer2.value = null
  searchResults.value = []
}

const formatDate = (dateString) => {
  return new Date(dateString).toLocaleString()
}
</script>
