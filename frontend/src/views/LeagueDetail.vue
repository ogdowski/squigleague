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
        <div class="flex items-center gap-3">
          <!-- Join League Button (prominent) -->
          <button
            v-if="league.is_registration_open && !isJoined"
            @click="joinLeague"
            class="btn-primary"
            :disabled="joining"
          >
            {{ joining ? 'Joining...' : 'Join League' }}
          </button>
          <div
            :class="statusClass(league.status)"
            class="px-4 py-2 rounded text-sm font-bold"
          >
            {{ statusText(league.status) }}
          </div>
          <!-- Hamburger Menu -->
          <div v-if="hasAnyActions" class="relative">
            <button
              @click="showActionsMenu = !showActionsMenu"
              class="p-2 rounded hover:bg-gray-700 transition-colors"
              title="Actions"
            >
              <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16" />
              </svg>
            </button>
            <!-- Dropdown Menu -->
            <div
              v-if="showActionsMenu"
              class="absolute right-0 top-full mt-2 w-56 bg-gray-800 border border-gray-700 rounded-lg shadow-xl z-30"
            >
              <div class="py-1">
                <!-- Leave League -->
                <button
                  v-if="isJoined && canLeaveLeague"
                  @click="showLeaveLeagueModal = true; showActionsMenu = false"
                  class="w-full text-left px-4 py-2 hover:bg-gray-700 text-red-400"
                  :disabled="actionLoading"
                >
                  Leave League
                </button>

                <!-- Divider -->
                <div v-if="isOrganizer && isJoined && canLeaveLeague" class="border-t border-gray-700 my-1"></div>

                <!-- Organizer Actions -->
                <template v-if="isOrganizer">
                  <router-link
                    :to="`/league/${league.id}/settings`"
                    @click="showActionsMenu = false"
                    class="block px-4 py-2 hover:bg-gray-700"
                  >
                    Settings
                  </router-link>

                  <div class="border-t border-gray-700 my-1"></div>

                  <!-- Phase Actions -->
                  <button
                    v-if="league.status === 'registration'"
                    @click="showDrawGroupsModal = true; showActionsMenu = false"
                    class="w-full text-left px-4 py-2 hover:bg-gray-700 text-blue-400"
                    :disabled="actionLoading"
                  >
                    Draw Groups
                  </button>
                  <button
                    v-if="league.status === 'group_phase' && !groupPhaseEnded"
                    @click="showEndGroupPhaseModal = true; showActionsMenu = false"
                    class="w-full text-left px-4 py-2 hover:bg-gray-700 text-yellow-400"
                    :disabled="actionLoading"
                  >
                    End Group Phase
                  </button>
                  <button
                    v-if="league.status === 'group_phase' && groupPhaseEnded && league.has_knockout_phase"
                    @click="showStartKnockoutModal = true; showActionsMenu = false"
                    class="w-full text-left px-4 py-2 hover:bg-gray-700 text-orange-400"
                    :disabled="actionLoading"
                  >
                    Start Knockout
                  </button>
                  <button
                    v-if="league.status === 'group_phase' && groupPhaseEnded && !league.has_knockout_phase"
                    @click="showFinishLeagueModal = true; showActionsMenu = false"
                    class="w-full text-left px-4 py-2 hover:bg-gray-700 text-green-400"
                    :disabled="actionLoading"
                  >
                    Finish League
                  </button>

                  <!-- List Actions -->
                  <template v-if="hasListActions">
                    <div class="border-t border-gray-700 my-1"></div>
                    <div class="px-4 py-1 text-xs text-gray-500 uppercase">Army Lists</div>
                    <button
                      v-if="league.has_group_phase_lists && !league.group_lists_frozen && league.status === 'registration'"
                      @click="freezeGroupLists(); showActionsMenu = false"
                      class="w-full text-left px-4 py-2 hover:bg-gray-700"
                      :disabled="actionLoading"
                    >
                      Freeze Group Lists
                    </button>
                    <button
                      v-if="league.has_group_phase_lists && league.group_lists_frozen && !league.group_lists_visible"
                      @click="revealGroupLists(); showActionsMenu = false"
                      class="w-full text-left px-4 py-2 hover:bg-gray-700"
                      :disabled="actionLoading"
                    >
                      Reveal Group Lists
                    </button>
                    <button
                      v-if="league.has_knockout_phase_lists && league.status === 'knockout_phase' && !league.knockout_lists_frozen"
                      @click="freezeKnockoutLists(); showActionsMenu = false"
                      class="w-full text-left px-4 py-2 hover:bg-gray-700"
                      :disabled="actionLoading"
                    >
                      Freeze Knockout Lists
                    </button>
                    <button
                      v-if="league.has_knockout_phase_lists && league.status === 'knockout_phase' && !league.knockout_lists_visible"
                      @click="showRevealListsModal = true; showActionsMenu = false"
                      class="w-full text-left px-4 py-2 hover:bg-gray-700"
                      :disabled="actionLoading"
                    >
                      Reveal Knockout Lists
                    </button>
                  </template>
                </template>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Click outside to close menu -->
      <div v-if="showActionsMenu" @click="showActionsMenu = false" class="fixed inset-0 z-20"></div>

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
          <h3 class="text-sm text-gray-400 mb-1">Format</h3>
          <p class="text-lg font-bold">{{ leagueFormat }}</p>
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
        <div class="card">
          <h3 class="text-sm text-gray-400 mb-1">{{ phaseEndLabel }}</h3>
          <p class="text-lg font-bold">{{ phaseEndDate }}</p>
        </div>
      </div>

      <!-- Action Error -->
      <div v-if="actionError" class="mb-4 bg-red-900/30 border border-red-500 text-red-200 px-4 py-3 rounded">
        {{ actionError }}
      </div>

      <!-- Army List Submission (for players) -->
      <div v-if="isJoined && canSubmitList" class="card mb-8">
        <h3 class="text-lg font-semibold mb-3">
          {{ listSubmissionPhase === 'group' ? 'Group Phase Army List' : 'Knockout Phase Army List' }}
        </h3>
        <p class="text-sm text-gray-400 mb-4">
          <template v-if="listSubmissionPhase === 'group'">
            Submit your army list before the league starts. Lists will be revealed by the organizer.
          </template>
          <template v-else>
            Submit your army list for the knockout phase.
          </template>
        </p>

        <div v-if="currentPlayerListSubmitted" class="mb-4 p-3 bg-green-900/20 border border-green-600 rounded">
          <p class="text-green-300 text-sm">List submitted!</p>
        </div>

        <div class="mb-4">
          <label class="block text-sm font-medium text-gray-300 mb-2">Army Faction</label>
          <select
            v-model="armyFactionForm"
            class="w-full bg-gray-700 border border-gray-600 rounded px-4 py-2 focus:outline-none focus:border-squig-yellow"
            :disabled="listIsFrozen"
          >
            <option value="">Select your army...</option>
            <option v-for="faction in armyFactions" :key="faction" :value="faction">{{ faction }}</option>
          </select>
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-300 mb-2">Army List</label>
          <textarea
            v-model="armyListForm"
            rows="8"
            class="w-full bg-gray-700 border border-gray-600 rounded px-4 py-2 focus:outline-none focus:border-squig-yellow font-mono text-sm"
            placeholder="Paste your army list here..."
            :disabled="listIsFrozen"
          ></textarea>
        </div>

        <div class="flex items-center justify-between mt-4">
          <p v-if="listIsFrozen" class="text-sm text-yellow-400">Lists are frozen - no more changes allowed.</p>
          <button
            v-if="!listIsFrozen"
            @click="submitArmyList"
            class="btn-primary"
            :disabled="submittingList || !armyListForm.trim() || !armyFactionForm"
          >
            {{ submittingList ? 'Submitting...' : (currentPlayerListSubmitted ? 'Update List' : 'Submit List') }}
          </button>
        </div>
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

      <!-- Registration Phase - Show registered players -->
      <div v-if="league.status === 'registration'" class="card mb-6">
        <h2 class="text-xl font-bold mb-4">Registered Players ({{ players.length }})</h2>
        <div v-if="players.length === 0" class="text-gray-500">No players registered yet.</div>
        <div v-else class="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-3">
          <div v-for="player in players" :key="player.id" class="bg-gray-800 rounded px-3 py-2 flex items-center gap-2">
            <!-- Avatar thumbnail -->
            <div v-if="player.avatar_url" class="w-6 h-6 rounded-full overflow-hidden flex-shrink-0">
              <img :src="player.avatar_url" :alt="player.username" class="w-full h-full object-cover" />
            </div>
            <div v-else class="w-6 h-6 rounded-full bg-gray-700 flex items-center justify-center text-xs text-gray-400 flex-shrink-0">
              {{ (player.username || player.discord_username || '?').charAt(0).toUpperCase() }}
            </div>
            <router-link v-if="player.user_id" :to="`/player/${player.user_id}`" class="hover:text-squig-yellow flex-1 truncate">
              {{ player.username || player.discord_username }}
            </router-link>
            <span v-else class="flex-1 truncate">{{ player.username || player.discord_username }}</span>
            <!-- Army list icon -->
            <button
              v-if="league.has_group_phase_lists"
              @click="player.group_army_list ? showPlayerListModal(player) : null"
              :class="getListIconClass(player, 'group')"
              :title="getListIconTitle(player, 'group')"
              class="flex-shrink-0"
              :disabled="!player.group_army_list"
            >
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
            </button>
            <!-- Remove button for organizer -->
            <button
              v-if="isOrganizer"
              @click="openRemovePlayerModal(player)"
              class="text-red-400 hover:text-red-300 flex-shrink-0"
              title="Remove player"
            >
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
        </div>
      </div>

      <div v-if="activeTab === 'standings'" class="space-y-6">
        <div v-for="group in standings" :key="group.group_id" class="card">
          <div class="flex justify-between items-center mb-4">
            <div class="flex items-center gap-2">
              <h3 v-if="editingGroupId !== group.group_id" class="text-xl font-bold">{{ group.group_name }}</h3>
              <input
                v-else
                v-model="editingGroupName"
                @keyup.enter="saveGroupName(group.group_id)"
                @keyup.escape="cancelEditGroupName"
                class="text-xl font-bold bg-gray-700 border border-gray-600 rounded px-2 py-1 w-48"
                ref="groupNameInput"
              />
              <button
                v-if="isOrganizer && editingGroupId !== group.group_id"
                @click="startEditGroupName(group)"
                class="text-gray-400 hover:text-white"
                title="Edit group name"
              >
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15.232 5.232l3.536 3.536m-2.036-5.036a2.5 2.5 0 113.536 3.536L6.5 21.036H3v-3.572L16.732 3.732z" />
                </svg>
              </button>
              <template v-if="editingGroupId === group.group_id">
                <button @click="saveGroupName(group.group_id)" class="text-green-400 hover:text-green-300" title="Save">
                  <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
                  </svg>
                </button>
                <button @click="cancelEditGroupName" class="text-red-400 hover:text-red-300" title="Cancel">
                  <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              </template>
            </div>
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
                  <td class="py-2 px-2">
                    <div class="flex items-center gap-2">
                      <div v-if="entry.avatar_url" class="w-6 h-6 rounded-full overflow-hidden flex-shrink-0">
                        <img :src="entry.avatar_url" :alt="entry.username" class="w-full h-full object-cover" />
                      </div>
                      <div v-else class="w-6 h-6 rounded-full bg-gray-700 flex items-center justify-center text-xs text-gray-400 flex-shrink-0">
                        {{ (entry.username || entry.discord_username || '?').charAt(0).toUpperCase() }}
                      </div>
                      <div class="flex items-center gap-1">
                        <router-link v-if="entry.user_id" :to="`/player/${entry.user_id}`" class="hover:text-squig-yellow">
                          {{ entry.username || entry.discord_username }}
                        </router-link>
                        <span v-else>{{ entry.username || entry.discord_username }}</span>
                        <!-- Army list icon -->
                        <button
                          v-if="league.has_group_phase_lists"
                          @click="entry.army_list ? showListModal(entry) : null"
                          :class="getStandingsListIconClass(entry)"
                          :title="getStandingsListIconTitle(entry)"
                          :disabled="!entry.army_list"
                        >
                          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                          </svg>
                        </button>
                        <span v-if="entry.army_faction" class="text-xs text-gray-500">({{ entry.army_faction }})</span>
                      </div>
                    </div>
                  </td>
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
              :league-id="league.id"
              :can-edit="canEditMatch(match)"
              :current-player-id="currentUserPlayerId"
              :show-round="true"
              @edit="openMatchModal"
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
                :league-id="league.id"
                :can-edit="canEditMatch(match)"
                :current-player-id="currentUserPlayerId"
                @edit="openMatchModal"
              />
            </div>

            <!-- Other matches in this group -->
            <div v-if="group.otherMatches.length > 0" class="space-y-2">
              <p v-if="group.myMatches.length > 0" class="text-xs text-gray-500 uppercase tracking-wide">Other Matches</p>
              <MatchCard
                v-for="match in group.otherMatches"
                :key="match.id"
                :match="match"
                :league-id="league.id"
                :can-edit="canEditMatch(match)"
                :current-player-id="currentUserPlayerId"
                @edit="openMatchModal"
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
                <th v-if="showKnockoutPlacement" class="text-center py-2 px-2">Knockout</th>
                <th v-if="isOrganizer && league.status !== 'finished'" class="text-center py-2 px-2">Actions</th>
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
                  <div class="flex items-center gap-2">
                    <router-link v-if="player.user_id" :to="`/player/${player.user_id}`" class="hover:text-squig-yellow">
                      {{ player.username || player.discord_username }}
                    </router-link>
                    <span v-else>{{ player.username || player.discord_username }}</span>
                    <!-- Army list icon -->
                    <button
                      v-if="hasAnyListsEnabled"
                      @click="getPlayerArmyList(player) ? showPlayerListModal(player) : null"
                      :class="getListIconClass(player, getCurrentListPhase)"
                      :title="getListIconTitle(player, getCurrentListPhase)"
                      :disabled="!getPlayerArmyList(player)"
                    >
                      <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                      </svg>
                    </button>
                    <span v-if="player.wouldQualify" class="text-xs text-green-400" title="Would advance to knockout">Q</span>
                  </div>
                </td>
                <td class="py-2 px-2">{{ player.group_name || '-' }}</td>
                <td class="py-2 px-2 text-center text-gray-400">{{ player.games_played }}</td>
                <td class="py-2 px-2 text-right font-bold">{{ player.total_points }}</td>
                <td v-if="showKnockoutPlacement" class="py-2 px-2 text-center">
                  <span v-if="player.knockout_placement" :class="placementClass(player.knockout_placement)">
                    {{ formatPlacement(player.knockout_placement) }}
                  </span>
                  <span v-else class="text-gray-600">-</span>
                </td>
                <td v-if="isOrganizer && league.status !== 'finished'" class="py-2 px-2 text-center">
                  <div class="flex items-center justify-center gap-2">
                    <button
                      v-if="league.status === 'group_phase' && player.group_id"
                      @click="openChangeGroupModal(player)"
                      class="text-blue-400 hover:text-blue-300"
                      title="Change group"
                    >
                      <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7h12m0 0l-4-4m4 4l-4 4m0 6H4m0 0l4 4m-4-4l4-4" />
                      </svg>
                    </button>
                    <button
                      @click="openRemovePlayerModal(player)"
                      class="text-red-400 hover:text-red-300"
                      title="Remove player"
                    >
                      <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                      </svg>
                    </button>
                  </div>
                </td>
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
          :league-id="league.id"
          :current-round="league.current_knockout_round"
          :knockout-size="league.knockout_size || league.total_qualifying_spots"
          :qualified-players="qualifiedPlayers"
          :is-preview="knockoutMatches.length === 0"
          @match-click="navigateToMatch"
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

    <ConfirmModal
      :show="showLeaveLeagueModal"
      title="Leave League"
      :message="leaveLeagueMessage"
      confirmText="Leave League"
      :danger="true"
      @confirm="leaveLeague"
      @cancel="showLeaveLeagueModal = false"
    />

    <ConfirmModal
      :show="showRemovePlayerModal"
      title="Remove Player"
      :message="removePlayerMessage"
      confirmText="Remove Player"
      :danger="true"
      @confirm="removePlayer"
      @cancel="showRemovePlayerModal = false"
    />

    <!-- Change Group Modal -->
    <div v-if="showChangeGroupModal && selectedPlayerForAction" class="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
      <div class="bg-gray-800 rounded-lg p-6 max-w-md w-full mx-4">
        <h3 class="text-xl font-bold mb-4">Change Group</h3>
        <p class="text-gray-400 mb-4">
          Move <span class="text-white font-semibold">{{ selectedPlayerForAction.username || selectedPlayerForAction.discord_username }}</span> to:
        </p>
        <select v-model="newGroupId" class="w-full bg-gray-700 border border-gray-600 rounded px-3 py-2 mb-4">
          <option v-for="group in availableGroups" :key="group.group_id" :value="group.group_id">
            {{ group.group_name }}
          </option>
        </select>
        <div v-if="changeGroupError" class="mb-4 bg-red-900/30 border border-red-500 text-red-200 px-4 py-3 rounded text-sm">
          {{ changeGroupError }}
        </div>
        <div class="flex gap-3">
          <button @click="showChangeGroupModal = false" class="flex-1 btn-secondary">Cancel</button>
          <button @click="changePlayerGroup" :disabled="actionLoading" class="flex-1 btn-primary">
            {{ actionLoading ? 'Moving...' : 'Move Player' }}
          </button>
        </div>
      </div>
    </div>

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

    <!-- Army List Modal -->
    <div v-if="showArmyListModal && selectedListEntry" class="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
      <div class="bg-gray-800 rounded-lg p-6 max-w-2xl w-full mx-4 max-h-[80vh] flex flex-col">
        <div class="flex items-center justify-between mb-4">
          <div class="flex items-center gap-3">
            <div v-if="selectedListEntry.avatar_url" class="w-10 h-10 rounded-full overflow-hidden">
              <img :src="selectedListEntry.avatar_url" :alt="selectedListEntry.username" class="w-full h-full object-cover" />
            </div>
            <div v-else class="w-10 h-10 rounded-full bg-gray-700 flex items-center justify-center text-lg text-gray-400">
              {{ (selectedListEntry.username || selectedListEntry.discord_username || '?').charAt(0).toUpperCase() }}
            </div>
            <div>
              <h3 class="text-xl font-bold">{{ selectedListEntry.username || selectedListEntry.discord_username }}</h3>
              <p v-if="selectedListEntry.army_faction && !editingList" class="text-sm text-gray-400">{{ selectedListEntry.army_faction }}</p>
            </div>
          </div>
          <div class="flex items-center gap-2">
            <button
              v-if="isOrganizer && !editingList"
              @click="startEditingList"
              class="text-blue-400 hover:text-blue-300"
              title="Edit list"
            >
              <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15.232 5.232l3.536 3.536m-2.036-5.036a2.5 2.5 0 113.536 3.536L6.5 21.036H3v-3.572L16.732 3.732z" />
              </svg>
            </button>
            <button @click="closeListModal" class="text-gray-400 hover:text-white">
              <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
        </div>

        <!-- View Mode -->
        <template v-if="!editingList">
          <div class="bg-gray-900 rounded p-4 overflow-y-auto flex-1">
            <pre class="whitespace-pre-wrap font-mono text-sm text-gray-300">{{ selectedListEntry.army_list }}</pre>
          </div>
          <button
            @click="closeListModal"
            class="mt-4 w-full btn-secondary"
          >
            Close
          </button>
        </template>

        <!-- Edit Mode (Organizer) -->
        <template v-else>
          <div class="space-y-4 flex-1 overflow-y-auto">
            <div>
              <label class="block text-sm text-gray-400 mb-1">Army Faction</label>
              <select v-model="editListFaction" class="w-full bg-gray-700 border border-gray-600 rounded px-3 py-2">
                <option value="">Select faction...</option>
                <option v-for="faction in armyFactions" :key="faction" :value="faction">{{ faction }}</option>
              </select>
            </div>
            <div class="flex-1">
              <label class="block text-sm text-gray-400 mb-1">Army List</label>
              <textarea
                v-model="editListContent"
                rows="12"
                class="w-full bg-gray-700 border border-gray-600 rounded px-3 py-2 font-mono text-sm"
                placeholder="Paste army list here..."
              ></textarea>
            </div>
            <div v-if="editListError" class="bg-red-900/30 border border-red-500 text-red-200 px-4 py-2 rounded text-sm">
              {{ editListError }}
            </div>
          </div>
          <div class="flex gap-3 mt-4">
            <button @click="cancelEditingList" class="flex-1 btn-secondary">Cancel</button>
            <button
              @click="saveEditedList"
              :disabled="savingList || !editListFaction || !editListContent.trim()"
              class="flex-1 btn-primary"
            >
              {{ savingList ? 'Saving...' : 'Save Changes' }}
            </button>
          </div>
        </template>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import axios from 'axios'
