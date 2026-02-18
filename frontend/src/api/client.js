import axios from 'axios'

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL ?? '/api'
})

// ── Auth helpers ──────────────────────────────────────────────────────────────
/** Set the auth token for all subsequent API requests. */
export const setAuthToken = (token) => {
  if (token) {
    api.defaults.headers.common['Authorization'] = `Token ${token}`
  } else {
    delete api.defaults.headers.common['Authorization']
  }
}

/**
 * Register a new account.
 * POST /api/auth/register/  {email, username, password, display_name?}
 * Returns { token, user, detail }
 */
export const register = (payload) => api.post('/auth/register/', payload)

/**
 * Login — obtain auth token + user profile.
 * POST /api/auth/login/  {username, password}
 * Accepts username or email as the "username" field.
 * Returns { token, user }
 */
export const login = (username, password) => api.post('/auth/login/', { username, password })

/**
 * Verify email with a token from the verification email.
 * POST /api/auth/verify-email/  {token}
 */
export const verifyEmail = (token) => api.post('/auth/verify-email/', { token })

/**
 * Get current user profile.
 * GET /api/auth/me/  (auth required)
 */
export const getMe = () => api.get('/auth/me/')

/**
 * Update current user profile.
 * PATCH /api/auth/me/  (auth required)
 */
export const updateMe = (payload) => api.patch('/auth/me/', payload)

/**
 * Resend verification email.
 * POST /api/auth/resend-verify/  (auth required)
 */
export const resendVerify = () => api.post('/auth/resend-verify/')

/**
 * Logout — delete the server-side auth token.
 * POST /api/auth/logout/  (auth required)
 */
export const logout = () => api.post('/auth/logout/')

/**
 * Delete the current user's account.
 * Reviews are anonymized (shown as 'Deleted User'), everything else is removed.
 * DELETE /api/auth/me/  (auth required)
 */
export const deleteAccount = () => api.delete('/auth/me/')

/**
 * Request a password-reset email.
 * POST /api/auth/forgot-password/  {email}
 * Always returns 200 (prevents email enumeration).
 */
export const forgotPassword = (email) => api.post('/auth/forgot-password/', { email })

/**
 * Reset password using a token from the reset email.
 * POST /api/auth/reset-password/  {token, new_password}
 */
export const resetPassword = (token, newPassword) =>
  api.post('/auth/reset-password/', { token, new_password: newPassword })

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

// ── Reviews ───────────────────────────────────────────────────────────────────
/**
 * List reviews for a business.
 * @param {Object} params
 * @param {number} params.business — business id (required)
 * @param {number} [params.rating] — filter by rating (1-5)
 */
export const getReviews = (params) => api.get('/reviews/', { params })
export const getReview = (id) => api.get(`/reviews/${id}/`)

/**
 * Create a review (auth required).
 * @param {Object} payload
 * @param {number} payload.business — business id
 * @param {number} payload.rating — 1–5
 * @param {string} [payload.description]
 * @param {string} [payload.photo] — base64-encoded image (optional)
 */
export const createReview = (payload) => api.post('/reviews/', payload)
export const updateReview = (id, payload) => api.patch(`/reviews/${id}/`, payload)
export const deleteReview = (id) => api.delete(`/reviews/${id}/`)

/**
 * Toggle a helpfulness vote on a review.
 * POST /api/reviews/:id/vote/  {vote_type: "useful"|"funny"|"cool"}
 * Auth + verified email required. Toggles on/off.
 * Returns { status: "added"|"removed", vote_type }
 */
export const voteReview = (reviewId, voteType) =>
  api.post(`/reviews/${reviewId}/vote/`, { vote_type: voteType })

// ── Bookmarks ─────────────────────────────────────────────────────────────────
/** List current user's bookmarks. Auth required. */
export const getBookmarks = (params) => api.get('/bookmarks/', { params })
/** Bookmark a business. Auth required. */
export const createBookmark = (payload) => api.post('/bookmarks/', payload)
/** Update bookmark note. Auth required. */
export const updateBookmark = (id, payload) => api.patch(`/bookmarks/${id}/`, payload)
/** Remove a bookmark. Auth required. */
export const deleteBookmark = (id) => api.delete(`/bookmarks/${id}/`)
/** Toggle bookmark on/off. Returns { status: 'added'|'removed', bookmark? } */
export const toggleBookmark = (businessId) => api.post('/bookmarks/toggle/', { business: businessId })
/** Check if business is bookmarked. Returns { bookmarked: bool } */
export const checkBookmark = (businessId) => api.get('/bookmarks/check/', { params: { business: businessId } })
/** Get all bookmarked business IDs. Returns { business_ids: number[] } */
export const getBookmarkIds = () => api.get('/bookmarks/ids/')

export default api
