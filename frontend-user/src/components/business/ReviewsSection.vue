<!--
  ReviewsSection.vue — Reviews List with Summary + Sort
  ─────────────────────────────────────────────────────────────────────────────
  Full reviews section on the Business Detail page.

  SECTIONS (top → bottom)
  1. Summary header  — big rating number + stars + total count
  2. "Customers Say"  — AI-generated one-liner about common themes
  3. Sort controls    — Newest / Oldest / Highest / Lowest
  4. Review list      — <ReviewCard> for each review
  5. Load more button — paginated fetching

  This is a presentational component — all data and actions are passed via
  props/emits from BusinessDetailPage (which uses useBusinessDetail).

  MODULAR FLOW
    useBusinessDetail → allReviews, sortedReviews, customersSay
    → BusinessDetailPage passes them as props → this component renders.
  ─────────────────────────────────────────────────────────────────────────────
-->
<template>
  <section class="section reviews-section">
    <!-- Summary Header -->
    <div class="reviews-header">
      <div class="reviews-summary">
        <span class="big-rating">{{ avgRating.toFixed(1) }}</span>
        <div class="summary-right">
          <StarRating :model-value="avgRating" />
          <span class="review-total">{{ totalCount }} Reviews</span>
        </div>
      </div>
    </div>

    <!-- Customers Say -->
    <div v-if="customersSay" class="customers-say">
      <div class="cs-icon">
        <img src="@/components/icons/orbit-logo.png" alt="Orbit" />
      </div>
      <div>
        <strong class="cs-label">Customers Say</strong>
        <p class="cs-text">{{ customersSay }}</p>
      </div>
    </div>

    <!-- Sort Controls -->
    <div class="review-sort">
      <span class="sort-label">Sort by:</span>
      <button
        v-for="opt in sortOptions" :key="opt.value"
        class="sort-btn" :class="{ active: currentSort === opt.value }"
        @click="$emit('sort', opt.value)"
      >{{ opt.label }}</button>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="reviews-loading">
      <div class="spinner-small" />
      <span>Loading reviews...</span>
    </div>

    <!-- Review List -->
    <div v-else class="review-list">
      <ReviewCard
        v-for="r in reviews" :key="r.id"
        :review="r"
        @vote="(id, type) => $emit('vote', id, type)"
      />
      <div v-if="reviews.length === 0" class="no-reviews">
        <p>No reviews yet. Be the first to share your experience!</p>
      </div>
    </div>

    <!-- Load More -->
    <div v-if="hasMore && !loading" class="load-more-section">
      <button class="load-more-btn" :disabled="loadingMore" @click="$emit('load-more')">
        {{ loadingMore ? 'Loading...' : 'Load More Reviews' }}
      </button>
    </div>
  </section>
</template>

<script setup>
import StarRating from '@/components/ui/StarRating.vue'
import ReviewCard from './ReviewCard.vue'

defineProps({
  avgRating: { type: Number, default: 0 },
  totalCount: { type: Number, default: 0 },
  customersSay: String,
  reviews: { type: Array, default: () => [] },
  currentSort: { type: String, default: '-created_at' },
  loading: Boolean,
  loadingMore: Boolean,
  hasMore: Boolean
})

defineEmits(['sort', 'vote', 'load-more'])

const sortOptions = [
  { value: '-created_at', label: 'Newest' },
  { value: 'created_at', label: 'Oldest' },
  { value: '-rating', label: 'Highest Rated' },
  { value: 'rating', label: 'Lowest Rated' }
]
</script>

<style scoped>
.section { max-width: 900px; margin: 0 auto; padding: 28px 32px; border-bottom: 1px solid var(--color-border); }
.reviews-section { padding-bottom: 60px; }
.reviews-header { display: flex; align-items: center; justify-content: space-between; margin-bottom: 16px; }
.reviews-summary { display: flex; align-items: center; gap: 14px; }
.big-rating { font-size: 42px; font-weight: 800; line-height: 1; color: var(--color-text); }
.summary-right { display: flex; flex-direction: column; }
.review-total { font-size: 13px; color: var(--color-text-muted); }

.customers-say {
  display: flex; align-items: flex-start; gap: 12px;
  padding: 14px 18px; margin-bottom: 20px;
  background: linear-gradient(135deg, rgba(67,56,202,0.05), rgba(139,92,246,0.03));
  border: 1px solid var(--color-border-light, #c7d2fe); border-radius: 10px;
}
.cs-icon {
  flex-shrink: 0; width: 40px; height: 40px;
  display: flex; align-items: center; justify-content: center;
  border-radius: 10px; background: #fff;
  box-shadow: 0 1px 3px rgba(0,0,0,0.08);
}
.cs-icon img { width: 28px; height: 28px; object-fit: contain; }
.cs-label { display: block; font-size: 12px; text-transform: uppercase; letter-spacing: 0.04em; color: var(--color-accent, #4338ca); margin-bottom: 4px; }
.cs-text { font-size: 13px; line-height: 1.5; color: var(--color-text-light, #475569); margin: 0; }

.review-sort { display: flex; flex-wrap: wrap; align-items: center; gap: 8px; margin-bottom: 16px; }
.sort-label { font-size: 13px; color: var(--color-text-muted); margin-right: 4px; }
.sort-btn {
  padding: 5px 14px; font-size: 12px; border-radius: 999px; cursor: pointer;
  background: var(--color-surface); border: 1px solid var(--color-border);
  color: var(--color-text-muted); transition: all 0.15s;
}
.sort-btn:hover { border-color: var(--color-primary); color: var(--color-text); }
.sort-btn.active { background: rgba(74,112,169,0.1); border-color: var(--color-primary); color: var(--color-primary); font-weight: 500; }

.reviews-loading { display: flex; align-items: center; justify-content: center; gap: 10px; padding: 40px 0; color: var(--color-text-muted); font-size: 14px; }
.spinner-small { width: 20px; height: 20px; border: 2px solid var(--color-border); border-top-color: var(--color-primary); border-radius: 50%; animation: spin 0.7s linear infinite; }
@keyframes spin { to { transform: rotate(360deg); } }

.no-reviews { text-align: center; padding: 40px 20px; color: var(--color-text-muted); font-size: 14px; }
.review-list { display: flex; flex-direction: column; gap: 20px; }

.load-more-section { display: flex; justify-content: center; margin-top: 24px; }
.load-more-btn {
  display: inline-flex; align-items: center; justify-content: center;
  padding: 12px 36px; min-width: 180px;
  background: var(--color-surface); border: 1px solid var(--color-border);
  color: var(--color-text); border-radius: 8px; font-size: 14px; font-weight: 500;
  cursor: pointer; transition: background 0.2s, border-color 0.2s;
}
.load-more-btn:hover:not(:disabled) { background: rgba(74,112,169,0.06); border-color: var(--color-primary); }
.load-more-btn:disabled { opacity: 0.6; cursor: not-allowed; }
</style>
