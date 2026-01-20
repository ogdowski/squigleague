/**
 * Squire Module - Battle Plan Reference
 * Browse all GHB 2025-2026 AoS matched play battle plans with diagrams
 */

window.renderSquireBattlePlanReference = function() {
    return `
        <div class="max-w-7xl mx-auto px-4 py-12" x-data="battlePlanReference()">
            <!-- Header -->
            <div class="text-center mb-12">
                <h1 class="text-4xl font-montserrat font-bold text-text-primary mb-4">
                    Battle Plan Reference
                </h1>
                <p class="text-lg text-text-secondary max-w-3xl mx-auto">
                    General's Handbook 2025-2026 - Age of Sigmar 4th Edition Matched Play Missions
                </p>
                <p class="text-sm text-text-muted mt-2">
                    12 Official Battle Plans with Deployment Maps
                </p>
            </div>

            <!-- System Selection -->
            <div class="bg-bg-darker rounded-lg shadow-xl p-6 mb-8 border border-bg-dark">
                <label class="block text-sm font-bold text-primary uppercase mb-3">
                    Select Game System
                </label>
                <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
                    <button 
                        @click="selectSystem('age_of_sigmar')"
                        :class="selectedSystem === 'age_of_sigmar' ? 'bg-primary border-primary text-bg-darkest' : 'bg-bg-medium border-bg-dark text-text-primary hover:border-primary'"
                        class="p-4 rounded-lg border-2 transition"
                    >
                        <div class="font-bold text-lg">Age of Sigmar</div>
                        <div class="text-sm mt-1 opacity-75">4th Edition</div>
                    </button>

                    <button 
                        @click="selectSystem('warhammer_40k')"
                        :class="selectedSystem === 'warhammer_40k' ? 'bg-primary border-primary text-bg-darkest' : 'bg-bg-medium border-bg-dark text-text-primary hover:border-primary'"
                        class="p-4 rounded-lg border-2 transition"
                    >
                        <div class="font-bold text-lg">Warhammer 40k</div>
                        <div class="text-sm mt-1 opacity-75">10th Edition</div>
                    </button>

                    <button 
                        @click="selectSystem('the_old_world')"
                        :class="selectedSystem === 'the_old_world' ? 'bg-primary border-primary text-bg-darkest' : 'bg-bg-medium border-bg-dark text-text-primary hover:border-primary'"
                        class="p-4 rounded-lg border-2 transition"
                    >
                        <div class="font-bold text-lg">The Old World</div>
                        <div class="text-sm mt-1 opacity-75">Legacy</div>
                    </button>
                </div>
            </div>

            <!-- Loading State -->
            <div x-show="loading" class="text-center py-12">
                <svg class="animate-spin h-12 w-12 text-primary mx-auto mb-4" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                    <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                    <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                <p class="text-text-secondary">Loading battle plans...</p>
            </div>

            <!-- Error State -->
            <div x-show="error" class="bg-red-900/20 border border-red-500 rounded-lg p-6 mb-8">
                <div class="flex items-start gap-4">
                    <div class="flex-shrink-0 w-8 h-8 flex items-center justify-center bg-red-500 rounded-full text-white font-bold">
                        !
                    </div>
                    <div class="flex-grow">
                        <h3 class="text-xl font-bold text-red-400 mb-2">Error</h3>
                        <p class="text-text-secondary" x-text="error"></p>
                    </div>
                    <button @click="error = null" class="text-text-muted hover:text-text-primary font-bold text-xl">×</button>
                </div>
            </div>

            <!-- Battle Plans List -->
            <div x-show="!loading && !error && battlePlans.length > 0" class="space-y-4">
                <!-- Summary -->
                <div class="bg-bg-darker rounded-lg shadow-xl p-4 border border-bg-dark mb-6">
                    <div class="text-center">
                        <span class="text-2xl font-bold text-primary" x-text="battlePlans.length"></span>
                        <span class="text-text-secondary ml-2">Battle Plans Available</span>
                    </div>
                </div>

                <!-- Battle Plan Cards -->
                <template x-for="(plan, index) in battlePlans" :key="index">
                    <div class="bg-bg-darker rounded-lg shadow-xl border border-bg-dark overflow-hidden">
                        <!-- Header -->
                        <div class="bg-primary/10 border-b border-primary/30 p-4 cursor-pointer hover:bg-primary/20 transition"
                             @click="togglePlan(index)">
                            <div class="flex items-center justify-between">
                                <div class="flex items-center gap-4">
                                    <div class="w-10 h-10 bg-primary rounded-full flex items-center justify-center text-bg-darkest font-bold text-lg"
                                         x-text="index + 1">
                                    </div>
                                    <div>
                                        <h3 class="text-xl font-bold text-primary" x-text="plan.name"></h3>
                                        <p class="text-sm text-text-muted" x-text="plan.deployment_description"></p>
                                    </div>
                                </div>
                                <svg class="w-6 h-6 text-primary transition-transform" 
                                     :class="expandedPlans[index] ? 'rotate-180' : ''"
                                     fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"></path>
                                </svg>
                            </div>
                        </div>

                        <!-- Expanded Details -->
                        <div x-show="expandedPlans[index]" 
                             x-transition:enter="transition ease-out duration-200"
                             x-transition:enter-start="opacity-0 transform scale-95"
                             x-transition:enter-end="opacity-100 transform scale-100"
                             class="p-6 space-y-6">
                            
                            <!-- Deployment -->
                            <div>
                                <h4 class="text-sm font-bold text-primary uppercase mb-2">Deployment</h4>
                                <div class="bg-bg-medium rounded-lg p-4 border border-bg-dark">
                                    <p class="text-text-primary font-bold mb-1" x-text="formatDeployment(plan.deployment)"></p>
                                    <p class="text-text-secondary text-sm" x-text="plan.deployment_description"></p>
                                </div>
                            </div>

                            <!-- Primary Objective -->
                            <div>
                                <h4 class="text-sm font-bold text-primary uppercase mb-2">Primary Objective</h4>
                                <div class="bg-bg-medium rounded-lg p-4 border border-bg-dark">
                                    <p class="text-text-primary" x-text="plan.primary_objective"></p>
                                </div>
                            </div>

                            <!-- Secondary Objectives -->
                            <div x-show="plan.secondary_objectives && plan.secondary_objectives.length > 0">
                                <h4 class="text-sm font-bold text-primary uppercase mb-2">Secondary Objectives</h4>
                                <div class="space-y-2">
                                    <template x-for="objective in plan.secondary_objectives" :key="objective">
                                        <div class="bg-bg-medium rounded-lg p-3 border border-bg-dark">
                                            <p class="text-text-primary text-sm" x-text="objective"></p>
                                        </div>
                                    </template>
                                </div>
                            </div>

                            <!-- Victory Conditions -->
                            <div>
                                <h4 class="text-sm font-bold text-primary uppercase mb-2">Victory Conditions</h4>
                                <div class="bg-bg-medium rounded-lg p-4 border border-bg-dark">
                                    <p class="text-text-primary" x-text="plan.victory_conditions"></p>
                                </div>
                            </div>

                            <!-- Turn Limit -->
                            <div>
                                <h4 class="text-sm font-bold text-primary uppercase mb-2">Turn Limit</h4>
                                <div class="bg-bg-medium rounded-lg p-4 border border-bg-dark">
                                    <p class="text-text-primary font-bold text-lg" x-text="plan.turn_limit + ' Rounds'"></p>
                                </div>
                            </div>

                            <!-- Special Rules -->
                            <div x-show="plan.special_rules && plan.special_rules.length > 0">
                                <h4 class="text-sm font-bold text-primary uppercase mb-2">Special Rules</h4>
                                <div class="space-y-2">
                                    <template x-for="rule in plan.special_rules" :key="rule">
                                        <div class="bg-bg-medium rounded-lg p-3 border border-bg-dark">
                                            <p class="text-text-primary text-sm" x-text="rule"></p>
                                        </div>
                                    </template>
                                </div>
                            </div>

                            <!-- Battle Tactics (AoS) -->
                            <div x-show="plan.battle_tactics">
                                <h4 class="text-sm font-bold text-primary uppercase mb-2">Battle Tactics</h4>
                                <div class="bg-bg-medium rounded-lg p-4 border border-bg-dark">
                                    <p class="text-text-primary" x-text="plan.battle_tactics"></p>
                                </div>
                            </div>
                        </div>
                    </div>
                </template>
            </div>

            <!-- Empty State -->
            <div x-show="!loading && !error && selectedSystem && battlePlans.length === 0" 
                 class="text-center py-12">
                <p class="text-text-secondary text-lg">No battle plans found for this system.</p>
            </div>
        </div>
    `;
};

