<!--
  CategoryGrid.vue — "Browse by Category" 2×3 Image Grid
  ─────────────────────────────────────────────────────────────────────────────
  Displayed below the hero on the Home page. Shows the top 6 parent categories
  as clickable image cards arranged in two rows of three.

  VISUAL DETAILS
  • Each card has a photo + dark navy overlay + star sparkle hover animation.
  • Vertical dividers separate cards within a row; a horizontal divider
    separates row 1 from row 2.
  • On mobile the rows stack vertically.

  STAR SPARKLE EFFECT
  Five invisible <span class="star"> elements are positioned around each card.
  On hover they animate in with a cross-shaped SVG-like effect
  (two perpendicular bars created via ::before and ::after pseudo-elements).

  PROPS
  • categories — Array of parent category objects (from API)
  • loading    — shows orbital spinner while categories are being fetched

  EVENTS
  • @select(category) — emitted when a user clicks a category card

  MODULAR FLOW
    HomePage fetches categories → passes them here → user clicks →
    HomePage pushes to /search?category=…
  ─────────────────────────────────────────────────────────────────────────────
-->
<template>
  <section class="categories-section">
    <h2 class="section-title">Browse by Category</h2>

    <!-- Loading State -->
    <div v-if="loading" class="loading-state">
      <div class="spinner"></div>
      <span>Loading categories...</span>
    </div>

    <!-- Categories: 2 rows of 3, with dividers -->
    <div v-else class="categories-container">
      <!-- Row 1 -->
      <div class="grid-row">
        <button
          v-for="(category, i) in row1"
          :key="category.id"
          class="grid-col"
          :class="{ 'has-divider': i < row1.length - 1 }"
          @click="$emit('select', category)"
        >
          <span class="star" /><span class="star" /><span class="star" /><span class="star" /><span class="star" />
          <div class="category-box">
            <img :src="getImage(category)" :alt="category.name" />
          </div>
          <span class="category-label">{{ category.name }}</span>
        </button>
      </div>

      <!-- Horizontal divider -->
      <hr class="divider-h" />

      <!-- Row 2 -->
      <div class="grid-row">
        <button
          v-for="(category, i) in row2"
          :key="category.id"
          class="grid-col"
          :class="{ 'has-divider': i < row2.length - 1 }"
          @click="$emit('select', category)"
        >
          <span class="star" /><span class="star" /><span class="star" /><span class="star" /><span class="star" />
          <div class="category-box">
            <img :src="getImage(category)" :alt="category.name" />
          </div>
          <span class="category-label">{{ category.name }}</span>
        </button>
      </div>
    </div>
  </section>
</template>

<script setup>
import { computed } from 'vue'
import { getCategoryImage } from '@/config/homepage'

const props = defineProps({
  categories: { type: Array, required: true },
  loading: { type: Boolean, default: false }
})

defineEmits(['select'])

const getImage = getCategoryImage

// Split categories into two rows of 3
const row1 = computed(() => props.categories.slice(0, 3))
const row2 = computed(() => props.categories.slice(3, 6))
</script>

<style scoped>
.categories-section {
  padding: 40px 24px 60px;
  max-width: 1100px;
  margin: 0 auto;
}

.section-title {
  font-size: 24px;
  font-weight: 700;
  color: var(--color-text);
  margin: 0 0 32px;
  text-align: center;
}

/* ── Loading ── */
.loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
  padding: 60px 20px;
  color: var(--color-text-muted);
}

/* .spinner and @keyframes orbit-spin are defined in global.css and
   automatically cascade into scoped components — no redefinition needed. */

