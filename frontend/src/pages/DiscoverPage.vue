<template>
  <section class="discover-figma" :class="{ 'dropdown-open': ratingOpen || sortOpen }">
    <!-- Header — sits OUTSIDE the scaled shell, stays full-size like other pages -->
    <TopBar :show-search="true" :show-location="true" v-model:ai-enabled="aiEnabled" />

    <!-- Scaled content — sidebar + main body shrink together -->
    <div
      class="discover-shell-wrap"
      :style="{ height: (1200 * figmaScale) + 'px' }"
    >
      <div
        class="discover-shell"
        :style="{ transform: 'scale(' + figmaScale + ')' }"
      >
      <aside class="discover-sidebar">
        <!-- Map / List Toggle -->
        <div class="view-toggle">
          <button
            class="view-toggle-btn"
            :class="{ active: viewMode === 'list' }"
            type="button"
            @click="viewMode = 'list'"
          >
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M3 6h18M3 12h18M3 18h18" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
            </svg>
            List
          </button>
          <button
            class="view-toggle-btn"
            :class="{ active: viewMode === 'map' }"
            type="button"
            @click="viewMode = 'map'"
          >
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M1 6v16l7-4 8 4 7-4V2l-7 4-8-4-7 4z" stroke="currentColor" stroke-width="2" stroke-linejoin="round"/>
              <path d="M8 2v16M16 6v16" stroke="currentColor" stroke-width="2" stroke-linejoin="round"/>
            </svg>
            Map
          </button>
        </div>

        <nav class="side-nav">
          <template v-for="cat in categories" :key="cat.key">
            <div class="side-item side-item-toggle">
              <button class="side-toggle" type="button" @click="cat.open = !cat.open">
                <img :src="cat.icon" alt="" />
                <span>{{ cat.label }}</span>
              </button>
            </div>
            <div v-if="cat.open" class="side-subitems">
              <div
                v-for="sub in cat.subs"
                :key="sub.key"
                class="side-subitem"
                :class="{ active: activeSubcategory === sub.key }"
                @click="activeSubcategory = sub.key"
              >{{ sub.label }}</div>
            </div>
          </template>
        </nav>
      </aside>

      <main class="discover-main">
        <!-- ─── List View ─── -->
        <template v-if="viewMode === 'list'">
        <section class="summary-block">
          <img class="summary-logo" src="/figma-discovery-page/orbit-logo-transparent.png" alt="" />
          <div class="summary-text">
            <div class="summary-title">Summary:</div>
            <div class="summary-body">Text</div>
          </div>
        </section>

        <div class="divider-line"></div>

        <section class="recommendations">
          <div class="recommendation-card light">
            Recommendation #1
            <div class="mini-pill"></div>
          </div>
          <div class="recommendation-card mid">
            Recommendation #2
            <div class="mini-pill"></div>
          </div>
          <div class="recommendation-card dark">
            Recommendation #3
            <div class="mini-pill"></div>
          </div>
        </section>

        <section class="filters">
          <div class="filter-pill">
            <img src="/figma-discovery-page/image-removebg-preview-13.png" alt="" />
            <span>Special Offers</span>
          </div>
          <div class="filter-pill">
            <img src="/figma-discovery-page/image-removebg-preview-14.png" alt="" />
            <span>Highest Rated</span>
          </div>
          <div class="filter-pill rating-pill">
            <div class="pill-row">
              <img src="/figma-discovery-page/image-removebg-preview-15.png" alt="" />
              <span>Rating</span>
              <button class="rating-toggle" type="button" @click="ratingOpen = !ratingOpen; sortOpen = false" aria-label="Toggle rating filter">
                <img src="/figma-discovery-page/image-removebg-preview-17.png" alt="" />
              </button>
            </div>
            <div v-if="ratingOpen" class="rating-dropdown">
              <div class="rating-header">
                <span class="rating-title">Rating</span>
                <span class="rating-value">over {{ ratingValue.toFixed(1) }}</span>
              </div>
              <div class="rating-slider">
                <input
                  v-model.number="ratingValue"
                  type="range"
                  min="0"
                  max="5"
                  step="0.1"
                  aria-label="Rating range"
                />
              </div>
            </div>
          </div>
          <div class="filter-pill sort-pill">
            <div class="pill-row">
              <span>Sort</span>
              <button class="sort-toggle" type="button" @click="sortOpen = !sortOpen; ratingOpen = false" aria-label="Toggle sort filter">
                <img src="/figma-discovery-page/image-removebg-preview-17.png" alt="" />
              </button>
            </div>
            <div v-if="sortOpen" class="sort-dropdown">
              <div class="sort-title">Sort</div>
              <label class="sort-option">
                <input type="radio" value="recommended" v-model="sortValue" />
                <span>Recommended</span>
              </label>
              <label class="sort-option">
                <input type="radio" value="most-reviewed" v-model="sortValue" />
                <span>Most Reviewed</span>
              </label>
              <label class="sort-option">
                <input type="radio" value="distance" v-model="sortValue" />
                <span>Distance</span>
              </label>
            </div>
          </div>
          <div class="filter-pill blue">
            <span>Additional Tag</span>
            <img src="/figma-discovery-page/sort-close-x.svg" alt="" />
          </div>
          <div class="filter-pill blue">
            <span>Additional Tag</span>
            <img src="/figma-discovery-page/sort-close-x.svg" alt="" />
          </div>
        </section>

        <section class="business-grid">
          <RouterLink
            v-for="n in 2"
            :key="n"
            class="business-link"
            to="/business/name-of-business"
          >
            <div class="business-card">
              <div class="business-image"></div>
              <div class="business-meta">
                <div class="business-title">Name of Business | Coupon</div>
                <div class="business-rating">4.0 ★</div>
                <div class="review-pill">Customer reviews with bolded words of tags</div>
                <div class="coupon-row">
                  <span class="coupon-pill">Coupon</span>
                  <span class="coupon-pill">Coupon</span>
                </div>
              </div>
            </div>
          </RouterLink>
        </section>
        </template>

        <!-- ─── Map View ─── -->
        <template v-else>
          <div class="map-container">
            <div class="map-surface" ref="mapSurface">
              <!-- Map pin markers -->
              <div
                v-for="pin in mapPins"
                :key="pin.id"
                class="map-pin"
                :style="{ left: pin.x + '%', top: pin.y + '%' }"
                :class="{ active: activePin === pin.id }"
                @click="activePin = activePin === pin.id ? null : pin.id"
              >
                <svg width="28" height="36" viewBox="0 0 28 36" fill="none" xmlns="http://www.w3.org/2000/svg">
                  <path d="M14 0C6.268 0 0 6.268 0 14c0 10.5 14 22 14 22s14-11.5 14-22C28 6.268 21.732 0 14 0z" :fill="activePin === pin.id ? '#4a70a9' : '#0f172a'"/>
                  <circle cx="14" cy="13" r="5" fill="#fff"/>
                </svg>
                <!-- Info popup -->
                <div v-if="activePin === pin.id" class="map-pin-popup">
                  <div class="popup-name">{{ pin.name }}</div>
                  <div class="popup-rating">{{ pin.rating }} ★</div>
                  <div class="popup-category">{{ pin.category }}</div>
                  <RouterLink :to="'/business/' + pin.slug" class="popup-link">View Details →</RouterLink>
                </div>
              </div>

              <!-- "You" marker -->
              <div class="map-you-marker" style="left: 50%; top: 52%;">
                <div class="you-pulse"></div>
                <div class="you-dot"></div>
                <span class="you-label">You</span>
              </div>
            </div>

            <!-- Map controls -->
            <div class="map-controls">
              <button class="map-ctrl-btn" type="button" @click="mapZoom = Math.min(mapZoom + 0.25, 3)" aria-label="Zoom in">+</button>
              <button class="map-ctrl-btn" type="button" @click="mapZoom = Math.max(mapZoom - 0.25, 0.5)" aria-label="Zoom out">−</button>
            </div>
          </div>
        </template>
      </main>
    </div><!-- .discover-shell -->
    </div><!-- .discover-shell-wrap -->
  </section>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue';
