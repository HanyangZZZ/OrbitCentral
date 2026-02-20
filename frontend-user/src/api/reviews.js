/**
 * reviews.js — Review CRUD & Voting Endpoints
 * ==============================================
 * PURPOSE:
 *   Manages all user review operations — creating, reading, updating,
 *   deleting reviews, and casting votes (useful/funny/cool).
 *
 * MODULAR LOGIC:
 *   Simple one-liner exports. Each function = one backend endpoint.
 *   useBusinessDetail composable imports these for the review system.
 */
import api from './core'

// ── CRUD operations ──────────────────────────────────────────────────────
export const getReviews   = (params)              => api.get('/reviews/', { params })
export const getReview    = (id)                  => api.get(`/reviews/${id}/`)
export const createReview = (payload)             => api.post('/reviews/', payload)
export const updateReview = (id, payload)         => api.patch(`/reviews/${id}/`, payload)
export const deleteReview = (id)                  => api.delete(`/reviews/${id}/`)

// ── Voting (useful / funny / cool) ──────────────────────────────────────
export const voteReview   = (reviewId, voteType)  => api.post(`/reviews/${reviewId}/vote/`, { vote_type: voteType })
