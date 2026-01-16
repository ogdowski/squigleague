<template>
  <div class="max-w-6xl mx-auto">
    <div v-if="loading" class="text-center py-12">
      <p class="text-xl text-gray-300">Loading league...</p>
    </div>

    <div v-else-if="error" class="card">
      <div class="bg-red-900/30 border border-red-500 text-red-200 px-4 py-3 rounded">
        {{ error }}
      </div>
    </div>

    <div v-else-if="league">
      <!-- Header -->
      <div class="flex justify-between items-start mb-6">
        <div>
          <h1 class="text-3xl font-bold text-squig-yellow mb-2">{{ league.name }}</h1>
          <p v-if="league.description" class="text-gray-400">{{ league.description }}</p>
        </div>
        <div
          :class="statusClass(league.status)"
          class="px-4 py-2 rounded text-sm font-bold"
        >
          {{ statusText(league.status) }}
        </div>
      </div>

      <!-- Info Cards -->
      <div class="grid md:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
        <div class="card">
          <h3 class="text-sm text-gray-400 mb-1">Players</h3>
          <p class="text-2xl font-bold">{{ league.player_count }}</p>
          <p v-if="league.qualifying_spots_per_group" class="text-xs text-gray-500 mt-1">
            Top {{ league.qualifying_spots_per_group }} per group advance
          </p>
        </div>
        <div class="card">
          <div class="flex items-center gap-2 mb-1">
            <h3 class="text-sm text-gray-400">Scoring</h3>
            <div class="relative group">
              <svg class="w-4 h-4 text-gray-400 cursor-help" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <circle cx="12" cy="12" r="10" stroke-width="2"/>
                <path stroke-width="2" d="M12 16v-4m0-4h.01"/>
              </svg>
              <div class="absolute left-0 top-6 w-72 p-3 bg-gray-800 border border-gray-600 rounded shadow-lg text-xs text-gray-300 hidden group-hover:block z-20">
                <p class="font-semibold mb-2">How scoring works:</p>
                <ul class="space-y-1 mb-2">
                  <li><span class="text-green-400">Win:</span> {{ league.points_per_win }} pts</li>
                  <li><span class="text-yellow-400">Draw:</span> {{ league.points_per_draw }} pts</li>
                  <li><span class="text-red-400">Loss:</span> {{ league.points_per_loss }} pts</li>
                </ul>
                <p class="mb-2">Plus bonus based on score difference:<br/>
                <span class="text-gray-400">bonus = min(100, max(0, diff + 50))</span></p>
                <p class="font-semibold mb-1">Examples:</p>
                <ul class="space-y-1 text-gray-400">
                  <li>Win 72-68: {{ league.points_per_win }} + 54 = <span class="text-white">{{ league.points_per_win + 54 }}</span></li>
                  <li>Lose 68-72: {{ league.points_per_loss }} + 46 = <span class="text-white">{{ league.points_per_loss + 46 }}</span></li>
                  <li>Draw 70-70: {{ league.points_per_draw }} + 50 = <span class="text-white">{{ league.points_per_draw + 50 }}</span></li>
                </ul>
              </div>
            </div>
          </div>
          <p class="text-sm">W: {{ league.points_per_win }} / D: {{ league.points_per_draw }} / L: {{ league.points_per_loss }}</p>
        </div>
        <div v-if="league.group_phase_end" class="card">
          <h3 class="text-sm text-gray-400 mb-1">Group Phase Ends</h3>
          <p class="text-lg font-bold">{{ formatDateTime(league.group_phase_end) }}</p>
        </div>
        <div v-if="league.knockout_phase_end && league.has_knockout_phase" class="card">
          <h3 class="text-sm text-gray-400 mb-1">Knockout Ends</h3>
          <p class="text-lg font-bold">{{ formatDateTime(league.knockout_phase_end) }}</p>
        </div>
      </div>

      <!-- Action Error -->
      <div v-if="actionError" class="mb-4 bg-red-900/30 border border-red-500 text-red-200 px-4 py-3 rounded">
        {{ actionError }}
      </div>

      <!-- Actions -->
      <div class="flex gap-4 mb-8">
        <button
          v-if="league.is_registration_open && !isJoined"
          @click="joinLeague"
          class="btn-primary"
          :disabled="joining"
        >
          {{ joining ? 'Joining...' : 'Join League' }}
        </button>

        <template v-if="isOrganizer">
          <router-link
            :to="`/league/${league.id}/settings`"
            class="btn-secondary"
          >
            Settings
          </router-link>
          <button
            v-if="league.status === 'registration'"
            @click="showDrawGroupsModal = true"
            class="btn-secondary"
            :disabled="actionLoading"
          >
            Draw Groups
          </button>
          <button
            v-if="league.status === 'group_phase' && !groupPhaseEnded"
            @click="showEndGroupPhaseModal = true"
            class="btn-secondary"
            :disabled="actionLoading"
          >
            End Group Phase
          </button>
          <button
            v-if="league.status === 'group_phase' && groupPhaseEnded && league.has_knockout_phase"
            @click="showStartKnockoutModal = true"
            class="btn-secondary"
            :disabled="actionLoading"
          >
            Start Knockout
          </button>
          <button
            v-if="league.status === 'group_phase' && groupPhaseEnded && !league.has_knockout_phase"
            @click="showFinishLeagueModal = true"
            class="btn-secondary"
            :disabled="actionLoading"
          >
            Finish League
          </button>
          <button
            v-if="league.status === 'knockout_phase' && !league.knockout_lists_visible"
            @click="showRevealListsModal = true"
            class="btn-secondary"
            :disabled="actionLoading"
          >
            Reveal Lists
          </button>
        </template>
      </div>

      <!-- Tabs -->
      <div class="flex gap-2 mb-6 border-b border-gray-700">
        <button
          v-for="tab in tabs"
          :key="tab.id"
          @click="activeTab = tab.id"
          :class="activeTab === tab.id ? 'border-squig-yellow text-squig-yellow' : 'border-transparent text-gray-400'"
          class="px-4 py-2 border-b-2 transition-colors"
        >
          {{ tab.name }}
        </button>
      </div>

      <!-- Tab Content -->
      <div v-if="activeTab === 'standings'" class="space-y-6">
        <div v-for="group in standings" :key="group.group_id" class="card">
          <div class="flex justify-between items-center mb-4">
            <h3 class="text-xl font-bold">{{ group.group_name }}</h3>
            <span v-if="group.qualifying_spots" class="text-sm text-gray-400">
              Top {{ group.qualifying_spots }} advance
            </span>
          </div>
          <div class="overflow-x-auto">
            <table class="w-full text-sm">
              <thead>
                <tr class="text-gray-400 border-b border-gray-700">
                  <th class="text-left py-2 px-2">#</th>
                  <th class="text-left py-2 px-2">Player</th>
                  <th class="text-center py-2 px-2">P</th>
                  <th class="text-center py-2 px-2">W</th>
                  <th class="text-center py-2 px-2">D</th>
                  <th class="text-center py-2 px-2">L</th>
                  <th class="text-right py-2 px-2">Pts</th>
                  <th class="text-right py-2 px-2">Avg</th>
                </tr>
              </thead>
              <tbody>
                <tr
                  v-for="entry in group.standings"
                  :key="entry.player_id"
                  :class="[
                    'border-b',
                    entry.qualifies
                      ? 'border-green-800 bg-green-900/20'
                      : 'border-gray-800'
                  ]"
                >
                  <td class="py-2 px-2 font-bold">
                    <span v-if="entry.qualifies" class="text-green-400">{{ entry.position }}</span>
                    <span v-else>{{ entry.position }}</span>
                  </td>
                  <td class="py-2 px-2">{{ entry.username || entry.discord_username }}</td>
                  <td class="py-2 px-2 text-center">{{ entry.games_played }}</td>
                  <td class="py-2 px-2 text-center text-green-400">{{ entry.games_won }}</td>
                  <td class="py-2 px-2 text-center text-yellow-400">{{ entry.games_drawn }}</td>
                  <td class="py-2 px-2 text-center text-red-400">{{ entry.games_lost }}</td>
                  <td class="py-2 px-2 text-right font-bold text-squig-yellow">{{ entry.total_points }}</td>
                  <td class="py-2 px-2 text-right text-gray-400">{{ entry.average_points.toFixed(0) }}</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>

      <div v-if="activeTab === 'matches'" class="space-y-4">
        <div v-if="matches.length === 0" class="card text-center py-8">
          <p class="text-gray-400">No matches yet</p>
        </div>

        <!-- Knockout Matches (shown first when in knockout phase) -->
        <div v-if="knockoutMatches.length > 0 && league.status === 'knockout_phase'" class="border border-orange-700 rounded-lg overflow-hidden">
          <button
            @click="toggleGroup('knockout')"
            class="w-full flex items-center justify-between px-4 py-3 bg-orange-900/30 hover:bg-orange-900/40 transition-colors"
          >
            <h3 class="text-lg font-bold text-orange-400">Knockout Phase</h3>
            <div class="flex items-center gap-3">
              <span class="text-sm text-orange-300">{{ knockoutMatches.length }} matches</span>
              <svg
                :class="['w-5 h-5 text-orange-400 transition-transform', expandedGroups['knockout'] ? 'rotate-180' : '']"
                fill="none" stroke="currentColor" viewBox="0 0 24 24"
              >
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
              </svg>
            </div>
          </button>

          <div v-if="expandedGroups['knockout']" class="p-4 space-y-2">
            <MatchCard
              v-for="match in knockoutMatches"
              :key="match.id"
              :match="match"
              :can-edit="canEditMatch(match)"
              :current-player-id="currentUserPlayerId"
              :show-round="true"
              @click="openMatchModal(match)"
            />
          </div>
        </div>

        <!-- Group Phase Matches - grouped by group -->
        <div v-for="group in groupedMatches" :key="group.name" class="border border-gray-700 rounded-lg overflow-hidden">
          <button
            @click="toggleGroup(group.name)"
            class="w-full flex items-center justify-between px-4 py-3 bg-gray-800 hover:bg-gray-700 transition-colors"
          >
            <h3 class="text-lg font-bold text-squig-yellow">{{ group.name }}</h3>
            <div class="flex items-center gap-3">
              <span class="text-sm text-gray-400">{{ group.myMatches.length + group.otherMatches.length }} matches</span>
              <svg
                :class="['w-5 h-5 text-gray-400 transition-transform', expandedGroups[group.name] ? 'rotate-180' : '']"
                fill="none" stroke="currentColor" viewBox="0 0 24 24"
              >
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
              </svg>
            </div>
          </button>

          <div v-if="expandedGroups[group.name]" class="p-4 space-y-4">
            <!-- My matches in this group first -->
            <div v-if="group.myMatches.length > 0" class="space-y-2">
              <p class="text-xs text-gray-500 uppercase tracking-wide">My Matches</p>
              <MatchCard
                v-for="match in group.myMatches"
                :key="match.id"
                :match="match"
                :can-edit="canEditMatch(match)"
                :current-player-id="currentUserPlayerId"
                @click="openMatchModal(match)"
              />
            </div>

            <!-- Other matches in this group -->
            <div v-if="group.otherMatches.length > 0" class="space-y-2">
              <p v-if="group.myMatches.length > 0" class="text-xs text-gray-500 uppercase tracking-wide">Other Matches</p>
              <MatchCard
                v-for="match in group.otherMatches"
                :key="match.id"
                :match="match"
                :can-edit="canEditMatch(match)"
                :current-player-id="currentUserPlayerId"
                @click="openMatchModal(match)"
              />
            </div>
          </div>
        </div>
      </div>

      <div v-if="activeTab === 'players'" class="card">
        <div class="overflow-x-auto">
          <table class="w-full text-sm">
            <thead>
              <tr class="text-gray-400 border-b border-gray-700">
                <th class="text-left py-2 px-2">Player</th>
                <th class="text-left py-2 px-2">Group</th>
                <th class="text-center py-2 px-2">Games</th>
                <th class="text-right py-2 px-2">Points</th>
              </tr>
            </thead>
            <tbody>
              <tr
                v-for="player in sortedPlayers"
                :key="player.id"
                :class="[
                  'border-b border-gray-800',
                  player.wouldQualify ? 'bg-green-900/20' : ''
                ]"
              >
                <td class="py-2 px-2">
                  <span>{{ player.username || player.discord_username }}</span>
                  <span v-if="player.wouldQualify" class="ml-2 text-xs text-green-400" title="Would advance to knockout">Q</span>
                </td>
                <td class="py-2 px-2">{{ player.group_name || '-' }}</td>
                <td class="py-2 px-2 text-center text-gray-400">{{ player.games_played }}</td>
                <td class="py-2 px-2 text-right font-bold">{{ player.total_points }}</td>
              </tr>
            </tbody>
          </table>
        </div>
        <p v-if="league?.qualifying_spots_per_group && league?.has_knockout_phase" class="text-xs text-gray-500 mt-3">
          <span class="text-green-400">Q</span> = Would qualify for knockout (top {{ league.qualifying_spots_per_group }} per group)
        </p>
      </div>

      <!-- Knockout Tab -->
      <div v-if="activeTab === 'knockout'" class="space-y-6">
        <!-- Org action buttons (only during knockout phase) -->
        <div v-if="isOrganizer && league.status === 'knockout_phase'" class="flex items-center gap-4 mb-4">
          <button
            v-if="canAdvanceKnockout"
            @click="showAdvanceKnockoutModal = true"
            class="btn-primary bg-orange-600 hover:bg-orange-700"
            :disabled="actionLoading"
          >
            {{ league.current_knockout_round === 'final' ? 'Finish League' : 'Advance to Next Round' }}
          </button>
          <span v-else-if="pendingKnockoutMatches > 0" class="text-sm text-gray-400">
            {{ pendingKnockoutMatches }} match{{ pendingKnockoutMatches > 1 ? 'es' : '' }} pending confirmation in {{ knockoutRoundText(league.current_knockout_round) }}
          </span>
        </div>

        <!-- Preview notice when not in knockout yet -->
        <div v-if="league.status !== 'knockout_phase' && league.status !== 'finished'" class="mb-4 bg-blue-900/20 border border-blue-500 rounded p-3">
          <p class="text-blue-200 text-sm">
            <span class="font-bold">Preview Mode:</span> This bracket shows projected matchups based on current standings. Final seeding will be determined when knockout phase starts.
          </p>
        </div>

        <!-- Bracket visualization - show real matches OR preview with qualified players -->
        <KnockoutBracket
          v-if="knockoutMatches.length > 0 || qualifiedPlayers.length >= 2"
          :matches="knockoutMatches"
          :current-round="league.current_knockout_round"
          :knockout-size="league.knockout_size || league.total_qualifying_spots"
          :qualified-players="qualifiedPlayers"
          :is-preview="knockoutMatches.length === 0"
          @match-click="openMatchModal"
        />

        <!-- Not enough qualified players yet -->
        <div v-else class="card text-center py-8">
          <p class="text-gray-400 mb-2">Not enough qualified players yet.</p>
          <p class="text-sm text-gray-500">
            Players need to play at least one match to appear in the bracket preview.
          </p>
        </div>

        <!-- League finished -->
        <div v-if="league.status === 'finished' && knockoutMatches.length > 0" class="card text-center py-6 bg-green-900/20 border border-green-500">
          <h3 class="text-2xl font-bold text-green-400 mb-2">League Complete!</h3>
          <p class="text-gray-300">The knockout phase has concluded.</p>
        </div>
      </div>
    </div>

    <!-- Confirm Modals -->
    <ConfirmModal
      :show="showDrawGroupsModal"
      title="Draw Groups"
      message="Are you sure you want to draw groups? This action cannot be undone."
      confirmText="Draw Groups"
      :danger="true"
      @confirm="drawGroups"
      @cancel="showDrawGroupsModal = false"
    />

    <ConfirmModal
      :show="showStartKnockoutModal"
      title="Start Knockout Phase"
      message="Are you sure you want to start the knockout phase? Make sure all group matches are completed."
      confirmText="Start Knockout"
      :danger="true"
      @confirm="startKnockout"
      @cancel="showStartKnockoutModal = false"
    />

    <ConfirmModal
      :show="showRevealListsModal"
      title="Reveal Army Lists"
      message="Are you sure you want to reveal all army lists? Players will be able to see each other's lists."
      confirmText="Reveal Lists"
      @confirm="revealLists"
      @cancel="showRevealListsModal = false"
    />

    <ConfirmModal
      :show="showEndGroupPhaseModal"
      title="End Group Phase"
      message="Are you sure you want to end the group phase? Players will no longer be able to submit group match results."
      confirmText="End Group Phase"
      :danger="true"
      @confirm="endGroupPhase"
      @cancel="showEndGroupPhaseModal = false"
    />

    <ConfirmModal
      :show="showFinishLeagueModal"
      title="Finish League"
      message="Are you sure you want to finish this league? This will mark it as completed."
      confirmText="Finish League"
      :danger="true"
      @confirm="finishLeague"
      @cancel="showFinishLeagueModal = false"
    />

    <ConfirmModal
      :show="showAdvanceKnockoutModal"
      title="Advance to Next Round"
      :message="league?.current_knockout_round === 'final' ? 'The final is complete. This will finish the league.' : 'All matches in this round are confirmed. Advance to the next round?'"
      :confirmText="league?.current_knockout_round === 'final' ? 'Finish League' : 'Advance'"
      @confirm="advanceKnockout"
      @cancel="showAdvanceKnockoutModal = false"
    />

    <!-- Match Score Modal -->
    <div v-if="showMatchModal && selectedMatch" class="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
      <div class="bg-gray-800 rounded-lg p-6 max-w-md w-full mx-4">
        <h3 class="text-xl font-bold mb-4">
          {{ selectedMatch.player1_username }} vs {{ selectedMatch.player2_username }}
        </h3>

        <div v-if="selectedMatch.status === 'confirmed'" class="mb-4">
          <div class="bg-green-900/30 border border-green-500 text-green-200 px-4 py-3 rounded">
            Match result confirmed and locked
          </div>
          <div class="mt-4 text-center">
            <p class="text-2xl font-bold text-squig-yellow">
              {{ selectedMatch.player1_score }} - {{ selectedMatch.player2_score }}
            </p>
            <p class="text-sm text-gray-400 mt-2">
              League points: {{ selectedMatch.player1_league_points }} - {{ selectedMatch.player2_league_points }}
            </p>
          </div>
          <button
            v-if="canConfirmMatch"
            @click="unlockMatch"
            :disabled="submittingScore"
            class="mt-4 w-full btn-secondary border-yellow-500 text-yellow-400 hover:bg-yellow-900/30"
          >
            {{ submittingScore ? 'Unlocking...' : 'Unlock for Editing' }}
          </button>
          <div v-if="matchError" class="mt-2 bg-red-900/30 border border-red-500 text-red-200 px-4 py-3 rounded text-sm">
            {{ matchError }}
          </div>
        </div>

        <div v-else-if="canEditMatch(selectedMatch)">
          <div class="grid grid-cols-2 gap-4 mb-4">
            <div>
              <label class="block text-sm text-gray-400 mb-1">{{ selectedMatch.player1_username }}</label>
              <input
                v-model.number="scoreForm.player1_score"
                type="number"
                min="0"
                max="100"
                class="w-full bg-gray-700 border border-gray-600 rounded px-4 py-2 focus:outline-none focus:border-squig-yellow text-center text-xl"
              />
              <p v-if="calculatedPoints.player1 !== null" class="text-sm text-squig-yellow font-semibold mt-2 text-center">
                {{ calculatedPoints.player1 }} pts
              </p>
            </div>
            <div>
              <label class="block text-sm text-gray-400 mb-1">{{ selectedMatch.player2_username }}</label>
              <input
                v-model.number="scoreForm.player2_score"
                type="number"
                min="0"
                max="100"
                class="w-full bg-gray-700 border border-gray-600 rounded px-4 py-2 focus:outline-none focus:border-squig-yellow text-center text-xl"
              />
              <p v-if="calculatedPoints.player2 !== null" class="text-sm text-squig-yellow font-semibold mt-2 text-center">
                {{ calculatedPoints.player2 }} pts
              </p>
            </div>
          </div>

          <div class="mb-4">
            <label class="block text-sm text-gray-400 mb-1">Map (optional)</label>
            <select
              v-model="scoreForm.map_name"
              class="w-full bg-gray-700 border border-gray-600 rounded px-4 py-2 focus:outline-none focus:border-squig-yellow"
            >
              <option value="">-- Select map --</option>
              <option v-for="map in missionMaps" :key="map" :value="map">{{ map }}</option>
              <option value="__custom__">Custom...</option>
            </select>
            <input
              v-if="scoreForm.map_name === '__custom__'"
              v-model="scoreForm.custom_map"
              type="text"
              placeholder="Enter custom map name"
              class="w-full mt-2 bg-gray-700 border border-gray-600 rounded px-4 py-2 focus:outline-none focus:border-squig-yellow"
            />
          </div>

          <div v-if="matchError" class="mb-4 bg-red-900/30 border border-red-500 text-red-200 px-4 py-3 rounded text-sm">
            {{ matchError }}
          </div>

          <div class="flex gap-2">
            <button
              @click="submitScore"
              :disabled="submittingScore"
              class="flex-1 btn-primary"
            >
              {{ submittingScore ? 'Saving...' : 'Save Score' }}
            </button>
            <button
              v-if="canConfirmThisMatch && selectedMatch.player1_score !== null"
              @click="confirmScore"
              :disabled="submittingScore"
              class="flex-1 btn-primary bg-green-600 hover:bg-green-700"
            >
              {{ submittingScore ? 'Confirming...' : 'Confirm & Lock' }}
            </button>
          </div>
        </div>

        <div v-else class="text-center text-gray-400">
          <p>You don't have permission to edit this match.</p>
          <div v-if="selectedMatch.player1_score !== null" class="mt-4">
            <p class="text-2xl font-bold text-squig-yellow">
              {{ selectedMatch.player1_score }} - {{ selectedMatch.player2_score }}
            </p>
          </div>
        </div>

        <button
          @click="showMatchModal = false"
          class="mt-4 w-full btn-secondary"
        >
          Close
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import axios from 'axios'
import ConfirmModal from '../components/ConfirmModal.vue'
import MatchCard from '../components/MatchCard.vue'
import KnockoutBracket from '../components/KnockoutBracket.vue'

