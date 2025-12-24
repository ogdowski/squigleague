// Squire user profile page
window.renderSquireProfile = function() {
    return `
<div class="max-w-4xl mx-auto px-4 py-12" x-data="squireProfile()">
    <div class="text-center mb-8">
        <h1 class="text-4xl font-montserrat mb-4 text-primary">User Profile</h1>
        <p class="text-lg text-text-secondary">Manage your account and view your stats</p>
    </div>

    <!-- Loading State -->
    <div x-show="loading" class="text-center py-12">
        <div class="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-primary"></div>
        <p class="mt-4 text-text-secondary">Loading profile...</p>
    </div>

    <!-- Error State -->
    <div x-show="error" class="bg-red-900/30 border border-red-700 rounded-lg p-6 mb-6">
        <p class="text-red-400" x-text="error"></p>
    </div>

    <!-- Profile Content -->
    <div x-show="!loading && !error" class="space-y-6">
        <!-- Profile Info Card -->
        <div class="bg-bg-dark border border-accent-dark rounded-lg p-6">
            <h2 class="text-2xl font-montserrat mb-6 text-primary">Account Information</h2>
            
            <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                    <label class="block text-sm font-medium text-text-secondary mb-2">Username</label>
                    <p class="text-lg text-text-primary font-semibold" x-text="profile?.username"></p>
                </div>
                
                <div>
                    <label class="block text-sm font-medium text-text-secondary mb-2">Email</label>
                    <p class="text-lg text-text-primary" x-text="profile?.email"></p>
                </div>
                
                <div>
                    <label class="block text-sm font-medium text-text-secondary mb-2">Member Since</label>
                    <p class="text-lg text-text-primary" x-text="formatDate(profile?.created_at)"></p>
                </div>
                
                <div>
                    <label class="block text-sm font-medium text-text-secondary mb-2">Email Status</label>
                    <p class="text-lg" :class="profile?.email_verified ? 'text-green-400' : 'text-yellow-400'">
                        <span x-show="profile?.email_verified">✓ Verified</span>
                        <span x-show="!profile?.email_verified">⚠️ Not Verified</span>
                    </p>
                </div>
            </div>
        </div>

        <!-- Stats Card -->
        <div class="bg-bg-dark border border-accent-dark rounded-lg p-6">
            <h2 class="text-2xl font-montserrat mb-6 text-primary">Statistics</h2>
            
            <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
                <div class="text-center p-4 bg-bg-medium rounded-lg">
                    <div class="text-3xl font-bold text-primary mb-2" x-text="profile?.stats?.total_matchups || 0"></div>
                    <div class="text-sm text-text-secondary">Total Matchups</div>
                </div>
                
                <div class="text-center p-4 bg-bg-medium rounded-lg">
                    <div class="text-3xl font-bold text-accent-light mb-2" x-text="profile?.stats?.favorite_system || 'N/A'"></div>
                    <div class="text-sm text-text-secondary">Favorite System</div>
                </div>
                
                <div class="text-center p-4 bg-bg-medium rounded-lg">
                    <div class="text-3xl font-bold text-accent-mid mb-2" x-text="profile?.stats?.matchups_this_month || 0"></div>
                    <div class="text-sm text-text-secondary">Games This Month</div>
                </div>
            </div>
        </div>

        <!-- Actions -->
        <div class="flex gap-4">
            <a href="/squire/history" @click.prevent="$root.navigate('/squire/history')" 
               class="flex-1 bg-primary hover:bg-primary-dark text-bg-darkest font-semibold py-3 px-6 rounded-lg text-center transition">
                📜 View Matchup History
            </a>
            <a href="/squire/settings" @click.prevent="$root.navigate('/squire/settings')" 
               class="flex-1 bg-accent-dark hover:bg-accent-mid text-text-primary font-semibold py-3 px-6 rounded-lg text-center transition">
                ⚙️ Account Settings
            </a>
        </div>
    </div>
</div>
    `;
};

function squireProfile() {
    return {
        loading: true,
        error: null,
        profile: null,

        async init() {
            await this.loadProfile();
        },

        async loadProfile() {
            this.loading = true;
            this.error = null;

            const token = localStorage.getItem('auth_token');
            if (!token) {
                this.error = 'Please log in to view your profile';
                this.loading = false;
                setTimeout(() => {
                    window.location.href = '/squire/login';
                }, 2000);
                return;
            }

            try {
                const response = await fetch('/api/squire/user/profile', {
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
                        this.error = 'Failed to load profile';
                    }
                    return;
                }

                this.profile = await response.json();
            } catch (error) {
                console.error('Profile load error:', error);
                this.error = 'Network error. Please try again.';
            } finally {
                this.loading = false;
            }
        },

        formatDate(dateString) {
            if (!dateString) return 'N/A';
            const date = new Date(dateString);
            return date.toLocaleDateString('en-US', { 
                year: 'numeric', 
                month: 'long', 
                day: 'numeric' 
            });
        }
    };
}
