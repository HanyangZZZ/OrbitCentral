<!--
  BusinessDetailPage.vue — Single Business View (route: /business/:id)
  ─────────────────────────────────────────────────────────────────────────────
  Orchestrates all the sub-components that make up a business profile:

  ┌──────────────────────────────────────────────────────────┐
  │  BusinessHero  — banner image, name, rating, bookmark    │
  ├──────────────────────────────────────────────────────────┤
  │  ContactBar    — address, email, phone, website, actions │
  ├──────────────────────────────────────────────────────────┤
  │  Highlights    — feature pills (Wi-Fi, Parking, etc.)    │
  │  Description   — short business description              │
  │  Hours         — today's open/close times                │
  ├──────────────────────────────────────────────────────────┤
  │  ReviewsSection — sorted reviews with vote buttons       │
  └──────────────────────────────────────────────────────────┘

  MODALS (toggled by ContactBar action buttons)
  • WriteReviewModal    — AI-assisted review chat
  • ActivitiesModal     — vote for desired activities
  • CouponsModal        — business coupon display

  All data and logic lives in the `useBusinessDetail` composable.
  This page is purely an orchestrator — it wires composable refs/methods
  to child component props/events.

  MODULAR FLOW
    route.params.id → useBusinessDetail.fetchBusiness() → reactive state
    → child components render via props; user actions emit events back up
    → this page calls the appropriate composable method.
  ─────────────────────────────────────────────────────────────────────────────
-->
<template>
  <div class="detail-page">
    <!-- Loading / Error States -->
    <div v-if="loading" class="state-msg"><div class="spinner" /><span>Loading...</span></div>
    <div v-else-if="error" class="state-msg error">
      <p>{{ error }}</p>
      <router-link to="/search" class="back-link">← Back to search</router-link>
    </div>

    <template v-else-if="business">
      <!-- Hero Banner -->
      <BusinessHero
        :name="business.name"
        :banner-url="bannerUrl"
        :avg-rating="Number(business.avg_rating || 0)"
        :review-count="business.user_rating_count || 0"
        :tags="business.tags"
        :bookmarked="bookmarked"
        @toggle-bookmark="onToggleBookmark"
      />

      <!-- Contact Bar -->
      <ContactBar
        :address="business.address"
        :maps-uri="business.google_maps_uri"
        :email="business.contact_email"
        :phone="business.phone"
        :website="business.website_url"
        @write-review="showReviewModal = true"
        @vote-activities="showActivitiesModal = true"
        @view-coupons="showCouponsModal = true"
      />

      <!-- About / Short Description -->
      <section v-if="shortDescription" class="section about-section">
        <h2 class="section-title">About</h2>
        <p class="description-text">{{ shortDescription }}</p>
      </section>

      <!-- Hours -->
      <section v-if="weekdayHours.length" class="section">
        <h2 class="section-title">Hours</h2>
        <div class="hours-grid">
          <div v-for="(line, i) in weekdayHours" :key="i" class="hour-row" :class="{ today: i === todayIndex }">
            {{ line }}
          </div>
        </div>
      </section>

      <!-- Highlights -->
      <section v-if="highlights.length" class="section">
        <h2 class="section-title">Highlights</h2>
        <div class="highlights-grid">
          <div v-for="(h, i) in highlights" :key="i" class="highlight-card">
            <span class="highlight-icon" v-html="h.icon"></span>
            <div>
              <strong class="highlight-title">{{ h.title }}</strong>
              <p class="highlight-desc">{{ h.desc }}</p>
            </div>
          </div>
        </div>
      </section>

      <!-- Reviews Section -->
      <ReviewsSection
        :avg-rating="Number(business.avg_rating || 0)"
        :total-count="totalReviewCount"
        :customers-say="customersSay"
        :reviews="allReviews"
        :current-sort="reviewSort"
        :current-user-id="currentUserId"
        :loading="reviewsLoading"
        :loading-more="loadingMoreReviews"
        :has-more="!!reviewsNext"
        @sort="changeReviewSort"
        @vote="onVoteReview"
        @delete="onDeleteReview"
        @load-more="handleLoadMore"
      />

      <!-- Modals -->
      <WriteReviewModal
        v-model="showReviewModal"
        :business-id="business.id"
        @review-published="onReviewPublished"
      />
      <ActivitiesModal v-model="showActivitiesModal" :business-name="business.name" />
      <CouponsModal v-model="showCouponsModal" :business-name="business.name" />
    </template>

    <!-- Back FAB -->
    <router-link to="/search" class="fab-back" title="Back to search">
      <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="m15 18-6-6 6-6"/></svg>
    </router-link>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useBusinessDetail } from '@/composables/useBusinessDetail'