import { useRoute } from 'vue-router';
import { TopBar } from '@/components';
import { useResponsiveScale } from '@/composables';

const route = useRoute();
const { scale: figmaScale } = useResponsiveScale(1440);

// ── Sidebar categories (data-driven) ──
const categories = reactive([
  { key: 'food-drink', label: 'Food & Drink', icon: '/figma-discovery-page/nav-food-drink.png', open: false,
    subs: [
      { key: 'restaurants', label: 'Restaurants' },
      { key: 'fast-food', label: 'Fast Food' },
      { key: 'sweets', label: 'Sweets' },
      { key: 'grocery', label: 'Grocery' },
    ]},
  { key: 'retail', label: 'Retail', icon: '/figma-discovery-page/nav-retail.png', open: false,
    subs: [
      { key: 'apparel-accessories', label: 'Apparel & Accessories' },
      { key: 'retail-home', label: 'Home' },
      { key: 'gifts-hobbies', label: 'Gifts & Hobbies' },
      { key: 'electronics', label: 'Electronics' },
    ]},
  { key: 'entertainment', label: 'Entertainment', icon: '/figma-discovery-page/nav-entertainment.png', open: false,
    subs: [
      { key: 'arts', label: 'Arts' },
      { key: 'recreation', label: 'Recreation' },
    ]},
  { key: 'personal-services', label: 'Personal Services', icon: '/figma-discovery-page/nav-personal-services.png', open: false,
    subs: [
      { key: 'health', label: 'Health' },
      { key: 'beauty', label: 'Beauty' },
      { key: 'education', label: 'Education' },
      { key: 'pet-care', label: 'Pet Care' },
    ]},
  { key: 'home-services', label: 'Home Services', icon: '/figma-discovery-page/nav-home-services.png', open: false,
    subs: [
      { key: 'maintenance', label: 'Maintenance' },
      { key: 'cleaning', label: 'Cleaning' },
      { key: 'auto', label: 'Auto' },
    ]},
]);

