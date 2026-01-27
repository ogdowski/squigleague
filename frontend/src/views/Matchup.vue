<template>
  <div class="max-w-4xl mx-auto">
    <div v-if="loading" class="flex justify-center py-12">
      <div class="w-10 h-10 border-4 border-squig-yellow border-t-transparent rounded-full animate-spin"></div>
    </div>

    <div v-else-if="error" class="card">
      <div class="bg-red-900/30 border border-red-500 text-red-200 px-4 py-3 rounded">
        {{ error }}
      </div>
    </div>

    <!-- Cancelled matchup message -->
    <div v-else-if="matchup && matchup.is_cancelled" class="card">
      <div class="bg-red-900/30 border border-red-500 text-red-200 px-4 py-3 rounded mb-4">
        {{ t('matchups.matchupCancelled') }}
      </div>
      <h1 class="text-2xl font-bold mb-2">
        {{ matchup.title || t('matchups.matchupTitle') + ': ' + matchup.name }}
      </h1>
      <p class="text-gray-400">ID: {{ matchup.name }}</p>
    </div>

    <div v-else-if="matchup">
      <div class="card mb-6">
        <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-2 mb-4">
          <div class="flex-1">
            <!-- Title display mode -->
            <div v-if="!editingTitle" class="flex items-center gap-2">
              <h1 class="text-2xl md:text-3xl font-bold">
                {{ matchup.title || t('matchups.matchupTitle') + ': ' + matchup.name }}
              </h1>
              <button
                v-if="canEditMatchup"
                @click="startEditTitle"
                class="p-1 text-gray-400 hover:text-squig-yellow transition-colors"
                :title="t('common.edit')"
              >
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15.232 5.232l3.536 3.536m-2.036-5.036a2.5 2.5 0 113.536 3.536L6.5 21.036H3v-3.572L16.732 3.732z" />
                </svg>
              </button>
            </div>
            <!-- Title edit mode -->
            <div v-else class="flex items-center gap-2">
              <input
                v-model="editTitleValue"
                type="text"
                maxlength="100"
                class="input-field text-xl md:text-2xl font-bold flex-1"
                :placeholder="t('matchups.matchupTitlePlaceholder')"
                @keyup.enter="saveTitle"
                @keyup.escape="cancelEditTitle"
              />
              <button
                @click="saveTitle"
                :disabled="savingTitle"
                class="p-2 text-green-400 hover:text-green-300 transition-colors"
                :title="t('common.save')"
              >
                <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
                </svg>
              </button>
              <button
                @click="cancelEditTitle"
                class="p-2 text-gray-400 hover:text-gray-300 transition-colors"
                :title="t('common.cancel')"
              >
                <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>
            <p v-if="matchup.title" class="text-sm text-gray-400">ID: {{ matchup.name }}</p>
          </div>
        </div>

        <!-- Player status tiles - only show when not revealed -->
        <div v-if="!matchup.is_revealed" class="grid md:grid-cols-2 gap-4 mb-6">
          <div class="bg-gray-900 p-4 rounded">
            <div class="flex items-center gap-3 mb-2">
              <img
                v-if="matchup.player1_avatar"
                :src="matchup.player1_avatar"
                class="w-10 h-10 rounded-full"
                :alt="matchup.player1_username"
              />
              <div v-else class="w-10 h-10 rounded-full bg-gray-700 flex items-center justify-center text-gray-400">
                <svg class="w-6 h-6" fill="currentColor" viewBox="0 0 24 24">
                  <path d="M12 12c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm0 2c-2.67 0-8 1.34-8 4v2h16v-2c0-2.66-5.33-4-8-4z"/>
                </svg>
              </div>
              <div>
                <h3 class="font-bold">
                  <RouterLink
                    v-if="matchup.player1_id"
                    :to="{ name: 'PlayerProfile', params: { userId: matchup.player1_id } }"
                    class="hover:text-squig-yellow hover:underline"
                  >{{ matchup.player1_username }}</RouterLink>
                  <span v-else>{{ matchup.player1_username || t('matchups.player1') }}</span>
                </h3>
                <p v-if="matchup.player1_army_faction" class="text-sm text-squig-yellow">
                  {{ matchup.player1_army_faction }}
                </p>
              </div>
            </div>
            <p :class="matchup.player1_submitted ? 'text-green-400' : 'text-gray-400'">
              {{ matchup.player1_submitted ? '✓ ' + t('matchups.listSubmitted') : '○ ' + t('matchups.waitingForList') }}
            </p>
          </div>
          <div class="bg-gray-900 p-4 rounded">
            <div class="flex items-center gap-3 mb-2">
              <img
                v-if="matchup.player2_avatar"
                :src="matchup.player2_avatar"
                class="w-10 h-10 rounded-full"
                :alt="matchup.player2_username"
              />
              <div v-else class="w-10 h-10 rounded-full bg-gray-700 flex items-center justify-center text-gray-400">
                <svg class="w-6 h-6" fill="currentColor" viewBox="0 0 24 24">
                  <path d="M12 12c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm0 2c-2.67 0-8 1.34-8 4v2h16v-2c0-2.66-5.33-4-8-4z"/>
                </svg>
              </div>
              <div>
                <h3 class="font-bold">
                  <RouterLink
                    v-if="matchup.player2_id"
                    :to="{ name: 'PlayerProfile', params: { userId: matchup.player2_id } }"
                    class="hover:text-squig-yellow hover:underline"
                  >{{ matchup.player2_username }}</RouterLink>
                  <span v-else>{{ matchup.player2_username || t('matchups.player2') }}</span>
                </h3>
                <p v-if="matchup.player2_army_faction" class="text-sm text-squig-yellow">
                  {{ matchup.player2_army_faction }}
                </p>
              </div>
            </div>
            <p :class="matchup.player2_submitted ? 'text-green-400' : 'text-gray-400'">
              {{ matchup.player2_submitted ? '✓ ' + t('matchups.listSubmitted') : '○ ' + t('matchups.waitingForList') }}
            </p>
          </div>
        </div>
      </div>

      <!-- Waiting message for user who already submitted -->
      <div v-if="!matchup.is_revealed && hasUserSubmitted" class="card">
        <div class="bg-green-900/30 border border-green-500 text-green-200 px-4 py-3 rounded">
          {{ t('matchups.yourListSubmitted') }}
        </div>
        <p class="text-gray-300 mt-4">{{ t('matchups.waitingForOpponent') }}</p>

        <!-- Share link -->
        <div class="mt-6 pt-4 border-t border-gray-700">
          <label class="block text-sm font-medium mb-2">{{ t('matchups.shareLink') }}</label>
          <div class="flex gap-2">
            <input
              :value="matchupUrl"
              readonly
              class="input-field flex-1 font-mono text-sm"
            />
            <button
              @click="copyMatchupUrl"
              class="btn-secondary whitespace-nowrap"
            >
              {{ urlCopied ? t('matchups.copied') : t('matchups.copy') }}
            </button>
          </div>
        </div>

        <!-- Public visibility toggle -->
        <div class="mt-6 pt-4 border-t border-gray-700">
          <div class="flex items-center gap-3">
            <input
              type="checkbox"
              id="isPublicToggleWaiting"
              :checked="matchup.is_public"
              @change="togglePublic"
              class="w-4 h-4 rounded border-gray-600 bg-gray-700 text-squig-yellow focus:ring-squig-yellow"
            />
            <label for="isPublicToggleWaiting" class="text-sm text-gray-300">
              {{ t('matchups.showInPublicList') }}
            </label>
          </div>
        </div>

        <!-- Cancel button for player1 -->
        <div v-if="matchup.can_cancel" class="mt-4 pt-4 border-t border-gray-700">
          <button
            @click="openCancelModal"
            class="btn-secondary text-red-400 hover:text-red-300 hover:border-red-500"
          >
            {{ t('matchups.cancelMatchup') }}
          </button>
        </div>
      </div>

      <!-- Message for users blocked by assigned opponent -->
      <div v-if="isBlockedByAssignedOpponent" class="card">
        <div class="bg-yellow-900/30 border border-yellow-500 text-yellow-200 px-4 py-3 rounded">
          {{ t('matchups.assignedOpponentOnly') }}
        </div>
      </div>

      <!-- Submit form for user who hasn't submitted yet -->
      <div v-if="canSubmitList" class="card">
        <div class="mb-6">
          <div class="bg-blue-900/30 border border-blue-500 text-blue-200 px-4 py-3 rounded">
            {{ t('matchups.submitPrompt') }}
          </div>
        </div>

        <h2 class="text-2xl font-bold mb-4">{{ t('matchups.submitYourList') }}</h2>

        <form @submit.prevent="submitList" class="space-y-4">
          <div>
            <label class="block text-sm font-medium mb-2">
              {{ t('matchups.pasteListHere') }}
            </label>
            <textarea
              v-model="armyList"
              rows="15"
              class="input-field w-full font-mono text-sm"
              :placeholder="t('matchups.pasteListHere') + '...'"
              required
            ></textarea>
          </div>

          <div v-if="submitError" class="bg-red-900/30 border border-red-500 text-red-200 px-4 py-3 rounded">
            {{ submitError }}
          </div>

          <div v-if="submitSuccess" class="bg-green-900/30 border border-green-500 text-green-200 px-4 py-3 rounded">
            {{ t('matchups.listSubmittedSuccess') }}
            <span v-if="!matchup.is_revealed">{{ t('matchups.waitingForReveal') }}</span>
          </div>

          <button
            type="submit"
            :disabled="submitting"
            class="btn-primary w-full"
          >
            {{ submitting ? t('matchups.submitting') : t('matchups.submitList') }}
          </button>
        </form>

        <!-- Public visibility toggle for participants -->
        <div v-if="isParticipant" class="mt-6 pt-6 border-t border-gray-700">
          <div class="flex items-center gap-3">
            <input
              type="checkbox"
              id="isPublicToggleSubmit"
              :checked="matchup.is_public"
              @change="togglePublic"
              class="w-4 h-4 rounded border-gray-600 bg-gray-700 text-squig-yellow focus:ring-squig-yellow"
            />
            <label for="isPublicToggleSubmit" class="text-sm text-gray-300">
              {{ t('matchups.showInPublicList') }}
            </label>
          </div>
        </div>
      </div>

      <!-- Revealed matchup section -->
      <div v-if="matchup.is_revealed && reveal" class="space-y-6">
        <div class="card">
          <div class="bg-green-900/30 border border-green-500 text-green-200 px-4 py-3 rounded mb-6">
            {{ t('matchups.bothListsSubmitted') }}
          </div>

          <!-- Map Section - collapsible on mobile -->
          <div class="mb-6">
            <button
              @click="showMapSection = !showMapSection"
              class="w-full flex items-center justify-between text-left md:cursor-default"
            >
              <h2 class="text-lg md:text-2xl font-bold text-squig-yellow">
                <span class="md:hidden">{{ reveal.map_name || t('matchups.mapAssignment') }}</span>
                <span class="hidden md:inline">{{ t('matchups.mapAssignment') }}</span>
              </h2>
              <svg
                class="w-5 h-5 text-gray-400 md:hidden transition-transform"
                :class="{ 'rotate-180': showMapSection }"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
              </svg>
            </button>
            <div :class="{ 'hidden md:block': !showMapSection }" class="mt-4">
              <BattlePlanDisplay
                :map-name="reveal.map_name"
                :map-image="reveal.map_image"
                :battle-plan="revealBattlePlan"
              />
            </div>
          </div>

          <!-- Army Lists Section - collapsible on mobile -->
          <div class="mb-6">
            <button
              @click="showListsSection = !showListsSection"
              class="w-full flex items-center justify-between text-left md:cursor-default"
            >
              <h2 class="text-xl md:text-2xl font-bold text-squig-yellow">{{ t('matchups.armyLists') }}</h2>
              <svg
                class="w-5 h-5 text-gray-400 md:hidden transition-transform"
                :class="{ 'rotate-180': showListsSection }"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
              </svg>
            </button>
            <div :class="{ 'hidden md:block': !showListsSection }" class="mt-4 grid md:grid-cols-2 gap-4 md:gap-6">
              <!-- Player 1 List -->
              <div>
                <div class="flex items-center gap-3 mb-3">
                  <img
                    v-if="reveal.player1_avatar"
                    :src="reveal.player1_avatar"
                    class="w-8 h-8 rounded-full"
                    :alt="reveal.player1_username"
                  />
                  <div v-else class="w-8 h-8 rounded-full bg-gray-700 flex items-center justify-center text-gray-400">
                    <svg class="w-5 h-5" fill="currentColor" viewBox="0 0 24 24">
                      <path d="M12 12c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm0 2c-2.67 0-8 1.34-8 4v2h16v-2c0-2.66-5.33-4-8-4z"/>
                    </svg>
                  </div>
                  <div>
                    <h3 class="text-lg md:text-xl font-bold">
                      <RouterLink
                        v-if="reveal.player1_id"
                        :to="{ name: 'PlayerProfile', params: { userId: reveal.player1_id } }"
                        class="hover:text-squig-yellow hover:underline"
                      >{{ reveal.player1_username }}</RouterLink>
                      <span v-else>{{ reveal.player1_username || t('matchups.player1') }}</span>
                    </h3>
                    <p v-if="reveal.player1_army_faction" class="text-sm text-squig-yellow">
                      {{ reveal.player1_army_faction }}
                    </p>
                  </div>
                </div>
                <div class="bg-gray-900 p-3 md:p-4 rounded relative group">
                  <button
                    @click="copyList(reveal.player1_list, 'p1')"
                    class="absolute top-2 right-2 p-1.5 bg-gray-700 hover:bg-gray-600 rounded text-gray-400 hover:text-white transition-colors"
                    :title="t('common.copy') || 'Copy'"
                  >
                    <svg v-if="copiedList !== 'p1'" class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" />
                    </svg>
                    <svg v-else class="w-4 h-4 text-green-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
                    </svg>
                  </button>
                  <pre class="whitespace-pre-wrap font-mono text-xs md:text-sm text-gray-300 pr-8">{{ reveal.player1_list }}</pre>
                </div>
              </div>

              <!-- Player 2 List -->
              <div>
                <div class="flex items-center gap-3 mb-3">
                  <img
                    v-if="reveal.player2_avatar"
                    :src="reveal.player2_avatar"
                    class="w-8 h-8 rounded-full"
                    :alt="reveal.player2_username"
                  />
                  <div v-else class="w-8 h-8 rounded-full bg-gray-700 flex items-center justify-center text-gray-400">
                    <svg class="w-5 h-5" fill="currentColor" viewBox="0 0 24 24">
                      <path d="M12 12c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm0 2c-2.67 0-8 1.34-8 4v2h16v-2c0-2.66-5.33-4-8-4z"/>
                    </svg>
                  </div>
                  <div>
                    <h3 class="text-lg md:text-xl font-bold">
                      <RouterLink
                        v-if="reveal.player2_id"
                        :to="{ name: 'PlayerProfile', params: { userId: reveal.player2_id } }"
                        class="hover:text-squig-yellow hover:underline"
                      >{{ reveal.player2_username }}</RouterLink>
                      <span v-else>{{ reveal.player2_username || t('matchups.player2') }}</span>
                    </h3>
                    <p v-if="reveal.player2_army_faction" class="text-sm text-squig-yellow">
                      {{ reveal.player2_army_faction }}
                    </p>
                  </div>
                </div>
                <div class="bg-gray-900 p-3 md:p-4 rounded relative group">
                  <button
                    @click="copyList(reveal.player2_list, 'p2')"
                    class="absolute top-2 right-2 p-1.5 bg-gray-700 hover:bg-gray-600 rounded text-gray-400 hover:text-white transition-colors"
                    :title="t('common.copy') || 'Copy'"
                  >
                    <svg v-if="copiedList !== 'p2'" class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" />
                    </svg>
                    <svg v-else class="w-4 h-4 text-green-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
                    </svg>
                  </button>
                  <pre class="whitespace-pre-wrap font-mono text-xs md:text-sm text-gray-300 pr-8">{{ reveal.player2_list }}</pre>
                </div>
              </div>
            </div>
          </div>

          <!-- Result section -->
          <div class="mt-6 pt-6 border-t border-gray-700">
            <!-- Confirmed result display -->
            <div v-if="reveal?.result_status === 'confirmed'" class="mb-6">
              <h3 class="text-xl font-bold mb-3 text-squig-yellow">{{ t('matchups.matchResult') }}</h3>
              <div class="grid grid-cols-3 gap-4 bg-gray-900 p-4 rounded text-center">
                <div>
                  <p class="text-2xl font-bold" :class="reveal.player1_score > reveal.player2_score ? 'text-green-400' : ''">
                    {{ reveal.player1_score }}
                  </p>
                  <p class="text-sm text-gray-400">{{ reveal.player1_username || t('matchups.player1') }}</p>
                </div>
                <div class="flex items-center justify-center text-gray-500">vs</div>
                <div>
                  <p class="text-2xl font-bold" :class="reveal.player2_score > reveal.player1_score ? 'text-green-400' : ''">
                    {{ reveal.player2_score }}
                  </p>
                  <p class="text-sm text-gray-400">{{ reveal.player2_username || t('matchups.player2') }}</p>
                </div>
              </div>
            </div>

            <!-- Pending confirmation -->
            <div v-else-if="reveal?.result_status === 'pending_confirmation'" class="mb-6">
              <h3 class="text-xl font-bold mb-3">{{ t('matchups.pendingConfirmation') }}</h3>
              <div class="bg-yellow-900/30 border border-yellow-500 text-yellow-200 px-4 py-3 rounded mb-4">
                {{ t('matchups.resultAwaitingConfirmation') }}
                <span v-if="reveal.result_auto_confirm_at" class="block text-sm mt-1">
                  {{ t('matchups.autoConfirmAt') }}: {{ formatDate(reveal.result_auto_confirm_at) }}
                </span>
              </div>
              <div class="grid grid-cols-3 gap-4 bg-gray-900 p-4 rounded text-center mb-4">
                <div>
                  <p class="text-2xl font-bold">{{ reveal.player1_score }}</p>
                  <p class="text-sm text-gray-400">{{ reveal.player1_username || t('matchups.player1') }}</p>
                </div>
                <div class="flex items-center justify-center text-gray-500">vs</div>
                <div>
                  <p class="text-2xl font-bold">{{ reveal.player2_score }}</p>
                  <p class="text-sm text-gray-400">{{ reveal.player2_username || t('matchups.player2') }}</p>
                </div>
              </div>
              <!-- Confirm/Edit buttons for opponent - stacked on mobile -->
              <div v-if="reveal.can_confirm_result && !showEditForm" class="flex flex-col sm:flex-row gap-3">
                <button @click="confirmResult" :disabled="resultSubmitting" class="btn-primary flex-1 py-3 text-base">
                  {{ t('matchups.confirmResult') }}
                </button>
                <button @click="showEditForm = true; editPlayer1Score = reveal.player1_score; editPlayer2Score = reveal.player2_score" class="btn-secondary flex-1 py-3 text-base">
                  {{ t('matchups.editResult') }}
                </button>
              </div>
              <!-- Edit form - mobile-optimized -->
              <div v-if="reveal.can_confirm_result && showEditForm" class="mt-4">
                <form @submit.prevent="editResult" class="space-y-4">
                  <div class="flex items-center justify-center gap-4 py-4">
                    <div class="text-center flex-1 max-w-32">
                      <label class="block text-sm font-medium mb-2 text-gray-300 truncate">
                        {{ reveal.player1_username || t('matchups.player1') }}
                      </label>
                      <div class="relative group">
                        <input
                          v-model.number="editPlayer1Score"
                          type="number"
                          min="0"
                          inputmode="numeric"
                          pattern="[0-9]*"
                          class="score-input w-full bg-gray-700 border-2 border-gray-600 rounded-lg text-center text-3xl font-bold py-4 focus:outline-none focus:border-squig-yellow transition-colors"
                          style="font-size: 28px; min-height: 70px;"
                          required
                        />
                        <button type="button" @click="editPlayer1Score++" class="score-btn-up">
                          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 15l7-7 7 7"/></svg>
                        </button>
                        <button type="button" @click="editPlayer1Score = Math.max(0, editPlayer1Score - 1)" class="score-btn-down">
                          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"/></svg>
                        </button>
                      </div>
                    </div>
                    <div class="text-2xl text-gray-500 font-bold pt-6">:</div>
                    <div class="text-center flex-1 max-w-32">
                      <label class="block text-sm font-medium mb-2 text-gray-300 truncate">
                        {{ reveal.player2_username || t('matchups.player2') }}
                      </label>
                      <div class="relative group">
                        <input
                          v-model.number="editPlayer2Score"
                          type="number"
                          min="0"
                          inputmode="numeric"
                          pattern="[0-9]*"
                          class="score-input w-full bg-gray-700 border-2 border-gray-600 rounded-lg text-center text-3xl font-bold py-4 focus:outline-none focus:border-squig-yellow transition-colors"
                          style="font-size: 28px; min-height: 70px;"
                          required
                        />
                        <button type="button" @click="editPlayer2Score++" class="score-btn-up">
                          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 15l7-7 7 7"/></svg>
                        </button>
                        <button type="button" @click="editPlayer2Score = Math.max(0, editPlayer2Score - 1)" class="score-btn-down">
                          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"/></svg>
                        </button>
                      </div>
                    </div>
                  </div>
                  <div class="flex flex-col sm:flex-row gap-3">
                    <button type="submit" :disabled="resultSubmitting" class="btn-primary flex-1 py-3 text-base">
                      {{ t('matchups.submitEditedResult') }}
                    </button>
                    <button type="button" @click="showEditForm = false" class="btn-secondary flex-1 py-3 text-base">
                      {{ t('common.cancel') }}
                    </button>
                  </div>
                </form>
              </div>
            </div>

            <!-- Submit result form -->
            <div v-else-if="reveal?.can_submit_result" class="mb-6">
              <h3 class="text-xl font-bold mb-4">{{ t('matchups.submitResult') }}</h3>
              <form @submit.prevent="submitResult" class="space-y-4">
                <!-- Mobile-optimized score entry -->
                <div class="flex items-center justify-center gap-4 py-4">
                  <div class="text-center flex-1 max-w-32">
                    <label class="block text-sm font-medium mb-2 text-gray-300 truncate">
                      {{ reveal.player1_username || t('matchups.player1') }}
                    </label>
                    <div class="relative group">
                      <input
                        v-model.number="player1Score"
                        type="number"
                        min="0"
                        inputmode="numeric"
                        pattern="[0-9]*"
                        class="score-input w-full bg-gray-700 border-2 border-gray-600 rounded-lg text-center text-3xl font-bold py-4 focus:outline-none focus:border-squig-yellow transition-colors"
                        style="font-size: 28px; min-height: 70px;"
                        required
                      />
                      <button type="button" @click="player1Score++" class="score-btn-up">
                        <svg class="w-4 h-4 md:w-4 md:h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 15l7-7 7 7"/></svg>
                      </button>
                      <button type="button" @click="player1Score = Math.max(0, player1Score - 1)" class="score-btn-down">
                        <svg class="w-4 h-4 md:w-4 md:h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"/></svg>
                      </button>
                    </div>
                  </div>
                  <div class="text-2xl text-gray-500 font-bold pt-6">:</div>
                  <div class="text-center flex-1 max-w-32">
                    <label class="block text-sm font-medium mb-2 text-gray-300 truncate">
                      {{ reveal.player2_username || t('matchups.player2') }}
                    </label>
                    <div class="relative group">
                      <input
                        v-model.number="player2Score"
                        type="number"
                        min="0"
                        inputmode="numeric"
                        pattern="[0-9]*"
                        class="score-input w-full bg-gray-700 border-2 border-gray-600 rounded-lg text-center text-3xl font-bold py-4 focus:outline-none focus:border-squig-yellow transition-colors"
                        style="font-size: 28px; min-height: 70px;"
                        required
                      />
                      <button type="button" @click="player2Score++" class="score-btn-up">
                        <svg class="w-4 h-4 md:w-4 md:h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 15l7-7 7 7"/></svg>
                      </button>
                      <button type="button" @click="player2Score = Math.max(0, player2Score - 1)" class="score-btn-down">
                        <svg class="w-4 h-4 md:w-4 md:h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"/></svg>
                      </button>
                    </div>
                  </div>
                </div>
                <div v-if="resultError" class="bg-red-900/30 border border-red-500 text-red-200 px-4 py-3 rounded">
                  {{ resultError }}
                </div>
                <button type="submit" :disabled="resultSubmitting" class="btn-primary w-full py-4 text-lg">
                  {{ resultSubmitting ? t('matchups.submitting') : t('matchups.submitResult') }}
                </button>
              </form>
            </div>

            <!-- Info message for non-logged users -->
            <div v-else-if="reveal?.result_info_message" class="mb-6">
              <div class="bg-blue-900/30 border border-blue-500 text-blue-200 px-4 py-3 rounded">
                {{ reveal.result_info_message }}
              </div>
            </div>
          </div>

          <!-- Public visibility toggle (for participants at any time) -->
          <div v-if="isParticipant" class="mt-6 pt-6 border-t border-gray-700">
            <div class="flex items-center gap-3">
              <input
                type="checkbox"
                id="isPublicToggle"
                :checked="matchup.is_public"
                @change="togglePublic"
                class="w-4 h-4 rounded border-gray-600 bg-gray-700 text-squig-yellow focus:ring-squig-yellow"
              />
              <label for="isPublicToggle" class="text-sm text-gray-300">
                {{ t('matchups.showInPublicList') }}
              </label>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Cancel Confirmation Modal -->
    <div v-if="showCancelModal" class="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
      <div class="card max-w-md mx-4">
        <h3 class="text-xl font-bold mb-4">{{ t('matchups.cancelMatchup') }}</h3>
        <p class="text-gray-300 mb-6">
          {{ t('matchups.confirmCancel') }}
        </p>
        <div class="flex gap-4">
          <button @click="closeCancelModal" class="flex-1 btn-secondary">
            {{ t('common.cancel') }}
          </button>
          <button
            @click="cancelMatchup"
            :disabled="cancelling"
            class="flex-1 btn-primary bg-red-600 hover:bg-red-700"
          >
            {{ cancelling ? t('matchups.cancelling') : t('matchups.confirmCancelButton') }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, RouterLink } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { useAuthStore } from '../stores/auth'
