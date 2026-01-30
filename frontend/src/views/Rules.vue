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
          <div class="flex-shrink-0 flex flex-col items-center gap-3">
            <UnitStatCircle
              :move="selectedManifestation.move"
              :health="selectedManifestation.health"
              :save="selectedManifestation.save"
              :control="selectedManifestation.banishment"
              bottom-label="Ban"
            />
          </div>
          <!-- Content -->
          <div class="flex-1 space-y-4">
            <div>
              <h2 class="text-2xl font-bold text-squig-yellow">{{ selectedManifestation.name.replace(/^Summon\s+/, '') }}</h2>
              <p v-if="selectedManifestationLore" class="text-sm text-gray-400">{{ selectedManifestationLore.name }}</p>
            </div>
            <div v-if="selectedManifestation.casting_value" class="flex flex-wrap gap-2">
              <span class="text-xs bg-purple-900/50 text-purple-300 px-2 py-0.5 rounded">
                Casting Value: {{ selectedManifestation.casting_value }}+
              </span>
            </div>

            <!-- Weapons table (desktop) -->
            <div v-if="selectedManifestation.weapons?.length" class="card">
              <h3 class="font-bold text-squig-yellow mb-3">Weapons</h3>
              <table class="w-full text-sm">
                <thead>
                  <tr class="text-gray-500 text-xs border-b border-gray-700">
                    <th class="text-left pb-2 pr-3">Name</th>
                    <th class="pb-2 px-2">Range</th>
                    <th class="pb-2 px-2">Attacks</th>
                    <th class="pb-2 px-2">To Hit</th>
                    <th class="pb-2 px-2">To Wound</th>
                    <th class="pb-2 px-2">Rend</th>
                    <th class="pb-2 px-2">Damage</th>
                    <th class="text-left pb-2 pl-3">Ability</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="weapon in selectedManifestation.weapons" :key="weapon.name" class="border-b border-gray-800/50 last:border-0">
                    <td class="py-2 pr-3 text-left font-medium">{{ weapon.name }}</td>
                    <td class="py-2 px-2 text-center">{{ weapon.weapon_type === 'ranged' ? (weapon.range || '-') : '-' }}</td>
                    <td class="py-2 px-2 text-center">{{ weapon.attacks || '-' }}</td>
                    <td class="py-2 px-2 text-center">{{ weapon.hit || '-' }}</td>
                    <td class="py-2 px-2 text-center">{{ weapon.wound || '-' }}</td>
                    <td class="py-2 px-2 text-center">{{ weapon.rend || '-' }}</td>
                    <td class="py-2 px-2 text-center">{{ weapon.damage || '-' }}</td>
                    <td class="py-2 pl-3 text-left text-gray-400">{{ weapon.ability || '-' }}</td>
                  </tr>
                </tbody>
              </table>
            </div>

            <!-- Abilities -->
            <div v-if="selectedManifestation.abilities?.length" class="card">
              <h3 class="font-bold text-squig-yellow mb-3">Abilities</h3>
              <div class="space-y-3">
                <div v-for="ability in selectedManifestation.abilities" :key="ability.name" class="bg-gray-700/50 rounded-lg overflow-hidden">
                  <div :class="['px-3 py-1 text-xs font-medium', getAbilityPhaseClass(ability.color)]">
                    {{ ability.timing || (ability.ability_type === 'passive' ? 'Passive' : getAbilityPhaseLabel(ability.color)) }}
                  </div>
                  <div class="p-3">
                    <div class="flex items-start justify-between mb-1">
                      <h4 class="font-bold">{{ ability.name }}</h4>
                      <span :class="['text-xs px-2 py-0.5 rounded flex-shrink-0 ml-2', ability.ability_type === 'passive' ? 'bg-green-900/50 text-green-300' : 'bg-blue-900/50 text-blue-300']">{{ ability.ability_type }}</span>
                    </div>
                    <p v-if="ability.declare" class="text-sm text-gray-400 mb-2 whitespace-pre-wrap"><span class="font-medium text-gray-300">Declare:</span> {{ ability.declare }}</p>
                    <p v-if="ability.effect" class="text-sm text-gray-300 whitespace-pre-wrap">{{ ability.effect }}</p>
                    <div v-if="ability.keywords?.length" class="flex flex-wrap gap-1 mt-2 pt-2 border-t border-gray-600/50">
                      <span v-for="kw in ability.keywords" :key="kw" class="text-xs bg-gray-600/50 text-gray-400 px-2 py-0.5 rounded">{{ kw }}</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <!-- Summon ability -->
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
            <h2 class="text-xl font-bold text-squig-yellow">{{ selectedManifestation.name.replace(/^Summon\s+/, '') }}</h2>
            <p v-if="selectedManifestationLore" class="text-sm text-gray-400">{{ selectedManifestationLore.name }}</p>
          </div>
          <!-- Stats table (mobile) -->
          <div class="card overflow-hidden">
            <table class="w-full text-sm">
              <thead>
                <tr class="text-gray-400 border-b border-gray-700">
                  <th class="py-2 px-3 text-center">Move</th>
                  <th class="py-2 px-3 text-center">Health</th>
                  <th class="py-2 px-3 text-center">Save</th>
                  <th class="py-2 px-3 text-center">Ban</th>
                </tr>
              </thead>
              <tbody>
                <tr>
                  <td class="py-2 px-3 text-center font-bold text-lg">{{ selectedManifestation.move || '-' }}</td>
                  <td class="py-2 px-3 text-center font-bold text-lg">{{ selectedManifestation.health || '-' }}</td>
                  <td class="py-2 px-3 text-center font-bold text-lg">{{ selectedManifestation.save || '-' }}</td>
                  <td class="py-2 px-3 text-center font-bold text-lg">{{ selectedManifestation.banishment || '-' }}</td>
                </tr>
              </tbody>
            </table>
            <div v-if="selectedManifestation.casting_value" class="border-t border-gray-700 px-3 py-2 text-xs text-gray-500">
              Casting Value: <span class="text-purple-300 font-bold">{{ selectedManifestation.casting_value }}+</span>
            </div>
          </div>

          <!-- Weapons (mobile) -->
          <div v-if="selectedManifestation.weapons?.length" class="card">
            <h3 class="font-bold text-squig-yellow mb-3">Weapons</h3>
            <div class="space-y-2">
              <template v-for="weapon in selectedManifestation.weapons" :key="weapon.name">
                <div class="bg-gray-700/50 rounded-lg p-3">
                  <div class="flex items-center justify-between mb-1.5">
                    <h4 class="font-medium">{{ weapon.name }}</h4>
                    <span v-if="weapon.weapon_type === 'ranged'" class="text-sm font-bold text-white bg-gray-600/80 px-2 py-0.5 rounded">{{ weapon.range || '-' }}</span>
                  </div>
                  <div class="grid grid-cols-5 gap-1 text-center text-xs">
                    <div><span class="text-gray-500 block">Atk</span><span class="font-bold">{{ weapon.attacks || '-' }}</span></div>
                    <div><span class="text-gray-500 block">Hit</span><span class="font-bold">{{ weapon.hit || '-' }}</span></div>
                    <div><span class="text-gray-500 block">Wnd</span><span class="font-bold">{{ weapon.wound || '-' }}</span></div>
                    <div><span class="text-gray-500 block">Rnd</span><span class="font-bold">{{ weapon.rend || '-' }}</span></div>
                    <div><span class="text-gray-500 block">Dmg</span><span class="font-bold">{{ weapon.damage || '-' }}</span></div>
                  </div>
                  <p v-if="weapon.ability && weapon.ability !== '-'" class="text-xs text-gray-400 mt-1.5"><span class="text-gray-500">Ability:</span> {{ weapon.ability }}</p>
                </div>
              </template>
            </div>
          </div>

          <!-- Abilities -->
          <div v-if="selectedManifestation.abilities?.length" class="card">
            <h3 class="font-bold text-squig-yellow mb-3">Abilities</h3>
            <div class="space-y-3">
              <div v-for="ability in selectedManifestation.abilities" :key="ability.name" class="bg-gray-700/50 rounded-lg overflow-hidden">
                <div :class="['px-3 py-1 text-xs font-medium', getAbilityPhaseClass(ability.color)]">
                  {{ ability.timing || (ability.ability_type === 'passive' ? 'Passive' : getAbilityPhaseLabel(ability.color)) }}
                </div>
                <div class="p-3">
                  <div class="flex items-start justify-between mb-1">
                    <h4 class="font-bold">{{ ability.name }}</h4>
                    <span :class="['text-xs px-2 py-0.5 rounded flex-shrink-0 ml-2', ability.ability_type === 'passive' ? 'bg-green-900/50 text-green-300' : 'bg-blue-900/50 text-blue-300']">{{ ability.ability_type }}</span>
                  </div>
                  <p v-if="ability.declare" class="text-sm text-gray-400 mb-2 whitespace-pre-wrap"><span class="font-medium text-gray-300">Declare:</span> {{ ability.declare }}</p>
                  <p v-if="ability.effect" class="text-sm text-gray-300 whitespace-pre-wrap">{{ ability.effect }}</p>
                  <div v-if="ability.keywords?.length" class="flex flex-wrap gap-1 mt-2 pt-2 border-t border-gray-600/50">
                    <span v-for="kw in ability.keywords" :key="kw" class="text-xs bg-gray-600/50 text-gray-400 px-2 py-0.5 rounded">{{ kw }}</span>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- Summon ability -->
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
          <p v-if="selectedManifestationLore.points" class="text-squig-yellow font-bold">{{ selectedManifestationLore.points }} pts</p>
        </div>

        <div class="lg:w-1/2 space-y-1">
          <div
            v-for="manifestation in selectedManifestationLore.manifestations"
            :key="manifestation.id"
            @click="selectManifestation(manifestation)"
            class="bg-gray-700/50 rounded px-3 py-2 cursor-pointer hover:bg-gray-600/50 transition-colors"
          >
            <span class="text-sm font-medium">{{ manifestation.name.replace(/^Summon\s+/, '') }}</span>
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
          @select-manifestation="loadFactionManifestation"
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
              <span v-if="lore.points" class="text-sm text-squig-yellow font-bold">{{ lore.points }} pts</span>
            </div>
          </div>
        </div>

        <!-- Battle Tactics -->
        <div v-if="battleTactics.length > 0" class="mt-12">
          <div class="flex items-center gap-3 mb-6">
            <h2 class="text-xl font-bold text-amber-400">Battle Tactics</h2>
            <div class="flex-1 h-px bg-amber-400/30"></div>
          </div>

          <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
            <div
              v-for="tactic in battleTactics"
              :key="tactic.id"
              @click="toggleBattleTactic(tactic.id)"
              class="card cursor-pointer transition-colors"
              :class="isTacticExpanded(tactic.id) ? 'border-amber-500/50' : 'hover:border-amber-500/30'"
            >
              <div class="flex items-center justify-between">
                <span class="font-medium text-amber-300">{{ tactic.name }}</span>
                <!-- Chevron only on mobile -->
                <svg
                  class="w-4 h-4 text-gray-500 transition-transform lg:hidden"
                  :class="{ 'rotate-180': isTacticExpanded(tactic.id) }"
                  fill="none" stroke="currentColor" viewBox="0 0 24 24"
                >
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
                </svg>
              </div>

              <!-- Expanded: 3 phase steps -->
              <div v-if="isTacticExpanded(tactic.id)" class="mt-3 space-y-2" @click.stop>
                <p v-if="tactic.card_rules" class="text-xs text-gray-400 mb-3">{{ tactic.card_rules }}</p>

                <!-- Affray -->
                <div v-if="tactic.affray_name || tactic.affray_effect" class="rounded bg-red-900/20 border border-red-800/30 p-2.5">
                  <div class="flex items-center gap-2 mb-1">
                    <span class="text-[10px] font-bold uppercase tracking-wider text-red-400">1. Affray</span>
                    <span v-if="tactic.affray_name" class="text-xs font-medium text-red-300">{{ tactic.affray_name }}</span>
                  </div>
                  <p v-if="tactic.affray_effect" class="text-xs text-gray-300 whitespace-pre-wrap">{{ tactic.affray_effect }}</p>
                </div>

                <!-- Strike -->
                <div v-if="tactic.strike_name || tactic.strike_effect" class="rounded bg-orange-900/20 border border-orange-800/30 p-2.5">
                  <div class="flex items-center gap-2 mb-1">
                    <span class="text-[10px] font-bold uppercase tracking-wider text-orange-400">2. Strike</span>
                    <span v-if="tactic.strike_name" class="text-xs font-medium text-orange-300">{{ tactic.strike_name }}</span>
                  </div>
                  <p v-if="tactic.strike_effect" class="text-xs text-gray-300 whitespace-pre-wrap">{{ tactic.strike_effect }}</p>
                </div>

                <!-- Domination -->
                <div v-if="tactic.domination_name || tactic.domination_effect" class="rounded bg-blue-900/20 border border-blue-800/30 p-2.5">
                  <div class="flex items-center gap-2 mb-1">
                    <span class="text-[10px] font-bold uppercase tracking-wider text-blue-400">3. Domination</span>
                    <span v-if="tactic.domination_name" class="text-xs font-medium text-blue-300">{{ tactic.domination_name }}</span>
                  </div>
                  <p v-if="tactic.domination_effect" class="text-xs text-gray-300 whitespace-pre-wrap">{{ tactic.domination_effect }}</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </template>
    </template>

    <!-- Disclaimer -->
    <p class="text-xs text-gray-600 text-center mt-8">Squig League is not affiliated with Games Workshop.<br>It only displays data from <a href="https://github.com/BSData/age-of-sigmar-4th" target="_blank" class="underline hover:text-gray-400">BSData</a>.</p>
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
import UnitStatCircle from '../components/rules/UnitStatCircle.vue'

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
const battleTactics = ref([])
const allTacticsExpanded = ref(false)
const expandedTacticIds = ref(new Set())

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
    const [gaResponse, factionsResponse, loresResponse, tacticsResponse] = await Promise.all([
      axios.get(`${API_URL}/bsdata/grand-alliances`),
      axios.get(`${API_URL}/bsdata/factions?include_aor=true`),
      axios.get(`${API_URL}/bsdata/manifestation-lores`),
      axios.get(`${API_URL}/bsdata/battle-tactics`),
    ])

    grandAlliances.value = gaResponse.data
    factions.value = factionsResponse.data
    universalManifestationLores.value = loresResponse.data
    battleTactics.value = tacticsResponse.data
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
  window.scrollTo(0, 0)
  router.push({ name: 'RulesFaction', params: { factionSlug: toSlug(faction.name) } })
}

