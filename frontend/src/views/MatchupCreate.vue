<template>
  <div class="max-w-2xl mx-auto">
    <div class="card">
      <h1 class="text-3xl font-bold mb-6 text-center">{{ t('matchups.createNewMatchup') }}</h1>

      <div v-if="!created">
        <p class="text-gray-300 mb-6">
          {{ t('matchups.createMatchupInfo') }}
        </p>

        <form @submit.prevent="createMatchup" class="space-y-4">
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
import { ref } from 'vue'
import { useI18n } from 'vue-i18n'
import axios from 'axios'

const { t } = useI18n()
const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

const armyList = ref('')
const loading = ref(false)
const error = ref('')
const created = ref(false)
const matchup = ref(null)
const copied = ref(false)

const matchupUrl = ref('')

const createMatchup = async () => {
  loading.value = true
  error.value = ''

  try {
    const response = await axios.post(`${API_URL}/matchup`, {
      army_list: armyList.value
    })
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
}

const formatDate = (dateString) => {
  return new Date(dateString).toLocaleString()
}
</script>