import ConfirmModal from '../components/ConfirmModal.vue'
import MatchCard from '../components/MatchCard.vue'
import KnockoutBracket from '../components/KnockoutBracket.vue'
import { ARMY_FACTIONS } from '../constants/armies'
import { MISSION_MAPS } from '../constants/maps'

const armyFactions = ARMY_FACTIONS
const missionMaps = MISSION_MAPS

const API_URL = import.meta.env.VITE_API_URL || '/api'
const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()

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

// Leave league modal
const showLeaveLeagueModal = ref(false)

// Player management modals
const showRemovePlayerModal = ref(false)
const showChangeGroupModal = ref(false)
const selectedPlayerForAction = ref(null)
const newGroupId = ref(null)
const changeGroupError = ref('')

// Actions menu state
const showActionsMenu = ref(false)

// List editing state (for organizers)
const editingList = ref(false)
const editListFaction = ref('')
const editListContent = ref('')
const editListError = ref('')
const savingList = ref(false)
const editListPhase = ref('group') // 'group' or 'knockout'

// Army list viewing modal
const showArmyListModal = ref(false)
const selectedListEntry = ref(null)

// Group name editing
const editingGroupId = ref(null)
const editingGroupName = ref('')
const matchError = ref('')
const scoreForm = ref({
  player1_score: null,
  player2_score: null,
  map_name: '',
  custom_map: '',
})

