<template>
  <div class="max-w-6xl mx-auto">
    <!-- Tabs: Menu overlay on mobile, buttons on desktop -->
    <!-- Mobile tabs menu -->
    <div class="md:hidden mb-4">
      <button
        @click="showTabsMenu = !showTabsMenu"
        class="w-full flex items-center justify-between bg-gray-700 border border-gray-600 rounded-lg px-4 py-3 text-white"
      >
        <span class="font-medium">{{ t(tabs.find(t => t.id === activeTab)?.label) }}</span>
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
                @click="activeTab = tab.id; showTabsMenu = false"
                class="w-full flex items-center justify-between px-4 py-3 rounded-lg transition-colors"
                :class="activeTab === tab.id ? 'bg-squig-yellow/20 text-squig-yellow' : 'hover:bg-gray-700 text-white'"
              >
                <span class="font-medium">{{ t(tab.label) }}</span>
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
    <div class="hidden md:flex border-b border-gray-700 mb-6">
      <button
        v-for="tab in tabs"
        :key="tab.id"
        @click="activeTab = tab.id"
        :class="[
          'px-6 py-3 text-sm font-medium border-b-2 -mb-px transition-colors',
          activeTab === tab.id
            ? 'border-squig-yellow text-squig-yellow'
            : 'border-transparent text-gray-400 hover:text-gray-200'
        ]"
      >
        {{ t(tab.label) }}
      </button>
    </div>

    <div v-if="loading" class="flex justify-center py-12">
      <div class="w-10 h-10 border-4 border-squig-yellow border-t-transparent rounded-full animate-spin"></div>
    </div>

    <div v-else-if="error" class="card">
      <div class="bg-red-900/30 border border-red-500 text-red-200 px-4 py-3 rounded">
        {{ error }}
      </div>
    </div>

    <div v-else>
      <!-- Users Tab -->
      <div v-show="activeTab === 'users'">
        <!-- Stats - compact on mobile -->
        <div class="grid grid-cols-2 md:grid-cols-4 gap-2 md:gap-4 mb-6 md:mb-8">
          <div class="card p-3 md:p-6">
            <h3 class="text-xs md:text-sm text-gray-400 mb-1">{{ t('admin.totalUsers') }}</h3>
            <p class="text-xl md:text-2xl font-bold">{{ stats.total_users }}</p>
          </div>
          <div class="card p-3 md:p-6">
            <h3 class="text-xs md:text-sm text-gray-400 mb-1">{{ t('admin.players') }}</h3>
            <p class="text-xl md:text-2xl font-bold text-blue-400">{{ stats.players }}</p>
          </div>
          <div class="card p-3 md:p-6">
            <h3 class="text-xs md:text-sm text-gray-400 mb-1">{{ t('admin.organizers') }}</h3>
            <p class="text-xl md:text-2xl font-bold text-yellow-400">{{ stats.organizers }}</p>
          </div>
          <div class="card p-3 md:p-6">
            <h3 class="text-xs md:text-sm text-gray-400 mb-1">{{ t('admin.admins') }}</h3>
            <p class="text-xl md:text-2xl font-bold text-red-400">{{ stats.admins }}</p>
          </div>
        </div>

        <!-- Role Error -->
        <div v-if="roleError" class="mb-4 bg-red-900/30 border border-red-500 text-red-200 px-4 py-3 rounded text-sm">
          {{ roleError }}
        </div>

        <!-- Users - Cards on mobile, Table on desktop -->
        <!-- Mobile cards -->
        <div class="md:hidden space-y-3">
          <div
            v-for="user in users"
            :key="user.id"
            class="card p-4"
          >
            <div class="flex items-start justify-between mb-3">
              <div class="min-w-0 flex-1">
                <p class="font-bold truncate">{{ user.username || user.email }}</p>
                <p class="text-xs text-gray-400 truncate">{{ user.email }}</p>
              </div>
              <span
                :class="user.is_active ? 'bg-green-900/30 text-green-400' : 'bg-red-900/30 text-red-400'"
                class="text-xs px-2 py-1 rounded flex-shrink-0"
              >
                {{ user.is_active ? t('admin.active') : t('admin.inactive') }}
              </span>
            </div>
            <div class="flex items-center justify-between gap-2">
              <button
                @click="openRoleMenu(user)"
                :disabled="user.updating"
                class="flex-1 flex items-center justify-between bg-gray-700 border border-gray-600 rounded px-3 py-2 text-sm"
                :class="getRoleClass(user.role)"
              >
                <span>{{ getRoleLabel(user.role) }}</span>
                <svg class="w-4 h-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
                </svg>
              </button>
              <span v-if="user.updating" class="text-yellow-400 text-sm">{{ t('admin.saving') }}</span>
              <span v-else-if="user.saved" class="text-green-400 text-sm">✓</span>
              <button
                v-else
                @click="confirmDeleteUser(user)"
                class="p-2 text-red-400 hover:bg-red-900/30 rounded"
                :disabled="user.deleting"
              >
                <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                </svg>
              </button>
            </div>
            <div class="mt-2 text-xs text-gray-500">
              {{ t('admin.created') }}: {{ formatDate(user.created_at) }}
            </div>
          </div>
        </div>

        <!-- Role selection overlay menu -->
        <Transition name="tabs-menu">
          <div v-if="roleMenuUser" class="fixed inset-0 z-50">
            <div class="fixed inset-0 bg-black/50" @click="roleMenuUser = null"></div>
            <div class="fixed inset-x-4 top-1/3 bg-gray-800 border border-gray-700 rounded-xl shadow-xl overflow-hidden">
              <div class="px-4 py-3 border-b border-gray-700">
                <p class="text-sm text-gray-400">{{ t('admin.role') }}</p>
                <p class="font-medium">{{ roleMenuUser.username || roleMenuUser.email }}</p>
              </div>
              <div class="p-2 space-y-1">
                <button
                  v-for="role in roles"
                  :key="role.id"
                  @click="selectRole(role.id)"
                  class="w-full flex items-center justify-between px-4 py-3 rounded-lg transition-colors"
                  :class="roleMenuUser.role === role.id ? 'bg-squig-yellow/20 text-squig-yellow' : 'hover:bg-gray-700 text-white'"
                >
                  <span class="font-medium">{{ t(role.label) }}</span>
                  <svg
                    v-if="roleMenuUser.role === role.id"
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

        <!-- Desktop table -->
        <div class="hidden md:block card">
          <div class="overflow-x-auto">
            <table class="w-full text-sm">
              <thead>
                <tr class="text-gray-400 border-b border-gray-700">
                  <th class="text-left py-3 px-4">{{ t('admin.id') }}</th>
                  <th class="text-left py-3 px-4">{{ t('admin.email') }}</th>
                  <th class="text-left py-3 px-4">{{ t('admin.username') }}</th>
                  <th class="text-center py-3 px-4">{{ t('admin.role') }}</th>
                  <th class="text-center py-3 px-4">{{ t('admin.status') }}</th>
                  <th class="text-right py-3 px-4">{{ t('admin.created') }}</th>
                  <th class="text-right py-3 px-4">{{ t('admin.lastLogin') }}</th>
                  <th class="text-center py-3 px-4">{{ t('admin.actions') }}</th>
                </tr>
              </thead>
              <tbody>
                <tr
                  v-for="user in users"
                  :key="user.id"
                  class="border-b border-gray-800 hover:bg-gray-700/50"
                >
                  <td class="py-3 px-4 text-gray-400">{{ user.id }}</td>
                  <td class="py-3 px-4">{{ user.email }}</td>
                  <td class="py-3 px-4">{{ user.username || '-' }}</td>
                  <td class="py-3 px-4 text-center">
                    <select
                      v-model="user.role"
                      @change="updateRole(user)"
                      :disabled="user.updating"
                      class="bg-gray-700 border border-gray-600 rounded px-2 py-1 text-sm focus:outline-none focus:border-squig-yellow"
                    >
                      <option value="player">{{ t('admin.rolePlayer') }}</option>
                      <option value="organizer">{{ t('admin.roleOrganizer') }}</option>
                      <option value="admin">{{ t('admin.roleAdmin') }}</option>
                    </select>
                  </td>
                  <td class="py-3 px-4 text-center">
                    <span v-if="user.is_active" class="text-green-400">{{ t('admin.active') }}</span>
                    <span v-else class="text-red-400">{{ t('admin.inactive') }}</span>
                  </td>
                  <td class="py-3 px-4 text-right text-gray-400">{{ formatDate(user.created_at) }}</td>
                  <td class="py-3 px-4 text-right text-gray-400">{{ user.last_login ? formatDate(user.last_login) : '-' }}</td>
                  <td class="py-3 px-4 text-center">
                    <span v-if="user.updating" class="text-yellow-400">{{ t('admin.saving') }}</span>
                    <span v-else-if="user.saved" class="text-green-400">{{ t('admin.saved') }}</span>
                    <button
                      v-else
                      @click="confirmDeleteUser(user)"
                      class="text-red-400 hover:text-red-300 text-sm"
                      :disabled="user.deleting"
                    >
                      {{ user.deleting ? t('admin.deleting') : t('admin.delete') }}
                    </button>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>

      <!-- Settings Tab -->
      <div v-show="activeTab === 'settings'" class="max-w-2xl">
        <div class="card">
          <h2 class="text-xl font-bold mb-4">{{ t('admin.eloSettings') }}</h2>

          <form @submit.prevent="saveEloSettings" class="space-y-4">
            <div>
              <label class="block text-sm font-medium text-gray-300 mb-2">
                {{ t('admin.globalKFactor') }}
              </label>
              <input
                v-model.number="eloSettings.k_factor"
                type="number"
                min="1"
                max="100"
                class="w-full bg-gray-700 border border-gray-600 rounded px-4 py-2 focus:outline-none focus:border-squig-yellow"
              />
              <p class="text-sm text-gray-500 mt-1">
                {{ t('admin.globalKFactorNote') }}
              </p>
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-300 mb-2">
                {{ t('admin.newPlayerKFactor') }}
              </label>
              <input
                v-model.number="eloSettings.new_player_k"
                type="number"
                min="1"
                max="100"
                class="w-full bg-gray-700 border border-gray-600 rounded px-4 py-2 focus:outline-none focus:border-squig-yellow"
              />
              <p class="text-sm text-gray-500 mt-1">
                {{ t('admin.newPlayerKFactorNote') }}
              </p>
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-300 mb-2">
                {{ t('admin.newPlayerGamesThreshold') }}
              </label>
              <input
                v-model.number="eloSettings.new_player_games"
                type="number"
                min="1"
                max="50"
                class="w-full bg-gray-700 border border-gray-600 rounded px-4 py-2 focus:outline-none focus:border-squig-yellow"
              />
              <p class="text-sm text-gray-500 mt-1">
                {{ t('admin.newPlayerGamesThresholdNote') }}
              </p>
            </div>

            <div v-if="saveError" class="bg-red-900/30 border border-red-500 text-red-200 px-4 py-3 rounded">
              {{ saveError }}
            </div>

            <div v-if="saveSuccess" class="bg-green-900/30 border border-green-500 text-green-200 px-4 py-3 rounded">
              {{ t('admin.settingsSaved') }}
            </div>

            <button
              type="submit"
              :disabled="saving"
              class="w-full btn-primary py-3"
            >
              {{ saving ? t('common.saving') : t('admin.saveSettings') }}
            </button>
          </form>
        </div>
      </div>

      <!-- Matchups Tab -->
      <div v-show="activeTab === 'matchups'">
        <!-- Filter -->
        <div class="card mb-4 md:mb-6 p-3 md:p-6">
          <div class="flex flex-col sm:flex-row gap-2 sm:gap-4 sm:items-center">
            <label class="text-sm text-gray-400">{{ t('admin.filter') }}:</label>
            <select
              v-model="matchupFilter"
              @change="fetchMatchups"
              class="bg-gray-700 border border-gray-600 rounded px-3 py-2 text-sm focus:outline-none focus:border-squig-yellow"
              style="font-size: 16px;"
            >
              <option value="all">{{ t('admin.allMatchups') }}</option>
              <option value="pending">{{ t('admin.pendingMatchups') }}</option>
              <option value="revealed">{{ t('admin.revealedMatchups') }}</option>
            </select>
          </div>
        </div>

        <div v-if="matchupsLoading" class="text-center py-8">
          <p class="text-gray-400">{{ t('common.loading') }}</p>
        </div>
        <div v-else-if="matchups.length === 0" class="card text-center py-8">
          <p class="text-gray-400">{{ t('admin.noMatchups') }}</p>
        </div>
        <template v-else>
          <!-- Mobile cards -->
          <div class="md:hidden space-y-3">
            <router-link
              v-for="matchup in matchups"
              :key="matchup.id"
              :to="`/matchup/${matchup.name}`"
              class="card p-4 block hover:bg-gray-700 transition-colors"
            >
              <div class="flex items-start justify-between mb-2">
                <div>
                  <p class="font-bold text-squig-yellow">{{ matchup.name }}</p>
                  <p v-if="matchup.title" class="text-xs text-gray-500">{{ matchup.title }}</p>
                </div>
                <span
                  :class="matchup.is_revealed ? 'bg-green-900/30 text-green-400' : 'bg-yellow-900/30 text-yellow-400'"
                  class="text-xs px-2 py-1 rounded"
                >
                  {{ matchup.is_revealed ? t('admin.revealed') : t('admin.pending') }}
                </span>
              </div>
              <!-- Players -->
              <div class="space-y-1 text-sm mb-2">
                <div class="flex items-center gap-2">
                  <span :class="matchup.player1_submitted ? 'text-green-400' : 'text-yellow-400'">
                    {{ matchup.player1_submitted ? '✓' : '⏳' }}
                  </span>
                  <span class="truncate">{{ matchup.player1_username || t('admin.anonymous') }}</span>
                </div>
                <div class="flex items-center gap-2">
                  <span :class="matchup.player2_submitted ? 'text-green-400' : 'text-yellow-400'">
                    {{ matchup.player2_submitted ? '✓' : '⏳' }}
                  </span>
                  <span class="truncate">{{ matchup.player2_username || t('admin.anonymous') }}</span>
                </div>
              </div>
              <!-- Result -->
              <div class="flex items-center justify-between text-sm">
                <span v-if="matchup.result_status === 'confirmed'" class="text-green-400 font-bold">
                  {{ matchup.player1_score }} - {{ matchup.player2_score }}
                </span>
                <span v-else-if="matchup.result_status === 'pending_confirmation'" class="text-yellow-400">
                  {{ matchup.player1_score }} - {{ matchup.player2_score }} (pending)
                </span>
                <span v-else class="text-gray-500">No result</span>
                <span class="text-xs text-gray-500">{{ formatDate(matchup.created_at) }}</span>
              </div>
            </router-link>
          </div>

          <!-- Desktop table -->
          <div class="hidden md:block card">
            <div class="overflow-x-auto">
              <table class="w-full text-sm">
                <thead>
                  <tr class="text-gray-400 border-b border-gray-700">
                    <th class="text-left py-3 px-4">{{ t('admin.matchupId') }}</th>
                    <th class="text-left py-3 px-4">{{ t('admin.player1') }}</th>
                    <th class="text-left py-3 px-4">{{ t('admin.player2') }}</th>
                    <th class="text-center py-3 px-4">{{ t('admin.status') }}</th>
                    <th class="text-center py-3 px-4">{{ t('admin.result') }}</th>
                    <th class="text-right py-3 px-4">{{ t('admin.created') }}</th>
                  </tr>
                </thead>
                <tbody>
                  <tr
                    v-for="matchup in matchups"
                    :key="matchup.id"
                    class="border-b border-gray-800 hover:bg-gray-700/50"
                  >
                    <td class="py-3 px-4">
                      <router-link
                        :to="`/matchup/${matchup.name}`"
                        class="text-squig-yellow hover:underline"
                      >
                        {{ matchup.name }}
                      </router-link>
                      <div v-if="matchup.title" class="text-xs text-gray-500">{{ matchup.title }}</div>
                    </td>
                    <td class="py-3 px-4">
                      <div class="flex items-center gap-2">
                        <span :class="matchup.player1_submitted ? 'text-green-400' : 'text-yellow-400'">
                          {{ matchup.player1_submitted ? '✓' : '⏳' }}
                        </span>
                        {{ matchup.player1_username || t('admin.anonymous') }}
                        <span v-if="matchup.is_revealed && matchup.player1_army_faction" class="text-xs text-gray-500">
                          ({{ matchup.player1_army_faction }})
                        </span>
                      </div>
                    </td>
                    <td class="py-3 px-4">
                      <div class="flex items-center gap-2">
                        <span :class="matchup.player2_submitted ? 'text-green-400' : 'text-yellow-400'">
                          {{ matchup.player2_submitted ? '✓' : '⏳' }}
                        </span>
                        {{ matchup.player2_username || t('admin.anonymous') }}
                        <span v-if="matchup.is_revealed && matchup.player2_army_faction" class="text-xs text-gray-500">
                          ({{ matchup.player2_army_faction }})
                        </span>
                      </div>
                    </td>
                    <td class="py-3 px-4 text-center">
                      <span v-if="matchup.is_revealed" class="text-green-400">{{ t('admin.revealed') }}</span>
                      <span v-else class="text-yellow-400">{{ t('admin.pending') }}</span>
                      <span v-if="!matchup.is_public" class="ml-2 text-xs text-gray-500">({{ t('admin.private') }})</span>
                    </td>
                    <td class="py-3 px-4 text-center">
                      <span v-if="matchup.result_status === 'confirmed'" class="text-green-400">
                        {{ matchup.player1_score }} - {{ matchup.player2_score }}
                      </span>
                      <span v-else-if="matchup.result_status === 'pending_confirmation'" class="text-yellow-400">
                        {{ matchup.player1_score }} - {{ matchup.player2_score }} ({{ t('admin.awaitingConfirm') }})
                      </span>
                      <span v-else class="text-gray-500">-</span>
                    </td>
                    <td class="py-3 px-4 text-right text-gray-400">{{ formatDate(matchup.created_at) }}</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </template>
      </div>

      <!-- Data Tab (BSData) -->
      <div v-show="activeTab === 'data'">
        <!-- Feature Toggles -->
        <div class="card mb-6">
          <h3 class="text-lg font-bold mb-3">Feature Toggles</h3>
          <label class="flex items-center gap-3 cursor-pointer">
            <input
              type="checkbox"
              :checked="rulesNavVisible"
              @change="toggleRulesNav"
              class="w-4 h-4 accent-squig-yellow"
            />
            <span class="text-sm">Show Rules button in navigation</span>
          </label>
        </div>

        <div v-if="bsDataLoading" class="text-center py-8">
          <p class="text-gray-400">{{ t('common.loading') }}</p>
        </div>
        <template v-else>
          <!-- Sync Status Card -->
          <div class="card mb-6">
            <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
              <div>
                <h3 class="text-lg font-bold mb-2">BSData Status</h3>
                <div v-if="bsDataStatus" class="text-sm space-y-1">
                  <p><span class="text-gray-400">Commit:</span> <code class="text-squig-yellow">{{ bsDataStatus.commit_short }}</code></p>
                  <p><span class="text-gray-400">Last sync:</span> {{ formatDate(bsDataStatus.last_sync) }}</p>
                  <p><span class="text-gray-400">Factions:</span> {{ bsDataStatus.factions_count }} | <span class="text-gray-400">Units:</span> {{ bsDataStatus.units_count }}</p>
                </div>
                <p v-else class="text-gray-500 text-sm">No sync data available</p>
              </div>
              <div class="flex gap-2">
                <button
                  @click="triggerBSDataSync(false)"
                  :disabled="bsSyncing"
                  class="btn-secondary text-sm px-4 py-2"
                >
                  {{ bsSyncing ? 'Syncing...' : 'Sync' }}
                </button>
                <button
                  @click="triggerBSDataSync(true)"
                  :disabled="bsSyncing"
                  class="btn-secondary text-sm px-4 py-2"
                >
                  {{ bsSyncing ? 'Syncing...' : 'Force Full Sync' }}
                </button>
              </div>
            </div>
            <!-- Sync Result -->
            <div v-if="bsSyncResult" class="mt-4 p-3 rounded text-sm" :class="bsSyncResult.error ? 'bg-red-900/30 text-red-300' : 'bg-green-900/30 text-green-300'">
              <p v-if="bsSyncResult.error">Error: {{ bsSyncResult.error }}</p>
              <template v-else>
                <p>Sync completed ({{ bsSyncResult.sync_type }})</p>
                <p>Commit: {{ bsSyncResult.commit_short }} | Factions: {{ bsSyncResult.factions_count }} | Units: {{ bsSyncResult.units_count }}</p>
              </template>
            </div>
          </div>

          <!-- Battle Tactic Cards -->
          <div class="card mb-6">
            <h3 class="text-lg font-bold mb-4">Battle Tactic Cards ({{ bsBattleTactics.length }})</h3>
            <div v-if="bsBattleTactics.length === 0" class="text-gray-500 text-center py-4">
              No battle tactics synced yet.
            </div>
            <div v-else class="flex flex-wrap gap-2">
              <span v-for="card in bsBattleTactics" :key="card.id" class="bg-gray-800 px-3 py-1 rounded text-sm">
                {{ card.name }}
              </span>
            </div>
          </div>

          <!-- Factions List -->
          <div class="card">
            <h3 class="text-lg font-bold mb-4">Factions ({{ bsDataFactions.length }})</h3>
            <div v-if="bsDataFactions.length === 0" class="text-gray-500 text-center py-4">
              No factions synced yet. Run a sync first.
            </div>
            <div v-else class="overflow-x-auto">
              <table class="w-full text-sm">
                <thead>
                  <tr class="text-gray-400 border-b border-gray-700">
                    <th class="text-left py-2 px-3">Faction</th>
                    <th class="text-left py-2 px-3">Grand Alliance</th>
                    <th class="text-right py-2 px-3">Units</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="faction in bsDataFactions" :key="faction.id" class="border-b border-gray-800 hover:bg-gray-700/50">
                    <td class="py-2 px-3">{{ faction.name }}</td>
                    <td class="py-2 px-3">
                      <span :class="{
                        'text-blue-400': faction.grand_alliance === 'Order',
                        'text-red-400': faction.grand_alliance === 'Chaos',
                        'text-purple-400': faction.grand_alliance === 'Death',
                        'text-green-400': faction.grand_alliance === 'Destruction',
                      }">{{ faction.grand_alliance }}</span>
                    </td>
                    <td class="py-2 px-3 text-right">{{ faction.units_count }}</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </template>
      </div>
    </div>

    <!-- Delete Confirmation Modal -->
    <div v-if="deleteModal.show" class="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
      <div class="card max-w-md mx-4">
        <h3 class="text-xl font-bold mb-4">{{ t('admin.confirmDelete') }}</h3>
        <p class="text-gray-300 mb-6">
          {{ t('admin.deleteUserConfirm', { username: deleteModal.user?.username || deleteModal.user?.email }) }}
        </p>
        <div class="flex gap-4">
          <button @click="deleteModal.show = false" class="flex-1 btn-secondary">
            {{ t('common.cancel') }}
          </button>
          <button @click="deleteUser" class="flex-1 bg-red-600 hover:bg-red-700 text-white py-2 px-4 rounded">
            {{ t('admin.delete') }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRoute, useRouter } from 'vue-router'
