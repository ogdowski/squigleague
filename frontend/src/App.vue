<template>
  <div id="app" class="min-h-screen flex flex-col">
    <nav class="bg-gray-800 border-b border-gray-700 sticky top-0 z-40">
      <div class="container mx-auto px-3 py-1.5 md:px-4 md:py-3">
        <div class="flex items-center justify-between">
          <router-link to="/" class="text-lg md:text-2xl font-bold tracking-wide" style="font-family: system-ui, -apple-system, sans-serif;">
            <span class="text-squig-yellow">SQUIG</span> <span class="text-white">LEAGUE</span>
          </router-link>

          <!-- Desktop Navigation -->
          <div class="hidden md:flex items-center gap-3">
            <router-link to="/leagues" class="btn-secondary flex items-center gap-2">
              <svg class="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M6 9H4a2 2 0 01-2-2V4a2 2 0 012-2h2M18 9h2a2 2 0 002-2V4a2 2 0 00-2-2h-2M6 2h12v7a6 6 0 11-12 0V2zM12 15v4M8 21h8" stroke-linecap="round" stroke-linejoin="round"/>
              </svg>
              {{ t('nav.leagues') }}
            </router-link>
            <router-link to="/matchups" class="btn-secondary flex items-center gap-2">
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7h12m0 0l-4-4m4 4l-4 4m0 6H4m0 0l4 4m-4-4l4-4" />
              </svg>
              {{ t('nav.matchups') }}
            </router-link>
            <router-link to="/ranking" class="btn-secondary flex items-center gap-2">
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
              </svg>
              {{ t('nav.ranking') }}
            </router-link>
            <router-link v-if="rulesNavVisible && authStore.isAuthenticated" to="/rules" class="btn-secondary flex items-center gap-2">
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
              </svg>
              {{ t('nav.rules') }}
            </router-link>

            <div v-if="authStore.isAuthenticated" class="flex items-center gap-4">
              <router-link
                v-if="authStore.user?.role === 'admin'"
                to="/admin/users"
                class="btn-secondary bg-red-900/30 border-red-500 text-red-200"
              >
                {{ t('nav.admin') }}
              </router-link>
              <!-- User dropdown -->
              <div class="relative">
                <button
                  @click="showUserMenu = !showUserMenu"
                  class="btn-secondary flex items-center gap-2"
                >
                  <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                  </svg>
                  {{ authStore.user?.username }}
                  <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
                  </svg>
                </button>
                <div
                  v-if="showUserMenu"
                  class="absolute right-0 top-full mt-2 w-48 bg-gray-800 border border-gray-700 rounded-lg shadow-xl z-30"
                >
                  <router-link
                    :to="`/player/${authStore.user?.id}`"
                    @click="showUserMenu = false"
                    class="flex items-center gap-2 px-4 py-2 hover:bg-gray-700 rounded-t-lg"
                  >
                    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                    </svg>
                    {{ t('nav.profile') }}
                  </router-link>
                  <router-link
                    to="/settings"
                    @click="showUserMenu = false"
                    class="flex items-center gap-2 px-4 py-2 hover:bg-gray-700"
                  >
                    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                    </svg>
                    {{ t('nav.settings') }}
                  </router-link>
                  <button
                    @click="authStore.logout(); showUserMenu = false"
                    class="flex items-center gap-2 w-full text-left px-4 py-2 hover:bg-gray-700 rounded-b-lg text-red-400"
                  >
                    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
                    </svg>
                    {{ t('nav.logout') }}
                  </button>
                </div>
              </div>
              <!-- Click outside to close -->
              <div v-if="showUserMenu" @click="showUserMenu = false" class="fixed inset-0 z-20"></div>
            </div>

            <div v-else class="flex gap-2">
              <router-link to="/login" class="btn-secondary">
                {{ t('nav.login') }}
              </router-link>
              <router-link to="/register" class="btn-primary">
                {{ t('nav.register') }}
              </router-link>
            </div>
          </div>

          <!-- Mobile: Login/Register or User + Hamburger -->
          <div class="flex md:hidden items-center gap-2">
            <div v-if="!authStore.isAuthenticated" class="flex items-center gap-2">
              <router-link to="/login" class="inline-flex items-center justify-center bg-gray-700 hover:bg-gray-600 text-white text-sm font-bold h-9 px-3 rounded transition-colors">
                {{ t('nav.login') }}
              </router-link>
              <router-link to="/register" class="inline-flex items-center justify-center bg-squig-yellow hover:bg-yellow-500 text-black text-sm font-bold h-9 px-3 rounded transition-colors">
                {{ t('nav.register') }}
              </router-link>
            </div>
            <div v-else class="flex items-center">
              <router-link :to="`/player/${authStore.user?.id}`" class="text-squig-yellow text-sm font-medium truncate max-w-20">
                {{ authStore.user?.username }}
              </router-link>
            </div>
            <!-- Hamburger button -->
            <button
              @click="showMobileMenu = !showMobileMenu"
              class="p-2 text-gray-300 hover:text-white hover:bg-gray-700 rounded-lg transition-colors"
              aria-label="Menu"
            >
              <svg v-if="!showMobileMenu" class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16" />
              </svg>
              <svg v-else class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
        </div>

      </div>
    </nav>

    <!-- Mobile Menu Overlay -->
    <Transition name="mobile-menu">
      <div
        v-if="showMobileMenu"
        class="md:hidden fixed inset-x-0 top-[41px] z-40"
      >
        <!-- Backdrop (below nav) -->
        <div class="fixed inset-x-0 top-[41px] bottom-0 bg-black/50" @click="showMobileMenu = false"></div>
        <!-- Menu panel -->
        <div class="relative bg-gray-800 border-b border-gray-700 shadow-xl px-4 py-3 space-y-1">
          <router-link
            to="/leagues"
            @click="showMobileMenu = false"
            class="flex items-center gap-3 px-3 py-3 rounded-lg hover:bg-gray-700 transition-colors"
          >
            <svg class="w-5 h-5 text-squig-yellow" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M6 9H4a2 2 0 01-2-2V4a2 2 0 012-2h2M18 9h2a2 2 0 002-2V4a2 2 0 00-2-2h-2M6 2h12v7a6 6 0 11-12 0V2zM12 15v4M8 21h8" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
            {{ t('nav.leagues') }}
          </router-link>
          <router-link
            to="/matchups"
            @click="showMobileMenu = false"
            class="flex items-center gap-3 px-3 py-3 rounded-lg hover:bg-gray-700 transition-colors"
          >
            <svg class="w-5 h-5 text-squig-yellow" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7h12m0 0l-4-4m4 4l-4 4m0 6H4m0 0l4 4m-4-4l4-4" />
            </svg>
            {{ t('nav.matchups') }}
          </router-link>
          <router-link
            to="/ranking"
            @click="showMobileMenu = false"
            class="flex items-center gap-3 px-3 py-3 rounded-lg hover:bg-gray-700 transition-colors"
          >
            <svg class="w-5 h-5 text-squig-yellow" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
            </svg>
            {{ t('nav.ranking') }}
          </router-link>
          <router-link
            v-if="rulesNavVisible && authStore.isAuthenticated"
            to="/rules"
            @click="showMobileMenu = false"
            class="flex items-center gap-3 px-3 py-3 rounded-lg hover:bg-gray-700 transition-colors"
          >
            <svg class="w-5 h-5 text-squig-yellow" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
            </svg>
            {{ t('nav.rules') }}
          </router-link>

          <template v-if="authStore.isAuthenticated">
            <div class="border-t border-gray-700 my-2"></div>
            <router-link
              v-if="authStore.user?.role === 'admin'"
              to="/admin/users"
              @click="showMobileMenu = false"
              class="flex items-center gap-3 px-3 py-3 rounded-lg hover:bg-gray-700 transition-colors text-red-300"
            >
              <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6V4m0 2a2 2 0 100 4m0-4a2 2 0 110 4m-6 8a2 2 0 100-4m0 4a2 2 0 110-4m0 4v2m0-6V4m6 6v10m6-2a2 2 0 100-4m0 4a2 2 0 110-4m0 4v2m0-6V4" />
              </svg>
              {{ t('nav.admin') }}
            </router-link>
            <router-link
              :to="`/player/${authStore.user?.id}`"
              @click="showMobileMenu = false"
              class="flex items-center gap-3 px-3 py-3 rounded-lg hover:bg-gray-700 transition-colors"
            >
              <svg class="w-5 h-5 text-squig-yellow" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
              </svg>
              {{ t('nav.profile') }}
            </router-link>
            <router-link
              to="/settings"
              @click="showMobileMenu = false"
              class="flex items-center gap-3 px-3 py-3 rounded-lg hover:bg-gray-700 transition-colors"
            >
              <svg class="w-5 h-5 text-squig-yellow" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
              </svg>
              {{ t('nav.settings') }}
            </router-link>
            <button
              @click="authStore.logout(); showMobileMenu = false"
              class="flex items-center gap-3 px-3 py-3 rounded-lg hover:bg-gray-700 transition-colors text-red-400 w-full text-left"
            >
              <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
              </svg>
              {{ t('nav.logout') }}
            </button>
          </template>
        </div>
      </div>
    </Transition>

    <!-- Navigation loading spinner -->
    <div v-if="isNavigating" class="fixed inset-0 z-50 flex items-center justify-center bg-gray-900/50">
      <div class="w-10 h-10 border-4 border-squig-yellow border-t-transparent rounded-full animate-spin"></div>
    </div>

    <main class="container mx-auto px-4 py-8 pb-16 flex-1">
      <router-view />
    </main>

    <!-- Back to top button -->
    <button
      v-if="showBackToTop"
      @click="scrollToTop"
      class="fixed bottom-16 right-4 md:bottom-20 md:right-6 p-2 bg-gray-700 hover:bg-squig-yellow hover:text-black rounded-full shadow-lg transition-colors z-20"
      aria-label="Back to top"
    >
      <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 15l7-7 7 7" />
      </svg>
    </button>

    <!-- Footer: sticky on tablet/desktop, normal on mobile -->
    <footer class="mt-auto border-t border-gray-700 bg-gray-800 md:sticky md:bottom-0">
      <!-- Mobile: compact footer -->
      <div class="md:hidden">
        <div class="container mx-auto px-4 py-2 space-y-1">
          <div class="flex items-center justify-between text-xs text-gray-400">
            <LanguageSwitcher />
            <div class="flex items-center gap-2">
              <span v-if="bsDataStatus" class="text-gray-500">BSData: {{ bsDataStatus.commit_short }}</span>
              <span v-if="stats">v{{ stats.version }}</span>
            </div>
          </div>
          <div class="flex items-center justify-between text-xs">
            <span class="text-gray-500">© 2025 Ariel Ogdowski</span>
            <button @click="showFeedbackInfo = true" class="text-squig-yellow">
              {{ t('footer.feedback') }}
            </button>
          </div>
        </div>
      </div>
      <!-- Desktop: full footer -->
      <div class="hidden md:block">
        <div class="container mx-auto px-4 py-4">
          <div class="flex justify-between items-center text-sm text-gray-400">
            <div class="flex items-center gap-3">
              <LanguageSwitcher />
              <span>© 2025 Ariel Ogdowski. {{ t('footer.copyright') }}</span>
            </div>
            <div class="flex items-center gap-3">
              <button @click="showFeedbackInfo = true" class="hover:text-squig-yellow transition-colors">
                {{ t('footer.feedback') }}
              </button>
              <span v-if="bsDataStatus" class="text-gray-500">• BSData: {{ bsDataStatus.commit_short }}</span>
              <span v-if="stats">• v{{ stats.version }}</span>
            </div>
          </div>
        </div>
      </div>
    </footer>

    <!-- Feedback Modal -->
    <div v-if="showFeedbackInfo" class="fixed inset-0 bg-black/50 flex items-center justify-center z-50" @click.self="showFeedbackInfo = false">
      <div class="bg-gray-800 rounded-lg p-6 max-w-sm w-full mx-4">
        <h3 class="text-xl font-bold mb-4">{{ t('footer.feedback') }}</h3>
        <p class="text-gray-300 mb-4">{{ t('footer.feedbackInfo') }}</p>
        <div class="space-y-3">
          <a href="mailto:ariel@ogdowscy.pl" class="flex items-center gap-3 bg-gray-700 rounded px-4 py-3 hover:bg-gray-600 transition-colors">
            <svg class="w-5 h-5 text-squig-yellow" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
            </svg>
            <span class="text-squig-yellow">ariel@ogdowscy.pl</span>
          </a>
          <div class="flex items-center gap-3 bg-gray-700 rounded px-4 py-3">
            <svg class="w-5 h-5 text-squig-yellow" viewBox="0 0 24 24" fill="currentColor">
              <path d="M20.317 4.37a19.791 19.791 0 0 0-4.885-1.515a.074.074 0 0 0-.079.037c-.21.375-.444.864-.608 1.25a18.27 18.27 0 0 0-5.487 0a12.64 12.64 0 0 0-.617-1.25a.077.077 0 0 0-.079-.037A19.736 19.736 0 0 0 3.677 4.37a.07.07 0 0 0-.032.027C.533 9.046-.32 13.58.099 18.057a.082.082 0 0 0 .031.057a19.9 19.9 0 0 0 5.993 3.03a.078.078 0 0 0 .084-.028a14.09 14.09 0 0 0 1.226-1.994a.076.076 0 0 0-.041-.106a13.107 13.107 0 0 1-1.872-.892a.077.077 0 0 1-.008-.128a10.2 10.2 0 0 0 .372-.292a.074.074 0 0 1 .077-.01c3.928 1.793 8.18 1.793 12.062 0a.074.074 0 0 1 .078.01c.12.098.246.198.373.292a.077.077 0 0 1-.006.127a12.299 12.299 0 0 1-1.873.892a.077.077 0 0 0-.041.107c.36.698.772 1.362 1.225 1.993a.076.076 0 0 0 .084.028a19.839 19.839 0 0 0 6.002-3.03a.077.077 0 0 0 .032-.054c.5-5.177-.838-9.674-3.549-13.66a.061.061 0 0 0-.031-.03zM8.02 15.33c-1.183 0-2.157-1.085-2.157-2.419c0-1.333.956-2.419 2.157-2.419c1.21 0 2.176 1.096 2.157 2.42c0 1.333-.956 2.418-2.157 2.418zm7.975 0c-1.183 0-2.157-1.085-2.157-2.419c0-1.333.955-2.419 2.157-2.419c1.21 0 2.176 1.096 2.157 2.42c0 1.333-.946 2.418-2.157 2.418z"/>
            </svg>
            <span class="text-squig-yellow">Arieli61</span>
          </div>
        </div>
        <button @click="showFeedbackInfo = false" class="btn-secondary w-full mt-4">
          {{ t('common.close') }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRouter } from 'vue-router'
