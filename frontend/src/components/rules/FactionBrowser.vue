<template>
  <div class="space-y-8">
    <div v-for="allianceName in allianceOrder" :key="allianceName">
      <!-- Grand Alliance header -->
      <div class="flex items-center gap-3 mb-4">
        <h2 :class="['text-xl font-bold', getAllianceTextColor(allianceName)]">
          {{ allianceName }}
        </h2>
        <div class="flex-1 h-px" :class="getAllianceBorderColor(allianceName)"></div>
      </div>

      <!-- Factions grid -->
      <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
        <div
          v-for="faction in getFactionsByAlliance(allianceName)"
          :key="faction.id"
          @click="$emit('selectFaction', faction.id)"
          class="card hover:bg-gray-700 cursor-pointer transition-colors group"
        >
          <h3 class="font-bold text-lg group-hover:text-squig-yellow transition-colors">
            {{ faction.name }}
          </h3>
        </div>
      </div>
    </div>

    <div v-if="factions.length === 0" class="text-center py-8 text-gray-400">
      {{ t('rules.noFactionsFound') }}
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'

const { t } = useI18n()

const props = defineProps({
  grandAlliances: {
    type: Array,
    required: true
  },
  factions: {
    type: Array,
    required: true
  }
})

defineEmits(['selectFaction'])

const allianceOrder = ['Order', 'Chaos', 'Death', 'Destruction']

const getFactionsByAlliance = (allianceName) => {
  return props.factions.filter(faction => faction.grand_alliance === allianceName)
}

const hasFactionsInAlliance = (allianceName) => {
  return props.factions.some(faction => faction.grand_alliance === allianceName)
}

const getAllianceTextColor = (name) => {
  const colors = {
    'Order': 'text-blue-400',
    'Chaos': 'text-red-400',
    'Death': 'text-purple-400',
    'Destruction': 'text-green-400',
  }
  return colors[name] || 'text-gray-400'
}

const getAllianceBorderColor = (name) => {
  const colors = {
    'Order': 'bg-blue-400/30',
    'Chaos': 'bg-red-400/30',
    'Death': 'bg-purple-400/30',
    'Destruction': 'bg-green-400/30',
  }
  return colors[name] || 'bg-gray-400/30'
}
</script>
