import axios from 'axios'

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL ?? '/api',
  withCredentials: true,   // send/receive HttpOnly auth cookies
})

// ── Auth helpers ──────────────────────────────────────────────────────────────
const TOKEN_KEY = 'fblc_auth_token'

/**
 * Set (or clear) the auth token for all subsequent API requests.
 * Persists to localStorage so the session survives page refreshes.
 */
export const setAuthToken = (token) => {
  if (token) {
    localStorage.setItem(TOKEN_KEY, token)
    api.defaults.headers.common['Authorization'] = `Token ${token}`
  } else {
    localStorage.removeItem(TOKEN_KEY)
    delete api.defaults.headers.common['Authorization']
  }
}

/** Return the saved token (if any) without touching the header. */
export const getSavedToken = () => localStorage.getItem(TOKEN_KEY) || ''

// Auto-restore token on module load so the very first request is authenticated
const _saved = getSavedToken()
if (_saved) {
  api.defaults.headers.common['Authorization'] = `Token ${_saved}`
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
 * Logout — delete the server-side auth token and clear cookie.
 * POST /api/auth/logout/  (auth required)
 * Also clears the local token.
 */
export const logout = () => {
  localStorage.removeItem(TOKEN_KEY)
  delete api.defaults.headers.common['Authorization']
  return api.post('/auth/logout/')
}

/**
 * Auto-login: try to restore session from cookie or localStorage.
 * Call on app startup. Returns the user profile if authenticated, null otherwise.
 *
 * Priority:
 *   1. localStorage token → sets header, calls /auth/me/
 *   2. HttpOnly cookie (browser sends it automatically) → calls /auth/me/
 */
export const autoLogin = async () => {
  try {
    const { data } = await getMe()
    return data
  } catch {
    // Cookie or token expired / invalid — clear any stale localStorage
    localStorage.removeItem(TOKEN_KEY)
    delete api.defaults.headers.common['Authorization']
    return null
  }
}

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

/**
 * Get a proxied Google Places photo URL for a business.
 * Returns a URL string (use as <img src>).  The backend 302-redirects to the real photo.
 * @param {number} id — business id
 * @param {Object} [opts]
 * @param {number} [opts.idx=0]        — photo index (0 = primary)
 * @param {number} [opts.maxHeight=400] — max pixel height
 * @returns {string} URL
 */
export const getBusinessPhotoUrl = (id, { idx = 0, maxHeight = 400 } = {}) =>
  `${api.defaults.baseURL}/businesses/${id}/photo/?idx=${idx}&maxHeight=${maxHeight}`

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

// ── Personalized Recommendations ──────────────────────────────────────────────
/**
 * AI-personalized business recommendations based on user's reviews & bookmarks.
 * @param {Object} [params]
 * @param {number} [params.lat]   — user latitude (recommended)
 * @param {number} [params.lng]   — user longitude (recommended)
 * @param {number} [params.limit] — max results (default 5, max 20)
 */
export const getPersonalized = (params = {}) => api.get('/businesses/personalized/', { params })

// ── Geocode ───────────────────────────────────────────────────────────────────
/**
 * Reverse-geocode coordinates to city + province.
 * @param {number} lat — latitude
 * @param {number} lng — longitude
 * @returns {{ city, province, province_code, country, country_code, formatted_address }}
 */
export const reverseGeocode = (lat, lng) => api.get('/businesses/geocode/', { params: { lat, lng } })

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

// ── AI Reviews ────────────────────────────────────────────────────────────────
/** List user's AI review chat sessions. Auth required. */
export const getAIReviewSessions = () => api.get('/ai-reviews/')
/** Get a specific AI review chat session by UUID. */
export const getAIReviewSession = (id) => api.get(`/ai-reviews/${id}/`)
/**
 * Start a new AI-guided review chat.
 * POST /api/ai-reviews/start/  {business, rating}
 * Returns session with AI's opening message.
 */
export const startAIReview = (businessId, rating) =>
  api.post('/ai-reviews/start/', { business: businessId, rating })
/**
 * Send a message in an AI review chat.
 * POST /api/ai-reviews/:id/message/  {message}
 * Returns { reply, tags_added, tags_removed, session }
 */
export const sendAIReviewMessage = (sessionId, message) =>
  api.post(`/ai-reviews/${sessionId}/message/`, { message })
/**
 * Generate the final review text from the conversation.
 * POST /api/ai-reviews/:id/generate/
 * Returns { generated_description, session }
 */
export const generateAIReview = (sessionId) =>
  api.post(`/ai-reviews/${sessionId}/generate/`)
/**
 * Confirm and create the actual Review from the AI session.
 * POST /api/ai-reviews/:id/confirm/
 * Returns { review, tags_added, tags_removed }
 */
export const confirmAIReview = (sessionId) =>
  api.post(`/ai-reviews/${sessionId}/confirm/`)
/** Abandon an AI review session. DELETE /api/ai-reviews/:id/ */
export const abandonAIReview = (sessionId) =>
  api.delete(`/ai-reviews/${sessionId}/`)

// ── Pagination helper ─────────────────────────────────────────────────────────
/**
 * Fetch the next page from a cursor-paginated response.
 * Pass the `next` URL from a previous response.
 * Works for reviews (cursor) and businesses (page number).
 * @param {string} nextUrl — the full `next` URL from a previous response
 * @returns {Promise} axios response
 */
export const getNextPage = (nextUrl) => {
  if (!nextUrl) return Promise.reject(new Error('No next page'))
  // nextUrl is absolute; extract path + query relative to baseURL
  try {
    const u = new URL(nextUrl)
    return api.get(u.pathname + u.search)
  } catch {
    return api.get(nextUrl)
  }
}

export default api