import axios from 'axios'

const { t } = useI18n()
const route = useRoute()
const router = useRouter()
const API_URL = import.meta.env.VITE_API_URL || '/api'

const tabs = [
  { id: 'users', label: 'admin.usersTab' },
  { id: 'settings', label: 'admin.settingsTab' },
  { id: 'matchups', label: 'admin.matchupsTab' },
  { id: 'data', label: 'admin.dataTab' },
]

const roles = [
  { id: 'player', label: 'admin.rolePlayer' },
  { id: 'organizer', label: 'admin.roleOrganizer' },
  { id: 'admin', label: 'admin.roleAdmin' },
]

const activeTab = ref(route.params.tab || 'users')
const showTabsMenu = ref(false)
const roleMenuUser = ref(null)
const loading = ref(true)
const error = ref('')
const roleError = ref('')

// Users state
const users = ref([])
const stats = ref({
  total_users: 0,
  players: 0,
  organizers: 0,
  admins: 0,
})

// Settings state
const eloSettings = ref({
  k_factor: 32,
  new_player_k: 50,
  new_player_games: 5,
})
const saving = ref(false)
const saveError = ref('')
const saveSuccess = ref(false)

// Matchups state
const matchups = ref([])
const matchupsLoading = ref(false)
const matchupFilter = ref('all')