const activeSubcategory = ref('');
const ratingOpen = ref(false);
const ratingValue = ref(4.5);
const sortOpen = ref(false);
const sortValue = ref('recommended');
const aiEnabled = ref(false);
const viewMode = ref('list');
const activePin = ref(null);
const mapZoom = ref(1);
const mapSurface = ref(null);

// Simulated business pins on the map
const mapPins = [
  { id: 1, name: 'Blue Bottle Coffee', slug: 'name-of-business', rating: '4.5', category: 'Food & Drink', x: 35, y: 30 },
  { id: 2, name: 'Urban Outfitters', slug: 'name-of-business', rating: '4.2', category: 'Retail', x: 62, y: 25 },
  { id: 3, name: 'Sunrise Bakery', slug: 'name-of-business', rating: '4.8', category: 'Food & Drink', x: 28, y: 58 },
  { id: 4, name: 'The Barber Shop', slug: 'name-of-business', rating: '4.6', category: 'Personal Services', x: 72, y: 45 },
  { id: 5, name: 'Green Thumb Garden', slug: 'name-of-business', rating: '4.1', category: 'Home Services', x: 45, y: 70 },
  { id: 6, name: 'Regal Cinema', slug: 'name-of-business', rating: '4.3', category: 'Entertainment', x: 55, y: 38 },
  { id: 7, name: 'Fresh Mart', slug: 'name-of-business', rating: '4.0', category: 'Food & Drink', x: 80, y: 62 },
  { id: 8, name: 'Pixel Electronics', slug: 'name-of-business', rating: '4.4', category: 'Retail', x: 20, y: 42 },
];

// Open sidebar category from query param
onMounted(() => {
  const cat = route.query.category;
  if (cat) {
    const target = categories.find(c => c.key === cat);
    if (target) target.open = true;
  }
});
</script>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Barlow:wght@500&display=swap');
.discover-figma {
  background: #ffffff;
  display: flex;
  flex-direction: column;
  align-items: center;
  width: 100%;
  min-height: 100vh;
  overflow-x: hidden;
  font-family: 'SF Pro', 'Inter', sans-serif;
  color: #0f172a;
}

.discover-shell-wrap {
  width: 100%;
  max-width: 1440px;
  overflow: hidden;
  margin: 0 auto;
}

.discover-shell {
  width: 1440px;
  padding: 1.5rem 2rem;
  display: grid;
  grid-template-columns: 220px 1fr;
  column-gap: 32px;
  transform-origin: top left;
}

.discover-sidebar {
  padding-top: 12px;
  padding-left: 24px;
}

/* ─── Map / List Toggle ─── */
.view-toggle {
  display: flex;
  background: #efece3;
  border-radius: 10px;
  padding: 3px;
  gap: 2px;
  margin-bottom: 20px;
}