const API_URL = import.meta.env.VITE_API_URL || '/api'
const route = useRoute()
const authStore = useAuthStore()

// GHB 2025/2026 missions
const missionMaps = [
  "Passing Seasons",
  "Paths of the Fey",
  "Roiling Roots",
  "Cyclic Shifts",
  "Surge of Slaughter",
  "Linked Ley Lines",
  "Noxious Nexus",
  "The Liferoots",
  "Bountiful Equinox",
  "Lifecycle",
  "Creeping Corruption",
  "Grasp of Thorns",
]

const loading = ref(true)
const error = ref('')
const actionError = ref('')
const league = ref(null)
const standings = ref([])
const matches = ref([])
const players = ref([])
const activeTab = ref('standings')
const joining = ref(false)
const actionLoading = ref(false)

// Modal states
const showDrawGroupsModal = ref(false)
const showStartKnockoutModal = ref(false)
const showRevealListsModal = ref(false)
const showEndGroupPhaseModal = ref(false)
const showFinishLeagueModal = ref(false)
const showAdvanceKnockoutModal = ref(false)
const showMatchModal = ref(false)
const selectedMatch = ref(null)
const submittingScore = ref(false)
const matchError = ref('')
const scoreForm = ref({
  player1_score: null,
  player2_score: null,
  map_name: '',
  custom_map: '',
})

