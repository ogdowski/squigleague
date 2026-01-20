<template>
  <div class="card hover:bg-gray-700 transition-colors">
    <div class="flex items-center justify-between cursor-pointer" @click="$emit('click')">
      <div class="flex-1">
        <h3 class="text-xl font-bold text-squig-yellow mb-2">
          {{ matchup.title || matchup.name }}
        </h3>
        <div class="flex flex-wrap gap-4 text-sm mb-2">
          <div>
            <span class="text-gray-400">{{ t('matchups.created') }}:</span>
            <span class="text-white ml-2">{{ formatDate(matchup.created_at) }}</span>
          </div>
        </div>
        <div class="flex gap-4 text-sm items-center">
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
            <div>
              <RouterLink
                v-if="matchup.player1_id"
                :to="{ name: 'PlayerProfile', params: { userId: matchup.player1_id } }"
                class="text-squig-yellow hover:underline"
                @click.stop
              >{{ matchup.player1_username }}</RouterLink>
              <span v-else class="text-squig-yellow">{{ matchup.player1_username || t('matchups.anonymous') }}</span>
              <span v-if="matchup.player1_army_faction" class="text-xs text-gray-400 ml-1">({{ matchup.player1_army_faction }})</span>
            </div>
          </div>

          <!-- Result display -->
          <div v-if="matchup.result_status === 'confirmed'" class="flex items-center gap-2 font-bold">
            <span :class="matchup.player1_score > matchup.player2_score ? 'text-green-400' : 'text-white'">{{ matchup.player1_score }}</span>
            <span class="text-gray-500">:</span>
            <span :class="matchup.player2_score > matchup.player1_score ? 'text-green-400' : 'text-white'">{{ matchup.player2_score }}</span>
          </div>
          <span v-else class="text-gray-500">vs</span>

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
            <div>
              <RouterLink
                v-if="matchup.player2_id"
                :to="{ name: 'PlayerProfile', params: { userId: matchup.player2_id } }"
                class="text-squig-yellow hover:underline"
                @click.stop
              >{{ matchup.player2_username }}</RouterLink>
              <span v-else class="text-squig-yellow">{{ matchup.player2_username || t('matchups.anonymous') }}</span>
              <span v-if="matchup.player2_army_faction" class="text-xs text-gray-400 ml-1">({{ matchup.player2_army_faction }})</span>
            </div>
          </div>
        </div>
      </div>

      <div class="flex items-center gap-4">
        <!-- Status badges - only show when no result -->
        <template v-if="!matchup.result_status">
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
        </template>

        <!-- Result status badge -->
        <div
          v-if="matchup.result_status === 'confirmed'"
          class="bg-green-900/30 border border-green-500 text-green-200 px-3 py-1 rounded text-sm"
        >
          {{ t('matchups.resultConfirmed') }}
        </div>
        <div
          v-else-if="matchup.result_status === 'pending_confirmation'"
          class="bg-yellow-900/30 border border-yellow-500 text-yellow-200 px-3 py-1 rounded text-sm"
        >
          {{ matchup.player1_score }} : {{ matchup.player2_score }} ({{ t('matchups.awaitingConfirmation') }})
        </div>
        <div
          v-else-if="matchup.is_revealed"
          class="bg-blue-900/30 border border-blue-500 text-blue-200 px-3 py-1 rounded text-sm"
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

    <!-- Action buttons row -->
    <div v-if="matchup.can_submit_result || matchup.can_confirm_result" class="mt-3 pt-3 border-t border-gray-700 flex gap-2">
      <button
        v-if="matchup.can_submit_result && !matchup.result_status"
        @click.stop="$emit('submit-result', matchup)"
        class="btn-secondary text-sm px-3 py-1"
      >
        {{ t('matchups.submitResult') }}
      </button>
      <button
        v-if="matchup.can_confirm_result"
        @click.stop="$emit('confirm-result', matchup)"
        class="btn-primary text-sm px-3 py-1"
      >
        {{ t('matchups.confirmResult') }}
      </button>
      <button
        v-if="matchup.can_confirm_result"
        @click.stop="$emit('edit-result', matchup)"
        class="btn-secondary text-sm px-3 py-1"
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
