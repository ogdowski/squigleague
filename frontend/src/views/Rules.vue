<template>
  <div class="max-w-7xl mx-auto">
    <!-- BSData info panel -->
    <div v-if="!infoPanelHidden && !selectedFaction && !selectedUnit && !selectedManifestationLore && !selectedManifestation" class="mb-6 bg-blue-900/20 border border-blue-700/50 rounded-lg p-4">
      <div class="flex items-start justify-between gap-4">
        <div class="flex items-start gap-3">
          <svg class="w-5 h-5 text-blue-400 flex-shrink-0 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          <p class="text-sm text-gray-300">
            {{ t('rules.bsdataInfo') }}
          </p>
        </div>
        <button
          @click="hideInfoPanel"
          class="text-gray-400 hover:text-white transition-colors p-1 flex-shrink-0"
          :aria-label="t('common.close')"
        >
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      </div>
    </div>

    <!-- Search Bar -->
    <div class="relative mb-6">
      <div class="relative">
        <svg class="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
        </svg>
        <input
          v-model="searchQuery"
          @input="onSearchInput"
          @focus="searchFocused = true"
          @blur="onSearchBlur"
          type="text"
          :placeholder="t('rules.searchPlaceholder')"
          class="w-full bg-gray-800 border border-gray-700 rounded-lg pl-10 pr-4 py-2.5 text-sm text-white placeholder-gray-500 focus:outline-none focus:border-squig-yellow/50"
        />
        <button
          v-if="searchQuery"
          @mousedown.prevent="clearSearch"
          class="absolute right-3 top-1/2 -translate-y-1/2 text-gray-500 hover:text-white"
        >
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      </div>

      <!-- Search Results Dropdown -->
      <div
        v-if="searchFocused && searchQuery.length >= 2 && (searchResults.length > 0 || searchLoading)"
        class="absolute z-50 w-full mt-1 bg-gray-800 border border-gray-700 rounded-lg shadow-xl max-h-96 overflow-y-auto"
      >
        <div v-if="searchLoading" class="px-4 py-3 text-sm text-gray-400">
          {{ t('common.loading') || 'Loading...' }}
        </div>
        <template v-else>
          <div
            v-for="(result, index) in searchResults"
            :key="index"
            @mousedown.prevent="selectSearchResult(result)"
            class="px-4 py-2.5 hover:bg-gray-700/50 cursor-pointer border-b border-gray-700/50 last:border-b-0"
          >
            <div class="flex items-center justify-between gap-2">
              <div class="min-w-0">
                <span class="text-sm font-medium text-white">{{ result.name }}</span>
                <span v-if="result.faction_name" class="text-xs text-gray-500 ml-2">{{ result.faction_name }}</span>
                <span v-if="result.extra && result.result_type === 'ability'" class="text-xs text-gray-500 ml-1">/ {{ result.extra }}</span>
              </div>
              <div class="flex items-center gap-2 flex-shrink-0">
                <span v-if="result.points" class="text-xs text-squig-yellow font-bold">{{ result.points }} pts</span>
                <span :class="['text-xs px-1.5 py-0.5 rounded', searchResultTypeClass(result.result_type)]">
                  {{ searchResultTypeLabel(result.result_type) }}
                </span>
              </div>
            </div>
          </div>
        </template>
      </div>
    </div>

    <!-- Loading -->
    <div v-if="loading" class="flex justify-center py-12">
      <div class="w-10 h-10 border-4 border-squig-yellow border-t-transparent rounded-full animate-spin"></div>
    </div>

    <!-- Error -->
    <div v-else-if="error" class="card bg-red-900/30 border-red-500 text-red-200">
      {{ error }}
    </div>

    <!-- Content -->
    <template v-else>
      <!-- Manifestation Detail View (unit-like) -->
      <div v-if="selectedManifestation">
        <button
          @click="goBack"
          class="flex items-center gap-2 text-gray-400 hover:text-white mb-4 transition-colors"
        >
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
          </svg>
          {{ t('common.back') }}
        </button>

        <!-- Desktop layout -->
        <div class="hidden lg:flex gap-6">
          <!-- Stats circle -->
          <div class="flex-shrink-0">
            <div class="w-36 h-36 rounded-full border-4 border-squig-yellow flex flex-col items-center justify-center bg-gray-800/50">
              <div class="text-center">
                <div class="text-2xl font-bold text-squig-yellow">{{ selectedManifestation.health || '-' }}</div>
                <div class="text-[10px] text-gray-400 uppercase tracking-wider">Health</div>
              </div>
              <div class="flex gap-4 mt-1">
                <div class="text-center">
                  <div class="text-sm font-bold">{{ selectedManifestation.move || '-' }}</div>
                  <div class="text-[9px] text-gray-500">Move</div>
                </div>
                <div class="text-center">
                  <div class="text-sm font-bold">{{ selectedManifestation.save || '-' }}</div>
                  <div class="text-[9px] text-gray-500">Save</div>
                </div>
              </div>
            </div>
          </div>
          <!-- Content -->
          <div class="flex-1 space-y-4">
            <div>
              <h2 class="text-2xl font-bold text-squig-yellow">{{ selectedManifestation.name }}</h2>
              <p v-if="selectedManifestationLore" class="text-sm text-gray-400">{{ selectedManifestationLore.name }}</p>
            </div>
            <div class="flex flex-wrap gap-2">
              <span v-if="selectedManifestation.casting_value" class="text-xs bg-purple-900/50 text-purple-300 px-2 py-0.5 rounded">
                Casting Value: {{ selectedManifestation.casting_value }}+
              </span>
              <span v-if="selectedManifestation.banishment" class="text-xs bg-red-900/50 text-red-300 px-2 py-0.5 rounded">
                Banishment: {{ selectedManifestation.banishment }}+
              </span>
            </div>
            <div v-if="selectedManifestation.declare || selectedManifestation.effect" class="card">
              <div class="bg-yellow-800/60 text-yellow-200 px-3 py-1 text-xs font-medium rounded-t-lg -mx-4 -mt-4 mb-3">
                Hero Phase
              </div>
              <h3 class="font-bold text-squig-yellow mb-2">Summon</h3>
              <p v-if="selectedManifestation.declare" class="text-sm text-gray-400 mb-2 whitespace-pre-wrap"><span class="font-medium text-gray-300">Declare:</span> {{ selectedManifestation.declare }}</p>
              <p v-if="selectedManifestation.effect" class="text-sm text-gray-300 whitespace-pre-wrap">{{ selectedManifestation.effect }}</p>
            </div>
          </div>
        </div>

        <!-- Mobile layout -->
        <div class="lg:hidden space-y-4">
          <div>
            <h2 class="text-xl font-bold text-squig-yellow">{{ selectedManifestation.name }}</h2>
            <p v-if="selectedManifestationLore" class="text-sm text-gray-400">{{ selectedManifestationLore.name }}</p>
          </div>
          <!-- Stats table -->
          <div class="card">
            <table class="w-full text-center text-sm">
              <thead><tr class="text-gray-500 text-xs">
                <th class="pb-1">Move</th><th class="pb-1">Health</th><th class="pb-1">Save</th>
              </tr></thead>
              <tbody><tr class="font-bold">
                <td>{{ selectedManifestation.move || '-' }}</td>
                <td>{{ selectedManifestation.health || '-' }}</td>
                <td>{{ selectedManifestation.save || '-' }}</td>
              </tr></tbody>
            </table>
          </div>
          <!-- Badges -->
          <div class="flex flex-wrap gap-2">
            <span v-if="selectedManifestation.casting_value" class="text-xs bg-purple-900/50 text-purple-300 px-2 py-0.5 rounded">
              Casting Value: {{ selectedManifestation.casting_value }}+
            </span>
            <span v-if="selectedManifestation.banishment" class="text-xs bg-red-900/50 text-red-300 px-2 py-0.5 rounded">
              Banishment: {{ selectedManifestation.banishment }}+
            </span>
          </div>
          <!-- Ability -->
          <div v-if="selectedManifestation.declare || selectedManifestation.effect" class="card">
            <div class="bg-yellow-800/60 text-yellow-200 px-3 py-1 text-xs font-medium rounded-t-lg -mx-4 -mt-4 mb-3">
              Hero Phase
            </div>
            <h3 class="font-bold text-squig-yellow mb-2">Summon</h3>
            <p v-if="selectedManifestation.declare" class="text-sm text-gray-400 mb-2 whitespace-pre-wrap"><span class="font-medium text-gray-300">Declare:</span> {{ selectedManifestation.declare }}</p>
            <p v-if="selectedManifestation.effect" class="text-sm text-gray-300 whitespace-pre-wrap">{{ selectedManifestation.effect }}</p>
          </div>
        </div>
      </div>

      <!-- Manifestation Lore List View -->
      <div v-else-if="selectedManifestationLore">
        <button
          @click="goBack"
          class="flex items-center gap-2 text-gray-400 hover:text-white mb-4 transition-colors"
        >
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
          </svg>
          {{ t('common.back') }}
        </button>

        <div class="mb-6">
          <h2 class="text-2xl font-bold">{{ selectedManifestationLore.name }}</h2>
          <p class="text-gray-400">{{ selectedManifestationLore.manifestations?.length || 0 }} manifestations</p>
        </div>

        <div class="space-y-1">
          <div
            v-for="manifestation in selectedManifestationLore.manifestations"
            :key="manifestation.id"
            @click="selectManifestation(manifestation)"
            class="bg-gray-700/50 rounded px-3 py-2 cursor-pointer hover:bg-gray-600/50 transition-colors flex items-center justify-between"
          >
            <div class="flex-1 min-w-0">
              <span class="text-sm font-medium">{{ manifestation.name }}</span>
              <div class="flex gap-3 text-xs text-gray-500 mt-0.5">
                <span v-if="manifestation.move">Move {{ manifestation.move }}</span>
                <span v-if="manifestation.health">HP {{ manifestation.health }}</span>
                <span v-if="manifestation.save">Save {{ manifestation.save }}</span>
              </div>
            </div>
            <span v-if="manifestation.banishment" class="text-xs text-red-400 flex-shrink-0 ml-3">Ban {{ manifestation.banishment }}+</span>
          </div>
        </div>
      </div>

      <!-- Unit Detail View -->
      <div v-else-if="selectedUnit">
        <button
          @click="goBack"
          class="flex items-center gap-2 text-gray-400 hover:text-white mb-4 transition-colors"
        >
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
          </svg>
          {{ t('common.back') }}
        </button>

        <UnitDetail :unit="selectedUnit" />
      </div>

      <!-- Faction Detail View -->
      <div v-else-if="selectedFaction">
        <button
          @click="goBack"
          class="flex items-center gap-2 text-gray-400 hover:text-white mb-4 transition-colors"
        >
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
          </svg>
          {{ t('common.back') }}
        </button>

        <FactionDetail
          :key="selectedFaction.id"
          :faction="selectedFaction"
          @select-unit="loadUnit"
          @select-faction="loadFaction"
        />
      </div>

      <!-- Factions List -->
      <template v-else>
        <FactionBrowser
          :grand-alliances="grandAlliances"
          :factions="mainFactions"
          @select-faction="loadFaction"
        />

        <!-- Universal Manifestation Lores -->
        <div v-if="universalManifestationLores.length > 0" class="mt-12">
          <div class="flex items-center gap-3 mb-6">
            <h2 class="text-xl font-bold text-purple-400">{{ t('rules.universalManifestations') }}</h2>
            <div class="flex-1 h-px bg-purple-400/30"></div>
          </div>

          <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
            <div
              v-for="lore in universalManifestationLores"
              :key="lore.id"
              @click="selectManifestationLore(lore)"
              class="card cursor-pointer hover:border-purple-500/50 transition-colors flex items-center justify-between"
            >
              <span class="font-medium">{{ lore.name }}</span>
              <span class="text-sm text-gray-400">{{ lore.manifestations?.length || 0 }}</span>
            </div>
          </div>
        </div>
      </template>
    </template>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRoute, useRouter } from 'vue-router'