import axios from 'axios'
import BattlePlanDisplay from '@/components/BattlePlanDisplay.vue'

const { t } = useI18n()
const authStore = useAuthStore()
const API_URL = import.meta.env.VITE_API_URL || '/api'
const route = useRoute()

const loading = ref(true)
const error = ref('')
const matchup = ref(null)
const reveal = ref(null)

const armyList = ref('')
const submitting = ref(false)
const submitError = ref('')
const submitSuccess = ref(false)

// Result submission
const player1Score = ref(0)
const player2Score = ref(0)
const resultSubmitting = ref(false)
const resultError = ref('')

// Result editing
const showEditForm = ref(false)
const editPlayer1Score = ref(0)
const editPlayer2Score = ref(0)

// Mobile section toggles
const showMapSection = ref(true)
const showListsSection = ref(true)

// Copy list feedback
const copiedList = ref(null)
const copyList = async (text, listId) => {
  try {
    await navigator.clipboard.writeText(text)
    copiedList.value = listId
    setTimeout(() => { copiedList.value = null }, 2000)
  } catch (err) {
    console.error('Failed to copy:', err)
  }
}

// Matchup URL for sharing
const matchupUrl = computed(() => {
  return `${window.location.origin}/matchup/${route.params.name}`
})

const urlCopied = ref(false)

