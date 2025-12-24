// Squire matchup history page
window.renderSquireHistory = function() {
    return `
<div class="max-w-6xl mx-auto px-4 py-12" x-data="squireHistory()">
    <div class="text-center mb-8">
        <h1 class="text-4xl font-montserrat mb-4 text-primary">Matchup History</h1>
        <p class="text-lg text-text-secondary">View your past games and battle records</p>
    </div>

    <!-- Loading State -->
    <div x-show="loading" class="text-center py-12">
        <div class="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-primary"></div>
        <p class="mt-4 text-text-secondary">Loading matchups...</p>
    </div>

    <!-- Error State -->
    <div x-show="error" class="bg-red-900/30 border border-red-700 rounded-lg p-6 mb-6">
        <p class="text-red-400" x-text="error"></p>
    </div>

    <!-- Filters -->
    <div x-show="!loading && !error" class="bg-bg-dark border border-accent-dark rounded-lg p-6 mb-6">
        <h2 class="text-xl font-montserrat mb-4 text-primary">Filters</h2>
        
        <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
                <label class="block text-sm font-medium text-text-secondary mb-2">Game System</label>
                <select x-model="selectedSystem" @change="loadHistory()" 
                        class="w-full px-4 py-2 bg-bg-darkest border border-accent-dark rounded-lg focus:outline-none focus:border-primary text-text-primary">
                    <option value="all">All Systems</option>
                    <option value="age_of_sigmar">Age of Sigmar</option>
                    <option value="warhammer_40k">Warhammer 40,000</option>
                    <option value="the_old_world">The Old World</option>
                </select>
            </div>
            
            <div>
                <label class="block text-sm font-medium text-text-secondary mb-2">Status</label>
                <select x-model="selectedStatus" @change="loadHistory()" 
                        class="w-full px-4 py-2 bg-bg-darkest border border-accent-dark rounded-lg focus:outline-none focus:border-primary text-text-primary">
                    <option value="all">All Matchups</option>
                    <option value="completed">Completed</option>
                    <option value="in_progress">In Progress</option>
                </select>
            </div>
            
            <div>
                <label class="block text-sm font-medium text-text-secondary mb-2">Results</label>
                <div class="text-text-primary pt-2">
                    <span class="font-semibold text-2xl" x-text="matchups.length"></span>
                    <span class="text-text-secondary ml-2">matchup(s) found</span>
                </div>
            </div>
        </div>
    </div>

    <!-- Matchup List -->
    <div x-show="!loading && !error" class="space-y-4">
        <!-- Empty State -->
        <div x-show="matchups.length === 0" class="bg-bg-dark border border-accent-dark rounded-lg p-12 text-center">
            <div class="text-6xl mb-4">🎲</div>
            <h3 class="text-2xl font-montserrat text-text-secondary mb-2">No matchups yet</h3>
            <p class="text-text-muted mb-6">Create your first matchup to get started!</p>
            <a href="/squire/matchup" @click.prevent="$root.navigate('/squire/matchup')" 
               class="inline-block bg-primary hover:bg-primary-dark text-bg-darkest font-semibold py-3 px-6 rounded-lg transition">
                Create Matchup
            </a>
        </div>

        <!-- Matchup Cards -->
        <template x-for="matchup in matchups" :key="matchup.matchup_id">
            <div class="bg-bg-dark border border-accent-dark rounded-lg p-6 hover:border-primary transition cursor-pointer"
                 @click="viewMatchup(matchup.matchup_id)">
                <div class="flex items-start justify-between mb-4">
                    <div>
                        <h3 class="text-xl font-montserrat text-primary mb-2" x-text="formatSystem(matchup.game_system)"></h3>
                        <p class="text-sm text-text-secondary" x-text="formatDate(matchup.created_at)"></p>
                    </div>
                    <div>
                        <span class="px-3 py-1 rounded-full text-xs font-semibold"
                              :class="matchup.is_complete ? 'bg-green-900/30 text-green-400 border border-green-700' : 'bg-yellow-900/30 text-yellow-400 border border-yellow-700'"
                              x-text="matchup.is_complete ? 'Completed' : 'In Progress'">
                        </span>
                    </div>
                </div>

                <div class="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
                    <!-- Your Info -->
                    <div class="bg-bg-medium rounded-lg p-4">
                        <div class="text-sm text-text-secondary mb-1">You</div>
                        <div class="text-text-primary font-semibold" x-text="getPlayerName(matchup, true)"></div>
                    </div>

                    <!-- Opponent Info -->
                    <div class="bg-bg-medium rounded-lg p-4">
                        <div class="text-sm text-text-secondary mb-1">Opponent</div>
                        <div class="text-text-primary font-semibold" x-text="getPlayerName(matchup, false) || 'Waiting...'"></div>
                    </div>
                </div>

                <div x-show="matchup.battle_plan" class="text-sm text-text-secondary">
                    <span class="text-accent-light">📋 Battle Plan:</span>
                    <span x-text="matchup.battle_plan?.name"></span>
                </div>
            </div>
        </template>

        <!-- Pagination -->
        <div x-show="totalPages > 1" class="flex justify-center gap-2 mt-6">
            <button @click="changePage(currentPage - 1)" 
                    :disabled="currentPage === 1"
                    :class="currentPage === 1 ? 'opacity-50 cursor-not-allowed' : 'hover:bg-bg-medium'"
                    class="px-4 py-2 bg-bg-dark border border-accent-dark rounded-lg text-text-primary transition">
                Previous
            </button>
            
            <div class="flex items-center gap-2 px-4 py-2 bg-bg-dark border border-accent-dark rounded-lg text-text-primary">
                <span x-text="currentPage"></span>
                <span class="text-text-secondary">/</span>
                <span x-text="totalPages"></span>
            </div>
            
            <button @click="changePage(currentPage + 1)" 
                    :disabled="currentPage === totalPages"
                    :class="currentPage === totalPages ? 'opacity-50 cursor-not-allowed' : 'hover:bg-bg-medium'"
                    class="px-4 py-2 bg-bg-dark border border-accent-dark rounded-lg text-text-primary transition">
                Next
            </button>
        </div>
    </div>
</div>
    `;
};

