/**
 * Authentication Utilities
 * 
 * Helpers for JWT token management and auth state
 */

// ═══════════════════════════════════════════════
// TOKEN MANAGEMENT
// ═══════════════════════════════════════════════

export function getToken() {
    return localStorage.getItem('squig_token');
}

export function setToken(token) {
    localStorage.setItem('squig_token', token);
}

export function clearToken() {
    localStorage.removeItem('squig_token');
    localStorage.removeItem('squig_user');
}

export function getUser() {
    const userJson = localStorage.getItem('squig_user');
    return userJson ? JSON.parse(userJson) : null;
}

export function isAuthenticated() {
    return !!getToken();
}

// ═══════════════════════════════════════════════
// API REQUESTS WITH AUTH
// ═══════════════════════════════════════════════

export function getAuthHeaders() {
    const token = getToken();
    return token ? {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
    } : {
        'Content-Type': 'application/json',
    };
}

export async function authenticatedFetch(url, options = {}) {
    const headers = {
        ...getAuthHeaders(),
        ...options.headers,
    };
    
    const response = await fetch(url, {
        ...options,
        headers,
    });
    
    // Handle token expiration
    if (response.status === 401 || response.status === 403) {
        clearToken();
        const currentPath = window.location.hash;
        window.location.hash = `#/squire/login?return=${encodeURIComponent(currentPath)}`;
        throw new Error('Authentication required');
    }
    
    return response;
}

// ═══════════════════════════════════════════════
// LOGOUT
// ═══════════════════════════════════════════════

export function logout() {
    clearToken();
    window.location.hash = '#/';
}

// ═══════════════════════════════════════════════
// ROUTE PROTECTION
// ═══════════════════════════════════════════════

export function requireAuth() {
    if (!isAuthenticated()) {
        const currentPath = window.location.hash;
        window.location.hash = `#/squire/login?return=${encodeURIComponent(currentPath)}`;
        return false;
    }
    return true;
}

// ═══════════════════════════════════════════════
// CURRENT USER INFO
// ═══════════════════════════════════════════════

export async function fetchCurrentUser() {
    if (!isAuthenticated()) {
        return null;
    }
    
    try {
        const response = await authenticatedFetch('/api/squire/auth/me');
        if (!response.ok) {
            clearToken();
            return null;
        }
        
        const user = await response.json();
        localStorage.setItem('squig_user', JSON.stringify(user));
        return user;
        
    } catch (error) {
        return null;
    }
}
