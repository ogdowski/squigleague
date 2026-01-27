<template>
  <div>
    <!-- Two column layout -->
    <div class="flex gap-6">
      <!-- Left column - Battle Profile -->
      <div class="flex-shrink-0 w-32">
        <UnitStatCircle
          :move="unit.move"
          :health="unit.health"
          :save="unit.save"
          :control="unit.control"
          :ward="wardValue"
        />
        <!-- Battle Profile card (collapsible) -->
        <div class="card mt-4 overflow-hidden">
          <button
            @click="showBattleProfile = !showBattleProfile"
            class="w-full flex items-center justify-between p-3 text-left"
          >
            <h4 class="text-xs font-bold text-gray-400">Battle Profile</h4>
            <svg
              :class="['w-4 h-4 text-gray-500 transition-transform', showBattleProfile ? 'rotate-180' : '']"
              fill="none" stroke="currentColor" viewBox="0 0 24 24"
            >
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
            </svg>
          </button>
          <div v-if="showBattleProfile" class="px-3 pb-3 space-y-1 text-sm">
            <div class="flex justify-between">
              <span class="text-gray-500">Move</span>
              <span class="font-bold">{{ unit.move || '-' }}</span>
            </div>
            <div class="flex justify-between">
              <span class="text-gray-500">Health</span>
              <span class="font-bold">{{ unit.health || '-' }}</span>
            </div>
            <div class="flex justify-between">
              <span class="text-gray-500">Save</span>
              <span class="font-bold text-squig-yellow">{{ unit.save || '-' }}</span>
            </div>
            <div class="flex justify-between">
              <span class="text-gray-500">Control</span>
              <span class="font-bold">{{ unit.control || '-' }}</span>
            </div>
            <div v-if="wardValue" class="flex justify-between">
              <span class="text-gray-500">Ward</span>
              <span class="font-bold text-purple-400">{{ wardValue }}</span>
            </div>
          </div>
        </div>
      </div>

      <!-- Right column - Name, Keywords, Weapons, Abilities -->
      <div class="flex-1 min-w-0 space-y-6">
        <!-- Header -->
        <div>
          <div class="flex items-start justify-between gap-4">
            <div class="min-w-0">
              <h2 class="text-2xl font-bold">{{ unit.name }}</h2>
              <p class="text-gray-400">{{ unit.faction_name }}</p>
              <!-- Keywords under name -->
              <div v-if="unitKeywords.length" class="flex flex-wrap gap-1 mt-2">
                <span
                  v-for="keyword in unitKeywords"
                  :key="keyword"
                  class="text-xs bg-gray-700 text-gray-400 px-2 py-0.5 rounded"
                >
                  {{ keyword }}
                </span>
              </div>
            </div>
            <span class="text-2xl font-bold text-squig-yellow flex-shrink-0">{{ unit.points || '-' }} pts</span>
          </div>
        </div>
      <!-- Weapons -->
      <div v-if="unit.weapons?.length" class="card">
        <h3 class="font-bold text-squig-yellow mb-4">{{ t('rules.weapons') }}</h3>

        <!-- Melee Weapons -->
        <div v-if="meleeWeapons.length" class="mb-4">
          <h4 class="text-sm text-gray-400 mb-2">{{ t('rules.meleeWeapons') }}</h4>
          <div class="overflow-x-auto">
            <table class="w-full text-sm">
              <thead>
                <tr class="text-left text-gray-400 border-b border-gray-700">
                  <th class="py-2 pr-4">{{ t('rules.weapon') }}</th>
                  <th class="py-2 px-2 text-center">Atk</th>
                  <th class="py-2 px-2 text-center">Hit</th>
                  <th class="py-2 px-2 text-center">Wnd</th>
                  <th class="py-2 px-2 text-center">Rnd</th>
                  <th class="py-2 px-2 text-center">Dmg</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="weapon in meleeWeapons" :key="weapon.id" class="border-b border-gray-700/50">
                  <td class="py-2 pr-4 font-medium">{{ weapon.name }}</td>
                  <td class="py-2 px-2 text-center">{{ weapon.attacks }}</td>
                  <td class="py-2 px-2 text-center">{{ weapon.hit }}</td>
                  <td class="py-2 px-2 text-center">{{ weapon.wound }}</td>
                  <td class="py-2 px-2 text-center">{{ weapon.rend || '-' }}</td>
                  <td class="py-2 px-2 text-center">{{ weapon.damage }}</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        <!-- Ranged Weapons -->
        <div v-if="rangedWeapons.length">
          <h4 class="text-sm text-gray-400 mb-2">{{ t('rules.rangedWeapons') }}</h4>
          <div class="overflow-x-auto">
            <table class="w-full text-sm">
              <thead>
                <tr class="text-left text-gray-400 border-b border-gray-700">
                  <th class="py-2 pr-4">{{ t('rules.weapon') }}</th>
                  <th class="py-2 px-2 text-center">Rng</th>
                  <th class="py-2 px-2 text-center">Atk</th>
                  <th class="py-2 px-2 text-center">Hit</th>
                  <th class="py-2 px-2 text-center">Wnd</th>
                  <th class="py-2 px-2 text-center">Rnd</th>
                  <th class="py-2 px-2 text-center">Dmg</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="weapon in rangedWeapons" :key="weapon.id" class="border-b border-gray-700/50">
                  <td class="py-2 pr-4 font-medium">{{ weapon.name }}</td>
                  <td class="py-2 px-2 text-center">{{ formatRange(weapon.range) }}</td>
                  <td class="py-2 px-2 text-center">{{ weapon.attacks }}</td>
                  <td class="py-2 px-2 text-center">{{ weapon.hit }}</td>
                  <td class="py-2 px-2 text-center">{{ weapon.wound }}</td>
                  <td class="py-2 px-2 text-center">{{ weapon.rend || '-' }}</td>
                  <td class="py-2 px-2 text-center">{{ weapon.damage }}</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>

      <!-- Abilities -->
      <div v-if="unit.abilities?.length" class="card">
        <h3 class="font-bold text-squig-yellow mb-4">{{ t('rules.abilities') }}</h3>
        <div class="space-y-3">
          <div
            v-for="ability in unit.abilities"
            :key="ability.id"
            class="bg-gray-700/50 rounded-lg overflow-hidden"
          >
            <!-- Phase indicator bar -->
            <div
              :class="['px-3 py-1 text-xs font-medium', getPhaseBarClass(ability)]"
            >
              {{ getPhaseLabel(ability) }}
            </div>
            <!-- Ability content -->
            <div class="p-4">
              <div class="flex items-start justify-between mb-2">
                <h4 class="font-bold">{{ ability.name }}</h4>
                <span
                  v-if="ability.ability_type"
                  :class="['text-xs px-2 py-0.5 rounded', getAbilityTypeClass(ability.ability_type)]"
                >
                  {{ ability.ability_type }}
                </span>
              </div>
              <p class="text-sm text-gray-300 whitespace-pre-wrap">{{ ability.effect }}</p>
            </div>
          </div>
        </div>
      </div>

      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useI18n } from 'vue-i18n'