// Track which groups are expanded in matches view
const expandedGroups = ref({})

const showActionError = (message) => {
  actionError.value = message
  setTimeout(() => {
    actionError.value = ''
  }, 5000)
}

const tabs = computed(() => {
  const baseTabs = [
    { id: 'standings', name: 'Standings' },
    { id: 'matches', name: 'Matches' },
    { id: 'players', name: 'Players' },
  ]
  // Add Knockout tab if league has knockout phase
  if (league.value?.has_knockout_phase) {
    baseTabs.push({ id: 'knockout', name: 'Knockout' })
  }
  return baseTabs
})

const isOrganizer = computed(() => {
  if (!authStore.user || !league.value) return false
  return league.value.organizer_id === authStore.user.id || authStore.user.role === 'admin'
})

const isJoined = computed(() => {
  if (!authStore.user) return false
  return players.value.some(p => p.user_id === authStore.user.id)
})

const groupPhaseEnded = computed(() => {
  if (!league.value) return false
  return league.value.group_phase_ended === true
})

// Get current user's player ID in this league
const currentUserPlayerId = computed(() => {
  if (!authStore.user) return null
  const player = players.value.find(p => p.user_id === authStore.user.id)
  return player?.id || null
})

// Check if match involves current user
const isMyMatch = (match) => {
  const playerId = currentUserPlayerId.value
  if (!playerId) return false
  return match.player1_id === playerId || match.player2_id === playerId
}

