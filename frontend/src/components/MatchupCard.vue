<template>
  <div class="card hover:bg-gray-700 transition-colors cursor-pointer" @click="$emit('click')">
    <!-- Header row: Title + Status badge -->
    <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-2 mb-3">
      <h3 class="text-lg md:text-xl font-bold text-squig-yellow truncate">
        {{ matchup.title || matchup.name }}
      </h3>
      <!-- Status badge - shown inline on mobile -->
      <div class="flex-shrink-0">
        <div
          v-if="matchup.result_status === 'confirmed'"
          class="bg-green-900/30 border border-green-500 text-green-200 px-2 py-1 rounded text-xs sm:text-sm inline-block"
        >
          {{ t('matchups.resultConfirmed') }}
        </div>
        <div
          v-else-if="matchup.result_status === 'pending_confirmation'"
          class="bg-yellow-900/30 border border-yellow-500 text-yellow-200 px-2 py-1 rounded text-xs sm:text-sm inline-block"
        >
          {{ matchup.player1_score }} : {{ matchup.player2_score }} ({{ t('matchups.awaitingConfirmation') }})
        </div>
        <div
          v-else-if="matchup.is_revealed"
          class="bg-blue-900/30 border border-blue-500 text-blue-200 px-2 py-1 rounded text-xs sm:text-sm inline-block"
        >
          {{ t('matchups.revealed') }}
        </div>
        <div
          v-else
          class="bg-yellow-900/30 border border-yellow-500 text-yellow-200 px-2 py-1 rounded text-xs sm:text-sm inline-block"
        >
          {{ t('matchups.pending') }}
        </div>
      </div>
    </div>

    <!-- Players section - stacked on mobile, inline on desktop -->
    <div class="flex flex-col sm:flex-row sm:items-center gap-3 sm:gap-4 text-sm">
      <!-- Player 1 -->
      <div class="flex items-center gap-2 min-w-0">
        <img
          v-if="matchup.player1_avatar"
          :src="matchup.player1_avatar"
          class="w-8 h-8 sm:w-6 sm:h-6 rounded-full flex-shrink-0"
          alt=""
        />
        <div v-else class="w-8 h-8 sm:w-6 sm:h-6 rounded-full bg-gray-600 flex items-center justify-center text-xs flex-shrink-0">
          {{ matchup.player1_username ? matchup.player1_username.charAt(0).toUpperCase() : '?' }}
        </div>
        <div class="min-w-0 flex-1">
          <div class="flex items-center gap-1 flex-wrap">
            <RouterLink
              v-if="matchup.player1_id"
              :to="{ name: 'PlayerProfile', params: { userId: matchup.player1_id } }"
              class="text-squig-yellow hover:underline truncate"
              @click.stop
            >{{ matchup.player1_username }}</RouterLink>
            <span v-else class="text-squig-yellow truncate">{{ matchup.player1_username || t('matchups.anonymous') }}</span>
            <span v-if="!matchup.result_status" :class="matchup.player1_submitted ? 'text-green-400' : 'text-gray-500'" class="text-sm">
              {{ matchup.player1_submitted ? '✓' : '○' }}
            </span>
          </div>
          <span v-if="matchup.player1_army_faction" class="text-xs text-gray-400 block truncate">({{ matchup.player1_army_faction }})</span>
        </div>
      </div>

      <!-- Score / VS separator -->
      <div class="flex items-center justify-center sm:justify-start gap-2 py-1 sm:py-0">
        <div v-if="matchup.result_status === 'confirmed'" class="flex items-center gap-2 font-bold text-lg">
          <span :class="matchup.player1_score > matchup.player2_score ? 'text-green-400' : 'text-white'">{{ matchup.player1_score }}</span>
          <span class="text-gray-500">:</span>
          <span :class="matchup.player2_score > matchup.player1_score ? 'text-green-400' : 'text-white'">{{ matchup.player2_score }}</span>
        </div>
        <span v-else class="text-gray-500 font-medium">vs</span>
      </div>

      <!-- Player 2 -->
      <div class="flex items-center gap-2 min-w-0">
        <img
          v-if="matchup.player2_avatar"
          :src="matchup.player2_avatar"
          class="w-8 h-8 sm:w-6 sm:h-6 rounded-full flex-shrink-0"
          alt=""
        />
        <div v-else class="w-8 h-8 sm:w-6 sm:h-6 rounded-full bg-gray-600 flex items-center justify-center text-xs flex-shrink-0">
          {{ matchup.player2_username ? matchup.player2_username.charAt(0).toUpperCase() : '?' }}
        </div>
        <div class="min-w-0 flex-1">
          <div class="flex items-center gap-1 flex-wrap">
            <RouterLink
              v-if="matchup.player2_id"
              :to="{ name: 'PlayerProfile', params: { userId: matchup.player2_id } }"
              class="text-squig-yellow hover:underline truncate"
              @click.stop
            >{{ matchup.player2_username }}</RouterLink>
            <span v-else class="text-squig-yellow truncate">{{ matchup.player2_username || t('matchups.anonymous') }}</span>
            <span v-if="!matchup.result_status" :class="matchup.player2_submitted ? 'text-green-400' : 'text-gray-500'" class="text-sm">
              {{ matchup.player2_submitted ? '✓' : '○' }}
            </span>
          </div>
          <span v-if="matchup.player2_army_faction" class="text-xs text-gray-400 block truncate">({{ matchup.player2_army_faction }})</span>
        </div>
      </div>
    </div>

    <!-- Date info - smaller, secondary -->
    <div class="mt-2 text-xs text-gray-400">
      {{ formatDate(matchup.created_at) }}
    </div>

    <!-- Action buttons row - larger touch targets on mobile -->
    <div v-if="matchup.can_submit_result || matchup.can_confirm_result" class="mt-3 pt-3 border-t border-gray-700 flex flex-col sm:flex-row gap-2">
      <button
        v-if="matchup.can_submit_result && !matchup.result_status"
        @click.stop="$emit('submit-result', matchup)"
        class="btn-secondary text-sm px-4 py-2.5 sm:py-1.5 flex-1 sm:flex-initial"
      >
        {{ t('matchups.submitResult') }}
      </button>
      <button
        v-if="matchup.can_confirm_result"
        @click.stop="$emit('confirm-result', matchup)"
        class="btn-primary text-sm px-4 py-2.5 sm:py-1.5 flex-1 sm:flex-initial"
      >
        {{ t('matchups.confirmResult') }}
      </button>
      <button
        v-if="matchup.can_confirm_result"
        @click.stop="$emit('edit-result', matchup)"
        class="btn-secondary text-sm px-4 py-2.5 sm:py-1.5 flex-1 sm:flex-initial"
      >
        {{ t('matchups.editResult') }}
      </button>
    </div>
  </div>
</template>

<script setup>
import { useI18n } from 'vue-i18n'
import { RouterLink } from 'vue-router'

const { t } = useI18n()

defineProps({
  matchup: {
    type: Object,
    required: true
  }
})

defineEmits(['click', 'submit-result', 'confirm-result', 'edit-result'])

const formatDate = (dateString) => {
  const date = new Date(dateString)
  return date.toLocaleDateString() + ' ' + date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
}
</script>