import axios from 'axios'

import FactionBrowser from '../components/rules/FactionBrowser.vue'
import FactionDetail from '../components/rules/FactionDetail.vue'
import UnitDetail from '../components/rules/UnitDetail.vue'

const { t } = useI18n()
const route = useRoute()
const router = useRouter()

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

const loading = ref(true)
const error = ref('')
const infoPanelHidden = ref(localStorage.getItem('rules_infoPanelHidden') === 'true')
const expandedSections = ref(new Set())

// Search state
const searchQuery = ref('')
const searchResults = ref([])
const searchLoading = ref(false)
const searchFocused = ref(false)
let searchTimeout = null

const grandAlliances = ref([])
const factions = ref([])
const universalManifestationLores = ref([])

const selectedFaction = ref(null)
const selectedUnit = ref(null)
const selectedManifestationLore = ref(null)
const selectedManifestation = ref(null)

// Main factions (non-AoR) for the list display
const mainFactions = computed(() => factions.value.filter(faction => !faction.is_aor))

// Convert name to URL-friendly slug
const toSlug = (name) => {
  return name
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, '-')
    .replace(/^-|-$/g, '')
}

// Find faction by slug
const findFactionBySlug = (slug) => {
  return factions.value.find(f => toSlug(f.name) === slug)
}