// Group matches by group, with my matches first
const groupedMatches = computed(() => {
  const groupMatches = matches.value.filter(m => m.phase === 'group')
  const groups = {}

  for (const match of groupMatches) {
    const groupName = match.group_name || 'Ungrouped'
    if (!groups[groupName]) {
      groups[groupName] = { name: groupName, myMatches: [], otherMatches: [] }
    }
    if (isMyMatch(match)) {
      groups[groupName].myMatches.push(match)
    } else {
      groups[groupName].otherMatches.push(match)
    }
  }

  return Object.values(groups).sort((a, b) => a.name.localeCompare(b.name))
})

// Knockout matches
const knockoutMatches = computed(() => {
  return matches.value.filter(m => m.phase === 'knockout')
})

// Qualified players list (for knockout tab)
const qualifiedPlayers = computed(() => {
  const spots = league.value?.qualifying_spots_per_group || 0
  if (!spots || !league.value?.has_knockout_phase) return []

  // Get qualifying players from each group
  const qualified = []
  for (const group of standings.value) {
    const groupQualified = group.standings
      .filter((p, idx) => idx < spots && p.games_played > 0)
      .map(p => ({
        ...p,
        group_name: group.group_name
      }))
    qualified.push(...groupQualified)
  }

  // Sort by total points (best seed first)
  qualified.sort((a, b) => {
    if (b.total_points !== a.total_points) return b.total_points - a.total_points
    return b.average_points - a.average_points
  })

  return qualified.map((p, idx) => ({ ...p, seed: idx + 1 }))
})

