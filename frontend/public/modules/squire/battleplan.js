/**
 * Squire Module - Battle Plan Randomizer
 * Selects random battle plans for Age of Sigmar, 40k, and The Old World
 */

window.renderSquireBattlePlan = function() {
    return `
        <div class="max-w-4xl mx-auto px-4 py-12" x-data="battlePlanGenerator()">
            <!-- Header -->
            <div class="text-center mb-12">
                <h1 class="text-4xl font-montserrat font-bold text-text-primary mb-4">
                    Battle Plan Reference
                </h1>
                <p class="text-lg text-text-secondary max-w-2xl mx-auto">
                    Browse and randomize battle plans for practice and reference. 
                    Supports Age of Sigmar (General's Handbook 2025-2026), Warhammer 40k, and The Old World.
                </p>
                <div class="mt-4 p-4 bg-bg-dark rounded-lg border border-primary/30 max-w-3xl mx-auto">
                    <p class="text-sm text-text-muted">
                        <strong class="text-primary">Note:</strong> This is a reference tool for practice. 
                        In tournaments, battle plans are automatically selected when both players submit their lists.
                    </p>
                </div>
            </div>

            <!-- Game System Selection -->
            <div class="bg-bg-darker rounded-lg shadow-xl p-8 mb-8 border border-bg-dark">
                <h2 class="text-2xl font-montserrat font-bold text-text-primary mb-6">
                    Select Game System
                </h2>
                
                <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
                    <!-- Age of Sigmar -->
                    <button 
                        @click="selectSystem('age_of_sigmar')"
                        :class="selectedSystem === 'age_of_sigmar' ? 'bg-primary border-primary text-bg-darkest' : 'bg-bg-medium border-bg-dark text-text-primary hover:border-primary'"
                        class="p-6 rounded-lg border-2 transition duration-300 transform hover:scale-105"
                    >
                        <div class="text-2xl font-bold mb-2">AoS</div>
                        <div class="font-bold text-lg">Age of Sigmar</div>
                        <div class="text-sm mt-2 opacity-75">4th Edition</div>
                    </button>

                    <!-- Warhammer 40k -->
                    <button 
                        @click="selectSystem('warhammer_40k')"
                        :class="selectedSystem === 'warhammer_40k' ? 'bg-primary border-primary text-bg-darkest' : 'bg-bg-medium border-bg-dark text-text-primary hover:border-primary'"
                        class="p-6 rounded-lg border-2 transition duration-300 transform hover:scale-105"
                    >
                        <div class="text-2xl font-bold mb-2">40K</div>
                        <div class="font-bold text-lg">Warhammer 40k</div>
                        <div class="text-sm mt-2 opacity-75">10th Edition</div>
                    </button>

                    <!-- The Old World -->
                    <button 
                        @click="selectSystem('the_old_world')"
                        :class="selectedSystem === 'the_old_world' ? 'bg-primary border-primary text-bg-darkest' : 'bg-bg-medium border-bg-dark text-text-primary hover:border-primary'"
                        class="p-6 rounded-lg border-2 transition duration-300 transform hover:scale-105"
                    >
                        <div class="text-2xl font-bold mb-2">TOW</div>
                        <div class="font-bold text-lg">The Old World</div>
                        <div class="text-sm mt-2 opacity-75">Legacy</div>
                    </button>
                </div>

                <!-- Randomize Button -->
                <div class="mt-8 text-center">
                    <button 
                        @click="generateBattlePlan()"
                        :disabled="!selectedSystem || loading"
                        class="px-8 py-4 bg-primary hover:bg-primary-dark text-bg-darkest font-bold text-lg rounded-lg shadow-lg transition duration-300 transform hover:scale-105 disabled:opacity-50 disabled:cursor-not-allowed disabled:transform-none"
                    >
                        <span x-show="!loading">Randomize Battle Plan</span>
                        <span x-show="loading">
                            <svg class="animate-spin h-5 w-5 inline-block mr-2" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                            </svg>
                            Generating...
                        </span>
                    </button>
                </div>
            </div>

            <!-- Error Display -->
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

            <!-- Battle Plan Display -->
            <div x-show="battlePlan" x-cloak class="bg-bg-darker rounded-lg shadow-xl p-8 border border-primary/30">
                <!-- Mission Name -->
                <div class="text-center mb-8 pb-6 border-b border-bg-dark">
                    <h2 class="text-3xl font-montserrat font-bold text-primary mb-2" x-text="battlePlan?.name"></h2>
                    <p class="text-text-secondary" x-text="getSystemName(battlePlan?.game_system)"></p>
                </div>

                <!-- Core Info Grid -->
                <div class="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
                    <!-- Deployment -->
                    <div class="bg-bg-medium rounded-lg p-6">
                        <h3 class="text-sm font-bold text-primary uppercase mb-2">Deployment</h3>
                        <p class="text-text-primary text-lg" x-text="battlePlan?.deployment_description"></p>
                    </div>

                    <!-- Turn Limit -->
                    <div class="bg-bg-medium rounded-lg p-6">
                        <h3 class="text-sm font-bold text-primary uppercase mb-2">Battle Length</h3>
                        <p class="text-text-primary text-lg">
                            <span x-text="battlePlan?.turn_limit"></span> Battle Rounds
                        </p>
                    </div>
                </div>

                <!-- Primary Objective -->
                <div class="bg-bg-medium rounded-lg p-6 mb-6">
                    <h3 class="text-lg font-bold text-primary mb-3 uppercase tracking-wide">Primary Objective</h3>
                    <p class="text-text-primary text-lg" x-text="battlePlan?.primary_objective"></p>
                </div>

                <!-- Victory Conditions -->
                <div class="bg-bg-medium rounded-lg p-6 mb-6">
                    <h3 class="text-lg font-bold text-primary mb-3 uppercase tracking-wide">Victory Conditions</h3>
                    <p class="text-text-primary" x-text="battlePlan?.victory_conditions"></p>
                </div>

                <!-- Secondary Objectives -->
                <div x-show="battlePlan?.secondary_objectives?.length > 0" class="bg-bg-medium rounded-lg p-6 mb-6">
                    <h3 class="text-lg font-bold text-primary mb-3 uppercase tracking-wide">Secondary Objectives</h3>
                    <ul class="space-y-2">
                        <template x-for="objective in battlePlan?.secondary_objectives" :key="objective">
                            <li class="flex items-start gap-2">
                                <span class="text-primary font-bold">•</span>
                                <span class="text-text-primary" x-text="objective"></span>
                            </li>
                        </template>
                    </ul>
                </div>

                <!-- Special Rules -->
                <div x-show="battlePlan?.special_rules?.length > 0" class="bg-bg-medium rounded-lg p-6 mb-6">
                    <h3 class="text-lg font-bold text-primary mb-3 uppercase tracking-wide">Special Rules</h3>
                    <ul class="space-y-2">
                        <template x-for="rule in battlePlan?.special_rules" :key="rule">
                            <li class="flex items-start gap-2">
                                <span class="text-primary font-bold">•</span>
                                <span class="text-text-primary" x-text="rule"></span>
                            </li>
                        </template>
                    </ul>
                </div>

                <!-- Battle Tactics -->
                <div x-show="battlePlan?.battle_tactics?.length > 0" class="bg-bg-medium rounded-lg p-6 mb-6">
                    <h3 class="text-lg font-bold text-primary mb-3 uppercase tracking-wide">Battle Tactics</h3>
                    <ul class="space-y-2">
                        <template x-for="tactic in battlePlan?.battle_tactics" :key="tactic">
                            <li class="flex items-start gap-2">
                                <span class="text-primary font-bold">•</span>
                                <span class="text-text-primary" x-text="tactic"></span>
                            </li>
                        </template>
                    </ul>
                </div>

                <!-- Actions -->
                <div class="flex gap-4 justify-center mt-8 pt-6 border-t border-bg-dark">
                    <button 
                        @click="generateBattlePlan()"
                        class="px-6 py-3 bg-primary hover:bg-primary-dark text-bg-darkest font-bold rounded-lg shadow-lg transition duration-300"
                    >
                        Randomize Another
                    </button>
                    <button 
                        @click="printBattlePlan()"
                        class="px-6 py-3 bg-bg-dark hover:bg-bg-medium text-text-primary font-bold rounded-lg border border-bg-dark transition"
                    >
                        Print
                    </button>
                </div>
            </div>

            <!-- How It Works -->
            <div class="mt-12 bg-bg-dark rounded-lg p-8 border border-bg-medium">
                <h3 class="text-2xl font-montserrat font-bold text-text-primary mb-4">About This Tool</h3>
                <div class="space-y-3 text-text-secondary">
                    <p><strong class="text-text-primary">Practice & Reference:</strong> Use this tool to familiarize yourself with mission types and practice different scenarios before tournaments.</p>
                    <p><strong class="text-text-primary">Tournament Play:</strong> In official SquigLeague tournaments, battle plans are automatically selected when both players submit their army lists. You cannot manually select or change the assigned battle plan.</p>
                    <p><strong class="text-text-primary">Fair Competition:</strong> The automated system ensures unbiased mission selection and prevents players from cherry-picking favorable matchups.</p>
                </div>
            </div>
        </div>
    `;
};

