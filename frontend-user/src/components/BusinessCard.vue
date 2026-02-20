<!--
  BusinessCard.vue — Search Result / Listing Card
  ─────────────────────────────────────────────────────────────────────────────
  Horizontal card used in SearchPage, BookmarksPage, and NearbyForYou.

  LAYOUT
  ┌────────────────────────────────────────────────────────┐
  │  [Photo]  │  Title                                     │
  │           │  Category · ★ 4.2 · $$ · 1.3 km           │
  │           │  "Great cozy spot…" — review snippet       │
  │           │  📍 123 Main St                            │
  │           │  [tag] [tag] [tag]                         │
  └────────────────────────────────────────────────────────┘

  KEY FEATURES
  • Entire card is a <router-link> so clicking anywhere navigates.
  • Review snippets: picks the best review (one that mentions the most tags),
    truncates to ~140 chars, and bolds any tag keywords with v-html.
  • Photo cascade: GCS image_url → photo proxy → fallback placeholder SVG.
  • `escapeHtml` sanitises review text before bolding (XSS protection).

  MODULAR FLOW
    props.business → computed photoSrc + reviewSnippets → template renders
  ─────────────────────────────────────────────────────────────────────────────
-->
<template>
  <router-link :to="{ name: 'BusinessDetail', params: { id: business.id } }" class="business-card">
    <!-- Photo -->
    <div class="card-image">
      <img
        v-if="photoSrc"
        :src="photoSrc"
        :alt="business.name"
        @error="imgFailed = true"
      />
      <div v-else class="no-photo">
        <svg xmlns="http://www.w3.org/2000/svg" width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="3" width="18" height="18" rx="2" ry="2"/><circle cx="8.5" cy="8.5" r="1.5"/><polyline points="21 15 16 10 5 21"/></svg>
      </div>
    </div>

    <!-- Body -->
    <div class="card-body">
      <h3 class="card-title">{{ business.name }}</h3>

      <div class="card-meta">
        <span v-if="business.category_detail" class="category-badge">
          {{ business.category_detail.name }}
        </span>
        <span v-if="business.avg_rating" class="rating">
          ★ {{ Number(business.avg_rating).toFixed(1) }}
        </span>
        <span v-if="business.price_level != null" class="price">
          {{ '$'.repeat(business.price_level) }}
        </span>
        <span v-if="business.distance_km != null" class="distance">
          {{ business.distance_km.toFixed(1) }} km
        </span>
      </div>

      <!-- ── Review snippets (1–2 reviews, tag words bolded) ── -->
      <div v-if="reviewSnippets.length" class="card-reviews">
        <div
          v-for="(snippet, idx) in reviewSnippets"
          :key="idx"
          class="review-snippet"
        >
          <span class="review-author">{{ snippet.author }}</span>
          <span class="review-stars">{{ '★'.repeat(snippet.rating) }}{{ '☆'.repeat(5 - snippet.rating) }}</span>
          <p class="review-text" v-html="snippet.html"></p>
        </div>
      </div>

      <p v-if="business.address" class="card-address">
        <svg xmlns="http://www.w3.org/2000/svg" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="address-icon"><path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"/><circle cx="12" cy="10" r="3"/></svg>
        {{ business.address }}
      </p>

      <!-- Tags -->
      <div v-if="business.tags?.length" class="card-tags">
        <span v-for="tag in business.tags.slice(0, 5)" :key="tag.id" class="tag-pill">
          {{ tag.name }}
        </span>
        <span v-if="business.tags.length > 5" class="tag-pill more">
          +{{ business.tags.length - 5 }}
        </span>
      </div>

      <!-- Search relevance (only shown for search results) -->
      <div v-if="business.similarity != null" class="card-score">
        <span class="score-item">
          Match: {{ (business.similarity * 100).toFixed(0) }}%
        </span>
      </div>
    </div>
  </router-link>
</template>

<script setup>
import { computed, ref } from 'vue'
import { getBusinessPhotoUrl } from '@/api/client'
import { truncate, escapeHtml } from '@/utils/helpers'

const props = defineProps({
  business: { type: Object, required: true }
})

const imgFailed = ref(false)

const photoSrc = computed(() => {
  if (imgFailed.value) return null
  // Prefer the stored GCS image_url if available
  if (props.business.image_url) return props.business.image_url
  // Fall back to the photo proxy if the business has photo_references
  if (props.business.photo_references?.length) {
    return getBusinessPhotoUrl(props.business.id)
  }
  return null
})

/**
 * Bold any words in `text` that match one of the business's tag names.
 * Uses a single regex pass for efficiency.
 */