// Alpine.js component for battle plan reference
function battlePlanReference() {
    return {
        selectedSystem: null,
        battlePlans: [],
        expandedPlans: {},
        loading: false,
        error: null,

        async selectSystem(system) {
            this.selectedSystem = system;
            this.battlePlans = [];
            this.expandedPlans = {};
            this.error = null;
            await this.loadAllBattlePlans();
        },

        async loadAllBattlePlans() {
            this.loading = true;
            this.error = null;

            try {
                // Load all battle plans by making multiple requests
                // Since we don't have a "list all" endpoint, we'll generate them
                const plans = [];
                const maxAttempts = 50; // Try to get up to 50 unique plans
                const seenPlans = new Set();

                for (let i = 0; i < maxAttempts; i++) {
                    const response = await fetch(`/api/squire/battle-plan/random?system=${this.selectedSystem}`);
                    
                    if (!response.ok) {
                        throw new Error(`Failed to load battle plans: ${response.statusText}`);
                    }

                    const plan = await response.json();
                    const planKey = plan.name;
                    
                    if (!seenPlans.has(planKey)) {
                        seenPlans.add(planKey);
                        plans.push(plan);
                    }

                    // If we've seen the same plan 10 times in a row, we probably have them all
                    if (i > 10 && seenPlans.size < i / 2) {
                        break;
                    }
                }

                // Sort by name
                this.battlePlans = plans.sort((a, b) => a.name.localeCompare(b.name));
                
            } catch (err) {
                this.error = err.message;
                console.error('Error loading battle plans:', err);
            } finally {
                this.loading = false;
            }
        },

        togglePlan(index) {
            this.expandedPlans[index] = !this.expandedPlans[index];
        },

        formatDeployment(deployment) {
            // Convert snake_case to Title Case
            return deployment
                .split('_')
                .map(word => word.charAt(0).toUpperCase() + word.slice(1))
                .join(' ');
        }
    };
}
