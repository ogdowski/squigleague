<template>
  <div v-if="mapName" class="bg-gray-900 p-4 md:p-6 rounded">
    <p class="text-2xl md:text-3xl font-bold text-center mb-4">{{ mapName }}</p>

    <div v-if="mapImage" class="flex justify-center mb-6">
      <div class="relative cursor-pointer group" @click="showFullscreen = true">
        <img
          :src="`/assets/battle-plans/${mapImage}`"
          :alt="mapName"
          class="max-w-full h-auto rounded border-2 border-squig-yellow"
        />
        <!-- Zoom icon in bottom right corner -->
        <div class="absolute bottom-2 right-2 p-1.5 bg-black/60 rounded-full text-white">
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0zM10 7v3m0 0v3m0-3h3m-3 0H7" />
          </svg>
        </div>
      </div>
    </div>

    <!-- Battle Plan Details -->
    <div v-if="battlePlan" class="mt-4 md:mt-6 space-y-4">
      <div v-if="battlePlan.objectives" class="border-t border-gray-700 pt-4">
        <h3 class="text-base md:text-lg font-semibold text-squig-yellow mb-2">Objectives</h3>
        <div v-if="battlePlan.objective_types && battlePlan.objective_types.length > 0" class="mb-3 flex flex-wrap gap-2">
          <span v-for="type in battlePlan.objective_types" :key="type"
            :class="getObjectiveClass(type)"
            class="inline-flex items-center px-2 md:px-3 py-1 rounded-full text-xs md:text-sm font-medium">
            <span :class="getObjectiveDotClass(type)" class="w-2 h-2 md:w-3 md:h-3 rounded-full mr-1.5 md:mr-2"></span>
            {{ type }}
          </span>
        </div>
        <p class="text-gray-300 text-sm md:text-base">{{ battlePlan.objectives }}</p>
      </div>

      <div v-if="battlePlan.scoring" class="border-t border-gray-700 pt-4">
        <h3 class="text-base md:text-lg font-semibold text-squig-yellow mb-2">Scoring</h3>
        <p class="text-gray-300 text-sm md:text-base whitespace-pre-wrap">{{ battlePlan.scoring }}</p>
      </div>

      <div v-if="battlePlan.underdog_ability" class="border-t border-gray-700 pt-4">
        <h3 class="text-base md:text-lg font-semibold text-squig-yellow mb-2">Underdog Ability</h3>
        <p class="text-gray-300 text-sm md:text-base">{{ battlePlan.underdog_ability }}</p>
      </div>
    </div>
  </div>
  <div v-else class="text-gray-500">{{ t('matchDetail.noMapSelected') }}</div>

  <!-- Fullscreen Map Modal -->
  <Teleport to="body">
    <div
      v-if="showFullscreen && mapImage"
      class="fixed inset-0 bg-black/95 z-50 flex flex-col"
      @click="showFullscreen = false"
    >
      <!-- Header -->
      <div class="flex items-center justify-between p-4 text-white">
        <h3 class="text-lg font-bold">{{ mapName }}</h3>
        <button
          @click="showFullscreen = false"
          class="p-2 hover:bg-white/10 rounded-full transition-colors"
        >
          <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      </div>
      <!-- Zoomable image container -->
      <div
        class="flex-1 overflow-auto flex items-center justify-center p-4"
        @click.stop
      >
        <img
          :src="`/assets/battle-plans/${mapImage}`"
          :alt="mapName"
          class="max-w-none w-auto h-auto touch-pinch-zoom"
          :style="{ maxHeight: 'none', transform: `scale(${zoomLevel})`, transformOrigin: 'center center' }"
        />
      </div>
      <!-- Zoom controls -->
      <div class="flex items-center justify-center gap-4 p-4">
        <button
          @click.stop="zoomLevel = Math.max(0.5, zoomLevel - 0.25)"
          class="p-3 bg-white/10 hover:bg-white/20 rounded-full transition-colors"
        >
          <svg class="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20 12H4" />
          </svg>
        </button>
        <span class="text-white text-sm min-w-16 text-center">{{ Math.round(zoomLevel * 100) }}%</span>
        <button
          @click.stop="zoomLevel = Math.min(3, zoomLevel + 0.25)"
          class="p-3 bg-white/10 hover:bg-white/20 rounded-full transition-colors"
        >
          <svg class="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
          </svg>
        </button>
        <button
          @click.stop="zoomLevel = 1"
          class="px-3 py-2 bg-white/10 hover:bg-white/20 rounded-lg text-white text-sm transition-colors"
        >
          Reset
        </button>
      </div>
    </div>
  </Teleport>
</template>

<script setup>
import { ref } from 'vue'
import { useI18n } from 'vue-i18n'

const { t } = useI18n()

defineProps({
  mapName: {
    type: String,
    default: null,
  },
  mapImage: {
    type: String,
    default: null,
  },
  battlePlan: {
    type: Object,
    default: null,
  },
})

const showFullscreen = ref(false)
const zoomLevel = ref(1)

const getObjectiveClass = (type) => {
  const colors = {
    'Gnarlroot': 'bg-red-900/50 text-red-200 border border-red-700',
    'Oakenbrow': 'bg-green-900/50 text-green-200 border border-green-700',
    'Heartwood': 'bg-blue-900/50 text-blue-200 border border-blue-700',
    'Winterleaf': 'bg-purple-900/50 text-purple-200 border border-purple-700'
  }
  return colors[type] || 'bg-gray-900/50 text-gray-200 border border-gray-700'
}

const getObjectiveDotClass = (type) => {
  const colors = {
    'Gnarlroot': 'bg-red-500',
    'Oakenbrow': 'bg-green-500',
    'Heartwood': 'bg-blue-500',
    'Winterleaf': 'bg-purple-500'
  }
  return colors[type] || 'bg-gray-500'
}
</script>
