<!--
  BusinessHero.vue — Business Detail Page Banner
  ─────────────────────────────────────────────────────────────────────────────
  Full-width hero image with a dark gradient overlay at the bottom showing:
  • Business logo (or first-letter placeholder)
  • Business name
  • Star rating + review count
  • Tag pills (first 5)
  • Bookmark (heart) toggle button

  PROPS
  • name, bannerUrl, avgRating, reviewCount, tags, bookmarked

  EVENTS
  • @toggle-bookmark — heart button clicked

  MODULAR FLOW
    BusinessDetailPage passes data from useBusinessDetail composable
    → this component renders the visual hero section.
  ─────────────────────────────────────────────────────────────────────────────
-->
<template>
  <section class="hero" :style="bannerUrl ? { backgroundImage: `url(${bannerUrl})` } : {}">
    <div class="hero-overlay" />
    <div class="hero-content">
      <div class="hero-logo">
        <img v-if="bannerUrl" :src="bannerUrl" :alt="name" class="logo-img" @error="$event.target.style.display='none'" />
        <div v-else class="logo-placeholder">{{ name.charAt(0) }}</div>
      </div>
      <div class="hero-text">
        <h1 class="business-name">{{ name }}</h1>
        <div class="hero-rating">
          <StarRating :model-value="avgRating" />
          <span class="rating-num">{{ avgRating.toFixed(1) }}</span>
          <span class="rating-count">({{ reviewCount }} reviews)</span>
        </div>
        <div v-if="tags?.length" class="hero-tags">
          <span v-for="tag in tags.slice(0, 5)" :key="tag.id" class="hero-tag">{{ tag.name }}</span>
        </div>
      </div>
      <button class="bookmark-btn" :class="{ active: bookmarked }" @click="$emit('toggle-bookmark')">
        <svg xmlns="http://www.w3.org/2000/svg" width="22" height="22" viewBox="0 0 24 24"
          :fill="bookmarked ? 'currentColor' : 'none'" stroke="currentColor"
          stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z"/>
        </svg>
      </button>
    </div>
  </section>
</template>

<script setup>
import StarRating from '@/components/ui/StarRating.vue'

defineProps({
  name: { type: String, required: true },
  bannerUrl: String,
  avgRating: { type: Number, default: 0 },
  reviewCount: { type: Number, default: 0 },
  tags: Array,
  bookmarked: Boolean
})

defineEmits(['toggle-bookmark'])
</script>

<style scoped>
.hero {
  position: relative; height: 280px;
  background: var(--color-surface) center / cover no-repeat;
  display: flex; align-items: flex-end;
}
.hero-overlay {
  position: absolute; inset: 0;
  background: linear-gradient(to top, rgba(15,23,42,0.85) 0%, rgba(15,23,42,0.2) 100%);
}
.hero-content {
  position: relative; z-index: 1;
  display: flex; align-items: flex-end; gap: 20px;
  width: 100%; max-width: 900px; margin: 0 auto; padding: 24px 32px;
}
.hero-logo {
  width: 80px; height: 80px; flex-shrink: 0;
  border-radius: 12px; overflow: hidden;
  border: 3px solid rgba(255,255,255,0.2);
  background: var(--color-surface);
}
.logo-img { width: 100%; height: 100%; object-fit: cover; }
.logo-placeholder {
  width: 100%; height: 100%;
  display: flex; align-items: center; justify-content: center;
  font-size: 32px; font-weight: 700; color: var(--color-primary);
  background: rgba(74,112,169,0.1);
}
.hero-text { flex: 1; min-width: 0; color: #fff; }
.business-name {
  font-size: 28px; font-weight: 700; margin: 0 0 6px;
  white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
}
.hero-rating { display: flex; align-items: center; gap: 8px; font-size: 14px; }
.rating-num { font-weight: 700; font-size: 16px; }
.rating-count { color: rgba(255,255,255,0.7); }
.hero-tags { display: flex; gap: 6px; margin-top: 8px; flex-wrap: wrap; }
.hero-tag {
  padding: 2px 10px; font-size: 11px; border-radius: 999px;
  background: rgba(255,255,255,0.15); border: 1px solid rgba(255,255,255,0.25); color: #fff;
}
.bookmark-btn {
  flex-shrink: 0; width: 44px; height: 44px;
  display: flex; align-items: center; justify-content: center;
  border-radius: 50%; border: 1px solid rgba(255,255,255,0.25);
  background: rgba(0,0,0,0.3); color: rgba(255,255,255,0.7);
  cursor: pointer; transition: all 0.2s;
}
.bookmark-btn:hover { border-color: #ef4444; color: #ef4444; }
.bookmark-btn.active { color: #ef4444; border-color: #ef4444; background: rgba(239,68,68,0.15); }
</style>
