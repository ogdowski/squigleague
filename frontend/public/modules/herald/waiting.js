// Herald waiting page
window.heraldWaitingPage = function(exchangeId) {
    // Fetch exchange data
    fetch(`/api/herald/exchange/${exchangeId}`)
        .then(res => res.json())
        .then(data => {
            const content = document.getElementById('app-content');
            content.innerHTML = renderWaitingPage(exchangeId, data);
        });

    return '<div class="max-w-3xl mx-auto mt-10 px-4 text-center"><p>Loading...</p></div>';
};

function renderWaitingPage(exchangeId, data) {
    return `
<div class="max-w-3xl mx-auto mt-10 px-4" x-data="waitingPageLogic('${exchangeId}', '${data.hash_a}')">
    <div class="bg-bg-dark rounded-lg shadow-lg p-8 border border-bg-medium">
        <h1 class="text-3xl font-montserrat text-center mb-6 text-accent-light">Waiting for Opponent</h1>

        <!-- Prominent Share Link Box -->
        <div class="bg-accent-dark border-2 border-accent-light p-6 rounded-lg mb-6">
            <div class="flex items-center gap-3 mb-3">
                <svg class="w-6 h-6 text-accent-light" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8.684 13.342C8.886 12.938 9 12.482 9 12c0-.482-.114-.938-.316-1.342m0 2.684a3 3 0 110-2.684m0 2.684l6.632 3.316m-6.632-6l6.632-3.316m0 0a3 3 0 105.367-2.684 3 3 0 00-5.367 2.684zm0 9.316a3 3 0 105.368 2.684 3 3 0 00-5.368-2.684z"/>
                </svg>
                <h2 class="text-xl font-bold text-accent-light">Share This Link</h2>
            </div>
            <p class="text-sm text-text-primary mb-4">Send this URL to your opponent so they can submit their list:</p>
            <div class="flex gap-2 mb-3">
                <input readonly :value="exchangeUrl" class="flex-1 px-4 py-3 border-2 border-accent-mid rounded-lg font-mono text-sm bg-bg-darkest text-text-primary focus:outline-none focus:border-accent-light">
                <button @click="copyUrl" class="bg-primary hover:bg-primary-dark text-bg-darkest px-6 py-3 rounded-lg font-bold text-base shadow-lg transition">
                    <span x-text="urlCopied ? '✓ Copied!' : 'Copy Link'"></span>
                </button>
            </div>
            <p class="text-xs text-text-secondary italic">⚠️ Keep this page open - it will auto-refresh when your opponent submits their list</p>
        </div>

        <div class="bg-bg-darker p-6 rounded-lg mb-6 border border-bg-medium">
            <h3 class="font-semibold mb-2 text-accent-light">Your List Hash:</h3>
            <div class="flex gap-2">
                <code class="flex-1 bg-bg-darkest px-3 py-2 rounded text-xs break-all text-text-secondary" x-text="hash"></code>
                <button @click="copyHash" class="bg-accent-mid hover:bg-primary-dark text-white px-4 py-2 rounded text-sm font-semibold">
                    <span x-text="hashCopied ? 'Copied' : 'Copy'"></span>
                </button>
            </div>
            <p class="text-xs text-text-muted mt-2">Created: ${data.timestamp_a}</p>
        </div>

        <div class="text-center">
            <div class="inline-block mb-4">
                <svg class="w-16 h-16 text-accent-light animate-spin" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <circle cx="12" cy="12" r="10" stroke="currentColor" stroke-width="2" opacity="0.25"/>
                    <path d="M12 2 A10 10 0 0 1 22 12" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
                </svg>
            </div>
            <p class="text-text-secondary">Page will auto-refresh when opponent submits...</p>
        </div>
    </div>
</div>
    `;
}

function waitingPageLogic(exchangeId, hash) {
    return {
        exchangeUrl: `${window.location.protocol}//${window.location.host}/exchange/${exchangeId}`,
        hash: hash,
        urlCopied: false,
        hashCopied: false,

        copyUrl() {
            const textarea = document.createElement('textarea');
            textarea.value = this.exchangeUrl;
            textarea.style.position = 'fixed';
            textarea.style.opacity = '0';
            document.body.appendChild(textarea);
            textarea.select();
            try {
                document.execCommand('copy');
                this.urlCopied = true;
                setTimeout(() => this.urlCopied = false, 2000);
            } catch (err) {
                console.error('Failed to copy:', err);
                alert('Failed to copy. Please copy manually.');
            }
            document.body.removeChild(textarea);
        },

        copyHash() {
            const textarea = document.createElement('textarea');
            textarea.value = this.hash;
            textarea.style.position = 'fixed';
            textarea.style.opacity = '0';
            document.body.appendChild(textarea);
            textarea.select();
            try {
                document.execCommand('copy');
                this.hashCopied = true;
                setTimeout(() => this.hashCopied = false, 2000);
            } catch (err) {
                console.error('Failed to copy:', err);
            }
            document.body.removeChild(textarea);
        },

        init() {
            setInterval(async () => {
                const res = await fetch(`/api/herald/exchange/${exchangeId}/status`);
                const data = await res.json();
                if (data.ready) window.location.reload();
            }, 5000);
        }
    }
}
