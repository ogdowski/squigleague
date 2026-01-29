<template>
  <div>
    <!-- Faction header -->
    <div class="mb-6">
      <h2 class="text-2xl font-bold">{{ faction.name }}</h2>
      <p class="text-gray-400">{{ faction.grand_alliance }}</p>
    </div>

    <!-- Loading all data -->
    <div v-if="initialLoading" class="flex justify-center py-12">
      <div class="w-10 h-10 border-4 border-squig-yellow border-t-transparent rounded-full animate-spin"></div>
    </div>

    <div v-else class="space-y-4">
      <!-- Battle Traits -->
      <CollapsibleSection
        v-if="sectionData.battle_traits?.length"
        :title="t('rules.battleTraits')"
        :count="sectionData.battle_traits.length"
        :expanded="expandedSections.has('battle_traits')"
        @toggle="toggleSection('battle_traits')"
      >
        <div class="grid grid-cols-1 md:grid-cols-2 gap-3">
          <div
            v-for="trait in sectionData.battle_traits"
            :key="trait.id"
            class="bg-gray-700/50 rounded-lg p-4"
          >
            <h4 class="font-bold text-squig-yellow mb-2">{{ trait.name }}</h4>
            <p class="text-sm text-gray-300 whitespace-pre-wrap">{{ trait.effect }}</p>
          </div>
        </div>
      </CollapsibleSection>

      <!-- Heroic Traits -->
      <CollapsibleSection
        v-if="sectionData.heroic_traits?.length"
        :title="t('rules.heroicTraits')"
        :count="sectionData.heroic_traits.length"
        :expanded="expandedSections.has('heroic_traits')"
        @toggle="toggleSection('heroic_traits')"
      >
        <div class="grid grid-cols-1 md:grid-cols-2 gap-3">
          <div
            v-for="trait in sectionData.heroic_traits"
            :key="trait.id"
            class="bg-gray-700/50 rounded-lg p-4"
          >
            <h4 class="font-bold text-squig-yellow mb-2">{{ trait.name }}</h4>
            <p class="text-sm text-gray-300 whitespace-pre-wrap">{{ trait.effect }}</p>
          </div>
        </div>
      </CollapsibleSection>

      <!-- Artefacts -->
      <CollapsibleSection
        v-if="sectionData.artefacts?.length"
        :title="t('rules.artefacts')"
        :count="sectionData.artefacts.length"
        :expanded="expandedSections.has('artefacts')"
        @toggle="toggleSection('artefacts')"
      >
        <div class="grid grid-cols-1 md:grid-cols-2 gap-3">
          <div
            v-for="artefact in sectionData.artefacts"
            :key="artefact.id"
            class="bg-gray-700/50 rounded-lg p-4"
          >
            <h4 class="font-bold text-squig-yellow mb-2">{{ artefact.name }}</h4>
            <p class="text-sm text-gray-300 whitespace-pre-wrap">{{ artefact.effect }}</p>
          </div>
        </div>
      </CollapsibleSection>

      <!-- Units (grouped by type) - always visible, not collapsible -->
      <div v-if="sectionData.units?.length" class="card">
        <div class="flex items-center justify-between mb-4">
          <h3 class="font-bold text-squig-yellow">{{ t('rules.units') }}</h3>
          <span class="text-sm text-gray-400">{{ sectionData.units.length }}</span>
        </div>
        <div class="space-y-6">
          <div v-for="group in groupedUnits" :key="group.name">
            <h4 class="text-sm font-medium text-gray-400 mb-3">{{ group.name }}</h4>
            <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
              <div
                v-for="unit in group.units"
                :key="unit.id"
                @click="$emit('selectUnit', unit.id, unit.name)"
                class="bg-gray-700/50 rounded-lg p-4 cursor-pointer hover:bg-gray-600/50 transition-colors"
              >
                <div class="flex items-start justify-between">
                  <h4 class="font-bold">{{ unit.name }}</h4>
                  <span class="text-squig-yellow font-bold text-sm">{{ unit.points || '-' }} pts</span>
                </div>
                <div class="flex gap-3 mt-2 text-xs text-gray-400">
                  <span v-if="unit.move">M: {{ unit.move }}</span>
                  <span v-if="unit.health">H: {{ unit.health }}</span>
                  <span v-if="unit.save">Sv: {{ unit.save }}</span>
                  <span v-if="unit.control">C: {{ unit.control }}</span>
                </div>
                <div v-if="unit.keywords" class="flex flex-wrap gap-1 mt-2">
                  <span
                    v-for="keyword in getMainKeywords(unit.keywords)"
                    :key="keyword"
                    class="text-[10px] bg-gray-600/50 text-gray-400 px-1.5 py-0.5 rounded"
                  >
                    {{ keyword }}
                  </span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Spell Lores -->
      <CollapsibleSection
        v-if="sectionData.spell_lores?.length"
        :title="t('rules.spellLores')"
        :count="sectionData.spell_lores.length"
        :expanded="expandedSections.has('spell_lores')"
        @toggle="toggleSection('spell_lores')"
      >
        <div class="space-y-4">
          <div v-for="lore in sectionData.spell_lores" :key="lore.id" class="bg-gray-700/50 rounded-lg p-4">
            <h4 class="font-bold text-purple-400 mb-3">{{ lore.name }}</h4>
            <div class="space-y-3">
              <div
                v-for="spell in lore.spells"
                :key="spell.id"
                class="bg-gray-800/50 rounded p-3"
              >
                <div class="flex items-start justify-between mb-1">
                  <h5 class="font-medium text-squig-yellow">{{ spell.name }}</h5>
                  <span v-if="spell.casting_value" class="text-xs bg-purple-900/50 text-purple-300 px-2 py-0.5 rounded">
                    {{ spell.casting_value }}+
                  </span>
                </div>
                <p class="text-sm text-gray-300 whitespace-pre-wrap">{{ spell.effect }}</p>
              </div>
            </div>
          </div>
        </div>
      </CollapsibleSection>

      <!-- Manifestation Lores -->
      <CollapsibleSection
        v-if="sectionData.manifestation_lores?.length"
        :title="t('rules.manifestationLores')"
        :count="sectionData.manifestation_lores.length"
        :expanded="expandedSections.has('manifestation_lores')"
        @toggle="toggleSection('manifestation_lores')"
      >
        <div class="space-y-4">
          <div v-for="lore in sectionData.manifestation_lores" :key="lore.id" class="bg-gray-700/50 rounded-lg p-4">
            <h4 class="font-bold text-cyan-400 mb-3">{{ lore.name }}</h4>
            <div class="space-y-3">
              <div
                v-for="manifestation in lore.manifestations"
                :key="manifestation.id"
                class="bg-gray-800/50 rounded p-3"
              >
                <div class="flex items-start justify-between mb-1">
                  <h5 class="font-medium text-squig-yellow">{{ manifestation.name }}</h5>
                  <span v-if="manifestation.points" class="text-sm text-squig-yellow">
                    {{ manifestation.points }} pts
                  </span>
                </div>
                <div v-if="manifestation.move || manifestation.health || manifestation.save" class="flex gap-3 mb-2 text-xs text-gray-400">
                  <span v-if="manifestation.move">M: {{ manifestation.move }}</span>
                  <span v-if="manifestation.health">H: {{ manifestation.health }}</span>
                  <span v-if="manifestation.save">Sv: {{ manifestation.save }}</span>
                </div>
                <p v-if="manifestation.effect" class="text-sm text-gray-300 whitespace-pre-wrap">{{ manifestation.effect }}</p>
              </div>
            </div>
          </div>
        </div>
      </CollapsibleSection>

      <!-- Armies of Renown -->
      <CollapsibleSection
        v-if="sectionData.armies_of_renown?.length"
        :title="t('rules.armiesOfRenown')"
        :count="sectionData.armies_of_renown.length"
        :expanded="expandedSections.has('armies_of_renown')"
        @toggle="toggleSection('armies_of_renown')"
      >
        <div class="space-y-4">
          <div v-for="aor in sectionData.armies_of_renown" :key="aor.id" class="bg-gray-700/50 rounded-lg p-4">
            <h4 class="font-bold text-squig-yellow mb-2">{{ aor.name }}</h4>
            <p v-if="aor.description" class="text-sm text-gray-300 whitespace-pre-wrap mb-3">{{ aor.description }}</p>
            <div v-if="aor.battle_traits?.length" class="space-y-2">
              <h5 class="text-sm font-medium text-gray-400">{{ t('rules.battleTraits') }}:</h5>
              <div
                v-for="trait in aor.battle_traits"
                :key="trait.id"
                class="bg-gray-800/50 rounded p-3"
              >
                <h6 class="font-medium mb-1">{{ trait.name }}</h6>
                <p class="text-sm text-gray-300 whitespace-pre-wrap">{{ trait.effect }}</p>
              </div>
            </div>
          </div>
        </div>
      </CollapsibleSection>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import axios from 'axios'