// Track which groups are expanded in matches view
const expandedGroups = ref({})

// Army list submission
const armyFactionForm = ref('')
const armyListForm = ref('')
const submittingList = ref(false)

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

// Can player leave the league?
const canLeaveLeague = computed(() => {
  if (!league.value) return false
  // Can leave during registration or active phases, but not when finished
  return league.value.status !== 'finished'
})

// Message for leave league modal
const leaveLeagueMessage = computed(() => {
  if (!league.value) return ''
  if (league.value.status === 'registration') {
    return 'Are you sure you want to leave this league? You can rejoin before registration closes.'
  }
  return 'Are you sure you want to leave? Your opponents will receive walkover wins (25:0, 1075 points) for unplayed matches.'
})

// Message for remove player modal
const removePlayerMessage = computed(() => {
  if (!selectedPlayerForAction.value || !league.value) return ''
  const name = selectedPlayerForAction.value.username || selectedPlayerForAction.value.discord_username
  if (league.value.status === 'registration') {
    return `Remove ${name} from the league?`
  }
  return `Remove ${name}? Their opponents will receive walkover wins (25:0, 1075 points) for unplayed matches.`
})

// Available groups for change group modal
const availableGroups = computed(() => {
  if (!standings.value || !selectedPlayerForAction.value) return []
  return standings.value.filter(g => g.group_id !== selectedPlayerForAction.value.group_id)
})