// Alpine.js component for battle plan randomizer
function battlePlanGenerator() {
    return {
        selectedSystem: null,
        battlePlan: null,
        loading: false,
        error: null,

        selectSystem(system) {
            this.selectedSystem = system;
            this.error = null;
        },

        async generateBattlePlan() {
            if (!this.selectedSystem) {
                this.error = 'Please select a game system first';
                return;
            }

            this.loading = true;
            this.error = null;

            try {
                const response = await fetch(`/api/squire/battle-plan/random?system=${this.selectedSystem}`, {
                    headers: {
                        'User-Agent': 'Squire-Frontend/1.0'
                    }
                });

                if (!response.ok) {
                    throw new Error(`Failed to randomize battle plan: ${response.statusText}`);
                }

                this.battlePlan = await response.json();
            } catch (err) {
                this.error = err.message;
                console.error('Error generating battle plan:', err);
            } finally {
                this.loading = false;
            }
        },

        getSystemName(system) {
            const names = {
                'age_of_sigmar': 'Age of Sigmar (General\'s Handbook 2025-2026)',
                'warhammer_40k': 'Warhammer 40,000 (10th Edition)',
                'the_old_world': 'Warhammer: The Old World'
            };
            return names[system] || system;
        },

        printBattlePlan() {
            window.print();
        }
    };
}