// Feature toggles
const rulesNavVisible = ref(localStorage.getItem('rules_nav_visible') === 'true')

const toggleRulesNav = () => {
  rulesNavVisible.value = !rulesNavVisible.value
  localStorage.setItem('rules_nav_visible', rulesNavVisible.value.toString())
}

// BSData state
const bsDataStatus = ref(null)
const bsDataFactions = ref([])
const bsBattleTactics = ref([])
const bsDataLoading = ref(false)
const bsSyncing = ref(false)
const bsSyncResult = ref(null)

// Delete modal
const deleteModal = ref({
  show: false,
  user: null,
})

// Watch tab changes
watch(activeTab, (newTab) => {
  router.replace({ params: { tab: newTab } })
  if (newTab === 'matchups' && matchups.value.length === 0) {
    fetchMatchups()
  }
  if (newTab === 'data' && !bsDataStatus.value) {
    fetchBSData()
  }
})

const fetchData = async () => {
  try {
    const [usersRes, statsRes, eloRes] = await Promise.all([
      axios.get(`${API_URL}/admin/users`),
      axios.get(`${API_URL}/admin/stats`),
      axios.get(`${API_URL}/admin/settings/elo`),
    ])

    users.value = usersRes.data.map(user => ({
      ...user,
      updating: false,
      saved: false,
      deleting: false,
      originalRole: user.role,
    }))
    stats.value = statsRes.data
    eloSettings.value = eloRes.data
  } catch (err) {
    if (err.response?.status === 403) {
      error.value = t('admin.accessDenied')
    } else {
      error.value = t('admin.failedToLoad')
    }
  } finally {
    loading.value = false
  }
}