// Check if there are any actions available for the menu (excluding Join which is a separate button)
const hasAnyActions = computed(() => {
  if (!league.value) return false
  // Can leave
  if (isJoined.value && canLeaveLeague.value) return true
  // Is organizer
  if (isOrganizer.value) return true
  return false
})

// Check if there are list-related actions available
const hasListActions = computed(() => {
  if (!league.value || !isOrganizer.value) return false
  // Group phase list actions
  if (league.value.has_group_phase_lists && !league.value.group_lists_frozen && league.value.status === 'registration') return true
  if (league.value.has_group_phase_lists && league.value.group_lists_frozen && !league.value.group_lists_visible) return true
  // Knockout phase list actions
  if (league.value.has_knockout_phase_lists && league.value.status === 'knockout_phase' && !league.value.knockout_lists_frozen) return true
  if (league.value.has_knockout_phase_lists && league.value.status === 'knockout_phase' && !league.value.knockout_lists_visible) return true
  return false
})

const groupPhaseEnded = computed(() => {
  if (!league.value) return false
  return league.value.group_phase_ended === true
})

// League format description
const leagueFormat = computed(() => {
  if (!league.value) return ''
  if (league.value.has_knockout_phase) {
    const knockoutInfo = league.value.knockout_size ? ` (Top ${league.value.knockout_size})` : ''
    return `Groups + Knockout${knockoutInfo}`
  }
  return 'Groups Only'
})

