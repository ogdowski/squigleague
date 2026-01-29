<template>
  <div>
    <!-- Desktop: side-by-side layout -->
    <div class="hidden lg:flex gap-6">
      <!-- Left column - Stat Circle + Battle Profile -->
      <div class="flex-shrink-0 w-44">
        <UnitStatCircle
          :move="unit.move"
          :health="unit.health"
          :save="unit.save"
          :control="unit.control"
          :ward="wardValue"
        />
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

      <!-- Right column -->
      <div class="flex-1 min-w-0 space-y-4">
        <!-- Header -->
        <div>
          <div class="flex items-start justify-between gap-4">
            <div class="min-w-0">
              <h2 class="text-2xl font-bold flex items-center gap-2">
                {{ unit.name }}
                <svg v-if="isUniqueHero" class="w-5 h-5 text-squig-yellow flex-shrink-0" viewBox="0 0 24 24" fill="currentColor">
                  <path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z"/>
                </svg>
              </h2>
              <p class="text-gray-400">{{ unit.faction_name }}</p>
            </div>
            <span class="text-2xl font-bold text-squig-yellow flex-shrink-0">{{ unit.points || '-' }} pts</span>
          </div>
          <div v-if="unitKeywords.length" class="flex flex-wrap gap-1 mt-2">
            <span v-for="keyword in unitKeywords" :key="keyword" class="text-xs bg-gray-700 text-gray-400 px-2 py-0.5 rounded">{{ keyword }}</span>
          </div>
        </div>

        <!-- Desktop weapons & abilities rendered below -->
        <template v-if="unit.weapons?.length">
          <div class="card">
            <h3 class="font-bold text-squig-yellow mb-3">{{ t('rules.weapons') }}</h3>
            <div class="space-y-3">
              <template v-if="meleeWeapons.length">
                <p class="text-xs text-gray-500 font-medium">{{ t('rules.meleeWeapons') }}</p>
                <div v-for="weapon in meleeWeapons" :key="weapon.id" class="bg-gray-700/50 rounded-lg p-3">
                  <h4 class="font-medium mb-1.5">{{ weapon.name }}</h4>
                  <div class="grid grid-cols-6 gap-1 text-center text-xs">
                    <div><span class="text-gray-500 block">Atk</span><span class="font-bold">{{ weapon.attacks }}</span></div>
                    <div><span class="text-gray-500 block">Hit</span><span class="font-bold">{{ weapon.hit }}</span></div>
                    <div><span class="text-gray-500 block">Wnd</span><span class="font-bold">{{ weapon.wound }}</span></div>
                    <div><span class="text-gray-500 block">Rnd</span><span class="font-bold">{{ weapon.rend || '-' }}</span></div>
                    <div><span class="text-gray-500 block">Dmg</span><span class="font-bold">{{ weapon.damage }}</span></div>
                    <div><span class="text-gray-500 block">Abi</span><span class="font-bold text-gray-400">{{ weapon.ability || '-' }}</span></div>
                  </div>
                </div>
              </template>
              <template v-if="rangedWeapons.length">
                <p class="text-xs text-gray-500 font-medium">{{ t('rules.rangedWeapons') }}</p>
                <div v-for="weapon in rangedWeapons" :key="weapon.id" class="bg-gray-700/50 rounded-lg p-3">
                  <div class="flex items-center justify-between mb-1.5">
                    <h4 class="font-medium">{{ weapon.name }}</h4>
                    <span class="text-xs text-gray-400">{{ formatRange(weapon.range) }}</span>
                  </div>
                  <div class="grid grid-cols-6 gap-1 text-center text-xs">
                    <div><span class="text-gray-500 block">Atk</span><span class="font-bold">{{ weapon.attacks }}</span></div>
                    <div><span class="text-gray-500 block">Hit</span><span class="font-bold">{{ weapon.hit }}</span></div>
                    <div><span class="text-gray-500 block">Wnd</span><span class="font-bold">{{ weapon.wound }}</span></div>
                    <div><span class="text-gray-500 block">Rnd</span><span class="font-bold">{{ weapon.rend || '-' }}</span></div>
                    <div><span class="text-gray-500 block">Dmg</span><span class="font-bold">{{ weapon.damage }}</span></div>
                    <div><span class="text-gray-500 block">Abi</span><span class="font-bold text-gray-400">{{ weapon.ability || '-' }}</span></div>
                  </div>
                </div>
              </template>
            </div>
          </div>
        </template>

        <template v-if="unit.abilities?.length">
          <div class="card">
            <h3 class="font-bold text-squig-yellow mb-3">{{ t('rules.abilities') }}</h3>
            <div class="space-y-3">
              <div v-for="ability in unit.abilities" :key="ability.id" class="bg-gray-700/50 rounded-lg overflow-hidden">
                <div :class="['px-3 py-1 text-xs font-medium', getColorBarClass(ability.color)]">{{ ability.timing || getPhaseFromColor(ability.color) || ability.ability_type }}</div>
                <div class="p-3">
                  <div class="flex items-start justify-between mb-1"><h4 class="font-bold">{{ ability.name }}</h4><span v-if="ability.ability_type" :class="['text-xs px-2 py-0.5 rounded flex-shrink-0 ml-2', getAbilityTypeClass(ability.ability_type)]">{{ ability.ability_type }}</span></div>
                  <p v-if="ability.declare" class="text-sm text-gray-400 mb-2 whitespace-pre-wrap"><span class="font-medium text-gray-300">Declare:</span> {{ ability.declare }}</p>
                  <p class="text-sm text-gray-300 whitespace-pre-wrap">{{ ability.effect }}</p>
                  <div v-if="ability.keywords?.length" class="flex flex-wrap gap-1 mt-2 pt-2 border-t border-gray-600/50"><span v-for="kw in ability.keywords" :key="kw" class="text-xs bg-gray-600/50 text-gray-400 px-2 py-0.5 rounded">{{ kw }}</span></div>
                </div>
              </div>
            </div>
          </div>
        </template>
      </div>
    </div>

    <!-- Mobile: stacked layout -->
    <div class="lg:hidden space-y-4">
      <!-- Name + Points -->
      <div>
        <h2 class="text-2xl font-bold">{{ unit.name }}</h2>
        <div class="flex items-center justify-between">
          <p class="text-gray-400">{{ unit.faction_name }}</p>
          <span class="text-lg font-bold text-squig-yellow flex items-center gap-1.5">
            <svg v-if="isUniqueHero" class="w-4 h-4" viewBox="0 0 24 24" fill="currentColor">
              <path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z"/>
            </svg>
            {{ unit.points || '-' }} pts
          </span>
        </div>
      </div>

      <!-- Keywords -->
      <div v-if="unitKeywords.length" class="flex flex-wrap gap-1">
        <span v-for="keyword in unitKeywords" :key="keyword" class="text-xs bg-gray-700 text-gray-400 px-2 py-0.5 rounded">{{ keyword }}</span>
      </div>

      <!-- Stats Table (mobile) -->
      <div class="card overflow-hidden">
        <table class="w-full text-sm">
          <thead>
            <tr class="text-gray-400 border-b border-gray-700">
              <th class="py-2 px-3 text-center">Move</th>
              <th class="py-2 px-3 text-center">Health</th>
              <th class="py-2 px-3 text-center">Save</th>
              <th class="py-2 px-3 text-center">Control</th>
              <th v-if="wardValue" class="py-2 px-3 text-center">Ward</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td class="py-2 px-3 text-center font-bold text-lg">{{ unit.move || '-' }}</td>
              <td class="py-2 px-3 text-center font-bold text-lg">{{ unit.health || '-' }}</td>
              <td class="py-2 px-3 text-center font-bold text-lg">{{ unit.save || '-' }}</td>
              <td class="py-2 px-3 text-center font-bold text-lg">{{ unit.control || '-' }}</td>
              <td v-if="wardValue" class="py-2 px-3 text-center font-bold text-lg text-purple-400">{{ wardValue }}</td>
            </tr>
          </tbody>
        </table>
        <div class="border-t border-gray-700 px-3 py-2 flex flex-wrap gap-x-4 gap-y-1 text-xs text-gray-500">
          <span v-if="unit.unit_size">Size: <span class="text-gray-300">{{ unit.unit_size }}</span></span>
          <span v-if="unit.base_size">Base: <span class="text-gray-300">{{ unit.base_size }}</span></span>
          <span>Reinforced: <span :class="unit.can_be_reinforced ? 'text-green-400' : 'text-gray-500'">{{ unit.can_be_reinforced ? 'Yes' : 'No' }}</span></span>
        </div>
        <div v-if="unit.notes" class="border-t border-gray-700 px-3 py-2">
          <p class="text-xs text-gray-400 italic whitespace-pre-wrap">{{ unit.notes }}</p>
        </div>
      </div>

    <!-- Weapons -->
    <div v-if="unit.weapons?.length" class="card">
      <h3 class="font-bold text-squig-yellow mb-3">{{ t('rules.weapons') }}</h3>
      <div class="space-y-3">
        <template v-if="meleeWeapons.length">
          <p class="text-xs text-gray-500 font-medium">{{ t('rules.meleeWeapons') }}</p>
          <div v-for="weapon in meleeWeapons" :key="weapon.id" class="bg-gray-700/50 rounded-lg p-3">
            <h4 class="font-medium mb-1.5">{{ weapon.name }}</h4>
            <div class="grid grid-cols-5 gap-1 text-center text-xs">
              <div><span class="text-gray-500 block">Atk</span><span class="font-bold">{{ weapon.attacks }}</span></div>
              <div><span class="text-gray-500 block">Hit</span><span class="font-bold">{{ weapon.hit }}</span></div>
              <div><span class="text-gray-500 block">Wnd</span><span class="font-bold">{{ weapon.wound }}</span></div>
              <div><span class="text-gray-500 block">Rnd</span><span class="font-bold">{{ weapon.rend || '-' }}</span></div>
              <div><span class="text-gray-500 block">Dmg</span><span class="font-bold">{{ weapon.damage }}</span></div>
            </div>
            <p v-if="weapon.ability && weapon.ability !== '-'" class="text-xs text-gray-400 mt-1.5"><span class="text-gray-500">Ability:</span> {{ weapon.ability }}</p>
          </div>
        </template>
        <template v-if="rangedWeapons.length">
          <p class="text-xs text-gray-500 font-medium">{{ t('rules.rangedWeapons') }}</p>
          <div v-for="weapon in rangedWeapons" :key="weapon.id" class="bg-gray-700/50 rounded-lg p-3">
            <div class="flex items-center justify-between mb-1.5">
              <h4 class="font-medium">{{ weapon.name }}</h4>
              <span class="text-sm font-bold text-white bg-gray-600/80 px-2 py-0.5 rounded">{{ formatRange(weapon.range) }}</span>
            </div>
            <div class="grid grid-cols-5 gap-1 text-center text-xs">
              <div><span class="text-gray-500 block">Atk</span><span class="font-bold">{{ weapon.attacks }}</span></div>
              <div><span class="text-gray-500 block">Hit</span><span class="font-bold">{{ weapon.hit }}</span></div>
              <div><span class="text-gray-500 block">Wnd</span><span class="font-bold">{{ weapon.wound }}</span></div>
              <div><span class="text-gray-500 block">Rnd</span><span class="font-bold">{{ weapon.rend || '-' }}</span></div>
              <div><span class="text-gray-500 block">Dmg</span><span class="font-bold">{{ weapon.damage }}</span></div>
            </div>
            <p v-if="weapon.ability && weapon.ability !== '-'" class="text-xs text-gray-400 mt-1.5"><span class="text-gray-500">Ability:</span> {{ weapon.ability }}</p>
          </div>
        </template>
      </div>
    </div>

    <!-- Abilities -->
    <div v-if="unit.abilities?.length" class="card">
      <h3 class="font-bold text-squig-yellow mb-3">{{ t('rules.abilities') }}</h3>
      <div class="space-y-3">
        <div
          v-for="ability in unit.abilities"
          :key="ability.id"
          class="bg-gray-700/50 rounded-lg overflow-hidden"
        >
          <div
            :class="['px-3 py-1 text-xs font-medium', getColorBarClass(ability.color)]"
          >
            {{ ability.timing || getPhaseFromColor(ability.color) || ability.ability_type }}
          </div>
          <div class="p-3">
            <div class="flex items-start justify-between mb-1">
              <h4 class="font-bold">{{ ability.name }}</h4>
              <span
                v-if="ability.ability_type"
                :class="['text-xs px-2 py-0.5 rounded flex-shrink-0 ml-2', getAbilityTypeClass(ability.ability_type)]"
              >
                {{ ability.ability_type }}
              </span>
            </div>
            <p v-if="ability.declare" class="text-sm text-gray-400 mb-2 whitespace-pre-wrap"><span class="font-medium text-gray-300">Declare:</span> {{ ability.declare }}</p>
            <p class="text-sm text-gray-300 whitespace-pre-wrap">{{ ability.effect }}</p>
            <div v-if="ability.keywords?.length" class="flex flex-wrap gap-1 mt-2 pt-2 border-t border-gray-600/50">
              <span v-for="kw in ability.keywords" :key="kw" class="text-xs bg-gray-600/50 text-gray-400 px-2 py-0.5 rounded">{{ kw }}</span>
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