.view-toggle-btn {
  flex: 1;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  padding: 7px 0;
  border: none;
  border-radius: 8px;
  background: transparent;
  font-family: 'SF Pro', 'Inter', sans-serif;
  font-size: 12px;
  font-weight: 400;
  color: #64748b;
  cursor: pointer;
  transition: all 0.2s ease;
}

.view-toggle-btn.active {
  background: #fff;
  color: #0f172a;
  font-weight: 500;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.08);
}

.view-toggle-btn svg {
  flex-shrink: 0;
}

.side-nav {
  display: grid;
  gap: 18px;
  margin-top: 24px;
}

.side-item {
  display: flex;
  align-items: center;
  gap: 12px;
  font-family: 'SF Pro', 'Inter', sans-serif;
  font-size: 14px;
  font-weight: 300;
}

.side-item-toggle {
  align-items: flex-start;
}

.side-toggle {
  display: inline-flex;
  align-items: center;
  gap: 12px;
  background: none;
  border: none;
  padding: 0;
  font: inherit;
  color: inherit;
  cursor: pointer;
  font-weight: 400;
}

.side-subitems {
  display: grid;
  gap: 12px;
  margin-top: 6px;
  padding-left: 38px;
  font-family: 'SF Pro', 'Inter', sans-serif;
  font-size: 14px;
  font-weight: 300;
}

.side-subitem {
  line-height: 1.2;
  padding: 4px 8px;
  border-radius: 6px;
  cursor: pointer;
}

.side-subitem.active {
  background: #e4edfa;
}

.side-item img {
  width: 26px;
  height: 26px;
  object-fit: contain;
}

.discover-main {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.summary-block {
  display: flex;
  gap: 20px;
  align-items: center;
}

.summary-logo {
  height: 150px;
  width: auto;
  max-width: 180px;
  object-fit: contain;
}

.summary-title {
  font-family: 'SF Pro', 'Inter', sans-serif;
  font-weight: 500;
  font-size: 14px;
  margin-bottom: 4px;
}

.summary-body {
  font-family: 'SF Pro', 'Inter', sans-serif;
  font-weight: 300;
  font-size: 14px;
}

.divider-line {
  height: 1px;
  background: #efece3;
}

.recommendations {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 18px;
}

.recommendation-card {
  border-radius: 14px;
  padding: 24px;
  font-size: 20px;
  font-weight: 600;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  min-height: 120px;
}

.recommendation-card.light {
  background: #efece3;
}

.recommendation-card.mid {
  background: #8fabd4;
}

.recommendation-card.dark {
  background: #4a70a9;
  color: #0f172a;
}

.recommendation-card .mini-pill {
  align-self: flex-end;
  margin-top: auto;
  width: 64px;
  height: 14px;
  background: #ffffff;
  border-radius: 18px;
}

.filters {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
}

.filter-pill {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 6px 12px;
  border-radius: 18px;
  background: #efece3;
  font-size: 14px;
  font-weight: 600;
  font-family: 'SF Pro', 'Inter', sans-serif;
}

.rating-pill {
  position: relative;
}

.pill-row {
  display: flex;
  align-items: center;
  gap: 6px;
}

.rating-toggle {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  border: none;
  background: transparent;
  padding: 0;
  cursor: pointer;
}

.rating-toggle img {
  width: 18px;
  height: 18px;
}

.rating-dropdown {
  position: absolute;
  top: 100%;
  left: 0;
  margin-top: 8px;
  width: 320px;
  background: #ffffff;
  border-radius: 18px;
  box-shadow: 0 20px 40px rgba(15, 23, 42, 0.15);
  padding: 20px 22px;
  z-index: 20;
}

.sort-pill {
  position: relative;
}

.sort-toggle {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  border: none;
  background: transparent;
  padding: 0;
  cursor: pointer;
}

.sort-toggle img {
  width: 18px;
  height: 18px;
}

.sort-dropdown {
  position: absolute;
  top: 100%;
  left: 0;
  margin-top: 8px;
  width: 260px;
  background: #ffffff;
  border-radius: 18px;
  box-shadow: 0 20px 40px rgba(15, 23, 42, 0.15);
  padding: 10px 14px;
  z-index: 20;
}

.sort-title {
  font-size: 16px;
  font-weight: 700;
  margin-bottom: 4px;
  font-family: 'SF Pro', 'Inter', sans-serif;
}

.sort-option {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 13px;
  font-weight: 400;
  font-family: 'SF Pro', 'Inter', sans-serif;
  margin-bottom: 2px;
  line-height: 1.1;
}

.sort-option:last-child {
  margin-bottom: 0;
}

.sort-option input {
  width: 22px;
  height: 22px;
  accent-color: #0f172a;
}

.rating-header {
  display: flex;
  align-items: center;
  gap: 16px;
  font-size: 14px;
  font-weight: 700;
  font-family: 'SF Pro', 'Inter', sans-serif;
}

.rating-value {
  font-size: 11px;
  font-weight: 400;
  font-family: 'SF Pro', 'Inter', sans-serif;
}

.rating-slider {
  margin-top: 18px;
}

.rating-slider input[type='range'] {
  width: 100%;
  accent-color: #0f172a;
  height: 3px;
}

.rating-slider input[type='range']::-webkit-slider-runnable-track {
  height: 3px;
}

.rating-slider input[type='range']::-webkit-slider-thumb {
  width: 12px;
  height: 12px;
  border-radius: 50%;
  margin-top: -4.5px;
}

.rating-slider input[type='range']::-moz-range-track {
  height: 3px;
}

.rating-slider input[type='range']::-moz-range-thumb {
  width: 12px;
  height: 12px;
  border-radius: 50%;
  border: none;
}

.filter-pill img {
  width: 18px;
  height: 18px;
}

.filter-pill.blue {
  background: #8fabd4;
}

.pill-close {
  font-weight: 600;
}

.business-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 24px;
}