const hideInfoPanel = () => {
  infoPanelHidden.value = true
  localStorage.setItem('rules_infoPanelHidden', 'true')
}

const toggleSection = (key) => {
  if (expandedSections.value.has(key)) {
    expandedSections.value.delete(key)
  } else {
    expandedSections.value.add(key)
  }
}

const fetchData = async () => {
  loading.value = true
  error.value = ''

  try {
    const [gaResponse, factionsResponse, loresResponse] = await Promise.all([
      axios.get(`${API_URL}/bsdata/grand-alliances`),
      axios.get(`${API_URL}/bsdata/factions?include_aor=true`),
      axios.get(`${API_URL}/bsdata/manifestation-lores`),
    ])

    grandAlliances.value = gaResponse.data
    factions.value = factionsResponse.data
    universalManifestationLores.value = loresResponse.data
  } catch (err) {
    console.error('Failed to fetch BSData:', err)
    error.value = t('rules.failedToLoad')
  } finally {
    loading.value = false
  }
}

const loadFaction = (factionId) => {
  const faction = factions.value.find(f => f.id === factionId)
  if (!faction) return
  if (faction.is_aor && faction.parent_faction_id) {
    const parent = factions.value.find(f => f.id === faction.parent_faction_id)
    faction.parentFactionName = parent ? parent.name : null
  }
  selectedFaction.value = faction
  router.push({ name: 'RulesFaction', params: { factionSlug: toSlug(faction.name) } })
}

