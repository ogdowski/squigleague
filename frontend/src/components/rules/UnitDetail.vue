<template>
  <div>
    <!-- Two column layout -->
    <div class="flex gap-6">
      <!-- Left column - Battle Profile -->
      <div class="flex-shrink-0 w-44">
        <UnitStatCircle
          :move="unit.move"
          :health="unit.health"
          :save="unit.save"
          :control="unit.control"
          :ward="wardValue"
        />
        <!-- Battle Profile card (collapsible) -->
        <div class="card mt-3 overflow-hidden">
          <h4 class="text-xs font-bold text-gray-400 px-2 pt-2">Battle Profile</h4>
          <div class="px-2 pb-2 pt-1 space-y-1 text-sm">
            <div v-if="unit.unit_size" class="flex justify-between">
              <span class="text-gray-500">Unit Size</span>
              <span class="font-bold">{{ unit.unit_size }}</span>
            </div>
            <div v-if="unit.base_size" class="flex justify-between">
              <span class="text-gray-500">Base</span>
              <span class="font-bold text-xs whitespace-pre-line text-right">{{ unit.base_size }}</span>
            </div>
            <div class="flex justify-between">
              <span class="text-gray-500">Reinforced</span>
              <span :class="['font-bold', unit.can_be_reinforced ? 'text-green-400' : 'text-gray-500']">
                {{ unit.can_be_reinforced ? 'Yes' : 'No' }}
              </span>
            </div>
            <div v-if="unit.notes" class="pt-1">
              <p class="text-xs text-gray-400 italic whitespace-pre-wrap">{{ unit.notes }}</p>
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
              <tr v-if="meleeWeapons.length" class="border-b border-gray-600">
                <td colspan="7" class="py-1 text-xs text-gray-500 font-medium">{{ t('rules.meleeWeapons') }}</td>
              </tr>
              <tr v-for="weapon in meleeWeapons" :key="weapon.id" class="border-b border-gray-700/50">
                <td class="py-2 pr-4 font-medium">{{ weapon.name }}</td>
                <td class="py-2 px-2 text-center text-gray-500">-</td>
                <td class="py-2 px-2 text-center">{{ weapon.attacks }}</td>
                <td class="py-2 px-2 text-center">{{ weapon.hit }}</td>
                <td class="py-2 px-2 text-center">{{ weapon.wound }}</td>
                <td class="py-2 px-2 text-center">{{ weapon.rend || '-' }}</td>
                <td class="py-2 px-2 text-center">{{ weapon.damage }}</td>
              </tr>
              <tr v-if="rangedWeapons.length" class="border-b border-gray-600">
                <td colspan="7" class="py-1 text-xs text-gray-500 font-medium">{{ t('rules.rangedWeapons') }}</td>
              </tr>
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

      <!-- Abilities -->
      <div v-if="unit.abilities?.length" class="card">
        <h3 class="font-bold text-squig-yellow mb-4">{{ t('rules.abilities') }}</h3>
        <div class="space-y-3">
          <div
            v-for="ability in unit.abilities"
            :key="ability.id"
            class="bg-gray-700/50 rounded-lg overflow-hidden"
          >
            <!-- Phase indicator bar (using BSData color) -->
            <div
              :class="['px-3 py-1 text-xs font-medium', getColorBarClass(ability.color)]"
            >
              {{ ability.timing || getPhaseFromColor(ability.color) || ability.ability_type }}
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
              <p v-if="ability.declare" class="text-sm text-gray-400 mb-2 italic">{{ ability.declare }}</p>
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
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import UnitStatCircle from './UnitStatCircle.vue'

const { t } = useI18n()


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

// Extract ward value from keywords (e.g., "WARD (5+)" or "WARD (6+)")
const wardValue = computed(() => {
  const keywordsList = Array.isArray(props.unit.keywords) ? props.unit.keywords : []
  for (const keyword of keywordsList) {
    const wardMatch = keyword.match(/Ward\s*\((\d+\+?)\)/i)
    if (wardMatch) return wardMatch[1]
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
    'spell': 'bg-purple-900/50 text-purple-300',
    'prayer': 'bg-amber-900/50 text-amber-300',
    'command': 'bg-cyan-900/50 text-cyan-300',
  }
  return classes[type?.toLowerCase()] || 'bg-gray-700 text-gray-300'
}

// Map BSData color to phase name (fallback when timing is null)
const getPhaseFromColor = (color) => {
  const phases = {
    'Yellow': 'Hero Phase',
    'Red': 'Combat Phase',
    'Blue': 'Shooting Phase',
    'Green': 'Movement Phase',
    'Purple': 'End Phase',
    'Orange': 'Charge Phase',
    'Gray': 'Passive',
    'Grey': 'Passive',
    'Black': 'Passive',
    'Teal': 'Deployment',
    'Cyan': 'Any Phase',
  }
  return phases[color] || null
}

// Map BSData color attribute to Tailwind classes
const getColorBarClass = (color) => {
  const classes = {
    'Yellow': 'bg-yellow-600 text-yellow-100',
    'Red': 'bg-red-700 text-red-100',
    'Blue': 'bg-blue-600 text-blue-100',
    'Green': 'bg-green-700 text-green-100',
    'Purple': 'bg-purple-700 text-purple-100',
    'Orange': 'bg-orange-600 text-orange-100',
    'Gray': 'bg-gray-600 text-gray-200',
    'Grey': 'bg-gray-600 text-gray-200',
    'Black': 'bg-gray-800 text-gray-300',
    'White': 'bg-gray-200 text-gray-800',
    'Teal': 'bg-teal-700 text-teal-100',
    'Cyan': 'bg-cyan-700 text-cyan-100',
  }
  return classes[color] || 'bg-gray-700 text-gray-300'
}

// Keywords to show as tags
const unitKeywords = computed(() => {
  if (!props.unit.keywords) return []
  return Array.isArray(props.unit.keywords) ? props.unit.keywords : []
})
</script>
