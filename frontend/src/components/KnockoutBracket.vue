<template>
  <div>
    <!-- Mobile: Vertical list view -->
    <div class="md:hidden space-y-4">
      <div v-for="round in bracketRounds" :key="round.name" class="space-y-2">
        <!-- Round header -->
        <div
          :class="[
            'px-3 py-2 rounded font-bold text-sm',
            round.isCurrentRound ? 'bg-orange-900/50 text-orange-400' : 'bg-gray-800 text-gray-400'
          ]"
        >
          {{ round.displayName }}
          <span v-if="round.isCurrentRound" class="text-xs ml-2">(Current)</span>
        </div>
        <!-- Matches -->
        <div class="space-y-2 pl-2 border-l-2 border-gray-700">
          <div
            v-for="(match, matchIndex) in round.matches"
            :key="match?.id || `mobile-placeholder-${round.name}-${matchIndex}`"
            :class="[
              'bg-gray-800 rounded-lg overflow-hidden',
              match && match.status !== 'preview' ? 'cursor-pointer active:bg-gray-700' : '',
              !round.isCurrentRound && !round.isCompleted ? 'opacity-60' : ''
            ]"
            @click="match && match.status !== 'preview' && $emit('match-click', match)"
          >
            <template v-if="match">
              <div
                :class="[
                  'flex items-center justify-between px-3 py-2 border-b border-gray-700',
                  isWinner(match, match.player1_id) ? 'bg-green-900/20' : ''
                ]"
              >
                <span :class="['text-sm', isWinner(match, match.player1_id) ? 'font-bold text-green-400' : '']">
                  {{ match.player1_username || 'TBD' }}
                </span>
                <span v-if="match.player1_score !== null" class="text-squig-yellow font-bold">
                  {{ match.player1_score }}
                </span>
              </div>
              <div
                :class="[
                  'flex items-center justify-between px-3 py-2',
                  isWinner(match, match.player2_id) ? 'bg-green-900/20' : ''
                ]"
              >
                <span :class="['text-sm', isWinner(match, match.player2_id) ? 'font-bold text-green-400' : '']">
                  {{ match.player2_username || 'TBD' }}
                </span>
                <span v-if="match.player2_score !== null" class="text-squig-yellow font-bold">
                  {{ match.player2_score }}
                </span>
              </div>
            </template>
            <template v-else>
              <div class="px-3 py-2 text-gray-500 text-sm border-b border-gray-700">TBD</div>
              <div class="px-3 py-2 text-gray-500 text-sm">TBD</div>
            </template>
          </div>
        </div>
      </div>
      <!-- Champion on mobile -->
      <div v-if="winner" class="bg-gradient-to-r from-yellow-900/30 to-orange-900/30 border-2 border-squig-yellow rounded-lg p-4 text-center">
        <div class="text-2xl mb-1">🏆</div>
        <div class="font-bold text-squig-yellow">{{ winner }}</div>
      </div>
    </div>

    <!-- Desktop: Horizontal bracket -->
    <div class="hidden md:block bracket-wrapper overflow-x-auto pb-4 relative">
      <div class="bracket flex items-stretch" :style="{ minWidth: bracketWidth + 'px' }">
      <!-- Each round is a column -->
      <div
        v-for="(round, roundIndex) in bracketRounds"
        :key="round.name"
        class="round flex flex-col"
        :style="{ minWidth: '200px' }"
      >
        <!-- Round header -->
        <div
          :class="[
            'text-center py-2 mb-4 rounded font-bold text-sm',
            round.isCurrentRound ? 'bg-orange-900/50 text-orange-400' : 'bg-gray-800 text-gray-400'
          ]"
        >
          {{ round.displayName }}
          <span v-if="round.isCurrentRound" class="text-xs block">(Current)</span>
        </div>

        <!-- Matches container with flex for vertical distribution -->
        <div class="matches-container flex-1 flex flex-col justify-around py-2">
          <div
            v-for="(match, matchIndex) in round.matches"
            :key="match?.id || `placeholder-${roundIndex}-${matchIndex}`"
            class="match-slot flex items-center"
            :style="getMatchSlotStyle(roundIndex)"
          >
            <!-- Left connector (from previous round) -->
            <div
              v-if="roundIndex > 0"
              class="connector-in w-6 flex items-center"
            >
              <div class="w-full border-t-2 border-gray-600"></div>
            </div>

            <!-- Match card -->
            <div
              v-if="match"
              :class="[
                'match-card flex-1 bg-gray-800 rounded border-l-4 transition-all',
                match.status === 'confirmed' ? 'border-l-green-500' :
                match.status === 'pending_confirmation' ? 'border-l-yellow-500' :
                match.status === 'preview' ? 'border-l-blue-500 border-dashed' :
                'border-l-gray-600',
                !round.isCurrentRound && !round.isCompleted ? 'opacity-50' : '',
                match.status !== 'preview' ? 'cursor-pointer hover:brightness-110' : ''
              ]"
              @click="match.status !== 'preview' && $emit('match-click', match)"
            >
              <div
                :class="[
                  'player flex justify-between items-center px-3 py-2 border-b border-gray-700',
                  isWinner(match, match.player1_id) ? 'bg-green-900/30' : ''
                ]"
              >
                <span :class="['text-sm truncate', isWinner(match, match.player1_id) ? 'font-bold text-green-400' : '']">
                  {{ match.player1_username || 'TBD' }}
                </span>
                <span v-if="match.player1_score !== null" class="text-squig-yellow font-bold ml-2">
                  {{ match.player1_score }}
                </span>
              </div>
              <div
                :class="[
                  'player flex justify-between items-center px-3 py-2',
                  isWinner(match, match.player2_id) ? 'bg-green-900/30' : ''
                ]"
              >
                <span :class="['text-sm truncate', isWinner(match, match.player2_id) ? 'font-bold text-green-400' : '']">
                  {{ match.player2_username || 'TBD' }}
                </span>
                <span v-if="match.player2_score !== null" class="text-squig-yellow font-bold ml-2">
                  {{ match.player2_score }}
                </span>
              </div>
            </div>

            <!-- Placeholder match -->
            <div
              v-else
              class="match-card flex-1 bg-gray-800/30 rounded border-l-4 border-l-gray-700 opacity-40"
            >
              <div class="player flex justify-between items-center px-3 py-2 border-b border-gray-700">
                <span class="text-sm text-gray-500">TBD</span>
              </div>
              <div class="player flex justify-between items-center px-3 py-2">
                <span class="text-sm text-gray-500">TBD</span>
              </div>
            </div>

            <!-- Right connector (to next round) -->
            <div
              v-if="roundIndex < bracketRounds.length - 1"
              class="connector-out w-6 h-full relative"
            >
              <div class="absolute top-1/2 left-0 w-3 border-t-2 border-gray-600"></div>
              <!-- Vertical connector -->
              <div
                v-if="matchIndex % 2 === 0"
                class="absolute left-3 border-l-2 border-gray-600"
                :style="getVerticalConnectorStyle(roundIndex)"
              ></div>
              <div
                v-if="matchIndex % 2 === 1"
                class="absolute left-3 border-l-2 border-gray-600"
                :style="getVerticalConnectorStyleUp(roundIndex)"
              ></div>
              <!-- Horizontal to next -->
              <div
                v-if="matchIndex % 2 === 0"
                class="absolute left-3 w-3 border-t-2 border-gray-600"
                :style="{ top: `calc(50% + ${getVerticalOffset(roundIndex)}px)` }"
              ></div>
              <div
                v-if="matchIndex % 2 === 1"
                class="absolute left-3 w-3 border-t-2 border-gray-600"
                :style="{ top: `calc(50% - ${getVerticalOffset(roundIndex)}px)` }"
              ></div>
            </div>
          </div>
        </div>
      </div>

      <!-- Champion display -->
      <div v-if="showChampion" class="champion-column flex flex-col" style="min-width: 160px">
        <div class="text-center py-2 mb-4 rounded font-bold text-sm bg-squig-yellow/20 text-squig-yellow">
          Champion
        </div>
        <div class="flex-1 flex items-center">
          <!-- Connector line -->
          <div class="w-6 flex items-center">
            <div class="w-full border-t-2 border-gray-600"></div>
          </div>
          <div
            v-if="winner"
            class="flex-1 bg-gradient-to-r from-yellow-900/30 to-orange-900/30 border-2 border-squig-yellow rounded-lg p-4 text-center"
          >
            <div class="text-2xl mb-1">🏆</div>
            <div class="font-bold text-squig-yellow">{{ winner }}</div>
          </div>
          <div v-else class="flex-1 bg-gray-800/30 border-2 border-gray-700 border-dashed rounded-lg p-4 text-center opacity-40">
            <div class="text-2xl mb-1 grayscale">🏆</div>
            <div class="text-gray-500">TBD</div>
          </div>
        </div>
      </div>
    </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  matches: {
    type: Array,
    required: true,
  },
  leagueId: {
    type: [Number, String],
    required: true,
  },
  currentRound: {
    type: String,
    default: null,
  },
  knockoutSize: {
    type: Number,
    default: null,
  },
  qualifiedPlayers: {
    type: Array,
    default: () => [],
  },
  isPreview: {
    type: Boolean,
    default: false,
  },
})