const copyMatchupUrl = async () => {
  try {
    await navigator.clipboard.writeText(matchupUrl.value)
    urlCopied.value = true
    setTimeout(() => { urlCopied.value = false }, 2000)
  } catch (err) {
    console.error('Failed to copy URL:', err)
  }
}

// Check if current user is a participant
const isParticipant = computed(() => {
  if (!authStore.isAuthenticated || !authStore.user || !matchup.value) {
    return false
  }
  const username = authStore.user.username
  return matchup.value.player1_username === username || matchup.value.player2_username === username
})

// Check if user can edit matchup (participant and result not confirmed)
const canEditMatchup = computed(() => {
  if (!isParticipant.value || !matchup.value) return false
  return matchup.value.result_status !== 'confirmed'
})

// Title editing
const editingTitle = ref(false)
const editTitleValue = ref('')
const savingTitle = ref(false)

const startEditTitle = () => {
  editTitleValue.value = matchup.value?.title || ''
  editingTitle.value = true
}

const cancelEditTitle = () => {
  editingTitle.value = false
  editTitleValue.value = ''
}

const saveTitle = async () => {
  if (!matchup.value) return
  savingTitle.value = true
  try {
    await axios.patch(`${API_URL}/matchup/${route.params.name}/title`, {
      title: editTitleValue.value || null
    })
    matchup.value.title = editTitleValue.value || null
    editingTitle.value = false
  } catch (err) {
    console.error('Failed to save title:', err)
  } finally {
    savingTitle.value = false
  }
}