const fetchMatchups = async () => {
  matchupsLoading.value = true
  try {
    const params = matchupFilter.value !== 'all' ? { status_filter: matchupFilter.value } : {}
    const response = await axios.get(`${API_URL}/admin/matchups`, { params })
    matchups.value = response.data
  } catch (err) {
    console.error('Failed to fetch matchups:', err)
  } finally {
    matchupsLoading.value = false
  }
}

const fetchBSData = async () => {
  bsDataLoading.value = true
  try {
    const [statusRes, factionsRes, tacticsRes] = await Promise.all([
      axios.get(`${API_URL}/bsdata/status`),
      axios.get(`${API_URL}/bsdata/factions`),
      axios.get(`${API_URL}/bsdata/battle-tactics`),
    ])
    bsDataStatus.value = statusRes.data
    bsDataFactions.value = factionsRes.data
    bsBattleTactics.value = tacticsRes.data
  } catch (err) {
    console.error('Failed to fetch BSData:', err)
  } finally {
    bsDataLoading.value = false
  }
}

const triggerBSDataSync = async (forceFull = false) => {
  bsSyncing.value = true
  bsSyncResult.value = null
  try {
    const response = await axios.post(`${API_URL}/bsdata/sync`, null, {
      params: { force_full: forceFull }
    })
    bsSyncResult.value = response.data
    // Refresh data after sync
    await fetchBSData()
  } catch (err) {
    bsSyncResult.value = { error: err.response?.data?.detail || 'Sync failed' }
  } finally {
    bsSyncing.value = false
  }
}