function highlightTags(text, tagNames) {
  if (!tagNames.length) return escapeHtml(text)
  // Build a regex that matches any tag name (case-insensitive, word boundaries)
  const escaped = tagNames.map(t => t.replace(/[.*+?^${}()|[\]\\]/g, '\\$&'))
  const re = new RegExp(`\\b(${escaped.join('|')})\\b`, 'gi')
  // We need to escape HTML first, then apply the bold tags
  const safe = escapeHtml(text)
  return safe.replace(re, '<strong class="tag-highlight">$1</strong>')
}

/**
 * Pick the best 1–2 reviews from `reviews_data` and produce
 * truncated HTML snippets with tag-related words bolded.
 */
const reviewSnippets = computed(() => {
  const reviews = props.business.reviews_data
  if (!reviews?.length) return []

  const tagNames = (props.business.tags || []).map(t => t.name)

  // Sort reviews: prefer ones that mention tags, then by highest rating, then most recent
  const scored = reviews
    .filter(r => r.text)
    .map(r => {
      const tagHits = tagNames.reduce((n, t) =>
        n + (r.text.toLowerCase().includes(t.toLowerCase()) ? 1 : 0), 0)
      return { ...r, tagHits }
    })
    .sort((a, b) => b.tagHits - a.tagHits || b.rating - a.rating)

  // Take at most 1
  return scored.slice(0, 1).map(r => {
    // Truncate to ~140 chars to get roughly 1–2 lines
    const short = truncate(r.text, 140)
    return {
      author: r.author || 'Anonymous',
      rating: Math.round(r.rating || 0),
      html: highlightTags(short, tagNames)
    }
  })
})
</script>

<style scoped>
.business-card {
  display: flex;
  gap: 16px;
  padding: 16px;
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: var(--radius, 8px);
  text-decoration: none;
  color: inherit;
  transition: border-color 0.2s, box-shadow 0.2s;
}
.business-card:hover {
  border-color: rgba(74, 112, 169, 0.3);
  box-shadow: var(--shadow-md);
}

/* ── Image ── */
.card-image {
  width: 140px;
  height: 110px;
  flex-shrink: 0;
  border-radius: 6px;
  overflow: hidden;
  background: var(--color-bg);
}
.card-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}
.no-photo {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--color-border);
}

/* ── Body ── */
.card-body {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.card-title {
  font-size: 16px;
  font-weight: 600;
  color: var(--color-text);
  margin: 0;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.card-meta {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 13px;
}
.category-badge {
  color: var(--color-primary);
  font-weight: 500;
}
.rating {
  color: var(--color-accent-gold, #f59e0b);
  font-weight: 600;
}
.price {
  color: var(--color-text-muted);
}
.distance {
  color: var(--color-text-muted);
}

.card-desc {
  font-size: 13px;
  color: var(--color-text-muted);
  line-height: 1.4;
  margin: 0;
}

.card-address {
  font-size: 12px;
  color: var(--color-text-muted);
  margin: 0;
  display: flex;
  align-items: center;
  gap: 4px;
}
.address-icon {
  flex-shrink: 0;
}

/* ── Tags ── */
.card-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
}
.tag-pill {
  padding: 2px 8px;
  font-size: 11px;
  border-radius: 999px;
  background: rgba(67, 56, 202, 0.06);
  border: 1px solid var(--color-border-light, #c7d2fe);
  color: var(--color-accent, #4338ca);
}
.tag-pill.more {
  background: transparent;
  border-color: var(--color-border);
  color: var(--color-text-muted);
}

/* ── Score (search results only) ── */
.card-score {
  display: flex;
  gap: 12px;
  margin-top: auto;
}
.score-item {
  font-size: 11px;
  color: var(--color-text-muted);
  background: rgba(0, 0, 0, 0.03);
  padding: 2px 8px;
  border-radius: 4px;
}

/* ── Review snippets ── */
.card-reviews {
  display: flex;
  flex-direction: column;
  gap: 6px;
  margin-top: 2px;
}
.review-snippet {
  display: flex;
  flex-wrap: wrap;
  align-items: baseline;
  gap: 6px;
  font-size: 12px;
  line-height: 1.5;
}
.review-author {
  font-weight: 600;
  color: var(--color-text);
  white-space: nowrap;
}
.review-stars {
  color: var(--color-accent-gold, #f59e0b);
  font-size: 11px;
  letter-spacing: 0.5px;
}
.review-text {
  width: 100%;
  margin: 0;
  color: var(--color-text-muted);
  font-style: italic;
  line-height: 1.45;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
.review-text :deep(.tag-highlight) {
  color: var(--color-primary);
  font-weight: 700;
  font-style: normal;
}
</style>