// Matchup cancellation
const cancelling = ref(false)
const showCancelModal = ref(false)

const openCancelModal = () => {
  showCancelModal.value = true
}

const closeCancelModal = () => {
  showCancelModal.value = false
}

const cancelMatchup = async () => {
  if (!matchup.value) return
  cancelling.value = true
  try {
    await axios.post(`${API_URL}/matchup/${route.params.name}/cancel`)
    matchup.value.is_cancelled = true
    showCancelModal.value = false
  } catch (err) {
    console.error('Failed to cancel matchup:', err)
  } finally {
    cancelling.value = false
  }
}

// Check if current user has already submitted their list
const hasUserSubmitted = computed(() => {
  if (!authStore.isAuthenticated || !authStore.user || !matchup.value) {
    return false
  }
  const username = authStore.user.username
  if (matchup.value.player1_username === username) {
    return matchup.value.player1_submitted
  }
  if (matchup.value.player2_username === username) {
    return matchup.value.player2_submitted
  }
  return false
})

// Check if user can submit a list (not revealed and hasn't submitted yet)
const canSubmitList = computed(() => {
  if (!matchup.value || matchup.value.is_revealed) {
    return false
  }
  // If logged in and already submitted, can't submit again
  if (hasUserSubmitted.value) {
    return false
  }
  // If player2 is assigned to a specific user, only they can submit
  if (matchup.value.player2_id && !matchup.value.player2_submitted) {
    // Player2 slot is taken by a registered user
    if (!authStore.isAuthenticated) {
      return false // Anonymous users can't submit
    }
    const currentUsername = authStore.user?.username
    // Only assigned player2 or player1 can submit
    if (currentUsername !== matchup.value.player2_username &&
        currentUsername !== matchup.value.player1_username) {
      return false
    }
  }
  return true
})

