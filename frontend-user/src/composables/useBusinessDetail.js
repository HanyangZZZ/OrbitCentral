/**
 * useBusinessDetail.js — Business Detail Data & State Manager
 * =============================================================
 * PURPOSE:
 *   Everything the BusinessDetailPage needs: fetching business data,
 *   reviews, bookmark state, and providing computed properties for
 *   highlights, short descriptions, and merged review lists.
 *
 * MODULAR LOGIC:
 *   This is the largest composable because the detail page has the
 *   most features. It's organized into clear sections:
 *   1. State refs (business, reviews, loading flags)
 *   2. Computed properties (highlights, customersSay, allReviews)
 *   3. API methods (fetch, sort, vote, bookmark, submit)
 *
 *   Highlights use icons from config/icons.js to show features
 *   like WiFi, parking, outdoor seating as visual cards.
 *
 * OOP FLOW:
 *   BusinessDetailPage mounts → calls fetchBusiness() + fetchReviews() →
 *   this composable fetches data → computed properties derive UI data →
 *   page template reads highlights, allReviews, customersSay, etc.
 *
 * API ENDPOINTS USED:
 *   GET  /api/businesses/{id}/           → full business object
 *   GET  /api/reviews/?business={id}     → paginated user reviews
 *   GET  /api/bookmarks/check/?business  → is this bookmarked?
 *   POST /api/bookmarks/toggle/          → add/remove bookmark
 *   POST /api/reviews/                   → submit a new review
 *   POST /api/reviews/{id}/vote/         → vote on a review
 */
import { ref, computed } from 'vue'
import {
  getBusiness,
  getBusinessPhotoUrl,
  getReviews,
  createReview,
  deleteReview,
  voteReview,
  checkBookmark,
  toggleBookmark,
  getNextPage,
  getSavedToken,
} from '@/api/client'

