/* ==========================================================================
   API — Configuration & Fetch Helpers
   Calls the CLOUD Orbit backend (business.orbitcentral.ca) for live data.
   Proxied through serve.py to avoid CORS. Auto-authenticates on first call.
   NOTE: All data is on the CLOUD database — never use local Docker for demos.
   ========================================================================== */

const API = {
  base: '/api',
  _token: null,
  _loginPromise: null,

  /* ── Auth ─────────────────────────────────────────────────────────────── */
  async _ensureAuth() {
    if (this._token) return this._token;
    if (this._loginPromise) return this._loginPromise;
    const creds = window.ORBIT_DEMO_CREDENTIALS;
    if (!creds) {
      console.warn('[Orbit] No demo credentials configured (see js/config.example.js) — auth-only endpoints will be skipped.');
      return null;
    }
    this._loginPromise = (async () => {
      try {
        const res = await fetch(`${this.base}/auth/login/`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(creds),
        });
        if (!res.ok) throw new Error(`Login ${res.status}`);
        const data = await res.json();
        this._token = data.token;
        console.info('[Orbit] Authenticated as', data.user?.display_name || data.user?.username);
        return this._token;
      } catch (e) {
        console.warn('[Orbit] Auto-login failed:', e.message);
        this._loginPromise = null;
        return null;
      }
    })();
    return this._loginPromise;
  },

  /* ── Fetchers ─────────────────────────────────────────────────────────── */
  async get(endpoint, { auth = false } = {}) {
    try {
      const headers = {};
      if (auth) {
        const token = await this._ensureAuth();
        if (token) headers['Authorization'] = `Token ${token}`;
      }
      const res = await fetch(`${this.base}${endpoint}`, { headers });
      if (!res.ok) throw new Error(`API ${res.status}`);
      return await res.json();
    } catch (e) {
      console.warn(`[Orbit] API call failed: ${endpoint}`, e.message);
      return null;
    }
  },

  async post(endpoint, body = {}) {
    try {
      const token = await this._ensureAuth();
      const headers = { 'Content-Type': 'application/json' };
      if (token) headers['Authorization'] = `Token ${token}`;
      const res = await fetch(`${this.base}${endpoint}`, {
        method: 'POST',
        headers,
        body: JSON.stringify(body),
      });
      if (!res.ok) throw new Error(`API ${res.status}`);
      return await res.json();
    } catch (e) {
      console.warn(`[Orbit] API POST failed: ${endpoint}`, e.message);
      return null;
    }
  },

  /* ── Convenience Methods ──────────────────────────────────────────────── */
  async getStats()            { return this.get('/businesses/stats/'); },
  async getCategories()       { return this.get('/categories/?page_size=100'); },
  async getTags(limit = 20)   { return this.get(`/tags/?page_size=${limit}`); },
  async getBusinesses(params)  { return this.get(`/businesses/?page_size=6${params ? '&' + params : ''}`); },
  async searchBusinesses(q)    { return this.get(`/businesses/search/?q=${encodeURIComponent(q)}&limit=5`, { auth: true }); },
  async getReviews(bizId)      { return this.get(`/reviews/?business=${bizId}&page_size=3`); },
  async getAllReviews(limit=5)  { return this.get(`/reviews/?page_size=${limit}`); },
  async searchTags(q)          { return this.get(`/tags/search/?q=${encodeURIComponent(q)}`); },
  async getBookmarkIds()       { return this.get('/bookmarks/ids/', { auth: true }); },
  async getBookmarks()         { return this.get('/bookmarks/', { auth: true }); },
  async toggleBookmark(bizId)  { return this.post('/bookmarks/toggle/', { business: bizId }); },
};