// Phase end label and date based on current status
const phaseEndLabel = computed(() => {
  if (!league.value) return 'Ends'
  if (league.value.status === 'registration') return 'Registration Ends'
  if (league.value.status === 'group_phase') return 'Group Phase Ends'
  if (league.value.status === 'knockout_phase') return 'Round Deadline'
  if (league.value.status === 'finished') return 'Finished'
  return 'Ends'
})

const phaseEndDate = computed(() => {
  if (!league.value) return '-'
  if (league.value.status === 'registration') {
    return formatDateTime(league.value.registration_end)
  }
  if (league.value.status === 'group_phase') {
    return league.value.group_phase_end ? formatDateTime(league.value.group_phase_end) : '-'
  }
  if (league.value.status === 'knockout_phase') {
    return league.value.knockout_phase_end ? formatDateTime(league.value.knockout_phase_end) : '-'
  }
  if (league.value.status === 'finished') {
    return league.value.finished_at ? formatDateTime(league.value.finished_at) : '-'
  }
  return '-'
})

// Get current user's player ID in this league
const currentUserPlayerId = computed(() => {
  if (!authStore.user) return null
  const player = players.value.find(p => p.user_id === authStore.user.id)
  return player?.id || null
})

// Get current user's player object
const currentPlayer = computed(() => {
  if (!authStore.user) return null
  return players.value.find(p => p.user_id === authStore.user.id)
})