// Role menu helpers
const openRoleMenu = (user) => {
  roleMenuUser.value = user
}

const selectRole = (roleId) => {
  if (roleMenuUser.value && roleId !== roleMenuUser.value.role) {
    roleMenuUser.value.role = roleId
    updateRole(roleMenuUser.value)
  }
  roleMenuUser.value = null
}

const getRoleLabel = (role) => {
  const found = roles.find(r => r.id === role)
  return found ? t(found.label) : role
}

const getRoleClass = (role) => {
  switch (role) {
    case 'admin': return 'text-red-400'
    case 'organizer': return 'text-yellow-400'
    default: return 'text-blue-400'
  }
}

const updateRole = async (user) => {
  if (user.role === user.originalRole) return

  user.updating = true
  user.saved = false
  roleError.value = ''

  try {
    await axios.patch(`${API_URL}/admin/users/${user.id}/role`, {
      role: user.role,
    })
    user.originalRole = user.role
    user.saved = true

    const statsRes = await axios.get(`${API_URL}/admin/stats`)
    stats.value = statsRes.data

    setTimeout(() => {
      user.saved = false
    }, 2000)
  } catch (err) {
    roleError.value = err.response?.data?.detail || t('admin.failedToUpdateRole')
    user.role = user.originalRole
    setTimeout(() => {
      roleError.value = ''
    }, 5000)
  } finally {
    user.updating = false
  }
}

