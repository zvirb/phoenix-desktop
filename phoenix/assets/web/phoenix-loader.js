/**
 * Phoenix Data Loader
 * Connects standalone HTML prototypes to the live Phoenix Backend.
 */

const PHOENIX_API_BASE = localStorage.getItem('phoenix_core_url') || 'http://localhost:8000'; // Dynamic backend
const DEVICE_ID = 'phoenix-example-viewer-' + Math.floor(Math.random() * 10000);

class PhoenixAPI {
    constructor() {
        this.token = localStorage.getItem('phoenix_access_token');
        this.deviceId = localStorage.getItem('phoenix_device_id') || DEVICE_ID;
        if (!localStorage.getItem('phoenix_device_id')) {
            localStorage.setItem('phoenix_device_id', this.deviceId);
        }
    }

    async authenticate() {
        try {
            const response = await fetch(`${PHOENIX_API_BASE}/api/v1/devices/authenticate`, {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${this.deviceId}`,
                    'Content-Type': 'application/json'
                }
            });

            if (response.ok) {
                const data = await response.json();
                if (data.access_token) {
                    this.token = data.access_token;
                    localStorage.setItem('phoenix_access_token', this.token);
                    console.log('Phoenix Auth: Success');
                    return true;
                }
            }
            console.error('Phoenix Auth: Failed', response.status);
            return false;
        } catch (e) {
            console.error('Phoenix Auth: Error', e);
            return false;
        }
    }

    async makeRequest(endpoint, method = 'GET', body = null) {
        if (!this.token) {
            const success = await this.authenticate();
            if (!success) throw new Error("Authentication failed");
        }

        const headers = {
            'Authorization': `Bearer ${this.token}`,
            'Content-Type': 'application/json'
        };

        try {
            let response = await fetch(`${PHOENIX_API_BASE}${endpoint}`, {
                method,
                headers,
                body: body ? JSON.stringify(body) : null
            });

            if (response.status === 401) {
                // Retry once
                console.log('Phoenix API: 401, retrying auth...');
                await this.authenticate();
                headers['Authorization'] = `Bearer ${this.token}`;
                response = await fetch(`${PHOENIX_API_BASE}${endpoint}`, {
                    method,
                    headers,
                    body: body ? JSON.stringify(body) : null
                });
            }

            if (!response.ok) {
                throw new Error(`API Error: ${response.status}`);
            }

            return await response.json();
        } catch (e) {
            console.error(`Phoenix Request Error (${endpoint}):`, e);
            throw e;
        }
    }

    async getGamificationProfile() {
        return this.makeRequest('/api/v1/gamification/profile');
    }

    async getFocusStats() {
        return this.makeRequest('/api/v1/focus/stats');
    }

    async getDailyChallenges() {
        return this.makeRequest('/api/v1/gamification/daily-challenges');
    }

    // Helper to calculate latency
    async checkLatency() {
        const start = performance.now();
        try {
            await fetch(`${PHOENIX_API_BASE}/`, { method: 'GET', mode: 'no-cors' });
            // no-cors is safer for simple ping if backend doesn't support CORS on root or health
        } catch (e) {
            console.warn("Latency check failed", e);
            return 9999;
        }
        return Math.round(performance.now() - start);
    }
}

// Global instance
window.phoenixAPI = new PhoenixAPI();

// Global Helper for updating generic elements
window.updateElement = (id, value) => {
    const el = document.getElementById(id);
    if (el) el.innerText = value;
};

// Auto-init if requested
document.addEventListener('DOMContentLoaded', () => {
    console.log("Phoenix Loader Initialized");
});