// Check if user is blocked from submitting because opponent is assigned
const isBlockedByAssignedOpponent = computed(() => {
  if (!matchup.value || matchup.value.is_revealed) return false
  if (matchup.value.player2_id && !matchup.value.player2_submitted) {
    if (!authStore.isAuthenticated) return true
    const currentUsername = authStore.user?.username
    if (currentUsername !== matchup.value.player2_username &&
        currentUsername !== matchup.value.player1_username) {
      return true
    }
  }
  return false
})

// Build battle plan object from reveal data (comes from API)
const revealBattlePlan = computed(() => {
  if (!reveal.value) return null
  return {
    objectives: reveal.value.objectives,
    scoring: reveal.value.scoring,
    underdog_ability: reveal.value.underdog_ability,
    objective_types: reveal.value.objective_types,
  }
})

const fetchMatchup = async () => {
  try {
    const response = await axios.get(`${API_URL}/matchup/${route.params.name}`)
    matchup.value = response.data

    if (response.data.is_revealed) {
      await fetchReveal()
    }
  } catch (err) {
    if (err.response?.status === 404) {
      error.value = t('matchups.matchupNotFound')
    } else {
      error.value = t('matchups.failedToLoad')
    }
  } finally {
    loading.value = false
  }
}

const fetchReveal = async () => {
  try {
    const response = await axios.get(`${API_URL}/matchup/${route.params.name}/reveal`)
    reveal.value = response.data
  } catch (err) {
    console.error('Failed to fetch reveal:', err)
  }
}