export function useBusinessDetail(businessId) {
  // ── Core state ─────────────────────────────────────────────────────────
  const business     = ref(null)
  const loading      = ref(true)
  const error        = ref('')

  // ── Reviews ────────────────────────────────────────────────────────────
  const userReviews      = ref([])   // from /api/reviews/
  const reviewsNext      = ref(null)
  const reviewsLoading   = ref(false)
  const reviewSort       = ref('-created_at')

  // ── Bookmark ───────────────────────────────────────────────────────────
  const bookmarked = ref(false)

  // ── Photo URLs ─────────────────────────────────────────────────────────
  /** Banner: first photo at high res. */
  const bannerUrl = computed(() => {
    if (!business.value) return null
    if (business.value.image_url) return business.value.image_url
    if (business.value.photo_references?.length) {
      return getBusinessPhotoUrl(business.value.id, { idx: 0, maxHeight: 800 })
    }
    return null
  })

  /** Gallery URLs for all available photos. */
  const photoUrls = computed(() => {
    if (!business.value?.photo_references?.length) return []
    return business.value.photo_references.map((_, i) =>
      getBusinessPhotoUrl(business.value.id, { idx: i, maxHeight: 600 })
    )
  })

  // ── SVG icon helpers for highlights ─────────────────────────────────────
  const svgIcon = (d) => `<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">${d}</svg>`

  const HIGHLIGHT_ICONS = {
    dineIn:     svgIcon('<path d="M3 2v7c0 1.1.9 2 2 2h4a2 2 0 0 0 2-2V2"/><path d="M7 2v20"/><path d="M21 15V2v0a5 5 0 0 0-5 5v6c0 1.1.9 2 2 2h3Zm0 0v7"/>'),
    takeout:    svgIcon('<path d="M16 6h3a1 1 0 0 1 1 1v11a2 2 0 0 1-4 0V6ZM4 6h3a1 1 0 0 1 1 1v11a2 2 0 0 1-4 0V6Z"/><path d="M7 6V4a2 2 0 0 1 2-2h6a2 2 0 0 1 2 2v2"/>'),
    delivery:   svgIcon('<rect x="1" y="3" width="15" height="13" rx="2"/><path d="M16 8h4l3 3v5h-7V8Z"/><circle cx="5.5" cy="18.5" r="2.5"/><circle cx="18.5" cy="18.5" r="2.5"/>'),
    calendar:   svgIcon('<rect x="3" y="4" width="18" height="18" rx="2"/><line x1="16" y1="2" x2="16" y2="6"/><line x1="8" y1="2" x2="8" y2="6"/><line x1="3" y1="10" x2="21" y2="10"/>'),
    sunrise:    svgIcon('<path d="M17 18a5 5 0 0 0-10 0"/><line x1="12" y1="9" x2="12" y2="2"/><line x1="4.22" y1="10.22" x2="5.64" y2="11.64"/><line x1="1" y1="18" x2="3" y2="18"/><line x1="21" y1="18" x2="23" y2="18"/><line x1="18.36" y1="11.64" x2="19.78" y2="10.22"/><line x1="23" y1="22" x2="1" y2="22"/>'),
    brunch:     svgIcon('<circle cx="12" cy="12" r="10"/><path d="M8 12h8"/><path d="M12 8v8"/>'),
    salad:      svgIcon('<path d="M7 21h10"/><path d="M12 21a9 9 0 0 0 9-9H3a9 9 0 0 0 9 9Z"/><path d="M12 3c-1.5 0-3.3.9-3.3 3h6.6c0-2.1-1.8-3-3.3-3Z"/>'),
    dinner:     svgIcon('<path d="M12 2a10 10 0 1 0 10 10"/><path d="M12 6v6l4 2"/>'),
    beer:       svgIcon('<path d="M17 11h1a3 3 0 0 1 0 6h-1"/><path d="M9 12v6"/><path d="M13 12v6"/><path d="M14 7.5c-1 0-1.44.5-3 .5s-2-.5-3-.5-1.72.5-2.5.5a2.5 2.5 0 0 1 0-5c.78 0 1.57.5 2.5.5S9.44 3 11 3s2 .5 3 .5 1.72-.5 2.5-.5a2.5 2.5 0 0 1 0 5c-.78 0-1.5-.5-2.5-.5Z"/><path d="M5 8v12a2 2 0 0 0 2 2h8a2 2 0 0 0 2-2V8"/>'),
    wine:       svgIcon('<path d="M8 22h8"/><path d="M7 10h10"/><path d="M12 15v7"/><path d="M12 15a5 5 0 0 0 5-5c0-2-.5-4-2-8H9c-1.5 4-2 6-2 8a5 5 0 0 0 5 5Z"/>'),
    sun:        svgIcon('<circle cx="12" cy="12" r="5"/><line x1="12" y1="1" x2="12" y2="3"/><line x1="12" y1="21" x2="12" y2="23"/><line x1="4.22" y1="4.22" x2="5.64" y2="5.64"/><line x1="18.36" y1="18.36" x2="19.78" y2="19.78"/><line x1="1" y1="12" x2="3" y2="12"/><line x1="21" y1="12" x2="23" y2="12"/><line x1="4.22" y1="19.78" x2="5.64" y2="18.36"/><line x1="18.36" y1="5.64" x2="19.78" y2="4.22"/>'),
    music:      svgIcon('<path d="M9 18V5l12-2v13"/><circle cx="6" cy="18" r="3"/><circle cx="18" cy="16" r="3"/>'),
    child:      svgIcon('<path d="M9 12h.01"/><path d="M15 12h.01"/><path d="M10 16c.5.3 1.2.5 2 .5s1.5-.2 2-.5"/><path d="M19.5 8c-1.5-1-3.5-1.5-5.5-1.5S10 7 8.5 8"/><circle cx="12" cy="12" r="10"/>'),
    group:      svgIcon('<path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M23 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/>'),
    dog:        svgIcon('<path d="M10 5.172C10 3.782 8.884 2.64 7.556 2.968l-2.225.556A2 2 0 0 0 4 5.476v.1c0 1.267.87 2.424 2.022 2.424H8"/><path d="M14 5.172C14 3.782 15.116 2.64 16.444 2.968l2.225.556A2 2 0 0 1 20 5.476v.1c0 1.267-.87 2.424-2.022 2.424H16"/><path d="M3 14h18v3a4 4 0 0 1-4 4H7a4 4 0 0 1-4-4v-3Z"/><path d="M8 8h8v6H8Z"/>'),
    restroom:   svgIcon('<path d="M16 21v-6a2 2 0 0 0-2-2h-4a2 2 0 0 0-2 2v6"/><circle cx="12" cy="7" r="3"/>'),
    accessible: svgIcon('<circle cx="12" cy="12" r="10"/><path d="M9.5 9.5 12 12l2.5-2.5"/><path d="M12 12v5"/><path d="M8 17h8"/>'),
    parking:    svgIcon('<rect x="3" y="3" width="18" height="18" rx="2"/><path d="M9 17V7h4a3 3 0 0 1 0 6H9"/>'),
    car:        svgIcon('<rect x="1" y="3" width="15" height="13" rx="2"/><path d="M16 8h4l3 3v5h-7V8Z"/><circle cx="5.5" cy="18.5" r="2.5"/><circle cx="18.5" cy="18.5" r="2.5"/>'),
    phone:      svgIcon('<rect x="5" y="2" width="14" height="20" rx="2"/><line x1="12" y1="18" x2="12.01" y2="18"/>'),
  }

  // ── Highlights (boolean feature flags → human-readable cards) ──────────
  const highlights = computed(() => {
    if (!business.value) return []
    const b = business.value
    const items = []

    // Service options
    if (b.dine_in)           items.push({ icon: HIGHLIGHT_ICONS.dineIn,   title: 'Dine-in',          desc: 'Sit-down dining available' })
    if (b.takeout)           items.push({ icon: HIGHLIGHT_ICONS.takeout,  title: 'Takeout',          desc: 'Order for pickup' })
    if (b.delivery)          items.push({ icon: HIGHLIGHT_ICONS.delivery, title: 'Delivery',         desc: 'Get it delivered' })
    if (b.reservable)        items.push({ icon: HIGHLIGHT_ICONS.calendar, title: 'Reservable',       desc: 'Accepts reservations' })

    // Food & drink
    if (b.serves_breakfast)  items.push({ icon: HIGHLIGHT_ICONS.sunrise,  title: 'Breakfast',        desc: 'Serves breakfast' })
    if (b.serves_brunch)     items.push({ icon: HIGHLIGHT_ICONS.brunch,   title: 'Brunch',           desc: 'Serves brunch' })
    if (b.serves_lunch)      items.push({ icon: HIGHLIGHT_ICONS.salad,    title: 'Lunch',            desc: 'Serves lunch' })
    if (b.serves_dinner)     items.push({ icon: HIGHLIGHT_ICONS.dinner,   title: 'Dinner',           desc: 'Serves dinner' })
    if (b.serves_beer)       items.push({ icon: HIGHLIGHT_ICONS.beer,     title: 'Beer',             desc: 'Beer available' })
    if (b.serves_wine)       items.push({ icon: HIGHLIGHT_ICONS.wine,     title: 'Wine',             desc: 'Wine available' })

    // Atmosphere
    if (b.outdoor_seating)   items.push({ icon: HIGHLIGHT_ICONS.sun,      title: 'Outdoor Seating',  desc: 'Patio or terrace' })
    if (b.live_music)        items.push({ icon: HIGHLIGHT_ICONS.music,    title: 'Live Music',       desc: 'Live performances' })
    if (b.good_for_children) items.push({ icon: HIGHLIGHT_ICONS.child,    title: 'Kid-Friendly',     desc: 'Good for children' })
    if (b.good_for_groups)   items.push({ icon: HIGHLIGHT_ICONS.group,    title: 'Group-Friendly',   desc: 'Great for groups' })
    if (b.allows_dogs)       items.push({ icon: HIGHLIGHT_ICONS.dog,      title: 'Dog-Friendly',     desc: 'Dogs allowed' })
    if (b.restroom)          items.push({ icon: HIGHLIGHT_ICONS.restroom, title: 'Restroom',         desc: 'Restroom on-site' })

    // Accessibility
    const acc = b.accessibility || {}
    if (acc.wheelchairAccessibleEntrance) items.push({ icon: HIGHLIGHT_ICONS.accessible, title: 'Accessible Entrance', desc: 'Wheelchair accessible' })
    if (acc.wheelchairAccessibleParking)  items.push({ icon: HIGHLIGHT_ICONS.parking,    title: 'Accessible Parking',  desc: 'Wheelchair parking' })

    // Parking
    const park = b.parking || {}
    if (park.freeParkingLot)    items.push({ icon: HIGHLIGHT_ICONS.parking, title: 'Free Parking',   desc: 'Free parking lot' })
    if (park.freeStreetParking) items.push({ icon: HIGHLIGHT_ICONS.car,     title: 'Street Parking', desc: 'Free street parking' })

    // Payment
    const pay = b.payment_options || {}
    if (pay.acceptsNfc)         items.push({ icon: HIGHLIGHT_ICONS.phone,   title: 'Tap to Pay',     desc: 'NFC / contactless' })

    return items
  })

  // ── "Customers Say" (synthesized from Google reviews_data) ─────────────
  const customersSay = computed(() => {
    const reviews = business.value?.reviews_data
    if (!reviews?.length) return ''

    const tagNames = (business.value.tags || []).map(t => t.name.toLowerCase())
    const totalRating = reviews.reduce((s, r) => s + (r.rating || 0), 0)
    const avg = (totalRating / reviews.length).toFixed(1)

    // Find the most frequently mentioned keywords
    const wordFreq = {}
    reviews.forEach(r => {
      if (!r.text) return
      const words = r.text.toLowerCase().split(/\W+/).filter(w => w.length > 3)
      const seen = new Set()
      words.forEach(w => {
        if (!seen.has(w)) { wordFreq[w] = (wordFreq[w] || 0) + 1; seen.add(w) }
      })
    })
    const topWords = Object.entries(wordFreq)
      .filter(([w]) => !['this', 'that', 'with', 'have', 'from', 'they', 'were', 'been', 'very', 'their', 'also', 'would', 'will', 'about'].includes(w))
      .sort((a, b) => b[1] - a[1])
      .slice(0, 5)
      .map(([w]) => w)

    const parts = [`Based on ${reviews.length} Google reviews (avg ${avg}/5)`]

    if (topWords.length) {
      parts.push(`customers frequently mention "${topWords.slice(0, 3).join('", "')}"`)
    }

    const highRated = reviews.filter(r => r.rating >= 4).length
    const pct = Math.round((highRated / reviews.length) * 100)
    if (pct >= 70) parts.push(`${pct}% of reviewers rate it 4/5 or above`)

    return parts.join('. ') + '.'
  })

  // ── Short description (from API or synthesized) ────────────────────────
  const shortDescription = computed(() => {
    if (!business.value) return ''

    // Use the API description if available
    if (business.value.description) return business.value.description

    // Otherwise synthesize from category, tags, and features
    const b = business.value
    const catName = b.category_detail?.name || ''
    const parentCat = b.category_detail?.parent_name || ''
    const tags = (b.tags || []).slice(0, 4).map(t => t.name.replace(/-/g, ' '))

    const parts = []

    // Category-based intro
    if (catName && parentCat) {
      parts.push(`${b.name} is a ${catName.toLowerCase()} spot in the ${parentCat.toLowerCase()} category`)
    } else if (catName) {
      parts.push(`${b.name} is a local ${catName.toLowerCase()} business`)
    }

    // Location
    if (b.address) {
      const shortAddr = b.address.split(',').slice(0, 2).join(',')
      parts.push(`located at ${shortAddr}`)
    }

    // Rating context
    const rating = Number(b.avg_rating || b.google_rating || 0)
    const reviewCount = b.user_rating_count || 0
    if (rating > 0 && reviewCount > 0) {
      parts.push(`with a ${rating.toFixed(1)}/5 rating from ${reviewCount} reviews`)
    }

    let desc = parts.join(', ')
    if (desc) desc += '.'

    // Tags as vibes
    if (tags.length) {
      desc += ` Known for: ${tags.join(', ')}.`
    }

    return desc
  })

  // ── All reviews combined (Google + user) ───────────────────────────────
  const allReviews = computed(() => {
    const google = (business.value?.reviews_data || []).map(r => ({
      id: `g-${r.author}-${r.time}`,
      source: 'google',
      author: r.author || 'Google User',
      rating: r.rating,
      text: r.text,
      date: r.time ? new Date(r.time) : null,
      imageUrl: null,
      voteCounts: null,
      userVotes: [],
    }))

    const user = userReviews.value.map(r => ({
      id: r.id,
      source: 'user',
      userId: r.user,
      author: r.username || 'User',
      rating: r.rating,
      text: r.description,
      date: r.created_at ? new Date(r.created_at) : null,
      imageUrl: r.image_url,
      voteCounts: r.vote_counts,
      userVotes: r.user_votes || [],
    }))

    // Combine all reviews
    const combined = [...user, ...google]

    // Sort based on reviewSort value
    const sortKey = reviewSort.value
    if (sortKey === '-created_at') {
      // Newest first
      combined.sort((a, b) => (b.date || 0) - (a.date || 0))
    } else if (sortKey === 'created_at') {
      // Oldest first
      combined.sort((a, b) => (a.date || 0) - (b.date || 0))
    } else if (sortKey === '-rating') {
      // Highest rated first
      combined.sort((a, b) => (b.rating || 0) - (a.rating || 0))
    } else if (sortKey === 'rating') {
      // Lowest rated first
      combined.sort((a, b) => (a.rating || 0) - (b.rating || 0))
    }

    return combined
  })

  const totalReviewCount = computed(() => {
    const googleCount = business.value?.reviews_data?.length || 0
    return googleCount + userReviews.value.length
  })

  // ── Fetch business ─────────────────────────────────────────────────────
  async function fetchBusiness() {
    loading.value = true
    error.value = ''
    try {
      const { data } = await getBusiness(businessId)
      business.value = data
    } catch (err) {
      error.value = err.response?.data?.detail || err.message || 'Failed to load business'
    } finally {
      loading.value = false
    }
  }

  // ── Fetch user reviews ─────────────────────────────────────────────────
  async function fetchReviews() {
    reviewsLoading.value = true
    try {
      const { data } = await getReviews({
        business: businessId,
        ordering: reviewSort.value,
        page_size: 30,
      })
      userReviews.value = data.results ?? []
      reviewsNext.value = data.next ?? null
    } catch {
      /* non-critical */
    } finally {
      reviewsLoading.value = false
    }
  }

  async function loadMoreReviews() {
    if (!reviewsNext.value) return
    try {
      const { data } = await getNextPage(reviewsNext.value)
      userReviews.value.push(...(data.results ?? []))
      reviewsNext.value = data.next ?? null
    } catch { /* ignore */ }
  }

  async function changeReviewSort(sort) {
    reviewSort.value = sort
    await fetchReviews()
  }

  // ── Bookmark ───────────────────────────────────────────────────────────
  async function fetchBookmarkState() {
    if (!getSavedToken()) return
    try {
      const { data } = await checkBookmark(businessId)
      bookmarked.value = data.bookmarked
    } catch { /* not logged in or unverified */ }
  }

  async function onToggleBookmark() {
    // Check if user is logged in first
    if (!getSavedToken()) {
      alert('Please log in to bookmark businesses')
      return
    }
    
    bookmarked.value = !bookmarked.value // optimistic
    try {
      await toggleBookmark(businessId)
    } catch (err) {
      bookmarked.value = !bookmarked.value // revert
      // Show error message
      const msg = err.response?.data?.detail || 'Failed to bookmark. Please verify your email.'
      alert(msg)
    }
  }

  // ── Submit review ──────────────────────────────────────────────────────
  async function submitReview(payload) {
    await createReview({ business: businessId, ...payload })
    await fetchReviews()           // refresh list
    await fetchBusiness()          // refresh avg_rating
  }

  // ── Delete review ──────────────────────────────────────────────────────
  async function onDeleteReview(reviewId) {
    try {
      await deleteReview(reviewId)
      await fetchReviews()    // refresh list
      await fetchBusiness()   // refresh avg_rating
    } catch { /* needs auth / not owner */ }
  }

  // ── Vote on review ─────────────────────────────────────────────────────
  async function onVoteReview(reviewId, voteType) {
    try {
      await voteReview(reviewId, voteType)
      await fetchReviews() // refresh vote counts
    } catch { /* needs auth */ }
  }

  return {
    business, loading, error,
    bannerUrl, photoUrls, highlights, customersSay, shortDescription,
    allReviews, totalReviewCount,
    userReviews, reviewsNext, reviewsLoading, reviewSort,
    bookmarked,
    fetchBusiness, fetchReviews, loadMoreReviews, changeReviewSort,
    fetchBookmarkState, onToggleBookmark,
    submitReview, onDeleteReview, onVoteReview,
  }
}
