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

    <div v-else class="grid grid-cols-1 lg:grid-cols-2 gap-6 items-start">
      <!-- LEFT column: Units -->
      <div v-if="sectionData.units?.length">
        <div class="card">
          <div class="flex items-center justify-between mb-4">
            <h3 class="font-bold text-squig-yellow">{{ t('rules.units') }}</h3>
            <span class="text-sm text-gray-400">{{ sectionData.units.length }}</span>
          </div>
          <div class="space-y-6">
            <div v-for="group in groupedUnits" :key="group.name">
              <h4 class="text-sm font-medium text-gray-400 mb-3">{{ group.name }}</h4>
              <div class="space-y-1">
                <div
                  v-for="unit in group.units"
                  :key="unit.id"
                  @click="$emit('selectUnit', unit.id, unit.name)"
                  class="bg-gray-700/50 rounded px-3 py-1.5 cursor-pointer hover:bg-gray-600/50 transition-colors flex items-center justify-between"
                >
                  <span class="text-sm flex items-center gap-1.5">
                    {{ unit.name }}
                    <svg v-if="isUniqueUnit(unit)" class="w-3.5 h-3.5 text-squig-yellow flex-shrink-0" viewBox="0 0 24 24" fill="currentColor">
                      <path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z"/>
                    </svg>
                    <svg v-if="isSoGUnit(unit)" class="w-3.5 h-3.5 text-green-400 flex-shrink-0" viewBox="0 0 24 24" fill="currentColor">
                      <path d="M17 8C8 10 5.9 16.17 3.82 21.34l1.89.66.95-2.3c.48.17.98.3 1.34.3C19 20 22 3 22 3c-1 2-8 2.25-13 3.25S2 11.5 2 13.5s1.75 3.75 1.75 3.75C7 8 17 8 17 8z"/>
                    </svg>
                  </span>
                  <span class="text-squig-yellow font-bold text-sm flex-shrink-0 ml-4">{{ unit.points || '-' }}</span>
                </div>
              </div>
            </div>
            <!-- Faction Manifestations at the end of unit list -->
            <div v-if="allFactionManifestations.length">
              <h4 class="text-sm font-medium text-gray-400 mb-3">Manifestations</h4>
              <div class="space-y-1">
                <div
                  v-for="manifestation in allFactionManifestations"
                  :key="manifestation.id"
                  @click="$emit('selectManifestation', manifestation)"
                  class="bg-gray-700/50 rounded px-3 py-1.5 cursor-pointer hover:bg-gray-600/50 transition-colors flex items-center justify-between"
                >
                  <span class="text-sm">{{ manifestation.name.replace(/^Summon\s+/, '') }}</span>
                  <span v-if="manifestation.casting_value" class="text-squig-yellow font-bold text-sm flex-shrink-0 ml-4">{{ manifestation.casting_value }}+</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- RIGHT column: Traits, Lores, Artefacts, AoR -->
      <div class="space-y-4">
        <!-- Battle Traits -->
        <CollapsibleSection
          v-if="sectionData.battle_traits?.length"
          :title="t('rules.battleTraits')"
          :count="sectionData.battle_traits.length"
          :expanded="expandedSections.has('battle_traits')"
          @toggle="toggleSection('battle_traits')"
        >
          <div class="space-y-3">
            <div
              v-for="trait in sectionData.battle_traits"
              :key="trait.id"
              class="bg-gray-700/50 rounded-lg overflow-hidden"
            >
              <div
                :class="['px-3 py-1 text-xs font-medium', getColorBarClass(trait.color)]"
              >
                {{ trait.timing || getPhaseFromColor(trait.color) || 'Passive' }}
              </div>
              <div class="p-4">
                <h4 class="font-bold text-squig-yellow mb-2">{{ trait.name }}</h4>
                <p v-if="trait.declare" class="text-sm text-gray-400 mb-2 whitespace-pre-wrap"><span class="font-medium text-gray-300">Declare:</span> {{ trait.declare }}</p>
                <p class="text-sm text-gray-300 whitespace-pre-wrap">{{ trait.effect }}</p>
                <div v-if="trait.keywords?.length" class="flex flex-wrap gap-1 mt-3 pt-3 border-t border-gray-600/50">
                  <span v-for="kw in trait.keywords" :key="kw" class="text-xs bg-gray-600/50 text-gray-400 px-2 py-0.5 rounded">{{ kw }}</span>
                </div>
              </div>
            </div>
          </div>
        </CollapsibleSection>

        <!-- Battle Formations -->
        <CollapsibleSection
          v-if="sectionData.battle_formations?.length"
          :title="t('rules.battleFormations')"
          :count="sectionData.battle_formations.length"
          :expanded="expandedSections.has('battle_formations')"
          @toggle="toggleSection('battle_formations')"
        >
          <div class="space-y-3">
            <div
              v-for="formation in sectionData.battle_formations"
              :key="formation.id"
              class="bg-gray-700/50 rounded-lg overflow-hidden"
            >
              <div
                :class="['px-3 py-1 text-xs font-medium', getColorBarClass(formation.color)]"
              >
                {{ formation.timing || getPhaseFromColor(formation.color) || 'Passive' }}
              </div>
              <div class="p-4">
                <div class="flex items-start justify-between mb-2">
                  <div>
                    <h4 class="font-bold text-squig-yellow">{{ formation.name }}</h4>
                    <p v-if="formation.ability_name && formation.ability_name !== formation.name" class="text-sm text-gray-400">{{ formation.ability_name }}</p>
                  </div>
                  <span v-if="formation.points" class="text-sm font-bold text-squig-yellow flex-shrink-0 ml-4">{{ formation.points }} pts</span>
                </div>
                <p v-if="formation.declare" class="text-sm text-gray-400 mb-2 whitespace-pre-wrap"><span class="font-medium text-gray-300">Declare:</span> {{ formation.declare }}</p>
                <p class="text-sm text-gray-300 whitespace-pre-wrap">{{ formation.effect }}</p>
                <div v-if="formation.keywords?.length" class="flex flex-wrap gap-1 mt-3 pt-3 border-t border-gray-600/50">
                  <span v-for="kw in formation.keywords" :key="kw" class="text-xs bg-gray-600/50 text-gray-400 px-2 py-0.5 rounded">{{ kw }}</span>
                </div>
              </div>
            </div>
          </div>
        </CollapsibleSection>

        <!-- Heroic Traits (grouped by group_name) -->
        <template v-for="(group, index) in groupedHeroicTraits" :key="'ht-' + index">
          <CollapsibleSection
            :title="group.name === '_default' ? t('rules.heroicTraits') : t('rules.heroicTraits') + ': ' + group.name"
            :count="group.items.length"
            :expanded="expandedSections.has('heroic_traits_' + group.name + (group.isSeasonal ? '_s' : ''))"
            @toggle="toggleSection('heroic_traits_' + group.name + (group.isSeasonal ? '_s' : ''))"
          >
            <template #title-prefix>
              <svg v-if="group.isSeasonal" class="w-4 h-4 text-green-400 mr-1.5 flex-shrink-0" viewBox="0 0 24 24" fill="currentColor">
                <path d="M17 8C8 10 5.9 16.17 3.82 21.34l1.89.66.95-2.3c.48.17.98.3 1.34.3C19 20 22 3 22 3c-1 2-8 2.25-13 3.25S2 11.5 2 13.5s1.75 3.75 1.75 3.75C7 8 17 8 17 8z"/>
              </svg>
            </template>
            <div class="space-y-3">
              <div
                v-for="trait in group.items"
                :key="trait.id"
                class="bg-gray-700/50 rounded-lg overflow-hidden"
              >
                <div
                  :class="['px-3 py-1 text-xs font-medium', getColorBarClass(trait.color)]"
                >
                  {{ trait.timing || getPhaseFromColor(trait.color) || 'Passive' }}
                </div>
                <div class="p-4">
                  <div class="flex items-start justify-between mb-2">
                    <h4 class="font-bold text-squig-yellow">{{ trait.name }}</h4>
                    <span v-if="trait.points" class="text-sm font-bold text-squig-yellow flex-shrink-0 ml-4">{{ trait.points }} pts</span>
                  </div>
                  <p v-if="trait.declare" class="text-sm text-gray-400 mb-2 whitespace-pre-wrap"><span class="font-medium text-gray-300">Declare:</span> {{ trait.declare }}</p>
                  <p class="text-sm text-gray-300 whitespace-pre-wrap">{{ trait.effect }}</p>
                  <div v-if="trait.keywords?.length" class="flex flex-wrap gap-1 mt-3 pt-3 border-t border-gray-600/50">
                    <span v-for="kw in trait.keywords" :key="kw" class="text-xs bg-gray-600/50 text-gray-400 px-2 py-0.5 rounded">{{ kw }}</span>
                  </div>
                </div>
              </div>
            </div>
          </CollapsibleSection>
        </template>

        <!-- Artefacts (grouped by group_name) -->
        <template v-for="(group, index) in groupedArtefacts" :key="'art-' + index">
          <CollapsibleSection
            :title="group.name === '_default' ? t('rules.artefacts') : t('rules.artefacts') + ': ' + group.name"
            :count="group.items.length"
            :expanded="expandedSections.has('artefacts_' + group.name + (group.isSeasonal ? '_s' : ''))"
            @toggle="toggleSection('artefacts_' + group.name + (group.isSeasonal ? '_s' : ''))"
          >
            <template #title-prefix>
              <svg v-if="group.isSeasonal" class="w-4 h-4 text-green-400 mr-1.5 flex-shrink-0" viewBox="0 0 24 24" fill="currentColor">
                <path d="M17 8C8 10 5.9 16.17 3.82 21.34l1.89.66.95-2.3c.48.17.98.3 1.34.3C19 20 22 3 22 3c-1 2-8 2.25-13 3.25S2 11.5 2 13.5s1.75 3.75 1.75 3.75C7 8 17 8 17 8z"/>
              </svg>
            </template>
            <div class="space-y-3">
              <div
                v-for="artefact in group.items"
                :key="artefact.id"
                class="bg-gray-700/50 rounded-lg overflow-hidden"
              >
                <div
                  :class="['px-3 py-1 text-xs font-medium', getColorBarClass(artefact.color)]"
                >
                  {{ artefact.timing || getPhaseFromColor(artefact.color) || 'Passive' }}
                </div>
                <div class="p-4">
                  <div class="flex items-start justify-between mb-2">
                    <h4 class="font-bold text-squig-yellow">{{ artefact.name }}</h4>
                    <span v-if="artefact.points" class="text-sm font-bold text-squig-yellow flex-shrink-0 ml-4">{{ artefact.points }} pts</span>
                  </div>
                  <p v-if="artefact.declare" class="text-sm text-gray-400 mb-2 whitespace-pre-wrap"><span class="font-medium text-gray-300">Declare:</span> {{ artefact.declare }}</p>
                  <p class="text-sm text-gray-300 whitespace-pre-wrap">{{ artefact.effect }}</p>
                  <div v-if="artefact.keywords?.length" class="flex flex-wrap gap-1 mt-3 pt-3 border-t border-gray-600/50">
                    <span v-for="kw in artefact.keywords" :key="kw" class="text-xs bg-gray-600/50 text-gray-400 px-2 py-0.5 rounded">{{ kw }}</span>
                  </div>
                </div>
              </div>
            </div>
          </CollapsibleSection>
        </template>

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
              <div class="flex items-start justify-between mb-3">
                <h4 class="font-bold text-purple-400">{{ lore.name }}</h4>
                <span v-if="lore.points" class="text-sm font-bold text-squig-yellow flex-shrink-0 ml-4">{{ lore.points }} pts</span>
              </div>
              <div class="space-y-3">
                <div
                  v-for="spell in lore.spells"
                  :key="spell.id"
                  class="bg-gray-800/50 rounded overflow-hidden"
                >
                  <div class="px-3 py-1 text-xs font-medium bg-yellow-600 text-yellow-100">
                    Hero Phase
                  </div>
                  <div class="p-3">
                    <div class="flex items-start justify-between mb-1">
                      <h5 class="font-medium text-squig-yellow">{{ spell.name }}</h5>
                      <span v-if="spell.casting_value" class="text-xs bg-purple-900/50 text-purple-300 px-2 py-0.5 rounded">
                        Casting value: {{ spell.casting_value }}+
                      </span>
                    </div>
                    <p v-if="spell.declare" class="text-sm text-gray-400 mb-2 whitespace-pre-wrap"><span class="font-medium text-gray-300">Declare:</span> {{ spell.declare }}</p>
                    <p class="text-sm text-gray-300 whitespace-pre-wrap">{{ spell.effect }}</p>
                    <div v-if="spell.keywords?.length" class="flex flex-wrap gap-1 mt-2 pt-2 border-t border-gray-600/50">
                      <span v-for="kw in spell.keywords" :key="kw" class="text-xs bg-gray-600/50 text-gray-400 px-2 py-0.5 rounded">{{ kw }}</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </CollapsibleSection>

        <!-- Prayer Lores -->
        <CollapsibleSection
          v-if="sectionData.prayer_lores?.length"
          :title="t('rules.prayerLores')"
          :count="sectionData.prayer_lores.length"
          :expanded="expandedSections.has('prayer_lores')"
          @toggle="toggleSection('prayer_lores')"
        >
          <div class="space-y-4">
            <div v-for="lore in sectionData.prayer_lores" :key="lore.id" class="bg-gray-700/50 rounded-lg p-4">
              <div class="flex items-start justify-between mb-3">
                <h4 class="font-bold text-amber-400">{{ lore.name }}</h4>
                <span v-if="lore.points" class="text-sm font-bold text-squig-yellow flex-shrink-0 ml-4">{{ lore.points }} pts</span>
              </div>
              <div class="space-y-3">
                <div
                  v-for="prayer in lore.prayers"
                  :key="prayer.id"
                  class="bg-gray-800/50 rounded overflow-hidden"
                >
                  <div class="px-3 py-1 text-xs font-medium bg-yellow-600 text-yellow-100">
                    Hero Phase
                  </div>
                  <div class="p-3">
                    <div class="flex items-start justify-between mb-1">
                      <h5 class="font-medium text-squig-yellow">{{ prayer.name }}</h5>
                      <span v-if="prayer.chanting_value" class="text-xs bg-amber-900/50 text-amber-300 px-2 py-0.5 rounded">
                        Chanting value: {{ prayer.chanting_value }}+
                      </span>
                    </div>
                    <p v-if="prayer.declare" class="text-sm text-gray-400 mb-2 whitespace-pre-wrap"><span class="font-medium text-gray-300">Declare:</span> {{ prayer.declare }}</p>
                    <p v-if="prayer.effect" class="text-sm text-gray-300 whitespace-pre-wrap">{{ prayer.effect }}</p>
                    <div v-if="prayer.keywords?.length" class="flex flex-wrap gap-1 mt-2 pt-2 border-t border-gray-600/50">
                      <span v-for="kw in prayer.keywords" :key="kw" class="text-xs bg-gray-600/50 text-gray-400 px-2 py-0.5 rounded">{{ kw }}</span>
                    </div>
                  </div>
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
                  class="bg-gray-800/50 rounded overflow-hidden"
                >
                  <div class="px-3 py-1 text-xs font-medium bg-yellow-600 text-yellow-100">
                    Hero Phase
                  </div>
                  <div class="p-3">
                    <div class="flex items-start justify-between mb-1">
                      <h5 class="font-medium text-squig-yellow">{{ manifestation.name }}</h5>
                      <span v-if="manifestation.points" class="text-sm font-bold text-squig-yellow flex-shrink-0 ml-2">
                        {{ manifestation.points }} pts
                      </span>
                    </div>
                    <!-- Casting & Banishment info -->
                    <div v-if="manifestation.casting_value || manifestation.banishment" class="flex flex-wrap gap-2 mb-2">
                      <span v-if="manifestation.casting_value" class="text-xs bg-purple-900/50 text-purple-300 px-2 py-0.5 rounded">
                        Casting value: {{ manifestation.casting_value }}+
                      </span>
                      <span v-if="manifestation.banishment" class="text-xs bg-red-900/50 text-red-300 px-2 py-0.5 rounded">
                        Banishment: {{ manifestation.banishment }}+
                      </span>
                    </div>
                    <!-- Stats row -->
                    <div v-if="manifestation.move || manifestation.health || manifestation.save" class="flex flex-wrap gap-3 mb-2 text-xs text-gray-400">
                      <span v-if="manifestation.move">Move: {{ manifestation.move }}</span>
                      <span v-if="manifestation.health">Health: {{ manifestation.health }}</span>
                      <span v-if="manifestation.save">Save: {{ manifestation.save }}+</span>
                    </div>
                    <p v-if="manifestation.declare" class="text-sm text-gray-400 mb-2 whitespace-pre-wrap"><span class="font-medium text-gray-300">Declare:</span> {{ manifestation.declare }}</p>
                    <p v-if="manifestation.effect" class="text-sm text-gray-300 whitespace-pre-wrap">{{ manifestation.effect }}</p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </CollapsibleSection>

        <!-- Armies of Renown (sub-factions) -->
        <CollapsibleSection
          v-if="sectionData.armies_of_renown?.length"
          :title="t('rules.armiesOfRenown')"
          :count="sectionData.armies_of_renown.length"
          :expanded="expandedSections.has('armies_of_renown')"
          @toggle="toggleSection('armies_of_renown')"
        >
          <div class="space-y-1">
            <div
              v-for="aor in sectionData.armies_of_renown"
              :key="aor.id"
              @click="$emit('selectFaction', aor.id, aor.name)"
              class="bg-gray-700/50 rounded px-3 py-2 cursor-pointer hover:bg-gray-600/50 transition-colors flex items-center justify-between"
            >
              <span class="text-sm font-medium">{{ aor.name }}</span>
              <span class="text-xs text-gray-400">AoR</span>
            </div>
          </div>
        </CollapsibleSection>
      </div>
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

