/**
 * homepage.js — Homepage Configuration & Static Data
 * =====================================================
 * PURPOSE:
 *   Central config for the homepage components (HeroSearch, CategoryGrid,
 *   NearbyForYou). All category images, icons, time-based greeting logic,
 *   and preference keywords live here instead of being scattered around.
 *
 * MODULAR LOGIC:
 *   Separating config from components is a core principle. Components
 *   handle rendering, config handles data. If a category image URL
 *   changes, you edit this file — never touch the component code.
 *
 * OOP FLOW:
 *   This file exports pure data (objects/arrays) and pure helper
 *   functions. No side effects, no reactive state. Components
 *   import what they need at setup time.
 */

// ── Category Images ──────────────────────────────────────────────────────
// Maps category slugs/names to photo URLs (local or Unsplash).
// Used by CategoryGrid to show a background image per category card.
export const CATEGORY_IMAGES = {
  restaurants: '/icons/food-drink.png',
  'food-drink': '/icons/food-drink.png',
  food: '/icons/food-drink.png',
  retail: '/icons/retail.webp',
  shopping: '/icons/retail.webp',
  'cafes-coffee': 'https://images.unsplash.com/photo-1501339847302-ac426a4a7cbb?w=600&q=80',
  health: 'https://images.unsplash.com/photo-1576091160399-112ba8d25d1f?w=600&q=80',
  fitness: 'https://images.unsplash.com/photo-1534438327276-14e5300c3a48?w=600&q=80',
  beauty: 'https://images.unsplash.com/photo-1560066984-138dadb4c035?w=600&q=80',
  entertainment: '/icons/entertainment.jpeg',
  services: '/icons/personal-services.jpg',
  'personal-services': '/icons/personal-services.jpg',
  education: 'https://images.unsplash.com/photo-1497633762265-9d179a990aa6?w=600&q=80',
  nightlife: 'https://images.unsplash.com/photo-1566417713940-fe7c737a9ef2?w=600&q=80',
  grocery: 'https://images.unsplash.com/photo-1542838132-92c53300491e?w=600&q=80',
  automotive: 'https://images.unsplash.com/photo-1486006920555-c77dcf18193c?w=600&q=80',
  pets: 'https://images.unsplash.com/photo-1601758228041-f3b2795255f1?w=600&q=80',
  home: '/icons/home-services.webp',
  'home-services': '/icons/home-services.webp',
  default: 'https://images.unsplash.com/photo-1486406146926-c627a92ad1ab?w=600&q=80'
}