import CollapsibleSection from './CollapsibleSection.vue'

const { t } = useI18n()

const props = defineProps({
  faction: {
    type: Object,
    required: true
  }
})

defineEmits(['selectUnit'])

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

const initialLoading = ref(true)
const expandedSections = ref(new Set())
const sectionData = reactive({
  battle_traits: null,
  heroic_traits: null,
  artefacts: null,
  units: null,
  spell_lores: null,
  manifestation_lores: null,
  armies_of_renown: null,
})

const sectionEndpoints = {
  battle_traits: 'battle-traits',
  heroic_traits: 'heroic-traits',
  artefacts: 'artefacts',
  units: 'units',
  spell_lores: 'spell-lores',
  manifestation_lores: 'manifestation-lores',
  armies_of_renown: 'armies-of-renown',
}

// Unit type order for grouping
const unitTypeOrder = [
  'Hero Infantry',
  'Hero Cavalry',
  'Hero Monster',
  'Hero',
  'Infantry',
  'Cavalry',
  'Monster',
  'Beast',
  'War Machine',
  'Other'
]

const groupedUnits = computed(() => {
  if (!sectionData.units) return []

  const groups = {}

  for (const unit of sectionData.units) {
    const category = getUnitCategory(unit)
    if (!groups[category]) {
      groups[category] = []
    }
    groups[category].push(unit)
  }

  // Sort groups by predefined order
  return unitTypeOrder
    .filter(type => groups[type]?.length > 0)
    .map(type => ({
      name: type,
      units: groups[type].sort((a, b) => a.name.localeCompare(b.name))
    }))
})