const loadUnit = async (unitId, unitName) => {
  try {
    const response = await axios.get(`${API_URL}/bsdata/units/${unitId}`)
    selectedUnit.value = response.data
    window.scrollTo(0, 0)
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
  window.scrollTo(0, 0)
  router.push({ name: 'RulesFaction', params: { factionSlug: toSlug(lore.name) } })
}

const isDesktop = () => window.matchMedia('(min-width: 1024px)').matches

const getAbilityPhaseLabel = (color) => {
  const phases = {
    'Yellow': 'Hero Phase', 'Red': 'Combat Phase', 'Blue': 'Movement Phase',
    'Green': 'Start of Turn', 'Purple': 'Shooting Phase', 'Orange': 'Charge Phase',
    'Grey': 'Passive', 'Gray': 'Passive', 'Black': 'Deployment', 'Cyan': 'Any Phase',
  }
  return phases[color] || color
}

const getAbilityPhaseClass = (color) => {
  const classes = {
    'Yellow': 'bg-yellow-800/60 text-yellow-200', 'Red': 'bg-red-900/60 text-red-200',
    'Blue': 'bg-blue-800/60 text-blue-200', 'Green': 'bg-gray-700/60 text-gray-300',
    'Purple': 'bg-purple-900/60 text-purple-200', 'Orange': 'bg-orange-800/60 text-orange-200',
    'Grey': 'bg-green-900/60 text-green-200', 'Gray': 'bg-green-900/60 text-green-200',
    'Black': 'bg-gray-800/60 text-gray-300', 'Cyan': 'bg-cyan-900/60 text-cyan-200',
  }
  return classes[color] || 'bg-gray-700/60 text-gray-300'
}

const isTacticExpanded = (tacticId) => {
  return allTacticsExpanded.value || expandedTacticIds.value.has(tacticId)
}

const toggleBattleTactic = (tacticId) => {
  if (isDesktop()) {
    allTacticsExpanded.value = !allTacticsExpanded.value
  } else {
    const newSet = new Set(expandedTacticIds.value)
    if (newSet.has(tacticId)) {
      newSet.delete(tacticId)
    } else {
      newSet.add(tacticId)
    }
    expandedTacticIds.value = newSet
  }
}

const loadFactionManifestation = (manifestation) => {
  selectedManifestation.value = manifestation
  window.scrollTo(0, 0)
  if (selectedFaction.value) {
    router.push({
      name: 'RulesUnit',
      params: {
        factionSlug: toSlug(selectedFaction.value.name),
        unitSlug: toSlug(manifestation.name)
      }
    })
  }
}

const selectManifestation = (manifestation) => {
  selectedManifestation.value = manifestation
  window.scrollTo(0, 0)
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
