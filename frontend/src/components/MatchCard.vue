<template>
  <div
    :class="[
      'card hover:brightness-110 transition-all py-3 cursor-pointer',
      resultClass
    ]"
    @click="router.push(`/league/${leagueId}/match/${match.id}`)"
  >
    <div>
      <!-- Mobile: stacked layout, Desktop: horizontal -->
      <div class="flex flex-col sm:flex-row sm:items-center gap-2 sm:gap-4">
        <!-- Player 1 -->
        <div class="flex items-center gap-2 min-w-0">
          <img
            v-if="displayLeftAvatar"
            :src="displayLeftAvatar"
            class="w-7 h-7 sm:w-6 sm:h-6 rounded-full flex-shrink-0"
            :alt="displayLeftPlayer"
          />
          <div v-else class="w-7 h-7 sm:w-6 sm:h-6 rounded-full bg-gray-700 flex items-center justify-center text-gray-400 flex-shrink-0">
            <svg class="w-4 h-4" fill="currentColor" viewBox="0 0 24 24">
              <path d="M12 12c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm0 2c-2.67 0-8 1.34-8 4v2h16v-2c0-2.66-5.33-4-8-4z"/>
            </svg>
          </div>
          <span class="font-bold truncate">{{ displayLeftPlayer }}</span>
          <svg v-if="leftListStatus" class="w-4 h-4 flex-shrink-0" :class="leftListStatus === 'revealed' ? 'text-white' : 'text-squig-yellow'" fill="currentColor" viewBox="0 0 24 24">
            <path d="M14 2H6c-1.1 0-1.99.9-1.99 2L4 20c0 1.1.89 2 1.99 2H18c1.1 0 2-.9 2-2V8l-6-6zm2 16H8v-2h8v2zm0-4H8v-2h8v2zm-3-5V3.5L18.5 9H13z"/>
          </svg>
        </div>

        <!-- Score / vs -->
        <div class="flex items-center gap-2 py-1 sm:py-0">
          <span v-if="match.player1_score !== null" class="text-xl sm:text-2xl font-bold text-squig-yellow">
            {{ displayLeftScore }} - {{ displayRightScore }}
          </span>
          <span v-else class="text-gray-500 font-medium">vs</span>
        </div>

        <!-- Player 2 -->
        <div class="flex items-center gap-2 min-w-0">
          <svg v-if="rightListStatus" class="w-4 h-4 flex-shrink-0 sm:order-first" :class="rightListStatus === 'revealed' ? 'text-white' : 'text-squig-yellow'" fill="currentColor" viewBox="0 0 24 24">
            <path d="M14 2H6c-1.1 0-1.99.9-1.99 2L4 20c0 1.1.89 2 1.99 2H18c1.1 0 2-.9 2-2V8l-6-6zm2 16H8v-2h8v2zm0-4H8v-2h8v2zm-3-5V3.5L18.5 9H13z"/>
          </svg>
          <img
            v-if="displayRightAvatar"
            :src="displayRightAvatar"
            class="w-7 h-7 sm:w-6 sm:h-6 rounded-full flex-shrink-0"
            :alt="displayRightPlayer"
          />
          <div v-else class="w-7 h-7 sm:w-6 sm:h-6 rounded-full bg-gray-700 flex items-center justify-center text-gray-400 flex-shrink-0">
            <svg class="w-4 h-4" fill="currentColor" viewBox="0 0 24 24">
              <path d="M12 12c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm0 2c-2.67 0-8 1.34-8 4v2h16v-2c0-2.66-5.33-4-8-4z"/>
            </svg>
          </div>
          <span class="font-bold truncate">{{ displayRightPlayer }}</span>
        </div>
      </div>

      <!-- Match info row -->
      <div class="text-xs sm:text-sm text-gray-400 mt-2 flex flex-wrap gap-x-2">
        <span v-if="showRound && match.knockout_round">{{ knockoutRoundText(match.knockout_round) }}</span>
        <span v-if="match.player1_league_points !== null">
          {{ t('matchCard.leaguePts') }} {{ displayLeftPoints }} - {{ displayRightPoints }}
        </span>
        <span v-if="match.map_name">{{ t('matchCard.map') }} {{ match.map_name }}</span>
      </div>
    </div>

    <!-- Action row - stacked on mobile -->
    <div class="flex flex-col sm:flex-row items-stretch sm:items-center gap-2 mt-3 pt-3 border-t border-gray-700">
      <div class="flex gap-2 flex-1">
        <button
          v-if="canConfirm"
          @click.stop="$emit('confirm', match)"
          class="flex-1 sm:flex-initial text-sm px-3 py-2 sm:py-1 bg-green-700 hover:bg-green-600 rounded text-white"
        >
          {{ t('matchCard.confirm') }}
        </button>
        <button
          v-if="canEdit"
          @click.stop="$emit('edit', match)"
          class="flex-1 sm:flex-initial text-sm px-3 py-2 sm:py-1 bg-gray-700 hover:bg-gray-600 rounded"
        >
          {{ t('matchCard.edit') }}
        </button>
      </div>
      <div
        :class="matchStatusClass(match.status)"
        class="px-3 py-1.5 sm:py-1 rounded text-sm text-center sm:text-left"
      >
        {{ matchStatusText(match.status) }}
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'