const loadUnit = async (unitId, unitName) => {
  try {
    const response = await axios.get(`${API_URL}/bsdata/units/${unitId}`)
    selectedUnit.value = response.data
    if (selectedFaction.value) {
      const unitSlug = toSlug(unitName || response.data.name)
      router.push({
        name: 'RulesUnit',
        params: {
          factionSlug: toSlug(selectedFaction.value.name),
          unitSlug: unitSlug
        }
      })
    }
  } catch (err) {
    console.error('Failed to fetch unit:', err)
  }
}

const goBack = () => {
  if (window.history.length > 1) {
    router.back()
  } else if (selectedManifestationLore.value) {
    selectedManifestationLore.value = null
    router.push({ name: 'Rules' })
  } else if (selectedUnit.value) {
    selectedUnit.value = null
    if (selectedFaction.value) {
      router.push({ name: 'RulesFaction', params: { factionSlug: toSlug(selectedFaction.value.name) } })
    }
  } else {
    selectedFaction.value = null
    selectedUnit.value = null
    router.push({ name: 'Rules' })
  }
}

const selectManifestationLore = (lore) => {
  selectedManifestationLore.value = lore
  selectedManifestation.value = null
  router.push({ name: 'RulesFaction', params: { factionSlug: toSlug(lore.name) } })
}

const selectManifestation = (manifestation) => {
  selectedManifestation.value = manifestation
  router.push({
    name: 'RulesUnit',
    params: {
      factionSlug: toSlug(selectedManifestationLore.value.name),
      unitSlug: toSlug(manifestation.name)
    }
  })
}

// Search
const onSearchInput = () => {
  clearTimeout(searchTimeout)
  if (searchQuery.value.length < 2) {
    searchResults.value = []
    return
  }
  searchLoading.value = true
  searchTimeout = setTimeout(async () => {
    try {
      const response = await axios.get(`${API_URL}/bsdata/search`, { params: { query: searchQuery.value } })
      searchResults.value = response.data
    } catch (err) {
      searchResults.value = []
    } finally {
      searchLoading.value = false
    }
  }, 300)
}

