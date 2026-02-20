<!--
  HomePage.vue — Landing Page (route: /)
  ─────────────────────────────────────────────────────────────────────────────
  Composes three presentational sections vertically:

  1. HeroSearch      — Orbit logo, tagline, natural-language search bar
  2. CategoryGrid    — "Browse by Category" 2×3 image grid
  3. NearbyForYou    — AI/time-based recommendations with orbital animation

  On mount, fetches top-level categories from the API. When a user searches
  or clicks a category, the page pushes to /search with the appropriate query.

  MODULAR FLOW
    API → categories → CategoryGrid renders them
    HeroSearch @search → router.push /search?q=…
    CategoryGrid @select → router.push /search?category=…
  ─────────────────────────────────────────────────────────────────────────────
-->
<template>
  <div class="home-page">
    <!-- Hero Section with Search -->
    <HeroSearch @search="handleSearch" />

    <!-- Categories Section -->
    <CategoryGrid
      :categories="parentCategories"
      :loading="loading"
      @select="navigateToCategory"
    />

    <!-- Nearby For You Section -->
    <NearbyForYou />
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { getCategories } from '@/api/client'

// Components
import HeroSearch from '@/components/home/HeroSearch.vue'
import CategoryGrid from '@/components/home/CategoryGrid.vue'
import NearbyForYou from '@/components/NearbyForYou.vue'

const router = useRouter()

// State
const categories = ref([])
const loading = ref(true)

// Computed: Only parent categories (no parent)
const parentCategories = computed(() => {
  return categories.value.filter(c => c.parent === null)
})

// Event handlers
function handleSearch(query) {
  router.push({ name: 'Search', query: { q: query } })
}

function navigateToCategory(category) {
  router.push({ name: 'Search', query: { category: category.id } })
}

// Fetch categories on mount
onMounted(async () => {
  try {
    const { data } = await getCategories()
    categories.value = data.results ?? []
  } catch (err) {
    console.error('Failed to load categories:', err)
  } finally {
    loading.value = false
  }
})
</script>

<style scoped>
.home-page {
  min-height: 100vh;
  background: var(--color-bg);
}
</style>