// Check if all current round matches are confirmed
const canAdvanceKnockout = computed(() => {
  if (!isOrganizer.value) return false
  if (league.value?.status !== 'knockout_phase') return false
  if (!league.value?.current_knockout_round) return false

  const currentRoundMatches = knockoutMatches.value.filter(
    m => m.knockout_round === league.value.current_knockout_round
  )

  return currentRoundMatches.length > 0 && currentRoundMatches.every(m => m.status === 'confirmed')
})

// Count pending matches in current knockout round
const pendingKnockoutMatches = computed(() => {
  if (!league.value?.current_knockout_round) return 0
  const currentRoundMatches = knockoutMatches.value.filter(
    m => m.knockout_round === league.value.current_knockout_round
  )
  return currentRoundMatches.filter(m => m.status !== 'confirmed').length
})

// Toggle group expansion
const toggleGroup = (groupName) => {
  expandedGroups.value[groupName] = !expandedGroups.value[groupName]
}

// Initialize expanded groups - expand player's group by default
const initExpandedGroups = () => {
  const userPlayer = players.value.find(p => p.user_id === authStore.user?.id)
  const userGroupName = userPlayer?.group_name

  // Reset all groups to collapsed
  expandedGroups.value = {}

  // Expand user's group if they have one
  if (userGroupName) {
    expandedGroups.value[userGroupName] = true
  }

  // Also expand knockout if in knockout phase
  if (league.value?.status === 'knockout_phase') {
    expandedGroups.value['knockout'] = true
  }
}

