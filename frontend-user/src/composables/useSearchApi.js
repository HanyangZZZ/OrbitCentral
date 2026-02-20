/**
 * useSearchApi.js — Search Page API Communication
 * ==================================================
 * PURPOSE:
 *   Handles all backend calls for the Search page. Builds the right
 *   query params, sends requests, and updates the shared search state.
 *
 * MODULAR LOGIC:
 *   This composable handles SIDE EFFECTS (API calls), while
 *   useSearchState handles STATE. They work together:
 *   - useSearchState provides the reactive data (query, filters, etc.)
 *   - useSearchApi reads that data, calls the API, writes results back
 *
 *   Private helper functions (buildSearchParams, buildBrowseParams,
 *   normaliseResults) keep the public methods clean.
 *
 * OOP FLOW:
 *   SearchPage watches route changes → calls fetchBusinesses() →
 *   this composable builds params from state → calls API →
 *   writes results back into state → Vue reactivity updates the UI.
 *
 * KEY METHODS:
 *   fetchBusinesses() — Main entry: search or browse depending on mode
 *   loadMore()        — Fetch next page of paginated results
 *   fetchSuggestedTags() — Get tag suggestions based on query/category
 *   fetchStats()      — Get total business/review/category counts
 */
import { ref } from 'vue'
import {
  getBusinesses,
  searchBusinesses,
  searchTags,
  getNextPage,
  getStats,
} from '@/api/client'

export function useSearchApi(state) {
  const dbStats = ref(null)

  // ── Fetch businesses (search or browse) ────────────────────────────────
  async function fetchBusinesses() {
    const {
      searchQuery, selectedCategory, sortOrder, selectedTagIds,
      businesses, totalCount, nextPageUrl, loading, error,
    } = state

    loading.value     = true
    error.value       = ''
    businesses.value  = []
    nextPageUrl.value = null

    try {
      if (searchQuery.value) {
        const params = buildSearchParams(state)
        const { data } = await searchBusinesses(params)
        const results = normaliseResults(data)
        businesses.value = results
        totalCount.value = results.length
      } else {
        const params = buildBrowseParams(state)
        const { data } = await getBusinesses(params)
        businesses.value = data.results ?? []
        totalCount.value = data.count   ?? 0
        nextPageUrl.value = data.next   ?? null
      }
    } catch (err) {
      console.error('Fetch failed:', err)
      error.value = err.response?.data?.detail || err.message || 'Something went wrong'
    } finally {
      loading.value = false
    }
  }

  // ── Pagination (browse mode) ───────────────────────────────────────────
  async function loadMore() {
    const { nextPageUrl, loadingMore, businesses } = state
    if (!nextPageUrl.value || loadingMore.value) return

    loadingMore.value = true
    try {
      const { data } = await getNextPage(nextPageUrl.value)
      businesses.value.push(...(data.results ?? []))
      nextPageUrl.value = data.next ?? null
    } catch (err) {
      console.error('Load more failed:', err)
    } finally {
      loadingMore.value = false
    }
  }

  // ── Suggested tags ─────────────────────────────────────────────────────
  async function fetchSuggestedTags() {
    const { searchQuery, suggestedTags, selectedTagIds } = state

    if (!searchQuery.value) {
      suggestedTags.value  = []
      selectedTagIds.value = []
      return
    }
    try {
      const { data } = await searchTags({
        q: searchQuery.value, limit: 10, min_usage: 2,
      })
      suggestedTags.value = normaliseResults(data)
    } catch {
      suggestedTags.value = []
    }
  }

  // ── Database stats (one-time) ──────────────────────────────────────────
  async function fetchStats() {
    try {
      const { data } = await getStats()
      dbStats.value = data
    } catch {
      /* non-critical */
    }
  }

  return { dbStats, fetchBusinesses, loadMore, fetchSuggestedTags, fetchStats }
}

// ── Private helpers ──────────────────────────────────────────────────────────

function buildSearchParams({ searchQuery, selectedCategory, sortOrder, selectedTagIds }) {
  const p = { q: searchQuery.value, limit: 30 }
  if (selectedCategory.value) p.category = selectedCategory.value
  if (sortOrder.value === 'distance' || sortOrder.value === 'rating') {
    p.sort = sortOrder.value
  }
  if (selectedTagIds.value.length) p.tag = selectedTagIds.value
  return p
}

function buildBrowseParams({ selectedCategory, sortOrder }) {
  const p = { page_size: 20 }
  if (selectedCategory.value) p.category = selectedCategory.value
  if (sortOrder.value && sortOrder.value !== 'distance' && sortOrder.value !== 'rating') {
    p.ordering = sortOrder.value
  }
  return p
}

/** Normalise paginated vs flat API responses. */
function normaliseResults(data) {
  return Array.isArray(data) ? data : (data.results ?? [])
}
