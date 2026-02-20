/**
 * businessDetail.js — Business Detail Page Config
 * ==================================================
 * PURPOSE:
 *   Static template data for the business detail modals (Activities,
 *   Coupons) and review voting icons. This is placeholder/demo data
 *   that will eventually come from the backend API.
 *
 * MODULAR LOGIC:
 *   Keeps template data separate from component logic. When real
 *   activities/coupons come from the API, you just swap the data
 *   source — the components don't need to change.
 *
 * NOTE:
 *   VOTE_ICONS are also available from config/icons.js. This file
 *   keeps them for backward compatibility with existing imports.
 */

// ── Template Activities (demo data for ActivitiesModal) ──────────────────
export const TEMPLATE_ACTIVITIES = [
  { icon: 'music', title: 'Live Music Night', desc: 'Local artists perform live at the venue.' },
  { icon: 'palette', title: 'Art Workshop', desc: 'Hands-on creative workshops for all ages.' },
  { icon: 'chef', title: 'Cooking Class', desc: 'Learn recipes from the chef.' },
  { icon: 'wellness', title: 'Wellness Session', desc: 'Yoga, meditation, or fitness events.' },
  { icon: 'mic', title: 'Open Mic / Karaoke', desc: 'Show off your talent on stage.' },
  { icon: 'game', title: 'Game Night', desc: 'Board games, trivia, and more.' },
  { icon: 'camera', title: 'Photo Walk', desc: 'Explore and photograph the neighbourhood.' },
  { icon: 'people', title: 'Networking Mixer', desc: 'Meet local entrepreneurs and creatives.' },
]

// ── Template Coupons (demo data for CouponsModal) ────────────────────────
export const TEMPLATE_COUPONS = [
  { value: '15% OFF', title: 'Weekend Special', desc: 'Valid on Saturdays & Sundays.' },
  { value: '$5 OFF', title: 'Lunch Deal', desc: 'Orders over $25 between 11am–2pm.' },
  { value: 'BOGO', title: 'Bring a Friend', desc: 'Buy one, get one free on select items.' },
  { value: '20% OFF', title: 'Happy Hour', desc: 'Drinks & appetizers, 4pm–6pm weekdays.' },
]

// ── Vote Icons (useful / funny / cool buttons on reviews) ────────────────
export const VOTE_ICONS = {
  useful: '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M14 9V5a3 3 0 0 0-3-3l-4 9v11h11.28a2 2 0 0 0 2-1.7l1.38-9a2 2 0 0 0-2-2.3H14z"/><path d="M7 22H4a2 2 0 0 1-2-2v-7a2 2 0 0 1 2-2h3"/></svg>',
  funny: '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><path d="M8 14s1.5 2 4 2 4-2 4-2"/><line x1="9" y1="9" x2="9.01" y2="9"/><line x1="15" y1="9" x2="15.01" y2="9"/></svg>',
  cool: '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><path d="M8 14s1.5 2 4 2 4-2 4-2"/><path d="M6 10h4"/><path d="M14 10h4"/></svg>'
}