// ── Category Icons (SVG) ─────────────────────────────────────────────────
// Maps icon names to inline SVG strings for the CategoryGrid component.
// The API returns icon_name values like "restaurant", "storefront", etc.
// This provides visual icons when images aren't available.
export const CATEGORY_ICONS = {
  // API icon_name values (exact matches)
  restaurant: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M3 2v7c0 1.1.9 2 2 2h4a2 2 0 0 0 2-2V2"/><path d="M7 2v20"/><path d="M21 15V2a5 5 0 0 0-5 5v6c0 1.1.9 2 2 2h3zm0 0v7"/></svg>',
  theater_comedy: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><rect x="2" y="4" width="20" height="16" rx="2"/><path d="M2 8h20"/><path d="M8 4v4"/><path d="M16 4v4"/><polygon points="10,11 10,18 16,14.5"/></svg>',
  storefront: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M6 2L3 6v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2V6l-3-4z"/><path d="M3 6h18"/><path d="M16 10a4 4 0 0 1-8 0"/></svg>',
  favorite: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><circle cx="12" cy="12" r="3"/><path d="M12 1v4"/><path d="M12 19v4"/><path d="M4.22 4.22l2.83 2.83"/><path d="M16.95 16.95l2.83 2.83"/><path d="M1 12h4"/><path d="M19 12h4"/><path d="M4.22 19.78l2.83-2.83"/><path d="M16.95 7.05l2.83-2.83"/></svg>',
  home_repair_service: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/><path d="M9 22V12h6v10"/></svg>',
  // Slug/name fallbacks
  coffee: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M17 8h1a4 4 0 1 1 0 8h-1"/><path d="M3 8h14v9a4 4 0 0 1-4 4H7a4 4 0 0 1-4-4V8z"/><path d="M6 2v3"/><path d="M10 2v3"/><path d="M14 2v3"/></svg>',
  shopping: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M6 2L3 6v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2V6l-3-4z"/><path d="M3 6h18"/><path d="M16 10a4 4 0 0 1-8 0"/></svg>',
  retail: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M6 2L3 6v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2V6l-3-4z"/><path d="M3 6h18"/><path d="M16 10a4 4 0 0 1-8 0"/></svg>',
  health: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M22 12h-4l-3 9L9 3l-3 9H2"/></svg>',
  fitness: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M6.5 6.5a3.5 3.5 0 1 0 7 0 3.5 3.5 0 0 0-7 0z"/><path d="M2 21c0-3.9 3.1-7 7-7h2a7 7 0 0 1 7 7"/></svg>',
  beauty: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M12 2a7 7 0 0 0-7 7c0 3.9 3.1 7 7 7s7-3.1 7-7a7 7 0 0 0-7-7z"/><path d="M12 16v6"/><path d="M9 22h6"/></svg>',
  entertainment: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><rect x="2" y="4" width="20" height="16" rx="2"/><path d="M2 8h20"/><path d="M8 4v4"/><path d="M16 4v4"/><polygon points="10,11 10,18 16,14.5"/></svg>',
  services: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><circle cx="12" cy="12" r="3"/><path d="M12 1v4"/><path d="M12 19v4"/><path d="M4.22 4.22l2.83 2.83"/><path d="M16.95 16.95l2.83 2.83"/><path d="M1 12h4"/><path d="M19 12h4"/><path d="M4.22 19.78l2.83-2.83"/><path d="M16.95 7.05l2.83-2.83"/></svg>',
  education: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M2 3h6a4 4 0 0 1 4 4v14a3 3 0 0 0-3-3H2z"/><path d="M22 3h-6a4 4 0 0 0-4 4v14a3 3 0 0 1 3-3h7z"/></svg>',
  nightlife: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/></svg>',
  bar: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M8 22h8"/><path d="M12 11v11"/><path d="M19 3l-7 8-7-8z"/></svg>',
  grocery: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><circle cx="9" cy="21" r="1"/><circle cx="20" cy="21" r="1"/><path d="M1 1h4l2.68 13.39a2 2 0 0 0 2 1.61h9.72a2 2 0 0 0 2-1.61L23 6H6"/></svg>',
  bakery: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M12 8a4 4 0 1 0 0-8 4 4 0 0 0 0 8z"/><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/></svg>',
  pizza: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M12 2L2 19h20L12 2z"/><circle cx="12" cy="12" r="1.5"/></svg>',
  automotive: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M5 17h14v-5H5v5z"/><path d="M5 12l2-5h10l2 5"/><circle cx="7.5" cy="17" r="1.5"/><circle cx="16.5" cy="17" r="1.5"/></svg>',
  pets: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><circle cx="11" cy="4" r="2"/><circle cx="4" cy="8" r="2"/><circle cx="18" cy="8" r="2"/><circle cx="6" cy="15" r="2"/><circle cx="16" cy="15" r="2"/></svg>',
  home: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/><path d="M9 22V12h6v10"/></svg>',
  default: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"/><circle cx="12" cy="10" r="3"/></svg>'
}

