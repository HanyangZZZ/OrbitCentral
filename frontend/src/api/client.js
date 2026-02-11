import axios from 'axios'

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL ?? '/api'
})

// ── Users ─────────────────────────────────────────────────────────────────────
export const getUsers = (params) => api.get('/users/', { params })
export const createUser = (payload) => api.post('/users/', payload)
export const updateUser = (id, payload) => api.patch(`/users/${id}/`, payload)
export const deleteUser = (id) => api.delete(`/users/${id}/`)

// ── Profiles ──────────────────────────────────────────────────────────────────
export const getProfiles = (params) => api.get('/profiles/', { params })
export const upsertProfile = (payload) => api.post('/profiles/', payload)
export const updateProfile = (userId, payload) => api.patch(`/profiles/${userId}/`, payload)
export const deleteProfile = (userId) => api.delete(`/profiles/${userId}/`)

// ── Categories ────────────────────────────────────────────────────────────────
export const getCategories = (params) => api.get('/categories/', { params })
export const createCategory = (payload) => api.post('/categories/', payload)
export const updateCategory = (id, payload) => api.patch(`/categories/${id}/`, payload)
export const deleteCategory = (id) => api.delete(`/categories/${id}/`)

// ── Businesses ────────────────────────────────────────────────────────────────
export const getBusinesses = (params) => api.get('/businesses/', { params })
export const createBusiness = (payload) => api.post('/businesses/', payload)
export const updateBusiness = (id, payload) => api.patch(`/businesses/${id}/`, payload)
export const deleteBusiness = (id) => api.delete(`/businesses/${id}/`)

// ── Reviews ───────────────────────────────────────────────────────────────────
export const getReviews = (params) => api.get('/reviews/', { params })
export const createReview = (payload) => api.post('/reviews/', payload)
export const updateReview = (id, payload) => api.patch(`/reviews/${id}/`, payload)
export const deleteReview = (id) => api.delete(`/reviews/${id}/`)

// ── Bookmarks ─────────────────────────────────────────────────────────────────
export const getBookmarks = (params) => api.get('/bookmarks/', { params })
export const createBookmark = (payload) => api.post('/bookmarks/', payload)
export const deleteBookmark = (id) => api.delete(`/bookmarks/${id}/`)

// ── Rewards ───────────────────────────────────────────────────────────────────
export const getRewards = (params) => api.get('/rewards/', { params })
export const createReward = (payload) => api.post('/rewards/', payload)
export const updateReward = (id, payload) => api.patch(`/rewards/${id}/`, payload)
export const deleteReward = (id) => api.delete(`/rewards/${id}/`)

// ── Coupons ───────────────────────────────────────────────────────────────────
export const getCoupons = (params) => api.get('/coupons/', { params })
export const createCoupon = (payload) => api.post('/coupons/', payload)
export const updateCoupon = (id, payload) => api.patch(`/coupons/${id}/`, payload)
export const deleteCoupon = (id) => api.delete(`/coupons/${id}/`)

// ── Automation Logs ───────────────────────────────────────────────────────────
export const getAutomationLogs = (params) => api.get('/automation-logs/', { params })
export const createAutomationLog = (payload) => api.post('/automation-logs/', payload)

export default api
