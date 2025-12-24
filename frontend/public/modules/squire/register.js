// Squire registration page
window.renderSquireRegister = function() {
    return `
<div class="max-w-md mx-auto mt-10 px-4 pb-8" x-data="squireRegister()">
    
    <!-- Header -->
    <div class="text-center mb-8">
        <h1 class="text-4xl font-montserrat mb-4 text-primary">Register</h1>
        <p class="text-lg text-text-secondary">Create your SquigLeague account</p>
    </div>

    <!-- Registration Form -->
    <div class="bg-bg-dark border border-accent-dark rounded-lg p-6">
        
        <!-- Success Message -->
        <div x-show="registered" class="mb-6 p-4 bg-green-900/30 border border-green-700 rounded-lg">
            <p class="text-green-400 text-sm mb-2">
                Registration successful! Please check your email to verify your account.
            </p>
            <p class="text-green-400 text-xs">
                Dev: Check MailHog at <a href="http://localhost:8025" target="_blank" class="underline">localhost:8025</a>
            </p>
            <button @click="window.location.href='/squire/login'" 
                    class="mt-4 w-full bg-primary hover:bg-primary-dark text-bg-darkest font-semibold py-2 px-4 rounded-lg">
                Go to Login
            </button>
        </div>

        <!-- Error Message -->
        <div x-show="errors.submit" class="mb-6 p-4 bg-red-900/30 border border-red-700 rounded-lg">
            <p class="text-red-400 text-sm" x-text="errors.submit"></p>
        </div>

        <form @submit.prevent="submitRegistration" x-show="!registered">
            
            <!-- Username -->
            <div class="mb-4">
                <label class="block text-sm font-medium mb-2 text-text-primary">Username</label>
                <input 
                    type="text" 
                    x-model="username"
                    @blur="validateUsername"
                    required
                    minlength="3"
                    maxlength="20"
                    class="w-full px-4 py-2 bg-bg-darkest border border-accent-dark rounded-lg focus:outline-none focus:border-primary text-text-primary"
                    placeholder="Choose a username"
                >
                <p x-show="errors.username" class="text-red-400 text-xs mt-1" x-text="errors.username"></p>
            </div>

            <!-- Email -->
            <div class="mb-4">
                <label class="block text-sm font-medium mb-2 text-text-primary">Email</label>
                <input 
                    type="email" 
                    x-model="email"
                    @blur="validateEmail"
                    required
                    class="w-full px-4 py-2 bg-bg-darkest border border-accent-dark rounded-lg focus:outline-none focus:border-primary text-text-primary"
                    placeholder="your@email.com"
                >
                <p x-show="errors.email" class="text-red-400 text-xs mt-1" x-text="errors.email"></p>
            </div>

            <!-- Password -->
            <div class="mb-4">
                <label class="block text-sm font-medium mb-2 text-text-primary">Password</label>
                <input 
                    type="password" 
                    x-model="password"
                    @blur="validatePassword"
                    required
                    minlength="8"
                    class="w-full px-4 py-2 bg-bg-darkest border border-accent-dark rounded-lg focus:outline-none focus:border-primary text-text-primary"
                    placeholder="Minimum 8 characters"
                >
                <p x-show="errors.password" class="text-red-400 text-xs mt-1" x-text="errors.password"></p>
                <p class="text-text-secondary text-xs mt-1">Must be at least 8 characters</p>
            </div>

            <!-- Submit Button -->
            <button 
                type="submit"
                :disabled="loading || !isValid"
                class="w-full bg-primary hover:bg-primary-dark disabled:bg-gray-600 disabled:cursor-not-allowed text-bg-darkest font-semibold py-3 px-6 rounded-lg transition"
            >
                <span x-show="!loading">Create Account</span>
                <span x-show="loading">Creating Account...</span>
            </button>

        </form>

        <!-- Links -->
        <div class="mt-6 text-center text-sm" x-show="!registered">
            <span class="text-text-secondary">Already have an account?</span>
            <a href="/squire/login" class="text-primary hover:text-primary-dark ml-1">Login here</a>
        </div>

    </div>

</div>
    `;
};

// Registration Alpine.js component
function squireRegister() {
    return {
        username: '',
        email: '',
        password: '',
        loading: false,
        errors: {},
        registered: false,
        
        get isValid() {
            return this.username.length >= 3 &&
                   this.email.includes('@') &&
                   this.password.length >= 8 &&
                   Object.keys(this.errors).length === 0;
        },
        
        validateUsername() {
            if (this.username.length > 0 && this.username.length < 3) {
                this.errors.username = 'Username must be at least 3 characters';
            } else if (this.username.length > 20) {
                this.errors.username = 'Username must be 20 characters or less';
            } else {
                delete this.errors.username;
            }
        },
        
        validateEmail() {
            const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
            if (this.email.length > 0 && !emailRegex.test(this.email)) {
                this.errors.email = 'Please enter a valid email address';
            } else {
                delete this.errors.email;
            }
        },
        
        validatePassword() {
            if (this.password.length > 0 && this.password.length < 8) {
                this.errors.password = 'Password must be at least 8 characters';
            } else {
                delete this.errors.password;
            }
        },

        async submitRegistration() {
            if (!this.isValid) return;
            
            this.loading = true;
            this.errors = {};
            
            try {
                const response = await fetch('/api/squire/auth/register', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        username: this.username,
                        email: this.email,
                        password: this.password,
                    }),
                });
                
                const data = await response.json();
                
                if (!response.ok) {
                    this.errors.submit = data.detail || 'Registration failed';
                    return;
                }
                
                this.registered = true;
                
            } catch (error) {
                this.errors.submit = 'Network error. Please try again.';
            } finally {
                this.loading = false;
            }
        }
    };
}
