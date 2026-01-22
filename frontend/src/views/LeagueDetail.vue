<template>
  <div class="max-w-6xl mx-auto">
    <div v-if="loading" class="text-center py-12">
      <p class="text-xl text-gray-300">{{ t('leagueDetail.loadingLeague') }}</p>
    </div>

    <div v-else-if="error" class="card">
      <div class="bg-red-900/30 border border-red-500 text-red-200 px-4 py-3 rounded">
        {{ error }}
      </div>
    </div>

    <div v-else-if="league">
      <!-- Header -->
      <div class="flex flex-col sm:flex-row sm:justify-between sm:items-start gap-4 mb-6">
        <div>
          <h1 class="text-2xl md:text-3xl font-bold text-squig-yellow mb-2">{{ league.name }}</h1>
          <p v-if="league.organizer_name" class="text-sm text-gray-500">
            {{ t('leagueDetail.organizer') }}:
            <RouterLink
              v-if="league.organizer_id"
              :to="{ name: 'PlayerProfile', params: { userId: league.organizer_id } }"
              class="text-squig-yellow hover:underline"
            >{{ league.organizer_name }}</RouterLink>
            <span v-else class="text-gray-300">{{ league.organizer_name }}</span>
          </p>
          <p v-if="league.city || league.country" class="text-sm text-gray-500">
            {{ [league.city, league.country].filter(Boolean).join(', ') }}
          </p>
        </div>
        <div class="flex items-center gap-2 sm:gap-3 flex-wrap justify-end sm:justify-start">
          <!-- Join League Button (prominent) -->
          <button
            v-if="league.is_registration_open && !isJoined"
            @click="joinLeague"
            class="btn-primary"
            :disabled="joining"
          >
            {{ joining ? t('leagueDetail.joining') : t('leagueDetail.joinLeague') }}
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
              :title="t('leagueDetail.actions')"
            >
              <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16" />
              </svg>
            </button>
            <!-- Dropdown Menu -->
            <div
              v-if="showActionsMenu"
              class="absolute right-0 sm:right-0 top-full mt-2 w-[calc(100vw-2rem)] sm:w-56 max-w-[14rem] bg-gray-800 border border-gray-700 rounded-lg shadow-xl z-30"
              style="right: 0; left: auto;"
            >
              <div class="py-1">
                <!-- Leave League -->
                <button
                  v-if="isJoined && canLeaveLeague"
                  @click="showLeaveLeagueModal = true; showActionsMenu = false"
                  class="w-full text-left px-4 py-2 hover:bg-gray-700 text-red-400"
                  :disabled="actionLoading"
                >
                  {{ t('leagueDetail.leaveLeague') }}
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
                    {{ t('leagueDetail.settings') }}
                  </router-link>

                  <div class="border-t border-gray-700 my-1"></div>

                  <!-- Phase Actions -->
                  <button
                    v-if="league.status === 'registration'"
                    @click="showDrawGroupsModal = true; showActionsMenu = false"
                    class="w-full text-left px-4 py-2 hover:bg-gray-700 text-blue-400"
                    :disabled="actionLoading"
                  >
                    {{ t('leagueDetail.drawGroups') }}
                  </button>
                  <button
                    v-if="league.status === 'group_phase' && !groupPhaseEnded"
                    @click="showEndGroupPhaseModal = true; showActionsMenu = false"
                    class="w-full text-left px-4 py-2 hover:bg-gray-700 text-yellow-400"
                    :disabled="actionLoading"
                  >
                    {{ t('leagueDetail.endGroupPhase') }}
                  </button>
                  <button
                    v-if="league.status === 'group_phase' && groupPhaseEnded && league.has_knockout_phase"
                    @click="showStartKnockoutModal = true; showActionsMenu = false"
                    class="w-full text-left px-4 py-2 hover:bg-gray-700 text-orange-400"
                    :disabled="actionLoading"
                  >
                    {{ t('leagueDetail.startKnockout') }}
                  </button>
                  <button
                    v-if="league.status === 'group_phase' && groupPhaseEnded && !league.has_knockout_phase"
                    @click="showFinishLeagueModal = true; showActionsMenu = false"
                    class="w-full text-left px-4 py-2 hover:bg-gray-700 text-green-400"
                    :disabled="actionLoading"
                  >
                    {{ t('leagueDetail.finishLeague') }}
                  </button>

                  <!-- List Actions -->
                  <template v-if="hasListActions">
                    <div class="border-t border-gray-700 my-1"></div>
                    <div class="px-4 py-1 text-xs text-gray-500 uppercase">{{ t('leagueDetail.armyLists') }}</div>
                    <button
                      v-if="league.has_group_phase_lists && !league.group_lists_frozen && league.status === 'registration'"
                      @click="freezeGroupLists(); showActionsMenu = false"
                      class="w-full text-left px-4 py-2 hover:bg-gray-700"
                      :disabled="actionLoading"
                    >
                      {{ t('leagueDetail.freezeGroupLists') }}
                    </button>
                    <button
                      v-if="league.has_group_phase_lists && league.group_lists_frozen && !league.group_lists_visible"
                      @click="revealGroupLists(); showActionsMenu = false"
                      class="w-full text-left px-4 py-2 hover:bg-gray-700"
                      :disabled="actionLoading"
                    >
                      {{ t('leagueDetail.revealGroupLists') }}
                    </button>
                    <button
                      v-if="league.has_knockout_phase_lists && league.status === 'knockout_phase' && !league.knockout_lists_frozen"
                      @click="freezeKnockoutLists(); showActionsMenu = false"
                      class="w-full text-left px-4 py-2 hover:bg-gray-700"
                      :disabled="actionLoading"
                    >
                      {{ t('leagueDetail.freezeKnockoutLists') }}
                    </button>
                    <button
                      v-if="league.has_knockout_phase_lists && league.status === 'knockout_phase' && !league.knockout_lists_visible"
                      @click="showRevealListsModal = true; showActionsMenu = false"
                      class="w-full text-left px-4 py-2 hover:bg-gray-700"
                      :disabled="actionLoading"
                    >
                      {{ t('leagueDetail.revealKnockoutLists') }}
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

      <!-- Info Cards - collapsible on mobile -->
      <div class="mb-6 md:mb-8">
        <!-- Mobile: collapsible header -->
        <button
          @click="showInfoCards = !showInfoCards"
          class="md:hidden w-full flex items-center justify-between bg-gray-800 rounded-lg px-4 py-3 mb-2"
        >
          <div class="flex items-center gap-3">
            <span class="text-lg font-bold">{{ league.player_count }}</span>
            <span class="text-gray-400 text-sm">{{ t('leagueDetail.players') }}</span>
            <span class="text-gray-600">•</span>
            <span class="text-sm">{{ leagueFormat }}</span>
          </div>
          <svg
            class="w-5 h-5 text-gray-400 transition-transform"
            :class="{ 'rotate-180': showInfoCards }"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
          </svg>
        </button>
        <!-- Cards grid - always visible on desktop, toggleable on mobile -->
        <div :class="{ 'hidden': !showInfoCards }" class="md:block">
          <div class="grid grid-cols-2 md:grid-cols-2 lg:grid-cols-4 gap-3 md:gap-4">
            <div class="card p-3 md:p-6">
              <h3 class="text-xs md:text-sm text-gray-400 mb-1">{{ t('leagueDetail.players') }}</h3>
              <p class="text-xl md:text-2xl font-bold">{{ league.player_count }}</p>
              <p v-if="league.qualifying_spots_per_group" class="text-xs text-gray-500 mt-1 hidden md:block">
                {{ t('leagueDetail.topPerGroupAdvance', { count: league.qualifying_spots_per_group }) }}
              </p>
            </div>
            <div class="card p-3 md:p-6">
              <h3 class="text-xs md:text-sm text-gray-400 mb-1">{{ t('leagueDetail.format') }}</h3>
              <p class="text-base md:text-lg font-bold">{{ leagueFormat }}</p>
            </div>
            <div class="card p-3 md:p-6">
              <div class="flex items-center gap-1 md:gap-2 mb-1">
                <h3 class="text-xs md:text-sm text-gray-400">{{ t('leagueDetail.scoring') }}</h3>
                <div class="relative group hidden md:block">
                  <svg class="w-4 h-4 text-gray-400 cursor-help" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <circle cx="12" cy="12" r="10" stroke-width="2"/>
                    <path stroke-width="2" d="M12 16v-4m0-4h.01"/>
                  </svg>
                  <div class="absolute left-0 top-6 w-72 p-3 bg-gray-800 border border-gray-600 rounded shadow-lg text-xs text-gray-300 hidden group-hover:block z-20">
                    <p class="font-semibold mb-2">{{ t('leagueDetail.howScoringWorks') }}</p>
                    <ul class="space-y-1 mb-2">
                      <li><span class="text-green-400">{{ t('leagueDetail.win') }}:</span> {{ league.points_per_win }} {{ t('profile.pts') }}</li>
                      <li><span class="text-yellow-400">{{ t('leagueDetail.draw') }}:</span> {{ league.points_per_draw }} {{ t('profile.pts') }}</li>
                      <li><span class="text-red-400">{{ t('leagueDetail.loss') }}:</span> {{ league.points_per_loss }} {{ t('profile.pts') }}</li>
                    </ul>
                    <p class="mb-2">{{ t('leagueDetail.bonusExplanation') }}<br/>
                    <span class="text-gray-400">bonus = min(100, max(0, diff + 50))</span></p>
                    <p class="font-semibold mb-1">{{ t('leagueDetail.examples') }}</p>
                    <ul class="space-y-1 text-gray-400">
                      <li>{{ t('leagueDetail.win') }} 72-68: {{ league.points_per_win }} + 54 = <span class="text-white">{{ league.points_per_win + 54 }}</span></li>
                      <li>{{ t('leagueDetail.loss') }} 68-72: {{ league.points_per_loss }} + 46 = <span class="text-white">{{ league.points_per_loss + 46 }}</span></li>
                      <li>{{ t('leagueDetail.draw') }} 70-70: {{ league.points_per_draw }} + 50 = <span class="text-white">{{ league.points_per_draw + 50 }}</span></li>
                    </ul>
                  </div>
                </div>
              </div>
              <p class="text-xs md:text-sm">W: {{ league.points_per_win }} / D: {{ league.points_per_draw }} / L: {{ league.points_per_loss }}</p>
            </div>
            <div class="card p-3 md:p-6">
              <h3 class="text-xs md:text-sm text-gray-400 mb-1">{{ phaseEndLabel }}</h3>
              <p class="text-base md:text-lg font-bold">{{ phaseEndDate }}</p>
            </div>
          </div>
        </div>
      </div>

      <!-- Action Error -->
      <div v-if="actionError" class="mb-4 bg-red-900/30 border border-red-500 text-red-200 px-4 py-3 rounded">
        {{ actionError }}
      </div>

      <!-- Army List Submission (for players) -->
      <div v-if="isJoined && canSubmitList" class="card mb-8">
        <h3 class="text-lg font-semibold mb-3">
          {{ listSubmissionPhase === 'group' ? t('leagueDetail.groupPhaseArmyList') : t('leagueDetail.knockoutPhaseArmyList') }}
        </h3>
        <p class="text-sm text-gray-400 mb-4">
          <template v-if="listSubmissionPhase === 'group'">
            {{ t('leagueDetail.submitListBeforeLeagueStarts') }}
          </template>
          <template v-else>
            {{ t('leagueDetail.submitListForKnockout') }}
          </template>
        </p>

        <div v-if="currentPlayerListSubmitted" class="mb-4 p-3 bg-green-900/20 border border-green-600 rounded">
          <p class="text-green-300 text-sm">{{ t('leagueDetail.listSubmitted') }}</p>
        </div>

        <div class="mb-4">
          <label class="block text-sm font-medium text-gray-300 mb-2">{{ t('leagueDetail.armyFaction') }}</label>
          <select
            v-model="armyFactionForm"
            class="w-full bg-gray-700 border border-gray-600 rounded px-4 py-2 focus:outline-none focus:border-squig-yellow"
            :disabled="listIsFrozen"
          >
            <option value="">{{ t('leagueDetail.selectYourArmy') }}</option>
            <option v-for="faction in armyFactions" :key="faction" :value="faction">{{ faction }}</option>
          </select>
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-300 mb-2">{{ t('matchups.armyList') }}</label>
          <textarea
            v-model="armyListForm"
            rows="8"
            class="w-full bg-gray-700 border border-gray-600 rounded px-4 py-2 focus:outline-none focus:border-squig-yellow font-mono text-sm"
            :placeholder="t('leagueDetail.pasteArmyListHere')"
            :disabled="listIsFrozen"
          ></textarea>
        </div>

        <div class="flex items-center justify-between mt-4">
          <p v-if="listIsFrozen" class="text-sm text-yellow-400">{{ t('leagueDetail.listsFrozen') }}</p>
          <button
            v-if="!listIsFrozen"
            @click="submitArmyList"
            class="btn-primary"
            :disabled="submittingList || !armyListForm.trim() || !armyFactionForm"
          >
            {{ submittingList ? t('leagueDetail.submitting') : (currentPlayerListSubmitted ? t('leagueDetail.updateList') : t('leagueDetail.submitList')) }}
          </button>
        </div>
      </div>

      <!-- Registration Phase - Show registered players -->
      <div v-if="league.status === 'registration'" class="card mb-6">
        <h2 class="text-xl font-bold mb-4">{{ t('leagueDetail.registeredPlayers', { count: players.length }) }}</h2>
        <div v-if="players.length === 0" class="text-gray-500">{{ t('leagueDetail.noPlayersRegistered') }}</div>
        <div v-else class="space-y-2">
          <div v-for="player in players" :key="player.id" class="bg-gray-800 rounded px-4 py-3 flex items-center gap-3">
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
              :title="t('leagueDetail.removePlayer')"
            >
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
        </div>
      </div>

      <!-- Tabs: Menu overlay on mobile, buttons on desktop -->
      <!-- Mobile tabs menu -->
      <div class="md:hidden mb-4">
        <button
          @click="showTabsMenu = !showTabsMenu"
          class="w-full flex items-center justify-between bg-gray-700 border border-gray-600 rounded-lg px-4 py-3 text-white"
        >
          <span class="font-medium">{{ tabs.find(t => t.id === activeTab)?.name }}</span>
          <svg
            class="w-5 h-5 text-gray-400 transition-transform"
            :class="{ 'rotate-180': showTabsMenu }"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
          </svg>
        </button>
        <!-- Tabs overlay menu -->
        <Transition name="tabs-menu">
          <div v-if="showTabsMenu" class="fixed inset-0 z-50">
            <!-- Backdrop -->
            <div class="fixed inset-0 bg-black/50" @click="showTabsMenu = false"></div>
            <!-- Menu panel -->
            <div class="fixed inset-x-4 top-1/3 bg-gray-800 border border-gray-700 rounded-xl shadow-xl overflow-hidden">
              <div class="p-2 space-y-1">
                <button
                  v-for="tab in tabs"
                  :key="tab.id"
                  @click="changeTab(tab.id); showTabsMenu = false"
                  class="w-full flex items-center justify-between px-4 py-3 rounded-lg transition-colors"
                  :class="activeTab === tab.id ? 'bg-squig-yellow/20 text-squig-yellow' : 'hover:bg-gray-700 text-white'"
                >
                  <span class="font-medium">{{ tab.name }}</span>
                  <svg
                    v-if="activeTab === tab.id"
                    class="w-5 h-5"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
                  </svg>
                </button>
              </div>
            </div>
          </div>
        </Transition>
      </div>
      <!-- Desktop tabs -->
      <div class="hidden md:flex gap-2 mb-6 border-b border-gray-700">
        <button
          v-for="tab in tabs"
          :key="tab.id"
          @click="changeTab(tab.id)"
          :class="activeTab === tab.id ? 'border-squig-yellow text-squig-yellow' : 'border-transparent text-gray-400'"
          class="px-4 py-2 border-b-2 transition-colors"
        >
          {{ tab.name }}
        </button>
      </div>

      <!-- Tab Content -->

      <!-- Info Tab -->
      <div v-if="activeTab === 'info'" class="card">
        <div v-if="league.description" class="prose prose-invert prose-sm max-w-none" v-html="renderedDescription"></div>
        <p v-else class="text-gray-500">{{ t('leagueDetail.noDescription') }}</p>
      </div>

      <!-- Standings Tab -->
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
                :title="t('leagueDetail.editGroupName')"
              >
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15.232 5.232l3.536 3.536m-2.036-5.036a2.5 2.5 0 113.536 3.536L6.5 21.036H3v-3.572L16.732 3.732z" />
                </svg>
              </button>
              <template v-if="editingGroupId === group.group_id">
                <button @click="saveGroupName(group.group_id)" class="text-green-400 hover:text-green-300" :title="t('leagueDetail.saveButton')">
                  <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
                  </svg>
                </button>
                <button @click="cancelEditGroupName" class="text-red-400 hover:text-red-300" :title="t('leagueDetail.cancel')">
                  <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              </template>
            </div>
            <span v-if="group.qualifying_spots" class="text-sm text-gray-400">
              {{ t('leagueDetail.topAdvance', { count: group.qualifying_spots }) }}
            </span>
          </div>
          <div class="overflow-x-auto">
            <table class="w-full text-sm">
              <thead>
                <tr class="text-gray-400 border-b border-gray-700">
                  <th class="text-left py-2 px-2">{{ t('leagueDetail.position') }}</th>
                  <th class="text-left py-2 px-2">{{ t('leagueDetail.player') }}</th>
                  <th class="text-center py-2 px-2">{{ t('leagueDetail.played') }}</th>
                  <th class="text-center py-2 px-2">{{ t('leagueDetail.won') }}</th>
                  <th class="text-center py-2 px-2">{{ t('leagueDetail.drawn') }}</th>
                  <th class="text-center py-2 px-2">{{ t('leagueDetail.lost') }}</th>
                  <th class="text-right py-2 px-2">{{ t('leagueDetail.points') }}</th>
                  <th class="text-right py-2 px-2">{{ t('leagueDetail.average') }}</th>
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
                          v-if="league.has_group_phase_lists || league.group_phase_ended"
                          @click="entry.army_list ? showListModal(entry) : null"
                          :class="getStandingsListIconClass(entry)"
                          :title="getStandingsListIconTitle(entry)"
                          :disabled="!entry.army_list"
                        >
                          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                          </svg>
                        </button>
                        <span v-if="entry.army_faction && (league.has_group_phase_lists || league.group_phase_ended)" class="text-xs text-gray-500">({{ entry.army_faction }})</span>
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
          <p class="text-gray-400">{{ t('leagueDetail.noMatchesYet') }}</p>
        </div>

        <!-- Knockout Matches (shown first when in knockout phase) -->
        <div v-if="knockoutMatches.length > 0 && league.status === 'knockout_phase'" class="border border-orange-700 rounded-lg overflow-hidden">
          <button
            @click="toggleGroup('knockout')"
            class="w-full flex items-center justify-between px-4 py-3 bg-orange-900/30 hover:bg-orange-900/40 transition-colors"
          >
            <h3 class="text-lg font-bold text-orange-400">{{ t('leagueDetail.knockoutPhase') }}</h3>
            <div class="flex items-center gap-3">
              <span class="text-sm text-orange-300">{{ t('leagueDetail.matchesCount', { count: knockoutMatches.length }) }}</span>
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
              :can-confirm="canConfirmMatchInList(match)"
              :current-player-id="currentUserPlayerId"
              :show-round="true"
              :require-army-lists="league.require_army_lists"
              @edit="openMatchModal"
              @confirm="confirmMatchDirect"
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
              <span class="text-sm text-gray-400">{{ t('leagueDetail.matchesCount', { count: group.myMatches.length + group.otherMatches.length }) }}</span>
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
              <p class="text-xs text-gray-500 uppercase tracking-wide">{{ t('leagueDetail.myMatches') }}</p>
              <MatchCard
                v-for="match in group.myMatches"
                :key="match.id"
                :match="match"
                :league-id="league.id"
                :can-edit="canEditMatch(match)"
                :can-confirm="canConfirmMatchInList(match)"
                :current-player-id="currentUserPlayerId"
                :require-army-lists="league.require_army_lists"
                @edit="openMatchModal"
                @confirm="confirmMatchDirect"
              />
            </div>

            <!-- Other matches in this group -->
            <div v-if="group.otherMatches.length > 0" class="space-y-2">
              <p v-if="group.myMatches.length > 0" class="text-xs text-gray-500 uppercase tracking-wide">{{ t('leagueDetail.otherMatches') }}</p>
              <MatchCard
                v-for="match in group.otherMatches"
                :key="match.id"
                :match="match"
                :league-id="league.id"
                :can-edit="canEditMatch(match)"
                :can-confirm="canConfirmMatchInList(match)"
                :current-player-id="currentUserPlayerId"
                :require-army-lists="league.require_army_lists"
                @edit="openMatchModal"
                @confirm="confirmMatchDirect"
              />
            </div>
          </div>
        </div>
      </div>

      <div v-if="activeTab === 'players'">
        <!-- Mobile: Cards -->
        <div class="md:hidden space-y-2">
          <div
            v-for="player in sortedPlayers"
            :key="player.id"
            :class="[
              'card p-3',
              player.wouldQualify ? 'border-l-4 border-l-green-500' : ''
            ]"
          >
            <!-- Row 1: Name + Points -->
            <div class="flex items-center justify-between mb-2">
              <div class="flex items-center gap-2 min-w-0 flex-1">
                <router-link
                  v-if="player.user_id"
                  :to="`/player/${player.user_id}`"
                  class="font-medium truncate hover:text-squig-yellow"
                >
                  {{ player.username || player.discord_username }}
                </router-link>
                <span v-else class="font-medium truncate">{{ player.username || player.discord_username }}</span>
                <span v-if="player.wouldQualify" class="text-xs text-green-400 flex-shrink-0">Q</span>
              </div>
              <div class="text-lg font-bold text-squig-yellow flex-shrink-0 ml-2">{{ player.total_points }}</div>
            </div>
            <!-- Row 2: Group, Games, Actions -->
            <div class="flex items-center justify-between text-sm text-gray-400">
              <div class="flex items-center gap-3">
                <span v-if="player.group_name">{{ player.group_name }}</span>
                <span>{{ player.games_played }} {{ t('leagueDetail.games').toLowerCase() }}</span>
                <span v-if="showKnockoutPlacement && player.knockout_placement" :class="placementClass(player.knockout_placement)">
                  {{ formatPlacement(player.knockout_placement) }}
                </span>
              </div>
              <div class="flex items-center gap-2">
                <!-- Army list icon -->
                <button
                  v-if="hasAnyListsEnabled && getPlayerArmyList(player)"
                  @click="showPlayerListModal(player)"
                  :class="getListIconClass(player, getCurrentListPhase)"
                >
                  <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                  </svg>
                </button>
                <!-- Organizer actions -->
                <template v-if="isOrganizer && league.status !== 'finished'">
                  <button
                    v-if="league.status === 'group_phase' && player.group_id"
                    @click="openChangeGroupModal(player)"
                    class="text-blue-400 p-1"
                  >
                    <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7h12m0 0l-4-4m4 4l-4 4m0 6H4m0 0l4 4m-4-4l4-4" />
                    </svg>
                  </button>
                  <button
                    @click="openRemovePlayerModal(player)"
                    class="text-red-400 p-1"
                  >
                    <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                    </svg>
                  </button>
                </template>
              </div>
            </div>
          </div>
          <p v-if="league?.qualifying_spots_per_group && league?.has_knockout_phase" class="text-xs text-gray-500 mt-3 px-1">
            <span class="text-green-400">Q</span> = {{ t('leagueDetail.wouldQualify', { count: league.qualifying_spots_per_group }) }}
          </p>
        </div>

        <!-- Desktop: Table -->
        <div class="hidden md:block card">
          <div class="overflow-x-auto">
            <table class="w-full text-sm">
              <thead>
                <tr class="text-gray-400 border-b border-gray-700">
                  <th class="text-left py-2 px-2">{{ t('leagueDetail.player') }}</th>
                  <th class="text-left py-2 px-2">{{ t('leagueDetail.group') }}</th>
                  <th class="text-center py-2 px-2">{{ t('leagueDetail.games') }}</th>
                  <th class="text-right py-2 px-2">{{ t('leagueDetail.points') }}</th>
                  <th v-if="showKnockoutPlacement" class="text-center py-2 px-2">{{ t('leagueDetail.knockout') }}</th>
                  <th v-if="isOrganizer && league.status !== 'finished'" class="text-center py-2 px-2">{{ t('leagueDetail.actionsColumn') }}</th>
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
                      <span v-if="player.wouldQualify" class="text-xs text-green-400" :title="t('leagueDetail.wouldAdvanceToKnockout')">Q</span>
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
                        :title="t('leagueDetail.changeGroupTitle')"
                      >
                        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7h12m0 0l-4-4m4 4l-4 4m0 6H4m0 0l4 4m-4-4l4-4" />
                        </svg>
                      </button>
                      <button
                        @click="openRemovePlayerModal(player)"
                        class="text-red-400 hover:text-red-300"
                        :title="t('leagueDetail.removePlayer')"
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
            <span class="text-green-400">Q</span> = {{ t('leagueDetail.wouldQualify', { count: league.qualifying_spots_per_group }) }}
          </p>
        </div>
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
            {{ league.current_knockout_round === 'final' ? t('leagueDetail.finishLeague') : t('leagueDetail.advanceToNextRound') }}
          </button>
          <span v-else-if="pendingKnockoutMatches > 0" class="text-sm text-gray-400">
            {{ t('leagueDetail.matchesPendingConfirmation', { count: pendingKnockoutMatches, round: knockoutRoundText(league.current_knockout_round) }, pendingKnockoutMatches) }}
          </span>
        </div>

        <!-- Preview notice when not in knockout yet -->
        <div v-if="league.status !== 'knockout_phase' && league.status !== 'finished'" class="mb-4 bg-blue-900/20 border border-blue-500 rounded p-3">
          <p class="text-blue-200 text-sm">
            <span class="font-bold">{{ t('leagueDetail.previewMode') }}</span> {{ t('leagueDetail.previewNotice') }}
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
          <p class="text-gray-400 mb-2">{{ t('leagueDetail.notEnoughQualified') }}</p>
          <p class="text-sm text-gray-500">
            {{ t('leagueDetail.playersNeedMatch') }}
          </p>
        </div>

        <!-- League finished -->
        <div v-if="league.status === 'finished' && knockoutMatches.length > 0" class="card text-center py-6 bg-green-900/20 border border-green-500">
          <h3 class="text-2xl font-bold text-green-400 mb-2">{{ t('leagueDetail.leagueComplete') }}</h3>
          <p class="text-gray-300">{{ t('leagueDetail.knockoutConcluded') }}</p>
        </div>
      </div>
    </div>

    <!-- Confirm Modals -->
    <ConfirmModal
      :show="showDrawGroupsModal"
      :title="t('leagueDetail.drawGroups')"
      :message="t('leagueDetail.drawGroupsConfirm')"
      :confirmText="t('leagueDetail.drawGroups')"
      :danger="true"
      @confirm="drawGroups"
      @cancel="showDrawGroupsModal = false"
    />

    <ConfirmModal
      :show="showStartKnockoutModal"
      :title="t('leagueDetail.startKnockout')"
      :message="t('leagueDetail.startKnockoutConfirm')"
      :confirmText="t('leagueDetail.startKnockout')"
      :danger="true"
      @confirm="startKnockout"
      @cancel="showStartKnockoutModal = false"
    />

    <ConfirmModal
      :show="showRevealListsModal"
      :title="t('leagueDetail.revealLists')"
      :message="t('leagueDetail.revealListsConfirm')"
      :confirmText="t('leagueDetail.revealLists')"
      @confirm="revealLists"
      @cancel="showRevealListsModal = false"
    />

    <ConfirmModal
      :show="showEndGroupPhaseModal"
      :title="t('leagueDetail.endGroupPhase')"
      :message="t('leagueDetail.endGroupPhaseConfirm')"
      :confirmText="t('leagueDetail.endGroupPhase')"
      :danger="true"
      @confirm="endGroupPhase"
      @cancel="showEndGroupPhaseModal = false"
    />

    <ConfirmModal
      :show="showFinishLeagueModal"
      :title="t('leagueDetail.finishLeague')"
      :message="t('leagueDetail.finishLeagueConfirm')"
      :confirmText="t('leagueDetail.finishLeague')"
      :danger="true"
      @confirm="finishLeague"
      @cancel="showFinishLeagueModal = false"
    />

    <ConfirmModal
      :show="showAdvanceKnockoutModal"
      :title="t('leagueDetail.advanceToNextRound')"
      :message="league?.current_knockout_round === 'final' ? t('leagueDetail.advanceKnockoutFinal') : t('leagueDetail.advanceKnockoutConfirm')"
      :confirmText="league?.current_knockout_round === 'final' ? t('leagueDetail.finishLeague') : t('leagueDetail.advance')"
      @confirm="advanceKnockout"
      @cancel="showAdvanceKnockoutModal = false"
    />

    <ConfirmModal
      :show="showLeaveLeagueModal"
      :title="t('leagueDetail.leaveLeague')"
      :message="leaveLeagueMessage"
      :confirmText="t('leagueDetail.leaveLeague')"
      :danger="true"
      @confirm="leaveLeague"
      @cancel="showLeaveLeagueModal = false"
    />

    <ConfirmModal
      :show="showRemovePlayerModal"
      :title="t('leagueDetail.removePlayerTitle')"
      :message="removePlayerMessage"
      :confirmText="t('leagueDetail.removePlayer')"
      :danger="true"
      @confirm="removePlayer"
      @cancel="showRemovePlayerModal = false"
    />

    <!-- Login Prompt Modal -->
    <div v-if="showLoginPromptModal" class="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
      <div class="bg-gray-800 rounded-lg p-6 max-w-md w-full mx-4">
        <h3 class="text-xl font-bold mb-4">{{ t('leagueDetail.loginRequired') }}</h3>
        <p class="text-gray-300 mb-6">
          {{ t('leagueDetail.loginRequiredMessage') }}
        </p>
        <div class="flex gap-3">
          <button @click="showLoginPromptModal = false" class="flex-1 btn-secondary">
            {{ t('leagueDetail.cancel') }}
          </button>
          <router-link :to="`/login?redirect=${encodeURIComponent($route.fullPath)}`" class="flex-1 btn-primary text-center">
            {{ t('auth.login') }}
          </router-link>
          <router-link :to="`/register?redirect=${encodeURIComponent($route.fullPath)}`" class="flex-1 btn-secondary text-center">
            {{ t('auth.register') }}
          </router-link>
        </div>
      </div>
    </div>

    <!-- Change Group Modal -->
    <div v-if="showChangeGroupModal && selectedPlayerForAction" class="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
      <div class="bg-gray-800 rounded-lg p-6 max-w-md w-full mx-4">
        <h3 class="text-xl font-bold mb-4">{{ t('leagueDetail.changeGroup') }}</h3>
        <p class="text-gray-400 mb-4">
          {{ t('leagueDetail.moveTo', { name: selectedPlayerForAction.username || selectedPlayerForAction.discord_username }) }}
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
          <button @click="showChangeGroupModal = false" class="flex-1 btn-secondary">{{ t('leagueDetail.cancel') }}</button>
          <button @click="changePlayerGroup" :disabled="actionLoading" class="flex-1 btn-primary">
            {{ actionLoading ? t('leagueDetail.moving') : t('leagueDetail.movePlayer') }}
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
            {{ t('leagueDetail.matchResultConfirmed') }}
          </div>
          <div class="mt-4 text-center">
            <p class="text-2xl font-bold text-squig-yellow">
              {{ selectedMatch.player1_score }} - {{ selectedMatch.player2_score }}
            </p>
            <p class="text-sm text-gray-400 mt-2">
              {{ t('leagueDetail.leaguePoints') }} {{ selectedMatch.player1_league_points }} - {{ selectedMatch.player2_league_points }}
            </p>
          </div>
          <button
            v-if="canConfirmMatch"
            @click="unlockMatch"
            :disabled="submittingScore"
            class="mt-4 w-full btn-secondary border-yellow-500 text-yellow-400 hover:bg-yellow-900/30"
          >
            {{ submittingScore ? t('leagueDetail.unlocking') : t('leagueDetail.unlockForEditing') }}
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
              <p v-if="calculatedPoints.player1 !== null" class="text-sm text-squig-yellow font-semibold mt-1 text-center">
                → {{ calculatedPoints.player1 }} pkt
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
              <p v-if="calculatedPoints.player2 !== null" class="text-sm text-squig-yellow font-semibold mt-1 text-center">
                → {{ calculatedPoints.player2 }} pkt
              </p>
            </div>
          </div>

          <div class="mb-4">
            <label class="block text-sm text-gray-400 mb-1">{{ t('leagueDetail.mapOptional') }}</label>
            <select
              v-model="scoreForm.map_name"
              class="w-full bg-gray-700 border border-gray-600 rounded px-4 py-2 focus:outline-none focus:border-squig-yellow"
            >
              <option value="">{{ t('leagueDetail.selectMap') }}</option>
              <option v-for="map in missionMaps" :key="map" :value="map">{{ map }}</option>
              <option value="__custom__">{{ t('leagueDetail.custom') }}</option>
            </select>
            <input
              v-if="scoreForm.map_name === '__custom__'"
              v-model="scoreForm.custom_map"
              type="text"
              :placeholder="t('leagueDetail.enterCustomMapName')"
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
              {{ submittingScore ? t('leagueDetail.saving') : t('leagueDetail.saveScore') }}
            </button>
            <button
              v-if="canConfirmThisMatch && selectedMatch.player1_score !== null"
              @click="confirmScore"
              :disabled="submittingScore"
              class="flex-1 btn-primary bg-green-600 hover:bg-green-700"
            >
              {{ submittingScore ? t('leagueDetail.confirming') : t('leagueDetail.confirmAndLock') }}
            </button>
          </div>
        </div>

        <div v-else class="text-center text-gray-400">
          <p>{{ t('leagueDetail.noPermissionToEdit') }}</p>
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
          {{ t('leagueDetail.close') }}
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
              :title="t('leagueDetail.editList')"
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
            {{ t('leagueDetail.close') }}
          </button>
        </template>

        <!-- Edit Mode (Organizer) -->
        <template v-else>
          <div class="space-y-4 flex-1 overflow-y-auto">
            <div>
              <label class="block text-sm text-gray-400 mb-1">{{ t('leagueDetail.armyFaction') }}</label>
              <select v-model="editListFaction" class="w-full bg-gray-700 border border-gray-600 rounded px-3 py-2">
                <option value="">{{ t('leagueDetail.selectFaction') }}</option>
                <option v-for="faction in armyFactions" :key="faction" :value="faction">{{ faction }}</option>
              </select>
            </div>
            <div class="flex-1">
              <label class="block text-sm text-gray-400 mb-1">{{ t('matchups.armyList') }}</label>
              <textarea
                v-model="editListContent"
                rows="12"
                class="w-full bg-gray-700 border border-gray-600 rounded px-3 py-2 font-mono text-sm"
                :placeholder="t('leagueDetail.pasteArmyListHere')"
              ></textarea>
            </div>
            <div v-if="editListError" class="bg-red-900/30 border border-red-500 text-red-200 px-4 py-2 rounded text-sm">
              {{ editListError }}
            </div>
          </div>
          <div class="flex gap-3 mt-4">
            <button @click="cancelEditingList" class="flex-1 btn-secondary">{{ t('leagueDetail.cancel') }}</button>
            <button
              @click="saveEditedList"
              :disabled="savingList || !editListFaction || !editListContent.trim()"
              class="flex-1 btn-primary"
            >
              {{ savingList ? t('leagueDetail.saving') : t('leagueDetail.saveChanges') }}
            </button>
          </div>
        </template>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { useAuthStore } from '../stores/auth'
