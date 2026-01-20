<template>
  <div v-if="mapName" class="bg-gray-900 p-6 rounded">
    <p class="text-3xl font-bold text-center mb-4">{{ mapName }}</p>

    <div v-if="mapImage" class="flex justify-center mb-6">
      <img
        :src="`/assets/battle-plans/${mapImage}`"
        :alt="mapName"
        class="max-w-full h-auto rounded border-2 border-squig-yellow"
      />
    </div>

    <!-- Battle Plan Details -->
    <div v-if="battlePlan" class="mt-6 space-y-4">
      <div v-if="battlePlan.objectives" class="border-t border-gray-700 pt-4">
        <h3 class="text-lg font-semibold text-squig-yellow mb-2">Objectives</h3>
        <div v-if="battlePlan.objective_types && battlePlan.objective_types.length > 0" class="mb-3 flex flex-wrap gap-2">
          <span v-for="type in battlePlan.objective_types" :key="type"
            :class="getObjectiveClass(type)"
            class="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium">
            <span :class="getObjectiveDotClass(type)" class="w-3 h-3 rounded-full mr-2"></span>
            {{ type }}
          </span>
        </div>
        <p class="text-gray-300">{{ battlePlan.objectives }}</p>
      </div>

      <div v-if="battlePlan.scoring" class="border-t border-gray-700 pt-4">
        <h3 class="text-lg font-semibold text-squig-yellow mb-2">Scoring</h3>
        <p class="text-gray-300 whitespace-pre-wrap">{{ battlePlan.scoring }}</p>
      </div>

      <div v-if="battlePlan.underdog_ability" class="border-t border-gray-700 pt-4">
        <h3 class="text-lg font-semibold text-squig-yellow mb-2">Underdog Ability</h3>
        <p class="text-gray-300">{{ battlePlan.underdog_ability }}</p>
      </div>
    </div>
  </div>
  <div v-else class="text-gray-500">No map selected</div>
</template>

<script setup>
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
