/**
 * taxonomy.js — Category & Tag Endpoints
 * =========================================
 * PURPOSE:
 *   Manages the classification system — categories (Food & Drink,
 *   Retail, etc.) and tags (cozy, family-friendly, etc.).
 *
 * MODULAR LOGIC:
 *   Categories are hierarchical (parent → children). Tags are flat
 *   labels that users attach to businesses. The sidebar and filter
 *   bar both pull from these endpoints.
 */
import api from './core'

// ── Categories (hierarchical groups like "Food & Drink") ─────────────────
export const getCategories  = (params)       => api.get('/categories/', { params })
export const createCategory = (payload)      => api.post('/categories/', payload)
export const updateCategory = (id, payload)  => api.patch(`/categories/${id}/`, payload)
export const deleteCategory = (id)           => api.delete(`/categories/${id}/`)

// ── Tags (flat labels like "cozy" or "pet-friendly") ─────────────────────
export const getTags    = (params) => api.get('/tags/', { params })
export const getTag     = (id)     => api.get(`/tags/${id}/`)
export const searchTags = (params) => api.get('/tags/search/', { params })