// Determine which phase allows list submission
const listSubmissionPhase = computed(() => {
  if (!league.value) return null
  // During registration: group lists
  if (league.value.status === 'registration' && league.value.has_group_phase_lists) {
    return 'group'
  }
  // After group phase ended, before/during knockout: knockout lists
  if (league.value.has_knockout_phase_lists &&
      (league.value.group_phase_ended || league.value.status === 'knockout_phase')) {
    return 'knockout'
  }
  return null
})

// Can current user submit a list?
const canSubmitList = computed(() => {
  if (!league.value || !listSubmissionPhase.value) return false
  if (listSubmissionPhase.value === 'group') {
    return !league.value.group_lists_frozen
  }
  return !league.value.knockout_lists_frozen
})

// Is the current list frozen?
const listIsFrozen = computed(() => {
  if (!league.value || !listSubmissionPhase.value) return true
  if (listSubmissionPhase.value === 'group') {
    return league.value.group_lists_frozen
  }
  return league.value.knockout_lists_frozen
})

// Has current player submitted their list for current phase?
const currentPlayerListSubmitted = computed(() => {
  if (!currentPlayer.value || !listSubmissionPhase.value) return false
  if (listSubmissionPhase.value === 'group') {
    return currentPlayer.value.group_list_submitted
  }
  return currentPlayer.value.knockout_list_submitted
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

// Show knockout placement column when league is in knockout or finished
const showKnockoutPlacement = computed(() => {
  if (!league.value?.has_knockout_phase) return false
  return league.value.status === 'knockout_phase' || league.value.status === 'finished'
})

// Format placement for display
const formatPlacement = (placement) => {
  if (placement === '1') return '1st'
  if (placement === '2') return '2nd'
  return placement.replace('top_', 'Top ')
}

// Class for placement badge
const placementClass = (placement) => {
  if (placement === '1') return 'text-yellow-400 font-bold'
  if (placement === '2') return 'text-gray-300 font-bold'
  if (placement === 'top_4') return 'text-orange-400'
  return 'text-gray-400'
}

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

// Open army list modal
const showListModal = (entry) => {
  selectedListEntry.value = entry
  showArmyListModal.value = true
}

// Group name editing
const startEditGroupName = (group) => {
  editingGroupId.value = group.group_id
  editingGroupName.value = group.group_name
}

const cancelEditGroupName = () => {
  editingGroupId.value = null
  editingGroupName.value = ''
}

const saveGroupName = async (groupId) => {
  if (!editingGroupName.value.trim()) return

  try {
    await axios.patch(`${API_URL}/league/${league.value.id}/groups/${groupId}`, {
      name: editingGroupName.value.trim()
    })
    // Update local state
    const group = standings.value.find(g => g.group_id === groupId)
    if (group) {
      group.group_name = editingGroupName.value.trim()
    }
    cancelEditGroupName()
  } catch (err) {
    console.error('Failed to update group name:', err)
    showActionError(err.response?.data?.detail || 'Failed to update group name')
  }
}

// Navigate to match detail page (for bracket clicks)
const navigateToMatch = (match) => {
  if (match.status !== 'preview') {
    router.push(`/league/${league.value.id}/match/${match.id}`)
  }
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

const freezeGroupLists = async () => {
  actionLoading.value = true
  actionError.value = ''
  try {
    await axios.post(`${API_URL}/league/${league.value.id}/freeze-group-lists`)
    await fetchLeague()
  } catch (err) {
    showActionError(err.response?.data?.detail || 'Failed to freeze group lists')
  } finally {
    actionLoading.value = false
  }
}

const revealGroupLists = async () => {
  actionLoading.value = true
  actionError.value = ''
  try {
    await axios.post(`${API_URL}/league/${league.value.id}/reveal-group-lists`)
    await fetchLeague()
  } catch (err) {
    showActionError(err.response?.data?.detail || 'Failed to reveal group lists')
  } finally {
    actionLoading.value = false
  }
}

const freezeKnockoutLists = async () => {
  actionLoading.value = true
  actionError.value = ''
  try {
    await axios.post(`${API_URL}/league/${league.value.id}/freeze-lists`)
    await fetchLeague()
  } catch (err) {
    showActionError(err.response?.data?.detail || 'Failed to freeze knockout lists')
  } finally {
    actionLoading.value = false
  }
}

const submitArmyList = async () => {
  submittingList.value = true
  actionError.value = ''
  try {
    const endpoint = listSubmissionPhase.value === 'group'
      ? `${API_URL}/league/${league.value.id}/group-list`
      : `${API_URL}/league/${league.value.id}/knockout-list`
    await axios.post(endpoint, {
      army_faction: armyFactionForm.value,
      army_list: armyListForm.value
    })
    // Refresh players to update submitted status
    const playersRes = await axios.get(`${API_URL}/league/${league.value.id}/players`)
    players.value = playersRes.data
  } catch (err) {
    showActionError(err.response?.data?.detail || 'Failed to submit army list')
  } finally {
    submittingList.value = false
  }
}

// Leave league (player drops out)
const leaveLeague = async () => {
  showLeaveLeagueModal.value = false
  actionLoading.value = true
  actionError.value = ''
  try {
    await axios.post(`${API_URL}/league/${league.value.id}/leave`)
    await fetchLeague()
  } catch (err) {
    showActionError(err.response?.data?.detail || 'Failed to leave league')
  } finally {
    actionLoading.value = false
  }
}

// Open remove player modal (organizer)
const openRemovePlayerModal = (player) => {
  selectedPlayerForAction.value = player
  showRemovePlayerModal.value = true
}

// Remove player (organizer)
const removePlayer = async () => {
  showRemovePlayerModal.value = false
  actionLoading.value = true
  actionError.value = ''
  try {
    await axios.delete(`${API_URL}/league/${league.value.id}/player/${selectedPlayerForAction.value.id}`)
    selectedPlayerForAction.value = null
    await fetchLeague()
  } catch (err) {
    showActionError(err.response?.data?.detail || 'Failed to remove player')
  } finally {
    actionLoading.value = false
  }
}

// Open change group modal (organizer)
const openChangeGroupModal = (player) => {
  selectedPlayerForAction.value = player
  newGroupId.value = null
  changeGroupError.value = ''
  showChangeGroupModal.value = true
}

// Change player group (organizer)
const changePlayerGroup = async () => {
  if (!newGroupId.value) {
    changeGroupError.value = 'Please select a group'
    return
  }
  actionLoading.value = true
  changeGroupError.value = ''
  try {
    await axios.patch(
      `${API_URL}/league/${league.value.id}/player/${selectedPlayerForAction.value.id}/group`,
      { group_id: newGroupId.value }
    )
    showChangeGroupModal.value = false
    selectedPlayerForAction.value = null
    await fetchLeague()
  } catch (err) {
    changeGroupError.value = err.response?.data?.detail || 'Failed to change group'
  } finally {
    actionLoading.value = false
  }
}

// Check if any lists are enabled for this league
const hasAnyListsEnabled = computed(() => {
  if (!league.value) return false
  return league.value.has_group_phase_lists || league.value.has_knockout_phase_lists
})

// Get current list phase based on league status
const getCurrentListPhase = computed(() => {
  if (!league.value) return 'group'
  if (league.value.status === 'knockout_phase' || league.value.status === 'finished') {
    return league.value.has_knockout_phase_lists ? 'knockout' : 'group'
  }
  return 'group'
})

// Get player's army list based on current phase
const getPlayerArmyList = (player) => {
  if (!league.value) return null
  // Check if lists are visible for the current phase
  if (league.value.status === 'knockout_phase' || league.value.status === 'finished') {
    if (league.value.knockout_lists_visible && player.knockout_army_list) {
      return { faction: player.knockout_army_faction, list: player.knockout_army_list }
    }
  }
  if (league.value.group_lists_visible && player.group_army_list) {
    return { faction: player.group_army_faction, list: player.group_army_list }
  }
  return null
}

// Get list icon CSS class based on status
// White = revealed, Yellow = submitted but not visible, Red = not submitted
const getListIconClass = (player, phase) => {
  if (!league.value) return 'text-red-500'

  const isGroup = phase === 'group'
  const submitted = isGroup ? player.group_list_submitted : player.knockout_list_submitted
  const visible = isGroup ? league.value.group_lists_visible : league.value.knockout_lists_visible
  const hasList = isGroup ? player.group_army_list : player.knockout_army_list

  if (hasList && visible) {
    return 'text-white hover:text-gray-300 cursor-pointer'
  } else if (submitted) {
    return 'text-yellow-400 cursor-default'
  } else {
    return 'text-red-500 cursor-default'
  }
}

// Get list icon title/tooltip based on status
const getListIconTitle = (player, phase) => {
  if (!league.value) return 'List not submitted'

  const isGroup = phase === 'group'
  const submitted = isGroup ? player.group_list_submitted : player.knockout_list_submitted
  const visible = isGroup ? league.value.group_lists_visible : league.value.knockout_lists_visible
  const hasList = isGroup ? player.group_army_list : player.knockout_army_list

  if (hasList && visible) {
    return 'Army list'
  } else if (submitted) {
    return 'List hidden'
  } else {
    return 'List not submitted'
  }
}

// For standings entries (uses entry.list_submitted and entry.army_list)
const getStandingsListIconClass = (entry) => {
  if (!league.value) return 'text-red-500'

  if (entry.army_list && league.value.group_lists_visible) {
    return 'text-white hover:text-gray-300 cursor-pointer'
  } else if (entry.list_submitted) {
    return 'text-yellow-400 cursor-default'
  } else {
    return 'text-red-500 cursor-default'
  }
}

const getStandingsListIconTitle = (entry) => {
  if (!league.value) return 'List not submitted'

  if (entry.army_list && league.value.group_lists_visible) {
    return 'Army list'
  } else if (entry.list_submitted) {
    return 'List hidden'
  } else {
    return 'List not submitted'
  }
}

// Show player list modal
const showPlayerListModal = (player) => {
  const armyData = getPlayerArmyList(player)
  if (armyData) {
    selectedListEntry.value = {
      ...player,
      army_faction: armyData.faction,
      army_list: armyData.list
    }
    // Determine which phase this list is from
    if (league.value?.knockout_lists_visible && player.knockout_army_list) {
      editListPhase.value = 'knockout'
    } else {
      editListPhase.value = 'group'
    }
    editingList.value = false
    showArmyListModal.value = true
  }
}

// Close list modal
const closeListModal = () => {
  showArmyListModal.value = false
  editingList.value = false
  editListError.value = ''
}

// Start editing list (organizer)
const startEditingList = () => {
  editListFaction.value = selectedListEntry.value.army_faction || ''
  editListContent.value = selectedListEntry.value.army_list || ''
  editListError.value = ''
  editingList.value = true
}

// Cancel editing list
const cancelEditingList = () => {
  editingList.value = false
  editListError.value = ''
}

// Save edited list
const saveEditedList = async () => {
  if (!selectedListEntry.value || !league.value) return

  savingList.value = true
  editListError.value = ''

  try {
    const endpoint = editListPhase.value === 'knockout'
      ? `${API_URL}/league/${league.value.id}/knockout-list/${selectedListEntry.value.id}`
      : `${API_URL}/league/${league.value.id}/group-list/${selectedListEntry.value.id}`

    await axios.put(endpoint, {
      army_faction: editListFaction.value,
      army_list: editListContent.value
    })

    // Update the modal view
    selectedListEntry.value.army_faction = editListFaction.value
    selectedListEntry.value.army_list = editListContent.value

    // Refresh data
    await fetchLeague()

    editingList.value = false
  } catch (err) {
    editListError.value = err.response?.data?.detail || 'Failed to save list'
  } finally {
    savingList.value = false
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