import { useAuthStore } from './stores/auth'
import { useLanguageStore } from './stores/language'
import LanguageSwitcher from './components/LanguageSwitcher.vue'
import axios from 'axios'
import packageJson from '../package.json'

const { t, locale } = useI18n()
const router = useRouter()
const authStore = useAuthStore()
const languageStore = useLanguageStore()
const stats = ref(null)
const bsDataStatus = ref(null)
const rulesNavVisible = ref(localStorage.getItem('rules_nav_visible') === 'true')
const showUserMenu = ref(false)
const showMobileMenu = ref(false)
const showMobileFooter = ref(false)
const showFeedbackInfo = ref(false)
const isNavigating = ref(false)
const showBackToTop = ref(false)

// Show loading spinner during navigation
router.beforeEach(() => {
  isNavigating.value = true
})
router.afterEach(() => {
  isNavigating.value = false
})

// Back to top button
const scrollToTop = () => {
  window.scrollTo({ top: 0, behavior: 'smooth' })
}

const handleScroll = () => {
  showBackToTop.value = window.scrollY > 300
}

window.addEventListener('scroll', handleScroll)

const API_URL = import.meta.env.VITE_API_URL || '/api'

const fetchStats = async () => {
  try {
    const response = await axios.get(`${API_URL}/matchup/stats`)
    stats.value = response.data
  } catch (error) {
    console.error('Failed to fetch stats:', error)
    // Fallback to package.json version
    stats.value = {
      version: packageJson.version,
      exchanges_completed: 0
    }
  }
}

const fetchBSDataStatus = async () => {
  try {
    const response = await axios.get(`${API_URL}/bsdata/status`)
    bsDataStatus.value = response.data
  } catch (error) {
    // BSData not synced yet, ignore
  }
}

onMounted(() => {
  // Sync vue-i18n locale with language store
  locale.value = languageStore.currentLocale
  authStore.initAuth()
  fetchStats()
  fetchBSDataStatus()
})
</script>

<style scoped>
/* Mobile menu slide animation */
.mobile-menu-enter-active,
.mobile-menu-leave-active {
  transition: all 0.2s ease-out;
}

.mobile-menu-enter-from,
.mobile-menu-leave-to {
  opacity: 0;
  transform: translateY(-10px);
}

.mobile-menu-enter-to,
.mobile-menu-leave-from {
  opacity: 1;
  transform: translateY(0);
}
</style>
