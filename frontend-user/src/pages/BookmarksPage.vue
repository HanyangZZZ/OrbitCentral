<!--
  BookmarksPage.vue — Favourites / Saved Businesses (route: /bookmarks)
  ─────────────────────────────────────────────────────────────────────────────
  Auth-required page showing the user's bookmarked businesses.

  DATA FLOW
  1. On mount, fetches bookmark IDs via getBookmarkIds().
  2. For each bookmark, fetches the full business data (hydration).
     This is needed because the bookmarks API only returns IDs.
  3. Renders each business in a card with: photo, name, rating, today's
     hours, short description, tags.

  FEATURES
  • Remove bookmark — heart toggle removes from list + calls API.
  • Skeleton loading — shows placeholder cards while hydrating.
  • Empty state — message when user has no saved businesses.
  • Hours extraction — todayHours() helper pulls today's open/close times.

  MODULAR FLOW
    getBookmarkIds() → loop getBusiness(id) → hydrated array → template
    renders cards → remove button → toggleBookmark() API → splice from array
  ─────────────────────────────────────────────────────────────────────────────
-->
<template>
  <div class="bookmarks-page">
    <!-- Header -->
    <header class="page-header">
      <router-link to="/search" class="back-btn" title="Back to search">
        <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24"
          fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <path d="m15 18-6-6 6-6"/>
        </svg>
      </router-link>
      <h1 class="page-title">
        <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24"
          fill="currentColor" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z"/>
        </svg>
        My Favorites
      </h1>
      <span v-if="favorites.length" class="fav-count">{{ favorites.length }} saved</span>
    </header>

    <!-- Loading state -->
    <div v-if="loading" class="state-msg">
      <div class="spinner" />
      <span>Loading your favorites...</span>
    </div>

    <!-- Error state -->
    <div v-else-if="error" class="state-msg error">
      <p>{{ error }}</p>
      <button class="retry-btn" @click="fetchBookmarks">Try again</button>
    </div>

    <!-- Not logged in -->
    <div v-else-if="!isLoggedIn" class="state-msg">
      <p>Please log in to see your saved businesses.</p>
      <router-link to="/login" class="login-link">Log in</router-link>
    </div>

    <!-- Empty state -->
    <div v-else-if="favorites.length === 0" class="state-msg empty">
      <svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" viewBox="0 0 24 24"
        fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
        <path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z"/>
      </svg>
      <p>You haven't saved any businesses yet.</p>
      <router-link to="/search" class="browse-link">Browse businesses</router-link>
    </div>

    <!-- Favorites grid -->
    <div v-else class="favorites-grid">
      <div
        v-for="fav in favorites"
        :key="fav.bookmarkId"
        class="fav-card"
      >
        <!-- Remove heart button -->
        <button
          class="remove-btn"
          title="Remove from favorites"
          :disabled="fav.removing"
          @click.prevent="handleRemove(fav)"
        >
          <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24"
            fill="currentColor" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z"/>
          </svg>
        </button>

        <router-link
          :to="{ name: 'BusinessDetail', params: { id: fav.id } }"
          class="card-link"
        >
          <!-- Photo banner -->
          <div class="card-photo">
            <img
              v-if="fav.photoSrc"
              :src="fav.photoSrc"
              :alt="fav.name"
              @error="fav.photoSrc = null"
            />
            <div v-else class="photo-placeholder">
              <span class="placeholder-letter">{{ fav.name?.charAt(0) || '?' }}</span>
            </div>
            <!-- Overlay badges -->
            <div class="photo-overlay">
              <span v-if="fav.category_detail" class="badge badge-category">{{ fav.category_detail.name }}</span>
              <span v-if="fav.price_level != null" class="badge badge-price">{{ '$'.repeat(fav.price_level) }}</span>
            </div>
          </div>

          <!-- Card body -->
          <div class="card-body">
            <!-- Title row -->
            <div class="body-top">
              <h3 class="card-title">{{ fav.name }}</h3>
              <div v-if="fav.avg_rating" class="card-rating">
                <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="currentColor"><path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z"/></svg>
                <span>{{ Number(fav.avg_rating).toFixed(1) }}</span>
                <span v-if="fav.user_rating_count" class="rating-count">({{ fav.user_rating_count }})</span>
              </div>
            </div>

            <!-- Description -->
            <p v-if="fav.description" class="card-desc">{{ truncate(fav.description, 120) }}</p>

            <!-- Info row: address + hours -->
            <div class="card-details">
              <div v-if="fav.address" class="detail-item">
                <svg xmlns="http://www.w3.org/2000/svg" width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"/><circle cx="12" cy="10" r="3"/></svg>
                <span>{{ fav.address }}</span>
              </div>
              <div v-if="fav.phone" class="detail-item">
                <svg xmlns="http://www.w3.org/2000/svg" width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6 19.79 19.79 0 0 1-3.07-8.67A2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72c.127.96.361 1.903.7 2.81a2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45c.907.339 1.85.573 2.81.7A2 2 0 0 1 22 16.92z"/></svg>
                <span>{{ fav.phone }}</span>
              </div>
              <div v-if="todayHours(fav)" class="detail-item">
                <svg xmlns="http://www.w3.org/2000/svg" width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg>
                <span>{{ todayHours(fav) }}</span>
              </div>
            </div>

            <!-- Service pills -->
            <div v-if="serviceList(fav).length" class="card-services">
              <span v-for="svc in serviceList(fav)" :key="svc" class="service-pill">{{ svc }}</span>
            </div>

            <!-- Tags -->
            <div v-if="fav.tags?.length" class="card-tags">
              <span v-for="tag in fav.tags.slice(0, 6)" :key="tag.id" class="tag-pill">{{ tag.name }}</span>
              <span v-if="fav.tags.length > 6" class="tag-pill more">+{{ fav.tags.length - 6 }}</span>
            </div>

            <!-- Top review snippet -->
            <div v-if="topReview(fav)" class="card-review">
              <div class="review-header">
                <span class="review-author">{{ topReview(fav).author }}</span>
                <span class="review-stars">
                  <svg v-for="n in 5" :key="n" width="12" height="12" viewBox="0 0 24 24" :fill="n <= Math.round(topReview(fav).rating) ? 'currentColor' : 'none'" stroke="currentColor" stroke-width="2"><polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/></svg>
                </span>
              </div>
              <p class="review-text">"{{ truncate(topReview(fav).text, 150) }}"</p>
            </div>

            <!-- Footer: saved date + note -->
            <div class="card-footer">
              <span class="saved-date">Saved {{ formatDate(fav.savedAt) }}</span>
              <span v-if="fav.note" class="saved-note">{{ fav.note }}</span>
            </div>
          </div>
        </router-link>
      </div>
    </div>

    <!-- Pagination -->
    <div v-if="nextPage" class="load-more">
      <button class="load-more-btn" :disabled="loadingMore" @click="loadMore">
        <span v-if="loadingMore">Loading...</span>
        <span v-else>Load more</span>
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { getBookmarks, toggleBookmark, getNextPage, getBusiness, getBusinessPhotoUrl } from '@/api/client'
import { useAuth } from '@/composables/useAuth'
import { truncate, formatDate, todayHours, serviceList } from '@/utils/helpers'