import UnitStatCircle from './UnitStatCircle.vue'

const { t } = useI18n()

const showBattleProfile = ref(true)

const props = defineProps({
  unit: {
    type: Object,
    required: true
  }
})

const meleeWeapons = computed(() => {
  return props.unit.weapons?.filter(weapon => weapon.weapon_type === 'melee') || []
})

const rangedWeapons = computed(() => {
  return props.unit.weapons?.filter(weapon => weapon.weapon_type === 'ranged') || []
})

// Extract ward value from keywords (e.g., "Ward (5+)" or "Ward (6+)")
const wardValue = computed(() => {
  const keywords = props.unit.keywords || ''
  const wardMatch = keywords.match(/Ward\s*\((\d+\+?)\)/i)
  if (wardMatch) {
    return wardMatch[1]
  }
  // Also check abilities for ward
  const abilities = props.unit.abilities || []
  for (const ability of abilities) {
    if (ability.name?.toLowerCase().includes('ward')) {
      const match = ability.name.match(/(\d+\+?)/)
      if (match) return match[1]
    }
  }
  return null
})

const formatRange = (range) => {
  if (!range) return '-'
  // Remove trailing " if already present, then add it
  const cleaned = range.replace(/"+$/, '').replace(/^"+/, '')
  return cleaned + '"'
}

const getAbilityTypeClass = (type) => {
  const classes = {
    'passive': 'bg-blue-900/50 text-blue-300',
    'activated': 'bg-green-900/50 text-green-300',
    'reaction': 'bg-orange-900/50 text-orange-300',
  }
  return classes[type?.toLowerCase()] || 'bg-gray-700 text-gray-300'
}

// Detect phase from ability effect text or type
const detectPhase = (ability) => {
  const text = ((ability.effect || '') + ' ' + (ability.name || '')).toLowerCase()
  const type = (ability.ability_type || '').toLowerCase()

  if (type === 'passive' || text.includes('passive')) return 'passive'
  if (text.includes('hero phase')) return 'hero'
  if (text.includes('combat phase') || text.includes('fight phase')) return 'combat'
  if (text.includes('shooting phase')) return 'shooting'
  if (text.includes('movement phase') || text.includes('move phase')) return 'movement'
  if (text.includes('charge phase')) return 'charge'
  if (text.includes('end phase') || text.includes('end of')) return 'end'
  if (text.includes('deployment') || text.includes('deploy')) return 'deployment'
  if (text.includes('start of') || text.includes('beginning of')) return 'start'
  if (type === 'reaction') return 'reaction'

  return 'passive'
}

const getPhaseBarClass = (ability) => {
  const phase = detectPhase(ability)
  const classes = {
    'hero': 'bg-yellow-600 text-yellow-100',
    'combat': 'bg-red-700 text-red-100',
    'shooting': 'bg-blue-600 text-blue-100',
    'movement': 'bg-gray-600 text-gray-200',
    'charge': 'bg-orange-600 text-orange-100',
    'end': 'bg-purple-700 text-purple-100',
    'deployment': 'bg-gray-900 text-gray-300',
    'start': 'bg-green-700 text-green-100',
    'reaction': 'bg-orange-500 text-orange-100',
    'passive': 'bg-gray-700 text-gray-300',
  }
  return classes[phase] || classes['passive']
}

const getPhaseLabel = (ability) => {
  const phase = detectPhase(ability)
  const labels = {
    'hero': 'Hero Phase',
    'combat': 'Combat Phase',
    'shooting': 'Shooting Phase',
    'movement': 'Movement Phase',
    'charge': 'Charge Phase',
    'end': 'End Phase',
    'deployment': 'Deployment',
    'start': 'Start of Turn',
    'reaction': 'Reaction',
    'passive': 'Passive',
  }
  return labels[phase] || 'Passive'
}

// Keywords to show as tags
const unitKeywords = computed(() => {
  if (!props.unit.keywords) return []
  return props.unit.keywords.split(',').map(k => k.trim()).filter(k => k)
})
</script>