// Players sorted by points globally, with qualifying status based on group position
const sortedPlayers = computed(() => {
  const qualifyingSpots = league.value?.qualifying_spots_per_group || 0
  const hasKnockout = league.value?.has_knockout_phase

  // First, determine qualifying status by group
  const groups = {}
  for (const player of players.value) {
    const groupKey = player.group_id || 'ungrouped'
    if (!groups[groupKey]) {
      groups[groupKey] = []
    }
    groups[groupKey].push({ ...player })
  }

  // Sort each group and mark qualifying players
  const qualifyingPlayerIds = new Set()
  for (const groupKey of Object.keys(groups)) {
    if (groupKey === 'ungrouped') continue
    const groupPlayers = groups[groupKey]
    groupPlayers.sort((a, b) => {
      if (b.total_points !== a.total_points) return b.total_points - a.total_points
      return b.average_points - a.average_points
    })
    // Mark top N as qualifying (only if they have played games)
    groupPlayers.forEach((p, idx) => {
      if (hasKnockout && qualifyingSpots > 0 && idx < qualifyingSpots && p.games_played > 0) {
        qualifyingPlayerIds.add(p.id)
      }
    })
  }

  // Now sort all players globally by points
  const allPlayers = players.value.map(p => ({
    ...p,
    wouldQualify: qualifyingPlayerIds.has(p.id)
  }))

  allPlayers.sort((a, b) => {
    if (b.total_points !== a.total_points) return b.total_points - a.total_points
    return b.average_points - a.average_points
  })

  return allPlayers
})

