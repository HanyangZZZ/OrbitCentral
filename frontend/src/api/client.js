import axios from 'axios'

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL ?? '/api'
})

// ── Categories ────────────────────────────────────────────────────────────────
export const getCategories = (params) => api.get('/categories/', { params })
export const createCategory = (payload) => api.post('/categories/', payload)
export const updateCategory = (id, payload) => api.patch(`/categories/${id}/`, payload)
export const deleteCategory = (id) => api.delete(`/categories/${id}/`)

// ── Tags ──────────────────────────────────────────────────────────────────────
/**
 * List / search tags.
 * @param {Object} [params]
 * @param {string} [params.q]         — partial name search
 * @param {number} [params.min_usage] — hide tags used fewer times
 */
export const getTags = (params) => api.get('/tags/', { params })
export const getTag = (id) => api.get(`/tags/${id}/`)
/**
 * Semantic vector search for tags.
 * @param {Object} params
 * @param {string} params.q     — search query (required)
 * @param {number} [params.limit]     — max results (default 20)
 * @param {number} [params.min_usage] — min business count
 */
export const searchTags = (params) => api.get('/tags/search/', { params })

// ── Businesses ────────────────────────────────────────────────────────────────
export const getBusinesses = (params) => api.get('/businesses/', { params })
export const getBusiness = (id) => api.get(`/businesses/${id}/`)
export const createBusiness = (payload) => api.post('/businesses/', payload)
export const updateBusiness = (id, payload) => api.patch(`/businesses/${id}/`, payload)
export const deleteBusiness = (id) => api.delete(`/businesses/${id}/`)

// ── Vector Search ─────────────────────────────────────────────────────────────
/**
 * Weighted semantic search for businesses.
 * @param {Object} params
 * @param {string}   params.q          — search query (required)
 * @param {number}   [params.lat]      — user latitude
 * @param {number}   [params.lng]      — user longitude
 * @param {number}   [params.category] — category id filter
 * @param {number[]} [params.tag]      — tag id(s) filter
 * @param {string}   [params.sort]     — "distance" | "rating"
 * @param {number}   [params.limit]    — max results (default 10)
 */
export const searchBusinesses = (params = {}) => {
  // Build params, supporting tag as array
  const p = {}
  for (const [k, v] of Object.entries(params)) {
    if (v != null && v !== '' && !(Array.isArray(v) && v.length === 0)) p[k] = v
  }
  return api.get('/businesses/search/', { params: p, paramsSerializer: { indexes: null } })
}

// ── Stats ─────────────────────────────────────────────────────────────────────
export const getStats = () => api.get('/businesses/stats/')

export default api
