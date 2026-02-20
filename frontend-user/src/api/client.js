/**
 * client.js — API Barrel Re-Export (Single Import Point)
 * =======================================================
 * PURPOSE:
 *   This is the "front door" for the entire API layer. Instead of
 *   importing from 7 different files, components just do:
 *     import { login, searchBusinesses, toggleBookmark } from '@/api/client'
 *
 * MODULAR LOGIC:
 *   This pattern is called a "barrel export." It re-exports everything
 *   from each domain module so consumers don't need to know which
 *   file a function lives in. If you add a new API module, just add
 *   another `export * from './newModule'` line here.
 *
 * DOMAIN MODULES:
 *   core.js       → Axios instance, token management, pagination
 *   auth.js       → Login, register, profile, password reset
 *   businesses.js → Business CRUD, search, photos, geocoding
 *   reviews.js    → Review CRUD & voting (useful/funny/cool)
 *   bookmarks.js  → Favorites system (save, unsave, check)
 *   taxonomy.js   → Categories & tags
 *   aiReviews.js  → AI-powered review chat system
 */
export { default as api }                           from './core'
export { setAuthToken, getSavedToken, getNextPage } from './core'
export * from './auth'
export * from './businesses'
export * from './reviews'
export * from './bookmarks'
export * from './taxonomy'
export * from './aiReviews'

