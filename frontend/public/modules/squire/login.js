// Squire login page
window.renderSquireLogin = function() {
    return `
<div class="max-w-md mx-auto mt-10 px-4 pb-8" x-data="squireLogin()">
    
    <div class="text-center mb-8">
        <h1 class="text-4xl font-montserrat mb-4 text-primary">Login</h1>
        <p class="text-lg text-text-secondary">Welcome back to SquigLeague</p>
    </div>

    <div class="bg-bg-dark border border-accent-dark rounded-lg p-6">
        
        <div x-show="error" class="mb-6 p-4 bg-red-900/30 border border-red-700 rounded-lg">
            <p class="text-red-400 text-sm" x-text="error"></p>
            <p x-show="emailNotVerified" class="text-red-400 text-sm mt-2">
                <a href="/squire/resend-verification" class="underline">Resend verification email</a>
            </p>
        </div>

        <form @submit.prevent="submitLogin">
            
            <div class="mb-4">
                <label class="block text-sm font-medium mb-2 text-text-primary">Username or Email</label>
                <input 
                    type="text" 
                    x-model="usernameOrEmail"
                    required
                    class="w-full px-4 py-2 bg-bg-darkest border border-accent-dark rounded-lg focus:outline-none focus:border-primary text-text-primary"
                    placeholder="Enter your username or email"
                >
            </div>

            <div class="mb-6">
                <label class="block text-sm font-medium mb-2 text-text-primary">Password</label>
                <input 
                    type="password" 
                    x-model="password"
                    required
                    class="w-full px-4 py-2 bg-bg-darkest border border-accent-dark rounded-lg focus:outline-none focus:border-primary text-text-primary"
                    placeholder="Enter your password"
                >
            </div>

            <button 
                type="submit"
                :disabled="loading || !isValid"
                class="w-full bg-primary hover:bg-primary-dark disabled:bg-gray-600 disabled:cursor-not-allowed text-bg-darkest font-semibold py-3 px-6 rounded-lg transition"
            >
                <span x-show="!loading">Login</span>
                <span x-show="loading">Logging in...</span>
            </button>

        </form>

        <div class="mt-6 text-center text-sm space-y-2">
            <div>
                <span class="text-text-secondary">Don't have an account?</span>
                <a href="/squire/register" class="text-primary hover:text-primary-dark ml-1">Register here</a>
            </div>
            <div>
                <a href="/squire/resend-verification" class="text-primary hover:text-primary-dark">Resend verification email</a>
            </div>
        </div>

    </div>

</div>
    `;
};

function squireLogin() {
    return {
        usernameOrEmail: '',
        password: '',
        loading: false,
        error: null,
        emailNotVerified: false,
        
        get isValid() {
            return this.usernameOrEmail.length > 0 && this.password.length > 0;
        },
        
        async submitLogin() {
            if (!this.isValid) return;
            
            this.loading = true;
            this.error = null;
            this.emailNotVerified = false;
            
            try {
                const response = await fetch('/api/squire/auth/login', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        username_or_email: this.usernameOrEmail,
                        password: this.password,
                    }),
                });
                
                if (!response.ok) {
                    // Handle error responses with appropriate messages
                    if (response.status === 403) {
                        this.emailNotVerified = true;
                        this.error = "Email not verified. Please check your email for the verification link.";
                    } else if (response.status === 401) {
                        this.error = "Invalid username or password.";
                    } else if (response.status === 422) {
                        this.error = "Invalid request format.";
                    } else {
                        this.error = 'Login failed. Please try again.';
                    }
                    return;
                }
                
                // Success - parse response and store token
                const data = await response.json();
                localStorage.setItem('auth_token', data.token);
                window.location.href = '/';
                
            } catch (error) {
                console.error('Login error:', error);
                this.error = 'Network error. Please try again.';
            } finally {
                this.loading = false;
            }
        }
    };
}