const getUnitCategory = (unit) => {
  const keywordsList = Array.isArray(unit.keywords)
    ? unit.keywords.map(keyword => keyword.toUpperCase())
    : []

  const isHero = keywordsList.some(keyword => keyword.includes('HERO'))
  const isInfantry = keywordsList.includes('INFANTRY')
  const isCavalry = keywordsList.includes('CAVALRY')
  const isMonster = keywordsList.includes('MONSTER')
  const isBeast = keywordsList.includes('BEAST')
  const isWarMachine = keywordsList.includes('WAR MACHINE')

  if (isHero) {
    if (isInfantry) return 'Hero Infantry'
    if (isCavalry) return 'Hero Cavalry'
    if (isMonster) return 'Hero Monster'
    return 'Hero'
  }

  if (isInfantry) return 'Infantry'
  if (isCavalry) return 'Cavalry'
  if (isMonster) return 'Monster'
  if (isBeast) return 'Beast'
  if (isWarMachine) return 'War Machine'

  return 'Other'
}

// Main keywords to display on unit cards
const mainKeywordsList = ['HERO', 'INFANTRY', 'CAVALRY', 'MONSTER', 'BEAST', 'WAR MACHINE', 'WIZARD', 'PRIEST', 'UNIQUE', 'TOTEM', 'CHAMPION', 'MUSICIAN', 'STANDARD BEARER', 'FLY', 'WARD']

const getMainKeywords = (keywords) => {
  if (!keywords) return []
  const keywordsList = Array.isArray(keywords) ? keywords : []
  return keywordsList
    .map(keyword => keyword.toUpperCase())
    .filter(keyword => mainKeywordsList.some(main => keyword.includes(main)))
}

const toggleSection = (key) => {
  if (expandedSections.value.has(key)) {
    expandedSections.value.delete(key)
  } else {
    expandedSections.value.add(key)
  }
}

const fetchSection = async (key) => {
  try {
    const endpoint = sectionEndpoints[key]
    const response = await axios.get(`${API_URL}/bsdata/factions/${props.faction.id}/${endpoint}`)
    sectionData[key] = response.data
  } catch (err) {
    console.error(`Failed to fetch ${key}:`, err)
    sectionData[key] = []
  }
}

const loadAllData = async () => {
  initialLoading.value = true

  // Fetch all sections in parallel
  await Promise.all(
    Object.keys(sectionEndpoints).map(key => fetchSection(key))
  )

  initialLoading.value = false
}

onMounted(() => {
  loadAllData()
})
</script>
