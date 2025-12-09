// API Configuration
const API_CONFIG = {
    // For local development: backend runs on port 8000
    // For production: nginx proxies /api to backend
    baseUrl: window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1'
        ? 'http://localhost:8000'
        : ''  // Production uses same origin with nginx proxy
};

// Helper to build API URL
function getApiUrl(path) {
    // Remove leading slash if present
    const cleanPath = path.startsWith('/') ? path : '/' + path;
    return API_CONFIG.baseUrl + cleanPath;
}