/* ── Grid layout ── */
.categories-container {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.grid-row {
  display: flex;
  justify-content: center;
  gap: 0;
}

.grid-col {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
  padding: 10px 40px;
  cursor: pointer;
  border: none;
  background: none;
  border-radius: 12px;
  transition: transform 0.3s ease;
  position: relative;
  overflow: visible;
}

.grid-col:hover {
  transform: translateY(-4px);
}

/* ── Star sparkles on hover ── */
.grid-col .star {
  position: absolute;
  width: 6px;
  height: 6px;
  pointer-events: none;
  opacity: 0;
  z-index: 5;
}

.grid-col .star::before,
.grid-col .star::after {
  content: '';
  position: absolute;
  background: var(--color-primary);
  border-radius: 1px;
}

/* Vertical bar of the cross-star */
.grid-col .star::before {
  width: 2px;
  height: 100%;
  top: 0;
  left: 50%;
  transform: translateX(-50%);
}

/* Horizontal bar of the cross-star */
.grid-col .star::after {
  width: 100%;
  height: 2px;
  top: 50%;
  left: 0;
  transform: translateY(-50%);
}

.grid-col .star:nth-child(1) { top: -4px;  left: 15%;  }
.grid-col .star:nth-child(2) { top: 10%;   right: 8%;  }
.grid-col .star:nth-child(3) { bottom: 20%; left: 5%;  }
.grid-col .star:nth-child(4) { top: 5%;    left: 55%;  }
.grid-col .star:nth-child(5) { bottom: 10%; right: 15%; }

.grid-col:hover .star {
  animation: star-twinkle 0.7s ease-out forwards;
}

.grid-col:hover .star:nth-child(1) { animation-delay: 0s;    }
.grid-col:hover .star:nth-child(2) { animation-delay: 0.1s;  }
.grid-col:hover .star:nth-child(3) { animation-delay: 0.2s;  }
.grid-col:hover .star:nth-child(4) { animation-delay: 0.15s; }
.grid-col:hover .star:nth-child(5) { animation-delay: 0.25s; }

@keyframes star-twinkle {
  0%   { opacity: 0; transform: scale(0) rotate(0deg); }
  50%  { opacity: 1; transform: scale(1.3) rotate(20deg); }
  100% { opacity: 0.7; transform: scale(1) rotate(0deg); }
}

/* Vertical divider between columns */
.grid-col.has-divider {
  border-right: 2px solid #efece3;
}

/* ── Category image box ── */
.category-box {
  position: relative;
  width: 297px;
  height: 110px;
  background: var(--color-bg, #f0f0f0);
  border-radius: 10px;
  overflow: hidden;
}

/* Dark navy overlay */
.category-box::after {
  content: '';
  position: absolute;
  inset: 0;
  background: linear-gradient(135deg, rgba(10, 25, 60, 0.55), rgba(30, 55, 110, 0.50));
  border-radius: 10px;
  pointer-events: none;
  transition: background 0.2s ease;
}

.grid-col:hover .category-box::after {
  background: linear-gradient(135deg, rgba(10, 25, 60, 0.40), rgba(30, 55, 110, 0.35));
}

.category-box img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
  transition: transform 0.3s ease;
}

.grid-col:hover .category-box img {
  transform: scale(1.05);
}

/* ── Label below image ── */
.category-label {
  color: var(--color-text);
  font-family: var(--font-ui, -apple-system, BlinkMacSystemFont, 'SF Pro Text', 'Helvetica Neue', Arial, sans-serif);
  font-size: 13px;
  font-weight: 500;
  line-height: 18px;
  letter-spacing: 0.1px;
}

/* ── Horizontal divider ── */
.divider-h {
  width: 100%;
  max-width: 1011px;
  height: 0;
  border: none;
  border-top: 2px solid #efece3;
  margin: 10px auto;
}

/* ── Responsive ── */
@media (max-width: 1024px) {
  .grid-col {
    padding: 10px 24px;
  }

  .category-box {
    width: 240px;
    height: 90px;
  }
}

@media (max-width: 768px) {
  .categories-section {
    padding: 32px 16px 48px;
  }

  .grid-row {
    flex-direction: column;
    align-items: center;
    gap: 0;
  }

  .grid-col {
    padding: 12px 0;
  }

  /* Switch dividers: vertical → none, horizontal between items */
  .grid-col.has-divider {
    border-right: none;
    border-bottom: 2px solid #efece3;
    padding-bottom: 16px;
  }

  .category-box {
    width: 100%;
    max-width: 320px;
    height: 100px;
  }

  .divider-h {
    display: none;
  }
}
</style>
