// Main app controller
function app() {
    return {
        version: '0.1.0',
        currentRoute: '/',
        exchangeId: null,
        isCreator: false,

        init() {
            // Parse initial route
            this.parseRoute();

            // Handle browser back/forward
            window.addEventListener('popstate', () => {
                this.parseRoute();
                this.loadPage();
            });

            // Load initial page
            this.loadPage();
        },

        parseRoute() {
            const path = window.location.pathname;
            const params = new URLSearchParams(window.location.search);

            if (path === '/') {
                this.currentRoute = '/';
            } else if (path.startsWith('/exchange/')) {
                const parts = path.split('/');
                this.exchangeId = parts[2];
                this.isCreator = params.get('creator') === 'true';
                this.currentRoute = '/exchange';
            }
        },

        navigate(path, params = {}) {
            const url = new URL(path, window.location.origin);
            Object.entries(params).forEach(([key, value]) => {
                url.searchParams.set(key, value);
            });

            window.history.pushState({}, '', url);
            this.parseRoute();
            this.loadPage();
        },

        async loadPage() {
            const content = document.getElementById('app-content');

            if (this.currentRoute === '/') {
                content.innerHTML = window.heraldHomePage();
            } else if (this.currentRoute === '/exchange') {
                // Fetch exchange status to determine which page to show
                try {
                    const response = await fetch(`/api/herald/exchange/${this.exchangeId}`);

                    if (!response.ok) {
                        content.innerHTML = this.errorPage('Exchange not found');
                        return;
                    }

                    const data = await response.json();

                    if (data.status === 'complete') {
                        content.innerHTML = window.heraldRevealPage(this.exchangeId);
                    } else if (this.isCreator) {
                        content.innerHTML = window.heraldWaitingPage(this.exchangeId);
                    } else {
                        content.innerHTML = window.heraldRespondPage(this.exchangeId);
                    }
                } catch (err) {
                    console.error('Error loading exchange:', err);
                    content.innerHTML = this.errorPage('Error loading exchange');
                }
            }
        },

        errorPage(message) {
            return `
                <div class="max-w-4xl mx-auto mt-10 px-4 text-center">
                    <h1 class="text-3xl font-bold mb-4 text-accent-mid">Error</h1>
                    <p class="text-text-secondary">${message}</p>
                    <a href="/" class="inline-block mt-6 bg-primary hover:bg-primary-dark text-bg-darkest font-semibold py-3 px-6 rounded-lg transition">
                        Go Home
                    </a>
                </div>
            `;
        }
    };
}

// Footer stats
function footerStats() {
    return {
        completedExchanges: 0,
        version: '0.0.0',

        init() {
            this.loadStats();
        },

        async loadStats() {
            try {
                const res = await fetch('/api/herald/stats');
                if (res.ok) {
                    const data = await res.json();
                    this.completedExchanges = data.completed_exchanges || 0;
                    this.version = data.version || '0.0.0';
                }
            } catch (err) {
                console.error('Failed to load stats:', err);
            }
        }
    }
}
