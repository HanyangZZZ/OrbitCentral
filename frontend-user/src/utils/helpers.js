/**
 * helpers.js — Shared Utility Functions
 * =======================================
 * PURPOSE:
 *   Reusable helper functions used across multiple components and pages.
 *   Instead of each file defining its own truncate(), formatDate(), etc.,
 *   they all import from this single file.
 *
 * MODULAR LOGIC:
 *   Follows DRY (Don't Repeat Yourself). These small, pure functions have
 *   no side effects — they take input and return output, nothing else.
 *   That makes them easy to test and safe to use anywhere.
 */

/**
 * Truncate a string to a max length, adding an ellipsis if needed.
 * Used by BookmarksPage, BusinessCard, and anywhere text needs clipping.
 *
 * @param {string} str  — The string to truncate
 * @param {number} max  — Maximum character length
 * @returns {string}    — The original or shortened string
 */
export function truncate(str, max) {
  if (!str || str.length <= max) return str
  return str.slice(0, max).trimEnd() + '…'
}

/**
 * Format an ISO date string into a human-readable short date.
 * Example: "2025-02-14T..." → "Feb 14, 2025"
 *
 * @param {string} isoStr — ISO 8601 date string
 * @returns {string}      — Formatted date or empty string
 */
export function formatDate(isoStr) {
  if (!isoStr) return ''
  return new Date(isoStr).toLocaleDateString('en-US', {
    month: 'short',
    day: 'numeric',
    year: 'numeric',
  })
}

/**
 * Capitalize the first letter of a string and replace underscores with spaces.
 * Useful for displaying API field names in user-friendly format.
 *
 * @param {string} s — The string to capitalize
 * @returns {string}
 */
export function capitalize(s) {
  return s.charAt(0).toUpperCase() + s.slice(1).replace(/_/g, ' ')
}

/**
 * Format a file size in bytes to a human-readable string.
 * Example: 1536 → "1.5 KB"
 *
 * @param {number} bytes — Size in bytes
 * @returns {string}     — Formatted size string
 */
export function formatSize(bytes) {
  if (!bytes) return '—'
  if (bytes < 1024) return `${bytes} B`
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`
}

/**
 * Get today's opening hours string from a business object.
 * Parses the weekdayDescriptions array and returns just the hours portion.
 *
 * @param {object} biz — Business object with opening_hours.weekdayDescriptions
 * @returns {string|null} — Today's hours or null
 */
export function todayHours(biz) {
  const descs = biz?.opening_hours?.weekdayDescriptions
  if (!descs?.length) return null
  const dayIndex = new Date().getDay()
  // weekdayDescriptions is Mon–Sun (index 0 = Mon). JS getDay(): 0 = Sun
  const idx = dayIndex === 0 ? 6 : dayIndex - 1
  const line = descs[idx]
  if (!line) return null
  // "Monday: 7:00 AM – 6:00 PM" → "7:00 AM – 6:00 PM"
  const parts = line.split(': ')
  return parts.length > 1 ? parts.slice(1).join(': ') : line
}

/**
 * Build a list of available service labels from a business's boolean flags.
 * Example: { dine_in: true, takeout: true } → ['Dine-in', 'Takeout']
 *
 * @param {object} biz — Business object
 * @returns {string[]}  — Up to 5 service labels
 */
export function serviceList(biz) {
  const list = []
  if (biz.dine_in) list.push('Dine-in')
  if (biz.takeout) list.push('Takeout')
  if (biz.delivery) list.push('Delivery')
  if (biz.outdoor_seating) list.push('Outdoor')
  if (biz.serves_brunch) list.push('Brunch')
  if (biz.serves_breakfast) list.push('Breakfast')
  if (biz.serves_lunch) list.push('Lunch')
  if (biz.serves_dinner) list.push('Dinner')
  return list.slice(0, 5)
}

/**
 * Escape HTML special characters to prevent XSS when rendering user content.
 *
 * @param {string} str — Raw string
 * @returns {string}   — Escaped string safe for v-html
 */
export function escapeHtml(str) {
  return str
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
}