defineEmits(['match-click'])

const roundOrder = ['round_of_32', 'round_of_16', 'quarter', 'semi', 'final']

const roundDisplayNames = {
  round_of_32: 'Round of 32',
  round_of_16: 'Round of 16',
  quarter: 'Quarter-finals',
  semi: 'Semi-finals',
  final: 'Final',
}

// Generate preview matches from qualified players (seeding: 1v8, 2v7, 3v6, 4v5, etc.)
const generatePreviewMatches = (players, knockoutSize) => {
  const size = knockoutSize || Math.pow(2, Math.floor(Math.log2(players.length)))
  const seededPlayers = players.slice(0, size)
  const matches = []
  const half = size / 2

  for (let i = 0; i < half; i++) {
    const p1 = seededPlayers[i]
    const p2 = seededPlayers[size - 1 - i]
    matches.push({
      id: `preview-${i}`,
      player1_id: p1?.player_id,
      player2_id: p2?.player_id,
      player1_username: p1 ? `${p1.seed}. ${p1.username || p1.discord_username}` : 'TBD',
      player2_username: p2 ? `${p2.seed}. ${p2.username || p2.discord_username}` : 'TBD',
      player1_score: null,
      player2_score: null,
      status: 'preview',
      knockout_round: getFirstRound(size),
    })
  }
  return matches
}