// ── Time-Based Contexts ──────────────────────────────────────────────────
// NearbyForYou uses these to tailor recommendations based on time of day.
// Morning → suggest coffee/breakfast. Evening → suggest restaurants/bars.
export const TIME_CONTEXTS = {
  morning: {
    period: 'morning',
    greeting: 'Good morning',
    queries: ['breakfast', 'coffee', 'brunch spot', 'bakery'],
    emoji: '☀️',
    hourRange: [5, 11]
  },
  lunch: {
    period: 'lunch',
    greeting: 'Good afternoon',
    queries: ['lunch', 'quick bite', 'healthy lunch', 'sandwich'],
    emoji: '🍽️',
    hourRange: [11, 14]
  },
  afternoon: {
    period: 'afternoon',
    greeting: 'Good afternoon',
    queries: ['coffee', 'dessert', 'cafe', 'tea'],
    emoji: '☕',
    hourRange: [14, 17]
  },
  evening: {
    period: 'evening',
    greeting: 'Good evening',
    queries: ['dinner', 'restaurant', 'fine dining', 'casual dinner'],
    emoji: '🌆',
    hourRange: [17, 21]
  },
  night: {
    period: 'night',
    greeting: 'Good evening',
    queries: ['bar', 'nightlife', 'late night food', 'lounge'],
    emoji: '🌙',
    hourRange: [21, 5]
  }
}

// ── Preference Keywords ──────────────────────────────────────────────────
// Used to extract food/business preferences from the user's bookmarked
// business names, which then feeds into the AI personalization.
export const PREFERENCE_KEYWORDS = [
  'coffee', 'cafe', 'restaurant', 'bar', 'pizza', 'sushi',
  'thai', 'chinese', 'italian', 'mexican', 'indian', 'korean', 'japanese',
  'bakery', 'dessert', 'brunch', 'breakfast', 'lunch', 'dinner', 'grill',
  'steakhouse', 'seafood', 'vegan', 'vegetarian', 'burger', 'taco', 'ramen',
  'pho', 'bbq', 'wings', 'pub', 'lounge', 'bistro', 'diner'
]

// ── Helper Functions ─────────────────────────────────────────────────────────

/**
 * Get emoji icon for a category icon_name
 */
export function getCategoryIcon(iconName) {
  if (!iconName) return CATEGORY_ICONS.default
  if (CATEGORY_ICONS[iconName]) return CATEGORY_ICONS[iconName]
  const key = Object.keys(CATEGORY_ICONS).find(k => iconName.toLowerCase().includes(k))
  return key ? CATEGORY_ICONS[key] : CATEGORY_ICONS.default
}

/**
 * Get image URL for a category
 */
export function getCategoryImage(category) {
  const slug = category.slug?.toLowerCase()
  const icon = category.icon_name?.toLowerCase()
  const name = category.name?.toLowerCase()

  if (slug && CATEGORY_IMAGES[slug]) return CATEGORY_IMAGES[slug]
  if (icon && CATEGORY_IMAGES[icon]) return CATEGORY_IMAGES[icon]

  // Try partial match on name
  const matchKey = Object.keys(CATEGORY_IMAGES).find(k =>
    name?.includes(k) || k.includes(name?.split(' ')[0] || '')
  )
  if (matchKey) return CATEGORY_IMAGES[matchKey]

  return CATEGORY_IMAGES.default
}

/**
 * Get time context based on current hour
 */
export function getTimeContext() {
  const hour = new Date().getHours()

  if (hour >= 5 && hour < 11) return TIME_CONTEXTS.morning
  if (hour >= 11 && hour < 14) return TIME_CONTEXTS.lunch
  if (hour >= 14 && hour < 17) return TIME_CONTEXTS.afternoon
  if (hour >= 17 && hour < 21) return TIME_CONTEXTS.evening
  return TIME_CONTEXTS.night
}

/**
 * Extract preference keywords from business names
 */
export function extractKeywordsFromNames(businessNames) {
  const keywords = []
  businessNames.forEach(name => {
    const lower = name.toLowerCase()
    PREFERENCE_KEYWORDS.forEach(kw => {
      if (lower.includes(kw)) keywords.push(kw)
    })
  })
  return [...new Set(keywords)] // unique
}