// Can org/admin confirm/unlock matches
const canConfirmMatch = computed(() => {
  if (!authStore.user || !league.value) return false
  return league.value.organizer_id === authStore.user.id || authStore.user.role === 'admin'
})

// Can current user confirm this specific match (org/admin or opponent who didn't submit)
const canConfirmThisMatch = computed(() => {
  if (!selectedMatch.value || !authStore.user) return false

  // Org/admin can always confirm
  if (canConfirmMatch.value) return true

  // Check if current user is opponent (not the one who submitted)
  const playerId = currentUserPlayerId.value
  if (!playerId || !selectedMatch.value.submitted_by_id) return false

  const isPlayer1 = selectedMatch.value.player1_id === playerId
  const isPlayer2 = selectedMatch.value.player2_id === playerId

  if (!isPlayer1 && !isPlayer2) return false

  // Find the submitter's player ID
  const submitterPlayer = players.value.find(p => p.user_id === selectedMatch.value.submitted_by_id)
  if (!submitterPlayer) return false

  // Current user can confirm if they're not the submitter
  return submitterPlayer.id !== playerId
})

// Calculate league points from game scores
const calculatedPoints = computed(() => {
  const p1 = scoreForm.value.player1_score
  const p2 = scoreForm.value.player2_score
  if (p1 === null || p2 === null || p1 === '' || p2 === '') {
    return { player1: null, player2: null }
  }
  return {
    player1: calculateLeaguePoints(p1, p2),
    player2: calculateLeaguePoints(p2, p1),
  }
})