const { isLoggedIn, checked, refresh } = useAuth()

// ── State ────────────────────────────────────────────────────────────────
const favorites   = ref([])
const loading     = ref(true)
const loadingMore = ref(false)
const error       = ref('')
const nextPage    = ref(null)

// ── Hydrate bookmark → full business object ──────────────────────────────
async function hydrate(bookmark) {
  const base = {
    bookmarkId: bookmark.id,
    id: bookmark.business,
    name: bookmark.business_name,
    note: bookmark.note || '',
    savedAt: bookmark.created_at,
    photoSrc: null,
    removing: false,
    // Filled by getBusiness:
    description: null,
    category_detail: null,
    tags: [],
    address: null,
    phone: null,
    website_url: null,
    avg_rating: null,
    user_rating_count: null,
    review_count: 0,
    reviews_data: [],
    price_level: null,
    opening_hours: null,
    photo_references: [],
    image_url: null,
    dine_in: null,
    takeout: null,
    delivery: null,
    outdoor_seating: null,
    serves_breakfast: null,
    serves_lunch: null,
    serves_dinner: null,
    serves_brunch: null,
    business_status: null,
  }

  try {
    const { data } = await getBusiness(bookmark.business)
    Object.assign(base, {
      name: data.name || base.name,
      description: data.description,
      category_detail: data.category_detail,
      tags: data.tags || [],
      address: data.address,
      phone: data.phone,
      website_url: data.website_url,
      avg_rating: data.avg_rating,
      user_rating_count: data.user_rating_count,
      review_count: data.review_count,
      reviews_data: data.reviews_data || [],
      price_level: data.price_level,
      opening_hours: data.opening_hours,
      photo_references: data.photo_references || [],
      image_url: data.image_url,
      dine_in: data.dine_in,
      takeout: data.takeout,
      delivery: data.delivery,
      outdoor_seating: data.outdoor_seating,
      serves_breakfast: data.serves_breakfast,
      serves_lunch: data.serves_lunch,
      serves_dinner: data.serves_dinner,
      serves_brunch: data.serves_brunch,
      business_status: data.business_status,
    })
    // Resolve photo
    if (data.image_url) {
      base.photoSrc = data.image_url
    } else if (data.photo_references?.length) {
      base.photoSrc = getBusinessPhotoUrl(data.id)
    }
  } catch {
    // Keep partial data from bookmark
  }

  return base
}