const router = useRouter()

const { t } = useI18n()

const props = defineProps({
  match: {
    type: Object,
    required: true,
  },
  leagueId: {
    type: [Number, String],
    required: true,
  },
  canEdit: {
    type: Boolean,
    default: false,
  },
  canConfirm: {
    type: Boolean,
    default: false,
  },
  showRound: {
    type: Boolean,
    default: false,
  },
  currentPlayerId: {
    type: Number,
    default: null,
  },
  requireArmyLists: {
    type: Boolean,
    default: false,
  },
})

defineEmits(['edit', 'confirm'])

// Check if current player is player2 (need to swap display order)
const shouldSwap = computed(() => {
  return props.currentPlayerId && props.match.player2_id === props.currentPlayerId
})

// Display players - current user always on left if they're in the match
const displayLeftPlayer = computed(() => {
  return shouldSwap.value ? props.match.player2_username : props.match.player1_username
})

const displayRightPlayer = computed(() => {
  return shouldSwap.value ? props.match.player1_username : props.match.player2_username
})

const displayLeftScore = computed(() => {
  return shouldSwap.value ? props.match.player2_score : props.match.player1_score
})

const displayRightScore = computed(() => {
  return shouldSwap.value ? props.match.player1_score : props.match.player2_score
})

const displayLeftPoints = computed(() => {
  return shouldSwap.value ? props.match.player2_league_points : props.match.player1_league_points
})

const displayRightPoints = computed(() => {
  return shouldSwap.value ? props.match.player1_league_points : props.match.player2_league_points
})

const displayLeftAvatar = computed(() => {
  return shouldSwap.value ? props.match.player2_avatar : props.match.player1_avatar
})

const displayRightAvatar = computed(() => {
  return shouldSwap.value ? props.match.player1_avatar : props.match.player2_avatar
})

// Army list status for left player - 'revealed', 'submitted', or null
// Show icon whenever a list is submitted (regardless of league settings)
const leftListStatus = computed(() => {
  const hasSubmitted = shouldSwap.value
    ? props.match.player2_list_submitted
    : props.match.player1_list_submitted
  if (!hasSubmitted) return null
  if (props.match.lists_revealed) return 'revealed'
  return 'submitted'
})

// Army list status for right player
const rightListStatus = computed(() => {
  const hasSubmitted = shouldSwap.value
    ? props.match.player1_list_submitted
    : props.match.player2_list_submitted
  if (!hasSubmitted) return null
  if (props.match.lists_revealed) return 'revealed'
  return 'submitted'
})

const resultClass = computed(() => {
  if (!props.currentPlayerId || props.match.player1_score === null) {
    return ''
  }

  const isPlayer1 = props.match.player1_id === props.currentPlayerId
  const isPlayer2 = props.match.player2_id === props.currentPlayerId

  // Only color code matches involving the current player
  if (!isPlayer1 && !isPlayer2) {
    return ''
  }

  const myScore = isPlayer1 ? props.match.player1_score : props.match.player2_score
  const theirScore = isPlayer1 ? props.match.player2_score : props.match.player1_score

  if (myScore > theirScore) {
    return 'bg-green-900/20 border-l-4 border-l-green-500'
  } else if (myScore < theirScore) {
    return 'bg-red-900/20 border-l-4 border-l-red-500'
  } else {
    return 'bg-yellow-900/20 border-l-4 border-l-yellow-500'
  }
})

const matchStatusClass = (status) => {
  switch (status) {
    case 'scheduled': return 'bg-gray-900/30 border border-gray-500 text-gray-200'
    case 'pending_confirmation': return 'bg-yellow-900/30 border border-yellow-500 text-yellow-200'
    case 'confirmed': return 'bg-green-900/30 border border-green-500 text-green-200'
    default: return 'bg-gray-900/30 border border-gray-500 text-gray-200'
  }
}

const matchStatusText = (status) => {
  switch (status) {
    case 'scheduled': return t('matchCard.scheduled')
    case 'pending_confirmation': return t('matchCard.pending')
    case 'confirmed': return t('matchCard.completed')
    default: return status
  }
}

const knockoutRoundText = (round) => {
  switch (round) {
    case 'round_of_32': return t('matchCard.roundOf32')
    case 'round_of_16': return t('matchCard.roundOf16')
    case 'quarter': return t('matchCard.quarterFinal')
    case 'semi': return t('matchCard.semiFinal')
    case 'final': return t('matchCard.final')
    default: return round
  }
}
</script>
