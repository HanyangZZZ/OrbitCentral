<!--
  HeroSearch.vue — Homepage Hero Banner + Search Bar
  ─────────────────────────────────────────────────────────────────────────────
  Full-width hero section at the top of the Home page with the Orbit logo,
  tagline, and a natural-language search bar.

  LAYOUT
  ┌────────────────────────────────────────────────────────┐
  │       [Orbit Logo]  Orbit                              │
  │       The best spots gravitate to you.                 │
  │  ┌──────────────────────────────────────┐              │
  │  │ 🔍  Try "cozy date night spot"  [Search]│          │
  │  └──────────────────────────────────────┘              │
  └────────────────────────────────────────────────────────┘

  PROPS
  • placeholder — custom hint text for the input

  EVENTS
  • @search(query) — fired when the form is submitted with a non-empty string

  MODULAR FLOW
    User types → submits → emits 'search' → HomePage pushes to /search?q=…
  ─────────────────────────────────────────────────────────────────────────────
-->
<template>
  <section class="hero">
    <div class="hero-content">
      <div class="hero-brand">
        <img src="@/components/icons/orbit-logo.png" alt="Orbit" class="hero-logo" />
        <h1 class="hero-title">Orbit</h1>
      </div>
      <p class="hero-subtitle">The best spots gravitate to you.</p>

      <!-- Search Bar -->
      <form class="search-form" @submit.prevent="handleSearch">
        <div class="search-wrapper">
          <svg class="search-icon" xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <circle cx="11" cy="11" r="8"/>
            <line x1="21" y1="21" x2="16.65" y2="16.65"/>
          </svg>
          <input
            v-model="query"
            type="text"
            :placeholder="placeholder"
            class="search-input"
          />
          <button type="submit" class="search-btn" :disabled="!query.trim()">
            Search
          </button>
        </div>
      </form>
    </div>
  </section>
</template>

<script setup>
import { ref } from 'vue'

const props = defineProps({
  placeholder: { type: String, default: 'Try "cozy date night spot" or "rainy day café"' }
})

const emit = defineEmits(['search'])

const query = ref('')

function handleSearch() {
  const q = query.value.trim()
  if (q) emit('search', q)
}
</script>

<style scoped>
.hero {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 45vh;
  padding: 60px 24px;
  background: linear-gradient(180deg, #ffffff 0%, #f0f4fa 100%);
}

.hero-content {
  max-width: 760px;
  width: 100%;
  text-align: center;
  display: flex;
  flex-direction: column;
  align-items: center;
}

.hero-brand {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 18px;
  margin-bottom: 6px;
  margin-left: 20px;
}

.hero-logo {
  width: 110px;
  height: 110px;
  object-fit: contain;
}

.hero-title {
  font-family: var(--font-brand, 'Barlow', sans-serif);
  font-size: 64px;
  font-weight: 800;
  color: var(--color-text);
  margin: 0;
  letter-spacing: -0.5px;
  line-height: 1;
}

.hero-subtitle {
  font-size: 16px;
  color: var(--color-text-muted);
  margin: 0 0 32px;
  margin-left: 40px;
  font-weight: 400;
  letter-spacing: 0.3px;
}

/* ── Search Form ── */
.search-form {
  width: 100%;
  max-width: 660px;
  margin: 0 auto;
}

.search-wrapper {
  display: flex;
  align-items: center;
  background: var(--search-bg);
  border: 1px solid var(--color-border);
  border-radius: 999px;
  padding: 6px 6px 6px 20px;
  transition: border-color 0.2s, box-shadow 0.2s;
  box-shadow: var(--shadow-sm);
}

.search-wrapper:focus-within {
  border-color: var(--color-primary);
  box-shadow: 0 0 0 3px rgba(74, 112, 169, 0.12);
}

.search-icon {
  color: var(--search-icon-color);
  flex-shrink: 0;
}

.search-input {
  flex: 1;
  border: none;
  background: transparent;
  padding: 12px 14px;
  font-size: 15px;
  color: var(--search-text-color);
  outline: none;
}

.search-input::placeholder {
  color: var(--search-placeholder-color);
}

.search-btn {
  background: var(--color-primary);
  color: #fff;
  border: none;
  padding: 11px 26px;
  border-radius: 999px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: background 0.2s;
  flex-shrink: 0;
}

.search-btn:hover:not(:disabled) {
  background: var(--color-primary-hover);
}

.search-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* ── Responsive ── */
@media (max-width: 768px) {
  .hero {
    min-height: 35vh;
    padding: 40px 16px;
  }
}

@media (max-width: 480px) {
  .search-wrapper {
    flex-wrap: wrap;
    border-radius: 16px;
    padding: 12px;
    gap: 8px;
  }

  .search-icon {
    display: none;
  }

  .search-input {
    width: 100%;
    padding: 8px;
    font-size: 14px;
  }

  .search-btn {
    width: 100%;
    border-radius: 12px;
  }
}
</style>