defineEmits(['selectUnit', 'selectFaction', 'selectManifestation'])

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

const initialLoading = ref(true)
const expandedSections = ref(new Set())
const sectionData = reactive({
  battle_traits: null,
  battle_formations: null,
  heroic_traits: null,
  artefacts: null,
  units: null,
  spell_lores: null,
  prayer_lores: null,
  manifestation_lores: null,
  armies_of_renown: null,
})

const sectionEndpoints = {
  battle_traits: 'battle-traits',
  battle_formations: 'battle-formations',
  heroic_traits: 'heroic-traits',
  artefacts: 'artefacts',
  units: 'units',
  spell_lores: 'spell-lores',
  prayer_lores: 'prayer-lores',
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

const groupEnhancementsByGroupName = (items) => {
  if (!items?.length) return []

  const groups = {}
  const order = []

  for (const item of items) {
    const groupName = item.group_name || '_default'
    const seasonal = item.is_seasonal || false
    const key = groupName + (seasonal ? '::seasonal' : '')
    if (!groups[key]) {
      groups[key] = {
        name: groupName,
        isSeasonal: seasonal,
        items: [],
      }
      order.push(key)
    }
    groups[key].items.push(item)
  }

  // Non-seasonal groups first, then seasonal
  return order
    .map(key => groups[key])
    .sort((first, second) => (first.isSeasonal === second.isSeasonal ? 0 : first.isSeasonal ? 1 : -1))
}

const groupedHeroicTraits = computed(() => groupEnhancementsByGroupName(sectionData.heroic_traits))
const groupedArtefacts = computed(() => groupEnhancementsByGroupName(sectionData.artefacts))

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
      name: type === 'Other' ? 'Faction Terrain' : type,
      units: groups[type].sort((a, b) => a.name.localeCompare(b.name))
    }))
})

const allFactionManifestations = computed(() => {
  if (!sectionData.manifestation_lores?.length) return []
  return sectionData.manifestation_lores.flatMap(lore => lore.manifestations || [])
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

const isSoGUnit = (unit) => {
  return unit.name?.includes('(Scourge of Ghyran)')
}

const isUniqueUnit = (unit) => {
  const keywordsList = Array.isArray(unit.keywords)
    ? unit.keywords.map(keyword => keyword.toUpperCase())
    : []
  return keywordsList.includes('UNIQUE') && keywordsList.some(keyword => keyword.includes('HERO'))
}

const getMainKeywords = (keywords) => {
  if (!keywords) return []
  const keywordsList = Array.isArray(keywords) ? keywords : []
  return keywordsList
    .map(keyword => keyword.toUpperCase())
    .filter(keyword => mainKeywordsList.some(main => keyword.includes(main)))
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
