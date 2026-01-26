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

    <!-- Date and visibility info -->
    <div class="mt-2 flex items-center gap-3 text-xs text-gray-400">
      <span>{{ formatDate(matchup.created_at) }}</span>
      <!-- Visibility indicator -->
      <span v-if="matchup.is_public && matchup.is_revealed" class="flex items-center gap-1 text-green-400" :title="t('matchups.visibleOnPublicList')">
        <svg class="w-3 h-3" fill="currentColor" viewBox="0 0 24 24"><path d="M12 4.5C7 4.5 2.73 7.61 1 12c1.73 4.39 6 7.5 11 7.5s9.27-3.11 11-7.5c-1.73-4.39-6-7.5-11-7.5zM12 17c-2.76 0-5-2.24-5-5s2.24-5 5-5 5 2.24 5 5-2.24 5-5 5zm0-8c-1.66 0-3 1.34-3 3s1.34 3 3 3 3-1.34 3-3-1.34-3-3-3z"/></svg>
        {{ t('matchups.public') }}
      </span>
      <span v-else-if="matchup.is_public && !matchup.is_revealed" class="flex items-center gap-1 text-yellow-400" :title="t('matchups.willBePublic')">
        <svg class="w-3 h-3" fill="currentColor" viewBox="0 0 24 24"><path d="M12 4.5C7 4.5 2.73 7.61 1 12c1.73 4.39 6 7.5 11 7.5s9.27-3.11 11-7.5c-1.73-4.39-6-7.5-11-7.5zM12 17c-2.76 0-5-2.24-5-5s2.24-5 5-5 5 2.24 5 5-2.24 5-5 5zm0-8c-1.66 0-3 1.34-3 3s1.34 3 3 3 3-1.34 3-3-1.34-3-3-3z"/></svg>
        {{ t('matchups.willBePublic') }}
      </span>
      <span v-else class="flex items-center gap-1 text-gray-500" :title="t('matchups.private')">
        <svg class="w-3 h-3" fill="currentColor" viewBox="0 0 24 24"><path d="M12 7c2.76 0 5 2.24 5 5 0 .65-.13 1.26-.36 1.83l2.92 2.92c1.51-1.26 2.7-2.89 3.43-4.75-1.73-4.39-6-7.5-11-7.5-1.4 0-2.74.25-3.98.7l2.16 2.16C10.74 7.13 11.35 7 12 7zM2 4.27l2.28 2.28.46.46C3.08 8.3 1.78 10.02 1 12c1.73 4.39 6 7.5 11 7.5 1.55 0 3.03-.3 4.38-.84l.42.42L19.73 22 21 20.73 3.27 3 2 4.27zM7.53 9.8l1.55 1.55c-.05.21-.08.43-.08.65 0 1.66 1.34 3 3 3 .22 0 .44-.03.65-.08l1.55 1.55c-.67.33-1.41.53-2.2.53-2.76 0-5-2.24-5-5 0-.79.2-1.53.53-2.2zm4.31-.78l3.15 3.15.02-.16c0-1.66-1.34-3-3-3l-.17.01z"/></svg>
        {{ t('matchups.private') }}
      </span>
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