import axios from 'axios'
import ConfirmModal from '../components/ConfirmModal.vue'
import MatchCard from '../components/MatchCard.vue'
import KnockoutBracket from '../components/KnockoutBracket.vue'
import { ARMY_FACTIONS } from '../constants/armies'
import { marked } from 'marked'

// Configure marked to respect line breaks
marked.setOptions({
  breaks: true,
  gfm: true
})
import { fetchMapsData } from '../constants/maps'

const armyFactions = ARMY_FACTIONS
const { t } = useI18n()

// Maps data from API
const mapsData = ref(null)
const missionMaps = computed(() => mapsData.value?.maps || [])

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
const activeTab = ref(route.params.tab || 'info')
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

// Login prompt modal (for unauthenticated users trying to join)
const showLoginPromptModal = ref(false)

// Player management modals
const showRemovePlayerModal = ref(false)
const showChangeGroupModal = ref(false)
const selectedPlayerForAction = ref(null)
const newGroupId = ref(null)
const changeGroupError = ref('')

// Actions menu state
const showActionsMenu = ref(false)
const showTabsMenu = ref(false)
const showInfoCards = ref(false)

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
    { id: 'info', name: t('leagueDetail.info') },
    { id: 'standings', name: t('leagueDetail.standings') },
    { id: 'matches', name: t('leagueDetail.matches') },
    { id: 'players', name: t('leagueDetail.players') },
  ]
  // Add Knockout tab if league has knockout phase
  if (league.value?.has_knockout_phase) {
    baseTabs.push({ id: 'knockout', name: t('leagueDetail.knockout') })
  }
  return baseTabs
})