const submitList = async () => {
  submitError.value = ''
  submitSuccess.value = false
  submitting.value = true

  try {
    const response = await axios.post(
      `${API_URL}/matchup/${route.params.name}/submit`,
      { army_list: armyList.value }
    )

    submitSuccess.value = true
    armyList.value = ''

    if (response.data.is_revealed) {
      await fetchMatchup()
    } else {
      matchup.value.player1_submitted = true
    }
  } catch (err) {
    submitError.value = err.response?.data?.detail || t('matchups.failedToSubmitList')
  } finally {
    submitting.value = false
  }
}

const formatDate = (dateString) => {
  return new Date(dateString).toLocaleString()
}

const togglePublic = async () => {
  if (!matchup.value) return
  try {
    const newValue = !matchup.value.is_public
    await axios.patch(`${API_URL}/matchup/${route.params.name}/public`, {
      is_public: newValue
    })
    matchup.value.is_public = newValue
  } catch (err) {
    console.error('Failed to toggle public:', err)
  }
}

const submitResult = async () => {
  resultError.value = ''
  resultSubmitting.value = true

  try {
    await axios.post(`${API_URL}/matchup/${route.params.name}/result`, {
      player1_score: player1Score.value,
      player2_score: player2Score.value
    })
    await fetchReveal()
  } catch (err) {
    resultError.value = err.response?.data?.detail || t('matchups.failedToSubmitResult')
  } finally {
    resultSubmitting.value = false
  }
}

