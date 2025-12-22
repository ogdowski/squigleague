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

            // Match /squire/matchup/{id} or /matchup/{id}
            if (path.includes('/matchup/')) {
                this.currentRoute = '/matchup';
            } else if (path === '/missions' || path === '/squire/missions' || path === '/battle-plans' || path === '/squire/battle-plans') {
                // Support both old and new paths
                this.currentRoute = '/missions';
            } else {
                // Home page is matchup
                this.currentRoute = '/';
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

            // Route to appropriate interface
            if (this.currentRoute === '/missions') {
                content.innerHTML = window.renderBattlePlanGallery();
            } else {
                // Single interface - matchup system with battle plan
                content.innerHTML = window.renderSquireMatchup();
            }
            
            // Re-initialize Alpine.js for the new content
            if (window.Alpine) {
                window.Alpine.initTree(content);
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
                const res = await fetch(getApiUrl('/api/herald/stats'));
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
