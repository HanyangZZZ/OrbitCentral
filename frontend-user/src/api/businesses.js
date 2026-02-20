/**
 * businesses.js — Business CRUD, Search, Photos & Stats
 * =======================================================
 * PURPOSE:
 *   Every business-related API call lives here. Searching, fetching
 *   details, building photo URLs, AI personalization, geocoding.
 *
 * MODULAR LOGIC:
 *   Organized by concern: CRUD → photos → search → AI → geo → stats.
 *   The searchBusinesses() function filters out empty params so the
 *   backend never receives junk query strings.
 *
 * OOP FLOW:
 *   core.js (base Axios) → this file adds business endpoints →
 *   composables (useSearchApi, useNearbyForYou, useBusinessDetail)
 *   import these functions to talk to the backend.
 */
import api from './core'

// ── CRUD ─────────────────────────────────────────────────────────────────────
export const getBusinesses  = (params)       => api.get('/businesses/', { params })
export const getBusiness    = (id)           => api.get(`/businesses/${id}/`)
export const createBusiness = (payload)      => api.post('/businesses/', payload)
export const updateBusiness = (id, payload)  => api.patch(`/businesses/${id}/`, payload)
export const deleteBusiness = (id)           => api.delete(`/businesses/${id}/`)

// ── Photo URL (not an API call — builds a URL string) ────────────────────────
export const getBusinessPhotoUrl = (id, { idx = 0, maxHeight = 400 } = {}) =>
  `${api.defaults.baseURL}/businesses/${id}/photo/?idx=${idx}&maxHeight=${maxHeight}`

// ── Vector search ────────────────────────────────────────────────────────────
export function searchBusinesses(params = {}) {
  const p = {}
  for (const [k, v] of Object.entries(params)) {
    if (v != null && v !== '' && !(Array.isArray(v) && v.length === 0)) p[k] = v
  }
  return api.get('/businesses/search/', { params: p, paramsSerializer: { indexes: null } })
}

// ── AI Personalization (auth + verified email required) ──────────────────────
export const getPersonalized = (params = {}) =>
  api.get('/businesses/personalized/', { params })

// ── Reverse Geocode ──────────────────────────────────────────────────────────
export const reverseGeocode = (lat, lng) =>
  api.get('/businesses/geocode/', { params: { lat, lng } })

// ── Stats ────────────────────────────────────────────────────────────────────
export const getStats = () => api.get('/businesses/stats/')
