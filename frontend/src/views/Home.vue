<template>
  <div class="max-w-5xl mx-auto">
    <!-- Hero Section -->
    <div class="text-center mb-16">
      <h1 class="text-5xl font-bold text-squig-yellow mb-4">
        Squig League
      </h1>
      <p class="text-xl text-gray-300 max-w-2xl mx-auto">
        {{ t('home.subtitle') }}
      </p>
    </div>

    <!-- Feature Cards -->
    <div class="grid md:grid-cols-3 gap-6 mb-12">
      <!-- Leagues Card -->
      <router-link to="/leagues" class="card hover:bg-gray-700 transition-colors group">
        <div class="text-4xl mb-4">
          <span class="text-squig-yellow">
            <svg class="w-12 h-12" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
            </svg>
          </span>
        </div>
        <h2 class="text-2xl font-bold mb-3 group-hover:text-squig-yellow transition-colors">{{ t('home.leaguesTitle') }}</h2>
        <p class="text-gray-400 mb-4">
          {{ t('home.leaguesDesc') }}
        </p>
        <span class="text-squig-yellow font-semibold inline-flex items-center">
          {{ t('home.browseLeagues') }}
          <svg class="w-4 h-4 ml-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
          </svg>
        </span>
      </router-link>

      <!-- Matchups Card -->
      <router-link to="/matchups" class="card hover:bg-gray-700 transition-colors group">
        <div class="text-4xl mb-4">
          <span class="text-squig-yellow">
            <svg class="w-12 h-12" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7h12m0 0l-4-4m4 4l-4 4m0 6H4m0 0l4 4m-4-4l4-4" />
            </svg>
          </span>
        </div>
        <h2 class="text-2xl font-bold mb-3 group-hover:text-squig-yellow transition-colors">{{ t('home.matchupsTitle') }}</h2>
        <p class="text-gray-400 mb-4">
          {{ t('home.matchupsDesc') }}
        </p>
        <span class="text-squig-yellow font-semibold inline-flex items-center">
          {{ t('home.createMatchup') }}
          <svg class="w-4 h-4 ml-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
          </svg>
        </span>
      </router-link>

      <!-- Coming Soon Card -->
      <div class="card bg-gray-800/50 border-dashed border-gray-600">
        <div class="text-4xl mb-4">
          <span class="text-gray-500">
            <svg class="w-12 h-12" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
            </svg>
          </span>
        </div>
        <h2 class="text-2xl font-bold mb-3 text-gray-500">{{ t('common.comingSoon') }}</h2>
        <p class="text-gray-500 mb-4">
          {{ t('home.comingSoonDesc') }}
        </p>
        <span class="text-gray-500 font-semibold">
          {{ t('common.stayTuned') }}
        </span>
      </div>
    </div>

    <!-- Quick Info Section -->
    <div class="card text-center">
      <h3 class="text-xl font-bold mb-4">{{ t('home.communityTitle') }}</h3>
      <p class="text-gray-400 max-w-2xl mx-auto">
        {{ t('home.communityDesc') }}
      </p>
    </div>
  </div>
</template>

<script setup>
import { useI18n } from 'vue-i18n'

const { t } = useI18n()
</script>
