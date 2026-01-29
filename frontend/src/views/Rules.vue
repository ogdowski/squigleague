<template>
  <div class="max-w-7xl mx-auto">
    <!-- BSData info panel -->
    <div v-if="!infoPanelHidden && !selectedFaction && !selectedUnit" class="mb-6 bg-blue-900/20 border border-blue-700/50 rounded-lg p-4">
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
      <!-- Unit Detail View -->
      <div v-if="selectedUnit">
        <button
          @click="goBackToFaction"
          class="flex items-center gap-2 text-gray-400 hover:text-white mb-4 transition-colors"
        >
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
          </svg>
          {{ t('rules.backToFaction') }}
        </button>

        <UnitDetail :unit="selectedUnit" />
      </div>

      <!-- Faction Detail View -->
      <div v-else-if="selectedFaction">
        <button
          @click="goBackToFactions"
          class="flex items-center gap-2 text-gray-400 hover:text-white mb-4 transition-colors"
        >
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
          </svg>
          {{ t('rules.backToFactions') }}
        </button>

        <FactionDetail
          :faction="selectedFaction"
          @select-unit="loadUnit"
          @select-faction="loadFaction"
        />
      </div>

      <!-- Factions List -->
      <template v-else>
        <FactionBrowser
          :grand-alliances="grandAlliances"
          :factions="factions"
          @select-faction="loadFaction"
        />

        <!-- Universal Manifestation Lores -->
        <div v-if="universalManifestationLores.length > 0" class="mt-12">
          <div class="flex items-center gap-3 mb-6">
            <h2 class="text-xl font-bold text-purple-400">{{ t('rules.universalManifestations') }}</h2>
            <div class="flex-1 h-px bg-purple-400/30"></div>
          </div>

          <div class="space-y-4">
            <div v-for="lore in universalManifestationLores" :key="lore.id" class="card">
              <button
                @click="toggleSection('lore-' + lore.id)"
                class="w-full flex items-center justify-between text-left"
              >
                <h3 class="font-bold text-lg">{{ lore.name }}</h3>
                <svg
                  :class="['w-5 h-5 transition-transform', expandedSections.has('lore-' + lore.id) ? 'rotate-180' : '']"
                  fill="none" stroke="currentColor" viewBox="0 0 24 24"
                >
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
                </svg>
              </button>

              <div v-if="expandedSections.has('lore-' + lore.id)" class="mt-4 space-y-3">
                <div
                  v-for="manifestation in lore.manifestations"
                  :key="manifestation.id"
                  class="bg-gray-700/50 rounded-lg p-4"
                >
                  <div class="flex items-start justify-between mb-2">
                    <h4 class="font-bold text-squig-yellow">{{ manifestation.name }}</h4>
                    <div class="flex items-center gap-2 text-sm">
                      <span v-if="manifestation.points" class="text-squig-yellow">
                        {{ manifestation.points }} pts
                      </span>
                    </div>
                  </div>
                  <div v-if="manifestation.move || manifestation.health || manifestation.save" class="flex gap-3 mb-2 text-sm text-gray-400">
                    <span v-if="manifestation.move">M: {{ manifestation.move }}</span>
                    <span v-if="manifestation.health">H: {{ manifestation.health }}</span>
                    <span v-if="manifestation.save">Sv: {{ manifestation.save }}</span>
                  </div>
                  <p v-if="manifestation.description" class="text-sm text-gray-300 whitespace-pre-wrap">
                    {{ manifestation.description }}
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </template>
    </template>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
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

const grandAlliances = ref([])
const factions = ref([])
const universalManifestationLores = ref([])

const selectedFaction = ref(null)
const selectedUnit = ref(null)

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
    const [gaResponse, factionsResponse, manifestationsResponse] = await Promise.all([
      axios.get(`${API_URL}/bsdata/grand-alliances`),
      axios.get(`${API_URL}/bsdata/factions`),
      axios.get(`${API_URL}/bsdata/manifestations`),
    ])

    grandAlliances.value = gaResponse.data
    factions.value = factionsResponse.data
    // Group manifestations as a single "Universal" lore
    const manifestations = manifestationsResponse.data
    if (manifestations.length > 0) {
      universalManifestationLores.value = [{
        id: 0,
        name: 'Endless Spells & Invocations',
        manifestations: manifestations
      }]
    }
  } catch (err) {
    console.error('Failed to fetch BSData:', err)
    error.value = t('rules.failedToLoad')
  } finally {
    loading.value = false
  }
}

const loadFaction = async (factionId, factionName) => {
  // Try local cache first (for main factions)
  const faction = factions.value.find(f => f.id === factionId)
  if (faction) {
    selectedFaction.value = faction
    router.push({ name: 'RulesFaction', params: { factionSlug: toSlug(faction.name) } })
    return
  }
  // AoR factions won't be in the list - fetch detail from API
  try {
    const response = await axios.get(`${API_URL}/bsdata/factions/${factionId}`)
    const aorFaction = { id: response.data.id, name: factionName || response.data.name, grand_alliance: response.data.grand_alliance?.name }
    selectedFaction.value = aorFaction
    router.push({ name: 'RulesFaction', params: { factionSlug: toSlug(aorFaction.name) } })
  } catch (error) {
    console.error('Failed to load faction:', error)
  }
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

const goBackToFactions = () => {
  selectedFaction.value = null
  selectedUnit.value = null
  router.push({ name: 'Rules' })
}

const goBackToFaction = () => {
  selectedUnit.value = null
  if (selectedFaction.value) {
    router.push({ name: 'RulesFaction', params: { factionSlug: toSlug(selectedFaction.value.name) } })
  }
}

// Handle URL parameters
const handleRouteParams = async () => {
  if (factions.value.length === 0) return

  const params = route.params

  if (params.unitSlug && params.factionSlug) {
    // Load unit view
    const faction = findFactionBySlug(params.factionSlug)
    if (faction) {
      selectedFaction.value = faction
      // Need to search for unit by slug - fetch faction units first
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
  } else if (params.factionSlug) {
    // Load faction view
    const faction = findFactionBySlug(params.factionSlug)
    if (faction) {
      selectedFaction.value = faction
      selectedUnit.value = null
    }
  } else {
    // Show faction list
    selectedFaction.value = null
    selectedUnit.value = null
  }
}

watch(() => route.params, handleRouteParams, { immediate: true })

onMounted(async () => {
  await fetchData()
  await handleRouteParams()
})
</script>
