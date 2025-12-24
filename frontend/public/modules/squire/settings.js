// Squire settings page
window.renderSquireSettings = function() {
    return `
<div class="max-w-2xl mx-auto px-4 py-12" x-data="squireSettings()">
    <div class="text-center mb-8">
        <h1 class="text-4xl font-montserrat mb-4 text-primary">Account Settings</h1>
        <p class="text-lg text-text-secondary">Manage your account preferences</p>
    </div>

    <!-- Success Message -->
    <div x-show="success" class="bg-green-900/30 border border-green-700 rounded-lg p-4 mb-6">
        <p class="text-green-400" x-text="success"></p>
    </div>

    <!-- Error Message -->
    <div x-show="error" class="bg-red-900/30 border border-red-700 rounded-lg p-4 mb-6">
        <p class="text-red-400" x-text="error"></p>
    </div>

    <div class="space-y-6">
        <!-- Account Info -->
        <div class="bg-bg-dark border border-accent-dark rounded-lg p-6">
            <h2 class="text-2xl font-montserrat mb-4 text-primary">Account Information</h2>
            <div class="space-y-4">
                <div>
                    <label class="block text-sm font-medium text-text-secondary mb-2">Username</label>
                    <input type="text" 
                           x-model="username" 
                           disabled
                           class="w-full px-4 py-2 bg-bg-medium border border-accent-dark rounded-lg text-text-muted cursor-not-allowed">
                    <p class="text-xs text-text-muted mt-1">Username cannot be changed</p>
                </div>
                
                <div>
                    <label class="block text-sm font-medium text-text-secondary mb-2">Email</label>
                    <input type="email" 
                           x-model="email" 
                           disabled
                           class="w-full px-4 py-2 bg-bg-medium border border-accent-dark rounded-lg text-text-muted cursor-not-allowed">
                    <p class="text-xs text-text-muted mt-1">Contact support to change your email</p>
                </div>
            </div>
        </div>

        <!-- Change Password -->
        <div class="bg-bg-dark border border-accent-dark rounded-lg p-6">
            <h2 class="text-2xl font-montserrat mb-4 text-primary">Change Password</h2>
            <form @submit.prevent="changePassword" class="space-y-4">
                <div>
                    <label class="block text-sm font-medium text-text-secondary mb-2">Current Password</label>
                    <input type="password" 
                           x-model="currentPassword" 
                           required
                           class="w-full px-4 py-2 bg-bg-darkest border border-accent-dark rounded-lg focus:outline-none focus:border-primary text-text-primary">
                </div>
                
                <div>
                    <label class="block text-sm font-medium text-text-secondary mb-2">New Password</label>
                    <input type="password" 
                           x-model="newPassword" 
                           required
                           minlength="8"
                           class="w-full px-4 py-2 bg-bg-darkest border border-accent-dark rounded-lg focus:outline-none focus:border-primary text-text-primary">
                    <p class="text-xs text-text-muted mt-1">Minimum 8 characters</p>
                </div>
                
                <div>
                    <label class="block text-sm font-medium text-text-secondary mb-2">Confirm New Password</label>
                    <input type="password" 
                           x-model="confirmPassword" 
                           required
                           minlength="8"
                           class="w-full px-4 py-2 bg-bg-darkest border border-accent-dark rounded-lg focus:outline-none focus:border-primary text-text-primary">
                </div>
                
                <button type="submit" 
                        :disabled="changing || !canChangePassword"
                        class="w-full bg-primary hover:bg-primary-dark disabled:bg-gray-600 disabled:cursor-not-allowed text-bg-darkest font-semibold py-3 px-6 rounded-lg transition">
                    <span x-show="!changing">Change Password</span>
                    <span x-show="changing">Changing...</span>
                </button>
            </form>
        </div>

        <!-- Danger Zone -->
        <div class="bg-red-900/20 border border-red-700 rounded-lg p-6">
            <h2 class="text-2xl font-montserrat mb-4 text-red-400">Danger Zone</h2>
            <p class="text-text-secondary mb-4">Once you delete your account, there is no going back. This action is permanent.</p>
            <button @click="confirmDelete" 
                    class="bg-red-700 hover:bg-red-600 text-white font-semibold py-2 px-6 rounded-lg transition">
                Delete Account
            </button>
        </div>
    </div>
</div>
    `;
};

function squireSettings() {
    return {
        username: '',
        email: '',
        currentPassword: '',
        newPassword: '',
        confirmPassword: '',
        changing: false,
        error: null,
        success: null,

        async init() {
            await this.loadUserInfo();
        },

        async loadUserInfo() {
            const token = localStorage.getItem('auth_token');
            if (!token) {
                window.location.href = '/squire/login';
                return;
            }

            try {
                const response = await fetch('/api/squire/auth/me', {
                    headers: { 'Authorization': `Bearer ${token}` }
                });

                if (response.ok) {
                    const data = await response.json();
                    this.username = data.username;
                    this.email = data.email;
                } else {
                    window.location.href = '/squire/login';
                }
            } catch (error) {
                console.error('Failed to load user info:', error);
                window.location.href = '/squire/login';
            }
        },

        get canChangePassword() {
            return this.currentPassword && 
                   this.newPassword && 
                   this.confirmPassword && 
                   this.newPassword === this.confirmPassword &&
                   this.newPassword.length >= 8;
        },

        async changePassword() {
            if (!this.canChangePassword) return;

            this.changing = true;
            this.error = null;
            this.success = null;

            // TODO: Implement password change endpoint
            // For now, show not implemented message
            await new Promise(resolve => setTimeout(resolve, 1000));
            
            this.error = 'Password change feature coming soon!';
            this.changing = false;
        },

        confirmDelete() {
            if (confirm('Are you absolutely sure? This action cannot be undone.\n\nType "DELETE" to confirm.')) {
                const confirmation = prompt('Type DELETE to confirm:');
                if (confirmation === 'DELETE') {
                    this.deleteAccount();
                }
            }
        },

        async deleteAccount() {
            // TODO: Implement account deletion endpoint
            alert('Account deletion feature coming soon!');
        }
    };
}
