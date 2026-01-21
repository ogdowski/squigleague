<template>
  <div class="card hover:bg-gray-700 transition-colors cursor-pointer">
    <div class="flex items-center justify-between">
      <div class="flex-1">
        <div class="flex items-center gap-2 mb-2">
          <h3 class="text-xl font-bold text-squig-yellow">
            {{ league.name }}
          </h3>
          <span v-if="league.is_organizer" class="text-xs bg-purple-900/50 text-purple-300 px-2 py-0.5 rounded">
            {{ t('leagues.organizer') }}
          </span>
          <span v-else-if="league.is_player" class="text-xs bg-blue-900/50 text-blue-300 px-2 py-0.5 rounded">
            {{ t('leagues.playing') }}
          </span>
        </div>
        <div class="flex flex-wrap gap-x-6 gap-y-1 text-sm">
          <div v-if="league.city || league.country" class="flex items-center gap-1 text-gray-400">
            <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z"/>
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 11a3 3 0 11-6 0 3 3 0 016 0z"/>
            </svg>
            <span class="text-white">{{ [league.city, league.country].filter(Boolean).join(', ') }}</span>
          </div>
          <div>
            <span class="text-gray-400">{{ t('leagues.organizer') }}:</span>
            <span class="text-white ml-1">{{ league.organizer_name || 'N/A' }}</span>
          </div>
          <div>
            <span class="text-gray-400">{{ t('leagues.players') }}:</span>
            <span class="text-white ml-1">{{ league.player_count }}</span>
          </div>
          <div v-if="league.status === 'finished' && league.finished_at">
            <span class="text-gray-400">{{ t('leagues.finishedOn') }}:</span>
            <span class="text-white ml-1">{{ formatDate(league.finished_at) }}</span>
          </div>
          <div v-else-if="league.status === 'knockout_phase' && league.knockout_phase_end">
            <span class="text-gray-400">{{ t('leagues.knockoutEnds') }}:</span>
            <span class="text-white ml-1">{{ formatDate(league.knockout_phase_end) }}</span>
          </div>
          <div v-else-if="league.status === 'group_phase' && league.group_phase_end">
            <span class="text-gray-400">{{ t('leagues.groupPhaseEnds') }}:</span>
            <span class="text-white ml-1">{{ formatDate(league.group_phase_end) }}</span>
          </div>
          <div v-else-if="league.status === 'registration'">
            <span class="text-gray-400">{{ t('leagues.registrationEnds') }}:</span>
            <span class="text-white ml-1">{{ formatDate(league.registration_end) }}</span>
          </div>
        </div>
      </div>

      <div class="flex items-center gap-4">
        <div
          :class="statusClass(league.status)"
          class="px-3 py-1 rounded text-sm"
        >
          {{ statusText(league.status) }}
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { useI18n } from 'vue-i18n'

const { t } = useI18n()

defineProps({
  league: {
    type: Object,
    required: true,
  },
})

const formatDate = (dateString) => {
  const date = new Date(dateString)
  return date.toLocaleDateString()
}

const statusClass = (status) => {
  switch (status) {
    case 'registration':
      return 'bg-blue-900/30 border border-blue-500 text-blue-200'
    case 'group_phase':
      return 'bg-yellow-900/30 border border-yellow-500 text-yellow-200'
    case 'knockout_phase':
      return 'bg-orange-900/30 border border-orange-500 text-orange-200'
    case 'finished':
      return 'bg-green-900/30 border border-green-500 text-green-200'
    default:
      return 'bg-gray-900/30 border border-gray-500 text-gray-200'
  }
}

const statusText = (status) => {
  switch (status) {
    case 'registration':
      return t('leagues.registration')
    case 'group_phase':
      return t('leagues.groupPhase')
    case 'knockout_phase':
      return t('leagues.knockoutPhase')
    case 'finished':
      return t('leagues.finished')
    default:
      return status
  }
}
</script>
