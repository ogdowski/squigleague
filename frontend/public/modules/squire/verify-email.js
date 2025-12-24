// Squire email verification page
window.renderSquireVerifyEmail = function() {
    return `
<div class="max-w-md mx-auto mt-10 px-4 pb-8" x-data="squireVerifyEmail()" x-init="init">
    
    <div class="text-center mb-8">
        <h1 class="text-4xl font-montserrat mb-4 text-primary">Email Verification</h1>
        <p class="text-lg text-text-secondary">Verifying your account...</p>
    </div>

    <div class="bg-bg-dark border border-accent-dark rounded-lg p-6">
        
        <div x-show="verifying" class="text-center py-8">
            <div class="inline-block h-12 w-12 animate-spin rounded-full border-4 border-solid border-primary border-r-transparent mb-4"></div>
            <p class="text-text-primary">Verifying your email...</p>
        </div>

        <div x-show="verified && !verifying" class="text-center py-8">
            <div class="mb-6">
                <svg class="w-16 h-16 text-green-500 mx-auto" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                </svg>
            </div>
            <h2 class="text-2xl font-semibold mb-4 text-green-400">Email Verified!</h2>
            <p class="text-text-primary mb-6">Your account has been successfully verified.</p>
            <p class="text-sm text-text-secondary mb-6">
                Redirecting to login in <span x-text="countdown"></span> seconds...
            </p>
            <a href="/squire/login" class="inline-block bg-primary hover:bg-primary-dark text-bg-darkest font-semibold py-2 px-6 rounded-lg transition">
                Login Now
            </a>
        </div>

        <div x-show="error && !verifying" class="text-center py-8">
            <div class="mb-6">
                <svg class="w-16 h-16 text-red-500 mx-auto" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                </svg>
            </div>
            <h2 class="text-2xl font-semibold mb-4 text-red-400">Verification Failed</h2>
            <p class="text-text-primary mb-6" x-text="error"></p>
            <div class="space-y-3">
                <a href="/squire/resend-verification" class="block bg-primary hover:bg-primary-dark text-bg-darkest font-semibold py-2 px-6 rounded-lg transition">
                    Request New Verification Email
                </a>
                <a href="/squire/register" class="block text-primary hover:text-primary-dark">Register Again</a>
            </div>
        </div>

    </div>

</div>
    `;
};

function squireVerifyEmail() {
    return {
        verifying: true,
        verified: false,
        error: null,
        countdown: 3,
        
        async init() {
            const params = new URLSearchParams(window.location.search);
            const token = params.get('token');
            
            if (!token) {
                this.verifying = false;
                this.error = 'No verification token provided';
                return;
            }
            
            await this.verifyToken(token);
        },
        
        async verifyToken(token) {
            try {
                const response = await fetch(`/api/squire/auth/verify-email?token=${token}`);
                const data = await response.json();
                
                if (!response.ok) {
                    this.verifying = false;
                    this.error = data.detail || 'Verification failed';
                    return;
                }
                
                this.verifying = false;
                this.verified = true;
                this.startCountdown();
                
            } catch (error) {
                this.verifying = false;
                this.error = 'Network error. Please try again.';
            }
        },
        
        startCountdown() {
            const interval = setInterval(() => {
                this.countdown--;
                if (this.countdown <= 0) {
                    clearInterval(interval);
                    window.location.href = '/squire/login';
                }
            }, 1000);
        }
    };
}