const onSearchBlur = () => {
  setTimeout(() => { searchFocused.value = false }, 200)
}

const clearSearch = () => {
  searchQuery.value = ''
  searchResults.value = []
}

const selectSearchResult = (result) => {
  searchQuery.value = ''
  searchResults.value = []
  searchFocused.value = false

  if (result.result_type === 'unit' && result.unit_id) {
    // Navigate to unit detail via faction
    const faction = factions.value.find(f => f.id === result.faction_id)
    if (faction) {
      selectedFaction.value = faction
      loadUnit(result.unit_id, result.name)
    }
  } else if (result.result_type === 'ability' && result.unit_id) {
    // Navigate to the unit that has this ability
    const faction = factions.value.find(f => f.id === result.faction_id)
    if (faction) {
      selectedFaction.value = faction
      loadUnit(result.unit_id, result.extra)
    }
  } else if (result.faction_id) {
    // Battle trait, heroic trait, artefact, spell, prayer → go to faction
    loadFaction(result.faction_id)
  }
}

const searchResultTypeLabel = (type) => {
  const labels = {
    'unit': 'Unit',
    'ability': 'Ability',
    'battle_trait': 'Trait',
    'heroic_trait': 'Heroic',
    'artefact': 'Artefact',
    'spell': 'Spell',
    'prayer': 'Prayer',
  }
  return labels[type] || type
}

const searchResultTypeClass = (type) => {
  const classes = {
    'unit': 'bg-gray-700 text-gray-300',
    'ability': 'bg-blue-900/50 text-blue-300',
    'battle_trait': 'bg-green-900/50 text-green-300',
    'heroic_trait': 'bg-yellow-900/50 text-yellow-300',
    'artefact': 'bg-purple-900/50 text-purple-300',
    'spell': 'bg-indigo-900/50 text-indigo-300',
    'prayer': 'bg-amber-900/50 text-amber-300',
  }
  return classes[type] || 'bg-gray-700 text-gray-300'
}

// Handle URL parameters
const handleRouteParams = async () => {
  if (factions.value.length === 0) return

  const params = route.params

  if (params.unitSlug && params.factionSlug) {
    // Check if it's a manifestation lore slug
    const lore = universalManifestationLores.value.find(l => toSlug(l.name) === params.factionSlug)
    if (lore) {
      selectedManifestationLore.value = lore
      const manifestation = lore.manifestations?.find(m => toSlug(m.name) === params.unitSlug)
      if (manifestation) {
        selectedManifestation.value = manifestation
      }
    } else {
      // Load unit view
      const faction = findFactionBySlug(params.factionSlug)
      if (faction) {
        selectedFaction.value = faction
        try {
          const unitsResponse = await axios.get(`${API_URL}/bsdata/factions/${faction.id}/units`)
          const unit = unitsResponse.data.find(u => toSlug(u.name) === params.unitSlug)
          if (unit) {
            const response = await axios.get(`${API_URL}/bsdata/units/${unit.id}`)
            selectedUnit.value = response.data
          }
        } catch (err) {
          console.error('Failed to fetch unit:', err)
        }
      }
    }
  } else if (params.factionSlug) {
    // Try faction first
    const faction = findFactionBySlug(params.factionSlug)
    if (faction) {
      if (faction.is_aor && faction.parent_faction_id) {
        const parent = factions.value.find(f => f.id === faction.parent_faction_id)
        faction.parentFactionName = parent ? parent.name : null
      }
      selectedFaction.value = faction
      selectedUnit.value = null
      selectedManifestationLore.value = null
      selectedManifestation.value = null
    } else {
      // Try manifestation lore
      const lore = universalManifestationLores.value.find(l => toSlug(l.name) === params.factionSlug)
      if (lore) {
        selectedManifestationLore.value = lore
        selectedManifestation.value = null
        selectedFaction.value = null
        selectedUnit.value = null
      }
    }
  } else {
    // Show faction list
    selectedFaction.value = null
    selectedUnit.value = null
    selectedManifestationLore.value = null
    selectedManifestation.value = null
  }
}

watch(() => route.params, handleRouteParams, { immediate: true })

onMounted(async () => {
  await fetchData()
  await handleRouteParams()
})
</script>
