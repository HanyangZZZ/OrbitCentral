/**
 * core.js — API Foundation Layer
 * ================================
 * PURPOSE:
 *   Sets up the shared Axios HTTP client that every other API module uses.
 *   Handles auth token storage/retrieval and pagination helpers.
 *
 * MODULAR LOGIC:
 *   This is the "base" of our API layer. Other files (auth.js,
 *   businesses.js, etc.) import `api` from here and build on top of it.
 *   Networking config stays in one spot — if the base URL ever changes,
 *   you only update it here.
 *
 * OOP FLOW:
 *   api (Axios instance) → setToken/getToken manage auth headers →
 *   domain modules call api.get/post/patch/delete for their endpoints.
 */
import axios from 'axios'

// Create a pre-configured Axios instance — all requests go through this
const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL ?? '/api',
})

// ── Token Helpers ────────────────────────────────────────────────────────
// The backend uses token-based auth. These helpers store/retrieve the
// token from localStorage and attach it to every outgoing request.
const TOKEN_KEY = 'fblc_auth_token'
const CONSENT_KEY = 'cookie_consent'

/** Save (or clear) the auth token in localStorage and Axios headers */
export function setAuthToken(token) {
  if (token) {
    // Always set the header so the current session works
    api.defaults.headers.common['Authorization'] = `Token ${token}`
    // Only persist to localStorage if the user accepted cookie/storage consent
    if (localStorage.getItem(CONSENT_KEY) === 'accepted') {
      localStorage.setItem(TOKEN_KEY, token)
    }
  } else {
    localStorage.removeItem(TOKEN_KEY)
    delete api.defaults.headers.common['Authorization']
  }
}

/** Retrieve the stored token (returns empty string if none) */
export function getSavedToken() {
  return localStorage.getItem(TOKEN_KEY) || ''
}

// Auto-restore token on page load so returning users stay logged in
const saved = getSavedToken()
if (saved) api.defaults.headers.common['Authorization'] = `Token ${saved}`

// ── Pagination Helper ────────────────────────────────────────────────────
// The backend returns paginated lists with a `next` URL.
// This function fetches the next page using that URL.

/** Fetch the next page of paginated results */
export function getNextPage(nextUrl) {
  if (!nextUrl) return Promise.reject(new Error('No next page'))
  try {
    const u = new URL(nextUrl)
    return api.get(u.pathname + u.search)
  } catch {
    return api.get(nextUrl)
  }
}

export default api