const isUniqueHero = computed(() => {
  const keywordsList = Array.isArray(props.unit.keywords)
    ? props.unit.keywords.map(keyword => keyword.toUpperCase())
    : []
  return keywordsList.includes('UNIQUE') && keywordsList.some(keyword => keyword.includes('HERO'))
})

const meleeWeapons = computed(() => {
  return props.unit.weapons?.filter(weapon => weapon.weapon_type === 'melee') || []
})

const rangedWeapons = computed(() => {
  return props.unit.weapons?.filter(weapon => weapon.weapon_type === 'ranged') || []
})

const wardValue = computed(() => {
  const keywordsList = Array.isArray(props.unit.keywords) ? props.unit.keywords : []
  for (const keyword of keywordsList) {
    const wardMatch = keyword.match(/Ward\s*\((\d+\+?)\)/i)
    if (wardMatch) return wardMatch[1]
  }
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
    'Black': 'Deployment',
    'Cyan': 'Any Phase',
  }
  return phases[color] || null
}

const getColorBarClass = (color) => {
  const classes = {
    'Yellow': 'bg-yellow-800/60 text-yellow-200',
    'Red': 'bg-red-900/60 text-red-200',
    'Blue': 'bg-blue-800/60 text-blue-200',
    'Green': 'bg-gray-700/60 text-gray-300',
    'Purple': 'bg-purple-900/60 text-purple-200',
    'Orange': 'bg-orange-800/60 text-orange-200',
    'Gray': 'bg-green-900/60 text-green-200',
    'Grey': 'bg-green-900/60 text-green-200',
    'Black': 'bg-gray-800/60 text-gray-300',
    'White': 'bg-gray-300/40 text-gray-800',
    'Cyan': 'bg-cyan-900/60 text-cyan-200',
  }
  return classes[color] || 'bg-gray-700/60 text-gray-300'
}

const unitKeywords = computed(() => {
  if (!props.unit.keywords) return []
  return Array.isArray(props.unit.keywords) ? props.unit.keywords : []
})
</script>
