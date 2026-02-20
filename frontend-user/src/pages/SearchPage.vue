<!--
  SearchPage.vue — Search & Browse Results (route: /search)
  ─────────────────────────────────────────────────────────────────────────────
  The main discovery page. Two-column layout:

  ┌─────────────────┬──────────────────────────────────────┐
  │ CategorySidebar │  AiSummary banner                    │
  │  (left rail)    │  FilterBar (sort, rating, tags)      │
  │                 │  BusinessCard × N                    │
  │                 │  Load More / empty state             │
  └─────────────────┴──────────────────────────────────────┘

  COMPOSABLE ARCHITECTURE (4 composables work together)
  • useSearchState    — reactive state: query, filters, businesses, flags
  • useSearchApi      — backend fetches: search, browse, load-more, tags
  • useFilterBar      — dropdown toggles, sort, rating slider, tag clicks
  • useAiSummary      — client-side "Orbit Scout" summary from results

  ROUTE-DRIVEN SEARCH
  The page watches `route.query.q` — when it changes (e.g. user searches
  from the header), it triggers a new search. Category browsing is handled
  by the sidebar's v-model.

  MODULAR FLOW
    route.query.q changes → useSearchApi.fetchBusinesses() → results stored
    in useSearchState → template re-renders BusinessCard list + AiSummary.
  ─────────────────────────────────────────────────────────────────────────────
-->
<template>
  <div class="search-page">

    <div class="page-body">
      <CategorySidebar v-model="selectedCategory" />

      <main class="main-content">
        <!-- Results headline -->
        <p class="results-info">
          <template v-if="searchQuery">
            Results for "<strong>{{ searchQuery }}</strong>"
            <span v-if="filteredBusinesses.length">({{ filteredBusinesses.length }} found)</span>
          </template>
          <template v-else-if="selectedCategory">
            Browsing category
            <span v-if="totalCount">({{ totalCount }} businesses)</span>
          </template>
          <template v-else>
            All businesses <span v-if="totalCount">({{ totalCount }} total)</span>
          </template>
        </p>

        <!-- AI insight (search mode only) -->
        <AiSummary :text="aiSummary" :visible="!!searchQuery && !loading" />

        <!-- Filter bar -->
        <FilterBar
          :open-dropdown="openDropdown"
          :sort-order="sortOrder"
          :sort-options="sortOptions"
          :min-rating="minRating"
          :suggested-tags="suggestedTags"
          :selected-tag-ids="selectedTagIds"
          :show-no-tags-hint="!!searchQuery && !loading"
          @toggle-dropdown="toggleDropdown"
          @select-sort="selectSort"
          @rating-change="onRatingChange"
          @clear-rating="minRating = 0"
          @toggle-tag="toggleTag"
        />

        <!-- States: loading / error / empty / results -->
        <div v-if="loading" class="state-msg">
          <div class="spinner" /><span>Loading businesses...</span>
        </div>

        <div v-else-if="error" class="state-msg error">
          <p>{{ error }}</p>
          <button class="retry-btn" @click="fetchBusinesses">Try again</button>
        </div>

        <div v-else-if="!filteredBusinesses.length" class="state-msg">
          <p>No businesses found.</p>
          <p class="hint">Try a different search term, category, or adjust your filters.</p>
        </div>

        <div v-else class="business-list">
          <BusinessCard v-for="biz in filteredBusinesses" :key="biz.id" :business="biz" />
        </div>

        <!-- Pagination (browse mode) -->
        <div v-if="!searchQuery && nextPageUrl" class="pagination">
          <button class="load-more-btn" :disabled="loadingMore" @click="loadMore">
            {{ loadingMore ? 'Loading...' : 'Load More' }}
          </button>
        </div>
      </main>
    </div>

    <!-- Click-away to close dropdowns -->
    <div v-if="openDropdown" class="click-away" @click="closeDropdowns" />
  </div>
</template>

<script setup>
import { watch, onMounted } from 'vue'
import { useRoute } from 'vue-router'

// Components
import CategorySidebar from '@/components/CategorySidebar.vue'
import BusinessCard    from '@/components/BusinessCard.vue'
import FilterBar       from '@/components/FilterBar.vue'
import AiSummary       from '@/components/AiSummary.vue'

