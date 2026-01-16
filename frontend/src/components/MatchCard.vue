<template>
  <div
    :class="[
      'card cursor-pointer hover:brightness-110 transition-all py-3',
      resultClass
    ]"
  >
    <div class="flex items-center justify-between">
      <div class="flex-1">
        <div class="flex items-center gap-4">
          <span class="font-bold">{{ match.player1_username }}</span>
          <span v-if="match.player1_score !== null" class="text-2xl font-bold text-squig-yellow">
            {{ match.player1_score }} - {{ match.player2_score }}
          </span>
          <span v-else class="text-gray-500">vs</span>
          <span class="font-bold">{{ match.player2_username }}</span>
        </div>
        <div class="text-sm text-gray-400 mt-1">
          <span v-if="showRound && match.knockout_round">{{ knockoutRoundText(match.knockout_round) }}</span>
          <span v-if="match.player1_league_points !== null">
            League pts: {{ match.player1_league_points }} - {{ match.player2_league_points }}
          </span>
          <span v-if="match.map_name"> | Map: {{ match.map_name }}</span>
        </div>
      </div>
      <div class="flex items-center gap-2">
        <span v-if="canEdit" class="text-xs text-gray-500">Click to edit</span>
        <div
          :class="matchStatusClass(match.status)"
          class="px-3 py-1 rounded text-sm"
        >
          {{ matchStatusText(match.status) }}
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  match: {
    type: Object,
    required: true,
  },
  canEdit: {
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
    case 'scheduled': return 'Scheduled'
    case 'pending_confirmation': return 'Pending'
    case 'confirmed': return 'Completed'
    default: return status
  }
}

const knockoutRoundText = (round) => {
  switch (round) {
    case 'round_of_32': return 'Round of 32'
    case 'round_of_16': return 'Round of 16'
    case 'quarter': return 'Quarter-final'
    case 'semi': return 'Semi-final'
    case 'final': return 'Final'
    default: return round
  }
}
</script>
