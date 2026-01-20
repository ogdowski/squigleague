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
        <div class="flex gap-6 text-sm">
          <div>
            <span class="text-gray-400">{{ t('leagues.organizer') }}:</span>
            <span class="text-white ml-2">{{ league.organizer_name || 'N/A' }}</span>
          </div>
          <div>
            <span class="text-gray-400">{{ t('leagues.players') }}:</span>
            <span class="text-white ml-2">{{ league.player_count }}</span>
          </div>
          <div v-if="league.status === 'finished' && league.finished_at">
            <span class="text-gray-400">{{ t('leagues.finishedOn') }}:</span>
            <span class="text-white ml-2">{{ formatDate(league.finished_at) }}</span>
          </div>
          <div v-else>
            <span class="text-gray-400">{{ t('leagues.registrationEnds') }}:</span>
            <span class="text-white ml-2">{{ formatDate(league.registration_end) }}</span>
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
