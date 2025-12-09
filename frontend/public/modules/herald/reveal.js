// Herald reveal page
window.heraldRevealPage = function(exchangeId) {
    // Fetch exchange data
    fetch(`/api/herald/exchange/${exchangeId}`)
        .then(res => res.json())
        .then(data => {
            const content = document.getElementById('app-content');
            content.innerHTML = renderRevealPage(data);
        });

    return '<div class="max-w-3xl mx-auto mt-10 px-4 text-center"><p>Loading...</p></div>';
};

function renderRevealPage(data) {
    return `
<div class="max-w-6xl mx-auto mt-10 px-4" x-data="revealPageLogic()">
    <h1 class="text-3xl font-montserrat text-center mb-4 text-accent-light">Exchange Complete</h1>
    <p class="text-center text-sm text-text-muted mb-8">Lists are stored for 30 days only. Save them now if needed.</p>

    <div class="grid md:grid-cols-2 gap-6">
        <!-- Player A -->
        <div class="bg-bg-dark rounded-lg shadow-lg p-6 border border-bg-medium">
            <h2 class="text-xl font-bold mb-4 text-accent-mid">Player A's List</h2>
            <pre class="bg-bg-darker p-4 rounded text-xs overflow-auto mb-4 max-h-96 text-text-primary border border-bg-medium">${escapeHtml(data.list_a)}</pre>
            <button @click="copyListA('${escapeForJS(data.list_a)}')" class="bg-primary hover:bg-primary-dark text-bg-darkest px-4 py-2 rounded mb-2 w-full font-semibold">
                <span x-text="copiedA ? 'Copied!' : 'Copy List'"></span>
            </button>
            <div class="bg-bg-darker p-3 rounded border border-bg-medium">
                <p class="text-xs font-semibold mb-1 text-accent-light">Hash:</p>
                <code class="text-xs break-all text-text-secondary">${data.hash_a}</code>
                <button @click="verifyA('${escapeForJS(data.list_a)}', '${data.hash_a}')" class="mt-2 bg-accent-mid hover:bg-primary-dark text-white px-3 py-1 rounded text-xs w-full font-semibold">Verify</button>
                <div x-show="verifiedA !== null" :class="verifiedA ? 'bg-primary bg-opacity-20 text-primary' : 'bg-accent-mid bg-opacity-20 text-accent-mid'"
                    class="mt-2 p-2 rounded text-xs" x-text="verifiedA ? 'Hash verified!' : 'Hash mismatch!'"></div>
                <p class="text-xs text-text-muted mt-2">${data.timestamp_a}</p>
            </div>
        </div>

        <!-- Player B -->
        <div class="bg-bg-dark rounded-lg shadow-lg p-6 border border-bg-medium">
            <h2 class="text-xl font-bold mb-4 text-accent-mid">Player B's List</h2>
            <pre class="bg-bg-darker p-4 rounded text-xs overflow-auto mb-4 max-h-96 text-text-primary border border-bg-medium">${escapeHtml(data.list_b)}</pre>
            <button @click="copyListB('${escapeForJS(data.list_b)}')" class="bg-primary hover:bg-primary-dark text-bg-darkest px-4 py-2 rounded mb-2 w-full font-semibold">
                <span x-text="copiedB ? 'Copied!' : 'Copy List'"></span>
            </button>
            <div class="bg-bg-darker p-3 rounded border border-bg-medium">
                <p class="text-xs font-semibold mb-1 text-accent-light">Hash:</p>
                <code class="text-xs break-all text-text-secondary">${data.hash_b}</code>
                <button @click="verifyB('${escapeForJS(data.list_b)}', '${data.hash_b}')" class="mt-2 bg-accent-mid hover:bg-primary-dark text-white px-3 py-1 rounded text-xs w-full font-semibold">Verify</button>
                <div x-show="verifiedB !== null" :class="verifiedB ? 'bg-primary bg-opacity-20 text-primary' : 'bg-accent-mid bg-opacity-20 text-accent-mid'"
                    class="mt-2 p-2 rounded text-xs" x-text="verifiedB ? 'Hash verified!' : 'Hash mismatch!'"></div>
                <p class="text-xs text-text-muted mt-2">${data.timestamp_b}</p>
            </div>
        </div>
    </div>
</div>
    `;
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function escapeForJS(text) {
    return text.replace(/\\/g, '\\\\').replace(/'/g, "\\'").replace(/"/g, '\\"').replace(/\n/g, '\\n').replace(/\r/g, '\\r');
}

function revealPageLogic() {
    return {
        copiedA: false,
        copiedB: false,
        verifiedA: null,
        verifiedB: null,

        copyListA(listA) {
            const textarea = document.createElement('textarea');
            textarea.value = listA;
            textarea.style.position = 'fixed';
            textarea.style.opacity = '0';
            document.body.appendChild(textarea);
            textarea.select();
            try {
                document.execCommand('copy');
                this.copiedA = true;
                setTimeout(() => this.copiedA = false, 2000);
            } catch (err) {
                console.error('Failed to copy:', err);
            }
            document.body.removeChild(textarea);
        },

        copyListB(listB) {
            const textarea = document.createElement('textarea');
            textarea.value = listB;
            textarea.style.position = 'fixed';
            textarea.style.opacity = '0';
            document.body.appendChild(textarea);
            textarea.select();
            try {
                document.execCommand('copy');
                this.copiedB = true;
                setTimeout(() => this.copiedB = false, 2000);
            } catch (err) {
                console.error('Failed to copy:', err);
            }
            document.body.removeChild(textarea);
        },

        async verifyA(listA, hashA) {
            const hash = await this.sha256(listA);
            this.verifiedA = hash === hashA;
        },

        async verifyB(listB, hashB) {
            const hash = await this.sha256(listB);
            this.verifiedB = hash === hashB;
        },

        async sha256(str) {
            const buf = await crypto.subtle.digest('SHA-256', new TextEncoder().encode(str));
            return Array.from(new Uint8Array(buf)).map(b => b.toString(16).padStart(2, '0')).join('');
        }
    }
}