.business-card {
  background: #ffffff;
}

.business-link {
  text-decoration: none;
  color: inherit;
  display: block;
}

.business-image {
  background: #f0f0f0;
  border-radius: 12px;
  height: 160px;
}

.business-meta {
  margin-top: 10px;
  display: grid;
  gap: 8px;
  font-size: 13px;
}

.business-title {
  font-weight: 600;
}

.business-rating {
  font-size: 12px;
}

.review-pill {
  background: #ffca84;
  border-radius: 7px;
  padding: 6px 10px;
  color: #d45500;
  font-size: 12px;
}

.discover-figma:not(.dropdown-open) button:hover,
.discover-figma:not(.dropdown-open) .side-subitem:hover,
.discover-figma:not(.dropdown-open) .side-toggle:hover,
.discover-figma:not(.dropdown-open) .filter-pill:hover,
.discover-figma:not(.dropdown-open) .recommendation-card:hover,
.discover-figma:not(.dropdown-open) .business-card:hover,
.discover-figma:not(.dropdown-open) .location-chip:hover,
.discover-figma:not(.dropdown-open) .profile-icon:hover,
.discover-figma:not(.dropdown-open) img:hover {
  filter: brightness(0.95);
}

.discover-figma .rating-dropdown:hover,
.discover-figma .rating-dropdown *:hover {
  filter: none;
}

.discover-figma .rating-dropdown,
.discover-figma .rating-dropdown *,
.discover-figma .rating-pill:hover .rating-dropdown,
.discover-figma .rating-pill:hover .rating-dropdown * {
  filter: none;
}

.discover-figma:not(.dropdown-open) .side-subitem:hover,
.discover-figma:not(.dropdown-open) .side-toggle:hover,
.discover-figma:not(.dropdown-open) .filter-pill:hover,
.discover-figma:not(.dropdown-open) .recommendation-card:hover,
.discover-figma:not(.dropdown-open) .business-card:hover,
.discover-figma:not(.dropdown-open) .location-chip:hover,
.discover-figma:not(.dropdown-open) .profile-icon:hover {
  cursor: pointer;
}

.coupon-row {
  display: flex;
  gap: 10px;
}

.coupon-pill {
  background: #efece3;
  border-radius: 7px;
  padding: 6px 12px;
  color: #d45500;
  font-size: 12px;
}