// Composables
import { useSearchState }  from '@/composables/useSearchState'
import { useSearchApi }    from '@/composables/useSearchApi'
import { useAiSummary }    from '@/composables/useAiSummary'
import { useFilterBar }    from '@/composables/useFilterBar'

// ── 1. State ─────────────────────────────────────────────────────────────────
const state = useSearchState()
const {
  searchQuery, selectedCategory, sortOrder, minRating,
  suggestedTags, selectedTagIds,
  totalCount, nextPageUrl,
  loading, loadingMore, error,
  sortOptions, filteredBusinesses,
  syncQueryToRoute, resetFilters,
} = state

// ── 2. API ───────────────────────────────────────────────────────────────────
const { dbStats, fetchBusinesses, loadMore, fetchSuggestedTags, fetchStats } =
  useSearchApi(state)

// ── 3. AI summary ────────────────────────────────────────────────────────────
const { aiSummary, generate: generateSummary, clear: clearSummary } = useAiSummary()

// ── 4. Filter bar ────────────────────────────────────────────────────────────
const {
  openDropdown, toggleDropdown, closeDropdowns,
  selectSort, onRatingChange, toggleTag,
} = useFilterBar(state, { onFilterChange: fetchAndSummarise })

// ── Orchestration ────────────────────────────────────────────────────────────

/** Fetch businesses then regenerate the AI summary. */
async function fetchAndSummarise() {
  clearSummary()
  await fetchBusinesses()
  if (searchQuery.value) {
    generateSummary({
      query:   searchQuery.value,
      results: state.businesses.value,
      tags:    suggestedTags.value,
      stats:   dbStats.value,
    })
  }
}

function handleSearch(q) {
  if (loading.value) return           // guard against double-fire
  searchQuery.value = q
  resetFilters()
  clearSummary()
  fetchSuggestedTags()
  fetchAndSummarise()
}

// Re-fetch when category changes
watch(selectedCategory, fetchAndSummarise)

// React to route query changes (e.g. global AppHeader pushes ?q=…&t=…)
const route = useRoute()
watch(
  () => route.query,
  (newQuery) => {
    const q = (newQuery.q || '').trim()
    if (q) {
      handleSearch(q)
    } else if (!q && searchQuery.value) {
      // User cleared the search → revert to browse mode
      searchQuery.value = ''
      resetFilters()
      clearSummary()
      fetchAndSummarise()
    }
  },
)

onMounted(() => {
  fetchStats()
  if (searchQuery.value) fetchSuggestedTags()
  fetchAndSummarise()
})
</script>

<style scoped>
/* ── Layout ── */
.search-page { display: flex; flex-direction: column; min-height: 100vh; background: var(--color-bg); }
.page-body   { display: flex; flex: 1; }
.main-content { flex: 1; min-width: 0; padding: 24px 32px; }

/* ── Results info ── */
.results-info        { font-size: 14px; color: var(--color-text-muted); margin: 0 0 16px; }
.results-info strong { color: var(--color-text); }

/* ── Business list ── */
.business-list { display: flex; flex-direction: column; gap: 12px; }

/* ── States ── */
.state-msg.error { color: #ef4444; }
.hint { font-size: 13px; color: var(--color-text-muted); margin: 0; }

.retry-btn {
  background: var(--color-primary); color: #fff; border: none;
  padding: 8px 20px; border-radius: 6px; cursor: pointer; font-size: 14px;
}
.retry-btn:hover { background: var(--color-primary-hover); }

/* ── Pagination ── */
.pagination { display: flex; justify-content: center; padding: 24px 0; }
.load-more-btn {
  background: var(--color-surface); border: 1px solid var(--color-border);
  color: var(--color-text); padding: 10px 32px; border-radius: 8px;
  font-size: 14px; cursor: pointer; transition: background 0.2s, border-color 0.2s;
}
.load-more-btn:hover:not(:disabled) { background: rgba(74,112,169,0.06); border-color: var(--color-primary); }
.load-more-btn:disabled { opacity: 0.5; cursor: not-allowed; }

/* ── Click-away ── */
.click-away { position: fixed; inset: 0; z-index: 150; }
</style>