const calculateLeaguePoints = (playerScore, opponentScore) => {
  if (!league.value) return 0
  const { points_per_win, points_per_draw, points_per_loss } = league.value
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

// Check if current user can edit a match (player in match, org, or admin) - not if confirmed
const canEditMatch = (match) => {
  if (!authStore.user || !league.value) return false

  // Confirmed matches are locked for everyone
  if (match.status === 'confirmed') {
    return false
  }

  const isOrgOrAdmin = league.value.organizer_id === authStore.user.id || authStore.user.role === 'admin'

  // Check if user is a player in this match
  const userPlayer = players.value.find(p => p.user_id === authStore.user.id)
  const isPlayer = userPlayer && (userPlayer.id === match.player1_id || userPlayer.id === match.player2_id)

  return isPlayer || isOrgOrAdmin
}

const openMatchModal = (match) => {
  selectedMatch.value = match
  matchError.value = ''

  // Check if existing map is a standard mission or custom
  const existingMap = match.map_name || ''
  const isStandardMap = missionMaps.includes(existingMap)

  scoreForm.value = {
    player1_score: match.player1_score,
    player2_score: match.player2_score,
    map_name: isStandardMap ? existingMap : (existingMap ? '__custom__' : ''),
    custom_map: isStandardMap ? '' : existingMap,
  }
  showMatchModal.value = true
}

const getMapNameForSubmit = () => {
  if (scoreForm.value.map_name === '__custom__') {
    return scoreForm.value.custom_map || null
  }
  return scoreForm.value.map_name || null
}

const submitScore = async () => {
  if (scoreForm.value.player1_score === null || scoreForm.value.player2_score === null) {
    matchError.value = 'Please enter both scores'
    return
  }

  submittingScore.value = true
  matchError.value = ''

  try {
    await axios.post(
      `${API_URL}/league/${league.value.id}/matches/${selectedMatch.value.id}/result`,
      {
        player1_score: scoreForm.value.player1_score,
        player2_score: scoreForm.value.player2_score,
        map_name: getMapNameForSubmit(),
      }
    )
    showMatchModal.value = false
    await fetchLeague()
  } catch (err) {
    matchError.value = err.response?.data?.detail || 'Failed to save score'
  } finally {
    submittingScore.value = false
  }
}

const confirmScore = async () => {
  submittingScore.value = true
  matchError.value = ''

  try {
    // First submit if scores changed
    if (scoreForm.value.player1_score !== selectedMatch.value.player1_score ||
        scoreForm.value.player2_score !== selectedMatch.value.player2_score) {
      await axios.post(
        `${API_URL}/league/${league.value.id}/matches/${selectedMatch.value.id}/result`,
        {
          player1_score: scoreForm.value.player1_score,
          player2_score: scoreForm.value.player2_score,
          map_name: getMapNameForSubmit(),
        }
      )
    }
    // Then confirm
    await axios.post(`${API_URL}/league/${league.value.id}/matches/${selectedMatch.value.id}/confirm`)
    showMatchModal.value = false
    await fetchLeague()
  } catch (err) {
    matchError.value = err.response?.data?.detail || 'Failed to confirm score'
  } finally {
    submittingScore.value = false
  }
}

const unlockMatch = async () => {
  submittingScore.value = true
  matchError.value = ''

  try {
    await axios.post(`${API_URL}/league/${league.value.id}/matches/${selectedMatch.value.id}/unlock`)
    showMatchModal.value = false
    await fetchLeague()
  } catch (err) {
    matchError.value = err.response?.data?.detail || 'Failed to unlock match'
  } finally {
    submittingScore.value = false
  }
}

const fetchLeague = async () => {
  try {
    const leagueId = route.params.id
    const [leagueRes, standingsRes, matchesRes, playersRes] = await Promise.all([
      axios.get(`${API_URL}/league/${leagueId}`),
      axios.get(`${API_URL}/league/${leagueId}/standings`).catch(() => ({ data: [] })),
      axios.get(`${API_URL}/league/${leagueId}/matches`).catch(() => ({ data: [] })),
      axios.get(`${API_URL}/league/${leagueId}/players`).catch(() => ({ data: [] })),
    ])

    league.value = leagueRes.data
    standings.value = standingsRes.data
    matches.value = matchesRes.data
    players.value = playersRes.data

    // Initialize expanded groups after data loads (only on first load)
    if (Object.keys(expandedGroups.value).length === 0) {
      initExpandedGroups()
    }
  } catch (err) {
    error.value = 'Failed to load league'
  } finally {
    loading.value = false
  }
}

const joinLeague = async () => {
  joining.value = true
  actionError.value = ''
  try {
    await axios.post(`${API_URL}/league/${league.value.id}/join`)
    await fetchLeague()
  } catch (err) {
    showActionError(err.response?.data?.detail || 'Failed to join')
  } finally {
    joining.value = false
  }
}

const drawGroups = async () => {
  showDrawGroupsModal.value = false
  actionLoading.value = true
  actionError.value = ''
  try {
    await axios.post(`${API_URL}/league/${league.value.id}/draw-groups`)
    await fetchLeague()
  } catch (err) {
    showActionError(err.response?.data?.detail || 'Failed to draw groups')
  } finally {
    actionLoading.value = false
  }
}

const startKnockout = async () => {
  showStartKnockoutModal.value = false
  actionLoading.value = true
  actionError.value = ''
  try {
    await axios.post(`${API_URL}/league/${league.value.id}/start-knockout`)
    await fetchLeague()
  } catch (err) {
    showActionError(err.response?.data?.detail || 'Failed to start knockout')
  } finally {
    actionLoading.value = false
  }
}

const revealLists = async () => {
  showRevealListsModal.value = false
  actionLoading.value = true
  actionError.value = ''
  try {
    await axios.post(`${API_URL}/league/${league.value.id}/reveal-lists`)
    await fetchLeague()
  } catch (err) {
    showActionError(err.response?.data?.detail || 'Failed to reveal lists')
  } finally {
    actionLoading.value = false
  }
}

const endGroupPhase = async () => {
  showEndGroupPhaseModal.value = false
  actionLoading.value = true
  actionError.value = ''
  try {
    await axios.post(`${API_URL}/league/${league.value.id}/end-group-phase`)
    await fetchLeague()
  } catch (err) {
    showActionError(err.response?.data?.detail || 'Failed to end group phase')
  } finally {
    actionLoading.value = false
  }
}

const finishLeague = async () => {
  showFinishLeagueModal.value = false
  actionLoading.value = true
  actionError.value = ''
  try {
    await axios.patch(`${API_URL}/league/${league.value.id}`, { status: 'finished' })
    await fetchLeague()
  } catch (err) {
    showActionError(err.response?.data?.detail || 'Failed to finish league')
  } finally {
    actionLoading.value = false
  }
}

const advanceKnockout = async () => {
  showAdvanceKnockoutModal.value = false
  actionLoading.value = true
  actionError.value = ''
  try {
    await axios.post(`${API_URL}/league/${league.value.id}/advance-knockout`)
    await fetchLeague()
  } catch (err) {
    showActionError(err.response?.data?.detail || 'Failed to advance knockout')
  } finally {
    actionLoading.value = false
  }
}

const formatDate = (dateString) => {
  return new Date(dateString).toLocaleDateString()
}

const formatDateTime = (dateString) => {
  const date = new Date(dateString)
  return date.toLocaleDateString() + ' ' + date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
}

const statusClass = (status) => {
  switch (status) {
    case 'registration': return 'bg-blue-900/30 border border-blue-500 text-blue-200'
    case 'group_phase': return 'bg-yellow-900/30 border border-yellow-500 text-yellow-200'
    case 'knockout_phase': return 'bg-orange-900/30 border border-orange-500 text-orange-200'
    case 'finished': return 'bg-green-900/30 border border-green-500 text-green-200'
    default: return 'bg-gray-900/30 border border-gray-500 text-gray-200'
  }
}

const statusText = (status) => {
  switch (status) {
    case 'registration': return 'Registration'
    case 'group_phase': return 'Group Phase'
    case 'knockout_phase': return 'Knockout'
    case 'finished': return 'Finished'
    default: return status
  }
}

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

onMounted(() => {
  fetchLeague()
})
</script>