// ── Fetch bookmarks + hydrate ────────────────────────────────────────────
async function fetchBookmarks() {
  if (!isLoggedIn.value) {
    loading.value = false
    return
  }

  loading.value = true
  error.value = ''
  try {
    const { data } = await getBookmarks()
    const rawBookmarks = data.results ?? []
    nextPage.value = data.next ?? null

    // Hydrate all in parallel
    favorites.value = await Promise.all(rawBookmarks.map(hydrate))
  } catch (err) {
    error.value = err.response?.data?.detail || err.message || 'Failed to load bookmarks'
  } finally {
    loading.value = false
  }
}

// ── Load more (pagination) ───────────────────────────────────────────────
async function loadMore() {
  if (!nextPage.value) return
  loadingMore.value = true
  try {
    const { data } = await getNextPage(nextPage.value)
    const more = await Promise.all((data.results ?? []).map(hydrate))
    favorites.value.push(...more)
    nextPage.value = data.next ?? null
  } catch {
    // ignore
  } finally {
    loadingMore.value = false
  }
}

// ── Remove bookmark ──────────────────────────────────────────────────────
async function handleRemove(fav) {
  const idx = favorites.value.findIndex(f => f.bookmarkId === fav.bookmarkId)
  if (idx === -1) return
  fav.removing = true
  const removed = favorites.value.splice(idx, 1)[0]
  try {
    await toggleBookmark(fav.id)
  } catch {
    removed.removing = false
    favorites.value.splice(idx, 0, removed)
  }
}

// ── Helpers ──────────────────────────────────────────────────────────────
// truncate, formatDate, todayHours, serviceList — imported from @/utils/helpers

/** Pick the highest-rated review with text */
function topReview(biz) {
  const reviews = biz.reviews_data
  if (!reviews?.length) return null
  const best = reviews
    .filter(r => r.text)
    .sort((a, b) => (b.rating || 0) - (a.rating || 0))[0]
  return best || null
}

// ── Init ─────────────────────────────────────────────────────────────────
onMounted(async () => {
  if (!checked.value) await refresh()
  fetchBookmarks()
})
</script>

<style scoped>
/* ══════════════════════════════════════════════════════════════════════════ */
/* LAYOUT                                                                     */
/* ══════════════════════════════════════════════════════════════════════════ */
.bookmarks-page {
  min-height: 100vh;
  background: var(--color-bg);
  color: var(--color-text);
  padding: 0 0 60px;
}