const isOrganizer = computed(() => {
  if (!authStore.user || !league.value) return false
  return league.value.organizer_id === authStore.user.id || authStore.user.role === 'admin'
})

const renderedDescription = computed(() => {
  if (!league.value?.description) return ''
  return marked(league.value.description)
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
    return t('leagueDetail.leaveLeagueRegistration')
  }
  return t('leagueDetail.leaveLeagueActive')
})

// Message for remove player modal
const removePlayerMessage = computed(() => {
  if (!selectedPlayerForAction.value || !league.value) return ''
  const name = selectedPlayerForAction.value.username || selectedPlayerForAction.value.discord_username
  if (league.value.status === 'registration') {
    return t('leagueDetail.removePlayerRegistration', { name })
  }
  return t('leagueDetail.removePlayerActive', { name })
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
    if (league.value.knockout_size) {
      return t('leagueDetail.groupsKnockoutTop', { count: league.value.knockout_size })
    }
    return t('leagueDetail.groupsKnockout')
  }
  return t('leagueDetail.groupsOnly')
})

// Phase end label and date based on current status
const phaseEndLabel = computed(() => {
  if (!league.value) return t('leagueDetail.ends')
  if (league.value.status === 'registration') return t('leagueDetail.registrationEnds')
  if (league.value.status === 'group_phase') return t('leagueDetail.groupPhaseEnds')
  if (league.value.status === 'knockout_phase') return t('leagueDetail.roundDeadline')
  if (league.value.status === 'finished') return t('leagues.finished')
  return t('leagueDetail.ends')
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

// Qualified players list (for knockout tab bracket preview)
// Shows current top players in qualifying positions - actual qualification check happens when starting knockout
const qualifiedPlayers = computed(() => {
  const spots = league.value?.qualifying_spots_per_group || 0
  if (!spots || !league.value?.has_knockout_phase) return []

  // Get qualifying players from each group (based on standings which already use min games rule)
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
    if (b.games_played !== a.games_played) return b.games_played - a.games_played
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
    const groupSize = groupPlayers.length
    const maxGames = groupSize - 1
    const minRequiredGames = Math.max(1, maxGames - 1)

    // Sort: players with min required games first, then by points, games played, avg points
    groupPlayers.sort((a, b) => {
      const aMeetsMin = a.games_played >= minRequiredGames
      const bMeetsMin = b.games_played >= minRequiredGames
      // Players who meet minimum ranked above those who don't
      if (aMeetsMin !== bMeetsMin) return bMeetsMin - aMeetsMin
      // Then by total points
      if (b.total_points !== a.total_points) return b.total_points - a.total_points
      // Then by games played (more = better)
      if (b.games_played !== a.games_played) return b.games_played - a.games_played
      // Then by average points
      return b.average_points - a.average_points
    })
    // Mark top N as qualifying (must have at least 1 game played)
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
  // Both scores must be valid numbers (including 0)
  const p1Valid = typeof p1 === 'number' && !Number.isNaN(p1)
  const p2Valid = typeof p2 === 'number' && !Number.isNaN(p2)
  if (!p1Valid || !p2Valid) {
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

// Check if current user can confirm this match in the list (opponent or organizer, match is pending)
const canConfirmMatchInList = (match) => {
  if (!authStore.user || !league.value) return false
  if (match.status !== 'pending_confirmation') return false

  const isOrgOrAdmin = league.value.organizer_id === authStore.user.id || authStore.user.role === 'admin'
  if (isOrgOrAdmin) return true

  // Check if user is the opponent (not the one who submitted)
  const currentUserId = authStore.user.id

  // Check if current user is player1 or player2 (using user_id, not league_player_id)
  const isPlayer1 = match.player1_user_id === currentUserId
  const isPlayer2 = match.player2_user_id === currentUserId

  if (!isPlayer1 && !isPlayer2) return false

  // Can confirm if they are the opponent of whoever submitted
  // submitted_by_id is the USER ID of whoever submitted
  if (match.submitted_by_id) {
    // If player1 submitted, only player2 can confirm (and vice versa)
    return (isPlayer1 && match.submitted_by_id === match.player2_user_id) ||
           (isPlayer2 && match.submitted_by_id === match.player1_user_id)
  }

  return false
}

// Confirm match directly without opening modal
const confirmMatchDirect = async (match) => {
  try {
    await axios.post(`${API_URL}/league/${league.value.id}/matches/${match.id}/confirm`)
    await fetchLeague()
  } catch (err) {
    showActionError(err.response?.data?.detail || 'Failed to confirm match')
  }
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
  // Check if user is authenticated first
  if (!authStore.isAuthenticated) {
    showLoginPromptModal.value = true
    return
  }

  joining.value = true
  actionError.value = ''
  try {
    await axios.post(`${API_URL}/league/${league.value.id}/join`)
    await fetchLeague()
  } catch (err) {
    // Handle 401 error with login prompt
    if (err.response?.status === 401) {
      showLoginPromptModal.value = true
    } else {
      showActionError(err.response?.data?.detail || 'Failed to join')
    }
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

// Check if lists are relevant for current phase
const hasAnyListsEnabled = computed(() => {
  if (!league.value) return false
  // During registration/group phase, only show if group lists are enabled
  if (league.value.status === 'registration' || league.value.status === 'group_phase') {
    // Show knockout list icon only after group phase ended
    if (!league.value.has_group_phase_lists && league.value.has_knockout_phase_lists) {
      return league.value.group_phase_ended
    }
    return league.value.has_group_phase_lists
  }
  // During knockout/finished, show if knockout lists are enabled (or group if no knockout)
  return league.value.has_knockout_phase_lists || league.value.has_group_phase_lists
})

// Get current list phase based on league status
const getCurrentListPhase = computed(() => {
  if (!league.value) return 'group'
  // After group phase ended, switch to knockout lists
  if (league.value.status === 'knockout_phase' || league.value.status === 'finished' || league.value.group_phase_ended) {
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
    case 'registration': return t('leagueDetail.statusRegistration')
    case 'group_phase': return t('leagueDetail.statusGroupPhase')
    case 'knockout_phase': return t('leagueDetail.statusKnockout')
    case 'finished': return t('leagueDetail.statusFinished')
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

// Tab navigation via URL
const changeTab = (tabId) => {
  router.push({ name: 'LeagueDetail', params: { id: route.params.id, tab: tabId } })
}

watch(() => route.params.tab, (newTab) => {
  if (newTab) {
    activeTab.value = newTab
  } else {
    // Default to standings if user is joined, otherwise info
    activeTab.value = isJoined.value ? 'standings' : 'info'
  }
})

// When players load and no tab specified, switch to standings if joined
watch(isJoined, (joined) => {
  if (joined && !route.params.tab) {
    activeTab.value = 'standings'
  }
})

onMounted(async () => {
  mapsData.value = await fetchMapsData()
  fetchLeague()
})
</script>

<style scoped>
.tabs-menu-enter-active,
.tabs-menu-leave-active {
  transition: opacity 0.15s ease;
}

.tabs-menu-enter-from,
.tabs-menu-leave-to {
  opacity: 0;
}

.tabs-menu-enter-to,
.tabs-menu-leave-from {
  opacity: 1;
}
</style>