const confirmDeleteUser = (user) => {
  deleteModal.value = {
    show: true,
    user,
  }
}

const deleteUser = async () => {
  const user = deleteModal.value.user
  if (!user) return

  user.deleting = true
  deleteModal.value.show = false

  try {
    await axios.delete(`${API_URL}/admin/users/${user.id}`)
    users.value = users.value.filter(u => u.id !== user.id)

    const statsRes = await axios.get(`${API_URL}/admin/stats`)
    stats.value = statsRes.data
  } catch (err) {
    roleError.value = err.response?.data?.detail || t('admin.failedToDelete')
    setTimeout(() => {
      roleError.value = ''
    }, 5000)
  } finally {
    user.deleting = false
  }
}

const saveEloSettings = async () => {
  saving.value = true
  saveError.value = ''
  saveSuccess.value = false

  try {
    await axios.patch(`${API_URL}/admin/settings/elo`, eloSettings.value)
    saveSuccess.value = true
    setTimeout(() => {
      saveSuccess.value = false
    }, 3000)
  } catch (err) {
    saveError.value = err.response?.data?.detail || t('admin.failedToSave')
  } finally {
    saving.value = false
  }
}

const formatDate = (dateString) => {
  return new Date(dateString).toLocaleDateString()
}

onMounted(() => {
  fetchData()
  if (activeTab.value === 'matchups') {
    fetchMatchups()
  }
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
