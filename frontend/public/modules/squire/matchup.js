/**
 * Squire Module - Matchup System
 * Create matchups, submit lists, and reveal battle plans
 */

window.renderSquireMatchup = function() {
    return `
        <div class="max-w-6xl mx-auto px-4 py-12" x-data="matchupManager()">
            <!-- Header -->
            <div class="text-center mb-12">
                <h1 class="text-4xl font-montserrat font-bold text-text-primary mb-4">
                    Matchup System
                </h1>
                <p class="text-lg text-text-secondary max-w-2xl mx-auto">
                    Share army lists with your opponent and receive a randomized battle plan.
                </p>
            </div>

            <!-- Create New Matchup -->
            <div x-show="!matchupId && !loadingMatchup" class="bg-bg-darker rounded-lg shadow-xl p-8 mb-8 border border-bg-dark">
                <h2 class="text-2xl font-montserrat font-bold text-text-primary mb-6">
                    Create New Matchup
                </h2>
                
                <div class="space-y-6">
                    <!-- System Selection - AoS Only -->
                    <div>
                        <label class="block text-sm font-bold text-primary uppercase mb-3">
                            Game System
                        </label>
                        <div class="max-w-md mx-auto">
                            <div class="p-6 bg-primary border-2 border-primary rounded-lg text-center">
                                <div class="font-bold text-2xl text-bg-darkest mb-2">Age of Sigmar</div>
                                <div class="text-bg-darkest opacity-75">4th Edition - General's Handbook 2025-2026</div>
                                <div class="text-bg-darkest text-sm mt-2">12 Official Matched Play Missions</div>
                            </div>
                        </div>
                    </div>

                    <!-- Create Button -->
                    <div class="text-center">
                        <button 
                            @click="createMatchup()"
                            :disabled="!selectedSystem || creating"
                            class="px-8 py-4 bg-primary hover:bg-primary-dark text-bg-darkest font-bold text-lg rounded-lg shadow-lg transition disabled:opacity-50 disabled:cursor-not-allowed"
                        >
                            <span x-show="!creating">Create Matchup</span>
                            <span x-show="creating">Creating...</span>
                        </button>
                    </div>
                </div>
            </div>

            <!-- Matchup Created - Share Link and Submit -->
            <div x-show="matchupId && !matchup?.is_complete && !hasSubmitted && !loadingMatchup" class="bg-bg-darker rounded-lg shadow-xl p-8 mb-8 border border-primary/30">
                <h2 class="text-2xl font-montserrat font-bold text-primary mb-6">
                    <span x-show="!matchup">Matchup Created</span>
                    <span x-show="matchup && canSubmit()">Join Matchup</span>
                </h2>
                
                <div class="space-y-6">
                    <!-- Share Link (only show if no opponent yet) -->
                    <div x-show="!matchup || !hasOpponent()">
                        <label class="block text-sm font-bold text-text-primary uppercase mb-2">
                            Share This Link With Your Opponent
                        </label>
                        <div class="flex gap-2">
                            <input 
                                type="text" 
                                :value="getShareUrl()" 
                                readonly
                                class="flex-grow px-4 py-3 bg-bg-medium text-text-primary rounded-lg border border-bg-dark font-mono text-sm"
                            >
                            <button 
                                @click="copyShareLink()"
                                class="px-6 py-3 bg-primary hover:bg-primary-dark text-bg-darkest font-bold rounded-lg transition"
                            >
                                Copy
                            </button>
                        </div>
                        <p class="text-sm text-text-muted mt-2">
                            Both you and your opponent must submit army lists before the battle plan is revealed.
                        </p>
                    </div>

                    <!-- Show opponent's name if they already submitted -->
                    <div x-show="matchup && hasOpponent()" class="bg-bg-medium rounded-lg p-4 border border-bg-dark">
                        <div class="flex items-center gap-3">
                            <div class="w-10 h-10 bg-primary rounded-full flex items-center justify-center text-bg-darkest font-bold">
                                <span x-text="(matchup?.player1?.name || matchup?.player2?.name || 'P')[0]"></span>
                            </div>
                            <div>
                                <div class="text-sm text-text-muted">Opponent</div>
                                <div class="font-bold text-text-primary" x-text="matchup?.player1?.name || matchup?.player2?.name"></div>
                            </div>
                        </div>
                        <p class="text-sm text-text-muted mt-3">
                            Waiting for you to submit your army list.
                        </p>
                    </div>

                    <!-- Submit Your List -->
                    <div>
                        <label class="block text-sm font-bold text-text-primary uppercase mb-2">
                            Your Name
                        </label>
                        <input 
                            type="text" 
                            x-model="playerName"
                            placeholder="Enter your name"
                            class="w-full px-4 py-3 bg-bg-medium text-text-primary rounded-lg border border-bg-dark mb-4"
                        >

                        <label class="block text-sm font-bold text-text-primary uppercase mb-2">
                            Your Army List
                        </label>
                        <textarea 
                            x-model="armyList"
                            rows="10"
                            placeholder="Paste your army list here..."
                            class="w-full px-4 py-3 bg-bg-medium text-text-primary rounded-lg border border-bg-dark font-mono text-sm"
                        ></textarea>

                        <button 
                            @click="submitList()"
                            :disabled="!playerName || !armyList || submitting"
                            class="mt-4 px-6 py-3 bg-primary hover:bg-primary-dark text-bg-darkest font-bold rounded-lg transition disabled:opacity-50 disabled:cursor-not-allowed"
                        >
                            <span x-show="!submitting">Submit My List</span>
                            <span x-show="submitting">Submitting...</span>
                        </button>
                    </div>
                </div>
            </div>

            <!-- Waiting for Opponent -->
            <div x-show="hasSubmitted && !matchup?.is_complete" class="bg-bg-darker rounded-lg shadow-xl p-8 mb-8 border border-primary/30">
                <div class="text-center">
                    <h2 class="text-2xl font-montserrat font-bold text-primary mb-4">
                        List Submitted
                    </h2>
                    <p class="text-text-secondary mb-4">
                        Waiting for your opponent to submit their list...
                    </p>
                    <div class="inline-block">
                        <svg class="animate-spin h-8 w-8 text-primary" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                            <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                        </svg>
                    </div>
                    <p class="text-sm text-text-muted mt-4">
                        Refreshing automatically...
                    </p>
                </div>
            </div>

            <!-- Matchup Summary (Both Lists + Battle Plan) -->
            <div x-show="matchup?.is_complete" class="space-y-6">
                <!-- Battle Plan -->
                <div class="bg-bg-darker rounded-lg shadow-xl p-8 border border-primary/30">
                    <h2 class="text-2xl font-montserrat font-bold text-primary mb-6 text-center">
                        Battle Plan: <span x-text="matchup?.battle_plan?.name"></span>
                    </h2>
                    
                    <!-- Deployment & Length -->
                    <div class="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
                        <div class="bg-bg-medium rounded-lg p-6">
                            <h3 class="text-sm font-bold text-primary uppercase mb-2">Deployment</h3>
                            <p class="text-text-primary" x-text="matchup?.battle_plan?.deployment_description"></p>
                        </div>
                        <div class="bg-bg-medium rounded-lg p-6">
                            <h3 class="text-sm font-bold text-primary uppercase mb-2">Battle Length</h3>
                            <p class="text-text-primary text-lg">
                                <span x-text="matchup?.battle_plan?.turn_limit"></span> Battle Rounds
                            </p>
                        </div>
                    </div>

                    <!-- Primary Objective -->
                    <div class="bg-bg-medium rounded-lg p-6 mb-6">
                        <h3 class="text-lg font-bold text-primary mb-3 uppercase tracking-wide">Primary Objective</h3>
                        <p class="text-text-primary" x-text="matchup?.battle_plan?.primary_objective"></p>
                    </div>

                    <!-- Victory Conditions -->
                    <div class="bg-bg-medium rounded-lg p-6">
                        <h3 class="text-lg font-bold text-primary mb-3 uppercase tracking-wide">Victory Conditions</h3>
                        <p class="text-text-primary" x-text="matchup?.battle_plan?.victory_conditions"></p>
                    </div>
                </div>

                <!-- Army Lists Side by Side -->
                <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
                    <!-- Player 1 -->
                    <div class="bg-bg-darker rounded-lg shadow-xl p-6 border border-bg-dark">
                        <h3 class="text-xl font-bold text-primary mb-4" x-text="matchup?.player1?.name"></h3>
                        <pre class="text-sm text-text-primary whitespace-pre-wrap font-mono bg-bg-medium p-4 rounded-lg overflow-auto max-h-96" x-text="matchup?.player1?.army_list"></pre>
                    </div>

                    <!-- Player 2 -->
                    <div class="bg-bg-darker rounded-lg shadow-xl p-6 border border-bg-dark">
                        <h3 class="text-xl font-bold text-primary mb-4" x-text="matchup?.player2?.name"></h3>
                        <pre class="text-sm text-text-primary whitespace-pre-wrap font-mono bg-bg-medium p-4 rounded-lg overflow-auto max-h-96" x-text="matchup?.player2?.army_list"></pre>
                    </div>
                </div>

                <!-- Actions -->
                <div class="text-center">
                    <button 
                        @click="window.print()"
                        class="px-6 py-3 bg-bg-dark hover:bg-bg-medium text-text-primary font-bold rounded-lg border border-bg-dark transition"
                    >
                        Print Matchup Summary
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
        </div>
    `;
};

