// Squire resend verification page
window.renderSquireResendVerification = function() {
    return `
<div class="max-w-md mx-auto mt-10 px-4 pb-8" x-data="squireResendVerification()">
    
    <div class="text-center mb-8">
        <h1 class="text-4xl font-montserrat mb-4 text-primary">Resend Verification</h1>
        <p class="text-lg text-text-secondary">Didn't receive the email?</p>
    </div>

    <div class="bg-bg-dark border border-accent-dark rounded-lg p-6">
        
        <div x-show="sent" class="mb-6 p-4 bg-green-900/30 border border-green-700 rounded-lg">
            <p class="text-green-400 text-sm">
                Verification email sent! Please check your email.
            </p>
            <p class="text-green-400 text-xs mt-2">
                Dev: Check MailHog at <a href="http://localhost:8025" target="_blank" class="underline">localhost:8025</a>
            </p>
        </div>

        <div x-show="error" class="mb-6 p-4 bg-red-900/30 border border-red-700 rounded-lg">
            <p class="text-red-400 text-sm" x-text="error"></p>
        </div>

        <form @submit.prevent="submitResend" x-show="!sent">
            
            <div class="mb-6">
                <label class="block text-sm font-medium mb-2 text-text-primary">Email Address</label>
                <input 
                    type="email" 
                    x-model="email"
                    required
                    class="w-full px-4 py-2 bg-bg-darkest border border-accent-dark rounded-lg focus:outline-none focus:border-primary text-text-primary"
                    placeholder="Enter your email address"
                >
                <p class="text-xs text-text-secondary mt-1">
                    We'll send a new verification link to this email
                </p>
            </div>

            <button 
                type="submit"
                :disabled="loading || !isValid"
                class="w-full bg-primary hover:bg-primary-dark disabled:bg-gray-600 disabled:cursor-not-allowed text-bg-darkest font-semibold py-3 px-6 rounded-lg transition"
            >
                <span x-show="!loading">Send Verification Email</span>
                <span x-show="loading">Sending...</span>
            </button>

        </form>

        <div class="mt-6 text-center text-sm space-y-2">
            <div>
                <a href="/squire/login" class="text-primary hover:text-primary-dark">Back to Login</a>
            </div>
            <div>
                <span class="text-text-secondary">Don't have an account?</span>
                <a href="/squire/register" class="text-primary hover:text-primary-dark ml-1">Register here</a>
            </div>
        </div>

    </div>

</div>
    `;
};

function squireResendVerification() {
    return {
        email: '',
        loading: false,
        sent: false,
        error: null,
        
        get isValid() {
            return this.email.includes('@');
        },
        
        async submitResend() {
            if (!this.isValid) return;
            
            this.loading = true;
            this.error = null;
            
            try {
                const response = await fetch('/api/squire/auth/resend-verification', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ email: this.email }),
                });
                
                this.sent = true;
                
            } catch (error) {
                this.error = 'Network error. Please try again.';
            } finally {
                this.loading = false;
            }
        }
    };
}
