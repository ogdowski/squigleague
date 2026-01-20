<template>
  <div
    class="card hover:bg-gray-700 transition-colors cursor-pointer"
    @click="$emit('click')"
  >
    <div class="flex items-center justify-between">
      <div class="flex-1">
        <h3 class="text-xl font-bold text-squig-yellow mb-2">
          {{ matchup.name }}
        </h3>
        <div class="flex flex-wrap gap-4 text-sm mb-2">
          <div>
            <span class="text-gray-400">{{ t('matchups.created') }}:</span>
            <span class="text-white ml-2">{{ formatDate(matchup.created_at) }}</span>
          </div>
        </div>
        <div class="flex gap-4 text-sm">
          <div class="flex items-center gap-2">
            <img
              v-if="matchup.player1_avatar"
              :src="matchup.player1_avatar"
              class="w-6 h-6 rounded-full"
              alt=""
            />
            <div v-else class="w-6 h-6 rounded-full bg-gray-600 flex items-center justify-center text-xs">
              {{ matchup.player1_username ? matchup.player1_username.charAt(0).toUpperCase() : '?' }}
            </div>
            <span class="text-squig-yellow">{{ matchup.player1_username || t('matchups.anonymous') }}</span>
          </div>
          <span class="text-gray-500">vs</span>
          <div class="flex items-center gap-2">
            <img
              v-if="matchup.player2_avatar"
              :src="matchup.player2_avatar"
              class="w-6 h-6 rounded-full"
              alt=""
            />
            <div v-else class="w-6 h-6 rounded-full bg-gray-600 flex items-center justify-center text-xs">
              {{ matchup.player2_username ? matchup.player2_username.charAt(0).toUpperCase() : '?' }}
            </div>
            <span class="text-squig-yellow">{{ matchup.player2_username || t('matchups.anonymous') }}</span>
          </div>
        </div>
      </div>

      <div class="flex items-center gap-4">
        <div class="text-center">
          <div class="text-xs text-gray-400 mb-1">{{ t('matchups.player1') }}</div>
          <div :class="matchup.player1_submitted ? 'text-green-400' : 'text-gray-500'">
            {{ matchup.player1_submitted ? '✓' : '○' }}
          </div>
        </div>
        <div class="text-center">
          <div class="text-xs text-gray-400 mb-1">{{ t('matchups.player2') }}</div>
          <div :class="matchup.player2_submitted ? 'text-green-400' : 'text-gray-500'">
            {{ matchup.player2_submitted ? '✓' : '○' }}
          </div>
        </div>
        <div
          v-if="matchup.is_revealed"
          class="bg-green-900/30 border border-green-500 text-green-200 px-3 py-1 rounded text-sm"
        >
          {{ t('matchups.revealed') }}
        </div>
        <div
          v-else
          class="bg-yellow-900/30 border border-yellow-500 text-yellow-200 px-3 py-1 rounded text-sm"
        >
          {{ t('matchups.pending') }}
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { useI18n } from 'vue-i18n'

const { t } = useI18n()

defineProps({
  matchup: {
    type: Object,
    required: true
  }
})

defineEmits(['click'])

const formatDate = (dateString) => {
  const date = new Date(dateString)
  return date.toLocaleDateString() + ' ' + date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
}
</script>