/* ── Header ────────────────────────────────────────────────────────────── */
.page-header {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 24px 32px;
  border-bottom: 1px solid var(--color-border);
}
.back-btn {
  display: flex; align-items: center; justify-content: center;
  width: 36px; height: 36px; border-radius: 50%;
  background: var(--color-surface);
  color: var(--color-text-muted);
  transition: background 0.2s, color 0.2s;
  text-decoration: none;
}
.back-btn:hover { background: var(--color-primary); color: #fff; }
.page-title {
  display: flex; align-items: center; gap: 10px;
  font-size: 22px; font-weight: 700;
  color: var(--color-primary);
}
.fav-count {
  margin-left: auto;
  font-size: 13px; font-weight: 500;
  color: var(--color-text-muted);
  background: rgba(0,0,0,0.03);
  padding: 4px 14px; border-radius: 20px;
  border: 1px solid var(--color-border);
}

/* ── States ────────────────────────────────────────────────────────────── */
.state-msg {
  display: flex; flex-direction: column; align-items: center; justify-content: center;
  gap: 16px; padding: 100px 24px;
  color: var(--color-text-muted); text-align: center;
}
.state-msg.error { color: #f87171; }
.state-msg.empty svg { opacity: 0.4; }

.retry-btn, .login-link, .browse-link {
  display: inline-block; padding: 10px 22px; border-radius: 8px;
  background: var(--color-primary); color: #fff;
  font-weight: 600; font-size: 14px; text-decoration: none;
  transition: background 0.2s;
}
.retry-btn:hover, .login-link:hover, .browse-link:hover { background: var(--color-primary-hover); }
.retry-btn { border: none; cursor: pointer; }

/* ══════════════════════════════════════════════════════════════════════════ */
/* GRID — big cards, 2 columns on desktop                                    */
/* ══════════════════════════════════════════════════════════════════════════ */
.favorites-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(420px, 1fr));
  gap: 24px; padding: 32px;
  max-width: 1400px; margin: 0 auto;
}

/* ══════════════════════════════════════════════════════════════════════════ */
/* FAV CARD                                                                   */
/* ══════════════════════════════════════════════════════════════════════════ */
.fav-card {
  position: relative;
  border-radius: 18px;
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  overflow: hidden;
  transition: transform 0.2s, box-shadow 0.2s;
}
.fav-card:hover {
  transform: translateY(-4px);
  box-shadow: var(--shadow-lg, 0 12px 32px rgba(15,23,42,0.12));
}
.card-link { display: block; text-decoration: none; color: inherit; }