// Alpine.js component for matchup management
function matchupManager() {
    return {
        selectedSystem: 'age_of_sigmar', // AoS only - hardcoded
        matchupId: null,
        playerName: '',
        armyList: '',
        matchup: null,
        creating: false,
        submitting: false,
        hasSubmitted: false,
        loadingMatchup: false,
        error: null,
        pollInterval: null,

        init() {
            // Check if we're viewing an existing matchup from URL
            const path = window.location.pathname;
            const match = path.match(/\/squire\/matchup\/([^\/]+)/);
            if (match) {
                this.matchupId = match[1];
                this.loadMatchup();
                // Start polling for updates
                this.startPolling();
            }
        },

        async createMatchup() {
            // AoS only - system is hardcoded
            this.creating = true;
            this.error = null;

            try {
                const response = await fetch(getApiUrl('/api/squire/matchup/create'), {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        game_system: this.selectedSystem
                    })
                });

                if (!response.ok) {
                    throw new Error(`Failed to create matchup: ${response.statusText}`);
                }

                const data = await response.json();
                this.matchupId = data.matchup_id;
                
                // Update URL without reload
                window.history.pushState({}, '', `/squire/matchup/${this.matchupId}`);
                
            } catch (err) {
                this.error = err.message;
                console.error('Error creating matchup:', err);
            } finally {
                this.creating = false;
            }
        },

        async submitList() {
            if (!this.playerName || !this.armyList) {
                this.error = 'Please enter your name and army list';
                return;
            }

            this.submitting = true;
            this.error = null;

            try {
                const response = await fetch(getApiUrl(`/api/squire/matchup/${this.matchupId}/submit`), {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        player_name: this.playerName,
                        army_list: this.armyList
                    })
                });

                if (!response.ok) {
                    const errorData = await response.json();
                    throw new Error(errorData.detail || `Failed to submit list: ${response.statusText}`);
                }

                this.matchup = await response.json();
                this.hasSubmitted = true;
                
                // Start polling if not complete
                if (!this.matchup.is_complete) {
                    this.startPolling();
                }
                
            } catch (err) {
                this.error = err.message;
                console.error('Error submitting list:', err);
            } finally {
                this.submitting = false;
            }
        },

        async loadMatchup() {
            this.loadingMatchup = true;
            this.error = null;

            try {
                const response = await fetch(getApiUrl(`/api/squire/matchup/${this.matchupId}`));
                
                if (!response.ok) {
                    throw new Error(`Matchup not found: ${response.statusText}`);
                }

                this.matchup = await response.json();
                
                // If complete, stop polling
                if (this.matchup.is_complete) {
                    this.stopPolling();
                }
                
            } catch (err) {
                this.error = err.message;
                console.error('Error loading matchup:', err);
            } finally {
                this.loadingMatchup = false;
            }
        },

        startPolling() {
            if (this.pollInterval) return;
            
            this.pollInterval = setInterval(() => {
                this.loadMatchup();
            }, 5000); // Poll every 5 seconds
        },

        stopPolling() {
            if (this.pollInterval) {
                clearInterval(this.pollInterval);
                this.pollInterval = null;
            }
        },

        getShareUrl() {
            return `${window.location.origin}/squire/matchup/${this.matchupId}`;
        },

        copyShareLink() {
            const url = this.getShareUrl();
            navigator.clipboard.writeText(url).then(() => {
                alert('Link copied to clipboard!');
            }).catch(err => {
                console.error('Failed to copy:', err);
            });
        },

        canSubmit() {
            // Can submit if matchup not complete and not both slots filled
            return this.matchup && !this.matchup.is_complete && 
                   (!this.matchup.player1 || !this.matchup.player2);
        },

        hasOpponent() {
            // Has opponent if either player slot is filled
            return this.matchup && (this.matchup.player1 || this.matchup.player2);
        }
    };
}