function squireHistory() {
    return {
        loading: true,
        error: null,
        matchups: [],
        selectedSystem: 'all',
        selectedStatus: 'all',
        currentPage: 1,
        totalPages: 1,
        perPage: 10,
        username: '',

        async init() {
            // Get current username
            const token = localStorage.getItem('auth_token');
            if (token) {
                try {
                    const response = await fetch('/api/squire/auth/me', {
                        headers: { 'Authorization': `Bearer ${token}` }
                    });
                    if (response.ok) {
                        const data = await response.json();
                        this.username = data.username;
                    }
                } catch (error) {
                    console.error('Failed to get username:', error);
                }
            }

            await this.loadHistory();
        },

        async loadHistory() {
            this.loading = true;
            this.error = null;

            const token = localStorage.getItem('auth_token');
            if (!token) {
                this.error = 'Please log in to view your history';
                this.loading = false;
                setTimeout(() => {
                    window.location.href = '/squire/login';
                }, 2000);
                return;
            }

            try {
                const params = new URLSearchParams({
                    page: this.currentPage,
                    limit: this.perPage,
                    system: this.selectedSystem,
                    status: this.selectedStatus
                });

                const response = await fetch(`/api/squire/user/matchups?${params}`, {
                    headers: {
                        'Authorization': `Bearer ${token}`
                    }
                });

                if (!response.ok) {
                    if (response.status === 401) {
                        this.error = 'Session expired. Please log in again.';
                        localStorage.removeItem('auth_token');
                        setTimeout(() => {
                            window.location.href = '/squire/login';
                        }, 2000);
                    } else {
                        this.error = 'Failed to load matchup history';
                    }
                    return;
                }

                const data = await response.json();
                this.matchups = data.matchups || [];
                this.totalPages = data.pages || 1;
            } catch (error) {
                console.error('History load error:', error);
                this.error = 'Network error. Please try again.';
            } finally {
                this.loading = false;
            }
        },

        changePage(page) {
            if (page >= 1 && page <= this.totalPages) {
                this.currentPage = page;
                this.loadHistory();
            }
        },

        viewMatchup(matchupId) {
            window.location.href = `/squire/matchup?id=${matchupId}`;
        },

        getPlayerName(matchup, isMe) {
            // If user is player1
            if (matchup.player1?.name === this.username || matchup.creator_username === this.username) {
                return isMe ? matchup.player1?.name : matchup.player2?.name;
            }
            // User is player2
            return isMe ? matchup.player2?.name : matchup.player1?.name;
        },

        formatSystem(system) {
            const names = {
                'age_of_sigmar': 'Age of Sigmar',
                'warhammer_40k': 'Warhammer 40,000',
                'the_old_world': 'The Old World'
            };
            return names[system] || system;
        },

        formatDate(dateString) {
            if (!dateString) return 'N/A';
            const date = new Date(dateString);
            return date.toLocaleDateString('en-US', { 
                year: 'numeric', 
                month: 'short', 
                day: 'numeric',
                hour: '2-digit',
                minute: '2-digit'
            });
        }
    };
}