import { useAuth } from '@/composables/useAuth'

// Components
import BusinessHero from '@/components/business/BusinessHero.vue'
import ContactBar from '@/components/business/ContactBar.vue'
import ReviewsSection from '@/components/business/ReviewsSection.vue'
import WriteReviewModal from '@/components/business/WriteReviewModal.vue'
import ActivitiesModal from '@/components/business/ActivitiesModal.vue'
import CouponsModal from '@/components/business/CouponsModal.vue'

const props = defineProps({
  id: { type: [String, Number], required: true }
})

// ── Composable: All business data & methods ──────────────────────────────
const {
  business, loading, error,
  bannerUrl, highlights, customersSay, shortDescription,
  allReviews, totalReviewCount,
  reviewsNext, reviewSort, reviewsLoading,
  bookmarked,
  fetchBusiness, fetchReviews, loadMoreReviews, changeReviewSort,
  fetchBookmarkState, onToggleBookmark,
  submitReview, onDeleteReview, onVoteReview,
} = useBusinessDetail(props.id)

// ── Auth: current user for delete ownership check ─────────────────────
const { user: currentUser } = useAuth()
const currentUserId = computed(() => currentUser.value?.id ?? null)

// ── Local UI state ───────────────────────────────────────────────────────
const showReviewModal = ref(false)
const showActivitiesModal = ref(false)
const showCouponsModal = ref(false)
const loadingMoreReviews = ref(false)

// ── Derived data ─────────────────────────────────────────────────────────
const weekdayHours = computed(() => business.value?.opening_hours?.weekdayDescriptions || [])
const todayIndex = computed(() => {
  const d = new Date().getDay()
  return d === 0 ? 6 : d - 1
})

// ── Event handlers ───────────────────────────────────────────────────────
async function handleLoadMore() {
  loadingMoreReviews.value = true
  await loadMoreReviews()
  loadingMoreReviews.value = false
}

async function onReviewPublished() {
  await fetchReviews()
  await fetchBusiness()
}

// ── Initialization ───────────────────────────────────────────────────────
onMounted(async () => {
  await fetchBusiness()
  fetchReviews()
  fetchBookmarkState()
})
</script>

<style scoped>
.detail-page {
  min-height: 100vh;
  background: var(--color-bg);
  color: var(--color-text);
}

/* States */
.state-msg {
  display: flex; flex-direction: column; align-items: center; justify-content: center;
  gap: 12px; padding: 120px 20px; color: var(--color-text-muted); font-size: 15px;
}
.state-msg.error { color: #ef4444; }
.back-link { color: var(--color-primary); font-size: 14px; }

/* Sections */
.section {
  max-width: 900px; margin: 0 auto; padding: 28px 32px;
  border-bottom: 1px solid var(--color-border);
}
.section-title { font-size: 18px; font-weight: 600; color: var(--color-primary); margin-bottom: 16px; }

/* Description */
.description-text { font-size: 14px; line-height: 1.7; color: var(--color-text-light, #475569); margin: 0; }

/* Hours */
.hours-grid { display: flex; flex-direction: column; gap: 4px; }
.hour-row { font-size: 13px; color: var(--color-text-muted); padding: 4px 8px; border-radius: 4px; }
.hour-row.today { background: rgba(74,112,169,0.08); color: var(--color-text); font-weight: 600; }

/* Highlights */
.highlights-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(190px, 1fr)); gap: 12px; }
.highlight-card {
  display: flex; align-items: flex-start; gap: 10px; padding: 14px; border-radius: 10px;
  background: var(--color-surface); border: 1px solid var(--color-border);
}
.highlight-icon {
  flex-shrink: 0; width: 36px; height: 36px;
  display: flex; align-items: center; justify-content: center;
  border-radius: 8px; background: rgba(74,112,169,0.08); color: var(--color-primary, #4a70a9);
}
.highlight-title { font-size: 13px; display: block; }
.highlight-desc { font-size: 12px; color: var(--color-text-muted); margin: 2px 0 0; }

/* FAB */
.fab-back {
  position: fixed; bottom: 24px; left: 24px; z-index: 100;
  width: 44px; height: 44px; border-radius: 50%;
  display: flex; align-items: center; justify-content: center;
  background: var(--color-surface); border: 1px solid var(--color-border);
  color: var(--color-text); box-shadow: var(--shadow-md);
  transition: background 0.2s, border-color 0.2s; text-decoration: none;
}
.fab-back:hover { background: rgba(74,112,169,0.06); border-color: var(--color-primary); }
</style>