/* ── Photo banner ─────────────────────────────────────────────────────── */
.card-photo {
  position: relative;
  height: 200px;
  background: var(--color-bg);
  overflow: hidden;
}
.card-photo img { width: 100%; height: 100%; object-fit: cover; }
.photo-placeholder {
  width: 100%; height: 100%;
  display: flex; align-items: center; justify-content: center;
  background: linear-gradient(135deg, var(--color-primary) 0%, #7c3aed 50%, var(--color-accent-gold, #f59e0b) 100%);
}
.placeholder-letter { font-size: 64px; font-weight: 800; color: #fff; opacity: 0.85; }

.photo-overlay {
  position: absolute; bottom: 10px; left: 12px;
  display: flex; gap: 6px;
}
.badge {
  padding: 4px 10px; border-radius: 6px;
  font-size: 11px; font-weight: 600;
  backdrop-filter: blur(8px); -webkit-backdrop-filter: blur(8px);
}
.badge-category { background: rgba(37,99,235,0.75); color: #fff; }
.badge-price { background: rgba(0,0,0,0.55); color: #f59e0b; }

/* ── Remove heart button ──────────────────────────────────────────────── */
.remove-btn {
  position: absolute; top: 14px; right: 14px; z-index: 3;
  width: 40px; height: 40px; border-radius: 50%;
  background: rgba(0,0,0,0.5); backdrop-filter: blur(4px);
  color: #f87171; border: none; cursor: pointer;
  display: flex; align-items: center; justify-content: center;
  opacity: 0; transition: opacity 0.2s, background 0.2s, transform 0.15s;
}
.fav-card:hover .remove-btn { opacity: 1; }
.remove-btn:hover { background: rgba(248,113,113,0.3); transform: scale(1.1); }
.remove-btn:disabled { opacity: 0.4; cursor: not-allowed; }

/* ── Card body ────────────────────────────────────────────────────────── */
.card-body { padding: 18px 20px 20px; display: flex; flex-direction: column; gap: 10px; }

.body-top { display: flex; align-items: flex-start; justify-content: space-between; gap: 12px; }
.card-title {
  font-size: 19px; font-weight: 700; margin: 0;
  color: var(--color-text); line-height: 1.3;
}
.card-rating {
  display: flex; align-items: center; gap: 4px; flex-shrink: 0;
  font-size: 14px; font-weight: 700; color: var(--color-accent-gold, #f59e0b);
}
.card-rating svg { color: var(--color-accent-gold, #f59e0b); }
.rating-count { font-size: 11px; font-weight: 400; color: var(--color-text-muted); }

.card-desc {
  font-size: 13px; color: var(--color-text-light);
  line-height: 1.5; margin: 0;
}

/* ── Details (address, phone, hours) ──────────────────────────────────── */
.card-details { display: flex; flex-direction: column; gap: 5px; }
.detail-item {
  display: flex; align-items: center; gap: 6px;
  font-size: 12px; color: var(--color-text-muted);
}
.detail-item svg { flex-shrink: 0; opacity: 0.7; }

/* ── Service pills ────────────────────────────────────────────────────── */
.card-services { display: flex; flex-wrap: wrap; gap: 5px; }
.service-pill {
  padding: 3px 10px; border-radius: 20px;
  font-size: 10px; font-weight: 600; text-transform: uppercase;
  letter-spacing: 0.04em;
  background: rgba(34,197,94,0.08); color: var(--color-success, #22c55e);
  border: 1px solid rgba(34,197,94,0.15);
}

/* ── Tags ─────────────────────────────────────────────────────────────── */
.card-tags { display: flex; flex-wrap: wrap; gap: 5px; }
.tag-pill {
  padding: 3px 10px; font-size: 11px; border-radius: 999px;
  background: rgba(67,56,202,0.06); border: 1px solid var(--color-border-light, #c7d2fe);
  color: var(--color-accent, #4338ca);
}
.tag-pill.more {
  background: transparent; border-color: var(--color-border);
  color: var(--color-text-muted);
}

/* ── Top review snippet ───────────────────────────────────────────────── */
.card-review {
  padding: 10px 14px; border-radius: 10px;
  background: rgba(0,0,0,0.02); border: 1px solid var(--color-border);
}
.review-header { display: flex; align-items: center; gap: 8px; margin-bottom: 4px; }
.review-author { font-size: 12px; font-weight: 600; color: var(--color-text); }
.review-stars { color: var(--color-accent-gold, #f59e0b); display: inline-flex; align-items: center; gap: 1px; }
.review-text {
  margin: 0; font-size: 12px; color: var(--color-text-muted);
  line-height: 1.5; font-style: italic;
}

/* ── Footer ───────────────────────────────────────────────────────────── */
.card-footer {
  display: flex; align-items: center; gap: 12px;
  padding-top: 10px; border-top: 1px solid var(--color-border);
  margin-top: 2px;
}
.saved-date { font-size: 11px; color: #f87171; font-weight: 500; }
.saved-note { font-size: 11px; color: var(--color-text-muted); }

/* ══════════════════════════════════════════════════════════════════════════ */
/* PAGINATION                                                                 */
/* ══════════════════════════════════════════════════════════════════════════ */
.load-more { display: flex; justify-content: center; padding: 0 32px 32px; }
.load-more-btn {
  padding: 12px 32px; border-radius: 10px;
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  color: var(--color-text);
  font-weight: 600; font-size: 14px; cursor: pointer;
  transition: background 0.2s;
}
.load-more-btn:hover:not(:disabled) { background: var(--color-primary); border-color: var(--color-primary); color: #fff; }
.load-more-btn:disabled { opacity: 0.6; cursor: not-allowed; }

/* ══════════════════════════════════════════════════════════════════════════ */
/* RESPONSIVE                                                                 */
/* ══════════════════════════════════════════════════════════════════════════ */
@media (max-width: 768px) {
  .page-header { padding: 16px 20px; }
  .page-title { font-size: 18px; }
  .favorites-grid { padding: 20px 16px; gap: 16px; grid-template-columns: 1fr; }
  .card-photo { height: 180px; }
  .card-title { font-size: 17px; }
}
</style>