const getFirstRound = (size) => {
  const roundMap = { 2: 'final', 4: 'semi', 8: 'quarter', 16: 'round_of_16', 32: 'round_of_32' }
  return roundMap[size] || 'final'
}

const bracketRounds = computed(() => {
  // If preview mode, generate matches from qualified players
  let allMatches = props.matches
  if (props.isPreview && props.qualifiedPlayers.length >= 2) {
    const size = props.knockoutSize || Math.pow(2, Math.floor(Math.log2(props.qualifiedPlayers.length)))
    allMatches = generatePreviewMatches(props.qualifiedPlayers, size)
  }

  const matchesByRound = {}
  for (const match of allMatches) {
    const round = match.knockout_round
    if (!matchesByRound[round]) {
      matchesByRound[round] = []
    }
    matchesByRound[round].push(match)
  }

  // Find starting round
  let startRoundIndex = 0
  const firstRoundWithMatches = roundOrder.find(r => matchesByRound[r]?.length > 0)
  if (firstRoundWithMatches) {
    startRoundIndex = roundOrder.indexOf(firstRoundWithMatches)
  }

  // Build all rounds
  const rounds = []
  let expectedMatches = props.knockoutSize ? props.knockoutSize / 2 : (matchesByRound[firstRoundWithMatches]?.length || 1)

  for (let i = startRoundIndex; i < roundOrder.length; i++) {
    const roundName = roundOrder[i]
    const existingMatches = matchesByRound[roundName] || []

    // Sort matches by id to maintain bracket order
    const sortedMatches = [...existingMatches].sort((a, b) => {
      // Handle preview IDs like "preview-0"
      const aId = typeof a.id === 'string' ? parseInt(a.id.split('-')[1]) : a.id
      const bId = typeof b.id === 'string' ? parseInt(b.id.split('-')[1]) : b.id
      return aId - bId
    })

    // Fill with placeholders
    const roundMatches = [...sortedMatches]
    while (roundMatches.length < expectedMatches) {
      roundMatches.push(null)
    }

    rounds.push({
      name: roundName,
      displayName: roundDisplayNames[roundName],
      matches: roundMatches,
      isCurrentRound: props.isPreview ? (i === startRoundIndex) : props.currentRound === roundName,
      isCompleted: existingMatches.length > 0 && existingMatches.every(m => m.status === 'confirmed'),
      isPreview: props.isPreview,
    })

    expectedMatches = Math.max(1, Math.floor(expectedMatches / 2))
  }

  return rounds
})

const bracketWidth = computed(() => {
  return bracketRounds.value.length * 230 + 180
})

const showChampion = computed(() => {
  return bracketRounds.value.some(r => r.name === 'final')
})

const winner = computed(() => {
  const finalRound = bracketRounds.value.find(r => r.name === 'final')
  if (!finalRound?.matches[0]) return null

  const finalMatch = finalRound.matches[0]
  if (finalMatch.status !== 'confirmed') return null

  if (finalMatch.player1_score > finalMatch.player2_score) {
    return finalMatch.player1_username
  } else if (finalMatch.player2_score > finalMatch.player1_score) {
    return finalMatch.player2_username
  }
  return null
})

const isWinner = (match, playerId) => {
  if (!match || match.status !== 'confirmed' || match.player1_score === null) return false
  if (match.player1_score > match.player2_score && playerId === match.player1_id) return true
  if (match.player2_score > match.player1_score && playerId === match.player2_id) return true
  return false
}

// Height increases exponentially each round
const getMatchSlotStyle = (roundIndex) => {
  const baseHeight = 90
  const height = baseHeight * Math.pow(2, roundIndex)
  return { minHeight: `${height}px` }
}

// Vertical offset for connector lines
const getVerticalOffset = (roundIndex) => {
  const baseHeight = 90
  return (baseHeight * Math.pow(2, roundIndex)) / 2
}

// Down connector (from even-indexed match)
const getVerticalConnectorStyle = (roundIndex) => {
  const offset = getVerticalOffset(roundIndex)
  return {
    top: '50%',
    height: `${offset}px`,
  }
}

// Up connector (from odd-indexed match)
const getVerticalConnectorStyleUp = (roundIndex) => {
  const offset = getVerticalOffset(roundIndex)
  return {
    bottom: '50%',
    height: `${offset}px`,
  }
}
</script>

<style scoped>
.bracket-wrapper {
  background: linear-gradient(135deg, rgba(31, 41, 55, 0.5) 0%, rgba(17, 24, 39, 0.8) 100%);
  border-radius: 12px;
  padding: 20px;
}

.match-card {
  min-width: 150px;
  max-width: 170px;
}

.match-card .player {
  min-height: 36px;
}
</style>
