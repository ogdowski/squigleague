// Herald respond page
window.matchupRespondPage = function(exchangeId) {
    // Fetch exchange data
    fetch(`/api/matchup/exchange/${exchangeId}`)
        .then(res => res.json())
        .then(data => {
            const content = document.getElementById('app-content');
            content.innerHTML = renderRespondPage(exchangeId, data);
        });

    return '<div class="max-w-3xl mx-auto mt-10 px-4 text-center"><p>Loading...</p></div>';
};

function renderRespondPage(exchangeId, data) {
    return `
<div class="max-w-3xl mx-auto mt-10 px-4" x-data="respondPageLogic('${exchangeId}', '${data.hash_a}')">
    <div class="bg-bg-dark rounded-lg shadow-lg p-8 border border-bg-medium">
        <h1 class="text-3xl font-bold text-center mb-6 text-accent-light">Submit Your List</h1>

        <div class="bg-bg-darker border-l-4 border-accent-light p-4 mb-6 rounded-r-lg">
            <h3 class="font-semibold text-accent-light mb-2">Important: Opponent's Hash</h3>
            <div class="flex gap-2">
                <code class="flex-1 bg-bg-darkest px-3 py-2 rounded text-xs break-all text-text-secondary" x-text="opponentHash"></code>
                <button @click="copyHash" class="bg-accent-mid hover:bg-primary-dark text-white px-3 py-2 rounded text-sm font-semibold">
                    <span x-text="copied ? 'Copied' : 'Copy'"></span>
                </button>
            </div>
            <p class="text-sm text-text-secondary mt-2">This proves their list is locked and can't be changed.</p>
        </div>

        <form @submit.prevent="submitList" class="space-y-4">
            <div>
                <label class="block text-sm font-medium mb-2 text-text-primary">Your Army List:</label>
                <textarea x-model="listContent" rows="10" required maxlength="50000"
                    class="w-full px-4 py-3 border border-bg-medium rounded-lg font-mono text-sm bg-bg-darker text-text-primary placeholder-text-muted focus:outline-none focus:ring-2 focus:ring-primary"
                    placeholder="Paste your army list here..."></textarea>
                <p class="text-xs text-text-muted mt-1" x-show="listContent.length > 0">
                    <span x-text="listContent.length"></span> / 50,000
                </p>
            </div>

            <div x-show="error" class="bg-accent-mid bg-opacity-20 border border-accent-mid text-accent-light px-4 py-3 rounded text-sm" x-text="error"></div>

            <button type="submit" :disabled="loading"
                :class="loading ? 'bg-bg-medium cursor-not-allowed' : 'bg-primary hover:bg-primary-dark'"
                class="w-full text-bg-darkest font-semibold py-4 rounded-lg transition">
                <span x-show="!loading">Submit & Reveal Both Lists</span>
                <span x-show="loading">Submitting...</span>
            </button>
        </form>
    </div>
</div>
    `;
}

function respondPageLogic(exchangeId, opponentHash) {
    return {
        listContent: '',
        loading: false,
        error: null,
        copied: false,
        opponentHash: opponentHash,

        copyHash() {
            const textarea = document.createElement('textarea');
            textarea.value = this.opponentHash;
            textarea.style.position = 'fixed';
            textarea.style.opacity = '0';
            document.body.appendChild(textarea);
            textarea.select();
            try {
                document.execCommand('copy');
                this.copied = true;
                setTimeout(() => this.copied = false, 2000);
            } catch (err) {
                console.error('Failed to copy:', err);
            }
            document.body.removeChild(textarea);
        },

        async submitList() {
            if (!this.listContent.trim()) {
                this.error = 'Please enter your list';
                return;
            }

            this.loading = true;
            this.error = null;

            try {
                const res = await fetch(`/api/matchup/exchange/${exchangeId}/respond`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ list_content: this.listContent })
                });

                if (res.status === 429) {
                    this.error = 'Rate limit exceeded. Wait and try again.';
                    return;
                }

                if (res.ok) {
                    window.location.reload();
                } else {
                    this.error = 'Failed to submit. Try again.';
                }
            } catch (err) {
                this.error = 'Network error. Try again.';
            } finally {
                this.loading = false;
            }
        }
    }
}