const confirmResult = async () => {
  resultSubmitting.value = true
  try {
    await axios.post(`${API_URL}/matchup/${route.params.name}/result/confirm`)
    await fetchReveal()
  } catch (err) {
    console.error('Failed to confirm result:', err)
  } finally {
    resultSubmitting.value = false
  }
}

const editResult = async () => {
  resultSubmitting.value = true
  try {
    await axios.post(`${API_URL}/matchup/${route.params.name}/result/edit`, {
      player1_score: editPlayer1Score.value,
      player2_score: editPlayer2Score.value
    })
    showEditForm.value = false
    await fetchReveal()
  } catch (err) {
    console.error('Failed to edit result:', err)
  } finally {
    resultSubmitting.value = false
  }
}

onMounted(() => {
  fetchMatchup()
})
</script>

<style scoped>
.score-input::-webkit-inner-spin-button,
.score-input::-webkit-outer-spin-button {
  -webkit-appearance: none;
  margin: 0;
}
.score-input {
  -moz-appearance: textfield;
}

.score-btn-up,
.score-btn-down {
  position: absolute;
  right: 4px;
  width: 36px;
  height: 36px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #4b5563;
  border-radius: 8px;
  color: #d1d5db;
  opacity: 1;
  transition: background 0.15s;
}
.score-btn-up:hover,
.score-btn-down:hover,
.score-btn-up:active,
.score-btn-down:active {
  background: #f59e0b;
  color: #000;
}
.score-btn-up {
  top: 4px;
}
.score-btn-down {
  bottom: 4px;
}
.score-btn-up svg,
.score-btn-down svg {
  width: 20px;
  height: 20px;
}

@media (min-width: 768px) {
  .score-btn-up,
  .score-btn-down {
    width: 28px;
    height: 28px;
    opacity: 0;
  }
  .score-btn-up svg,
  .score-btn-down svg {
    width: 16px;
    height: 16px;
  }
  .group:hover .score-btn-up,
  .group:hover .score-btn-down {
    opacity: 1;
  }
}
</style>
