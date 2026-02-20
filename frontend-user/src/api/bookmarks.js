/**
 * bookmarks.js — Bookmark CRUD, Toggle & Check
 * ================================================
 * PURPOSE:
 *   Handles saving/removing businesses to the user's favorites list.
 *   The toggle endpoint is smart — it adds or removes automatically.
 *
 * MODULAR LOGIC:
 *   Used by useBusinessDetail (for the bookmark heart on detail pages)
 *   and BookmarksPage (for listing all saved businesses).
 */
import api from './core'

// ── CRUD operations ──────────────────────────────────────────────────────
export const getBookmarks   = (params)      => api.get('/bookmarks/', { params })
export const createBookmark = (payload)     => api.post('/bookmarks/', payload)
export const updateBookmark = (id, payload) => api.patch(`/bookmarks/${id}/`, payload)
export const deleteBookmark = (id)          => api.delete(`/bookmarks/${id}/`)

// ── Smart toggle (add if not bookmarked, remove if already saved) ────────
export const toggleBookmark = (businessId)  => api.post('/bookmarks/toggle/', { business: businessId })

// ── Quick checks (used to show filled/empty heart icon) ──────────────────
export const checkBookmark  = (businessId)  => api.get('/bookmarks/check/', { params: { business: businessId } })
export const getBookmarkIds = ()            => api.get('/bookmarks/ids/')