/* ─── Map View ─── */
.map-container {
  position: relative;
  width: 100%;
  min-height: 700px;
  border-radius: 14px;
  overflow: hidden;
  background:
    radial-gradient(circle at 30% 40%, #e4edfa 0%, transparent 50%),
    radial-gradient(circle at 70% 60%, #efece3 0%, transparent 50%),
    #f4f2ed;
}

.map-surface {
  position: relative;
  width: 100%;
  height: 100%;
  min-height: 700px;
  /* Subtle grid lines to hint at a map */
  background-image:
    linear-gradient(rgba(0,0,0,0.03) 1px, transparent 1px),
    linear-gradient(90deg, rgba(0,0,0,0.03) 1px, transparent 1px);
  background-size: 60px 60px;
}

/* Street-like decorative lines */
.map-surface::before {
  content: '';
  position: absolute;
  inset: 0;
  background:
    linear-gradient(15deg, transparent 42%, rgba(215,210,200,0.5) 42%, rgba(215,210,200,0.5) 42.5%, transparent 42.5%),
    linear-gradient(-30deg, transparent 55%, rgba(215,210,200,0.4) 55%, rgba(215,210,200,0.4) 55.5%, transparent 55.5%),
    linear-gradient(80deg, transparent 30%, rgba(215,210,200,0.3) 30%, rgba(215,210,200,0.3) 30.3%, transparent 30.3%),
    linear-gradient(-60deg, transparent 65%, rgba(215,210,200,0.35) 65%, rgba(215,210,200,0.35) 65.3%, transparent 65.3%);
  pointer-events: none;
}

/* ─── Map Pins ─── */
.map-pin {
  position: absolute;
  transform: translate(-50%, -100%);
  cursor: pointer;
  z-index: 5;
  transition: transform 0.15s ease;
}

.map-pin:hover {
  transform: translate(-50%, -100%) scale(1.15);
  z-index: 10;
}

.map-pin.active {
  z-index: 15;
  transform: translate(-50%, -100%) scale(1.15);
}

.map-pin svg {
  filter: drop-shadow(0 2px 4px rgba(0,0,0,0.2));
}

.map-pin-popup {
  position: absolute;
  bottom: calc(100% + 8px);
  left: 50%;
  transform: translateX(-50%);
  background: #fff;
  border-radius: 12px;
  box-shadow: 0 8px 24px rgba(0,0,0,0.12);
  padding: 12px 16px;
  min-width: 180px;
  z-index: 20;
}

.popup-name {
  font-family: 'SF Pro', 'Inter', sans-serif;
  font-size: 13px;
  font-weight: 600;
  color: #0f172a;
  margin-bottom: 2px;
}

.popup-rating {
  font-family: 'SF Pro', 'Inter', sans-serif;
  font-size: 12px;
  font-weight: 400;
  color: #e8b931;
  margin-bottom: 2px;
}

.popup-category {
  font-family: 'SF Pro', 'Inter', sans-serif;
  font-size: 11px;
  font-weight: 200;
  color: #64748b;
  margin-bottom: 8px;
}

.popup-link {
  display: inline-block;
  font-family: 'SF Pro', 'Inter', sans-serif;
  font-size: 12px;
  font-weight: 500;
  color: #4a70a9;
  text-decoration: none;
}

.popup-link:hover {
  text-decoration: underline;
}

/* ─── "You" Marker ─── */
.map-you-marker {
  position: absolute;
  transform: translate(-50%, -50%);
  z-index: 4;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
}

.you-pulse {
  position: absolute;
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: rgba(74, 112, 169, 0.15);
  animation: pulse-ring 2s ease-out infinite;
}

.you-dot {
  width: 14px;
  height: 14px;
  border-radius: 50%;
  background: #4a70a9;
  border: 3px solid #fff;
  box-shadow: 0 2px 6px rgba(74, 112, 169, 0.4);
  position: relative;
  z-index: 1;
}

.you-label {
  font-family: 'SF Pro', 'Inter', sans-serif;
  font-size: 10px;
  font-weight: 500;
  color: #4a70a9;
  background: #fff;
  padding: 1px 6px;
  border-radius: 4px;
  box-shadow: 0 1px 3px rgba(0,0,0,0.1);
}

@keyframes pulse-ring {
  0% { transform: scale(0.8); opacity: 1; }
  100% { transform: scale(2); opacity: 0; }
}

/* ─── Map Controls ─── */
.map-controls {
  position: absolute;
  bottom: 16px;
  right: 16px;
  display: flex;
  flex-direction: column;
  gap: 4px;
  z-index: 10;
}

.map-ctrl-btn {
  width: 32px;
  height: 32px;
  border-radius: 8px;
  border: none;
  background: #fff;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
  font-size: 18px;
  font-weight: 500;
  color: #0f172a;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  font-family: 'SF Pro', 'Inter', sans-serif;
}

.map-ctrl-btn:hover {
  background: #f8f8f8;
}
</style>
